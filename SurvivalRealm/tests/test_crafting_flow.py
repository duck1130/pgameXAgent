#!/usr/bin/env python3
"""
模擬實際遊戲中的製作流程測試
測試從按C鍵進入製作模式到按數字4製作工作台的完整流程

作者: 硬漢貓咪開發團隊 🐱
日期: 2025-07-31
"""

import pygame
import sys
import os

# 確保能導入遊戲模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_utils import (
    TestGameBase,
    print_test_header,
    print_test_result,
    cleanup_pygame,
)
from src.core.config import GameState


class CraftingFlowTester(TestGameBase):
    """製作流程測試類，使用共用基礎類"""

    def simulate_key_c(self):
        """模擬按下C鍵進入製作模式"""
        print(f"\n調試: 模擬按下C鍵...")
        print(
            f"C鍵被按下，當前狀態: {self.state}, 製作模式: {self.player.crafting_mode}"
        )

        if self.player.crafting_mode:
            result = self.exit_crafting_mode()
        else:
            result = self.enter_crafting_mode()

        print(result)
        self.print_current_state()

    def simulate_key_4(self):
        """模擬按下數字4鍵"""
        print(f"\n調試: 模擬按下數字4鍵...")
        self._handle_number_key(4)

    def _handle_number_key(self, number: int) -> None:
        """處理數字鍵輸入 - 簡化版本"""
        print(f"調試: 調試：收到數字鍵 {number}，當前狀態: {self.state}")
        print(f"調試: 調試：玩家製作模式: {self.player.crafting_mode}")

        # 檢查製作模式
        if self.player.crafting_mode or self.state == GameState.CRAFTING:
            print(f"調試：在製作模式，呼叫製作處理")
            self._handle_crafting(number)
        else:
            print(f"調試：在其他狀態 ({self.state})，跳過處理")

    def _handle_crafting(self, number: int) -> None:
        """處理製作操作 - 簡化版本"""
        print(f"調試：進入製作處理，數字={number}")

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
            print(f"調試：選中物品 {item_id} (索引 {number-1})")

            # 工作台可以隨時製作（基礎製作）
            if item_id == "workbench":
                print(f"調試：製作工作台，呼叫 craft_item_safely")
                message = self.craft_item_safely(item_id)
                print(f"📝 調試：製作結果訊息: {message}")
                if message:
                    print(f"💬 遊戲訊息: {message}")
                return

            # 其他物品需要靠近工作台才能製作（高級製作）
            print(f"調試：不在工作台附近，無法製作 {item_id}")
            print(f"💬 遊戲訊息: 製作 {item_id} 需要靠近工作台！")

        else:
            print(f"調試：數字 {number} 超出範圍 (1-{len(recipes)})")
            print(
                f"💬 遊戲訊息: 請按 1-7：1=斧頭 2=稿子 3=水桶 4=工作台 5=熔爐 6=鐵劍 7=鐵甲"
            )

    def run_test_scenario(self):
        """執行測試場景"""
        print("開始製作流程測試...")

        # 場景1: 直接在PLAYING狀態按數字4（應該跳過處理）
        print_test_header("場景1: 在PLAYING狀態直接按數字4")
        self.simulate_key_4()

        # 場景2: 按C鍵進入製作模式
        print_test_header("場景2: 按C鍵進入製作模式")
        self.simulate_key_c()

        # 場景3: 在製作模式下按數字4
        print_test_header("場景3: 在製作模式下按數字4")
        self.simulate_key_4()

        # 顯示最終狀態
        print_test_header("最終狀態")
        self.print_current_state()


def main():
    """主函數"""
    try:
        tester = CraftingFlowTester()
        tester.run_test_scenario()
        print_test_result(True, "製作流程測試完成！")

    except Exception as e:
        print_test_result(False, f"測試發生錯誤: {e}")
        import traceback

        traceback.print_exc()

    finally:
        cleanup_pygame()


if __name__ == "__main__":
    main()
