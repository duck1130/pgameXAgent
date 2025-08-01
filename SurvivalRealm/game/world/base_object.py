"""
Survival Realm - 遊戲物件基礎類
定義所有世界物件的基礎行為

作者: 硬漢貓咪開發團隊 🐱
日期: 2025-07-30
版本: 3.1.0 (重構版本)
"""

import pygame
from abc import ABC, abstractmethod
from typing import Optional, Dict, TYPE_CHECKING

# 避免循環引用
if TYPE_CHECKING:
    from ..entities.player import Player


class GameObject(ABC):
    """遊戲物件基礎類 - 所有世界物件的父類"""

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
        self.active = True  # 物件是否處於活躍狀態

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """
        繪製物件 - 子類必須實作

        Args:
            screen: pygame螢幕物件
        """
        pass

    def draw_with_camera(
        self, screen: pygame.Surface, screen_x: int, screen_y: int
    ) -> None:
        """
        使用相機座標繪製物件

        Args:
            screen: pygame螢幕物件
            screen_x: 物件在螢幕上的X座標
            screen_y: 物件在螢幕上的Y座標
        """
        # 預設實作：創建一個臨時矩形在指定螢幕位置繪製
        # 子類可以覆寫這個方法來自定義相機繪製行為
        temp_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)

        # 調用子類的繪製方法，但使用臨時位置
        original_x, original_y = self.x, self.y
        original_rect = self.rect

        # 暫時修改座標用於繪製
        self.x, self.y = screen_x, screen_y
        self.rect = temp_rect

        # 調用原始繪製方法
        self.draw(screen)

        # 恢復原始座標
        self.x, self.y = original_x, original_y
        self.rect = original_rect

    @abstractmethod
    def interact(self, player: "Player") -> Optional[Dict]:
        """
        與玩家互動 - 子類必須實作

        Args:
            player: 玩家物件

        Returns:
            Optional[Dict]: 互動結果字典，包含訊息和物品等信息
        """
        pass

    def update_rect(self) -> None:
        """更新碰撞箱位置"""
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def get_center(self) -> tuple:
        """獲取物件中心座標"""
        return (self.x + self.width // 2, self.y + self.height // 2)

    def distance_to(self, x: float, y: float) -> float:
        """
        計算到指定點的距離

        Args:
            x, y: 目標座標

        Returns:
            float: 距離
        """
        center_x, center_y = self.get_center()
        return ((center_x - x) ** 2 + (center_y - y) ** 2) ** 0.5

    def is_near(self, x: float, y: float, distance: float) -> bool:
        """
        檢查是否在指定距離內

        Args:
            x, y: 目標座標
            distance: 距離閾值

        Returns:
            bool: 是否在範圍內
        """
        return self.distance_to(x, y) <= distance

    def destroy(self) -> None:
        """銷毀物件"""
        self.active = False
