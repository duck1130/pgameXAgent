"""
Survival Realm - 世界管理系統
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
from ..core.config import WORLD_CONFIG

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
        self.river_count = 0  # 追蹤河流數量
        self.permanent_objects_generated = False  # 是否已生成永久物件

        print("世界: 世界管理器初始化完成")

    def generate_world(self) -> None:
        """生成初始世界物件"""
        print("開始: 開始生成世界物件...")

        num_objects = WORLD_CONFIG["initial_objects"]
        safe_zone_radius = WORLD_CONFIG["safe_zone_radius"]

        # 在相機系統中，玩家從世界中心開始
        player_start_x = 0  # 世界中心
        player_start_y = 0  # 世界中心

        objects_created = 0
        attempts = 0
        max_attempts = num_objects * 3  # 防止無限循環

        # 世界生成範圍（相機系統下需要更大的範圍）
        world_range = 2000  # 在玩家周圍 2000 像素範圍內生成物件

        # 首先生成永久物件（河流）
        if not self.permanent_objects_generated:
            self._generate_permanent_objects(
                player_start_x, player_start_y, safe_zone_radius, world_range
            )
            self.permanent_objects_generated = True

        while objects_created < num_objects and attempts < max_attempts:
            x = random.randint(-world_range, world_range)
            y = random.randint(-world_range, world_range)

            # 檢查是否在玩家安全區域內
            distance_to_player = math.sqrt(
                (x - player_start_x) ** 2 + (y - player_start_y) ** 2
            )

            if distance_to_player < safe_zone_radius:
                attempts += 1
                continue

            # 檢查是否與現有物件重疊
            if self._check_position_clear(x, y, 40):
                # 根據機率生成不同物件（排除永久物件）
                obj_type = self._choose_object_type(exclude_permanent=True)
                if obj_type:
                    self._spawn_object(obj_type, x, y)
                    objects_created += 1

            attempts += 1

        print(
            f"成功: 生成了 {objects_created} 個世界物件（包含 {self.river_count} 條河流）"
        )

    def _generate_permanent_objects(
        self,
        player_x: float,
        player_y: float,
        safe_zone_radius: float,
        world_range: int,
    ) -> None:
        """生成永久物件（如河流）"""
        max_rivers = WORLD_CONFIG["river_spawn_limit"]

        for _ in range(max_rivers):
            attempts = 0
            while attempts < 20:  # 限制嘗試次數
                x = random.randint(-world_range + 150, world_range - 150)
                y = random.randint(-world_range + 100, world_range - 100)

                # 確保不在玩家安全區域
                distance_to_player = math.sqrt(
                    (x - player_x) ** 2 + (y - player_y) ** 2
                )
                if distance_to_player > safe_zone_radius * 1.5:
                    if self._check_position_clear(x, y, 120):  # 河流需要更大空間
                        self._spawn_object("river", x, y)
                        self.river_count += 1
                        break
                attempts += 1

    def _check_position_clear(self, x: float, y: float, min_distance: float) -> bool:
        """檢查位置是否有足夠空間"""
        for obj in self.objects:
            if obj.active:
                distance = math.sqrt((obj.x - x) ** 2 + (obj.y - y) ** 2)
                if distance < min_distance:
                    return False
        return True

    def _choose_object_type(self, exclude_permanent: bool = False) -> str:
        """根據生成機率選擇物件類型"""
        # 基礎物件列表
        if exclude_permanent:
            # 排除永久物件（如河流）
            base_objects = ["tree", "rock", "food"]
        else:
            base_objects = ["tree", "rock", "food", "river"]

        # 偶爾生成特殊物件
        if random.random() < 0.15:  # 15% 機率生成特殊物件
            special_objects = ["chest", "cave"]
            base_objects.extend(special_objects)

        return random.choice(base_objects)

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

    def update(
        self,
        delta_time: float,
        player_moved: bool = False,
        player_x: float = 0,
        player_y: float = 0,
        time_manager=None,
    ) -> List[str]:
        """
        更新世界物件（支持主動攻擊怪物和消息系統）

        Args:
            delta_time (float): 幀時間差
            player_moved (bool): 玩家本回合是否移動
            player_x, player_y (float): 玩家當前位置
            time_manager: 時間管理器實例

        Returns:
            List[str]: 遊戲消息列表
        """
        messages = []
        self.spawn_timer += delta_time

        # 獲取時間狀態
        is_night_time = False
        is_day_time = True
        if time_manager:
            is_night_time = time_manager.is_night_time()
            is_day_time = time_manager.is_day_time()

        # 🔥 無限世界生成 - 更頻繁地檢查和生成物件
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0

            if is_night_time:
                # 夜晚優先生成怪物
                if self._try_spawn_monster(player_x, player_y):
                    messages.append("夜晚: 黑暗中出現了危險的怪物...")

            # 🔥 無論白天夜晚都要檢查並生成其他物件
            self._spawn_random_object(player_x, player_y)

        # 更新怪物行為 - 主動攻擊系統
        for obj in self.objects:
            if isinstance(obj, Monster) and obj.active:
                attack_result = obj.update_aggressive_behavior(
                    delta_time, player_x, player_y, is_day_time
                )

                # 處理怪物主動攻擊
                if attack_result and attack_result.get("monster_attack"):
                    from ..entities.player import Player  # 避免循環引用

                    if "attacker" in attack_result:
                        attacker = attack_result["attacker"]
                        # 這裡應該由遊戲主邏輯處理玩家受傷
                        messages.append(f"怪物主動攻擊！小心！")

        # 移除已摧毀的物件
        self.objects = [obj for obj in self.objects if obj.active]

        return messages

    def _try_spawn_monster(self, player_x: float = 0, player_y: float = 0) -> bool:
        """嘗試在夜晚生成怪物"""
        max_monsters = 4  # 最多同時存在4個怪物
        current_monsters = len(
            [obj for obj in self.objects if isinstance(obj, Monster) and obj.active]
        )

        if current_monsters >= max_monsters:
            return False

        # 在玩家視野邊緣外生成怪物（相機系統適配）
        spawn_distance = 300  # 距離玩家300像素外生成
        min_spawn_distance = 250  # 最小生成距離

        attempts = 0
        while attempts < 10:  # 限制嘗試次數
            # 隨機角度
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(min_spawn_distance, spawn_distance)

            # 計算生成位置
            x = player_x + distance * math.cos(angle)
            y = player_y + distance * math.sin(angle)

            # 確保生成位置沒有其他物件
            if self._check_position_clear(x, y, 50):
                self._spawn_object("monster", x, y)
                return True

            attempts += 1

        return False

    def _spawn_random_object(self, player_x: float = 0, player_y: float = 0) -> None:
        """🔥 無限世界生成系統 - 隨機生成世界物件"""
        # 🔥 實現無限世界：動態調整最大物件數
        active_objects = len([obj for obj in self.objects if obj.active])

        # 🔥 基於玩家周圍的物件密度動態生成
        nearby_objects = self.get_nearby_objects(player_x, player_y, 600)
        nearby_count = len(nearby_objects)

        # 如果玩家周圍物件不足，增加生成
        if nearby_count < 30:  # 玩家周圍保持至少30個物件
            # 🔥 擴大生成範圍，支持無限探索
            spawn_range = 1200  # 在玩家1200像素範圍內生成
            min_distance = 300  # 距離玩家至少300像素

            # 🔥 批量生成多個物件
            spawn_count = min(5, 30 - nearby_count)  # 一次最多生成5個

            for _ in range(spawn_count):
                attempts = 0
                while attempts < 15:  # 增加嘗試次數
                    # 隨機生成位置
                    angle = random.uniform(0, 2 * math.pi)
                    distance = random.uniform(min_distance, spawn_range)

                    x = player_x + distance * math.cos(angle)
                    y = player_y + distance * math.sin(angle)

                    if self._check_position_clear(x, y, 40):
                        # 選擇物件類型（排除永久物件）
                        obj_type = self._choose_object_type(exclude_permanent=True)

                        # 進一步排除河流
                        if obj_type != "river":
                            self._spawn_object(obj_type, x, y)
                            break
                    attempts += 1

        # 🔥 清理遠離玩家的物件，防止記憶體溢出
        self._cleanup_distant_objects(player_x, player_y)

    def _cleanup_distant_objects(self, player_x: float, player_y: float) -> None:
        """
        🔥 清理距離玩家太遠的物件，實現無限世界

        Args:
            player_x, player_y (float): 玩家當前位置
        """
        cleanup_distance = 2000  # 超過2000像素的物件將被清理
        objects_to_remove = []

        for obj in self.objects:
            if not obj.active:
                continue

            # 計算物件與玩家的距離
            distance = math.sqrt((obj.x - player_x) ** 2 + (obj.y - player_y) ** 2)

            # 🔥 保護重要物件：工作台、熔爐等玩家建造的建築
            if isinstance(obj, (Workbench, Furnace)):
                continue  # 永遠不清理玩家建造的建築

            # 🔥 保護河流等永久資源
            if isinstance(obj, River):
                continue  # 河流是珍貴資源，不輕易清理

            # 清理距離太遠的物件
            if distance > cleanup_distance:
                objects_to_remove.append(obj)

        # 執行清理
        for obj in objects_to_remove:
            obj.active = False

        if objects_to_remove:
            print(f"🧹 清理了 {len(objects_to_remove)} 個遠離的世界物件")

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

    def draw(self, screen: pygame.Surface, camera=None) -> None:
        """
        繪製所有世界物件

        Args:
            screen: pygame螢幕物件
            camera: 相機物件，如果提供則使用相機系統
        """
        # 按照深度排序繪製（遠的先畫，近的後畫）
        active_objects = [obj for obj in self.objects if obj.active]
        active_objects.sort(key=lambda obj: obj.y)  # 按Y座標排序

        for obj in active_objects:
            if camera:
                # 使用相機系統繪製
                # 只繪製可見的物件以提升效能
                if camera.is_visible(
                    obj.x, obj.y, getattr(obj, "width", 0), getattr(obj, "height", 0)
                ):
                    screen_x, screen_y = camera.world_to_screen(obj.x, obj.y)
                    obj.draw_with_camera(screen, screen_x, screen_y)
            else:
                # 傳統繪製方式（向後兼容）
                obj.draw(screen)

    def cleanup(self) -> None:
        """清理資源"""
        self.objects.clear()
        print("🧹 世界管理器已清理")
