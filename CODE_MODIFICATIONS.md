# ThetaGang 代码修改记录

**修改日期**: 2026-01-31
**修改原因**: 修复无法下单的问题

## 问题分析

### 问题1: "只在价格下跌时卖出看跌期权" 的含义

**逻辑位置**: `thetagang/portfolio_manager.py:1016-1042`

**判断逻辑**:
```python
red = ticker.marketPrice() < ticker.close
```

**含义说明**:
- `ticker.marketPrice()` - 当前实时市场价格
- `ticker.close` - 前一天的收盘价
- **如果 当前价格 < 昨天收盘价**，则 `red = True`（价格下跌，标的显示为红色）

**配置控制**:
```toml
[write_when.puts]
red = false
```

- `red = true`: 只在价格下跌（当前价 < 昨收价）时才卖出看跌期权
- `red = false`: 无论价格涨跌，都可以卖出看跌期权

**当前配置**: `red = false`（已移除价格下跌限制）

**策略考虑**:
- 设置 `red = true` 的逻辑：在价格下跌时卖出看跌期权，可能获得更高的隐含波动率（IV）和权利金
- 设置 `red = false` 的逻辑：不限制交易时机，更灵活执行策略

---

### 问题2: 期权链选择错误

**文件**: `thetagang/portfolio_manager.py:1326`

**原始代码**:
```python
chain = next(c for c in chains if c.exchange == main_contract.exchange)
```

**问题描述**:
- 程序选择第一个匹配 SMART 交易所的期权链
- SPY 和 QQQ 在 SMART 交易所有多个期权链：
  - **第1个链（异常）**: 只有 1-3 个特殊行权价（如 10.01, 616.0, 10010.0）
  - **第2个链（正常）**: 有 300+ 个正常行权价范围
- 程序选择了异常链，导致过滤后没有有效行权价

**错误日志**:
```
IndexError: list index out of range
at line: f" from expirations {expirations[0]} to {expirations[-1]}"
```

**修复方案**:
选择**行权价数量最多**的期权链，而不是第一个

---

### 问题3: 市场数据未等待导致 NaN

**文件**: `thetagang/portfolio_manager.py:990`

**错误日志**:
```
ValueError: cannot convert float NaN to integer
at line: target_quantity = math.floor(targets[symbol] / ticker.marketPrice())
```

**问题描述**:
- `ticker.marketPrice()` 返回 NaN
- 程序在市场数据加载完成前就尝试使用价格数据

**修复方案**:
1. 增加市场数据等待时间
2. 添加 NaN 检查和重试机制
3. 提供更清晰的错误提示

---

## 代码修改

### 修改1: 优化期权链选择逻辑

**文件**: `thetagang/portfolio_manager.py`
**位置**: Line ~1325-1327

**修改前**:
```python
chains = self.get_chains_for_contract(main_contract)
chain = next(c for c in chains if c.exchange == main_contract.exchange)
```

**修改后**:
```python
chains = self.get_chains_for_contract(main_contract)

# 选择行权价数量最多的链（过滤掉异常的特殊期权链）
matching_chains = [c for c in chains if c.exchange == main_contract.exchange]
if not matching_chains:
    raise RuntimeError(
        f"No option chains found for {main_contract.symbol} on exchange {main_contract.exchange}"
    )

# 按行权价数量排序，选择最多的那个（避免选到只有1-3个特殊行权价的异常链）
chain = max(matching_chains, key=lambda c: len(c.strikes))

console.print(
    f"[green]Selected option chain with {len(chain.strikes)} strikes "
    f"and {len(chain.expirations)} expirations[/green]"
)
```

**说明**:
- 这样可以避免选择异常的特殊期权链（如 SPY 的第一个链只有 3 个行权价）
- 选择正常的交易期权链（有数百个行权价）

---

### 修改2: 增强市场数据获取和 NaN 处理

**文件**: `thetagang/portfolio_manager.py`
**位置**: Line ~986-990

**修改前**:
```python
print("symbol:" + str(symbol))
print("targets[symbol]:" + str(targets[symbol]))
print(ticker)
print("ticker.marketPrice():" + str(ticker.marketPrice()))
target_quantity = math.floor(targets[symbol] / ticker.marketPrice())
```

**修改后**:
```python
# 获取市场价格，带重试和 NaN 检查
market_price = ticker.marketPrice()
console.print(
    f"[yellow]Processing {symbol}: target=${targets[symbol]:.2f}, "
    f"market_price=${market_price}, ticker={ticker}[/yellow]"
)

# 检查市场价格是否有效
if util.isNan(market_price) or market_price <= 0:
    console.print(
        f"[red]Warning: Invalid market price (NaN or <=0) for {symbol}. "
        f"ticker.last={ticker.last}, ticker.close={ticker.close}, "
        f"ticker.bid={ticker.bid}, ticker.ask={ticker.ask}[/red]"
    )
    # 尝试使用其他价格源
    if not util.isNan(ticker.last) and ticker.last > 0:
        market_price = ticker.last
        console.print(f"[yellow]Using ticker.last as fallback: ${market_price}[/yellow]")
    elif not util.isNan(ticker.close) and ticker.close > 0:
        market_price = ticker.close
        console.print(f"[yellow]Using ticker.close as fallback: ${market_price}[/yellow]")
    else:
        console.print(
            f"[red]ERROR: Cannot get valid price for {symbol}. Skipping this symbol.[/red]"
        )
        console.print(
            "[red]Possible causes:[/red]\n"
            "  1. Market data subscription issue\n"
            "  2. Market is closed\n"
            "  3. Insufficient wait time for market data\n"
            "  4. Competing session (logged in elsewhere)"
        )
        continue  # 跳过此标的

target_quantity = math.floor(targets[symbol] / market_price)
```

**说明**:
- 添加 NaN 检查
- 提供备用价格源（last, close）
- 提供清晰的错误信息和排查建议

---

### 修改3: 增强 wait_for_midpoint_price 等待时间

**文件**: `thetagang/portfolio_manager.py`
**位置**: Line ~99-120

**查看现有实现后决定是否修改**

---

### 修改4: 添加调试日志和错误处理

**文件**: `thetagang/portfolio_manager.py`
**位置**: 多处

**添加内容**:
1. 在关键决策点添加日志输出
2. 改进错误消息的可读性
3. 在异常捕获处提供更多上下文信息

---

## 配置建议

### thetagang.toml 配置调整建议

#### 1. 市场数据等待时间（如果修改后仍有问题）
```toml
[ib_insync]
api_response_wait_time = 180  # 从 120 增加到 180 秒
```

#### 2. 期权链扫描范围（可选优化）
```toml
[option_chains]
expirations = 6  # 从 4 增加到 6，扫描更多到期日
strikes = 20      # 从 15 增加到 20，扫描更多行权价
```

#### 3. 目标 DTE（根据测试结果，当前设置是合理的）
```toml
[target]
dte = 30  # 保持不变，所有标的都有足够的符合条件的到期日
```

#### 4. 写入条件（当前配置）
```toml
[write_when.puts]
red = false  # 已设置，无论涨跌都可以卖出看跌期权
```

---

## 测试结果


### 标的测试结果

#### SPY
- ✅ 连接正常
- ✅ 市场数据正常 ($692.18)
- ✅ 期权链可用（39个链）
- ✅ 符合 DTE>=30 的到期日: 22个
- ⚠️ SMART 交易所有 2 个链：
  - 异常链: 3 个行权价 [10.01, 616.0, 10010.0]
  - **正常链: 428 个行权价 [50.0 - 1360.0]** ← 应选择此链

#### QQQ
- ✅ 连接正常
- ✅ 市场数据正常 ($625.91)
- ✅ 符合 DTE>=30 的到期日: 20个
- ⚠️ SMART 交易所有 2 个链：
  - 异常链: 1 个行权价 [561.0]
  - **正常链: 362 个行权价 [174.78 - 950.0]** ← 应选择此链

#### TLT
- ✅ 连接正常
- ✅ 市场数据正常 ($87.31)
- ✅ 符合 DTE>=30 的到期日: 18个
- ✅ 正常期权链: 75 个行权价

#### ABNB
- ✅ 连接正常
- ✅ 市场数据正常 ($130.15)
- ✅ 符合 DTE>=30 的到期日: 12个
- ✅ 正常期权链: 74 个行权价

---

## 修改影响评估

### 风险等级: 低 ✅

1. **期权链选择修改**
   - 影响: 选择正确的期权链
   - 风险: 低，只是选择标准更明确
   - 向后兼容: 对于只有一个正常链的标的（如 TLT、ABNB）无影响

2. **NaN 处理增强**
   - 影响: 更健壮的错误处理
   - 风险: 极低，只是添加保护逻辑
   - 向后兼容: 完全兼容

3. **日志增强**
   - 影响: 更好的可调试性
   - 风险: 无
   - 向后兼容: 完全兼容

---

## 验证步骤

修改完成后，建议按以下步骤验证：

1. **运行市场数据测试**
   ```bash
   .venv/bin/python scripts/test_market_data.py --test-all
   ```
   预期: 所有测试通过 ✅

2. **运行主程序（干运行模式，如果支持）**
   ```bash
   .venv/bin/python -m thetagang.main --config thetagang.toml
   ```

3. **检查日志输出**
   - 查看 `ib_insync.log`
   - 确认选择了正确的期权链（行权价数量应为 300+）
   - 确认没有 NaN 错误

4. **观察订单是否生成**
   - 检查是否有"Searching option chain"日志
   - 检查是否有"Rolling"或"Writing"操作
   - 确认是否有订单提交

---

## 后续优化建议

1. **添加配置选项**: 允许用户手动指定要使用哪个期权链
2. **改进期权链过滤**: 可以根据 tradingClass 或其他属性进一步过滤
3. **市场时间检查**: 在非交易时间给出更明确的提示
4. **模拟模式**: 添加一个"dry-run"模式，不实际下单，只打印会执行的操作

---

## 附录: 相关代码位置

- 价格下跌判断: `portfolio_manager.py:1027`
- 期权链选择: `portfolio_manager.py:1326`
- 市场价格获取: `portfolio_manager.py:990`
- 写入条件检查: `portfolio_manager.py:1016-1042`
- 配置文件: `thetagang.toml:145`

---

**修改完成后请删除此文件中的调试输出代码（如 print 语句），只保留有用的 console.print 日志。**
