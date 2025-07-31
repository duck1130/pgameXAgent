#!/usr/bin/env python3
"""
🧪 Survival Realm 測試執行器
統一執行所有測試案例

使用方法:
    python tests/run_tests.py                # 運行所有測試
    python tests/run_tests.py crafting       # 只運行製作測試
    python tests/run_tests.py monster        # 只運行怪物測試
    python tests/run_tests.py scenario       # 只運行場景測試
"""

import sys
import os
import subprocess

# 添加根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_test(test_file, description):
    """運行單個測試"""
    print(f"\n🧪 {description}")
    print("=" * 50)

    try:
        result = subprocess.run(
            [sys.executable, test_file],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ 測試通過！")
            if result.stdout:
                print(result.stdout)
        else:
            print("❌ 測試失敗！")
            if result.stderr:
                print("錯誤信息:", result.stderr)
            if result.stdout:
                print("輸出:", result.stdout)

        return result.returncode == 0

    except Exception as e:
        print(f"❌ 測試執行錯誤: {e}")
        return False


def main():
    """主函數"""
    tests = {
        "systems": ("tests/test_game_systems.py", "遊戲系統整合測試"),
        "crafting": ("tests/test_crafting_flow.py", "製作流程詳細測試"),
        "monster": ("tests/test_monster_system.py", "怪物系統詳細測試"),
    }

    # 檢查命令行參數
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        if test_name in tests:
            test_file, description = tests[test_name]
            success = run_test(test_file, description)
            sys.exit(0 if success else 1)
        else:
            print(f"❌ 未知測試: {test_name}")
            print(f"可用測試: {', '.join(tests.keys())}")
            sys.exit(1)

    # 運行所有測試
    print("🚀 開始運行所有測試...")

    passed = 0
    total = len(tests)

    for test_name, (test_file, description) in tests.items():
        if run_test(test_file, description):
            passed += 1

    print("\n" + "=" * 50)
    print(f"📊 測試結果: {passed}/{total} 通過")

    if passed == total:
        print("🎉 所有測試都通過了！遊戲功能正常！")
        sys.exit(0)
    else:
        print("⚠️  有測試失敗，請檢查遊戲功能")
        sys.exit(1)


if __name__ == "__main__":
    main()
