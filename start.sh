#!/bin/bash
# ThetaGang 启动脚本

set -e

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
echo -e "${BLUE}ThetaGang 启动脚本${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# 创建日志目录
mkdir -p logs

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ 错误: 虚拟环境不存在${NC}"
    echo "请先创建虚拟环境: python3 -m venv .venv"
    exit 1
fi

echo -e "${GREEN}✅ 虚拟环境检查通过${NC}"

# 检查配置文件
if [ ! -f "thetagang.toml" ]; then
    echo -e "${RED}❌ 错误: 配置文件 thetagang.toml 不存在${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 配置文件检查通过${NC}"

# 检查是否已经在运行
if [ -f "thetagang.pid" ]; then
    PID=$(cat thetagang.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  程序已在运行，PID: $PID${NC}"
        echo "如需重启，请先运行: ./stop.sh"
        exit 1
    else
        echo -e "${YELLOW}⚠️  发现旧的 PID 文件，正在清理...${NC}"
        rm thetagang.pid
    fi
fi

# 测试 IB Gateway 连接
echo ""
echo -e "${BLUE}检查 IB Gateway 连接...${NC}"
.venv/bin/python -c "
from ib_insync import IB
import sys
ib = IB()
try:
    ib.connect('127.0.0.1', 4002, clientId=1)
    print('✅ IB Gateway 连接正常')
    ib.disconnect()
    sys.exit(0)
except Exception as e:
    print(f'❌ 无法连接到 IB Gateway: {e}')
    print('')
    print('请检查:')
    print('  1. IB Gateway 是否已启动')
    print('  2. 端口是否设置为 4002')
    print('  3. API 连接是否已启用')
    sys.exit(1)
" || exit 1

# 生成日志文件名
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="logs/thetagang_${TIMESTAMP}.log"

echo ""
echo -e "${BLUE}启动 ThetaGang...${NC}"
echo "日志文件: $LOG_FILE"
echo ""

# 启动程序
nohup .venv/bin/python -m thetagang.main --config thetagang.toml > "$LOG_FILE" 2>&1 &
PID=$!

# 保存 PID
echo $PID > thetagang.pid

# 创建最新日志的符号链接
ln -sf "$LOG_FILE" logs/thetagang_latest.log

echo -e "${GREEN}✅ ThetaGang 已启动${NC}"
echo "   PID: $PID"
echo "   日志: $LOG_FILE"
echo ""

# 等待几秒并检查状态
sleep 3

if ps -p $PID > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 程序运行正常${NC}"
    echo ""
    echo "查看实时日志:"
    echo "  tail -f $LOG_FILE"
    echo ""
    echo "查看状态:"
    echo "  ./status.sh"
    echo ""
    echo "停止程序:"
    echo "  ./stop.sh"
else
    echo -e "${RED}❌ 程序启动失败${NC}"
    echo "查看日志了解详情:"
    echo "  tail -50 $LOG_FILE"
    rm thetagang.pid
    exit 1
fi

echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}启动完成！${NC}"
echo -e "${BLUE}================================${NC}"
