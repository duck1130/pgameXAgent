#!/usr/bin/env python3
"""
👹 怪物系統專項測試
測試夜晚生成和白天死亡機制

作者: 硬漢貓咪開發團隊 🐱
日期: 2025-07-31
"""
import sys
import os

# 添加 src 目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from test_utils import print_test_header, print_test_result
from src.systems.time_manager import TimeManager
from src.world.world_manager import WorldManager
from src.world.world_objects import Monster


def test_time_system():
    """測試時間系統"""
    print_test_header("測試時間系統")

    time_manager = TimeManager()

    # 測試初始狀態（白天）
    print(f"   初始時間: {time_manager.get_time_string()}")
    print(f"   當前時段: {time_manager.get_time_period_chinese()}")
    print(f"   是否白天: {time_manager.is_day_time()}")
    print(f"   是否夜晚: {time_manager.is_night_time()}")

    # 模擬時間流逝到夜晚
    print("\n🌙 模擬時間流逝到夜晚...")
    time_manager.game_time = 350  # 跳到夜晚（第6分鐘）

    print(f"   夜晚時間: {time_manager.get_time_string()}")
    print(f"   當前時段: {time_manager.get_time_period_chinese()}")
    print(f"   是否白天: {time_manager.is_day_time()}")
    print(f"   是否夜晚: {time_manager.is_night_time()}")

    # 模擬時間流逝到下一天
    print("\n☀️ 模擬時間流逝到下一天...")
    time_manager.game_time = 610  # 跳到第2天白天

    print(f"   新一天時間: {time_manager.get_time_string()}")
    print(f"   當前時段: {time_manager.get_time_period_chinese()}")
    print(f"   當前天數: {time_manager.current_day}")

    print_test_result(True, "時間系統測試完成")
    return True


def test_monster_system():
    """測試怪物系統"""
    print_test_header("測試怪物系統")

    # 創建測試怪物
    monster = Monster(100, 100)
    print(f"   怪物生成: 位置 ({monster.x}, {monster.y})")
    print(f"   移動速度: {monster.move_speed} 像素/秒")
    print(f"   是否死亡中: {monster.is_dying}")

    # 模擬白天來臨
    print("\n☀️ 模擬白天來臨...")
    monster.update_slow_movement(0.1, 200, 200, True)  # is_day_time=True
    print(f"   是否開始死亡: {monster.is_dying}")

    # 模擬死亡過程
    print("\n💀 模擬死亡過程...")
    for i in range(5):
        monster.update_slow_movement(6.0, 200, 200, True)  # 每次6秒
        progress = int(monster.death_timer)
        print(f"   死亡進度: {progress}/30秒, 移動速度: {monster.move_speed:.2f}")
        if not monster.active:
            print("   怪物已完全消散！")
            break

    print_test_result(True, "怪物系統測試完成")
    return True


def test_world_manager_integration():
    """測試世界管理器整合"""
    print_test_header("測試世界管理器整合")

    world_manager = WorldManager()
    time_manager = TimeManager()

    # 測試白天狀態（不應生成怪物）
    print("   白天狀態測試...")
    initial_monster_count = len(
        [obj for obj in world_manager.objects if isinstance(obj, Monster)]
    )
    print(f"   初始怪物數量: {initial_monster_count}")

    # 模擬夜晚到來
    print("   切換到夜晚...")
    time_manager.game_time = 350  # 夜晚

    # 模擬更新循環
    for i in range(3):
        world_manager.update(5.0, False, 400, 300, time_manager)  # 5秒更新
        monster_count = len(
            [obj for obj in world_manager.objects if isinstance(obj, Monster)]
        )
        print(f"   更新 {i+1}: 怪物數量 {monster_count}")

    print_test_result(True, "世界管理器整合測試完成")
    return True


def main():
    """主函數"""
    print("🧪 開始怪物系統全面測試...\n")

    tests = [
        test_time_system,
        test_monster_system,
        test_world_manager_integration,
    ]

    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print_test_result(False, f"測試異常: {e}")

    print(f"\n📊 測試結果: {passed}/{len(tests)} 通過")

    if passed == len(tests):
        print_test_result(True, "所有怪物系統測試通過！")
    else:
        print_test_result(False, "部分測試失敗")


if __name__ == "__main__":
    main()
