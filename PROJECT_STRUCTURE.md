# ThetaGang 代码结构文档

## 项目概述
ThetaGang 是一个基于 Interactive Brokers (IBKR) 的自动化交易机器人，专门执行 "The Wheel" 期权策略。它通过卖出看跌期权（Puts）来获取权利金，并在需要时接手股票并转为卖出看涨期权（Covered Calls）。

## 核心模块结构

### 1. 入口点与 CLI
*   **[`thetagang/entry.py`](thetagang/entry.py)**: 程序的入口点，仅用于导入主模块。
*   **[`thetagang/main.py`](thetagang/main.py)**: 定义了命令行接口 (CLI)。
    *   使用 `click` 库处理命令行参数（如配置文件路径、是否启用 IBC 等）。
    *   负责初始化日志系统。
    *   调用 `thetagang.start` 启动主逻辑。

### 2. 主控制流程
*   **[`thetagang/thetagang.py`](thetagang/thetagang.py)**: 整个系统的编排者。
    *   **`start()`**:
        *   加载并校验 TOML 配置文件。
        *   初始化 `ib_insync.IB` 连接。
        *   管理 `IBC` (Interactive Brokers Controller) 实例，处理 TWS/Gateway 的自动登录。
        *   启动 `PortfolioManager` 进行投资组合管理。
        *   设置并启动 `Watchdog` 以监控连接状态。
        *   使用 `rich` 库在终端展示配置信息和状态。

### 3. 核心业务逻辑
*   **[`thetagang/portfolio_manager.py`](thetagang/portfolio_manager.py)**: 最核心的业务逻辑类 `PortfolioManager`。
    *   **职责**:
        *   监控账户状态、持仓和订单。
        *   执行 "The Wheel" 策略逻辑。
        *   决定何时卖出期权、何时滚动（Roll）期权合约。
        *   管理订单生命周期（创建、更新、取消）。
    *   **关键方法**:
        *   `manage()`: 主循环或触发点（在 `thetagang.py` 中被调用）。
        *   `orderStatusEvent()`: 处理订单状态变更回调。
        *   `get_options()`, `get_calls()`, `get_puts()`: 获取当前持仓中的期权信息。
        *   包含与 `ib_insync` 交互的具体逻辑，如获取市场数据、下单等。

### 4. 配置管理
*   **[`thetagang/config.py`](thetagang/config.py)**: 配置处理模块。
    *   **`validate_config()`**: 使用 `schema` 库定义配置文件的结构和验证规则。
    *   **`normalize_config()`**: 处理配置的向后兼容性、默认值合并及数据清洗（如将 `parts` 转换为 `weight`）。
*   **[`thetagang/config_defaults.py`](thetagang/config_defaults.py)**: (推测) 定义配置的默认值字典。
*   **[`thetagang/dict_merge.py`](thetagang/dict_merge.py)**: 提供递归合并字典的工具函数，用于将用户配置与默认配置合并。

### 5. 工具与辅助功能
*   **[`thetagang/util.py`](thetagang/util.py)**: 通用工具函数集合。
    *   **金融计算**: `get_target_delta` (获取目标 Delta), `position_pnl` (计算持仓盈亏)。
    *   **IBKR 数据处理**: `account_summary_to_dict`, `portfolio_positions_to_dict`, `midpoint_or_market_price` (获取中间价或市场价)。
    *   **持仓统计**: `count_short_option_positions`, `net_option_positions`。
    *   **价格获取**: `get_higher_price`, `get_lower_price` (基于模型价格和市场中间价的优选逻辑)。
*   **[`thetagang/options.py`](thetagang/options.py)**: 期权相关特定工具。
    *   `option_dte()`: 计算期权距离到期日的天数 (Days to Expiration)。
    *   `contract_date_to_datetime()`: 解析期权合约日期格式。
*   **[`thetagang/fmt.py`](thetagang/fmt.py)**: (推测) 格式化输出工具，用于 `rich` 终端展示的数值格式化（如百分比、货币格式）。

### 6. 外部依赖
*   **ib_insync**: 用于与 Interactive Brokers API 进行异步交互的核心库。
*   **IBC**: 用于自动化管理 IB Gateway/TWS 的登录和生命周期。
*   **Rich**: 用于构建美观的终端用户界面（表格、树状图、日志）。
*   **Click**: 用于构建命令行接口。
*   **Toml**: 配置文件格式解析。

## 数据流向
1.  **启动**: 用户运行 CLI -> `main.py` -> `thetagang.py`。
2.  **配置**: 读取 `thetagang.toml` -> `config.py` 校验并合并默认值。
3.  **连接**: `thetagang.py` 启动 IBC 和 IB 连接 -> 连接成功触发 `onConnected`。
4.  **策略执行**: `onConnected` 回调启动 `PortfolioManager.manage()`。
5.  **循环/事件**: `PortfolioManager` 根据市场数据（价格、Greeks）、账户数据（持仓、保证金）和配置规则，计算是否需要开仓、平仓或 Roll 仓位，并通过 `ib` 对象发送订单。
