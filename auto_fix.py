#!/usr/bin/env python3
"""
自动修复脚本 - 每 30 分钟运行一次
"""

import requests
import json
import os
from datetime import datetime

# 加载配置
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def log(msg):
    print("[%s] %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))

def login(config):
    r = requests.post("%s/api/v1/auth/login" % config["sub2api_url"], json={
        "email": config["admin_email"],
        "password": config["admin_password"]
    })
    return r.json()["data"]["access_token"]

def main():
    log("=== 开始自动修复 ===")

    config = load_config()
    token = login(config)
    headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}

    # 获取账号
    r = requests.get("%s/api/v1/admin/accounts?page=1&page_size=100" % config["sub2api_url"], headers=headers)
    accounts = r.json()["data"]["items"]

    active = sum(1 for a in accounts if a.get("status") == "active")
    error = sum(1 for a in accounts if a.get("status") == "error")
    log("Total: %d, Active: %d, Error: %d" % (len(accounts), active, error))

    # 修复 Error 账号
    error_accounts = [a for a in accounts if a.get("status") == "error"]

    if error_accounts:
        log("Found %d error accounts" % len(error_accounts))

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
                log("Fixed: %s" % name)

        # 更新 Group 路由
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
        log("Group routing updated")
    else:
        log("No error accounts found")

    # 最终统计
    r = requests.get("%s/api/v1/admin/accounts?page=1&page_size=100" % config["sub2api_url"], headers=headers)
    accounts = r.json()["data"]["items"]
    active = sum(1 for a in accounts if a.get("status") == "active")
    error = sum(1 for a in accounts if a.get("status") == "error")
    log("Final: Active=%d, Error=%d" % (active, error))
    log("=== 自动修复完成 ===")

if __name__ == "__main__":
    main()
