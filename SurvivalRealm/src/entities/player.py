"""
Survival Realm - 玩家角色系統
處理玩家角色的所有行為和狀態

作者: 硬漢貓咪開發團隊 🐱
日期: 2025-07-30
版本: 3.1.0 (重構版本)
"""

import pygame
import time
import math
import random
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
        self.is_sprinting = False  # 🔥 新增：衝刺狀態
        self.has_moved_this_turn = False  # 回合制移動標記
        self.previous_position = (x, y)  # 記錄上一次位置

        # 生存狀態管理
        self.survival_stats = SurvivalStats()

        # 物品欄系統
        self.inventory = Inventory(20)

        # 🐱 給玩家一些基礎資源開始遊戲 - 不然連工作台都做不了呢！
        self._add_starter_items()

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
        self.attack_range = PLAYER_CONFIG["attack_range"]
        self.last_attack = 0
        self.attack_cooldown = PLAYER_CONFIG["attack_cooldown"]

    def _add_starter_items(self) -> None:
        """
        給玩家一些基礎的起始資源

        讓玩家能夠開始遊戲體驗，不至於完全空手開始
        只給基礎材料，不給任何製作完成的物品
        """
        # 基礎資源 - 讓玩家能製作工作台和基礎工具
        wood_item = item_database.get_item("wood")
        stone_item = item_database.get_item("stone")

        if wood_item:
            self.inventory.add_item(
                wood_item, 10
            )  # 10個木材 - 足夠製作工作台和基礎工具

        if stone_item:
            self.inventory.add_item(stone_item, 8)  # 8個石頭 - 足夠製作基礎工具

        # 硬漢貓咪開發提醒：給玩家一些基礎食物，不然會餓死的！
        food_item = item_database.get_item("food")
        berry_item = item_database.get_item("berry")
        mushroom_item = item_database.get_item("mushroom")  # 🔥 新增蘑菇

        if food_item:
            self.inventory.add_item(food_item, 5)  # 5個基礎食物

        if berry_item:
            self.inventory.add_item(berry_item, 8)  # 8個漿果

        # 🔥 給玩家一些治療蘑菇用於測試衝刺和治療系統
        if mushroom_item:
            self.inventory.add_item(mushroom_item, 6)  # 6個蘑菇

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
        self.is_sprinting = False

        # 🔥 檢查衝刺條件（按住Shift且體力足夠）
        can_sprint = (
            keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        ) and self.survival_stats.energy >= PLAYER_CONFIG["sprint_threshold"]

        # 選擇移動速度
        current_speed = (
            PLAYER_CONFIG["sprint_speed"] if can_sprint else PLAYER_CONFIG["speed"]
        )

        # WASD 移動控制
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.velocity_y = -current_speed
            self.is_moving = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.velocity_y = current_speed
            self.is_moving = True
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velocity_x = -current_speed
            self.is_moving = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velocity_x = current_speed
            self.is_moving = True

        # 🔥 設定衝刺狀態
        if self.is_moving and can_sprint:
            self.is_sprinting = True

    def interact_with_world(self, world_manager: "WorldManager"):
        """
        與世界物件互動

        Args:
            world_manager: 世界管理器

        Returns:
            互動結果訊息或字典（洞穴入口的情況）
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

            # 檢查是否是洞穴入口互動
            if isinstance(result, dict) and result.get("cave_entry"):
                return result  # 返回完整的字典用於洞穴處理

            # 處理獲得的物品
            if isinstance(result, dict) and "items" in result:
                for item_id, quantity in result["items"]:
                    item = item_database.get_item(item_id)
                    if item:
                        added = self.inventory.add_item(item, quantity)
                        if added < quantity:
                            lost = quantity - added
                            return f"{result['message']} (物品欄已滿，丟失了{lost}個{item.name})"

            # 返回消息
            if isinstance(result, dict):
                return result["message"]
            else:
                return result

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

    def consume_food(self, food_type: str = None) -> bool:
        """
        消耗食物恢復飢餓值 - 智能搜尋可用食物

        Args:
            food_type (str): 指定食物類型（可選）

        Returns:
            bool: 是否成功消耗
        """
        # 定義所有可用的食物類型和恢復量
        food_types = {
            "food": 30,
            "berry": 15,
            "mushroom": 25,
            "fruit": 20,
            "health_potion": 0,  # 生命藥水不恢復飢餓但恢復血量
            "energy_potion": 0,  # 體力藥水不恢復飢餓但恢復體力
        }

        # 如果指定了食物類型，只嘗試該類型
        if food_type:
            if self.inventory.has_item(food_type, 1):
                removed = self.inventory.remove_item(food_type, 1)
                if removed > 0:
                    self._apply_food_effects(food_type)
                    return True
            return False

        # 智能搜尋：按優先順序嘗試消耗食物
        priority_order = [
            "food",
            "fruit",
            "mushroom",
            "berry",
            "health_potion",
            "energy_potion",
        ]

        for food_id in priority_order:
            if self.inventory.has_item(food_id, 1):
                removed = self.inventory.remove_item(food_id, 1)
                if removed > 0:
                    self._apply_food_effects(food_id)
                    return True

        return False

    def _apply_food_effects(self, food_type: str) -> None:
        """
        應用食物效果

        Args:
            food_type (str): 食物類型
        """
        # 恢復飢餓值的食物
        hunger_recovery = {"food": 30, "berry": 15, "mushroom": 25, "fruit": 20}

        if food_type in hunger_recovery:
            recovery_amount = hunger_recovery[food_type]
            self.survival_stats.hunger = min(
                100, self.survival_stats.hunger + recovery_amount
            )

        # 🔥 香菇特殊效果：既補血又補體力！
        if food_type == "mushroom":
            # 香菇額外恢復生命值和體力
            self.survival_stats.health = min(
                100, self.survival_stats.health + 20
            )  # 恢復20點血
            self.survival_stats.energy = min(
                100, self.survival_stats.energy + 30
            )  # 恢復30點體力
            print("香菇效果：恢復20點生命值和30點體力！")

        # 特殊效果食物
        if food_type == "health_potion":
            # 生命藥水恢復大量生命值
            self.survival_stats.health = min(100, self.survival_stats.health + 50)
        elif food_type == "energy_potion":
            # 體力藥水恢復大量體力
            self.survival_stats.energy = min(100, self.survival_stats.energy + 60)

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

    def attack(self, world_manager: "WorldManager") -> Optional[str]:
        """
        玩家攻擊動作

        Args:
            world_manager: 世界管理器

        Returns:
            Optional[str]: 攻擊結果訊息
        """
        current_time = time.time()

        # 檢查攻擊冷卻
        if current_time - self.last_attack < self.attack_cooldown:
            return None

        # 更新攻擊時間
        self.last_attack = current_time

        # 計算玩家中心點
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2

        # 獲取攻擊範圍內的物件
        nearby_objects = world_manager.get_nearby_objects(
            center_x, center_y, self.attack_range
        )

        # 導入音效管理器
        from ..systems.sound_manager import sound_manager

        # 檢查是否有鐵劍
        has_iron_sword = (
            self.equipped_weapon and self.equipped_weapon.id == "iron_sword"
        )

        # 播放攻擊音效
        if has_iron_sword:
            sound_manager.play_sword_whoosh_sound()
        else:
            sound_manager.play_attack_sound()

        # 找到攻擊目標
        targets = []
        for obj in nearby_objects:
            # 攻擊怪物
            if (
                hasattr(obj, "health")
                and hasattr(obj, "damage")
                and obj.__class__.__name__ in ["Monster", "CaveMonster"]
            ):
                targets.append(("monster", obj))
            # 攻擊樹木（如果有鐵劍或工具）
            elif obj.__class__.__name__ == "Tree" and (
                has_iron_sword or self.equipped_tool
            ):
                targets.append(("tree", obj))

        if not targets:
            return "揮空了！沒有攻擊到任何目標"

        # 計算攻擊傷害
        base_damage = PLAYER_CONFIG["base_attack_damage"]
        weapon_damage = 0

        if has_iron_sword:
            weapon_damage = 5  # 鐵劍額外傷害
        elif self.equipped_tool and self.equipped_tool.id in ["axe", "pickaxe"]:
            weapon_damage = 2  # 工具額外傷害

        total_damage = base_damage + weapon_damage

        results = []
        for target_type, target in targets:
            if target_type == "monster":
                # 攻擊怪物
                old_health = target.health
                target.health -= total_damage

                # 播放命中音效
                if has_iron_sword:
                    sound_manager.play_sword_hit_sound()
                else:
                    sound_manager.play_attack_sound()

                if target.health <= 0:
                    target.destroy()
                    results.append(f"擊敗了怪物！造成{total_damage}點傷害")

                    # 怪物死亡掉落物品
                    drop_items = [("food", 1), ("wood", random.randint(1, 2))]
                    for item_id, quantity in drop_items:
                        item = item_database.get_item(item_id)
                        if item:
                            self.inventory.add_item(item, quantity)
                else:
                    results.append(
                        f"攻擊怪物！造成{total_damage}點傷害 ({target.health}/{getattr(target, 'max_health', target.health)})"
                    )

            elif target_type == "tree":
                # 攻擊樹木
                efficiency = (
                    self.get_tool_efficiency("tree") if self.equipped_tool else 1.0
                )
                damage = int(total_damage * efficiency)

                old_health = target.health
                target.health -= damage

                # 播放砍樹音效
                sound_manager.play_tree_break_sound()

                if target.health <= 0:
                    target.destroy()
                    wood_amount = (
                        random.randint(3, 6) if efficiency > 1 else random.randint(2, 4)
                    )

                    # 添加木材到背包
                    wood_item = item_database.get_item("wood")
                    if wood_item:
                        self.inventory.add_item(wood_item, wood_amount)

                    weapon_name = (
                        "鐵劍"
                        if has_iron_sword
                        else (
                            "斧頭"
                            if self.equipped_tool and self.equipped_tool.id == "axe"
                            else "工具"
                        )
                    )
                    results.append(f"用{weapon_name}砍倒了樹！獲得木材 x{wood_amount}")
                else:
                    weapon_name = (
                        "鐵劍"
                        if has_iron_sword
                        else (
                            "斧頭"
                            if self.equipped_tool and self.equipped_tool.id == "axe"
                            else "工具"
                        )
                    )
                    results.append(
                        f"{weapon_name}砍伐中... ({target.health}/{target.max_health})"
                    )

        return " | ".join(results) if results else "攻擊未命中任何目標"

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

    def update(
        self, delta_time: float, window_width: int, window_height: int, cave_system=None
    ) -> None:
        """
        更新玩家狀態

        Args:
            delta_time (float): 幀時間差
            window_width (int): 視窗寬度（在相機系統中不用於邊界檢查）
            window_height (int): 視窗高度（在相機系統中不用於邊界檢查）
            cave_system: 洞穴系統實例，用於邊界檢查
        """
        # 記錄舊位置用於回合制檢測
        old_x, old_y = self.x, self.y

        # 🔥 衝刺體力消耗
        if self.is_sprinting:
            sprint_cost = PLAYER_CONFIG["sprint_energy_cost"] * delta_time
            self.survival_stats.energy = max(
                0, self.survival_stats.energy - sprint_cost
            )
        elif self.is_moving:
            # 普通移動消耗較少體力
            normal_move_cost = 5 * delta_time  # 每秒消耗5點體力
            self.survival_stats.energy = max(
                0, self.survival_stats.energy - normal_move_cost
            )

        # 更新位置
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time

        # 洞穴邊界檢查
        if cave_system and cave_system.in_cave and cave_system.current_room:
            from ..core.config import CAVE_CONFIG

            room_width = CAVE_CONFIG["room_size"]["width"]
            room_height = CAVE_CONFIG["room_size"]["height"]

            # 洞穴邊界限制 - 考慮玩家大小
            boundary_margin = 20  # 邊界緩衝區
            min_x = boundary_margin
            max_x = room_width - self.width - boundary_margin
            min_y = boundary_margin
            max_y = room_height - self.height - boundary_margin

            # 限制玩家在洞穴邊界內
            if self.x < min_x:
                self.x = min_x
                self.velocity_x = 0  # 停止向左移動
            elif self.x > max_x:
                self.x = max_x
                self.velocity_x = 0  # 停止向右移動

            if self.y < min_y:
                self.y = min_y
                self.velocity_y = 0  # 停止向上移動
            elif self.y > max_y:
                self.y = max_y
                self.velocity_y = 0  # 停止向下移動

            print(
                f"洞穴邊界檢查: 玩家位置 ({self.x:.1f}, {self.y:.1f}), 房間大小 {room_width}x{room_height}"
            )
        else:
            # 🔥 主世界無邊界！玩家可以無限探索
            # 不再有任何世界邊界限制，讓探索更自由
            pass  # 移除所有邊界檢查

        # 檢查是否真的移動了（回合制系統）
        moved_distance = math.sqrt((self.x - old_x) ** 2 + (self.y - old_y) ** 2)
        if moved_distance > 1.0:  # 移動超過1像素才算真正移動
            self.has_moved_this_turn = True

            # 🦶 播放腳步聲音效！硬漢貓咪也要有腳步聲呢～
            from ..systems.sound_manager import sound_manager

            # 衝刺時腳步聲更頻繁且音量更大
            if self.is_sprinting:
                # 衝刺時腳步聲間隔更短，音量更大
                sound_manager.footstep_interval = 0.25  # 衝刺時更快的腳步聲
                sound_manager.play_footstep()
            else:
                # 正常移動時使用預設間隔
                sound_manager.footstep_interval = PLAYER_CONFIG.get(
                    "footstep_interval", 0.4
                )
                sound_manager.play_footstep()
        else:
            self.has_moved_this_turn = False

        # 更新碰撞箱
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # 更新生存數值
        self.survival_stats.update(delta_time)

    def draw(
        self, screen: pygame.Surface, camera_x: int = None, camera_y: int = None
    ) -> None:
        """
        繪製玩家角色

        Args:
            screen: pygame螢幕物件
            camera_x: 相機X座標（如果提供，表示使用相機系統）
            camera_y: 相機Y座標（如果提供，表示使用相機系統）
        """
        # 根據生命值決定顏色
        if self.survival_stats.health > 60:
            player_color = COLORS["PRIMARY"]
        elif self.survival_stats.health > 30:
            player_color = COLORS["WARNING"]
        else:
            player_color = COLORS["DANGER"]

        # 🔥 衝刺狀態視覺效果：玩家發光！
        if self.is_sprinting:
            # 衝刺時使用亮黃色邊框
            sprint_glow_color = (255, 255, 0)  # 黃色發光
        else:
            sprint_glow_color = None

        # 如果使用相機系統，玩家固定在指定位置
        if camera_x is not None and camera_y is not None:
            # 玩家固定在相機指定位置（通常是螢幕中心）
            player_rect = pygame.Rect(
                camera_x - self.width // 2,
                camera_y - self.height // 2,
                self.width,
                self.height,
            )

            # 繪製玩家主體
            pygame.draw.rect(screen, player_color, player_rect)

            # 🔥 衝刺發光效果
            if sprint_glow_color:
                # 繪製衝刺光環
                glow_rect = pygame.Rect(
                    camera_x - self.width // 2 - 3,
                    camera_y - self.height // 2 - 3,
                    self.width + 6,
                    self.height + 6,
                )
                pygame.draw.rect(screen, sprint_glow_color, glow_rect, 3)  # 黃色邊框

            # 繪製眼睛表示方向
            eye_size = 4
            left_eye = (camera_x - self.width // 2 + 8, camera_y - self.height // 2 + 8)
            right_eye = (
                camera_x - self.width // 2 + 24,
                camera_y - self.height // 2 + 8,
            )
            pygame.draw.circle(screen, COLORS["TEXT"], left_eye, eye_size)
            pygame.draw.circle(screen, COLORS["TEXT"], right_eye, eye_size)

            # 繪製裝備指示器
            self._draw_equipment_indicators_with_camera(screen, camera_x, camera_y)
        else:
            # 傳統繪製方式（向後兼容）
            # 🔥 衝刺發光效果
            if sprint_glow_color:
                glow_rect = pygame.Rect(
                    self.x - 3, self.y - 3, self.width + 6, self.height + 6
                )
                pygame.draw.rect(screen, sprint_glow_color, glow_rect, 3)

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

    def _draw_equipment_indicators_with_camera(
        self, screen: pygame.Surface, camera_x: int, camera_y: int
    ) -> None:
        """使用相機座標繪製裝備指示器"""
        player_left = camera_x - self.width // 2
        player_top = camera_y - self.height // 2

        # 工具指示器
        if self.equipped_tool:
            tool_color = COLORS["INFO"]
            pygame.draw.circle(
                screen, tool_color, (player_left + self.width - 8, player_top + 8), 3
            )

        # 武器指示器
        if self.equipped_weapon:
            weapon_color = COLORS["DANGER"]
            pygame.draw.circle(
                screen,
                weapon_color,
                (player_left + 8, player_top + self.height - 8),
                3,
            )

        # 護甲指示器
        if self.equipped_armor:
            armor_color = COLORS["WARNING"]
            pygame.draw.circle(
                screen,
                armor_color,
                (player_left + self.width - 8, player_top + self.height - 8),
                3,
            )

    def get_world_center(self) -> tuple:
        """
        獲取玩家在世界中的中心座標

        Returns:
            tuple: (center_x, center_y) 玩家世界中心座標
        """
        return (self.x + self.width // 2, self.y + self.height // 2)

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
