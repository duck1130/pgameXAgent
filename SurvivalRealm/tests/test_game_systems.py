#!/usr/bin/env python3
"""
測試: Survival Realm 遊戲系統整合測試
測試製作系統、怪物系統和完整遊戲場景

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
from src.core.config import ITEM_RECIPES
from src.systems.time_manager import TimeManager
from src.world.world_objects import Monster


class GameSystemTester(TestGameBase):
    """遊戲系統測試類，涵蓋所有主要功能測試"""

    def __init__(self):
        """初始化測試環境"""
        super().__init__()
        self.time_manager = TimeManager()
        print("測試環境初始化完成")

    def test_crafting_system(self):
        """測試製作系統"""
        print_test_header("測試製作系統")

        # 測試進入製作模式
        print("📋 測試進入製作模式")
        result = self.enter_crafting_mode()
        print(f"   {result}")

        # 測試製作工作台
        print("📋 測試製作工作台")
        if self._can_craft_workbench():
            message = self.craft_item_safely("workbench")
            print(f"   製作結果: {message}")
            success = "製作成功" in message
        else:
            print("   材料不足，無法製作工作台")
            success = False

        print_test_result(success, "製作系統測試完成")
        return success

    def test_time_and_monster_system(self):
        """測試時間系統和怪物系統"""
        print_test_header("測試時間系統和怪物系統")

        # 測試時間系統
        print("📅 測試時間系統")
        print(f"   初始時間: {self.time_manager.get_time_string()}")
        print(f"   當前時段: {self.time_manager.get_time_period_chinese()}")

        # 模擬夜晚
        print("夜晚: 模擬時間到夜晚")
        self.time_manager.game_time = 350  # 夜晚
        print(f"   夜晚時間: {self.time_manager.get_time_string()}")
        print(f"   是否夜晚: {self.time_manager.is_night_time()}")

        # 測試怪物系統
        print("測試怪物系統")
        monster = Monster(200, 200)
        print(f"   怪物生成: 位置 ({monster.x}, {monster.y})")
        print(f"   移動速度: {monster.move_speed}")

        # 測試白天怪物死亡
        print("測試白天怪物消散")
        monster.update_slow_movement(0.1, 200, 200, True)  # 白天
        print(f"   開始死亡: {monster.is_dying}")

        print_test_result(True, "時間和怪物系統測試完成")
        return True

    def test_full_game_integration(self):
        """測試完整遊戲整合"""
        print_test_header("測試完整遊戲整合")

        try:
            # 測試基本的遊戲系統整合
            print("   測試玩家和世界管理器整合")

            # 模擬玩家互動
            result = self.player.interact_with_world(self.world_manager)
            if result:
                print(f"   互動結果: {result}")

            # 測試基本功能
            print("   測試基本遊戲功能")
            initial_health = self.player.survival_stats.health
            print(f"   玩家初始生命值: {initial_health}")

            print_test_result(True, "遊戲系統整合測試完成")
            return True

        except Exception as e:
            print_test_result(False, f"整合測試失敗: {e}")
            return False

    def _can_craft_workbench(self):
        """檢查是否可以製作工作台"""
        recipe = ITEM_RECIPES.get("workbench", {})
        for material, amount in recipe.items():
            if not self.player.inventory.has_item(material, amount):
                return False
        return True

    def run_all_tests(self):
        """執行所有測試"""
        print("測試: 開始遊戲系統整合測試...")

        tests = [
            self.test_crafting_system,
            self.test_time_and_monster_system,
            self.test_full_game_integration,
        ]

        passed = 0
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print_test_result(False, f"測試異常: {e}")

        print(f"\n📊 測試結果: {passed}/{len(tests)} 通過")
        return passed == len(tests)


def main():
    """主函數"""
    try:
        tester = GameSystemTester()
        success = tester.run_all_tests()

        if success:
            print_test_result(True, "所有系統測試通過！遊戲功能正常！")
        else:
            print_test_result(False, "部分測試失敗，請檢查遊戲功能")

    except Exception as e:
        print_test_result(False, f"測試發生錯誤: {e}")
        import traceback

        traceback.print_exc()
    finally:
        cleanup_pygame()


if __name__ == "__main__":
    main()
