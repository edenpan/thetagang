# ThetaGang 无法下单问题修复 - 用户指南

**修复日期**: 2026-01-31
**状态**: ✅ 已完成并验证

---

## 📋 问题总结

你的 ThetaGang 程序无法下单，主要有以下问题：

### 1. **期权链选择错误** ❌
- **问题**: SPY 和 QQQ 在 SMART 交易所有多个期权链，程序选择了第一个异常链
- **异常链**: 只有 1-3 个特殊行权价（如 10.01, 616.0, 10010.0），不是正常交易期权
- **结果**: 过滤后没有有效合约，触发 `IndexError: list index out of range`

### 2. **市场数据未加载** ❌
- **问题**: 程序在市场数据完全加载前就尝试使用价格
- **结果**: `ticker.marketPrice()` 返回 NaN，触发 `ValueError: cannot convert float NaN to integer`

### 3. **"只在价格下跌时卖出" 配置** ℹ️
- **配置**: `write_when.puts.red = false`（已正确配置）
- **含义**: 不限制交易时机，无论涨跌都可以卖出看跌期权
- **判断**: `red = ticker.marketPrice() < ticker.close`（当前价 < 昨收价）

---

## ✅ 已完成的修复

### 修复 1: 优化期权链选择 🎯

**修改位置**: `thetagang/portfolio_manager.py:1325-1341`

**修改内容**:
- 从"选择第一个匹配的链" → "选择行权价最多的链"
- 添加错误检查和日志输出

**验证结果**:
- ✅ SPY: 现在选择有 428 个行权价的正常链（之前选了只有 3 个的异常链）
- ✅ QQQ: 现在选择有 362 个行权价的正常链（之前选了只有 1 个的异常链）

### 修复 2: 增强 NaN 处理 🛡️

**修改位置**: `thetagang/portfolio_manager.py:986-1020`

**修改内容**:
- 添加 NaN 检查
- 提供备用价格源（ticker.last, ticker.close）
- 优雅跳过有问题的标的，不会崩溃
- 提供清晰的错误信息

**验证结果**:
- ✅ 能正确识别和处理 NaN、零值、负值
- ✅ 自动使用备用价格源
- ✅ 给出清晰的排查建议

---

## 🧪 验证测试结果

### 运行验证脚本
```bash
.venv/bin/python verify_fixes.py
```

**测试结果**: 🎉 所有测试通过！

```
================================================================================
测试结果总结
================================================================================
  期权链选择               : ✅ 通过
  NaN 处理              : ✅ 通过

🎉 所有测试通过！代码修改验证成功！
```

### SPY 测试结果
- 找到 2 个 SMART 交易所的期权链
  - 链 #1: 3 个行权价（异常链）
  - 链 #2: 428 个行权价（正常链）✅ 已选择
- **验证通过**: 选择了正常的期权链

### QQQ 测试结果
- 找到 2 个 SMART 交易所的期权链
  - 链 #1: 1 个行权价（异常链）
  - 链 #2: 362 个行权价（正常链）✅ 已选择
- **验证通过**: 选择了正常的期权链

---

## 🚀 下一步操作

### 1. 运行主程序
```bash
.venv/bin/python -m thetagang.main --config thetagang.toml
```

### 2. 观察日志输出

**期待看到的日志** ✅:
```
Selected option chain with 428 strikes and 35 expirations  # SPY
Selected option chain with 362 strikes and 33 expirations  # QQQ
Processing SPY: target=$400000.00, market_price=$692.18
Processing QQQ: target=$300000.00, market_price=$625.91
Searching option chain for symbol=SPY right=P, strike_limit=1000.0...
```

**不应再出现的错误** ❌:
```
IndexError: list index out of range
ValueError: cannot convert float NaN to integer
```

### 3. 检查订单生成

如果满足交易条件（目标持仓 vs 当前持仓），程序应该能够：
- ✅ 找到符合条件的期权合约（Delta ~0.3, DTE ~30）
- ✅ 生成卖出看跌期权的订单
- ✅ 提交订单到 IB Gateway

---

## 📚 "价格下跌"逻辑详解

### 配置位置
```toml
[write_when.puts]
red = false
```

### 判断代码
**位置**: `thetagang/portfolio_manager.py:1027`

```python
red = ticker.marketPrice() < ticker.close
```

### 详细说明

#### 价格比较
- `ticker.marketPrice()` - **当前实时市场价格**（买卖价中间价）
- `ticker.close` - **前一交易日的收盘价**

#### 判断逻辑
- **red = True**: 当前价 < 昨收价（价格下跌，通常显示为红色）
- **red = False**: 当前价 >= 昨收价（价格上涨或持平，通常显示为绿色）

#### 配置影响

**当 `red = true` 时**（只在下跌时交易）:
```python
if not red:  # 如果价格没跌
    print("跳过，因为价格没有下跌")
    return False  # 不卖期权
```

**当 `red = false` 时**（不限制，当前配置）:
```python
if not write_only_when_red:  # 不需要价格下跌
    return True  # 可以卖期权
```

#### 策略考虑

**设置 `red = true` 的理由**:
- ✅ 价格下跌时，市场恐慌，隐含波动率(IV)通常较高
- ✅ IV 高 → 期权价格高 → 收取更多权利金
- ✅ 符合"贪婪时恐惧，恐惧时贪婪"的原则
- ❌ 限制: 错过上涨时的交易机会，可能减少整体交易频率

**设置 `red = false` 的理由**（当前设置）:
- ✅ 不限制交易时机，更灵活执行 Wheel 策略
- ✅ 增加交易机会，保持资金利用率
- ✅ 适合长期系统化策略
- ❌ 可能在 IV 较低时卖出期权，权利金较少

#### 额外阈值检查

如果设置 `red = true`，还可以配置最小跌幅要求：

**配置示例**:
```toml
[symbols.QQQ.puts]
write_threshold = 0.01  # 要求至少下跌 1%
```

**判断逻辑**:
```python
absolute_daily_change = abs((ticker.marketPrice() - ticker.close) / ticker.close)
if absolute_daily_change < write_threshold:
    print(f"跳过，跌幅 {absolute_daily_change:.2%} < 阈值 {write_threshold:.2%}")
    return False
```

#### 示例场景

**场景 1**: SPY 昨收 $694.04，今日 $692.18
- `red = True`（下跌）
- 跌幅 = (692.18 - 694.04) / 694.04 = -0.27%
- 如果 `red = true` 且 `write_threshold = 0.01`，则可以卖出期权

**场景 2**: QQQ 昨收 $620.00，今日 $625.91
- `red = False`（上涨）
- 涨幅 = +0.95%
- 如果 `red = true`，则跳过不卖
- 如果 `red = false`（当前配置），则可以卖出期权

---

## 📊 配置建议

### 当前配置分析

你的 `thetagang.toml` 配置：

```toml
[target]
dte = 30              # 目标到期天数 - ✅ 合理
delta = 0.3           # 目标 Delta - ✅ 合理
minimum_open_interest = 10  # 最小持仓量 - ✅ 合理

[symbols.SPY]
weight = 0.4          # 40% 资金 - ✅ 合理

[symbols.QQQ]
weight = 0.3          # 30% 资金 - ✅ 合理
[symbols.QQQ.puts]
delta = 0.5           # QQQ 使用更高的 Delta - ✅ 更激进
strike_limit = 1000.0 # 最高行权价 $1000 - ✅ 合理
write_threshold = 0.01 # 最小跌幅 1% - ⚠️ 但 red=false，此项无效

[write_when.puts]
red = false           # 不限制交易时机 - ✅ 灵活
```

### 优化建议（可选）

#### 1. 如果想在下跌时获取更高 IV
```toml
[write_when.puts]
red = true  # 改为 true

# 为每个标的设置合理的阈值
[symbols.SPY.puts]
write_threshold = 0.005  # SPY 波动小，0.5% 即可

[symbols.QQQ.puts]
write_threshold = 0.01   # QQQ 波动大，1%

[symbols.TLT.puts]
write_threshold = 0.01

[symbols.ABNB.puts]
write_threshold = 0.02   # 个股波动更大，2%
```

#### 2. 如果市场数据仍有延迟
```toml
[ib_insync]
api_response_wait_time = 180  # 从 120 增加到 180
```

#### 3. 如果需要更多合约选择
```toml
[option_chains]
expirations = 6  # 从 4 增加到 6
strikes = 20     # 从 15 增加到 20
```

---

## 🔍 故障排查

### 如果程序仍然无法下单

#### 检查 1: 账户状态
```bash
# 运行测试脚本检查连接和账户
.venv/bin/python scripts/test_market_data.py
```

预期: ✅ 所有测试通过

#### 检查 2: 查看日志
```bash
tail -50 ib_insync.log
```

常见错误:
- **Error 10197**: 竞争会话（其他地方登录了同一账户）
- **Error 2107**: 市场数据农场连接问题
- **Error 200**: 合约描述模糊（需要指定 primary_exchange）

#### 检查 3: 交易条件
程序只有在满足以下条件时才会下单：

1. **有足够的购买力**
   - `margin_usage = 0.5` → 使用 50% 资金
   - 检查: 账户净值 * 0.5 是否足够

2. **目标持仓 > 当前持仓**
   - 如果已经持有足够的股票或期权，不会再卖出

3. **满足 write_when 条件**
   - 如果设置了 `red = true`，必须价格下跌
   - 如果设置了 `green = true`（calls），必须价格上涨

4. **找到符合条件的合约**
   - DTE >= 30
   - Delta ~0.3（或配置的值）
   - Open Interest >= 10

#### 检查 4: 运行干运行测试
```bash
# 添加详细日志
.venv/bin/python -m thetagang.main --config thetagang.toml 2>&1 | tee run.log
```

查看 `run.log` 确认:
- ✅ 选择了正确的期权链（300+ 行权价）
- ✅ 没有 NaN 或 IndexError
- ✅ 计算了目标持仓数量
- ✅ 搜索了期权合约

---

## 📁 相关文件

### 文档
- `CODE_MODIFICATIONS.md` - 详细技术修改文档
- `MODIFICATIONS_SUMMARY.md` - 修改总结
- `README_FIXES.md` - 本文档（用户指南）

### 脚本
- `scripts/test_market_data.py` - 市场数据测试脚本
- `test_symbols.py` - 标的测试脚本
- `verify_fixes.py` - 修复验证脚本

### 主程序
- `thetagang/portfolio_manager.py` - 已修改
- `thetagang.toml` - 配置文件

---

## ⚠️ 重要提示

1. **先在 Paper Trading 测试**
   - 确认程序运行正常后再用于实盘
   - Paper 账户: DU7122999（你当前使用的）

2. **监控首次运行**
   - 检查日志确认选择了正确的合约
   - 验证订单价格和数量
   - 确认策略执行符合预期

3. **理解风险**
   - Wheel 策略可能导致持有股票（如果 Put 被行权）
   - 确保有足够资金支持
   - 了解期权基础知识和风险

4. **市场时间**
   - 美股交易时间: 美东 9:30-16:00
   - 期权交易: 美东 9:30-16:00
   - 在非交易时间运行可能获取不到实时数据

---

## 📞 获取帮助

如果仍有问题:

1. **查看项目文档**
   - README.md
   - 项目 GitHub: https://github.com/brndnmtthws/thetagang

2. **检查日志**
   - `ib_insync.log`
   - 程序输出

3. **社区支持**
   - Reddit: r/thetagang
   - GitHub Issues

---

**修改完成！祝交易顺利！** 📈
