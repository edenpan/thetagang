#!/bin/bash
# ThetaGang 重启脚本

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
echo -e "${BLUE}ThetaGang 重启脚本${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# 停止程序
echo -e "${YELLOW}正在停止程序...${NC}"
./stop.sh

# 等待
echo ""
echo "等待 5 秒..."
sleep 5

# 启动程序
echo ""
echo -e "${YELLOW}正在启动程序...${NC}"
./start.sh

echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}重启完成！${NC}"
echo -e "${BLUE}================================${NC}"
