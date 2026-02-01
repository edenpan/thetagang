# PortfolioManager 类方法详解

[`thetagang/portfolio_manager.py`](thetagang/portfolio_manager.py) 是 ThetaGang 的核心业务逻辑类，负责管理投资组合、执行期权策略和订单管理。

## 类初始化

### `__init__(config, ib, completion_future)`
**功能**: 初始化投资组合管理器
- 设置账户号码、配置、IB 连接和完成信号
- 注册订单状态事件监听器
- 初始化超额持仓追踪集合和订单队列

---

## 数据获取与等待方法

### `api_response_wait_time() -> int`
**功能**: 获取 API 响应等待时间配置

### `wait_for_midpoint_price(ticker, wait_time)`
**功能**: 等待获取期权的中间价（买卖价中点）
- 用于确保价格数据可用后再进行交易决策

### `wait_for_market_price(ticker, wait_time)`
**功能**: 等待获取市场价格
- 确保市场价格数据已就绪

### `wait_for_greeks(ticker, wait_time)`
**功能**: 等待获取期权的希腊字母（Greeks）数据
- 特别是 Delta 值，用于选择合适的期权合约

### `wait_for_market_price_for(tickers: list[Ticker], wait_time)`
**功能**: 批量等待多个合约的市场价格

### `wait_for_greeks_for(tickers: list[Ticker], wait_time)`
**功能**: 批量等待多个合约的希腊字母数据

### `wait_for_open_interest_for(tickers: list[Ticker], wait_time)`
**功能**: 等待获取期权的未平仓合约数（Open Interest）
- 用于过滤流动性不足的合约

---

## 合约与价格查询方法

### `get_chains_for_contract(contract)` 🔒缓存
**功能**: 获取指定标的的期权链信息
- 包含所有可用的行权价和到期日
- 使用 LRU 缓存提高性能

### `get_ticker_for_stock(symbol, primary_exchange, order_exchange=None)` 🔒缓存
**功能**: 获取股票的实时报价数据
- 创建股票合约并获取其 Ticker 对象

### `get_ticker_for(contract, midpoint=False)` 🔒缓存
**功能**: 获取任意合约的实时报价
- 可选择等待中间价或市场价

### `get_ticker_list_for(contracts)` 🔒缓存
**功能**: 批量获取多个合约的报价列表

---

## 持仓筛选与分类方法

### `get_calls(portfolio_positions)`
**功能**: 从持仓中筛选出所有看涨期权（Calls）

### `get_puts(portfolio_positions)`
**功能**: 从持仓中筛选出所有看跌期权（Puts）

### `get_options(portfolio_positions, right)`
**功能**: 根据期权类型（C/P）筛选期权持仓
- 只返回配置中指定的标的的期权

### `get_symbols()`
**功能**: 获取配置中所有交易标的列表

### `filter_positions(portfolio_positions)`
**功能**: 过滤持仓，只保留相关账户和标的的有效持仓

### `get_portfolio_positions()`
**功能**: 获取当前投资组合持仓并转换为字典格式

---

## 期权状态判断方法

### `put_is_itm(contract)`
**功能**: 判断看跌期权是否为实值（In The Money）
- 当行权价 >= 当前市场价时为 ITM

### `call_is_itm(contract)`
**功能**: 判断看涨期权是否为实值
- 当行权价 <= 当前市场价时为 ITM
- 特殊处理 VIX 指数期权

### `position_can_be_closed(position, table)`
**功能**: 判断持仓是否可以平仓
- 根据盈亏比例（P&L）决定是否达到平仓条件

### `put_can_be_closed(put, table)`
**功能**: 判断看跌期权是否可以平仓

### `put_can_be_rolled(put, table)`
**功能**: 判断看跌期权是否可以滚动（Roll）
- 检查 DTE（到期天数）、P&L、ITM 状态等条件
- 考虑是否有超额持仓

### `call_can_be_closed(call, table)`
**功能**: 判断看涨期权是否可以平仓

### `call_can_be_rolled(call, table)`
**功能**: 判断看涨期权是否可以滚动
- 类似 put_can_be_rolled，但针对看涨期权

---

## 账户管理方法

### `initialize_account()`
**功能**: 初始化账户设置
- 设置市场数据类型
- 取消现有的未完成订单（如果配置启用）

### `summarize_account()`
**功能**: 汇总并展示账户信息
- 显示净清算价值、保证金、购买力等
- 展示所有持仓的详细信息（包括期权的 DTE、行权价、P&L 等）
- 返回账户摘要和持仓字典

### `get_buying_power(account_summary)`
**功能**: 计算可用购买力
- 根据净清算价值和配置的保证金使用率计算

### `get_primary_exchange(symbol)`
**功能**: 获取标的的主交易所

### `get_maximum_new_contracts_for(symbol, primary_exchange, account_summary)`
**功能**: 计算可以开仓的最大合约数量
- 基于配置的最大新合约百分比和当前购买力

---

## 核心策略执行方法

### `manage()` ⭐核心方法
**功能**: 主策略执行流程
1. 初始化账户
2. 汇总账户和持仓信息
3. 检查是否可以卖出看跌期权（获取标的）
4. 检查未覆盖的股票持仓（需要卖出看涨期权）
5. 执行卖出期权操作
6. 检查可滚动和可平仓的期权
7. 执行滚动和平仓操作
8. VIX 对冲管理
9. 现金管理
10. 提交所有订单并等待执行

### `check_if_can_write_puts(account_summary, portfolio_positions)`
**功能**: 检查是否可以卖出看跌期权
- 计算每个标的的目标持仓数量
- 确定需要卖出的看跌期权数量
- 考虑"只在红盘时卖出"的配置
- 返回持仓摘要表、操作表和待卖出列表

### `check_for_uncovered_positions(account_summary, portfolio_positions)`
**功能**: 检查未覆盖的股票持仓
- 计算需要卖出的看涨期权数量（Covered Calls）
- 考虑"只在绿盘时卖出"的配置
- 返回操作表和待卖出列表

### `check_puts(portfolio_positions)`
**功能**: 检查看跌期权的状态
- 识别可滚动和可平仓的看跌期权
- 返回可操作的期权列表和摘要

### `check_calls(portfolio_positions)`
**功能**: 检查看涨期权的状态
- 识别可滚动和可平仓的看涨期权

---

## 期权交易操作方法

### `write_puts(puts)`
**功能**: 卖出看跌期权（开仓）
- 为每个标的查找符合条件的期权合约
- 创建限价卖单并加入订单队列

### `write_calls(calls)`
**功能**: 卖出看涨期权（开仓）
- 类似 write_puts，但针对看涨期权

### `close_positions(positions)`
**功能**: 平仓期权持仓
- 创建买单（对于空头）或卖单（对于多头）
- 使用较低/较高价格以提高成交概率

### `close_puts(puts)`
**功能**: 平仓看跌期权（调用 close_positions）

### `close_calls(calls)`
**功能**: 平仓看涨期权（调用 close_positions）

### `roll_positions(positions, right, account_summary, portfolio_positions=None)`
**功能**: 滚动期权持仓 ⭐复杂操作
- 买入当前持仓（平仓）
- 同时卖出新的期权合约（开仓）
- 使用组合订单（BAG）执行
- 计算行权价限制，确保不会过度增加风险
- 支持"仅信用滚动"配置

### `roll_puts(puts, account_summary)`
**功能**: 滚动看跌期权

### `roll_calls(calls, account_summary, portfolio_positions)`
**功能**: 滚动看涨期权

---

## 合约搜索与筛选方法

### `find_eligible_contracts(...)` ⭐核心算法
**功能**: 查找符合条件的期权合约
**参数**:
- `main_contract`: 标的合约
- `right`: 期权类型（C/P）
- `strike_limit`: 行权价限制
- `exclude_expirations_before`: 排除早于此日期的到期日
- `exclude_exp_strike`: 排除特定行权价和到期日组合
- `minimum_price`: 最低价格要求
- `preferred_minimum_price`: 首选最低价格
- `target_dte`: 目标到期天数
- `target_delta`: 目标 Delta 值

**流程**:
1. 获取期权链
2. 筛选有效的行权价（基于当前价格和限制）
3. 筛选有效的到期日（基于目标 DTE）
4. 生成所有可能的合约组合
5. 请求市场数据
6. 按以下条件过滤：
   - 价格有效性
   - Delta 在目标范围内
   - 未平仓合约数满足最低要求
7. 排序并选择最佳合约
8. 如果找不到理想合约，放宽 Delta 限制重试

---

## 订单管理方法

### `enqueue_order(contract, order)`
**功能**: 将订单加入队列
- 不立即提交，等待批量处理

### `submit_orders()`
**功能**: 批量提交所有排队的订单
- 调用 IB API 下单
- 展示订单摘要表

### `adjust_prices()`
**功能**: 调整未成交订单的价格
- 在配置的延迟后更新限价单价格
- 使用最新的中间价
- 特殊处理组合订单（BAG）

### `wait_for_pending_orders()`
**功能**: 等待订单执行完成
- 监控订单状态直到全部完成或超时

### `orderStatusEvent(trade)`
**功能**: 订单状态变更事件处理器
- 打印订单成交、取消或更新信息

---

## 高级功能方法

### `do_vix_hedging(account_summary, portfolio_positions)`
**功能**: VIX 看涨期权对冲管理
- 基于 VIXMO（VIX 月度期货）价格决定对冲权重
- 购买 VIX 看涨期权作为尾部风险对冲
- 当 VIX 超过阈值时平仓对冲头寸
- 实现类似 CBOE VXTH 指数的策略

### `do_cashman(account_summary, portfolio_positions)`
**功能**: 现金管理
- 监控现金余额
- 当现金超过目标+阈值时，买入现金管理基金（如 SGOV）
- 当现金低于目标-阈值时，卖出现金管理基金
- 优化现金收益率

---

## 配置获取方法

### `get_algo_strategy()`
**功能**: 获取订单算法策略名称

### `get_algo_params()`
**功能**: 获取订单算法参数

### `get_order_exchange()`
**功能**: 获取订单交易所

---

## 方法调用流程图

```
manage() [主入口]
├── initialize_account()
├── summarize_account()
│   ├── get_portfolio_positions()
│   └── [显示账户和持仓信息]
├── check_if_can_write_puts()
│   ├── get_ticker_for_stock()
│   └── [计算目标持仓]
├── check_for_uncovered_positions()
│   └── [计算需要的 Covered Calls]
├── write_puts()
│   └── find_eligible_contracts() ⭐
│       ├── get_chains_for_contract()
│       ├── wait_for_greeks_for()
│       └── wait_for_open_interest_for()
├── write_calls()
│   └── find_eligible_contracts() ⭐
├── check_puts()
│   ├── put_can_be_rolled()
│   └── put_can_be_closed()
├── check_calls()
│   ├── call_can_be_rolled()
│   └── call_can_be_closed()
├── roll_puts()
│   └── roll_positions()
│       └── find_eligible_contracts() ⭐
├── roll_calls()
│   └── roll_positions()
├── close_puts()
│   └── close_positions()
├── close_calls()
│   └── close_positions()
├── do_vix_hedging()
│   └── find_eligible_contracts()
├── do_cashman()
├── submit_orders()
├── wait_for_pending_orders()
├── adjust_prices()
└── wait_for_pending_orders()
```

---

## 关键设计模式

1. **订单队列模式**: 所有订单先加入队列，最后批量提交，提高效率
2. **缓存装饰器**: 使用 `@lru_cache` 缓存市场数据查询，减少 API 调用
3. **策略模式**: 通过配置驱动不同的交易决策（如只在红盘/绿盘时交易）
4. **事件驱动**: 使用 `orderStatusEvent` 监听订单状态变化
5. **异常容错**: 大量使用 try-except 确保单个操作失败不影响整体流程

---

## 重要配置项影响的方法

- `roll_when.dte`: 影响 `put_can_be_rolled`, `call_can_be_rolled`
- `roll_when.pnl`: 影响滚动决策
- `roll_when.close_at_pnl`: 影响 `position_can_be_closed`
- `target.delta`: 影响 `find_eligible_contracts` 的合约选择
- `target.dte`: 影响目标到期日选择
- `write_when.calls.green`: 影响 `check_for_uncovered_positions`
- `write_when.puts.red`: 影响 `check_if_can_write_puts`
- `account.margin_usage`: 影响 `get_buying_power`
