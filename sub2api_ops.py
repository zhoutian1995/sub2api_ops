#!/usr/bin/env python3
"""
Sub2API / CPA 自动化运维工具
"""

import requests
import json
import sys
import os
from datetime import datetime

# 加载配置
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def log(msg):
    print("[%s] %s" % (datetime.now().strftime("%H:%M:%S"), msg))

def login(config):
    """登录获取 token"""
    r = requests.post("%s/api/v1/auth/login" % config["sub2api_url"], json={
        "email": config["admin_email"],
        "password": config["admin_password"]
    })
    return r.json()["data"]["access_token"]

def check_accounts(config):
    """检查账号状态"""
    log("检查账号状态...")
    token = login(config)
    headers = {"Authorization": "Bearer " + token}

    r = requests.get("%s/api/v1/admin/accounts?page=1&page_size=100" % config["sub2api_url"], headers=headers)
    accounts = r.json()["data"]["items"]

    active = sum(1 for a in accounts if a.get("status") == "active")
    error = sum(1 for a in accounts if a.get("status") == "error")
    paused = sum(1 for a in accounts if a.get("status") == "paused")

    print("=" * 60)
    print("Total: %d" % len(accounts))
    print("Active: %d ✅" % active)
    print("Error: %d ❌" % error)
    print("Paused: %d ⏸️" % paused)
    print("=" * 60)

    if error > 0:
        print("\nError 账号:")
        for acc in accounts:
            if acc.get("status") == "error":
                print("  - %s" % acc.get("name"))

    return accounts

def fix_accounts(config):
    """修复 Error 账号"""
    log("修复 Error 账号...")
    token = login(config)
    headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}

    r = requests.get("%s/api/v1/admin/accounts?page=1&page_size=100" % config["sub2api_url"], headers=headers)
    accounts = r.json()["data"]["items"]

    error_accounts = [a for a in accounts if a.get("status") == "error"]

    if not error_accounts:
        log("没有 Error 账号")
        return 0

    log("找到 %d 个 Error 账号" % len(error_accounts))
    fixed = 0

    for acc in error_accounts:
        old_id = acc.get("id")
        name = acc.get("name")

        requests.delete("%s/api/v1/admin/accounts/%d" % (config["sub2api_url"], old_id), headers=headers)

        new_acc = {
            "name": name,
            "platform": "openai",
            "type": "apikey",
            "credentials": {
                "api_key": config["cpa_api_key"],
                "base_url": config["cpa_url"]
            },
            "group_ids": [config["group_id"]],
            "concurrency": config["default_concurrency"],
            "priority": config["default_priority"],
            "status": "active"
        }
        r = requests.post("%s/api/v1/admin/accounts" % config["sub2api_url"], headers=headers, json=new_acc)
        if r.status_code == 200:
            log("修复: %s" % name)
            fixed += 1

    # 更新 Group 路由
    if fixed > 0:
        r = requests.get("%s/api/v1/admin/accounts?page=1&page_size=100" % config["sub2api_url"], headers=headers)
        accounts = r.json()["data"]["items"]
        active_ids = [a.get("id") for a in accounts if a.get("status") == "active"]

        requests.put("%s/api/v1/admin/groups/%d" % (config["sub2api_url"], config["group_id"]), headers=headers, json={
            "model_routing": {
                "gpt-5.4": active_ids,
                "gpt-5.4-mini": active_ids,
                "gpt-5.5": active_ids,
                "gpt-5.3-codex-spark": active_ids,
                "codex-auto-review": active_ids
            }
        })
        log("Group 路由已更新")

    log("修复完成: %d 个账号" % fixed)
    return fixed

def test_api(config, count=5):
    """测试 API"""
    log("测试 API (%d 次)..." % count)

    success = 0
    failed = 0

    for i in range(count):
        try:
            r = requests.post("%s/v1/chat/completions" % config["sub2api_url"],
                headers={"Authorization": "Bearer " + config["sub2api_api_key"], "Content-Type": "application/json"},
                json={"model": "gpt-5.4-mini", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5},
                timeout=30)

            if r.status_code == 200 and "choices" in r.json():
                success += 1
                print("Test %d: ✅ OK" % (i + 1))
            else:
                failed += 1
                print("Test %d: ❌ FAIL (%s)" % (i + 1, r.json().get("error", {}).get("message", "Unknown")))
        except Exception as e:
            failed += 1
            print("Test %d: ❌ ERROR (%s)" % (i + 1, str(e)[:50]))

    print("=" * 40)
    print("Success: %d" % success)
    print("Failed: %d" % failed)
    print("=" * 40)

    return success, failed

def service_status():
    """查看服务状态"""
    log("查看服务状态...")

    services = ["cpa", "sub2api", "auto-proxy"]

    for service in services:
        os.system("systemctl is-active %s 2>/dev/null | xargs -I {} echo '%s: {}'" % (service, service))

def restart_services():
    """重启服务"""
    log("重启服务...")

    services = ["cpa", "sub2api"]

    for service in services:
        os.system("systemctl restart %s" % service)
        log("%s 已重启" % service)

    log("等待服务启动...")
    os.system("sleep 5")
    log("服务重启完成")

def main():
    if len(sys.argv) < 2:
        print("用法: python3 sub2api_ops.py <command>")
        print("命令:")
        print("  check      - 检查账号状态")
        print("  fix        - 修复 Error 账号")
        print("  test [n]   - 测试 API (默认 5 次)")
        print("  status     - 查看服务状态")
        print("  restart    - 重启服务")
        return

    config = load_config()
    command = sys.argv[1]

    if command == "check":
        check_accounts(config)
    elif command == "fix":
        fix_accounts(config)
    elif command == "test":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        test_api(config, count)
    elif command == "status":
        service_status()
    elif command == "restart":
        restart_services()
    else:
        print("未知命令: %s" % command)

if __name__ == "__main__":
    main()
