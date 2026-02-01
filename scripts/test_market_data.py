#!/usr/bin/env python3
"""
IB Gateway 市场数据测试脚本

用于测试和诊断 IB Gateway 的市场数据连接问题。
可以测试股票、期权的实时行情数据获取。

使用方法:
    # 激活虚拟环境
    source .venv/bin/activate
    
    # 运行测试脚本
    python scripts/test_market_data.py
    
    # 或者指定参数
    python scripts/test_market_data.py --host 127.0.0.1 --port 4002 --symbol SPY
"""

import argparse
import logging
import sys
import time
from datetime import datetime

from ib_insync import IB, Stock, Option, Index, util

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def wait_with_updates(ib: IB, seconds: int, message: str = "等待中"):
    """等待指定秒数，同时处理 IB 事件"""
    for i in range(seconds):
        ib.sleep(1)
        logger.info(f"   {message}... ({i+1}/{seconds})")


def test_connection(ib: IB) -> bool:
    """测试 IB Gateway 连接"""
    logger.info("=" * 60)
    logger.info("测试 IB Gateway 连接")
    logger.info("=" * 60)
    
    if ib.isConnected():
        logger.info("✅ 已连接到 IB Gateway")
        try:
            logger.info(f"   服务器版本: {ib.client.serverVersion()}")
        except Exception:
            pass
        return True
    else:
        logger.error("❌ 未连接到 IB Gateway")
        return False


def test_account_info(ib: IB) -> bool:
    """测试账户信息获取"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("测试账户信息")
    logger.info("=" * 60)
    
    try:
        # 等待一下让连接稳定
        ib.sleep(1)
        
        accounts = ib.managedAccounts()
        logger.info(f"✅ 可用账户: {accounts}")
        
        for account in accounts:
            ib.sleep(0.5)  # 每个账户请求之间等待
            summary = ib.accountSummary(account)
            if summary:
                logger.info(f"   账户 {account} 摘要:")
                for item in summary[:5]:  # 只显示前5项
                    logger.info(f"      {item.tag}: {item.value} {item.currency}")
        return True
    except Exception as e:
        logger.error(f"❌ 获取账户信息失败: {e}")
        return False


def test_market_data_type(ib: IB, market_data_type: int) -> None:
    """设置市场数据类型"""
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"设置市场数据类型: {market_data_type}")
    logger.info("=" * 60)
    
    data_type_names = {
        1: "Live (实时数据)",
        2: "Frozen (冻结数据)",
        3: "Delayed (延迟数据)",
        4: "Delayed Frozen (延迟冻结数据)"
    }
    
    logger.info(f"   类型: {data_type_names.get(market_data_type, '未知')}")
    ib.reqMarketDataType(market_data_type)
    ib.sleep(1)  # 等待设置生效
    logger.info("✅ 市场数据类型已设置")


def test_stock_data(ib: IB, symbol: str, exchange: str = "SMART", max_retries: int = 3) -> bool:
    """测试股票行情数据，带重试机制"""
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"测试股票行情: {symbol}")
    logger.info("=" * 60)
    
    for retry in range(max_retries):
        try:
            if retry > 0:
                logger.info(f"   重试 {retry}/{max_retries}...")
                ib.sleep(2)  # 重试前等待
            
            # 创建股票合约
            stock = Stock(symbol, exchange, "USD")
            qualified = ib.qualifyContracts(stock)
            
            if not qualified:
                logger.error(f"❌ 无法验证合约: {symbol}")
                continue
                
            logger.info(f"✅ 合约已验证: {stock}")
            
            # 等待一下再请求市场数据
            ib.sleep(1)
            
            # 请求市场数据
            ticker = ib.reqMktData(stock, genericTickList="", snapshot=False, regulatorySnapshot=False)
            logger.info("   等待市场数据...")
            
            # 等待数据，使用更长的超时时间
            data_received = False
            for i in range(15):
                ib.sleep(1)
                
                # 检查是否有任何数据
                has_bid = not util.isNan(ticker.bid) and ticker.bid > 0
                has_ask = not util.isNan(ticker.ask) and ticker.ask > 0
                has_last = not util.isNan(ticker.last) and ticker.last > 0
                has_close = not util.isNan(ticker.close) and ticker.close > 0
                
                if has_bid or has_ask or has_last or has_close:
                    data_received = True
                    break
                    
                logger.info(f"   等待中... ({i+1}/15) bid={ticker.bid} ask={ticker.ask} last={ticker.last}")
            
            # 显示结果
            logger.info("")
            logger.info(f"   股票: {symbol}")
            logger.info(f"   最新价 (last): {ticker.last}")
            logger.info(f"   买价 (bid): {ticker.bid}")
            logger.info(f"   卖价 (ask): {ticker.ask}")
            logger.info(f"   市场价 (marketPrice): {ticker.marketPrice()}")
            logger.info(f"   中间价 (midpoint): {ticker.midpoint()}")
            logger.info(f"   开盘价 (open): {ticker.open}")
            logger.info(f"   最高价 (high): {ticker.high}")
            logger.info(f"   最低价 (low): {ticker.low}")
            logger.info(f"   收盘价 (close): {ticker.close}")
            logger.info(f"   成交量 (volume): {ticker.volume}")
            
            # 取消订阅
            ib.cancelMktData(stock)
            ib.sleep(0.5)
            
            if data_received:
                logger.info("✅ 股票行情数据获取成功")
                return True
            else:
                logger.warning("⚠️ 未能获取到有效的市场数据")
                if retry < max_retries - 1:
                    logger.info("   将重试...")
                
        except Exception as e:
            logger.error(f"❌ 获取股票行情失败: {e}")
            import traceback
            traceback.print_exc()
    
    logger.error("❌ 所有重试都失败了")
    logger.warning("   可能的原因:")
    logger.warning("   1. 没有订阅市场数据 (需要在 IBKR 账户中订阅)")
    logger.warning("   2. 存在竞争会话 (其他地方登录了同一账户)")
    logger.warning("   3. 非交易时间 (美股交易时间: 美东 9:30-16:00)")
    logger.warning("   4. 尝试使用延迟数据: --market-data-type 3")
    return False


def test_option_chain(ib: IB, symbol: str) -> bool:
    """测试期权链数据"""
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"测试期权链: {symbol}")
    logger.info("=" * 60)
    
    try:
        # 创建股票合约
        stock = Stock(symbol, "SMART", "USD")
        ib.qualifyContracts(stock)
        
        ib.sleep(1)  # 等待
        
        # 获取期权链参数
        chains = ib.reqSecDefOptParams(stock.symbol, "", stock.secType, stock.conId)
        
        if not chains:
            logger.error("❌ 无法获取期权链参数")
            return False
        
        logger.info(f"✅ 找到 {len(chains)} 个期权链")
        
        for chain in chains:
            logger.info(f"   交易所: {chain.exchange}")
            logger.info(f"   到期日数量: {len(chain.expirations)}")
            logger.info(f"   行权价数量: {len(chain.strikes)}")
            logger.info(f"   前5个到期日: {sorted(chain.expirations)[:5]}")
            logger.info(f"   部分行权价: {sorted(chain.strikes)[:10]}")
            logger.info("")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 获取期权链失败: {e}")
        return False


def test_option_data(ib: IB, symbol: str) -> bool:
    """测试期权行情数据"""
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"测试期权行情: {symbol}")
    logger.info("=" * 60)
    
    try:
        # 首先获取股票价格
        stock = Stock(symbol, "SMART", "USD")
        ib.qualifyContracts(stock)
        
        ib.sleep(1)
        
        stock_ticker = ib.reqMktData(stock)
        
        # 等待股票数据
        for i in range(10):
            ib.sleep(1)
            if not util.isNan(stock_ticker.close) or not util.isNan(stock_ticker.last):
                break
        
        stock_price = stock_ticker.last if not util.isNan(stock_ticker.last) else stock_ticker.close
        if util.isNan(stock_price):
            stock_price = 500  # 使用默认值
            logger.warning(f"   无法获取股票价格，使用默认值: {stock_price}")
        else:
            logger.info(f"   股票当前价格: {stock_price}")
        
        ib.cancelMktData(stock)
        ib.sleep(1)
        
        # 获取期权链
        chains = ib.reqSecDefOptParams(stock.symbol, "", stock.secType, stock.conId)
        if not chains:
            logger.error("❌ 无法获取期权链")
            return False
        
        chain = next((c for c in chains if c.exchange == "SMART"), chains[0])
        
        # 选择最近的到期日
        expirations = sorted(chain.expirations)
        if not expirations:
            logger.error("❌ 没有可用的到期日")
            return False
        
        expiration = expirations[0]
        logger.info(f"   选择到期日: {expiration}")
        
        # 选择接近当前价格的行权价
        strikes = sorted(chain.strikes)
        atm_strike = min(strikes, key=lambda x: abs(x - stock_price))
        logger.info(f"   选择行权价 (ATM): {atm_strike}")
        
        ib.sleep(1)
        
        # 创建期权合约 (Put)
        option = Option(symbol, expiration, atm_strike, "P", "SMART")
        qualified = ib.qualifyContracts(option)
        
        if not qualified:
            logger.error("❌ 无法验证期权合约")
            return False
        
        logger.info(f"✅ 期权合约已验证: {option}")
        
        ib.sleep(1)
        
        # 请求期权市场数据
        ticker = ib.reqMktData(option, genericTickList="101,106")  # 101=期权未平仓量, 106=隐含波动率
        logger.info("   等待期权市场数据...")
        
        for i in range(20):
            ib.sleep(1)
            has_data = (not util.isNan(ticker.bid) and ticker.bid > 0) or \
                       (not util.isNan(ticker.ask) and ticker.ask > 0) or \
                       (not util.isNan(ticker.last) and ticker.last > 0)
            has_greeks = ticker.modelGreeks is not None and \
                        ticker.modelGreeks.delta is not None and \
                        not util.isNan(ticker.modelGreeks.delta)
            
            if has_data and has_greeks:
                break
            logger.info(f"   等待中... ({i+1}/20) bid={ticker.bid} greeks={ticker.modelGreeks is not None}")
        
        # 显示结果
        logger.info("")
        logger.info(f"   期权: {option.localSymbol}")
        logger.info(f"   最新价: {ticker.last}")
        logger.info(f"   买价: {ticker.bid}")
        logger.info(f"   卖价: {ticker.ask}")
        logger.info(f"   市场价: {ticker.marketPrice()}")
        logger.info(f"   中间价: {ticker.midpoint()}")
        logger.info(f"   Put 未平仓量: {ticker.putOpenInterest}")
        logger.info(f"   Call 未平仓量: {ticker.callOpenInterest}")
        
        if ticker.modelGreeks:
            logger.info(f"   Greeks:")
            logger.info(f"      Delta: {ticker.modelGreeks.delta}")
            logger.info(f"      Gamma: {ticker.modelGreeks.gamma}")
            logger.info(f"      Theta: {ticker.modelGreeks.theta}")
            logger.info(f"      Vega: {ticker.modelGreeks.vega}")
            logger.info(f"      IV: {ticker.modelGreeks.impliedVol}")
        else:
            logger.warning("⚠️ 无法获取 Greeks 数据")
        
        ib.cancelMktData(option)
        
        if not util.isNan(ticker.bid) or not util.isNan(ticker.ask):
            logger.info("✅ 期权行情数据获取成功")
            return True
        else:
            logger.warning("⚠️ 期权市场价格为 NaN，可能需要订阅期权市场数据")
            return False
            
    except Exception as e:
        logger.error(f"❌ 获取期权行情失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vix_data(ib: IB) -> bool:
    """测试 VIX 指数数据"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("测试 VIX 指数")
    logger.info("=" * 60)
    
    try:
        vix = Index("VIX", "CBOE", "USD")
        ib.qualifyContracts(vix)
        logger.info(f"✅ VIX 合约已验证: {vix}")
        
        ib.sleep(1)
        
        ticker = ib.reqMktData(vix)
        logger.info("   等待 VIX 数据...")
        
        for i in range(15):
            ib.sleep(1)
            if not util.isNan(ticker.last) or not util.isNan(ticker.close):
                break
            logger.info(f"   等待中... ({i+1}/15)")
        
        logger.info("")
        logger.info(f"   VIX 最新价: {ticker.last}")
        logger.info(f"   VIX 市场价: {ticker.marketPrice()}")
        logger.info(f"   VIX 开盘: {ticker.open}")
        logger.info(f"   VIX 最高: {ticker.high}")
        logger.info(f"   VIX 最低: {ticker.low}")
        logger.info(f"   VIX 收盘: {ticker.close}")
        
        ib.cancelMktData(vix)
        
        if not util.isNan(ticker.last) or not util.isNan(ticker.close):
            logger.info("✅ VIX 数据获取成功")
            return True
        else:
            logger.warning("⚠️ VIX 价格为 NaN")
            return False
            
    except Exception as e:
        logger.error(f"❌ 获取 VIX 数据失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="IB Gateway 市场数据测试脚本")
    parser.add_argument("--host", default="127.0.0.1", help="IB Gateway 主机地址")
    parser.add_argument("--port", type=int, default=4002, help="IB Gateway 端口 (4002=IB Gateway, 7497=TWS)")
    parser.add_argument("--client-id", type=int, default=999, help="客户端 ID")
    parser.add_argument("--symbol", default="SPY", help="测试股票代码")
    parser.add_argument("--market-data-type", type=int, default=1, 
                        help="市场数据类型: 1=Live, 2=Frozen, 3=Delayed, 4=Delayed Frozen")
    parser.add_argument("--test-options", action="store_true", help="测试期权数据")
    parser.add_argument("--test-vix", action="store_true", help="测试 VIX 数据")
    parser.add_argument("--test-all", action="store_true", help="运行所有测试")
    parser.add_argument("--timeout", type=int, default=60, help="连接超时时间(秒)")
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("IB Gateway 市场数据测试")
    logger.info(f"时间: {datetime.now()}")
    logger.info("=" * 60)
    logger.info(f"连接参数:")
    logger.info(f"   主机: {args.host}")
    logger.info(f"   端口: {args.port}")
    logger.info(f"   客户端 ID: {args.client_id}")
    logger.info(f"   测试股票: {args.symbol}")
    logger.info(f"   市场数据类型: {args.market_data_type}")
    
    ib = IB()
    
    # 设置错误处理
    def on_error(reqId, errorCode, errorString, contract):
        if errorCode in [2104, 2106, 2158]:  # 连接状态消息
            logger.info(f"Warning {errorCode}, reqId {reqId}: {errorString}")
        elif errorCode == 10197:  # 竞争会话
            logger.error(f"Error {errorCode}, reqId {reqId}: {errorString}")
            logger.error("   ⚠️ 检测到竞争会话！请关闭其他 IBKR 客户端（TWS、网页版、手机App）")
        else:
            logger.error(f"Error {errorCode}, reqId {reqId}: {errorString}, contract: {contract}")
    
    ib.errorEvent += on_error
    
    try:
        # 连接到 IB Gateway
        logger.info("")
        logger.info("正在连接到 IB Gateway...")
        ib.connect(args.host, args.port, clientId=args.client_id, timeout=args.timeout)
        
        # 等待连接稳定
        logger.info("等待连接稳定...")
        ib.sleep(3)
        
        results = {}
        
        # 测试连接
        results["连接"] = test_connection(ib)
        
        if not results["连接"]:
            logger.error("连接失败，退出测试")
            return 1
        
        # 测试账户信息
        results["账户信息"] = test_account_info(ib)
        
        # 设置市场数据类型
        test_market_data_type(ib, args.market_data_type)
        
        # 等待市场数据类型设置生效
        ib.sleep(2)
        
        # 测试股票数据
        results["股票行情"] = test_stock_data(ib, args.symbol)
        
        # 测试期权链
        if args.test_options or args.test_all:
            results["期权链"] = test_option_chain(ib, args.symbol)
            results["期权行情"] = test_option_data(ib, args.symbol)
        
        # 测试 VIX
        if args.test_vix or args.test_all:
            results["VIX 数据"] = test_vix_data(ib)
        
        # 打印测试结果摘要
        logger.info("")
        logger.info("=" * 60)
        logger.info("测试结果摘要")
        logger.info("=" * 60)
        
        all_passed = True
        for test_name, passed in results.items():
            status = "✅ 通过" if passed else "❌ 失败"
            logger.info(f"   {test_name}: {status}")
            if not passed:
                all_passed = False
        
        logger.info("")
        if all_passed:
            logger.info("🎉 所有测试通过!")
        else:
            logger.warning("⚠️ 部分测试失败，请检查:")
            logger.warning("   1. IB Gateway 是否正在运行")
            logger.warning("   2. 是否已登录 IBKR 账户")
            logger.warning("   3. 是否存在竞争会话（关闭 TWS、网页版、手机App）")
            logger.warning("   4. 是否订阅了必要的市场数据:")
            logger.warning("      - Cboe One Add-On Bundle (期权数据)")
            logger.warning("      - US Equity and Options Add-On Streaming Bundle")
            logger.warning("   5. 账户是否已注资 (未注资账户无法接收数据)")
            logger.warning("   6. 尝试使用延迟数据: --market-data-type 3")
        
        return 0 if all_passed else 1
        
    except Exception as e:
        logger.error(f"❌ 连接失败: {e}")
        logger.error("")
        logger.error("请检查:")
        logger.error("   1. IB Gateway 是否正在运行")
        logger.error("   2. 端口是否正确 (IB Gateway: 4002, TWS: 7497)")
        logger.error("   3. API 连接是否已启用")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        if ib.isConnected():
            ib.disconnect()
            logger.info("")
            logger.info("已断开连接")


if __name__ == "__main__":
    sys.exit(main())
