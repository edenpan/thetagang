#!/bin/bash
# ThetaGang 停止脚本

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
echo -e "${BLUE}ThetaGang 停止脚本${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# 检查 PID 文件
if [ ! -f "thetagang.pid" ]; then
    echo -e "${YELLOW}⚠️  未找到 PID 文件${NC}"
    echo "尝试查找正在运行的进程..."

    # 查找进程
    PIDS=$(pgrep -f "thetagang.main" || true)

    if [ -z "$PIDS" ]; then
        echo -e "${YELLOW}⚠️  没有找到正在运行的 ThetaGang 进程${NC}"
        exit 0
    else
        echo -e "${YELLOW}找到进程: $PIDS${NC}"
        echo "是否强制停止这些进程？[y/N]"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            for pid in $PIDS; do
                echo "正在停止进程 $pid..."
                kill $pid 2>/dev/null || true
            done
            sleep 2
            echo -e "${GREEN}✅ 所有进程已停止${NC}"
        else
            echo "已取消"
            exit 0
        fi
    fi
else
    PID=$(cat thetagang.pid)

    # 检查进程是否存在
    if ps -p $PID > /dev/null 2>&1; then
        echo "正在停止 ThetaGang (PID: $PID)..."

        # 优雅停止
        kill $PID

        # 等待进程结束
        count=0
        while ps -p $PID > /dev/null 2>&1 && [ $count -lt 10 ]; do
            sleep 1
            count=$((count + 1))
            echo -n "."
        done
        echo ""

        # 如果进程仍在运行，强制停止
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${YELLOW}进程未响应，强制停止...${NC}"
            kill -9 $PID 2>/dev/null || true
            sleep 1
        fi

        # 验证停止
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${RED}❌ 无法停止进程${NC}"
            exit 1
        else
            echo -e "${GREEN}✅ ThetaGang 已停止${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  进程 (PID: $PID) 不存在${NC}"
    fi

    # 删除 PID 文件
    rm thetagang.pid
    echo "已删除 PID 文件"
fi

echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}停止完成！${NC}"
echo -e "${BLUE}================================${NC}"
