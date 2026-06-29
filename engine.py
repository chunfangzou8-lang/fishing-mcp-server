#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文字钓鱼游戏引擎 - 完整版
基于 tutusagi/ai-fishing-game
"""

import json
import os
from typing import Any, Dict, List, Optional, Tuple

# ==================== 伪随机数生成器 ====================
class Mulberry32:
    """确定性伪随机数生成器"""
    def __init__(self, seed: int):
        self.state = seed & 0xFFFFFFFF

    def random(self) -> float:
        self.state = (self.state + 0x6D2B79F5) & 0xFFFFFFFF
        t = self.state
        t = ((t ^ (t >> 15)) * (t | 1)) & 0xFFFFFFFF
        t ^= t + ((t ^ (t >> 7)) * (t | 61)) & 0xFFFFFFFF
        t = ((t ^ (t >> 14)) & 0xFFFFFFFF)
        return (t >> 0) / 0xFFFFFFFF

    def randint(self, a: int, b: int) -> int:
        return a + int(self.random() * (b - a + 1))

    def choice(self, items: list) -> Any:
        return items[self.randint(0, len(items) - 1)]

    def get_state(self) -> int:
        return self.state

    def set_state(self, state: int):
        self.state = state & 0xFFFFFFFF


# ==================== 游戏数据 ====================
FISH_DATA = {
    "common_carp": {"name": "鲤鱼", "rarity": "common", "value": 5},
    "crucian_carp": {"name": "鲫鱼", "rarity": "common", "value": 4},
    "grass_carp": {"name": "草鱼", "rarity": "common", "value": 6},
    "silver_carp": {"name": "白鲢", "rarity": "uncommon", "value": 10},
    "bighead_carp": {"name": "花鲢", "rarity": "uncommon", "value": 12},
    "catfish": {"name": "鲶鱼", "rarity": "uncommon", "value": 15},
    "mandarin_fish": {"name": "鳜鱼", "rarity": "rare", "value": 30},
    "snakehead": {"name": "黑鱼", "rarity": "rare", "value": 35},
    "sturgeon": {"name": "鲟鱼", "rarity": "epic", "value": 80},
    "golden_carp": {"name": "金鲤", "rarity": "legendary", "value": 200},
}

LOCATIONS = {
    "moonlight_pond": {"name": "月光池塘", "cost": 0, "unlocked": True},
    "reed_river": {"name": "芦苇河", "cost": 0, "unlocked": True},
    "misty_lake": {"name": "雾隐湖", "cost": 200, "unlocked": False},
    "crystal_stream": {"name": "水晶溪", "cost": 300, "unlocked": False},
}

BAIT_DATA = {
    "basic_worm": {"name": "普通蚯蚓", "cost": 5},
    "glow_bait": {"name": "夜光饵", "cost": 15},
    "premium_bait": {"name": "高级鱼饵", "cost": 30},
}

SEASONS = ["春", "夏", "秋", "冬"]


# ==================== 游戏引擎 ====================
class FishingEngine:
    def __init__(self, save_file: str = "fishing_save.json"):
        self.save_file = save_file
        self.rng = Mulberry32(0x9e3779b9)
        self.state = self._load_or_init()

    def _load_or_init(self) -> Dict:
        """加载或初始化游戏状态"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.rng.set_state(data.get("rng_state", 0x9e3779b9))
                    return data
            except:
                pass

        return {
            "points": 200,
            "location": "moonlight_pond",
            "season_index": 0,
            "turn": 0,
            "bait": {"basic_worm": 5},
            "inventory": [],
            "encyclopedia": [],
            "locations_unlocked": ["moonlight_pond", "reed_river"],
            "rng_state": self.rng.get_state(),
        }

    def _save(self):
        """保存游戏状态"""
        self.state["rng_state"] = self.rng.get_state()
        try:
            with open(self.save_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"⚠️ 保存失败: {e}"
        return None

    def cmd(self, command: str) -> str:
        """执行游戏指令"""
        command = command.strip()

        if not command:
            return "请输入指令。输入 help 查看帮助。"

        # 批量指令处理
        if ";" in command or "\n" in command:
            commands = [c.strip() for c in command.replace("\n", ";").split(";") if c.strip()]
            results = []
            for i, cmd in enumerate(commands[:8], 1):
                results.append(f"▶ {cmd}\n{self.cmd(cmd)}")
            return "\n\n".join(results)

        parts = command.split()
        action = parts[0].lower()

        if action == "help":
            return self._help()
        elif action == "status":
            return self._status()
        elif action == "shop":
            return self._shop()
        elif action == "buy":
            return self._buy(parts[1:])
        elif action == "cast":
            return self._cast(parts[1:])
        elif action == "goto":
            return self._goto(parts[1:])
        elif action == "inventory":
            return self._inventory()
        elif action == "sell":
            return self._sell(parts[1:])
        elif action == "encyclopedia":
            return self._encyclopedia()
        elif action == "look":
            return self._look(parts[1:])
        else:
            return f"未知指令: {action}。输入 help 查看帮助。"

    def _help(self) -> str:
        return """🎣 文字钓鱼游戏

基础指令：
  help          - 查看帮助
  status        - 查看状态
  shop          - 查看商店
  buy <饵> <数量> - 购买鱼饵
  cast [饵] [次数] - 抛竿钓鱼
  goto [地点]   - 前往地点（不带参数列出所有地点）
  inventory     - 查看背包
  sell <目标>   - 卖鱼（sell all 卖全部）
  encyclopedia  - 查看图鉴
  look <id>     - 查看详情

祝你好运！🌟"""

    def _status(self) -> str:
        loc_name = LOCATIONS[self.state["location"]]["name"]
        season = SEASONS[self.state["season_index"]]
        bait_list = ", ".join([f"{BAIT_DATA[k]['name']}×{v}" for k, v in self.state["bait"].items()]) or "无"

        status_json = json.dumps({
            "pts": self.state["points"],
            "loc": loc_name,
            "sea": season,
            "turn": self.state["turn"],
            "enc": f"{len(self.state['encyclopedia'])}/{len(FISH_DATA)}",
            "bait": self.state["bait"],
            "hold": len(self.state["inventory"])
        }, ensure_ascii=False)

        return f"""📍 状态
点数: {self.state['points']}
地点: {loc_name}
季节: {season}
回合: {self.state['turn']}
图鉴: {len(self.state['encyclopedia'])}/{len(FISH_DATA)}
鱼饵: {bait_list}
渔获: {len(self.state['inventory'])} 条

📊 {status_json}"""

    def _shop(self) -> str:
        items = []
        for bid, data in BAIT_DATA.items():
            items.append(f"  {bid} - {data['name']} ({data['cost']} 点)")
        return "🏪 商店\n\n" + "\n".join(items) + f"\n\n你的点数: {self.state['points']}"

    def _buy(self, args: List[str]) -> str:
        if len(args) < 1:
            return "用法: buy <饵id> [数量]"

        bait_id = args[0]
        qty = int(args[1]) if len(args) > 1 else 1

        if bait_id not in BAIT_DATA:
            return f"未知鱼饵: {bait_id}"

        cost = BAIT_DATA[bait_id]["cost"] * qty
        if self.state["points"] < cost:
            return f"点数不足。需要 {cost} 点，你有 {self.state['points']} 点。"

        self.state["points"] -= cost
        self.state["bait"][bait_id] = self.state["bait"].get(bait_id, 0) + qty
        self._save()

        return f"✅ 购买了 {BAIT_DATA[bait_id]['name']} × {qty}，花费 {cost} 点。\n\n{self._status()}"

    def _cast(self, args: List[str]) -> str:
        # 简化版：单次抛竿
        bait_id = "basic_worm"
        times = 1

        # 解析参数
        for arg in args:
            if arg.isdigit():
                times = min(int(arg), 20)
            elif arg in BAIT_DATA:
                bait_id = arg

        if bait_id not in self.state["bait"] or self.state["bait"][bait_id] < times:
            return f"鱼饵不足。需要 {BAIT_DATA[bait_id]['name']} × {times}。"

        results = []
        for _ in range(times):
            self.state["bait"][bait_id] -= 1
            self.state["turn"] += 1

            # 随机钓鱼
            fish_id = self.rng.choice(list(FISH_DATA.keys()))
            fish = FISH_DATA[fish_id]

            self.state["inventory"].append({"id": fish_id, "name": fish["name"], "value": fish["value"]})

            # 新发现
            is_new = fish_id not in self.state["encyclopedia"]
            if is_new:
                self.state["encyclopedia"].append(fish_id)
                results.append(f"🎉 钓到了 {fish['name']}（{fish['rarity']}）- 首次发现！+{fish['value']*2} 点")
                self.state["points"] += fish["value"] * 2
            else:
                results.append(f"🎣 钓到了 {fish['name']}（{fish['rarity']}）")

            # 季节推进
            if self.state["turn"] % 20 == 0:
                self.state["season_index"] = (self.state["season_index"] + 1) % 4
                results.append(f"🍂 季节更替 → {SEASONS[self.state['season_index']]}")

        self._save()
        return "\n".join(results) + f"\n\n{self._status()}"

    def _goto(self, args: List[str]) -> str:
        if not args:
            # 列出所有地点
            lines = ["📍 可前往的地点：\n"]
            for lid, data in LOCATIONS.items():
                status = "✓" if lid in self.state["locations_unlocked"] else f"{data['cost']}点"
                lines.append(f"  {lid} - {data['name']} [{status}]")
            return "\n".join(lines)

        loc_id = args[0]
        if loc_id not in LOCATIONS:
            return f"未知地点: {loc_id}"

        if loc_id not in self.state["locations_unlocked"]:
            cost = LOCATIONS[loc_id]["cost"]
            if self.state["points"] < cost:
                return f"解锁 {LOCATIONS[loc_id]['name']} 需要 {cost} 点，你只有 {self.state['points']} 点。"
            self.state["points"] -= cost
            self.state["locations_unlocked"].append(loc_id)

        self.state["location"] = loc_id
        self._save()
        return f"🚶 前往 {LOCATIONS[loc_id]['name']}\n\n{self._status()}"

    def _inventory(self) -> str:
        if not self.state["inventory"]:
            return "🎒 背包空空如也。"

        lines = ["🎒 渔获：\n"]
        for i, item in enumerate(self.state["inventory"], 1):
            lines.append(f"  {i}. {item['name']} ({item['value']} 点)")

        total = sum(item["value"] for item in self.state["inventory"])
        lines.append(f"\n总价值: {total} 点")
        return "\n".join(lines)

    def _sell(self, args: List[str]) -> str:
        if not args or args[0] == "all":
            if not self.state["inventory"]:
                return "没有可卖的渔获。"

            total = sum(item["value"] for item in self.state["inventory"])
            count = len(self.state["inventory"])
            self.state["points"] += total
            self.state["inventory"] = []
            self._save()
            return f"💰 卖出 {count} 条鱼，获得 {total} 点。\n\n{self._status()}"

        return "用法: sell all"

    def _encyclopedia(self) -> str:
        if not self.state["encyclopedia"]:
            return "📖 图鉴空空如也。快去钓鱼吧！"

        lines = [f"📖 图鉴 ({len(self.state['encyclopedia'])}/{len(FISH_DATA)})：\n"]
        for fish_id in self.state["encyclopedia"]:
            fish = FISH_DATA[fish_id]
            lines.append(f"  ✓ {fish['name']} ({fish['rarity']})")
        return "\n".join(lines)

    def _look(self, args: List[str]) -> str:
        if not args:
            return "用法: look <id>"

        target = args[0]
        if target in FISH_DATA:
            fish = FISH_DATA[target]
            if target in self.state["encyclopedia"]:
                return f"🐟 {fish['name']}\n稀有度: {fish['rarity']}\n价值: {fish['value']} 点"
            else:
                return "??? 你还没钓到过这种鱼。"

        return f"未知对象: {target}"

    def new_game(self, seed: int = 0x9e3779b9) -> str:
        """重新开始游戏"""
        self.rng = Mulberry32(seed)
        self.state = {
            "points": 200,
            "location": "moonlight_pond",
            "season_index": 0,
            "turn": 0,
            "bait": {"basic_worm": 5},
            "inventory": [],
            "encyclopedia": [],
            "locations_unlocked": ["moonlight_pond", "reed_river"],
            "rng_state": self.rng.get_state(),
        }
        self._save()
        return f"🎮 新游戏开始！种子: {seed}\n\n{self._status()}"


# ==================== 全局实例 ====================
_engine = None

def _get_engine() -> FishingEngine:
    global _engine
    if _engine is None:
        _engine = FishingEngine()
    return _engine

def cmd(command: str) -> str:
    """执行游戏指令"""
    return _get_engine().cmd(command)

def new_game(seed: int = 0x9e3779b9) -> str:
    """重新开始游戏"""
    return _get_engine().new_game(seed)


# ==================== 测试 ====================
if __name__ == "__main__":
    print(cmd("help"))
    print("\n" + "="*50 + "\n")
    print(cmd("status"))
