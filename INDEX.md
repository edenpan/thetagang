# ThetaGang 文档索引

**最后更新**: 2026-01-31

---

## 🎯 我想...

### 快速启动程序
→ 阅读 [`QUICK_START.md`](QUICK_START.md) (2分钟)  
→ 运行 `./start.sh`

### 第一次使用
→ 阅读 [`START_GUIDE.md`](START_GUIDE.md) (10分钟)  
→ 按步骤操作

### 了解修复了什么
→ 阅读 [`README_FIXES.md`](README_FIXES.md) - 用户友好版本  
→ 阅读 [`MODIFICATIONS_SUMMARY.md`](MODIFICATIONS_SUMMARY.md) - 技术总结

### 深入技术细节
→ 阅读 [`CODE_MODIFICATIONS.md`](CODE_MODIFICATIONS.md) - 完整技术文档

### 查看所有新文件
→ 阅读 [`FILES_CREATED.md`](FILES_CREATED.md) - 文件清单

---

## 📂 文档分类

### ⚡ 快速参考
- `QUICK_START.md` - 快速启动卡片
- `INDEX.md` - 本文件

### 📖 使用指南
- `START_GUIDE.md` - 完整启动指南
- `README_FIXES.md` - 问题修复说明

### 🔧 技术文档
- `CODE_MODIFICATIONS.md` - 详细代码修改
- `MODIFICATIONS_SUMMARY.md` - 修改总结
- `FILES_CREATED.md` - 文件清单

### 📜 原始文档
- `README.md` - 项目原始文档
- `CHANGELOG.md` - 项目更新日志

---

## 🛠️ 脚本索引

### 程序控制
```bash
./start.sh      # 启动程序
./stop.sh       # 停止程序
./restart.sh    # 重启程序
./status.sh     # 查看状态
```

### 日志查看
```bash
./view_logs.sh  # 交互式日志查看
```

### 测试验证
```bash
.venv/bin/python test_chain_selection.py  # 测试期权链选择
.venv/bin/python test_symbols.py          # 测试标的
.venv/bin/python verify_fixes.py          # 验证修复
```

---

## 🎓 学习路径

### 初学者
1. `QUICK_START.md` - 了解基本命令
2. `START_GUIDE.md` - 详细使用说明
3. 运行测试脚本验证环境

### 有经验用户
1. `MODIFICATIONS_SUMMARY.md` - 快速了解改动
2. 运行 `./start.sh` 直接启动
3. 使用 `./view_logs.sh` 监控

### 开发者
1. `CODE_MODIFICATIONS.md` - 代码修改细节
2. `FILES_CREATED.md` - 文件结构
3. 查看源代码了解实现

---

## 🔍 故障排查索引

| 问题 | 查看文档 | 位置 |
|------|----------|------|
| 无法连接 IB Gateway | START_GUIDE.md | "常见问题排查 → 1" |
| 程序启动后退出 | START_GUIDE.md | "常见问题排查 → 2" |
| 找不到期权合约 | README_FIXES.md | "问题分析 → 问题1" |
| NaN 价格错误 | README_FIXES.md | "问题分析 → 问题2" |
| 期权链选择错误 | CODE_MODIFICATIONS.md | "修改1" |

---

## 📊 关键概念索引

### "价格下跌"逻辑
- 详细说明: `CODE_MODIFICATIONS.md` 
- 用户指南: `README_FIXES.md` → "价格下跌逻辑详解"
- 代码位置: `portfolio_manager.py:1027`

### 期权链选择
- 问题说明: `README_FIXES.md` → "问题总结 → 1"
- 修复方案: `CODE_MODIFICATIONS.md` → "修改1"
- 验证脚本: `test_chain_selection.py`

### NaN 处理
- 问题说明: `README_FIXES.md` → "问题总结 → 2"
- 修复方案: `CODE_MODIFICATIONS.md` → "修改2"
- 代码位置: `portfolio_manager.py:986-1020`

---

## ⚡ 常用命令速查

```bash
# 启动
./start.sh

# 查看状态
./status.sh

# 实时日志
tail -f logs/thetagang_latest.log

# 查看订单
grep -i "order" logs/thetagang_latest.log | tail -20

# 查看错误
grep -i "error" logs/thetagang_latest.log | tail -20

# 停止
./stop.sh

# 重启
./restart.sh
```

---

## 📞 获取帮助

1. **查看对应文档**（见上方索引）
2. **运行测试脚本验证**
3. **查看日志文件分析**
4. **GitHub Issues**（原项目）

---

**提示**: 如果是第一次使用，建议从 `QUICK_START.md` 开始！
