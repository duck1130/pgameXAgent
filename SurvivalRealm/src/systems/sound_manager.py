"""
Survival Realm - 音效管理系統
負責處理遊戲音效的播放、管理和音量控制

作者: 硬漢貓咪開發團隊 🐱
日期: 2025-08-01
版本: 1.0.0
"""

import pygame
import os
import time
from typing import Optional, Dict
from ..core.config import AUDIO_CONFIG


class SoundManager:
    """音效管理器 - 負責遊戲音效控制"""

    def __init__(self):
        """初始化音效管理器"""
        # 確保 pygame mixer 已初始化
        if not pygame.mixer.get_init():
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()

        # 音效狀態
        self.master_volume = AUDIO_CONFIG["master_volume"]
        self.sfx_volume = AUDIO_CONFIG["sfx_volume"]

        # 音效通道管理
        self.max_channels = 8  # 最大同時播放音效數量
        pygame.mixer.set_num_channels(self.max_channels)

        # 音效快取
        self.sound_cache: Dict[str, pygame.mixer.Sound] = {}

        # 腳步聲特殊管理
        self.last_footstep_time = 0
        self.footstep_interval = AUDIO_CONFIG["footstep_interval"]

        # 預載入常用音效
        self._preload_sounds()

        print("🔊 音效管理器初始化完成！")

    def _preload_sounds(self) -> None:
        """預載入所有音效檔案"""
        for sound_key, sound_path in AUDIO_CONFIG["sound_files"].items():
            self._load_sound(sound_key, sound_path)

    def _load_sound(
        self, sound_key: str, sound_path: str
    ) -> Optional[pygame.mixer.Sound]:
        """
        載入音效檔案

        Args:
            sound_key (str): 音效鍵值
            sound_path (str): 音效檔案路徑

        Returns:
            pygame.mixer.Sound: 載入的音效物件，失敗返回 None
        """
        # 檢查是否已經快取
        if sound_key in self.sound_cache:
            return self.sound_cache[sound_key]

        # 檢查檔案是否存在
        if not os.path.exists(sound_path):
            print(f"⚠️  音效檔案不存在: {sound_path}")
            return None

        try:
            sound = pygame.mixer.Sound(sound_path)
            # 設定音量
            sound.set_volume(self.sfx_volume * self.master_volume)

            # 快取音效
            self.sound_cache[sound_key] = sound
            print(f"🎵 已載入音效: {sound_key}")
            return sound

        except pygame.error as e:
            print(f"❌ 載入音效失敗 {sound_key}: {e}")
            return None

    def play_sound(
        self, sound_key: str, volume_override: Optional[float] = None
    ) -> bool:
        """
        播放音效

        Args:
            sound_key (str): 音效鍵值
            volume_override (float, optional): 覆蓋音量 (0.0-1.0)

        Returns:
            bool: 播放成功返回 True
        """
        # 獲取音效
        if sound_key not in AUDIO_CONFIG["sound_files"]:
            print(f"❌ 未知音效: {sound_key}")
            return False

        sound_path = AUDIO_CONFIG["sound_files"][sound_key]
        sound = self._load_sound(sound_key, sound_path)

        if not sound:
            return False

        try:
            # 設定音量
            if volume_override is not None:
                sound.set_volume(volume_override * self.master_volume)
            else:
                sound.set_volume(self.sfx_volume * self.master_volume)

            # 播放音效
            sound.play()
            return True

        except pygame.error as e:
            print(f"❌ 播放音效失敗 {sound_key}: {e}")
            return False

    def play_footstep(self, force: bool = False) -> bool:
        """
        播放腳步聲（帶間隔控制）

        Args:
            force (bool): 是否強制播放，忽略間隔限制

        Returns:
            bool: 播放成功返回 True
        """
        current_time = time.time()

        # 檢查時間間隔
        if (
            not force
            and (current_time - self.last_footstep_time) < self.footstep_interval
        ):
            return False

        # 播放腳步聲
        if self.play_sound("footstep", volume_override=0.3):  # 腳步聲音量較小
            self.last_footstep_time = current_time
            return True

        return False

    def play_interact_sound(self) -> bool:
        """播放互動音效"""
        return self.play_sound("interact")

    def play_craft_sound(self) -> bool:
        """播放製作音效"""
        return self.play_sound("craft")

    def play_pickup_sound(self) -> bool:
        """播放撿取音效"""
        return self.play_sound("pickup")

    def play_attack_sound(self) -> bool:
        """播放攻擊音效"""
        return self.play_sound("attack")

    def play_sword_whoosh_sound(self) -> bool:
        """播放劍揮擊音效"""
        return self.play_sound("sword_whoosh")

    def play_sword_hit_sound(self) -> bool:
        """播放劍命中音效"""
        return self.play_sound("sword_hit")

    def play_tree_break_sound(self) -> bool:
        """播放砍樹音效"""
        return self.play_sound("tree_break")

    def play_chest_open_sound(self) -> bool:
        """播放寶箱開啟音效"""
        return self.play_sound("chest_open")

    def play_break_sound(self, material_type: str = "stone") -> bool:
        """
        播放破壞音效

        Args:
            material_type (str): 材料類型 ("stone", "wood")

        Returns:
            bool: 播放成功返回 True
        """
        sound_key = f"{material_type}_break"
        if sound_key in AUDIO_CONFIG["sound_files"]:
            return self.play_sound(sound_key)
        else:
            # 預設使用石頭破壞音效
            return self.play_sound("stone_break")

    def set_master_volume(self, volume: float) -> None:
        """
        設定主音量

        Args:
            volume (float): 音量值 (0.0-1.0)
        """
        self.master_volume = max(0.0, min(1.0, volume))

        # 更新所有快取音效的音量
        for sound in self.sound_cache.values():
            sound.set_volume(self.sfx_volume * self.master_volume)

        print(f"🔊 主音量設定為: {self.master_volume:.1f}")

    def set_sfx_volume(self, volume: float) -> None:
        """
        設定音效音量

        Args:
            volume (float): 音效音量值 (0.0-1.0)
        """
        self.sfx_volume = max(0.0, min(1.0, volume))

        # 更新所有快取音效的音量
        for sound in self.sound_cache.values():
            sound.set_volume(self.sfx_volume * self.master_volume)

        print(f"🎵 音效音量設定為: {self.sfx_volume:.1f}")

    def stop_all_sounds(self) -> None:
        """停止所有音效播放"""
        pygame.mixer.stop()
        print("🔇 已停止所有音效")

    def cleanup(self) -> None:
        """清理音效資源"""
        self.stop_all_sounds()
        self.sound_cache.clear()
        print("🧹 音效管理器已清理")


# 全域音效管理器實例
sound_manager = SoundManager()
