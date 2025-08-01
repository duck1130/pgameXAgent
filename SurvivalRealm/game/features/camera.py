"""
Survival Realm - 相機系統
實現玩家中心視角的相機跟隨系統

作者: 硬漢貓咪開發團隊 🐱
日期: 2025-07-31
版本: 3.1.0

相機系統的核心概念：
1. 玩家始終位於螢幕中心
2. 世界物件根據相機偏移進行繪製
3. 相機平滑跟隨玩家移動
"""

from typing import Tuple
from ..core.config import WINDOW_CONFIG


class Camera:
    """
    相機系統 - 處理視角跟隨和世界偏移計算

    玩家固定在螢幕中心，其他物件相對移動
    """

    def __init__(self):
        """初始化相機系統"""
        # 相機在世界中的位置
        self.world_x = 0.0
        self.world_y = 0.0

        # 螢幕中心點 - 玩家固定位置
        self.screen_center_x = WINDOW_CONFIG["width"] // 2
        self.screen_center_y = WINDOW_CONFIG["height"] // 2

        # 相機跟隨參數
        self.follow_speed = 1.0  # 1.0 = 即時跟隨，<1.0 = 平滑跟隨

        print("相機系統初始化完成！玩家將固定在螢幕中心")

    def update(self, target_x: float, target_y: float, delta_time: float) -> None:
        """
        更新相機位置，跟隨目標（玩家）

        Args:
            target_x (float): 目標世界X座標（玩家中心）
            target_y (float): 目標世界Y座標（玩家中心）
            delta_time (float): 幀時間差
        """
        # 相機應該指向的世界位置（玩家中心）
        target_camera_x = target_x
        target_camera_y = target_y

        # 即時跟隨（你也可以用平滑跟隨）
        if self.follow_speed >= 1.0:
            # 即時跟隨
            self.world_x = target_camera_x
            self.world_y = target_camera_y
        else:
            # 平滑跟隨
            self.world_x += (
                (target_camera_x - self.world_x) * self.follow_speed * delta_time * 60
            )
            self.world_y += (
                (target_camera_y - self.world_y) * self.follow_speed * delta_time * 60
            )

    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """
        將世界座標轉換為螢幕座標

        Args:
            world_x (float): 世界X座標
            world_y (float): 世界Y座標

        Returns:
            Tuple[int, int]: 螢幕座標 (screen_x, screen_y)
        """
        # 計算相對於相機的偏移
        relative_x = world_x - self.world_x
        relative_y = world_y - self.world_y

        # 轉換為螢幕座標（相機中心 + 相對偏移）
        screen_x = int(self.screen_center_x + relative_x)
        screen_y = int(self.screen_center_y + relative_y)

        return screen_x, screen_y

    def screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """
        將螢幕座標轉換為世界座標

        Args:
            screen_x (int): 螢幕X座標
            screen_y (int): 螢幕Y座標

        Returns:
            Tuple[float, float]: 世界座標 (world_x, world_y)
        """
        # 計算相對於螢幕中心的偏移
        relative_x = screen_x - self.screen_center_x
        relative_y = screen_y - self.screen_center_y

        # 轉換為世界座標
        world_x = self.world_x + relative_x
        world_y = self.world_y + relative_y

        return world_x, world_y

    def get_visible_area(self) -> Tuple[float, float, float, float]:
        """
        獲取相機可見區域的世界座標範圍

        Returns:
            Tuple[float, float, float, float]: (left, top, right, bottom)
        """
        half_width = WINDOW_CONFIG["width"] // 2
        half_height = WINDOW_CONFIG["height"] // 2

        left = self.world_x - half_width
        top = self.world_y - half_height
        right = self.world_x + half_width
        bottom = self.world_y + half_height

        return left, top, right, bottom

    def is_visible(
        self, world_x: float, world_y: float, width: int = 0, height: int = 0
    ) -> bool:
        """
        檢查世界物件是否在相機可見範圍內

        Args:
            world_x (float): 物件世界X座標
            world_y (float): 物件世界Y座標
            width (int): 物件寬度
            height (int): 物件高度

        Returns:
            bool: 是否可見
        """
        left, top, right, bottom = self.get_visible_area()

        # 物件邊界
        obj_left = world_x
        obj_top = world_y
        obj_right = world_x + width
        obj_bottom = world_y + height

        # 檢查是否有重疊
        return not (
            obj_right < left or obj_left > right or obj_bottom < top or obj_top > bottom
        )

    def get_player_screen_position(self) -> Tuple[int, int]:
        """
        獲取玩家在螢幕上的固定位置

        Returns:
            Tuple[int, int]: 玩家螢幕座標（始終是螢幕中心）
        """
        return self.screen_center_x, self.screen_center_y

    def set_follow_speed(self, speed: float) -> None:
        """
        設定相機跟隨速度

        Args:
            speed (float): 跟隨速度 (1.0=即時跟隨, <1.0=平滑跟隨)
        """
        self.follow_speed = max(0.1, min(1.0, speed))
        print(f"相機跟隨速度設定為: {self.follow_speed}")


# 創建全域相機實例
camera = Camera()
