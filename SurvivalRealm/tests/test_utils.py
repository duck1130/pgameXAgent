#!/usr/bin/env python3
"""
🛠️ 測試工具模組
提供共用的測試工具函數，避免重複程式碼

作者: 硬漢貓咪開發團隊 🐱
日期: 2025-07-31
"""

import pygame
import sys
import os

# 確保能導入遊戲模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import WINDOW_CONFIG, GameState, ITEM_RECIPES
from src.entities.player import Player
from src.systems.inventory import item_database
from src.world.world_manager import WorldManager
from src.ui.user_interface import UI


class TestGameBase:
    """測試遊戲基礎類，提供共用功能"""

    def __init__(self):
        """初始化測試環境"""
        # 初始化 pygame (如果需要)
        if not pygame.get_init():
            pygame.init()
            self.screen = pygame.display.set_mode(
                (WINDOW_CONFIG["width"], WINDOW_CONFIG["height"])
            )
            pygame.display.set_caption("測試環境")

        # 遊戲狀態
        self.running = True
        self._state = GameState.PLAYING

        # 創建遊戲物件
        self.player = Player(100, 100)
        self.world_manager = WorldManager()
        self.ui = UI()

        # 給玩家添加基本材料
        self._setup_test_materials()

    def _setup_test_materials(self):
        """設置測試用材料"""
        materials = [
            ("wood", 10),
            ("stone", 10),
            ("iron_ore", 5),
            ("coal", 5),
        ]

        for material_id, quantity in materials:
            item = item_database.get_item(material_id)
            if item:
                self.player.inventory.add_item(item, quantity)

    @property
    def state(self):
        """取得遊戲狀態"""
        return self._state

    @state.setter
    def state(self, new_state):
        """設定遊戲狀態（帶調試）"""
        if self._state != new_state:
            print(f"🔄 狀態變化: {self._state} -> {new_state}")
        self._state = new_state

    def print_current_state(self):
        """打印當前狀態"""
        print(f"\n📊 當前狀態:")
        print(f"   遊戲狀態: {self.state}")
        print(f"   製作模式: {self.player.crafting_mode}")
        print(f"   燒製模式: {self.player.smelting_mode}")

        print(f"📦 物品欄內容:")
        for slot_index, item_slot in enumerate(self.player.inventory.slots):
            if item_slot and item_slot.item:
                print(
                    f"   槽位 {slot_index}: {item_slot.item.name} x{item_slot.quantity}"
                )

    def craft_item_safely(self, item_id: str) -> str:
        """安全的製作物品邏輯（共用版本）"""
        if item_id not in ITEM_RECIPES:
            return "❌ 無法製作此物品"

        recipe = ITEM_RECIPES[item_id]
        item = item_database.get_item(item_id)

        if not item:
            return "❌ 物品不存在"

        # 檢查材料
        missing_materials = []
        for material, amount in recipe.items():
            if not self.player.inventory.has_item(material, amount):
                owned = self.player.inventory.get_item_count(material)
                missing_materials.append(f"{material} (需要{amount}，擁有{owned})")

        if missing_materials:
            return f"❌ 缺少材料: {', '.join(missing_materials)}"

        # 檢查物品欄空間
        if self.player.inventory.is_full():
            empty_slots = self.player.inventory.get_empty_slots()
            if empty_slots == 0:
                return "❌ 物品欄已滿，無法製作！請先清理物品欄"

        # 消耗材料
        consumed_materials = []
        for material, amount in recipe.items():
            removed = self.player.inventory.remove_item(material, amount)
            consumed_materials.append(f"{material} x{removed}")

        # 添加製作出的物品
        added = self.player.inventory.add_item(item, 1)
        if added > 0:
            materials_used = ", ".join(consumed_materials)
            return f"🎉 製作成功！獲得 [{item.name}] ✨\n消耗材料: {materials_used}"
        else:
            # 如果添加失敗，恢復材料
            for material, amount in recipe.items():
                mat_item = item_database.get_item(material)
                if mat_item:
                    self.player.inventory.add_item(mat_item, amount)
            return "❌ 物品欄已滿，製作失敗！材料已退還"

    def enter_crafting_mode(self):
        """進入製作模式"""
        self.player.crafting_mode = True
        self.player.smelting_mode = False
        self.state = GameState.CRAFTING
        return f"✅ 進入製作模式！狀態: {self.state}"

    def exit_crafting_mode(self):
        """退出製作模式"""
        self.player.crafting_mode = False
        self.state = GameState.PLAYING
        return f"❌ 退出製作模式！狀態: {self.state}"


def cleanup_pygame():
    """清理 pygame 資源"""
    try:
        pygame.quit()
    except:
        pass


def print_test_header(title: str):
    """打印測試標題"""
    print(f"\n{'=' * 50}")
    print(f"🧪 {title}")
    print(f"{'=' * 50}")


def print_test_result(success: bool, message: str = ""):
    """打印測試結果"""
    if success:
        print(f"✅ 測試通過！{message}")
    else:
        print(f"❌ 測試失敗！{message}")
