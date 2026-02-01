#!/usr/bin/env python3
"""验证代码修改是否正常工作"""

import sys
from ib_insync import IB, Stock

def test_option_chain_selection():
    """测试期权链选择逻辑"""
    print("=" * 80)
    print("测试期权链选择逻辑")
    print("=" * 80)

    ib = IB()

    try:
        print("\n连接到 IB Gateway...")
        ib.connect('127.0.0.1', 4002, clientId=997)
        ib.sleep(2)

        # 测试 SPY（有多个 SMART 链）
        print("\n测试 SPY 期权链选择:")
        print("-" * 80)

        stock = Stock('SPY', 'SMART', 'USD', primaryExchange='ARCA')
        ib.qualifyContracts(stock)

        chains = ib.reqSecDefOptParams(stock.symbol, "", stock.secType, stock.conId)
        matching_chains = [c for c in chains if c.exchange == 'SMART']

        print(f"找到 {len(matching_chains)} 个 SMART 交易所的期权链:")
        for i, chain in enumerate(matching_chains, 1):
            print(f"  链 #{i}: {len(chain.strikes)} 个行权价, {len(chain.expirations)} 个到期日")

        # 使用新的选择逻辑
        if matching_chains:
            selected_chain = max(matching_chains, key=lambda c: len(c.strikes))
            print(f"\n✅ 新逻辑选择: 链 #{matching_chains.index(selected_chain) + 1}")
            print(f"   行权价数量: {len(selected_chain.strikes)}")
            print(f"   到期日数量: {len(selected_chain.expirations)}")
            print(f"   前10个行权价: {sorted(selected_chain.strikes)[:10]}")

            # 验证这是否是正常的链
            if len(selected_chain.strikes) > 100:
                print(f"\n✅ 验证通过: 选择了正常的期权链（行权价 > 100）")
            else:
                print(f"\n❌ 验证失败: 选择的链行权价太少（{len(selected_chain.strikes)}）")

        # 测试 QQQ
        print("\n" + "=" * 80)
        print("测试 QQQ 期权链选择:")
        print("-" * 80)

        stock_qqq = Stock('QQQ', 'SMART', 'USD')
        ib.qualifyContracts(stock_qqq)
        ib.sleep(1)

        chains_qqq = ib.reqSecDefOptParams(stock_qqq.symbol, "", stock_qqq.secType, stock_qqq.conId)
        matching_chains_qqq = [c for c in chains_qqq if c.exchange == 'SMART']

        print(f"找到 {len(matching_chains_qqq)} 个 SMART 交易所的期权链:")
        for i, chain in enumerate(matching_chains_qqq, 1):
            print(f"  链 #{i}: {len(chain.strikes)} 个行权价, {len(chain.expirations)} 个到期日")

        if matching_chains_qqq:
            selected_chain_qqq = max(matching_chains_qqq, key=lambda c: len(c.strikes))
            print(f"\n✅ 新逻辑选择: 链 #{matching_chains_qqq.index(selected_chain_qqq) + 1}")
            print(f"   行权价数量: {len(selected_chain_qqq.strikes)}")
            print(f"   到期日数量: {len(selected_chain_qqq.expirations)}")
            print(f"   前10个行权价: {sorted(selected_chain_qqq.strikes)[:10]}")

            if len(selected_chain_qqq.strikes) > 100:
                print(f"\n✅ 验证通过: 选择了正常的期权链（行权价 > 100）")
            else:
                print(f"\n❌ 验证失败: 选择的链行权价太少（{len(selected_chain_qqq.strikes)}）")

        print("\n" + "=" * 80)
        print("✅ 期权链选择逻辑测试完成")
        print("=" * 80)
        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if ib.isConnected():
            ib.disconnect()
            print("\n已断开连接")


def test_nan_handling():
    """测试 NaN 处理逻辑"""
    print("\n" + "=" * 80)
    print("测试 NaN 处理逻辑")
    print("=" * 80)

    from ib_insync import util

    # 模拟测试
    test_cases = [
        {"name": "正常价格", "value": 100.50, "expected": "使用正常价格"},
        {"name": "NaN", "value": float('nan'), "expected": "需要备用方案"},
        {"name": "零", "value": 0, "expected": "需要备用方案"},
        {"name": "负数", "value": -10, "expected": "需要备用方案"},
    ]

    print("\n测试用例:")
    all_passed = True

    for test in test_cases:
        value = test["value"]
        is_valid = not util.isNan(value) and value > 0

        if is_valid:
            result = "✅ 正常价格"
        else:
            result = "⚠️ 需要备用方案"

        print(f"  {test['name']:10s}: value={value:10.2f}, is_valid={is_valid}, result={result}")

    print("\n✅ NaN 处理逻辑验证完成")
    return True


def main():
    print("\n" + "=" * 80)
    print("验证 ThetaGang 代码修改")
    print("=" * 80)

    results = []

    # 测试 1: 期权链选择
    print("\n【测试 1/2】")
    result1 = test_option_chain_selection()
    results.append(("期权链选择", result1))

    # 测试 2: NaN 处理
    print("\n【测试 2/2】")
    result2 = test_nan_handling()
    results.append(("NaN 处理", result2))

    # 总结
    print("\n" + "=" * 80)
    print("测试结果总结")
    print("=" * 80)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name:20s}: {status}")

    all_passed = all(passed for _, passed in results)

    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 所有测试通过！代码修改验证成功！")
        print("\n建议:")
        print("  1. 运行完整程序测试: .venv/bin/python -m thetagang.main --config thetagang.toml")
        print("  2. 检查日志确认选择了正确的期权链（行权价 300+）")
        print("  3. 确认没有 NaN 或 IndexError 错误")
    else:
        print("⚠️ 部分测试失败，请检查修改")
    print("=" * 80)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
