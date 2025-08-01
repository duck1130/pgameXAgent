"""
🎮 Survival Realm - 檔案結構測試

測試新的檔案結構是否能正常工作
"""

print("🎮 Survival Realm 檔案結構測試")
print("=" * 50)

# 測試各個模組的導入
modules_to_test = [
    ("game.settings.game_settings", "遊戲設定"),
    ("game.player", "玩家系統"),
    ("game.items", "物品系統"),
    ("game.world", "世界系統"),
    ("game.interface", "介面系統"),
    ("game.features", "特殊功能"),
]

success_count = 0
total_count = len(modules_to_test)

for module_name, description in modules_to_test:
    try:
        __import__(module_name)
        print(f"✅ {description} ({module_name}) - 載入成功")
        success_count += 1
    except ImportError as e:
        print(f"❌ {description} ({module_name}) - 載入失敗: {e}")
    except Exception as e:
        print(f"⚠️  {description} ({module_name}) - 其他錯誤: {e}")

print("=" * 50)
print(f"📊 測試結果: {success_count}/{total_count} 個模組載入成功")

if success_count == total_count:
    print("🎉 檔案結構重新規劃完成！所有模組都能正常載入！")
else:
    print("⚠️  部分模組載入失敗，需要進一步調整導入路徑")

print()
print("📁 新的檔案結構：")
print("game/")
print("├── player/      👤 玩家相關功能")
print("├── items/       🎒 物品和背包系統")
print("├── world/       🌍 遊戲世界和物件")
print("├── interface/   🖥️ 遊戲介面和UI")
print("├── settings/    ⚙️ 遊戲設定和配置")
print("└── features/    ✨ 特殊功能（洞穴、音樂等）")
