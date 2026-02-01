#!/usr/bin/env python3
"""快速测试期权链选择逻辑是否生效"""

from ib_insync import IB, Stock
import time

ib = IB()

try:
    print("连接到 IB Gateway...")
    ib.connect('127.0.0.1', 4002, clientId=996)
    time.sleep(2)

    # 模拟程序的期权链选择逻辑
    stock = Stock('SPY', 'SMART', 'USD', primaryExchange='ARCA')
    ib.qualifyContracts(stock)

    chains = ib.reqSecDefOptParams(stock.symbol, "", stock.secType, stock.conId)

    # 旧逻辑（会选错）
    old_chain = next(c for c in chains if c.exchange == 'SMART')
    print(f"\n❌ 旧逻辑会选择: {len(old_chain.strikes)} 个行权价")

    # 新逻辑（应该选对）
    matching_chains = [c for c in chains if c.exchange == 'SMART']
    new_chain = max(matching_chains, key=lambda c: len(c.strikes))
    print(f"✅ 新逻辑会选择: {len(new_chain.strikes)} 个行权价")

    if len(new_chain.strikes) > 100:
        print(f"\n🎉 成功！新逻辑选择了正确的期权链！")
    else:
        print(f"\n❌ 失败！新逻辑仍然选择了错误的链")

finally:
    if ib.isConnected():
        ib.disconnect()
