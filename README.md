# Sub2API Ops

Sub2API / CPA 自动化运维工具

## 功能

- ✅ 检查账号状态
- ✅ 修复 Error 账号
- ✅ 测试 API 调用
- ✅ 管理服务状态
- ✅ **自动代理配置** - 新账号自动挂代理
- ✅ 定时自动修复

## 安装

```bash
git clone https://github.com/zhoutian1995/sub2api_ops.git
cd sub2api_ops
pip install -r requirements.txt
```

## 使用方法

### 检查账号状态
```bash
python3 sub2api_ops.py check
```

### 修复 Error 账号
```bash
python3 sub2api_ops.py fix
```

### 测试 API
```bash
python3 sub2api_ops.py test        # 默认 5 次
python3 sub2api_ops.py test 10     # 测试 10 次
```

### 查看服务状态
```bash
python3 sub2api_ops.py status
```

### 重启服务
```bash
python3 sub2api_ops.py restart
```

### 启动自动代理守护进程
```bash
python3 auto_proxy.py
```

### 启动定时自动修复
```bash
python3 auto_fix.py
```

## 自动代理功能

当你在 CPA 上添加新的 OpenAI 账号时，`auto_proxy.py` 会：

1. 监控 `~/.cli-proxy-api/` 目录
2. 检测到新的 auth 文件
3. 根据 `config.json` 中的分配表自动添加代理
4. 确保每个账号使用固定的代理 IP

### 代理分配

每个账号绑定固定的代理 IP，避免 IP 轮换导致 token 被吊销。

| 代理编号 | 代理 IP | 分配账号数 |
|---------|---------|-----------|
| 1 | 154.44.99.29 | 10 个 |
| 2 | 50.2.7.58 | 10 个 |
| 3 | 50.2.7.59 | 10 个 |
| ... | ... | ... |

## 配置

编辑 `config.json` 文件：

```json
{
    "sub2api_url": "http://127.0.0.1:8080",
    "cpa_url": "http://127.0.0.1:8317",
    "admin_email": "your-email@gmail.com",
    "admin_password": "your-password",
    "cpa_api_key": "your-cpa-api-key",
    "sub2api_api_key": "your-sub2api-api-key",
    "proxies": {
        "1": "socks5://user:pass@host:port",
        ...
    },
    "assignments": {
        "account@email.com": "1",
        ...
    }
}
```

## 项目结构

```
sub2api_ops/
├── README.md           # 项目说明
├── sub2api_ops.py      # 主脚本
├── auto_proxy.py       # 自动代理守护进程
├── auto_fix.py         # 自动修复脚本
├── config.json         # 配置文件
├── requirements.txt    # 依赖
└── LICENSE             # 许可证
```

## License

MIT
