# ThetaGang 快速启动参考

## 🚀 一键启动

```bash
./start.sh
```

---

## 📋 常用命令

| 命令 | 说明 |
|------|------|
| `./start.sh` | 启动程序（后台运行） |
| `./stop.sh` | 停止程序 |
| `./restart.sh` | 重启程序 |
| `./status.sh` | 查看运行状态 |
| `./view_logs.sh` | 查看日志（交互式菜单） |

---

## 📊 快速检查

### 程序是否在运行？
```bash
./status.sh
```

### 查看实时日志
```bash
tail -f logs/thetagang_latest.log
```

### 查看最近订单
```bash
grep -i "order\|submitted" logs/thetagang_latest.log | tail -20
```

### 查看是否有错误
```bash
grep -i "error\|exception" logs/thetagang_latest.log | tail -20
```

---

## 🕐 最佳运行时间

**美东交易时间**: 周一至周五 9:30 AM - 4:00 PM
- 北京时间（冬令时）: 22:30 PM - 次日 5:00 AM
- 北京时间（夏令时）: 21:30 PM - 次日 4:00 AM

---

## 🔧 前置检查

运行前确保：
- [x] IB Gateway 已启动
- [x] 端口设置为 4002
- [x] API 连接已启用

测试连接：
```bash
.venv/bin/python scripts/test_market_data.py
```

---

## 📂 文件结构

```
thetagang/
├── start.sh              # 启动脚本
├── stop.sh               # 停止脚本
├── restart.sh            # 重启脚本
├── status.sh             # 状态检查
├── view_logs.sh          # 日志查看
├── thetagang.toml        # 配置文件
├── thetagang.pid         # 进程 PID（运行时）
├── logs/                 # 日志目录
│   ├── thetagang_latest.log  # 最新日志链接
│   └── thetagang_*.log       # 历史日志
└── ib_insync.log         # IB API 日志
```

---

## ⚡ 紧急停止

如果脚本无法停止：
```bash
pkill -9 -f thetagang.main
rm thetagang.pid
```

---

## 📖 详细文档

- **完整指南**: `START_GUIDE.md`
- **代码修改**: `CODE_MODIFICATIONS.md`
- **问题修复**: `README_FIXES.md`
- **项目文档**: `README.md`

---

## 💡 示例工作流

### 早上启动
```bash
cd /Volumes/SecondSSD/Users/shiqipan/code/python/thetagang
./start.sh
./status.sh  # 确认运行正常
```

### 监控中
```bash
./view_logs.sh  # 选择"1"查看实时日志
# 或
tail -f logs/thetagang_latest.log
```

### 晚上停止
```bash
./stop.sh
```

### 第二天重启
```bash
./restart.sh
```

---

## 🎯 预期输出

**正常运行的日志应该包含**:
```
✅ Selected option chain with 428 strikes and 35 expirations
✅ Processing SPY: target=$1758700.00, market_price=$689.04
✅ Found suitable contract for SPY at strike=680.0 dte=35 price=$2.50
✅ Order submitted: SELL 3 SPY puts
```

**如果看到这些，需要注意**:
```
⚠️ Warning: Invalid market price (NaN or <=0)
⚠️ Need to write puts, but skipping because underlying is not red
⚠️ Timeout waiting on market data
```

---

**快速上手就这么简单！** 🚀
