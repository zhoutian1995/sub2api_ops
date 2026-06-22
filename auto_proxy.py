#!/usr/bin/env python3
"""
自动代理配置守护进程
监控 CPA 的 auth 目录，为新账号自动添加代理
"""

import os
import json
import time
from datetime import datetime

# 加载配置
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def log(msg):
    print("[%s] %s" % (datetime.now().strftime("%H:%M:%S"), msg))

def get_email_from_filename(filename):
    """从文件名提取邮箱"""
    if not filename.startswith("codex-") or not filename.endswith("-plus.json"):
        return None
    email_part = filename[6:-13]
    return email_part + "@mail.com"

def process_file(filepath, config):
    """处理 auth 文件，添加 proxy_url"""
    filename = os.path.basename(filepath)
    email = get_email_from_filename(filename)

    if not email:
        return False

    assignments = config.get("assignments", {})
    proxies = config.get("proxies", {})

    proxy_num = assignments.get(email)
    if not proxy_num:
        return False

    proxy = proxies.get(str(proxy_num))
    if not proxy:
        return False

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        if data.get('proxy_url') == proxy:
            return False

        data['proxy_url'] = proxy

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        ts = time.strftime("%H:%M:%S")
        print("[%s] 已为 %s 设置代理 (代理%s)" % (ts, email, proxy_num))
        return True
    except Exception as e:
        ts = time.strftime("%H:%M:%S")
        print("[%s] 处理 %s 失败: %s" % (ts, filename, str(e)))
        return False

def main():
    config = load_config()
    auth_dir = config.get("auth_dir", os.path.expanduser("~/.cli-proxy-api"))
    check_interval = config.get("check_interval", 5)

    ts = time.strftime("%H:%M:%S")
    print("[%s] 自动代理配置守护进程已启动" % ts)
    print("[%s] 监控目录: %s" % (ts, auth_dir))
    print("[%s] 检查间隔: %d 秒" % (ts, check_interval))
    print()

    # 处理现有文件
    processed = 0
    for filename in os.listdir(auth_dir):
        if filename.startswith("codex-") and filename.endswith("-plus.json"):
            filepath = os.path.join(auth_dir, filename)
            if process_file(filepath, config):
                processed += 1

    ts = time.strftime("%H:%M:%S")
    if processed > 0:
        print("[%s] 初始处理完成，更新了 %d 个文件" % (ts, processed))
    else:
        print("[%s] 所有文件已配置代理" % ts)

    # 持续监控
    while True:
        time.sleep(check_interval)

        try:
            config = load_config()
        except:
            continue

        for filename in os.listdir(auth_dir):
            if filename.startswith("codex-") and filename.endswith("-plus.json"):
                filepath = os.path.join(auth_dir, filename)
                process_file(filepath, config)

if __name__ == "__main__":
    main()
