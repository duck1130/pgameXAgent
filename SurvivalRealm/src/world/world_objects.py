"""
🎮 Survival Realm - 世界物件實作
具體的世界物件類別實作

作者: 硬漢貓咪開發團隊 🐱
日期: 2025-07-30
版本: 3.1.0 (重構版本)
"""

import pygame
import random
import time
from typing import Optional, Dict, List, Tuple, TYPE_CHECKING

from .game_object import GameObject
from ..core.config import WORLD_OBJECTS, MINING_CHANCES, COLORS

# 避免循環引用
if TYPE_CHECKING:
    from ..entities.player import Player


class Tree(GameObject):
    """樹木物件 - 可砍伐獲得木材"""

    def __init__(self, x: float, y: float):
        size = WORLD_OBJECTS["tree"]["size"]
        super().__init__(x, y, size[0], size[1])
        self.health = WORLD_OBJECTS["tree"]["health"]
        self.max_health = self.health

    def draw(self, screen: pygame.Surface) -> None:
        """繪製樹木"""
        if not self.active:
            return

        # 樹幹
        trunk_rect = pygame.Rect(self.x + 15, self.y + 40, 10, 20)
        pygame.draw.rect(screen, (101, 67, 33), trunk_rect)

        # 樹冠
        crown_rect = pygame.Rect(self.x, self.y, 40, 40)
        color = WORLD_OBJECTS["tree"]["color"]
        pygame.draw.ellipse(screen, color, crown_rect)

        # 生命值條（如果受損）
        if self.health < self.max_health:
            self._draw_health_bar(screen)

    def _draw_health_bar(self, screen: pygame.Surface) -> None:
        """繪製生命值條"""
        bar_width = 30
        bar_height = 4
        bg_rect = pygame.Rect(self.x + 5, self.y - 10, bar_width, bar_height)
        pygame.draw.rect(screen, (100, 100, 100), bg_rect)

        health_width = int((self.health / self.max_health) * bar_width)
        health_rect = pygame.Rect(self.x + 5, self.y - 10, health_width, bar_height)
        pygame.draw.rect(screen, COLORS["SUCCESS"], health_rect)

    def interact(self, player: "Player") -> Optional[Dict]:
        """砍伐樹木"""
        if not self.active:
            return None

        # 根據工具效率計算傷害
        efficiency = player.get_tool_efficiency("tree")
        damage = int(efficiency)

        self.health -= damage
        if self.health <= 0:
            self.destroy()
            # 根據工具效率決定木材掉落量
            wood_amount = (
                random.randint(3, 6) if efficiency > 1 else random.randint(2, 4)
            )
            tool_name = "斧頭" if efficiency > 1 else "徒手"
            return {
                "message": f"用{tool_name}砍倒了樹！獲得木材 x{wood_amount}",
                "items": [("wood", wood_amount)],
            }

        tool_name = "斧頭" if efficiency > 1 else "徒手"
        return {"message": f"{tool_name}砍伐中... ({self.health}/{self.max_health})"}


class Rock(GameObject):
    """石頭物件 - 可挖掘獲得石頭和礦物"""

    def __init__(self, x: float, y: float):
        size = WORLD_OBJECTS["rock"]["size"]
        super().__init__(x, y, size[0], size[1])
        self.health = WORLD_OBJECTS["rock"]["health"]
        self.max_health = self.health

    def draw(self, screen: pygame.Surface) -> None:
        """繪製石頭"""
        if not self.active:
            return

        color = WORLD_OBJECTS["rock"]["color"]
        pygame.draw.ellipse(screen, color, self.rect)
        # 添加紋理
        pygame.draw.ellipse(screen, (169, 169, 169), self.rect, 3)

        # 生命值條（如果受損）
        if self.health < self.max_health:
            self._draw_health_bar(screen)

    def _draw_health_bar(self, screen: pygame.Surface) -> None:
        """繪製生命值條"""
        bar_width = 25
        bar_height = 4
        bg_rect = pygame.Rect(self.x + 2, self.y - 8, bar_width, bar_height)
        pygame.draw.rect(screen, (100, 100, 100), bg_rect)

        health_width = int((self.health / self.max_health) * bar_width)
        health_rect = pygame.Rect(self.x + 2, self.y - 8, health_width, bar_height)
        pygame.draw.rect(screen, COLORS["WARNING"], health_rect)

    def interact(self, player: "Player") -> Optional[Dict]:
        """挖掘石頭"""
        if not self.active:
            return None

        efficiency = player.get_tool_efficiency("rock")
        damage = int(efficiency)

        self.health -= damage
        if self.health <= 0:
            self.destroy()

            items = []
            # 基本石頭掉落
            stone_amount = (
                random.randint(2, 4) if efficiency > 1 else random.randint(1, 3)
            )
            items.append(("stone", stone_amount))

            # 使用稿子有機率獲得礦物
            if efficiency > 1:
                for ore_type, chance in MINING_CHANCES.items():
                    if random.random() < chance:
                        items.append((ore_type, 1))

            tool_name = "稿子" if efficiency > 1 else "徒手"
            message = f"用{tool_name}挖掘了石頭！"
            if len(items) > 1:
                message += " 發現了礦物！"

            return {"message": message, "items": items}

        tool_name = "稿子" if efficiency > 1 else "徒手"
        return {"message": f"{tool_name}挖掘中... ({self.health}/{self.max_health})"}


class Food(GameObject):
    """食物物件 - 可收集的食物"""

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

        self.destroy()
        food_names = {"berry": "漿果", "mushroom": "蘑菇", "fruit": "水果"}

        food_name = food_names.get(self.food_type, "食物")
        return {"message": f"收集了{food_name}！", "items": [(self.food_type, 1)]}


class River(GameObject):
    """河流物件 - 可取水"""

    def __init__(self, x: float, y: float):
        size = WORLD_OBJECTS["river"]["size"]
        super().__init__(x, y, size[0], size[1])

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
        has_bucket = player.inventory.has_item("bucket", 1)

        player.drink_water(has_bucket)

        # 喝過後河流消失
        self.destroy()

        if has_bucket:
            return {"message": "用木桶裝了河水並喝下，大幅恢復口渴值！河流乾涸了..."}
        else:
            return {"message": "用手喝了河水，稍微恢復口渴值，河流乾涸了..."}


class Chest(GameObject):
    """寶箱物件 - 包含隨機戰利品"""

    def __init__(self, x: float, y: float):
        size = WORLD_OBJECTS["chest"]["size"]
        super().__init__(x, y, size[0], size[1])
        self.opened = False
        self.loot = self._generate_loot()

    def _generate_loot(self) -> List[Tuple[str, int]]:
        """生成寶箱戰利品"""
        loot = []

        # 食物 (高機率)
        if random.random() < 0.7:
            food_types = ["food", "berry", "mushroom"]
            food_type = random.choice(food_types)
            loot.append((food_type, random.randint(2, 5)))

        # 工具 (中等機率)
        if random.random() < 0.3:
            tool_type = random.choice(["axe", "pickaxe", "bucket"])
            loot.append((tool_type, 1))

        # 稀有物品 (低機率)
        if random.random() < 0.15:
            rare_items = ["iron_sword", "iron_armor", "treasure"]
            rare_item = random.choice(rare_items)
            loot.append((rare_item, 1))

        # 礦物資源 (中等機率)
        if random.random() < 0.4:
            mineral_type = random.choice(["iron_ore", "coal"])
            loot.append((mineral_type, random.randint(1, 3)))

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
        if self.loot:
            return {"message": "打開了寶箱！發現了寶物", "items": self.loot}
        else:
            return {"message": "打開了寶箱，但裡面是空的..."}


class Cave(GameObject):
    """洞窟物件 - 可探索獲得資源"""

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

            # 隨機獲得資源
            loot = []

            # 基本資源
            loot.append(("stone", random.randint(3, 8)))

            # 有機率獲得礦物
            if random.random() < 0.5:
                loot.append(("iron_ore", random.randint(1, 3)))

            if random.random() < 0.3:
                loot.append(("coal", random.randint(1, 2)))

            # 稀有寶物
            if random.random() < 0.2:
                loot.append(("treasure", 1))

            return {"message": "探索了洞窟，發現了豐富的資源！", "items": loot}

        return {"message": "這個洞窟已經探索過了"}


class Workbench(GameObject):
    """工作台物件 - 用於製作工具"""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, 60, 40)
        self.crafting_enabled = True

    def draw(self, screen: pygame.Surface) -> None:
        """繪製工作台"""
        if not self.active:
            return

        # 工作台主體
        pygame.draw.rect(screen, (139, 69, 19), self.rect)  # 棕色
        pygame.draw.rect(screen, (101, 67, 33), self.rect, 3)  # 深棕色邊框

        # 工作檯面
        top_rect = pygame.Rect(self.x, self.y, self.width, 10)
        pygame.draw.rect(screen, (160, 82, 45), top_rect)

        # 工具標記
        pygame.draw.circle(
            screen, (255, 255, 255), (int(self.x + 15), int(self.y + 20)), 3
        )
        pygame.draw.circle(
            screen, (255, 255, 255), (int(self.x + 45), int(self.y + 20)), 3
        )

    def interact(self, player: "Player") -> Optional[Dict]:
        """使用工作台"""
        if not self.active:
            return None

        return {"message": "接近工作台！按 C 鍵開始製作"}


class Furnace(GameObject):
    """熔爐物件 - 用於燒製物品"""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, 50, 60)
        self.smelting_enabled = True
        self.is_lit = False

    def draw(self, screen: pygame.Surface) -> None:
        """繪製熔爐"""
        if not self.active:
            return

        # 熔爐主體
        main_color = (105, 105, 105) if not self.is_lit else (139, 69, 19)
        pygame.draw.rect(screen, main_color, self.rect)
        pygame.draw.rect(screen, (64, 64, 64), self.rect, 3)

        # 熔爐門
        door_rect = pygame.Rect(self.x + 10, self.y + 30, 30, 25)
        door_color = (64, 64, 64) if not self.is_lit else (255, 69, 0)
        pygame.draw.rect(screen, door_color, door_rect)

        # 煙囪
        chimney_rect = pygame.Rect(self.x + 35, self.y - 10, 10, 20)
        pygame.draw.rect(screen, (64, 64, 64), chimney_rect)

        # 火焰效果（如果點燃）
        if self.is_lit:
            flame_points = [
                (self.x + 15, self.y + 40),
                (self.x + 20, self.y + 30),
                (self.x + 25, self.y + 35),
                (self.x + 30, self.y + 25),
                (self.x + 35, self.y + 40),
            ]
            pygame.draw.polygon(screen, (255, 140, 0), flame_points)

    def interact(self, player: "Player") -> Optional[Dict]:
        """使用熔爐"""
        if not self.active:
            return None

        return {"message": "接近熔爐！按 S 鍵開始燒製"}


class Monster(GameObject):
    """怪物物件 - 敵對生物"""

    def __init__(self, x: float, y: float):
        size = WORLD_OBJECTS["monster"]["size"]
        super().__init__(x, y, size[0], size[1])

        self.health = WORLD_OBJECTS["monster"]["health"]
        self.max_health = self.health
        self.damage = WORLD_OBJECTS["monster"]["damage"]
        self.last_attack = 0
        self.attack_cooldown = WORLD_OBJECTS["monster"]["attack_cooldown"]

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
            self._draw_health_bar(screen)

    def _draw_health_bar(self, screen: pygame.Surface) -> None:
        """繪製生命值條"""
        bar_width = 30
        bar_height = 4
        bg_rect = pygame.Rect(self.x, self.y - 10, bar_width, bar_height)
        pygame.draw.rect(screen, (100, 100, 100), bg_rect)

        health_width = int((self.health / self.max_health) * bar_width)
        health_rect = pygame.Rect(self.x, self.y - 10, health_width, bar_height)
        pygame.draw.rect(screen, COLORS["HEALTH"], health_rect)

    def interact(self, player: "Player") -> Optional[Dict]:
        """戰鬥系統"""
        if not self.active:
            return None

        current_time = time.time()

        # 玩家攻擊怪物
        damage_to_monster = player.attack_damage
        self.health -= damage_to_monster

        if self.health <= 0:
            self.destroy()

            # 隨機掉落物品
            drops = []
            if random.random() < 0.6:
                drops.append(("food", random.randint(1, 3)))
            if random.random() < 0.3:
                drops.append(("treasure", 1))
            if random.random() < 0.2:
                mineral = random.choice(["iron_ore", "coal"])
                drops.append((mineral, 1))

            return {
                "message": f"擊敗了怪物！造成{damage_to_monster}點傷害",
                "items": drops,
            }

        # 怪物反擊
        if current_time - self.last_attack >= self.attack_cooldown:
            self.last_attack = current_time
            actual_damage = player.take_damage(self.damage)
            return {
                "message": f"與怪物戰鬥！你對怪物造成{damage_to_monster}傷害，怪物對你造成{actual_damage}傷害",
                "monster_attack": True,
            }

        return {"message": f"戰鬥中... 怪物生命值: {self.health}/{self.max_health}"}
