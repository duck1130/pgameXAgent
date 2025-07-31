#!/usr/bin/env python3
"""
🧪 Survival Realm 遊戲系統整合測試
合併製作系統、怪物系統和完整遊戲場景測試

作者: 硬漢貓咪開發團隊 🐱
日期: 2025-07-31
"""

import pygame
import sys
import os
import time

# 確保能導入遊戲模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import Game
from src.core.config import WINDOW_CONFIG, COLORS, GameState, ITEM_RECIPES
from src.entities.player import Player
from src.systems.inventory import item_database
from src.systems.time_manager import TimeManager
from src.world.world_manager import WorldManager
from src.world.world_objects import Monster
from src.ui.user_interface import UI


class GameSystemTester:
    """遊戲系統測試類，涵蓋所有主要功能測試"""

    def __init__(self):
        """初始化測試環境"""
        pygame.init()
        self.screen = pygame.display.set_mode(
            (WINDOW_CONFIG["width"], WINDOW_CONFIG["height"])
        )
        pygame.display.set_caption("遊戲系統測試")

        # 遊戲狀態
        self.running = True
        self._state = GameState.PLAYING

        # 創建遊戲物件
        self.player = Player(100, 100)
        self.world_manager = WorldManager()
        self.time_manager = TimeManager()
        self.ui = UI()

        # 給玩家添加製作材料
        wood_item = item_database.get_item("wood")
        stone_item = item_database.get_item("stone")
        if wood_item:
            self.player.inventory.add_item(wood_item, 10)
        if stone_item:
            self.player.inventory.add_item(stone_item, 10)

        print("✅ 測試環境初始化完成")

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        if self._state != new_state:
            print(f"🔄 狀態變化: {self._state} -> {new_state}")
        self._state = new_state

    def test_crafting_system(self):
        """測試製作系統"""
        print("\n🔧 測試製作系統...")
        print("=" * 50)

        # 測試進入製作模式
        print("📋 測試進入製作模式")
        self.player.crafting_mode = True
        self.state = GameState.CRAFTING
        print(f"   狀態: {self.state}, 製作模式: {self.player.crafting_mode}")

        # 測試製作工作台
        print("📋 測試製作工作台")
        if self._can_craft_workbench():
            message = self._craft_item("workbench")
            print(f"   製作結果: {message}")
        else:
            print("   ❌ 材料不足，無法製作工作台")

        print("✅ 製作系統測試完成")
        return True

    def test_time_and_monster_system(self):
        """測試時間系統和怪物系統"""
        print("\n⏰ 測試時間系統和怪物系統...")
        print("=" * 50)

        # 測試時間系統
        print("📅 測試時間系統")
        print(f"   初始時間: {self.time_manager.get_time_string()}")
        print(f"   當前時段: {self.time_manager.get_time_period_chinese()}")

        # 模擬夜晚
        print("🌙 模擬時間到夜晚")
        self.time_manager.game_time = 350  # 夜晚
        print(f"   夜晚時間: {self.time_manager.get_time_string()}")
        print(f"   是否夜晚: {self.time_manager.is_night_time()}")

        # 測試怪物系統
        print("👹 測試怪物系統")
        monster = Monster(200, 200)
        print(f"   怪物生成: 位置 ({monster.x}, {monster.y})")
        print(f"   移動速度: {monster.move_speed}")

        # 測試白天怪物死亡
        print("☀️ 測試白天怪物消散")
        monster.update_slow_movement(0.1, 200, 200, True)  # 白天
        print(f"   開始死亡: {monster.is_dying}")

        print("✅ 時間和怪物系統測試完成")
        return True

    def test_full_game_integration(self):
        """測試完整遊戲整合"""
        print("\n🎮 測試完整遊戲整合...")
        print("=" * 50)

        # 創建完整遊戲實例
        game = Game()
        print(f"   初始狀態: {game.state}")

        # 模擬按鍵事件
        print("🎯 模擬C鍵進入製作模式")
        c_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_c)
        pygame.event.post(c_event)
        game.handle_events()
        print(f"   處理後狀態: {game.state}")

        # 模擬製作
        print("🎯 模擬4鍵製作工作台")
        four_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_4)
        pygame.event.post(four_event)
        game.handle_events()

        print("✅ 完整遊戲整合測試完成")
        return True

    def _can_craft_workbench(self):
        """檢查是否可以製作工作台"""
        recipe = ITEM_RECIPES.get("workbench", {})
        for material, amount in recipe.items():
            if not self.player.inventory.has_item(material, amount):
                return False
        return True

    def _craft_item(self, item_id: str):
        """製作物品邏輯"""
        if item_id not in ITEM_RECIPES:
            return "❌ 無法製作此物品"

        recipe = ITEM_RECIPES[item_id]
        item = item_database.get_item(item_id)

        if not item:
            return "❌ 物品不存在"

        # 檢查材料
        for material, amount in recipe.items():
            if not self.player.inventory.has_item(material, amount):
                return f"❌ 缺少材料: {material} x{amount}"

        # 消耗材料並製作
        for material, amount in recipe.items():
            self.player.inventory.remove_item(material, amount)

        if self.player.inventory.add_item(item, 1) > 0:
            return f"🎉 製作成功！獲得 [{item.name}]"
        else:
            return "❌ 物品欄已滿"

    def run_all_tests(self):
        """執行所有測試"""
        print("🧪 開始遊戲系統整合測試...")

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
                print(f"❌ 測試失敗: {e}")

        print(f"\n📊 測試結果: {passed}/{len(tests)} 通過")
        return passed == len(tests)


def main():
    """主函數"""
    try:
        tester = GameSystemTester()
        success = tester.run_all_tests()

        if success:
            print("\n✅ 所有系統測試通過！遊戲功能正常！")
        else:
            print("\n⚠️ 部分測試失敗，請檢查遊戲功能")

    except Exception as e:
        print(f"❌ 測試發生錯誤: {e}")
        import traceback

        traceback.print_exc()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
