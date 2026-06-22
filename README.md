# Sub2API Ops

Sub2API / CPA 自动化运维工具

## 功能

- 检查账号状态
- 修复 Error 账号
- 测试 API 调用
- 管理服务状态
- 自动代理配置

## 安装

```bash
git clone https://github.com/your-username/sub2api_ops.git
cd sub2api_ops
chmod +x sub2api_ops.py
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

## 配置

编辑 `config.json` 文件：

```json
{
    "sub2api_url": "http://127.0.0.1:8080",
    "cpa_url": "http://127.0.0.1:8317",
    "admin_email": "your-email@gmail.com",
    "admin_password": "your-password",
    "cpa_api_key": "your-cpa-api-key",
    "sub2api_api_key": "your-sub2api-api-key"
}
```

## 项目结构

```
sub2api_ops/
├── README.md           # 项目说明
├── sub2api_ops.py      # 主脚本
├── config.json         # 配置文件
├── auto_fix.py         # 自动修复脚本
├── requirements.txt    # 依赖
└── LICENSE             # 许可证
```

## License

MIT
