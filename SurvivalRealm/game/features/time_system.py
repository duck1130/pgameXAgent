"""
Survival Realm - 時間管理系統
處理遊戲內的日夜循環和時間流逝

作者: 硬漢貓咪開發團隊 🐱
日期: 2025-07-30
版本: 3.1.0 (重構版本)
"""

from ..core.config import TimeOfDay, TIME_CONFIG


class TimeManager:
    """時間管理系統 - 處理日夜循環和時間流逝"""

    def __init__(self) -> None:
        """初始化時間管理器"""
        self.game_time = 0.0  # 遊戲內時間 (秒)
        self.time_scale = TIME_CONFIG["time_scale"]  # 時間倍率
        self.current_day = 1  # 當前天數
        self.day_length = TIME_CONFIG["day_length"]  # 一天的長度

    def update(self, delta_time: float) -> None:
        """
        更新遊戲時間

        Args:
            delta_time (float): 實際時間差(秒)
        """
        self.game_time += delta_time * self.time_scale

        # 檢查是否過了一天
        if self.game_time >= self.day_length:
            self.game_time = 0
            self.current_day += 1

    def get_time_of_day(self) -> TimeOfDay:
        """
        獲取當前時段

        Returns:
            TimeOfDay: 當前時段枚舉
        """
        # 簡化的日夜循環：前5分鐘為白天，後5分鐘為夜晚
        if self.game_time < 300:  # 前5分鐘 (300秒)
            return TimeOfDay.DAY
        else:  # 後5分鐘
            return TimeOfDay.NIGHT

    def get_time_string(self) -> str:
        """
        獲取時間字串顯示

        Returns:
            str: 格式化的時間字串
        """
        # 顯示當前時段和剩餘時間
        current_phase_time = self.game_time % 300  # 每個階段5分鐘
        remaining_minutes = int((300 - current_phase_time) / 60)
        remaining_seconds = int((300 - current_phase_time) % 60)

        time_of_day = self.get_time_of_day()
        phase_name = "白天" if time_of_day == TimeOfDay.DAY else "夜晚"

        return f"第{self.current_day}天 {phase_name} 剩餘 {remaining_minutes:02d}:{remaining_seconds:02d}"

    def get_time_period_chinese(self) -> str:
        """
        獲取中文時段描述

        Returns:
            str: 中文時段名稱
        """
        time_of_day = self.get_time_of_day()
        return "白天" if time_of_day == TimeOfDay.DAY else "夜晚"

    def is_night_time(self) -> bool:
        """檢查是否為夜晚"""
        return self.get_time_of_day() == TimeOfDay.NIGHT

    def is_day_time(self) -> bool:
        """檢查是否為白天"""
        return self.get_time_of_day() == TimeOfDay.DAY

    def get_light_level(self) -> float:
        """
        獲取當前光照等級 (0.0 - 1.0)

        Returns:
            float: 光照等級，1.0為最亮，0.0為最暗
        """
        time_of_day = self.get_time_of_day()

        light_levels = {
            TimeOfDay.DAWN: 0.6,
            TimeOfDay.DAY: 1.0,
            TimeOfDay.DUSK: 0.4,
            TimeOfDay.NIGHT: 0.2,
        }

        return light_levels.get(time_of_day, 1.0)

    def get_danger_multiplier(self) -> float:
        """
        獲取危險倍數 (夜晚更危險)

        Returns:
            float: 危險倍數
        """
        time_of_day = self.get_time_of_day()

        if time_of_day == TimeOfDay.NIGHT:
            return 2.0  # 夜晚危險度翻倍
        elif time_of_day == TimeOfDay.DUSK:
            return 1.5  # 黃昏稍微危險
        else:
            return 1.0  # 白天和黎明正常

    def skip_to_time(self, target_hour: int) -> None:
        """
        跳到指定時間

        Args:
            target_hour (int): 目標小時 (0-23)
        """
        if 0 <= target_hour <= 23:
            self.game_time = target_hour * 60  # 轉換為分鐘

    def add_time(self, minutes: int) -> None:
        """
        增加遊戲時間

        Args:
            minutes (int): 要增加的分鐘數
        """
        self.game_time += minutes

        # 檢查是否跨天
        while self.game_time >= self.day_length:
            self.game_time -= self.day_length
            self.current_day += 1

    def get_detailed_status(self) -> dict:
        """
        獲取詳細的時間狀態

        Returns:
            dict: 包含各種時間信息的字典
        """
        return {
            "day": self.current_day,
            "time_string": self.get_time_string(),
            "time_of_day": self.get_time_of_day(),
            "period_chinese": self.get_time_period_chinese(),
            "light_level": self.get_light_level(),
            "danger_multiplier": self.get_danger_multiplier(),
            "is_night": self.is_night_time(),
            "is_day": self.is_day_time(),
        }
