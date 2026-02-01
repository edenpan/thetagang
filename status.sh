#!/bin/bash
# ThetaGang 状态检查脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}ThetaGang 运行状态${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# 检查 PID 文件
if [ -f "thetagang.pid" ]; then
    PID=$(cat thetagang.pid)

    if ps -p $PID > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 程序正在运行${NC}"
        echo "   PID: $PID"

        # 显示进程信息
        echo ""
        echo "进程信息:"
        ps -p $PID -o pid,ppid,user,%cpu,%mem,etime,cmd

        # 检查最新日志
        if [ -L "logs/thetagang_latest.log" ]; then
            echo ""
            echo "最新日志文件:"
            ls -lh logs/thetagang_latest.log

            echo ""
            echo "最近10条日志:"
            echo -e "${YELLOW}---${NC}"
            tail -10 logs/thetagang_latest.log
            echo -e "${YELLOW}---${NC}"
        fi
    else
        echo -e "${RED}❌ 进程不存在 (PID: $PID)${NC}"
        echo "PID 文件存在但进程已结束"
        echo ""
        echo "建议:"
        echo "  1. 运行 ./stop.sh 清理"
        echo "  2. 运行 ./start.sh 重新启动"
    fi
else
    echo -e "${RED}❌ 程序未运行${NC}"
    echo "未找到 PID 文件"

    # 检查是否有遗留进程
    PIDS=$(pgrep -f "thetagang.main" || true)
    if [ -n "$PIDS" ]; then
        echo ""
        echo -e "${YELLOW}⚠️  发现遗留进程: $PIDS${NC}"
        echo "运行 ./stop.sh 清理这些进程"
    fi
fi

echo ""

# 检查 IB Gateway 连接
echo -e "${BLUE}IB Gateway 状态:${NC}"
.venv/bin/python -c "
from ib_insync import IB
import sys
ib = IB()
try:
    ib.connect('127.0.0.1', 4002, clientId=999, timeout=5)
    print('✅ IB Gateway 连接正常')
    print(f'   服务器版本: {ib.client.serverVersion()}')
    accounts = ib.managedAccounts()
    if accounts:
        print(f'   账户: {accounts}')
    ib.disconnect()
except Exception as e:
    print(f'❌ IB Gateway 连接失败: {e}')
    sys.exit(1)
" 2>/dev/null || echo -e "${RED}❌ IB Gateway 未连接${NC}"

echo ""

# 显示最近的日志文件
echo -e "${BLUE}最近的日志文件:${NC}"
ls -lht logs/*.log 2>/dev/null | head -5 || echo "  无日志文件"

echo ""
echo -e "${BLUE}================================${NC}"
