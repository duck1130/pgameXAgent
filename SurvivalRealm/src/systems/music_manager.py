"""
🎵 Survival Realm - 音樂管理系統
負責處理背景音樂的播放、切換和音量控制

作者: 硬漢貓咪開發團隊 🐱
日期: 2025-07-31
版本: 1.0.0
"""

import pygame
import os
from typing import Optional
from src.core.config import MUSIC_CONFIG, GameState, TimeOfDay


class MusicManager:
    """音樂管理器 - 負責遊戲背景音樂控制"""

    def __init__(self):
        """初始化音樂管理器"""
        # 初始化 pygame mixer
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.init()

        # 音樂狀態
        self.current_music = None
        self.is_playing = False
        self.volume = MUSIC_CONFIG["volume"]["music"]
        self.master_volume = MUSIC_CONFIG["volume"]["master"]

        # 音樂檔案映射
        self.music_tracks = {
            GameState.MENU: "menu_theme",
            GameState.PLAYING: "main_theme",
            GameState.PAUSED: None,  # 暫停時不改變音樂
            GameState.GAME_OVER: None,  # 遊戲結束時停止音樂
        }

        # 根據時間的音樂映射
        self.time_music_tracks = {
            TimeOfDay.NIGHT: "night_theme",
            TimeOfDay.DAY: "main_theme",
            TimeOfDay.DAWN: "main_theme",
            TimeOfDay.DUSK: "main_theme",
        }

        print("🎵 音樂管理器初始化完成！")

    def load_music(self, music_key: str) -> bool:
        """
        載入音樂檔案

        Args:
            music_key (str): 音樂鍵值

        Returns:
            bool: 載入成功返回 True
        """
        if music_key not in MUSIC_CONFIG["music_files"]:
            print(f"❌ 找不到音樂檔案: {music_key}")
            return False

        music_path = MUSIC_CONFIG["music_files"][music_key]

        # 檢查檔案是否存在
        if not os.path.exists(music_path):
            print(f"⚠️  音樂檔案不存在: {music_path}")
            return False

        try:
            pygame.mixer.music.load(music_path)
            print(f"🎶 已載入音樂: {music_key}")
            return True
        except pygame.error as e:
            print(f"❌ 載入音樂失敗 {music_key}: {e}")
            return False

    def play_music(self, music_key: str, fade_in: bool = True) -> None:
        """
        播放音樂

        Args:
            music_key (str): 音樂鍵值
            fade_in (bool): 是否使用淡入效果
        """
        # 如果已經在播放相同音樂，則不做任何操作
        if self.current_music == music_key and self.is_playing:
            return

        # 停止當前音樂
        if self.is_playing:
            self.stop_music(fade_out=True)

        # 載入並播放新音樂
        if self.load_music(music_key):
            try:
                loops = -1 if MUSIC_CONFIG["loop"] else 0
                fade_duration = MUSIC_CONFIG["fade_duration"] if fade_in else 0

                pygame.mixer.music.play(loops=loops, fade_ms=fade_duration)
                pygame.mixer.music.set_volume(self.volume * self.master_volume)

                self.current_music = music_key
                self.is_playing = True

                print(f"🎵 開始播放: {music_key}")

            except pygame.error as e:
                print(f"❌ 播放音樂失敗: {e}")

    def stop_music(self, fade_out: bool = True) -> None:
        """
        停止音樂播放

        Args:
            fade_out (bool): 是否使用淡出效果
        """
        if not self.is_playing:
            return

        try:
            if fade_out:
                pygame.mixer.music.fadeout(MUSIC_CONFIG["fade_duration"])
            else:
                pygame.mixer.music.stop()

            self.is_playing = False
            self.current_music = None
            print("🔇 已停止音樂播放")

        except pygame.error as e:
            print(f"❌ 停止音樂失敗: {e}")

    def pause_music(self) -> None:
        """暫停音樂"""
        if self.is_playing:
            pygame.mixer.music.pause()
            print("⏸️  音樂已暫停")

    def unpause_music(self) -> None:
        """恢復音樂播放"""
        if self.is_playing:
            pygame.mixer.music.unpause()
            print("▶️  音樂已恢復")

    def set_volume(self, volume: float) -> None:
        """
        設定音樂音量

        Args:
            volume (float): 音量值 (0.0 - 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume * self.master_volume)
        print(f"🔊 音樂音量設定為: {self.volume:.1f}")

    def set_master_volume(self, volume: float) -> None:
        """
        設定主音量

        Args:
            volume (float): 主音量值 (0.0 - 1.0)
        """
        self.master_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume * self.master_volume)
        print(f"🔊 主音量設定為: {self.master_volume:.1f}")

    def update_music_for_state(
        self, game_state: GameState, time_of_day: Optional[TimeOfDay] = None
    ) -> None:
        """
        根據遊戲狀態更新音樂

        Args:
            game_state (GameState): 當前遊戲狀態
            time_of_day (TimeOfDay, optional): 當前時間段
        """
        target_music = None

        # 處理特殊狀態
        if game_state == GameState.PAUSED:
            self.pause_music()
            return
        elif game_state == GameState.GAME_OVER:
            self.stop_music(fade_out=True)
            return

        # 如果遊戲正在進行中，根據時間選擇音樂
        if game_state == GameState.PLAYING and time_of_day:
            target_music = self.time_music_tracks.get(time_of_day, "main_theme")
        else:
            # 其他狀態使用預設音樂映射
            music_key = self.music_tracks.get(game_state)
            if music_key:
                target_music = music_key

        # 播放目標音樂
        if target_music and target_music != self.current_music:
            self.play_music(target_music, fade_in=True)

        # 確保音樂在恢復時繼續播放
        if (
            game_state == GameState.PLAYING
            and not pygame.mixer.music.get_busy()
            and self.current_music
        ):
            self.unpause_music()

    def is_music_playing(self) -> bool:
        """
        檢查音樂是否正在播放

        Returns:
            bool: 音樂是否正在播放
        """
        return pygame.mixer.music.get_busy() and self.is_playing

    def get_current_music(self) -> Optional[str]:
        """
        獲取當前播放的音樂

        Returns:
            str: 當前音樂鍵值，如果沒有則返回 None
        """
        return self.current_music if self.is_playing else None

    def toggle_music(self) -> bool:
        """
        切換音樂播放狀態

        Returns:
            bool: 切換後的播放狀態
        """
        if self.is_music_playing():
            self.pause_music()
            return False
        else:
            self.unpause_music()
            return True

    def cleanup(self) -> None:
        """清理音樂資源"""
        self.stop_music(fade_out=False)
        pygame.mixer.quit()
        print("🧹 音樂管理器已清理")
