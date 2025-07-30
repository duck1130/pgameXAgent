"""
🎮 Survival Realm - 玩家角色系統
處理玩家角色的所有行為和狀態

作者: 硬漢貓咪開發團隊 🐱
日期: 2025-07-30
版本: 3.1.0 (重構版本)
"""

import pygame
import time
import math
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from ..core.config import PLAYER_CONFIG, SURVIVAL_STATS, TOOL_EFFICIENCY, COLORS
from ..systems.inventory import Inventory, Item, ItemType, item_database

# 避免循環引用
if TYPE_CHECKING:
    from ..world.world_manager import WorldManager


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
        # 根據配置文件設定的衰減速率更新數值
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

        # 當飢餓和口渴度充足時，恢復生命值
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

    def is_critical(self) -> bool:
        """檢查是否處於危險狀態"""
        return (
            self.health <= 20
            or self.hunger <= 10
            or self.thirst <= 10
            or self.sanity <= 20
        )

    def get_status_effects(self) -> list:
        """獲取當前狀態效果"""
        effects = []

        if self.hunger <= 0:
            effects.append("飢餓")
        if self.thirst <= 0:
            effects.append("脫水")
        if self.energy <= 10:
            effects.append("疲憊")
        if self.sanity <= 20:
            effects.append("精神不穩")

        return effects


class Player:
    """玩家角色類 - 處理玩家的所有行為和狀態"""

    def __init__(self, x: float, y: float) -> None:
        """
        初始化玩家角色

        Args:
            x (float): 初始X座標
            y (float): 初始Y座標
        """
        # 位置和移動
        self.x = x
        self.y = y
        self.width = PLAYER_CONFIG["size"][0]
        self.height = PLAYER_CONFIG["size"][1]
        self.speed = PLAYER_CONFIG["speed"]
        self.rect = pygame.Rect(x, y, self.width, self.height)

        # 移動狀態
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_moving = False

        # 生存狀態管理
        self.survival_stats = SurvivalStats()

        # 物品欄系統
        self.inventory = Inventory(20)

        # 互動設定
        self.interaction_range = PLAYER_CONFIG["interaction_range"]
        self.last_interaction = 0
        self.interaction_cooldown = PLAYER_CONFIG["interaction_cooldown"]

        # 裝備系統
        self.equipped_tool: Optional[Item] = None
        self.equipped_weapon: Optional[Item] = None
        self.equipped_armor: Optional[Item] = None

        # 遊戲模式狀態
        self.crafting_mode = False
        self.smelting_mode = False

        # 戰鬥相關
        self.attack_damage = 1  # 基礎攻擊力
        self.defense = 0  # 防禦力

    def get_tool_efficiency(self, target_type: str) -> float:
        """
        獲取當前工具對特定目標的效率

        Args:
            target_type (str): 目標類型 ("tree", "rock", 等)

        Returns:
            float: 效率倍數
        """
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
        """
        裝備物品

        Args:
            item_id (str): 物品ID

        Returns:
            bool: 是否成功裝備
        """
        if not self.inventory.has_item(item_id, 1):
            return False

        item = item_database.get_item(item_id)
        if not item:
            return False

        # 根據物品類型進行裝備
        if item.item_type == ItemType.TOOL:
            self.equipped_tool = item
        elif item.item_type == ItemType.EQUIPMENT:
            if "sword" in item_id:
                self.equipped_weapon = item
                self.attack_damage = 3  # 武器增加攻擊力
            elif "armor" in item_id:
                self.equipped_armor = item
                self.defense = 2  # 護甲增加防禦力

        return True

    def unequip_item(self, slot_type: str) -> bool:
        """
        卸下裝備

        Args:
            slot_type (str): 裝備槽類型 ("tool", "weapon", "armor")

        Returns:
            bool: 是否成功卸下
        """
        if slot_type == "tool":
            self.equipped_tool = None
        elif slot_type == "weapon":
            self.equipped_weapon = None
            self.attack_damage = 1  # 恢復基礎攻擊力
        elif slot_type == "armor":
            self.equipped_armor = None
            self.defense = 0  # 恢復基礎防禦力
        else:
            return False

        return True

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        """
        處理玩家輸入

        Args:
            keys: pygame按鍵狀態
        """
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_moving = False

        # WASD 移動控制
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.velocity_y = -self.speed
            self.is_moving = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.velocity_y = self.speed
            self.is_moving = True
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velocity_x = -self.speed
            self.is_moving = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velocity_x = self.speed
            self.is_moving = True

        # 移動時消耗體力
        if self.is_moving and self.survival_stats.energy > 0:
            self.survival_stats.energy = max(0, self.survival_stats.energy - 0.1)

    def interact_with_world(self, world_manager: "WorldManager") -> Optional[str]:
        """
        與世界物件互動

        Args:
            world_manager: 世界管理器

        Returns:
            Optional[str]: 互動結果訊息
        """
        current_time = time.time()
        if current_time - self.last_interaction < self.interaction_cooldown:
            return None

        # 獲取附近物件
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        nearby_objects = world_manager.get_nearby_objects(
            center_x, center_y, self.interaction_range
        )

        if not nearby_objects:
            return "附近沒有可互動的物件"

        # 找到最近的物件
        closest_obj = min(
            nearby_objects,
            key=lambda obj: math.sqrt(
                (obj.x - center_x) ** 2 + (obj.y - center_y) ** 2
            ),
        )

        # 執行互動
        result = closest_obj.interact(self)
        if result:
            self.last_interaction = current_time

            # 處理獲得的物品
            if "items" in result:
                for item_id, quantity in result["items"]:
                    item = item_database.get_item(item_id)
                    if item:
                        added = self.inventory.add_item(item, quantity)
                        if added < quantity:
                            lost = quantity - added
                            return f"{result['message']} (物品欄已滿，丟失了{lost}個{item.name})"

            return result["message"]

        return None

    def place_building(
        self, building_id: str, world_manager: "WorldManager"
    ) -> Optional[str]:
        """
        放置建築物

        Args:
            building_id (str): 建築物ID
            world_manager: 世界管理器

        Returns:
            Optional[str]: 放置結果訊息
        """
        if not self.inventory.has_item(building_id, 1):
            return f"沒有{building_id}可以放置"

        # 檢查放置位置是否有足夠空間
        place_x = self.x + self.width + 20  # 在玩家右側放置
        place_y = self.y

        # 檢查位置是否被占用
        nearby_objects = world_manager.get_nearby_objects(place_x, place_y, 40)
        if nearby_objects:
            return "此位置已被占用，無法放置"

        # 消耗物品
        self.inventory.remove_item(building_id, 1)

        # 放置建築物
        if building_id == "workbench":
            from ..world.world_objects import Workbench

            workbench = Workbench(place_x, place_y)
            world_manager.add_object(workbench)
            return "成功放置工作台！"
        elif building_id == "furnace":
            from ..world.world_objects import Furnace

            furnace = Furnace(place_x, place_y)
            world_manager.add_object(furnace)
            return "成功放置熔爐！"

        return "無法放置此物品"

    def consume_food(self, food_type: str = "food") -> bool:
        """
        消耗食物恢復飢餓值

        Args:
            food_type (str): 食物類型

        Returns:
            bool: 是否成功消耗
        """
        if not self.inventory.has_item(food_type, 1):
            return False

        removed = self.inventory.remove_item(food_type, 1)
        if removed > 0:
            # 根據食物類型給予不同的恢復量
            recovery_amount = {"food": 30, "berry": 15, "mushroom": 25}.get(
                food_type, 20
            )

            self.survival_stats.hunger = min(
                100, self.survival_stats.hunger + recovery_amount
            )
            return True

        return False

    def drink_water(self, has_bucket: bool = False) -> None:
        """
        喝水恢復口渴值

        Args:
            has_bucket (bool): 是否使用木桶
        """
        recovery_amount = 50 if has_bucket else 20
        self.survival_stats.thirst = min(
            100, self.survival_stats.thirst + recovery_amount
        )

    def take_damage(self, damage: int) -> int:
        """
        承受傷害

        Args:
            damage (int): 傷害值

        Returns:
            int: 實際受到的傷害
        """
        # 計算防禦減免
        actual_damage = max(1, damage - self.defense)
        self.survival_stats.health = max(0, self.survival_stats.health - actual_damage)
        return actual_damage

    def is_alive(self) -> bool:
        """檢查玩家是否存活"""
        return self.survival_stats.health > 0

    def update(self, delta_time: float, window_width: int, window_height: int) -> None:
        """
        更新玩家狀態

        Args:
            delta_time (float): 幀時間差
            window_width (int): 視窗寬度
            window_height (int): 視窗高度
        """
        # 更新位置
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time

        # 螢幕邊界檢查
        self.x = max(0, min(window_width - self.width, self.x))
        self.y = max(0, min(window_height - self.height, self.y))

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
        # 根據生命值決定顏色
        if self.survival_stats.health > 60:
            player_color = COLORS["PRIMARY"]
        elif self.survival_stats.health > 30:
            player_color = COLORS["WARNING"]
        else:
            player_color = COLORS["DANGER"]

        # 繪製玩家主體
        pygame.draw.rect(screen, player_color, self.rect)

        # 繪製眼睛表示方向
        eye_size = 4
        left_eye = (int(self.x + 8), int(self.y + 8))
        right_eye = (int(self.x + 24), int(self.y + 8))
        pygame.draw.circle(screen, COLORS["TEXT"], left_eye, eye_size)
        pygame.draw.circle(screen, COLORS["TEXT"], right_eye, eye_size)

        # 繪製裝備指示器
        self._draw_equipment_indicators(screen)

    def _draw_equipment_indicators(self, screen: pygame.Surface) -> None:
        """繪製裝備指示器"""
        # 工具指示器
        if self.equipped_tool:
            tool_color = COLORS["INFO"]
            pygame.draw.circle(
                screen, tool_color, (int(self.x + self.width - 8), int(self.y + 8)), 3
            )

        # 武器指示器
        if self.equipped_weapon:
            weapon_color = COLORS["DANGER"]
            pygame.draw.circle(
                screen,
                weapon_color,
                (int(self.x + 8), int(self.y + self.height - 8)),
                3,
            )

        # 護甲指示器
        if self.equipped_armor:
            armor_color = COLORS["WARNING"]
            pygame.draw.circle(
                screen,
                armor_color,
                (int(self.x + self.width - 8), int(self.y + self.height - 8)),
                3,
            )

    def get_status_text(self) -> str:
        """獲取狀態文字描述"""
        status_parts = []

        # 裝備狀態
        if self.equipped_tool:
            status_parts.append(f"工具: {self.equipped_tool.name}")
        if self.equipped_weapon:
            status_parts.append(f"武器: {self.equipped_weapon.name}")
        if self.equipped_armor:
            status_parts.append(f"護甲: {self.equipped_armor.name}")

        # 狀態效果
        effects = self.survival_stats.get_status_effects()
        if effects:
            status_parts.append(f"狀態: {', '.join(effects)}")

        return " | ".join(status_parts) if status_parts else "正常"
