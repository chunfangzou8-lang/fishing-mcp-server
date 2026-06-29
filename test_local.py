#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地测试脚本 - 测试游戏是否正常工作
"""

import os
import sys

# 设置 UTF-8 编码
os.environ['PYTHONUTF8'] = '1'

import engine

print("=" * 60)
print("🎣 钓鱼游戏本地测试")
print("=" * 60)

# 测试 1: 查看帮助
print("\n[测试 1] 查看帮助")
print("-" * 60)
print(engine.cmd("help"))

# 测试 2: 查看状态
print("\n\n[测试 2] 查看初始状态")
print("-" * 60)
print(engine.cmd("status"))

# 测试 3: 抛竿钓鱼
print("\n\n[测试 3] 抛竿钓鱼 3 次")
print("-" * 60)
print(engine.cmd("cast 3"))

# 测试 4: 查看背包
print("\n\n[测试 4] 查看背包")
print("-" * 60)
print(engine.cmd("inventory"))

# 测试 5: 卖鱼
print("\n\n[测试 5] 卖掉所有鱼")
print("-" * 60)
print(engine.cmd("sell all"))

# 测试 6: 查看商店
print("\n\n[测试 6] 查看商店")
print("-" * 60)
print(engine.cmd("shop"))

# 测试 7: 购买鱼饵
print("\n\n[测试 7] 购买鱼饵")
print("-" * 60)
print(engine.cmd("buy basic_worm 5"))

# 测试 8: 查看地点
print("\n\n[测试 8] 查看所有地点")
print("-" * 60)
print(engine.cmd("goto"))

# 测试 9: 批量指令
print("\n\n[测试 9] 批量指令（买饵+抛竿）")
print("-" * 60)
print(engine.cmd("buy basic_worm 3; cast 3"))

print("\n\n" + "=" * 60)
print("✅ 测试完成！游戏运行正常。")
print("=" * 60)

# 清理测试存档
if os.path.exists("fishing_save.json"):
    os.remove("fishing_save.json")
    print("\n🧹 已清理测试存档")
