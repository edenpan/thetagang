# ThetaGang 启动指南

## 📋 前置检查清单

在运行程序前，请确保：

- [ ] IB Gateway 已启动并运行
- [ ] IB Gateway 端口设置为 **4002** (Paper Trading)
- [ ] IB Gateway 已启用 API 连接
- [ ] 网络连接正常
- [ ] 当前时间在美东交易时间内（可选，非交易时间会有数据延迟）

---

## 🚀 快速启动

### 方法 1: 使用启动脚本（推荐）

```bash
# 运行启动脚本
./start.sh
```

启动脚本会自动：
- ✅ 检查 IB Gateway 连接
- ✅ 创建带时间戳的日志文件
- ✅ 在后台运行程序
- ✅ 保存 PID 以便后续管理

### 方法 2: 直接命令行启动

```bash

# 前台运行（会占用终端，可以看到实时输出）
.venv/bin/python -m thetagang.main --config thetagang.toml

# 或后台运行（不占用终端）
nohup .venv/bin/python -m thetagang.main --config thetagang.toml > logs/thetagang_$(date +%Y%m%d_%H%M%S).log 2>&1 &
echo $! > thetagang.pid
```

---

## 📊 查看运行状态

### 查看程序是否运行

```bash
./status.sh
```

或手动检查：

```bash
# 检查进程
ps aux | grep thetagang | grep -v grep

# 或查看 PID 文件
if [ -f thetagang.pid ]; then
    echo "程序正在运行，PID: $(cat thetagang.pid)"
else
    echo "程序未运行"
fi
```

### 查看实时日志

```bash
./view_logs.sh
```

或手动查看：

```bash
# 查看最新的应用日志
tail -f logs/thetagang_*.log | tail -100

# 查看 IB API 日志
tail -f ib_insync.log

# 只看错误
grep -i "error\|exception\|fail" logs/thetagang_*.log
```

---

## 🛑 停止程序

### 使用停止脚本

```bash
./stop.sh
```

### 手动停止

```bash
# 如果有 PID 文件
kill $(cat thetagang.pid)
rm thetagang.pid

# 或强制停止所有 thetagang 进程
pkill -f "thetagang.main"
```

---

## 🔄 重启程序

```bash
./restart.sh
```

或手动：

```bash
./stop.sh
sleep 5
./start.sh
```

---

## 📁 日志文件位置

所有日志文件保存在 `logs/` 目录：

```
logs/
├── thetagang_20260131_093000.log  # 应用日志（带时间戳）
├── thetagang_20260131_140000.log
└── thetagang_latest.log           # 最新日志的符号链接
```

IB API 日志：
```
ib_insync.log  # IB API 连接和交易日志
```

---

## 🕐 最佳运行时间

**推荐在美东交易时间运行**：
- 美东时间：周一至周五 9:30 AM - 4:00 PM
- 北京时间（冬令时）：周一至周五 22:30 PM - 次日 5:00 AM
- 北京时间（夏令时）：周一至周五 21:30 PM - 次日 4:00 AM

**非交易时间运行**：
- ⚠️ 可以运行，但市场数据可能延迟或不完整
- ⚠️ 订单会排队等待市场开盘

---

## 🔧 常见问题排查

### 1. 无法连接 IB Gateway

**症状**：日志显示 "Connection refused" 或 "Connection timeout"

**解决方法**：
```bash
# 检查 IB Gateway 是否运行
ps aux | grep -i "ib\|gateway\|tws"

# 检查端口是否开放
lsof -i :4002

# 重启 IB Gateway
# （在 IB Gateway 应用中重启）
```

### 2. 程序启动后立即退出

**解决方法**：
```bash
# 查看日志中的错误
tail -50 logs/thetagang_*.log

# 检查配置文件
.venv/bin/python -c "import toml; print(toml.load('thetagang.toml'))"

# 测试 IB 连接
.venv/bin/python scripts/test_market_data.py
```

### 3. 找不到合适的期权合约

**症状**：日志显示 "No valid strikes found" 或 "No valid expirations found"

**解决方法**：
```bash
# 检查配置的 DTE 是否太高
# 编辑 thetagang.toml，调整：
[target]
dte = 25  # 从 30 降低到 25

# 检查市场数据订阅
# 确保在 IBKR 账户中订阅了相关市场数据
```

### 4. NaN 价格错误

**症状**：日志显示 "cannot convert float NaN to integer"

**解决方法**：
- ✅ 代码已修复（自动使用备用价格源）
- 如果仍出现，增加等待时间：
  ```toml
  [ib_insync]
  api_response_wait_time = 180
  ```

### 5. 选择了错误的期权链

**症状**：日志显示 "Valid strikes: [10.01, 616.0]" （只有2-3个行权价）

**解决方法**：
- ✅ 代码已修复（自动选择最多行权价的链）
- 验证修复：
  ```bash
  .venv/bin/python test_chain_selection.py
  ```

---

## 📈 监控运行状态

### 关键日志信息

**✅ 正常运行**：
```
Selected option chain with 428 strikes and 35 expirations
Processing SPY: target=$1758700.00, market_price=$689.04
Found suitable contract for SPY at strike=680.0 dte=35 price=$2.50
Order submitted: SELL 3 SPY puts at $680 strike
```

**⚠️ 需要注意**：
```
Warning: Invalid market price (NaN or <=0) for SPY
Need to write 25 puts, but skipping because underlying is not red
Timeout waiting on market data for contracts
```

**❌ 错误**：
```
Error: cannot convert float NaN to integer
IndexError: list index out of range
Connection refused
```

---

## 🎯 程序运行流程

1. **连接 IB Gateway**
   - 加载配置文件
   - 连接到 IB API
   - 验证账户和权限

2. **获取账户信息**
   - 净资产
   - 购买力
   - 当前持仓

3. **计算目标持仓**
   - 根据配置的权重分配资金
   - 计算每个标的需要的合约数量

4. **检查写入条件**
   - 检查是否满足 write_when 条件
   - 检查价格变化（如果配置了 red/green）

5. **搜索期权合约**
   - 获取期权链
   - 筛选符合条件的合约（DTE, Delta, OI）
   - 选择最佳合约

6. **提交订单**
   - 生成限价单
   - 提交到 IB Gateway
   - 等待成交

7. **持续监控**
   - 检查持仓状态
   - 检查是否需要平仓
   - 检查是否需要滚动
   - 循环执行

---

## 🔐 安全提示

1. **Paper Trading 优先**
   - 建议先在 Paper Trading 账户测试
   - 确认策略符合预期后再切换到实盘

2. **监控初次运行**
   - 第一次运行时保持前台运行
   - 观察日志输出
   - 验证订单价格和数量

3. **设置合理限制**
   - 使用 `maximum_new_contracts` 限制单次最大合约数
   - 使用 `margin_usage` 控制资金使用比例
   - 使用 `strike_limit` 限制行权价范围

4. **定期检查**
   - 每天检查持仓状态
   - 每周检查策略表现
   - 根据市场情况调整参数

---

## 📞 获取帮助

**查看项目文档**：
- README.md
- CODE_MODIFICATIONS.md
- README_FIXES.md

**日志分析**：
```bash
# 查看所有订单
grep -i "order\|submitted" logs/thetagang_*.log

# 查看所有错误
grep -i "error\|exception" logs/thetagang_*.log

# 查看期权链选择
grep -i "selected option chain" logs/thetagang_*.log
```

**测试脚本**：
```bash
# 测试市场数据
.venv/bin/python scripts/test_market_data.py --test-all

# 测试标的
.venv/bin/python test_symbols.py

# 测试期权链选择
.venv/bin/python test_chain_selection.py

# 验证修复
.venv/bin/python verify_fixes.py
```

---

**祝交易顺利！** 📈
