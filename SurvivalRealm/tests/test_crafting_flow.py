#!/usr/bin/env python3
"""
🔧 模擬實際遊戲中的製作流程測試
測試從按C鍵進入製作模式到按數字4製作工作台的完整流程

作者: 硬漢貓咪開發團隊 🐱
日期: 2025-07-31
"""

import pygame
import sys
import os

# 確保能導入遊戲模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import WINDOW_CONFIG, COLORS, GameState, ITEM_RECIPES
from src.entities.player import Player
from src.systems.inventory import item_database
from src.world.world_manager import WorldManager
from src.ui.user_interface import UI


class TestGame:
    """測試遊戲類，模擬實際遊戲流程"""

    def __init__(self):
        # 初始化 pygame
        pygame.init()
        self.screen = pygame.display.set_mode(
            (WINDOW_CONFIG["width"], WINDOW_CONFIG["height"])
        )
        pygame.display.set_caption("製作流程測試")

        # 遊戲狀態
        self.running = True
        self._state = GameState.PLAYING

        # 創建遊戲物件
        self.player = Player(100, 100)
        self.world_manager = WorldManager()
        self.ui = UI()

        # 給玩家添加製作材料
        wood_item = item_database.get_item("wood")
        stone_item = item_database.get_item("stone")
        if wood_item:
            self.player.inventory.add_item(wood_item, 10)
        if stone_item:
            self.player.inventory.add_item(stone_item, 10)

        print("✅ 測試遊戲初始化完成")
        self.print_current_state()

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

    def simulate_key_c(self):
        """模擬按下C鍵進入製作模式"""
        print(f"\n🎯 模擬按下C鍵...")
        print(
            f"🔄 C鍵被按下，當前狀態: {self.state}, 製作模式: {self.player.crafting_mode}"
        )

        self.player.crafting_mode = not self.player.crafting_mode
        self.player.smelting_mode = False

        if self.player.crafting_mode:
            self.state = GameState.CRAFTING
            print(
                f"✅ 進入製作模式！新狀態: {self.state}, 製作模式: {self.player.crafting_mode}"
            )
            print("📋 製作提示: 按 1-7 製作物品")
        else:
            self.state = GameState.PLAYING
            print(
                f"❌ 退出製作模式！新狀態: {self.state}, 製作模式: {self.player.crafting_mode}"
            )

        self.print_current_state()

    def simulate_key_4(self):
        """模擬按下數字4鍵"""
        print(f"\n🎯 模擬按下數字4鍵...")
        self._handle_number_key(4)

    def _handle_number_key(self, number: int) -> None:
        """處理數字鍵輸入 - 複製自main.py"""
        print(f"🎯 調試：收到數字鍵 {number}，當前狀態: {self.state}")
        print(f"🎯 調試：玩家製作模式: {self.player.crafting_mode}")
        print(f"🎯 調試：玩家燒製模式: {self.player.smelting_mode}")
        print(f"🎯 調試：完整狀態檢查:")
        print(f"   - GameState == CRAFTING: {self.state == GameState.CRAFTING}")
        print(f"   - GameState == SMELTING: {self.state == GameState.SMELTING}")
        print(f"   - GameState == INVENTORY: {self.state == GameState.INVENTORY}")
        print(f"   - crafting_mode == True: {self.player.crafting_mode == True}")
        print(f"   - smelting_mode == True: {self.player.smelting_mode == True}")

        # 檢查雙重條件 - 製作模式
        if self.player.crafting_mode or self.state == GameState.CRAFTING:
            print(f"✅ 調試：在製作模式，呼叫製作處理")
            self._handle_crafting(number)
        # 檢查雙重條件 - 燒製模式
        elif self.player.smelting_mode or self.state == GameState.SMELTING:
            print(f"🔥 調試：在燒製模式，呼叫燒製處理")
            # self._handle_smelting(number)
        # 物品欄狀態
        elif self.state == GameState.INVENTORY:
            print(f"🎒 調試：在物品欄狀態")
        else:
            print(f"⚔️ 調試：在其他狀態 ({self.state})，嘗試裝備")
            # self._handle_equipment(number)

    def _handle_crafting(self, number: int) -> None:
        """處理製作操作 - 複製自main.py"""
        print(f"🔧 調試：進入製作處理，數字={number}")

        recipes = [
            "axe",
            "pickaxe",
            "bucket",
            "workbench",
            "furnace",
            "iron_sword",
            "iron_armor",
        ]

        print(f"📋 調試：可用配方 {len(recipes)} 個: {recipes}")

        if 1 <= number <= len(recipes):
            item_id = recipes[number - 1]
            print(f"✅ 調試：選中物品 {item_id} (索引 {number-1})")

            # 工作台可以隨時製作（基礎製作）
            if item_id == "workbench":
                print(f"🏗️ 調試：製作工作台，呼叫 _craft_item")
                message = self._craft_item(item_id)
                print(f"📝 調試：製作結果訊息: {message}")
                if message:
                    print(f"💬 遊戲訊息: {message}")
                return

            # 其他物品需要靠近工作台才能製作（高級製作）
            print(f"❌ 調試：不在工作台附近，無法製作 {item_id}")
            print(f"💬 遊戲訊息: 製作 {item_id} 需要靠近工作台！")

        else:
            print(f"❌ 調試：數字 {number} 超出範圍 (1-{len(recipes)})")
            print(
                f"💬 遊戲訊息: 請按 1-7：1=斧頭 2=稿子 3=水桶 4=工作台 5=熔爐 6=鐵劍 7=鐵甲"
            )

    def _craft_item(self, item_id: str):
        """製作物品邏輯 - 複製自main.py"""
        from src.core.config import ITEM_RECIPES

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
            # 顯示詳細的製作成功信息
            materials_used = ", ".join(consumed_materials)
            return f"🎉 製作成功！獲得 [{item.name}] ✨\n消耗材料: {materials_used}"
        else:
            # 如果添加失敗，恢復材料
            for material, amount in recipe.items():
                mat_item = item_database.get_item(material)
                if mat_item:
                    self.player.inventory.add_item(mat_item, amount)
            return "❌ 物品欄已滿，製作失敗！材料已退還"

    def run_test_scenario(self):
        """執行測試場景"""
        print("🎮 開始製作流程測試...")

        # 場景1: 直接在PLAYING狀態按數字4（應該嘗試裝備）
        print("\n" + "=" * 50)
        print("📋 場景1: 在PLAYING狀態直接按數字4")
        self.simulate_key_4()

        # 場景2: 按C鍵進入製作模式
        print("\n" + "=" * 50)
        print("📋 場景2: 按C鍵進入製作模式")
        self.simulate_key_c()

        # 場景3: 在製作模式下按數字4
        print("\n" + "=" * 50)
        print("📋 場景3: 在製作模式下按數字4")
        self.simulate_key_4()

        # 顯示最終狀態
        print("\n" + "=" * 50)
        print("📊 最終狀態:")
        self.print_current_state()


def main():
    """主函數"""
    try:
        test_game = TestGame()
        test_game.run_test_scenario()

        print("\n✅ 製作流程測試完成！")

    except Exception as e:
        print(f"❌ 測試發生錯誤: {e}")
        import traceback

        traceback.print_exc()

    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
