"""
🎮 Survival Realm - 2D RPG 生存遊戲
Phase 3 製作系統與裝備進階 - 完整的生存體驗

作者: 硬漢貓咪開發團隊 🐱
日期: 2025-07-30
版本: 3.0.0
"""

import pygame
import sys
import time
import json
import random
import math
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, TYPE_CHECKING
from abc import ABC, abstractmethod

# 避免循環引用問題
if TYPE_CHECKING:
    from typing import TYPE_CHECKING

# ====== 遊戲配置常數 ======

# 視窗配置參數
WINDOW_CONFIG = {
    "width": 1280,
    "height": 720,
    "title": "Survival Realm - 生存領域",
    "fps": 60,
}

# 顏色定義 - 使用有意義的常數名稱
COLORS = {
    "PRIMARY": (57, 255, 20),  # 主要色彩 (生命綠)
    "DANGER": (255, 50, 50),  # 危險色 (血紅)
    "WARNING": (255, 165, 0),  # 警告色 (橙色)
    "INFO": (100, 150, 255),  # 資訊色 (天藍)
    "BACKGROUND": (40, 40, 40),  # 背景色 (深灰)
    "UI_PANEL": (60, 60, 60),  # UI面板色
    "TEXT": (255, 255, 255),  # 文字色 (白色)
    "TEXT_DARK": (0, 0, 0),  # 深色文字
    "HEALTH": (220, 20, 60),  # 生命值色
    "HUNGER": (255, 140, 0),  # 飢餓度色
    "THIRST": (0, 191, 255),  # 口渴度色
    "ENERGY": (255, 215, 0),  # 體力值色
    "SANITY": (138, 43, 226),  # 精神值色
}

# 玩家生存狀態參數 - 按照企劃書規格
SURVIVAL_STATS = {
    "health": {"max": 100, "regen_rate": 0.1, "current": 100},
    "hunger": {"max": 100, "decay_rate": 0.2, "current": 100},
    "thirst": {"max": 100, "decay_rate": 0.3, "current": 100},
    "energy": {"max": 100, "regen_rate": 0.15, "current": 100},
    "sanity": {"max": 100, "decay_rate": 0.05, "current": 100},
}

# 玩家移動設定
PLAYER_CONFIG = {
    "speed": 200,  # 像素/秒
    "size": (32, 32),
    "start_pos": (640, 360),  # 螢幕中央
}

# ====== 遊戲狀態枚舉 ======


class GameState(Enum):
    """遊戲狀態管理"""

    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    INVENTORY = "inventory"
    GAME_OVER = "game_over"


class TimeOfDay(Enum):
    """日夜循環狀態"""

    DAWN = "dawn"  # 黎明 05:00-07:00
    DAY = "day"  # 白天 07:00-17:00
    DUSK = "dusk"  # 黃昏 17:00-19:00
    NIGHT = "night"  # 夜晚 19:00-05:00


# ====== 核心遊戲類別 ======


@dataclass
class SurvivalStats:
    """玩家生存數值管理類"""

    health: float = 100.0
    hunger: float = 100.0
    thirst: float = 100.0
    energy: float = 100.0
    sanity: float = 100.0

    def update(self, delta_time: float) -> None:
        """
        更新生存數值 - 每幀調用

        Args:
            delta_time (float): 自上次更新的時間差(秒)
        """
        # 根據企劃書設定的衰減速率更新數值
        self.hunger = max(
            0, self.hunger - SURVIVAL_STATS["hunger"]["decay_rate"] * delta_time
        )
        self.thirst = max(
            0, self.thirst - SURVIVAL_STATS["thirst"]["decay_rate"] * delta_time
        )
        self.sanity = max(
            0, self.sanity - SURVIVAL_STATS["sanity"]["decay_rate"] * delta_time
        )

        # 體力和生命值的恢復機制
        if self.energy < SURVIVAL_STATS["energy"]["max"]:
            self.energy = min(
                SURVIVAL_STATS["energy"]["max"],
                self.energy + SURVIVAL_STATS["energy"]["regen_rate"] * delta_time,
            )

        if (
            self.health < SURVIVAL_STATS["health"]["max"]
            and self.hunger > 20
            and self.thirst > 20
        ):
            self.health = min(
                SURVIVAL_STATS["health"]["max"],
                self.health + SURVIVAL_STATS["health"]["regen_rate"] * delta_time,
            )

        # 飢餓和口渴影響生命值
        if self.hunger <= 0 or self.thirst <= 0:
            self.health = max(0, self.health - 0.5 * delta_time)


# ====== 物品系統 ======


class ItemType(Enum):
    """物品類型枚舉"""

    RESOURCE = "resource"
    CONSUMABLE = "consumable"
    EQUIPMENT = "equipment"
    VALUABLE = "valuable"
    TOOL = "tool"  # 新增：工具類型
    BUILDING = "building"  # 新增：建築物類型


@dataclass
class Item:
    """遊戲物品類"""

    id: str
    name: str
    item_type: ItemType
    stack_size: int
    description: str = ""

    def can_stack_with(self, other: "Item") -> bool:
        """檢查是否可以與另一個物品疊加"""
        return self.id == other.id and self.stack_size > 1


@dataclass
class ItemStack:
    """物品堆疊類"""

    item: Item
    quantity: int = 1

    def can_add(self, amount: int) -> bool:
        """檢查是否可以添加指定數量"""
        return self.quantity + amount <= self.item.stack_size

    def add(self, amount: int) -> int:
        """添加物品，返回實際添加的數量"""
        max_add = min(amount, self.item.stack_size - self.quantity)
        self.quantity += max_add
        return max_add

    def remove(self, amount: int) -> int:
        """移除物品，返回實際移除的數量"""
        actual_remove = min(amount, self.quantity)
        self.quantity -= actual_remove
        return actual_remove


class Inventory:
    """物品欄系統"""

    def __init__(self, size: int = 20):
        """
        初始化物品欄

        Args:
            size (int): 物品欄大小
        """
        self.size = size
        self.slots: List[Optional[ItemStack]] = [None] * size

    def add_item(self, item: Item, quantity: int = 1) -> int:
        """
        添加物品到物品欄

        Args:
            item (Item): 要添加的物品
            quantity (int): 數量

        Returns:
            int: 實際添加的數量
        """
        remaining = quantity

        # 先嘗試疊加到現有物品堆
        for slot in self.slots:
            if slot and slot.item.can_stack_with(item) and remaining > 0:
                added = slot.add(remaining)
                remaining -= added

        # 如果還有剩餘，尋找空格
        for i, slot in enumerate(self.slots):
            if slot is None and remaining > 0:
                add_amount = min(remaining, item.stack_size)
                self.slots[i] = ItemStack(item, add_amount)
                remaining -= add_amount

        return quantity - remaining

    def remove_item(self, item_id: str, quantity: int = 1) -> int:
        """
        從物品欄移除物品

        Args:
            item_id (str): 物品ID
            quantity (int): 要移除的數量

        Returns:
            int: 實際移除的數量
        """
        removed = 0

        for i, slot in enumerate(self.slots):
            if slot and slot.item.id == item_id and removed < quantity:
                need_remove = quantity - removed
                actual_remove = slot.remove(need_remove)
                removed += actual_remove

                # 如果物品堆空了，清空槽位
                if slot.quantity <= 0:
                    self.slots[i] = None

        return removed

    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """檢查是否有足夠的物品"""
        total = sum(
            slot.quantity for slot in self.slots if slot and slot.item.id == item_id
        )
        return total >= quantity

    def get_item_count(self, item_id: str) -> int:
        """獲取物品總數量"""
        return sum(
            slot.quantity for slot in self.slots if slot and slot.item.id == item_id
        )


# ====== 新增製作與裝備配置 ======

# 工具效率設定
TOOL_EFFICIENCY = {
    "hand": 1.0,  # 徒手效率
    "axe": 3.0,  # 斧頭砍樹效率
    "pickaxe": 2.5,  # 稱挖石效率
}

# 新增物品配置
ITEM_RECIPES = {
    "axe": {"wood": 3, "stone": 2},
    "pickaxe": {"wood": 2, "stone": 3},
    "bucket": {"wood": 4, "stone": 1},
    "furnace": {"stone": 8},
    "workbench": {"wood": 4},
    "iron_ingot": {"iron_ore": 1},  # 需要熔爐燒製
    "iron_sword": {"iron_ingot": 2, "wood": 1},
    "iron_armor": {"iron_ingot": 5},
}

# 礦物生成機率
MINING_CHANCES = {
    "iron_ore": 0.3,  # 30%機率挖到鐵礦
    "coal": 0.4,  # 40%機率挖到煤炭
    "rare_gem": 0.05,  # 5%機率挖到稀有寶石
}

# 新增世界物件配置
WORLD_OBJECTS = {
    "tree": {"spawn_rate": 0.3, "color": (34, 139, 34), "size": (40, 60)},
    "rock": {"spawn_rate": 0.2, "color": (105, 105, 105), "size": (30, 30)},
    "cave": {"spawn_rate": 0.05, "color": (64, 64, 64), "size": (80, 60)},
    "chest": {"spawn_rate": 0.08, "color": (218, 165, 32), "size": (35, 25)},
    "food": {"spawn_rate": 0.15, "color": (255, 0, 255), "size": (20, 20)},
    "monster": {"spawn_rate": 0.1, "color": (139, 0, 0), "size": (35, 35)},
    "river": {"spawn_rate": 0.02, "color": (0, 119, 190), "size": (120, 60)},
    "iron_ore": {"spawn_rate": 0.05, "color": (139, 69, 19), "size": (25, 25)},
}

# ====== 世界物件系統 ======


class GameObject(ABC):
    """遊戲物件基礎類"""

    def __init__(self, x: float, y: float, width: int, height: int):
        """
        初始化遊戲物件

        Args:
            x (float): X座標
            y (float): Y座標
            width (int): 寬度
            height (int): 高度
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.active = True

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """繪製物件"""
        pass

    @abstractmethod
    def interact(self, player: "Player") -> Optional[Dict]:
        """與玩家互動 - 使用字串註解避免前向引用"""
        pass

    def update_rect(self) -> None:
        """更新碰撞箱位置"""
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)


class Tree(GameObject):
    """樹木物件 - 更新工具效率"""

    def __init__(self, x: float, y: float):
        size = WORLD_OBJECTS["tree"]["size"]
        super().__init__(x, y, size[0], size[1])
        self.health = 3
        self.max_health = 3

    def draw(self, screen: pygame.Surface) -> None:
        """繪製樹木"""
        if not self.active:
            return

        color = WORLD_OBJECTS["tree"]["color"]
        # 樹幹
        trunk_rect = pygame.Rect(self.x + 15, self.y + 40, 10, 20)
        pygame.draw.rect(screen, (101, 67, 33), trunk_rect)

        # 樹冠
        crown_rect = pygame.Rect(self.x, self.y, 40, 40)
        pygame.draw.ellipse(screen, color, crown_rect)

    def interact(self, player: "Player") -> Optional[Dict]:
        """砍伐樹木 - 考慮工具效率"""
        if not self.active:
            return None

        # 根據工具效率計算傷害
        efficiency = player.get_tool_efficiency("tree")
        damage = int(efficiency)

        self.health -= damage
        if self.health <= 0:
            self.active = False
            # 斧頭砍樹獲得更多木材
            wood_amount = (
                random.randint(3, 6) if efficiency > 1 else random.randint(2, 4)
            )
            return {
                "message": f"獲得木材！(效率: {efficiency:.1f}x)",
                "items": [("wood", wood_amount)],
            }

        tool_name = "斧頭" if efficiency > 1 else "徒手"
        return {"message": f"{tool_name}砍伐中... ({self.health}/{self.max_health})"}


class Rock(GameObject):
    """石頭物件 - 更新工具效率和礦物掉落"""

    def __init__(self, x: float, y: float):
        size = WORLD_OBJECTS["rock"]["size"]
        super().__init__(x, y, size[0], size[1])
        self.health = 2
        self.max_health = 2

    def draw(self, screen: pygame.Surface) -> None:
        """繪製石頭"""
        if not self.active:
            return

        color = WORLD_OBJECTS["rock"]["color"]
        pygame.draw.ellipse(screen, color, self.rect)
        # 添加紋理
        pygame.draw.ellipse(screen, (169, 169, 169), self.rect, 3)

    def interact(self, player: "Player") -> Optional[Dict]:
        """挖掘石頭 - 考慮工具效率和礦物掉落"""
        if not self.active:
            return None

        efficiency = player.get_tool_efficiency("rock")
        damage = int(efficiency)

        self.health -= damage
        if self.health <= 0:
            self.active = False

            items = []
            # 基本石頭掉落
            stone_amount = (
                random.randint(2, 4) if efficiency > 1 else random.randint(1, 3)
            )
            items.append(("stone", stone_amount))

            # 稿子挖掘有機率獲得礦物
            if efficiency > 1:  # 使用稿子
                for ore_type, chance in MINING_CHANCES.items():
                    if random.random() < chance:
                        items.append((ore_type, 1))

            tool_name = "稿子" if efficiency > 1 else "徒手"
            message = f"獲得石頭！(效率: {efficiency:.1f}x)"
            if len(items) > 1:
                message += " 發現了礦物！"

            return {"message": message, "items": items}

        tool_name = "稿子" if efficiency > 1 else "徒手"
        return {"message": f"{tool_name}挖掘中... ({self.health}/{self.max_health})"}


class Cave(GameObject):
    """洞窟物件"""

    def __init__(self, x: float, y: float):
        size = WORLD_OBJECTS["cave"]["size"]
        super().__init__(x, y, size[0], size[1])
        self.explored = False

    def draw(self, screen: pygame.Surface) -> None:
        """繪製洞窟"""
        if not self.active:
            return

        color = WORLD_OBJECTS["cave"]["color"]
        pygame.draw.ellipse(screen, color, self.rect)

        # 洞穴入口
        entrance = pygame.Rect(self.x + 25, self.y + 20, 30, 20)
        pygame.draw.ellipse(screen, (0, 0, 0), entrance)

        if not self.explored:
            # 未探索標記
            pygame.draw.circle(
                screen, COLORS["WARNING"], (int(self.x + 10), int(self.y + 10)), 5
            )

    def interact(self, player: "Player") -> Optional[Dict]:
        """探索洞窟"""
        if not self.active:
            return None

        if not self.explored:
            self.explored = True
            # 隨機獲得資源或寶物
            if random.random() < 0.3:
                return {"message": "在洞窟深處發現了寶物！", "items": [("treasure", 1)]}
            else:
                return {
                    "message": "探索了洞窟，發現一些資源",
                    "items": [("stone", random.randint(2, 5))],
                }
        return {"message": "這個洞窟已經探索過了"}


class Chest(GameObject):
    """寶箱物件 - 降低寶物比例"""

    def __init__(self, x: float, y: float):
        size = WORLD_OBJECTS["chest"]["size"]
        super().__init__(x, y, size[0], size[1])
        self.opened = False
        self.loot = self._generate_loot()

    def _generate_loot(self) -> List[Tuple[str, int]]:
        """生成寶箱戰利品 - 降低寶物機率"""
        loot = []
        if random.random() < 0.2:  # 從0.5降低到0.2
            loot.append(("treasure", 1))
        if random.random() < 0.7:
            loot.append(("food", random.randint(2, 5)))
        if random.random() < 0.15:  # 從0.3降低到0.15
            loot.append(("iron_sword", 1))
        if random.random() < 0.3:  # 新增：工具掉落
            tool_type = random.choice(["axe", "pickaxe", "bucket"])
            loot.append((tool_type, 1))
        return loot

    def draw(self, screen: pygame.Surface) -> None:
        """繪製寶箱"""
        if not self.active:
            return

        color = WORLD_OBJECTS["chest"]["color"]
        if self.opened:
            color = (139, 69, 19)  # 暗棕色表示已開啟

        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)

        # 寶箱鎖
        if not self.opened:
            lock_pos = (int(self.x + self.width // 2), int(self.y + self.height // 2))
            pygame.draw.circle(screen, (255, 215, 0), lock_pos, 3)

    def interact(self, player: "Player") -> Optional[Dict]:
        """打開寶箱"""
        if not self.active or self.opened:
            return {"message": "寶箱已經空了"}

        self.opened = True
        return {"message": "打開了寶箱！", "items": self.loot}


class Food(GameObject):
    """食物物件"""

    def __init__(self, x: float, y: float):
        size = WORLD_OBJECTS["food"]["size"]
        super().__init__(x, y, size[0], size[1])
        self.food_type = random.choice(["berry", "mushroom", "fruit"])

    def draw(self, screen: pygame.Surface) -> None:
        """繪製食物"""
        if not self.active:
            return

        if self.food_type == "berry":
            pygame.draw.circle(
                screen, (255, 0, 127), (int(self.x + 10), int(self.y + 10)), 8
            )
        elif self.food_type == "mushroom":
            # 蘑菇莖
            stem = pygame.Rect(self.x + 8, self.y + 12, 4, 8)
            pygame.draw.rect(screen, (245, 245, 220), stem)
            # 蘑菇帽
            pygame.draw.circle(
                screen, (255, 69, 0), (int(self.x + 10), int(self.y + 8)), 8
            )
        else:  # fruit
            pygame.draw.circle(
                screen, (255, 165, 0), (int(self.x + 10), int(self.y + 10)), 8
            )

    def interact(self, player: "Player") -> Optional[Dict]:
        """收集食物"""
        if not self.active:
            return None

        self.active = False
        return {"message": f"收集了{self.food_type}！", "items": [("food", 1)]}


class Monster(GameObject):
    """怪物物件"""

    def __init__(self, x: float, y: float):
        size = WORLD_OBJECTS["monster"]["size"]
        super().__init__(x, y, size[0], size[1])
        self.health = 3
        self.max_health = 3
        self.damage = 10
        self.last_attack = 0
        self.attack_cooldown = 2.0  # 2秒攻擊間隔

    def draw(self, screen: pygame.Surface) -> None:
        """繪製怪物"""
        if not self.active:
            return

        color = WORLD_OBJECTS["monster"]["color"]
        pygame.draw.ellipse(screen, color, self.rect)

        # 怪物眼睛
        left_eye = (int(self.x + 8), int(self.y + 10))
        right_eye = (int(self.x + 25), int(self.y + 10))
        pygame.draw.circle(screen, (255, 0, 0), left_eye, 3)
        pygame.draw.circle(screen, (255, 0, 0), right_eye, 3)

        # 生命值條
        if self.health < self.max_health:
            bar_width = 30
            bar_height = 4
            bg_rect = pygame.Rect(self.x, self.y - 10, bar_width, bar_height)
            pygame.draw.rect(screen, (100, 100, 100), bg_rect)

            health_width = int((self.health / self.max_health) * bar_width)
            health_rect = pygame.Rect(self.x, self.y - 10, health_width, bar_height)
            pygame.draw.rect(screen, COLORS["HEALTH"], health_rect)

    def interact(self, player: "Player") -> Optional[Dict]:
        """戰鬥"""
        if not self.active:
            return None

        current_time = time.time()

        # 玩家攻擊怪物
        self.health -= 1

        if self.health <= 0:
            self.active = False
            # 隨機掉落物品
            drops = []
            if random.random() < 0.6:
                drops.append(("food", random.randint(1, 2)))
            if random.random() < 0.3:
                drops.append(("treasure", 1))

            return {"message": "擊敗了怪物！", "items": drops}

        # 怪物反擊
        if current_time - self.last_attack >= self.attack_cooldown:
            self.last_attack = current_time
            player.survival_stats.health -= self.damage
            return {
                "message": f"怪物攻擊了你！受到{self.damage}點傷害",
                "monster_attack": True,
            }

        return {
            "message": f"與怪物戰鬥中... 怪物生命值: {self.health}/{self.max_health}"
        }


class River(GameObject):
    """河流物件"""

    def __init__(self, x: float, y: float):
        size = WORLD_OBJECTS["river"]["size"]
        super().__init__(x, y, size[0], size[1])
        self.water_level = 100  # 水位

    def draw(self, screen: pygame.Surface) -> None:
        """繪製河流"""
        if not self.active:
            return

        color = WORLD_OBJECTS["river"]["color"]
        # 河流主體
        pygame.draw.ellipse(screen, color, self.rect)

        # 水流效果 - 簡單的波紋
        wave_color = (30, 144, 255)
        for i in range(3):
            wave_rect = pygame.Rect(self.x + i * 20, self.y + 20, 80, 20)
            pygame.draw.ellipse(screen, wave_color, wave_rect)

    def interact(self, player: "Player") -> Optional[Dict]:
        """取水互動"""
        if not self.active:
            return None

        # 檢查是否有木桶
        if player.inventory.has_item("bucket", 1):
            player.survival_stats.thirst = min(100, player.survival_stats.thirst + 50)
            return {"message": "用木桶裝了河水並喝下，恢復口渴值！"}
        else:
            # 直接用手喝水，效果較差
            player.survival_stats.thirst = min(100, player.survival_stats.thirst + 20)
            return {"message": "用手喝了河水，稍微恢復口渴值"}


# ====== 製作系統基礎類 ======


class CraftingStation(ABC):
    """製作站基礎類"""

    @abstractmethod
    def can_craft(self, recipe: Dict[str, int], inventory: Inventory) -> bool:
        """檢查是否可以製作"""
        pass

    @abstractmethod
    def craft_item(
        self, item_id: str, inventory: Inventory, item_database: Dict
    ) -> Optional[str]:
        """製作物品"""
        pass


class Workbench(CraftingStation):
    """工作臺製作站"""

    def can_craft(self, recipe: Dict[str, int], inventory: Inventory) -> bool:
        """檢查是否有足夠材料"""
        for item_id, required_amount in recipe.items():
            if not inventory.has_item(item_id, required_amount):
                return False
        return True

    def craft_item(
        self, item_id: str, inventory: Inventory, item_database: Dict
    ) -> Optional[str]:
        """在工作臺製作物品"""
        if item_id not in ITEM_RECIPES:
            return "無法製作此物品"

        recipe = ITEM_RECIPES[item_id]

        if not self.can_craft(recipe, inventory):
            return "材料不足"

        # 消耗材料
        for material, amount in recipe.items():
            inventory.remove_item(material, amount)

        # 添加製作出的物品
        if item_id in item_database:
            item = item_database[item_id]
            inventory.add_item(item, 1)
            return f"製作了 {item.name}！"

        return "製作失敗"


class Workbench(CraftingStation):
    """工作臺製作站"""

    def can_craft(self, recipe: Dict[str, int], inventory: Inventory) -> bool:
        """檢查是否有足夠材料"""
        for item_id, required_amount in recipe.items():
            if not inventory.has_item(item_id, required_amount):
                return False
        return True

    def craft_item(
        self, item_id: str, inventory: Inventory, item_database: Dict
    ) -> Optional[str]:
        """在工作臺製作物品"""
        if item_id not in ITEM_RECIPES:
            return "無法製作此物品"

        recipe = ITEM_RECIPES[item_id]

        if not self.can_craft(recipe, inventory):
            return "材料不足"

        # 消耗材料
        for material, amount in recipe.items():
            inventory.remove_item(material, amount)

        # 添加製作出的物品
        if item_id in item_database:
            item = item_database[item_id]
            inventory.add_item(item, 1)
            return f"製作了 {item.name}！"

        return "製作失敗"


class WorkbenchObject(GameObject):
    """工作臺物件"""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, 60, 40)
        self.workbench = Workbench()

    def draw(self, screen: pygame.Surface) -> None:
        """繪製工作臺"""
        if not self.active:
            return

        # 工作臺桌面
        pygame.draw.rect(screen, (139, 69, 19), self.rect)
        pygame.draw.rect(screen, (101, 67, 33), self.rect, 3)

        # 工具圖示
        tool_pos = (int(self.x + 10), int(self.y + 10))
        pygame.draw.circle(screen, (192, 192, 192), tool_pos, 5)

    def interact(self, player: "Player") -> Optional[Dict]:
        """工作臺製作互動"""
        if not self.active:
            return None

        return {"message": "工作臺：按 C 鍵開啟製作介面", "open_crafting": True}


class Furnace(CraftingStation):
    """熔爐製作站"""

    def __init__(self):
        self.fuel = 0  # 燃料值
        self.smelting_items = []  # 正在燒製的物品

    def can_craft(self, recipe: Dict[str, int], inventory: Inventory) -> bool:
        """檢查燒製條件"""
        # 需要有燃料（煤炭或木材）
        has_fuel = inventory.has_item("coal", 1) or inventory.has_item("wood", 1)

        # 檢查原料
        for item_id, required_amount in recipe.items():
            if not inventory.has_item(item_id, required_amount):
                return False

        return has_fuel

    def craft_item(
        self, item_id: str, inventory: Inventory, item_database: Dict
    ) -> Optional[str]:
        """在熔爐燒製物品"""
        if item_id not in ITEM_RECIPES:
            return "無法燒製此物品"

        recipe = ITEM_RECIPES[item_id]

        if not self.can_craft(recipe, inventory):
            return "燃料或原料不足"

        # 消耗燃料
        if inventory.has_item("coal", 1):
            inventory.remove_item("coal", 1)
            self.fuel += 3  # 煤炭燃料值高
        elif inventory.has_item("wood", 1):
            inventory.remove_item("wood", 1)
            self.fuel += 1  # 木材燃料值低

        # 消耗原料
        for material, amount in recipe.items():
            inventory.remove_item(material, amount)

        # 添加燒製出的物品
        if item_id in item_database:
            item = item_database[item_id]
            inventory.add_item(item, 1)
            self.fuel -= 1
            return f"燒製了 {item.name}！"

        return "燒製失敗"


class Furnace(CraftingStation):
    """熔爐製作站"""

    def __init__(self):
        self.fuel = 0  # 燃料值
        self.smelting_items = []  # 正在燒製的物品

    def can_craft(self, recipe: Dict[str, int], inventory: Inventory) -> bool:
        """檢查燒製條件"""
        # 需要有燃料（煤炭或木材）
        has_fuel = inventory.has_item("coal", 1) or inventory.has_item("wood", 1)

        # 檢查原料
        for item_id, required_amount in recipe.items():
            if not inventory.has_item(item_id, required_amount):
                return False

        return has_fuel

    def craft_item(
        self, item_id: str, inventory: Inventory, item_database: Dict
    ) -> Optional[str]:
        """在熔爐燒製物品"""
        if item_id not in ITEM_RECIPES:
            return "無法燒製此物品"

        recipe = ITEM_RECIPES[item_id]

        if not self.can_craft(recipe, inventory):
            return "燃料或原料不足"

        # 消耗燃料
        if inventory.has_item("coal", 1):
            inventory.remove_item("coal", 1)
            self.fuel += 3  # 煤炭燃料值高
        elif inventory.has_item("wood", 1):
            inventory.remove_item("wood", 1)
            self.fuel += 1  # 木材燃料值低

        # 消耗原料
        for material, amount in recipe.items():
            inventory.remove_item(material, amount)

        # 添加燒製出的物品
        if item_id in item_database:
            item = item_database[item_id]
            inventory.add_item(item, 1)
            self.fuel -= 1
            return f"燒製了 {item.name}！"

        return "燒製失敗"


class FurnaceObject(GameObject):
    """熔爐物件"""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, 50, 60)
        self.furnace = Furnace()
        self.is_lit = False

    def draw(self, screen: pygame.Surface) -> None:
        """繪製熔爐"""
        if not self.active:
            return

        # 熔爐主體
        furnace_color = (105, 105, 105) if not self.is_lit else (139, 69, 19)
        pygame.draw.rect(screen, furnace_color, self.rect)
        pygame.draw.rect(screen, (64, 64, 64), self.rect, 3)

        # 爐火效果
        if self.is_lit:
            fire_rect = pygame.Rect(self.x + 15, self.y + 10, 20, 30)
            pygame.draw.ellipse(screen, (255, 69, 0), fire_rect)
            pygame.draw.ellipse(
                screen, (255, 215, 0), pygame.Rect(self.x + 18, self.y + 15, 14, 20)
            )

    def interact(self, player: "Player") -> Optional[Dict]:
        """熔爐互動"""
        if not self.active:
            return None

        self.is_lit = True
        return {"message": "熔爐：按 S 鍵開啟燒製介面", "open_smelting": True}


# ====== 更新現有類別 ======


class Player:
    """玩家角色類 - 新增裝備和工具系統"""

    def __init__(self, x: float, y: float) -> None:
        """
        初始化玩家角色

        Args:
            x (float): 初始X座標
            y (float): 初始Y座標
        """
        self.x = x
        self.y = y
        self.width = PLAYER_CONFIG["size"][0]
        self.height = PLAYER_CONFIG["size"][1]
        self.speed = PLAYER_CONFIG["speed"]

        # 生存狀態管理
        self.survival_stats = SurvivalStats()

        # 玩家矩形碰撞箱
        self.rect = pygame.Rect(x, y, self.width, self.height)

        # 移動狀態
        self.velocity_x = 0
        self.velocity_y = 0

        # 新增：物品欄系統
        self.inventory = Inventory(20)

        # 新增：互動設定
        self.interaction_range = 50
        self.last_interaction = 0
        self.interaction_cooldown = 0.5  # 0.5秒互動冷卻

        # 新增：裝備系統
        self.equipped_tool = None  # 當前裝備的工具
        self.equipped_weapon = None  # 當前裝備的武器
        self.equipped_armor = None  # 當前裝備的護甲

        # 新增：製作系統狀態
        self.crafting_mode = False
        self.smelting_mode = False

        # 初始化物品資料
        self._init_items()

    def _init_items(self) -> None:
        """初始化物品資料庫"""
        self.item_database = {
            # 基礎資源
            "wood": Item("wood", "木材", ItemType.RESOURCE, 64, "用於建造的基礎材料"),
            "stone": Item("stone", "石頭", ItemType.RESOURCE, 64, "堅固的建築材料"),
            "food": Item("food", "食物", ItemType.CONSUMABLE, 32, "恢復飢餓值"),
            "treasure": Item("treasure", "寶物", ItemType.VALUABLE, 1, "珍貴的寶物"),
            # 新增：礦物資源
            "iron_ore": Item(
                "iron_ore", "鐵礦", ItemType.RESOURCE, 32, "可以燒製成鐵錠"
            ),
            "coal": Item("coal", "煤炭", ItemType.RESOURCE, 32, "優質燃料"),
            "rare_gem": Item(
                "rare_gem", "稀有寶石", ItemType.VALUABLE, 1, "極其珍貴的寶石"
            ),
            "iron_ingot": Item(
                "iron_ingot", "鐵錠", ItemType.RESOURCE, 16, "燒製後的鐵"
            ),
            # 新增：工具
            "axe": Item("axe", "斧頭", ItemType.TOOL, 1, "砍樹專用工具，效率提升"),
            "pickaxe": Item(
                "pickaxe", "稿子", ItemType.TOOL, 1, "挖掘專用工具，效率提升"
            ),
            "bucket": Item("bucket", "木桶", ItemType.TOOL, 1, "用於取水的容器"),
            # 新增：建築物
            "workbench": Item(
                "workbench", "工作臺", ItemType.BUILDING, 1, "製作工具的地方"
            ),
            "furnace": Item("furnace", "熔爐", ItemType.BUILDING, 1, "燒製礦物的設備"),
            # 新增：裝備
            "iron_sword": Item(
                "iron_sword", "鐵劍", ItemType.EQUIPMENT, 1, "強力的鐵製武器"
            ),
            "iron_armor": Item(
                "iron_armor", "鐵甲", ItemType.EQUIPMENT, 1, "防護力強的鐵製護甲"
            ),
        }

    def get_tool_efficiency(self, target_type: str) -> float:
        """獲取當前工具對特定目標的效率"""
        if (
            target_type == "tree"
            and self.equipped_tool
            and self.equipped_tool.id == "axe"
        ):
            return TOOL_EFFICIENCY["axe"]
        elif (
            target_type == "rock"
            and self.equipped_tool
            and self.equipped_tool.id == "pickaxe"
        ):
            return TOOL_EFFICIENCY["pickaxe"]
        return TOOL_EFFICIENCY["hand"]

    def equip_item(self, item_id: str) -> bool:
        """裝備物品"""
        if not self.inventory.has_item(item_id, 1):
            return False

        item = self.item_database.get(item_id)
        if not item:
            return False

        if item.item_type == ItemType.TOOL:
            self.equipped_tool = item
        elif item.item_type == ItemType.EQUIPMENT:
            if "sword" in item_id:
                self.equipped_weapon = item
            elif "armor" in item_id:
                self.equipped_armor = item

        return True

    def place_building(
        self, item_id: str, world_manager: "WorldManager"
    ) -> Optional[str]:
        """放置建築物"""
        if not self.inventory.has_item(item_id, 1):
            return "沒有此建築物"

        # 計算放置位置（玩家前方）
        place_x = self.x + 50
        place_y = self.y

        # 檢查位置是否有空間
        new_rect = pygame.Rect(place_x, place_y, 60, 40)
        for obj in world_manager.objects:
            if obj.active and new_rect.colliderect(obj.rect):
                return "此位置無法放置建築物"

        # 移除物品並放置建築
        self.inventory.remove_item(item_id, 1)

        if item_id == "workbench":
            world_manager.objects.append(WorkbenchObject(place_x, place_y))
            return "放置了工作臺！"
        elif item_id == "furnace":
            world_manager.objects.append(FurnaceObject(place_x, place_y))
            return "放置了熔爐！"

        return "放置失敗"

    def craft_item(self, item_id: str, station: CraftingStation) -> Optional[str]:
        """使用製作站製作物品"""
        return station.craft_item(item_id, self.inventory, self.item_database)

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        """
        處理玩家輸入

        Args:
            keys: pygame按鍵狀態
        """
        self.velocity_x = 0
        self.velocity_y = 0

        # WASD 移動控制
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.velocity_y = -self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.velocity_y = self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velocity_x = -self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velocity_x = self.speed

        # 移動時消耗體力
        if self.velocity_x != 0 or self.velocity_y != 0:
            if self.survival_stats.energy > 0:
                self.survival_stats.energy = max(0, self.survival_stats.energy - 0.1)

    def interact_with_world(self, world_manager: "WorldManager") -> Optional[str]:
        """與世界物件互動 - 使用字串註解避免前向引用"""
        current_time = time.time()
        if current_time - self.last_interaction < self.interaction_cooldown:
            return None

        # 獲取附近物件
        nearby_objects = world_manager.get_nearby_objects(
            self.x + self.width // 2, self.y + self.height // 2, self.interaction_range
        )

        if not nearby_objects:
            return "附近沒有可互動的物件"

        # 互動最近的物件
        closest_obj = min(
            nearby_objects,
            key=lambda obj: math.sqrt((obj.x - self.x) ** 2 + (obj.y - self.y) ** 2),
        )

        result = closest_obj.interact(self)
        if result:
            self.last_interaction = current_time

            # 處理獲得的物品
            if "items" in result:
                for item_id, quantity in result["items"]:
                    if item_id in self.item_database:
                        item = self.item_database[item_id]
                        added = self.inventory.add_item(item, quantity)
                        if added < quantity:
                            return f"{result['message']} (物品欄已滿，丟失了{quantity - added}個{item.name})"

            return result["message"]

        return None

    def consume_food(self) -> bool:
        """消耗食物恢復飢餓值"""
        if self.inventory.has_item("food", 1):
            removed = self.inventory.remove_item("food", 1)
            if removed > 0:
                self.survival_stats.hunger = min(100, self.survival_stats.hunger + 30)
                return True
        return False

    def update(self, delta_time: float) -> None:
        """
        更新玩家狀態

        Args:
            delta_time (float): 幀時間差
        """
        # 更新位置
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time

        # 螢幕邊界檢查
        self.x = max(0, min(WINDOW_CONFIG["width"] - self.width, self.x))
        self.y = max(0, min(WINDOW_CONFIG["height"] - self.height, self.y))

        # 更新碰撞箱
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # 更新生存數值
        self.survival_stats.update(delta_time)

    def draw(self, screen: pygame.Surface) -> None:
        """
        繪製玩家角色

        Args:
            screen: pygame螢幕物件
        """
        # 簡單的矩形表示玩家 (後續可替換為精靈圖)
        pygame.draw.rect(screen, COLORS["PRIMARY"], self.rect)

        # 繪製簡單的眼睛表示方向
        eye_size = 4
        left_eye = (int(self.x + 8), int(self.y + 8))
        right_eye = (int(self.x + 24), int(self.y + 8))
        pygame.draw.circle(screen, COLORS["TEXT"], left_eye, eye_size)
        pygame.draw.circle(screen, COLORS["TEXT"], right_eye, eye_size)


# ====== 時間管理系統 ======


class TimeManager:
    """時間管理系統 - 處理日夜循環"""

    def __init__(self) -> None:
        """初始化時間管理器"""
        self.game_time = 0.0  # 遊戲內時間 (秒)
        self.time_scale = 60.0  # 時間倍率 (1遊戲分鐘 = 1實際秒)
        self.current_day = 1

    def update(self, delta_time: float) -> None:
        """
        更新遊戲時間

        Args:
            delta_time (float): 實際時間差
        """
        self.game_time += delta_time * self.time_scale

        # 一天 = 1440 遊戲秒 (24小時)
        if self.game_time >= 1440:
            self.game_time = 0
            self.current_day += 1

    def get_time_of_day(self) -> TimeOfDay:
        """
        獲取當前時段

        Returns:
            TimeOfDay: 當前時段枚舉
        """
        # 將遊戲時間轉換為小時 (0-24)
        hour = (self.game_time / 60) % 24

        if 5 <= hour < 7:
            return TimeOfDay.DAWN
        elif 7 <= hour < 17:
            return TimeOfDay.DAY
        elif 17 <= hour < 19:
            return TimeOfDay.DUSK
        else:
            return TimeOfDay.NIGHT

    def get_time_string(self) -> str:
        """
        獲取時間字串顯示

        Returns:
            str: 格式化的時間字串
        """
        total_minutes = int(self.game_time)
        hours = (total_minutes // 60) % 24
        minutes = total_minutes % 60
        return f"第{self.current_day}天 {hours:02d}:{minutes:02d}"


# ====== 使用者介面管理類 ======


class UI:
    """使用者介面管理類 - 新增製作介面"""

    def __init__(self) -> None:
        """初始化UI系統"""
        pygame.font.init()

        # 使用 Microsoft JhengHei 字體支援中文顯示
        font_path = "C:/Windows/Fonts/msjh.ttc"  # 微軟正黑體

        try:
            self.font = pygame.font.Font(font_path, 24)
            self.small_font = pygame.font.Font(font_path, 18)
            self.tiny_font = pygame.font.Font(font_path, 14)
            print("✅ 成功載入 Microsoft JhengHei 字體！")
        except FileNotFoundError:
            # 備用方案：嘗試其他系統字體
            try:
                alt_font_path = "C:/Windows/Fonts/simhei.ttf"  # 黑體
                self.font = pygame.font.Font(alt_font_path, 24)
                self.small_font = pygame.font.Font(alt_font_path, 18)
                self.tiny_font = pygame.font.Font(alt_font_path, 14)
                print("⚠️  使用黑體作為備用字體")
            except FileNotFoundError:
                # 最後備用：系統預設字體
                self.font = pygame.font.Font(None, 24)
                self.small_font = pygame.font.Font(None, 18)
                self.tiny_font = pygame.font.Font(None, 14)
                print("❌ 無法載入中文字體，使用預設字體")

    def draw_survival_bars(self, screen: pygame.Surface, player: "Player") -> None:
        """
        繪製生存狀態條

        Args:
            screen: pygame螢幕物件
            player: 玩家物件
        """
        bar_width = 200
        bar_height = 20
        bar_spacing = 30
        start_x = 20
        start_y = 20

        stats = player.survival_stats
        stat_data = [
            ("生命值", stats.health, SURVIVAL_STATS["health"]["max"], COLORS["HEALTH"]),
            ("飢餓度", stats.hunger, SURVIVAL_STATS["hunger"]["max"], COLORS["HUNGER"]),
            ("口渴度", stats.thirst, SURVIVAL_STATS["thirst"]["max"], COLORS["THIRST"]),
            ("體力值", stats.energy, SURVIVAL_STATS["energy"]["max"], COLORS["ENERGY"]),
            ("精神值", stats.sanity, SURVIVAL_STATS["sanity"]["max"], COLORS["SANITY"]),
        ]

        for i, (name, current, max_val, color) in enumerate(stat_data):
            y = start_y + i * bar_spacing

            # 繪製背景條
            bg_rect = pygame.Rect(start_x, y, bar_width, bar_height)
            pygame.draw.rect(screen, COLORS["UI_PANEL"], bg_rect)
            pygame.draw.rect(screen, COLORS["TEXT"], bg_rect, 2)

            # 繪製數值條
            fill_width = int((current / max_val) * bar_width)
            if fill_width > 0:
                fill_rect = pygame.Rect(start_x, y, fill_width, bar_height)
                pygame.draw.rect(screen, color, fill_rect)

            # 繪製文字標籤
            text = f"{name}: {int(current)}/{int(max_val)}"
            text_surface = self.small_font.render(text, True, COLORS["TEXT"])
            screen.blit(text_surface, (start_x + bar_width + 10, y + 2))

    def draw_time_info(self, screen: pygame.Surface, time_manager: TimeManager) -> None:
        """
        繪製時間資訊

        Args:
            screen: pygame螢幕物件
            time_manager: 時間管理器
        """
        time_str = time_manager.get_time_string()
        time_of_day = time_manager.get_time_of_day()

        # 時間顯示
        time_text = self.font.render(time_str, True, COLORS["TEXT"])
        screen.blit(time_text, (WINDOW_CONFIG["width"] - 200, 20))

        # 時段顯示
        period_text = self.font.render(time_of_day.value, True, COLORS["WARNING"])
        screen.blit(period_text, (WINDOW_CONFIG["width"] - 200, 50))

    def draw_inventory(self, screen: pygame.Surface, inventory: Inventory) -> None:
        """
        繪製物品欄介面

        Args:
            screen: pygame螢幕物件
            inventory: 物品欄物件
        """
        # 物品欄背景
        inv_width = 400
        inv_height = 300
        inv_x = (WINDOW_CONFIG["width"] - inv_width) // 2
        inv_y = (WINDOW_CONFIG["height"] - inv_height) // 2

        bg_rect = pygame.Rect(inv_x, inv_y, inv_width, inv_height)
        pygame.draw.rect(screen, COLORS["UI_PANEL"], bg_rect)
        pygame.draw.rect(screen, COLORS["TEXT"], bg_rect, 3)

        # 標題
        title_text = self.font.render("物品欄", True, COLORS["TEXT"])
        title_rect = title_text.get_rect(centerx=inv_x + inv_width // 2, y=inv_y + 10)
        screen.blit(title_text, title_rect)

        # 繪製物品格子
        slot_size = 40
        slots_per_row = 5
        slot_spacing = 5
        start_x = inv_x + 20
        start_y = inv_y + 50

        for i in range(inventory.size):
            row = i // slots_per_row
            col = i % slots_per_row

            slot_x = start_x + col * (slot_size + slot_spacing)
            slot_y = start_y + row * (slot_size + slot_spacing)

            slot_rect = pygame.Rect(slot_x, slot_y, slot_size, slot_size)

            # 繪製格子背景
            pygame.draw.rect(screen, COLORS["BACKGROUND"], slot_rect)
            pygame.draw.rect(screen, COLORS["TEXT"], slot_rect, 2)

            # 如果有物品，繪製物品
            if i < len(inventory.slots) and inventory.slots[i]:
                item_stack = inventory.slots[i]

                # 根據物品類型選擇顏色
                item_colors = {
                    ItemType.RESOURCE: (139, 69, 19),  # 棕色
                    ItemType.CONSUMABLE: (255, 140, 0),  # 橙色
                    ItemType.EQUIPMENT: (192, 192, 192),  # 銀色
                    ItemType.VALUABLE: (255, 215, 0),  # 金色
                }

                item_color = item_colors.get(item_stack.item.item_type, COLORS["TEXT"])

                # 繪製物品圖示 (簡單的圓形)
                center = (slot_x + slot_size // 2, slot_y + slot_size // 2)
                pygame.draw.circle(screen, item_color, center, 12)

                # 繪製數量
                if item_stack.quantity > 1:
                    qty_text = self.tiny_font.render(
                        str(item_stack.quantity), True, COLORS["TEXT"]
                    )
                    qty_pos = (slot_x + slot_size - 15, slot_y + slot_size - 15)
                    screen.blit(qty_text, qty_pos)

        # 物品說明區域
        info_y = start_y + 4 * (slot_size + slot_spacing) + 20
        info_text = self.small_font.render("物品統計:", True, COLORS["TEXT"])
        screen.blit(info_text, (start_x, info_y))

        # 統計各類物品數量
        item_counts = {}
        for slot in inventory.slots:
            if slot:
                item_id = slot.item.id
                item_counts[item_id] = item_counts.get(item_id, 0) + slot.quantity

        y_offset = info_y + 25
        for item_id, count in item_counts.items():
            if item_id in ["wood", "stone", "food", "treasure", "weapon"]:
                item_names = {
                    "wood": "木材",
                    "stone": "石頭",
                    "food": "食物",
                    "treasure": "寶物",
                    "weapon": "武器",
                }
                text = f"{item_names.get(item_id, item_id)}: {count}"
                count_text = self.tiny_font.render(text, True, COLORS["TEXT"])
                screen.blit(count_text, (start_x, y_offset))
                y_offset += 20

    def draw_crafting_interface(self, screen: pygame.Surface, player: "Player") -> None:
        """繪製製作介面"""
        craft_width = 500
        craft_height = 400
        craft_x = (WINDOW_CONFIG["width"] - craft_width) // 2
        craft_y = (WINDOW_CONFIG["height"] - craft_height) // 2

        bg_rect = pygame.Rect(craft_x, craft_y, craft_width, craft_height)
        pygame.draw.rect(screen, COLORS["UI_PANEL"], bg_rect)
        pygame.draw.rect(screen, COLORS["TEXT"], bg_rect, 3)

        # 標題
        title_text = self.font.render("工作臺 - 製作", True, COLORS["TEXT"])
        title_rect = title_text.get_rect(
            centerx=craft_x + craft_width // 2, y=craft_y + 10
        )
        screen.blit(title_text, title_rect)

        # 顯示可製作的配方
        recipes = {
            "axe": {"materials": {"wood": 3, "stone": 2}, "name": "斧頭"},
            "pickaxe": {"materials": {"wood": 2, "stone": 3}, "name": "稿子"},
            "bucket": {"materials": {"wood": 4, "stone": 1}, "name": "木桶"},
            "workbench": {"materials": {"wood": 4}, "name": "工作臺"},
            "furnace": {"materials": {"stone": 8}, "name": "熔爐"},
        }

        y_offset = craft_y + 50
        for i, (item_id, recipe_data) in enumerate(recipes.items()):
            # 檢查是否可以製作
            can_craft = all(
                player.inventory.has_item(mat, amount)
                for mat, amount in recipe_data["materials"].items()
            )

            color = COLORS["PRIMARY"] if can_craft else COLORS["TEXT_DARK"]

            # 配方名稱
            recipe_text = f"{i+1}. {recipe_data['name']}"
            text_surface = self.small_font.render(recipe_text, True, color)
            screen.blit(text_surface, (craft_x + 20, y_offset))

            # 材料需求
            materials_text = " | ".join(
                [f"{mat}:{amount}" for mat, amount in recipe_data["materials"].items()]
            )
            mat_surface = self.tiny_font.render(materials_text, True, color)
            screen.blit(mat_surface, (craft_x + 20, y_offset + 20))

            y_offset += 50

        # 操作說明
        help_text = "按對應數字鍵製作物品，ESC退出"
        help_surface = self.tiny_font.render(help_text, True, COLORS["WARNING"])
        screen.blit(help_surface, (craft_x + 20, craft_y + craft_height - 30))

    def draw_smelting_interface(self, screen: pygame.Surface, player: "Player") -> None:
        """繪製燒製介面"""
        craft_width = 400
        craft_height = 300
        craft_x = (WINDOW_CONFIG["width"] - craft_width) // 2
        craft_y = (WINDOW_CONFIG["height"] - craft_height) // 2

        bg_rect = pygame.Rect(craft_x, craft_y, craft_width, craft_height)
        pygame.draw.rect(screen, COLORS["UI_PANEL"], bg_rect)
        pygame.draw.rect(screen, COLORS["TEXT"], bg_rect, 3)

        # 標題
        title_text = self.font.render("熔爐 - 燒製", True, COLORS["TEXT"])
        title_rect = title_text.get_rect(
            centerx=craft_x + craft_width // 2, y=craft_y + 10
        )
        screen.blit(title_text, title_rect)

        # 燒製配方
        smelting_recipes = {
            "iron_ingot": {"material": "iron_ore", "name": "鐵錠", "fuel": "煤炭/木材"},
        }

        y_offset = craft_y + 50
        for i, (item_id, recipe_data) in enumerate(smelting_recipes.items()):
            has_material = player.inventory.has_item(recipe_data["material"], 1)
            has_fuel = player.inventory.has_item(
                "coal", 1
            ) or player.inventory.has_item("wood", 1)
            can_smelt = has_material and has_fuel

            color = COLORS["PRIMARY"] if can_smelt else COLORS["TEXT_DARK"]

            recipe_text = f"{i+1}. {recipe_data['name']} (需要: {recipe_data['material']} + {recipe_data['fuel']})"
            text_surface = self.small_font.render(recipe_text, True, color)
            screen.blit(text_surface, (craft_x + 20, y_offset))

            y_offset += 40

        # 操作說明
        help_text = "按對應數字鍵燒製物品，ESC退出"
        help_surface = self.tiny_font.render(help_text, True, COLORS["WARNING"])
        screen.blit(help_surface, (craft_x + 20, craft_y + craft_height - 30))


# ====== 世界管理系統 ======


class WorldManager:
    """世界物件管理系統"""

    def __init__(self) -> None:
        """初始化世界管理器"""
        self.objects: List[GameObject] = []
        self.spawn_timer = 0
        self.spawn_interval = 5.0  # 5秒生成一次新物件

    def generate_world(self) -> None:
        """生成初始世界物件"""
        # 隨機生成各種物件
        num_objects = 50

        for _ in range(num_objects):
            x = random.randint(50, WINDOW_CONFIG["width"] - 50)
            y = random.randint(50, WINDOW_CONFIG["height"] - 50)

            # 根據機率生成不同物件
            rand = random.random()
            cumulative = 0

            for obj_type, config in WORLD_OBJECTS.items():
                cumulative += config["spawn_rate"]
                if rand <= cumulative:
                    self._spawn_object(obj_type, x, y)
                    break

    def _spawn_object(self, obj_type: str, x: float, y: float) -> None:
        """在指定位置生成物件"""
        if obj_type == "tree":
            self.objects.append(Tree(x, y))
        elif obj_type == "rock":
            self.objects.append(Rock(x, y))
        elif obj_type == "cave":
            self.objects.append(Cave(x, y))
        elif obj_type == "chest":
            self.objects.append(Chest(x, y))
        elif obj_type == "food":
            self.objects.append(Food(x, y))
        elif obj_type == "monster":
            self.objects.append(Monster(x, y))
        elif obj_type == "river":
            self.objects.append(River(x, y))

    def update(self, delta_time: float) -> None:
        """更新世界物件"""
        self.spawn_timer += delta_time

        # 定期生成新物件（非怪物）
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self._spawn_random_object()

        # 移除已摧毀的物件
        self.objects = [obj for obj in self.objects if obj.active]

    def _spawn_random_object(self) -> None:
        """隨機生成物件"""
        # 限制總物件數量
        if len(self.objects) >= 60:
            return

        x = random.randint(50, WINDOW_CONFIG["width"] - 50)
        y = random.randint(50, WINDOW_CONFIG["height"] - 50)

        # 避免在玩家附近生成
        if 600 <= x <= 680 and 320 <= y <= 400:
            return

        # 生成非怪物物件
        safe_objects = ["tree", "rock", "food", "river"]
        obj_type = random.choice(safe_objects)
        self._spawn_object(obj_type, x, y)

    def get_nearby_objects(self, x: float, y: float, radius: float) -> List[GameObject]:
        """獲取指定範圍內的物件"""
        nearby = []
        for obj in self.objects:
            if not obj.active:
                continue

            distance = math.sqrt((obj.x - x) ** 2 + (obj.y - y) ** 2)
            if distance <= radius:
                nearby.append(obj)

        return nearby

    def draw(self, screen: pygame.Surface) -> None:
        """繪製所有世界物件"""
        for obj in self.objects:
            if obj.active:
                obj.draw(screen)


# ====== 主遊戲類 ======


class Game:
    """主遊戲類 - 遊戲核心邏輯管理"""

    def __init__(self) -> None:
        """初始化遊戲"""
        pygame.init()

        # 建立遊戲視窗
        self.screen = pygame.display.set_mode(
            (WINDOW_CONFIG["width"], WINDOW_CONFIG["height"])
        )
        pygame.display.set_caption(WINDOW_CONFIG["title"])

        # 時鐘控制
        self.clock = pygame.time.Clock()

        # 遊戲狀態
        self.state = GameState.PLAYING
        self.running = True

        # 初始化各系統
        self.player = Player(
            PLAYER_CONFIG["start_pos"][0], PLAYER_CONFIG["start_pos"][1]
        )
        self.world_manager = WorldManager()
        self.time_manager = TimeManager()
        self.ui = UI()

        # 訊息系統
        self.messages: List[Tuple[str, float]] = []  # (訊息, 顯示時間)
        self.message_duration = 3.0  # 訊息顯示3秒

        # 生成初始世界
        self.world_manager.generate_world()

        print("🎮 Survival Realm 初始化完成！")
        print("📖 操作說明:")
        print("   WASD - 移動角色")
        print("   E - 與物件互動")
        print("   F - 消耗食物")
        print("   I - 開啟物品欄")
        print("   C - 製作介面 (需靠近工作臺)")
        print("   S - 燒製介面 (需靠近熔爐)")
        print("   1-5 - 裝備物品或製作")
        print("   ESC - 暫停遊戲")

    def handle_events(self) -> None:
        """處理遊戲事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state in [GameState.PAUSED, GameState.INVENTORY]:
                        self.state = GameState.PLAYING
                        self.player.crafting_mode = False
                        self.player.smelting_mode = False

                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_e:
                        # 與世界互動
                        message = self.player.interact_with_world(self.world_manager)
                        if message:
                            self.add_message(message)

                    elif event.key == pygame.K_f:
                        # 消耗食物
                        if self.player.consume_food():
                            self.add_message("消耗食物，恢復飢餓值！")
                        else:
                            self.add_message("沒有食物可以消耗")

                    elif event.key == pygame.K_i:
                        # 切換物品欄
                        self.state = (
                            GameState.INVENTORY
                            if self.state != GameState.INVENTORY
                            else GameState.PLAYING
                        )

                    elif event.key == pygame.K_c:
                        # 製作介面
                        self.player.crafting_mode = not self.player.crafting_mode
                        self.player.smelting_mode = False

                    elif event.key == pygame.K_s:
                        # 燒製介面
                        self.player.smelting_mode = not self.player.smelting_mode
                        self.player.crafting_mode = False

                    # 數字鍵操作
                    elif pygame.K_1 <= event.key <= pygame.K_5:
                        number = event.key - pygame.K_1 + 1
                        self._handle_number_key(number)

    def _handle_number_key(self, number: int) -> None:
        """處理數字鍵操作"""
        if self.player.crafting_mode:
            # 製作物品
            recipes = ["axe", "pickaxe", "bucket", "workbench", "furnace"]
            if 1 <= number <= len(recipes):
                item_id = recipes[number - 1]
                message = self._craft_item(item_id)
                if message:
                    self.add_message(message)

        elif self.player.smelting_mode:
            # 燒製物品
            if number == 1:  # 只有鐵錠可以燒製
                message = self._smelt_item("iron_ingot")
                if message:
                    self.add_message(message)

        else:
            # 裝備物品
            tools = ["axe", "pickaxe", "bucket", "iron_sword", "iron_armor"]
            if 1 <= number <= len(tools):
                item_id = tools[number - 1]
                if self.player.inventory.has_item(item_id, 1):
                    self.player.equip_item(item_id)
                    self.add_message(f"裝備了 {item_id}！")

    def _craft_item(self, item_id: str) -> Optional[str]:
        """製作物品"""
        if item_id not in ITEM_RECIPES:
            return "無法製作此物品"

        recipe = ITEM_RECIPES[item_id]

        # 檢查材料
        for material, amount in recipe.items():
            if not self.player.inventory.has_item(material, amount):
                return f"缺少材料: {material} x{amount}"

        # 消耗材料
        for material, amount in recipe.items():
            self.player.inventory.remove_item(material, amount)

        # 添加製作出的物品
        if item_id in self.player.item_database:
            item = self.player.item_database[item_id]
            added = self.player.inventory.add_item(item, 1)
            if added > 0:
                return f"製作了 {item.name}！"
            else:
                return "物品欄已滿"

        return "製作失敗"

    def _smelt_item(self, item_id: str) -> Optional[str]:
        """燒製物品"""
        if item_id == "iron_ingot":
            if not self.player.inventory.has_item("iron_ore", 1):
                return "缺少鐵礦"

            has_fuel = self.player.inventory.has_item(
                "coal", 1
            ) or self.player.inventory.has_item("wood", 1)
            if not has_fuel:
                return "缺少燃料(煤炭或木材)"

            # 消耗材料和燃料
            self.player.inventory.remove_item("iron_ore", 1)
            if self.player.inventory.has_item("coal", 1):
                self.player.inventory.remove_item("coal", 1)
            else:
                self.player.inventory.remove_item("wood", 1)

            # 添加鐵錠
            item = self.player.item_database["iron_ingot"]
            added = self.player.inventory.add_item(item, 1)
            if added > 0:
                return "燒製了鐵錠！"
            else:
                return "物品欄已滿"

        return "無法燒製此物品"

    def add_message(self, message: str) -> None:
        """添加遊戲訊息"""
        current_time = time.time()
        self.messages.append((message, current_time))

        # 限制訊息數量
        if len(self.messages) > 5:
            self.messages.pop(0)

    def update(self) -> None:
        """更新遊戲邏輯"""
        if self.state != GameState.PLAYING:
            return

        # 計算幀時間
        delta_time = self.clock.get_time() / 1000.0

        # 處理玩家輸入
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)

        # 更新各系統
        self.player.update(delta_time)
        self.world_manager.update(delta_time)
        self.time_manager.update(delta_time)

        # 清理過期訊息
        current_time = time.time()
        self.messages = [
            (msg, timestamp)
            for msg, timestamp in self.messages
            if current_time - timestamp < self.message_duration
        ]

        # 檢查遊戲結束條件
        if self.player.survival_stats.health <= 0:
            self.state = GameState.GAME_OVER

    def draw(self) -> None:
        """繪製遊戲畫面"""
        # 清空螢幕
        self.screen.fill(COLORS["BACKGROUND"])

        if self.state == GameState.PLAYING:
            # 繪製世界物件
            self.world_manager.draw(self.screen)

            # 繪製玩家
            self.player.draw(self.screen)

            # 繪製UI
            self.ui.draw_survival_bars(self.screen, self.player)
            self.ui.draw_time_info(self.screen, self.time_manager)

            # 繪製訊息
            self._draw_messages()

            # 繪製製作/燒製介面
            if self.player.crafting_mode:
                self.ui.draw_crafting_interface(self.screen, self.player)
            elif self.player.smelting_mode:
                self.ui.draw_smelting_interface(self.screen, self.player)

        elif self.state == GameState.INVENTORY:
            # 繪製物品欄
            self.ui.draw_inventory(self.screen, self.player.inventory)

        elif self.state == GameState.PAUSED:
            # 繪製暫停畫面
            self._draw_pause_screen()

        elif self.state == GameState.GAME_OVER:
            # 繪製遊戲結束畫面
            self._draw_game_over_screen()

        # 更新顯示
        pygame.display.flip()

    def _draw_messages(self) -> None:
        """繪製遊戲訊息"""
        y_offset = WINDOW_CONFIG["height"] - 150
        for message, timestamp in self.messages:
            # 計算透明度（訊息即將消失時變淡）
            current_time = time.time()
            age = current_time - timestamp
            alpha = max(0, min(255, int(255 * (1 - age / self.message_duration))))

            # 創建半透明表面
            text_surface = self.ui.small_font.render(message, True, COLORS["TEXT"])
            text_surface.set_alpha(alpha)

            self.screen.blit(text_surface, (20, y_offset))
            y_offset -= 25

    def _draw_pause_screen(self) -> None:
        """繪製暫停畫面"""
        # 半透明覆蓋層
        overlay = pygame.Surface((WINDOW_CONFIG["width"], WINDOW_CONFIG["height"]))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # 暫停文字
        pause_text = self.ui.font.render("遊戲暫停", True, COLORS["TEXT"])
        text_rect = pause_text.get_rect(
            center=(WINDOW_CONFIG["width"] // 2, WINDOW_CONFIG["height"] // 2)
        )
        self.screen.blit(pause_text, text_rect)

        # 提示文字
        hint_text = self.ui.small_font.render("按 ESC 繼續遊戲", True, COLORS["TEXT"])
        hint_rect = hint_text.get_rect(
            center=(WINDOW_CONFIG["width"] // 2, WINDOW_CONFIG["height"] // 2 + 50)
        )
        self.screen.blit(hint_text, hint_rect)

    def _draw_game_over_screen(self) -> None:
        """繪製遊戲結束畫面"""
        # 半透明覆蓋層
        overlay = pygame.Surface((WINDOW_CONFIG["width"], WINDOW_CONFIG["height"]))
        overlay.set_alpha(200)
        overlay.fill((100, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # 遊戲結束文字
        game_over_text = self.ui.font.render("遊戲結束", True, COLORS["DANGER"])
        text_rect = game_over_text.get_rect(
            center=(WINDOW_CONFIG["width"] // 2, WINDOW_CONFIG["height"] // 2)
        )
        self.screen.blit(game_over_text, text_rect)

        # 統計資訊
        stats_text = f"存活天數: {self.time_manager.current_day}"
        stats_surface = self.ui.small_font.render(stats_text, True, COLORS["TEXT"])
        stats_rect = stats_surface.get_rect(
            center=(WINDOW_CONFIG["width"] // 2, WINDOW_CONFIG["height"] // 2 + 50)
        )
        self.screen.blit(stats_surface, stats_rect)

    def run(self) -> None:
        """運行遊戲主迴圈"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(WINDOW_CONFIG["fps"])

        pygame.quit()
        sys.exit()


# ====== 主程式進入點 ======


def main() -> None:
    """主程式函數"""
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"❌ 遊戲發生錯誤: {e}")
        pygame.quit()
        sys.exit(1)


if __name__ == "__main__":
    main()
