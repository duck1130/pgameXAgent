"""
🎮 Survival Realm - 世界管理系統
管理遊戲世界中的所有物件生成、更新和銷毀

作者: 硬漢貓咪開發團隊 🐱
日期: 2025-07-30
版本: 3.1.0 (重構版本)
"""

import pygame
import random
import math
from typing import List, TYPE_CHECKING

from .game_object import GameObject
from .world_objects import (
    Tree,
    Rock,
    Food,
    River,
    Chest,
    Cave,
    Monster,
    Workbench,
    Furnace,
)
from ..core.config import WORLD_OBJECTS, WORLD_CONFIG, WINDOW_CONFIG

# 避免循環引用
if TYPE_CHECKING:
    pass


class WorldManager:
    """世界物件管理系統"""

    def __init__(self) -> None:
        """初始化世界管理器"""
        self.objects: List[GameObject] = []
        self.spawn_timer = 0
        self.spawn_interval = WORLD_CONFIG["spawn_interval"]

        print("🌍 世界管理器初始化完成")

    def generate_world(self) -> None:
        """生成初始世界物件"""
        print("🎲 開始生成世界物件...")

        num_objects = WORLD_CONFIG["initial_objects"]
        safe_zone_radius = WORLD_CONFIG["safe_zone_radius"]

        # 計算玩家起始位置（螢幕中央）
        player_start_x = WINDOW_CONFIG["width"] // 2
        player_start_y = WINDOW_CONFIG["height"] // 2

        objects_created = 0
        attempts = 0
        max_attempts = num_objects * 3  # 防止無限循環

        while objects_created < num_objects and attempts < max_attempts:
            x = random.randint(50, WINDOW_CONFIG["width"] - 50)
            y = random.randint(50, WINDOW_CONFIG["height"] - 50)

            # 檢查是否在玩家安全區域內
            distance_to_player = math.sqrt(
                (x - player_start_x) ** 2 + (y - player_start_y) ** 2
            )

            if distance_to_player < safe_zone_radius:
                attempts += 1
                continue

            # 檢查是否與現有物件重疊
            if self._check_position_clear(x, y, 40):
                # 根據機率生成不同物件
                obj_type = self._choose_object_type()
                if obj_type:
                    self._spawn_object(obj_type, x, y)
                    objects_created += 1

            attempts += 1

        print(f"✅ 生成了 {objects_created} 個世界物件")

    def _check_position_clear(self, x: float, y: float, min_distance: float) -> bool:
        """檢查位置是否有足夠空間"""
        for obj in self.objects:
            if obj.active:
                distance = math.sqrt((obj.x - x) ** 2 + (obj.y - y) ** 2)
                if distance < min_distance:
                    return False
        return True

    def _choose_object_type(self) -> str:
        """根據生成機率選擇物件類型"""
        rand = random.random()
        cumulative = 0

        for obj_type, config in WORLD_OBJECTS.items():
            cumulative += config["spawn_rate"]
            if rand <= cumulative:
                return obj_type

        # 備用：如果沒有選中任何類型，返回樹木
        return "tree"

    def _spawn_object(self, obj_type: str, x: float, y: float) -> None:
        """在指定位置生成物件"""
        if obj_type == "tree":
            self.objects.append(Tree(x, y))
        elif obj_type == "rock":
            self.objects.append(Rock(x, y))
        elif obj_type == "food":
            self.objects.append(Food(x, y))
        elif obj_type == "river":
            self.objects.append(River(x, y))
        elif obj_type == "chest":
            self.objects.append(Chest(x, y))
        elif obj_type == "cave":
            self.objects.append(Cave(x, y))
        elif obj_type == "monster":
            self.objects.append(Monster(x, y))
        elif obj_type == "workbench":
            self.objects.append(Workbench(x, y))
        elif obj_type == "furnace":
            self.objects.append(Furnace(x, y))

    def update(self, delta_time: float) -> None:
        """
        更新世界物件

        Args:
            delta_time (float): 幀時間差
        """
        self.spawn_timer += delta_time

        # 定期生成新物件
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self._spawn_random_object()

        # 移除已摧毀的物件
        self.objects = [obj for obj in self.objects if obj.active]

    def _spawn_random_object(self) -> None:
        """隨機生成新物件"""
        max_objects = WORLD_CONFIG["max_objects"]
        safe_zone_radius = WORLD_CONFIG["safe_zone_radius"]

        # 限制總物件數量
        if len(self.objects) >= max_objects:
            return

        # 嘗試找到合適的生成位置
        for _ in range(10):  # 最多嘗試10次
            x = random.randint(50, WINDOW_CONFIG["width"] - 50)
            y = random.randint(50, WINDOW_CONFIG["height"] - 50)

            # 避免在螢幕中央（玩家常在的區域）生成
            center_x = WINDOW_CONFIG["width"] // 2
            center_y = WINDOW_CONFIG["height"] // 2

            if math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2) < safe_zone_radius:
                continue

            # 檢查位置是否清空
            if not self._check_position_clear(x, y, 30):
                continue

            # 生成非危險物件（排除怪物）
            safe_objects = ["tree", "rock", "food", "river"]

            # 偶爾生成特殊物件
            if random.random() < 0.1:  # 10% 機率
                safe_objects.extend(["chest", "cave"])

            obj_type = random.choice(safe_objects)
            self._spawn_object(obj_type, x, y)
            break

    def get_nearby_objects(self, x: float, y: float, radius: float) -> List[GameObject]:
        """
        獲取指定範圍內的物件

        Args:
            x, y (float): 中心座標
            radius (float): 搜尋半徑

        Returns:
            List[GameObject]: 範圍內的物件列表
        """
        nearby = []
        for obj in self.objects:
            if obj.active and obj.is_near(x, y, radius):
                nearby.append(obj)
        return nearby

    def get_objects_by_type(self, obj_type: type) -> List[GameObject]:
        """
        獲取指定類型的所有物件

        Args:
            obj_type (type): 物件類型

        Returns:
            List[GameObject]: 指定類型的物件列表
        """
        return [obj for obj in self.objects if isinstance(obj, obj_type) and obj.active]

    def clear_area(self, x: float, y: float, radius: float) -> int:
        """
        清空指定區域的所有物件

        Args:
            x, y (float): 中心座標
            radius (float): 清空半徑

        Returns:
            int: 清除的物件數量
        """
        cleared_count = 0
        for obj in self.objects:
            if obj.active and obj.is_near(x, y, radius):
                obj.destroy()
                cleared_count += 1
        return cleared_count

    def add_object(self, game_object: GameObject) -> None:
        """
        添加新物件到世界

        Args:
            game_object (GameObject): 要添加的物件
        """
        self.objects.append(game_object)

    def remove_object(self, game_object: GameObject) -> bool:
        """
        從世界移除物件

        Args:
            game_object (GameObject): 要移除的物件

        Returns:
            bool: 是否成功移除
        """
        if game_object in self.objects:
            self.objects.remove(game_object)
            return True
        return False

    def get_object_count(self) -> int:
        """獲取活躍物件總數"""
        return len([obj for obj in self.objects if obj.active])

    def get_object_stats(self) -> dict:
        """獲取物件統計信息"""
        stats = {}

        for obj in self.objects:
            if obj.active:
                obj_type = type(obj).__name__
                stats[obj_type] = stats.get(obj_type, 0) + 1

        return stats

    def draw(self, screen: pygame.Surface) -> None:
        """
        繪製所有世界物件

        Args:
            screen: pygame螢幕物件
        """
        # 按照深度排序繪製（遠的先畫，近的後畫）
        active_objects = [obj for obj in self.objects if obj.active]
        active_objects.sort(key=lambda obj: obj.y)  # 按Y座標排序

        for obj in active_objects:
            obj.draw(screen)

    def cleanup(self) -> None:
        """清理資源"""
        self.objects.clear()
        print("🧹 世界管理器已清理")
