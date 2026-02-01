#!/usr/bin/env python3
"""测试各个配置的标的是否可以正常下单"""

import sys
from datetime import datetime, timedelta

# 计算 DTE
def option_dte(expiration_str):
    """计算到期日"""
    try:
        exp_date = datetime.strptime(expiration_str, "%Y%m%d")
        today = datetime.now()
        return (exp_date - today).days
    except:
        return 0

# 测试期权链
from ib_insync import IB, Stock
import time

ib = IB()

try:
    print("连接到 IB Gateway...")
    ib.connect('127.0.0.1', 4002, clientId=998)
    ib.sleep(2)

    print("\n测试配置中的标的:")
    print("=" * 80)

    symbols_config = {
        'SPY': {'exchange': 'SMART', 'primary_exchange': 'ARCA'},
        'QQQ': {'exchange': 'SMART', 'primary_exchange': None},
        'TLT': {'exchange': 'SMART', 'primary_exchange': None},
        'ABNB': {'exchange': 'SMART', 'primary_exchange': 'NASDAQ'},
    }

    target_dte = 30  # 从配置文件读取

    for symbol, config in symbols_config.items():
        print(f"\n{'='*80}")
        print(f"测试标的: {symbol}")
        print(f"{'='*80}")

        try:
            # 创建股票合约
            if config['primary_exchange']:
                stock = Stock(symbol, config['exchange'], "USD", primaryExchange=config['primary_exchange'])
            else:
                stock = Stock(symbol, config['exchange'], "USD")

            # 验证合约
            qualified = ib.qualifyContracts(stock)
            if not qualified:
                print(f"  ❌ 无法验证 {symbol} 合约")
                continue

            print(f"  ✅ 合约已验证: {qualified[0]}")
            ib.sleep(1)

            # 获取市场数据
            ticker = ib.reqMktData(stock)
            ib.sleep(3)  # 等待数据

            print(f"  当前价格: {ticker.marketPrice()}")
            print(f"  最新价: {ticker.last}")
            print(f"  买价: {ticker.bid}")
            print(f"  卖价: {ticker.ask}")

            # 取消市场数据订阅
            ib.cancelMktData(stock)
            ib.sleep(1)

            # 获取期权链
            chains = ib.reqSecDefOptParams(stock.symbol, "", stock.secType, stock.conId)

            if not chains:
                print(f"  ❌ 无法获取 {symbol} 期权链")
                continue

            print(f"\n  找到 {len(chains)} 个期权链")

            # 查找 SMART 交易所的链
            smart_chains = [c for c in chains if c.exchange == 'SMART']

            if smart_chains:
                for chain in smart_chains:
                    print(f"\n  SMART 交易所期权链:")
                    print(f"    到期日数量: {len(chain.expirations)}")
                    print(f"    行权价数量: {len(chain.strikes)}")

                    # 显示前10个到期日及其DTE
                    print(f"\n    前10个到期日及DTE:")
                    sorted_exp = sorted(chain.expirations)[:10]
                    for exp in sorted_exp:
                        dte = option_dte(exp)
                        符合条件 = "✅" if dte >= target_dte else "❌"
                        print(f"      {exp} (DTE={dte}) {符合条件}")

                    # 统计符合 DTE 条件的到期日数量
                    valid_expirations = [exp for exp in chain.expirations if option_dte(exp) >= target_dte]
                    print(f"\n    符合 DTE>={target_dte} 的到期日数量: {len(valid_expirations)}")

                    if len(valid_expirations) == 0:
                        print(f"    ⚠️ 警告: 没有符合 DTE>={target_dte} 条件的到期日!")
                        print(f"    建议: 降低 target.dte 配置值")

                    # 显示部分行权价
                    print(f"\n    部分行权价 (前10个和后10个):")
                    sorted_strikes = sorted(chain.strikes)
                    print(f"      前10个: {sorted_strikes[:10]}")
                    print(f"      后10个: {sorted_strikes[-10:]}")
            else:
                print(f"  ⚠️ 未找到 SMART 交易所的期权链")
                print(f"  可用的交易所: {[c.exchange for c in chains[:5]]}")

            print(f"\n  {'='*80}")

        except Exception as e:
            print(f"  ❌ 测试 {symbol} 时出错: {e}")
            import traceback
            traceback.print_exc()

        ib.sleep(1)

    print(f"\n{'='*80}")
    print("测试完成")
    print(f"{'='*80}")

except Exception as e:
    print(f"连接失败: {e}")
    import traceback
    traceback.print_exc()
finally:
    if ib.isConnected():
        ib.disconnect()
        print("\n已断开连接")
