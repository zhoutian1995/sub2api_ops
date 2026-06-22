# Sub2API Ops - Claude Code Skill

Sub2API / CPA 自动化运维技能，可通过 Claude Code 调用。

## 快速开始

### 安装 Skill

```bash
# 克隆仓库
git clone https://github.com/zhoutian1995/sub2api_ops.git
cd sub2api_ops

# 安装依赖
pip install -r requirements.txt

# 复制到 Claude Code skills 目录
cp -r . ~/.claude/skills/sub2api-ops/
```

### 配置

编辑 `config.json`，填入你的配置：

```json
{
    "sub2api_url": "http://your-server:8080",
    "cpa_url": "http://your-server:8317",
    "admin_email": "your-email@gmail.com",
    "admin_password": "your-password",
    "cpa_api_key": "your-cpa-api-key",
    "sub2api_api_key": "your-sub2api-api-key"
}
```

## 功能列表

### 1. 检查账号状态

```bash
python3 sub2api_ops.py check
```

输出示例：
```
============================================================
Total: 25
Active: 25 ✅
Error: 0 ❌
Paused: 0 ⏸️
============================================================
```

### 2. 修复 Error 账号

```bash
python3 sub2api_ops.py fix
```

自动修复所有 Error 状态的账号：
- 删除旧账号
- 重新添加为 Active
- 更新 Group 路由

### 3. 测试 API

```bash
python3 sub2api_ops.py test        # 默认 5 次
python3 sub2api_ops.py test 10     # 测试 10 次
```

输出示例：
```
Test 1: ✅ OK
Test 2: ✅ OK
Test 3: ✅ OK
Test 4: ✅ OK
Test 5: ✅ OK
========================================
Success: 5
Failed: 0
========================================
```

### 4. 查看服务状态

```bash
python3 sub2api_ops.py status
```

输出示例：
```
cpa: active
sub2api: active
auto-proxy: active
```

### 5. 重启服务

```bash
python3 sub2api_ops.py restart
```

### 6. 自动代理配置（核心功能）

```bash
python3 auto_proxy.py
```

**功能说明：**
- 监控 CPA 的 `~/.cli-proxy-api/` 目录
- 检测到新的 auth 文件时，自动添加代理配置
- 根据 `config.json` 中的分配表，为每个账号绑定固定的代理 IP

**工作流程：**
```
用户在 CPA 登录 OpenAI 账号
        ↓
auth 文件出现在 ~/.cli-proxy-api/
        ↓
auto_proxy.py 检测到新文件
        ↓
根据分配表自动添加 proxy_url
        ↓
CPA 使用固定代理访问 OpenAI
```

### 7. 定时自动修复

```bash
python3 auto_fix.py
```

**功能说明：**
- 检查所有账号状态
- 修复 Error 账号
- 更新并发和优先级
- 更新 Group 路由

## 代理分配

### 代理列表

| 代理编号 | 代理 IP | 端口 | 类型 |
|---------|---------|------|------|
| 1 | 154.44.99.29 | 7778 | SOCKS5 |
| 2 | 50.2.7.58 | 9194 | SOCKS5 |
| 3 | 50.2.7.59 | 9194 | SOCKS5 |
| 4 | 50.2.7.79 | 9194 | SOCKS5 |
| 5 | 50.2.7.86 | 9194 | SOCKS5 |
| 6 | 50.2.7.91 | 9194 | SOCKS5 |
| 7 | 50.2.7.95 | 9194 | SOCKS5 |
| 8 | 50.2.7.96 | 9194 | SOCKS5 |
| 9 | 50.2.7.99 | 9194 | SOCKS5 |
| 10 | 50.2.7.107 | 9194 | SOCKS5 |
| 11 | 50.2.7.37 | 9194 | SOCKS5 |

### 分配原则

- 每个代理最多分配 **10 个账号**
- 每个账号绑定固定的代理 IP
- 避免 IP 轮换导致 token 被吊销

### 添加新账号

1. 在 CPA 上登录新账号
2. `auto_proxy.py` 自动检测并添加代理
3. 在 sub2api 中添加账号
4. 运行 `python3 sub2api_ops.py fix` 更新路由

## 配置文件说明

```json
{
    // sub2api 配置
    "sub2api_url": "http://127.0.0.1:8080",
    "cpa_url": "http://127.0.0.1:8317",
    "admin_email": "admin@example.com",
    "admin_password": "password",
    
    // API Keys
    "cpa_api_key": "your-cpa-api-key",
    "sub2api_api_key": "your-sub2api-api-key",
    
    // 账号配置
    "group_id": 26,
    "default_concurrency": 5,
    "default_priority": 1,
    
    // 自动代理配置
    "auth_dir": "~/.cli-proxy-api",
    "check_interval": 5,
    
    // 代理列表
    "proxies": {
        "1": "socks5://user:pass@host:port",
        "2": "socks5://user:pass@host:port"
    },
    
    // 账号-代理分配表
    "assignments": {
        "account1@email.com": "1",
        "account2@email.com": "2"
    }
}
```

## 故障排查

### 问题 1：API 返回 503

**原因：** 没有可用的 Active 账号

**解决：**
```bash
python3 sub2api_ops.py fix
```

### 问题 2：API 返回 401

**原因：** Token 被吊销

**解决：**
```bash
# 在 CPA 上重新登录
/opt/cpa/login_with_proxy.sh account@email.com
```

### 问题 3：代理不可用

**原因：** 代理服务过期或不可用

**解决：**
1. 检查代理服务状态
2. 更新 `config.json` 中的代理配置
3. 重启服务

## 服务管理

```bash
# 查看状态
systemctl status cpa
systemctl status sub2api
systemctl status auto-proxy

# 重启服务
systemctl restart cpa
systemctl restart sub2api
systemctl restart auto-proxy

# 查看日志
journalctl -u cpa -f
journalctl -u sub2api -f
journalctl -u auto-proxy -f
```

## License

MIT
