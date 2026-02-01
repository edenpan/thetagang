#!/bin/bash
# ThetaGang 日志查看脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# 显示菜单
show_menu() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}ThetaGang 日志查看${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    echo "1. 查看实时日志 (tail -f)"
    echo "2. 查看最近 100 行"
    echo "3. 查看最近 50 行"
    echo "4. 搜索错误 (ERROR/Exception)"
    echo "5. 搜索订单 (Order/Trade)"
    echo "6. 搜索期权链选择"
    echo "7. 查看 IB API 日志"
    echo "8. 列出所有日志文件"
    echo "0. 退出"
    echo ""
    echo -n "请选择 [0-8]: "
}

# 获取最新日志文件
get_latest_log() {
    if [ -L "logs/thetagang_latest.log" ]; then
        echo "logs/thetagang_latest.log"
    else
        ls -t logs/thetagang_*.log 2>/dev/null | head -1
    fi
}

# 主循环
while true; do
    show_menu
    read choice

    LATEST_LOG=$(get_latest_log)

    case $choice in
        1)
            if [ -n "$LATEST_LOG" ]; then
                echo ""
                echo -e "${GREEN}实时查看日志 (Ctrl+C 退出)${NC}"
                echo "文件: $LATEST_LOG"
                echo -e "${YELLOW}---${NC}"
                tail -f "$LATEST_LOG"
            else
                echo -e "${RED}未找到日志文件${NC}"
            fi
            ;;
        2)
            if [ -n "$LATEST_LOG" ]; then
                echo ""
                echo -e "${GREEN}最近 100 行日志${NC}"
                echo "文件: $LATEST_LOG"
                echo -e "${YELLOW}---${NC}"
                tail -100 "$LATEST_LOG" | less
            else
                echo -e "${RED}未找到日志文件${NC}"
            fi
            ;;
        3)
            if [ -n "$LATEST_LOG" ]; then
                echo ""
                echo -e "${GREEN}最近 50 行日志${NC}"
                echo "文件: $LATEST_LOG"
                echo -e "${YELLOW}---${NC}"
                tail -50 "$LATEST_LOG"
            else
                echo -e "${RED}未找到日志文件${NC}"
            fi
            ;;
        4)
            if [ -n "$LATEST_LOG" ]; then
                echo ""
                echo -e "${GREEN}搜索错误${NC}"
                echo "文件: $LATEST_LOG"
                echo -e "${YELLOW}---${NC}"
                grep -i "error\|exception\|fail\|traceback" "$LATEST_LOG" | tail -50
            else
                echo -e "${RED}未找到日志文件${NC}"
            fi
            ;;
        5)
            if [ -n "$LATEST_LOG" ]; then
                echo ""
                echo -e "${GREEN}搜索订单${NC}"
                echo "文件: $LATEST_LOG"
                echo -e "${YELLOW}---${NC}"
                grep -i "order\|trade\|submitted\|filled" "$LATEST_LOG" | tail -50
            else
                echo -e "${RED}未找到日志文件${NC}"
            fi
            ;;
        6)
            if [ -n "$LATEST_LOG" ]; then
                echo ""
                echo -e "${GREEN}搜索期权链选择${NC}"
                echo "文件: $LATEST_LOG"
                echo -e "${YELLOW}---${NC}"
                grep -i "selected option chain\|valid strikes\|valid expirations" "$LATEST_LOG" | tail -30
            else
                echo -e "${RED}未找到日志文件${NC}"
            fi
            ;;
        7)
            if [ -f "ib_insync.log" ]; then
                echo ""
                echo -e "${GREEN}IB API 日志 (最近 100 行)${NC}"
                echo -e "${YELLOW}---${NC}"
                tail -100 ib_insync.log | less
            else
                echo -e "${RED}未找到 ib_insync.log${NC}"
            fi
            ;;
        8)
            echo ""
            echo -e "${GREEN}所有日志文件:${NC}"
            echo -e "${YELLOW}---${NC}"
            ls -lht logs/*.log 2>/dev/null || echo "无日志文件"
            echo ""
            echo "按任意键继续..."
            read -n 1
            ;;
        0)
            echo "退出"
            exit 0
            ;;
        *)
            echo -e "${RED}无效选择${NC}"
            sleep 1
            ;;
    esac

    if [ $choice -ne 1 ] && [ $choice -ne 0 ]; then
        echo ""
        echo "按任意键继续..."
        read -n 1
    fi

    clear
done
