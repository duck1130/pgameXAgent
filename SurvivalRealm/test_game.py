"""
🎮 Survival Realm - 測試腳本
測試重構後的遊戲是否能正常運行

作者: 硬漢貓咪開發團隊 🐱
日期: 2025-07-30
"""

import sys
import pygame


def test_imports():
    """測試所有模組是否能正常導入"""
    print("🧪 測試模組導入...")

    try:
        from src.core.config import WINDOW_CONFIG, COLORS

        print("✅ 核心配置模組 - OK")

        from src.entities.player import Player

        print("✅ 玩家實體模組 - OK")

        from src.systems.inventory import Inventory, Item, item_database

        print("✅ 物品系統模組 - OK")

        from src.systems.time_manager import TimeManager

        print("✅ 時間管理模組 - OK")

        from src.world.world_manager import WorldManager

        print("✅ 世界管理模組 - OK")

        from src.ui.user_interface import UI

        print("✅ UI系統模組 - OK")

        print("🎉 所有模組導入成功！")
        return True

    except ImportError as e:
        print(f"❌ 模組導入失敗: {e}")
        return False


def test_basic_functionality():
    """測試基本功能"""
    print("\n🔧 測試基本功能...")

    try:
        # 測試玩家創建
        from src.entities.player import Player

        player = Player(100, 100)
        print("✅ 玩家創建 - OK")

        # 測試物品系統
        from src.systems.inventory import item_database

        wood_item = item_database.get_item("wood")
        if wood_item:
            player.inventory.add_item(wood_item, 5)
            print("✅ 物品系統 - OK")

        # 測試時間管理
        from src.systems.time_manager import TimeManager

        time_manager = TimeManager()
        time_manager.update(1.0)
        print("✅ 時間管理 - OK")

        # 測試世界管理
        from src.world.world_manager import WorldManager

        world_manager = WorldManager()
        print("✅ 世界管理 - OK")

        print("🎉 基本功能測試成功！")
        return True

    except Exception as e:
        print(f"❌ 功能測試失敗: {e}")
        return False


def main():
    """主測試函數"""
    print("🚀 Survival Realm - 重構版測試")
    print("=" * 50)

    # 測試 pygame
    try:
        pygame.init()
        print("✅ Pygame 初始化 - OK")
    except Exception as e:
        print(f"❌ Pygame 初始化失敗: {e}")
        return False

    # 測試模組導入
    if not test_imports():
        return False

    # 測試基本功能
    if not test_basic_functionality():
        return False

    print("\n" + "=" * 50)
    print("🎊 所有測試通過！遊戲可以正常運行")
    print("💡 執行 'python main.py' 啟動完整遊戲")

    pygame.quit()
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
