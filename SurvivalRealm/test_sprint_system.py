"""
🔥 衝刺系統測試腳本
測試新的衝刺機制、體力系統和香菇治療效果

硬漢貓咪開發團隊 🐱
"""

import pygame
import sys
from src.entities.player import Player
from src.systems.inventory import item_database
from src.core.config import PLAYER_CONFIG, SURVIVAL_STATS


def test_sprint_system():
    """測試衝刺系統的所有功能"""

    print("🔥 測試衝刺系統...")

    # 初始化 pygame（簡化測試）
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    # 創建玩家
    player = Player(400, 300)

    # 給玩家一些蘑菇測試治療效果
    mushroom_item = item_database.get_item("mushroom")
    if mushroom_item:
        player.inventory.add_item(mushroom_item, 10)
        print("✅ 給玩家添加了10個蘑菇用於測試")

    print(f"📊 衝刺配置:")
    print(f"  普通移動速度: {PLAYER_CONFIG['speed']} 像素/秒")
    print(f"  衝刺移動速度: {PLAYER_CONFIG['sprint_speed']} 像素/秒")
    print(f"  衝刺體力消耗: {PLAYER_CONFIG['sprint_energy_cost']}/秒")
    print(f"  衝刺門檻體力: {PLAYER_CONFIG['sprint_threshold']}")
    print(f"  體力恢復速度: {SURVIVAL_STATS['energy']['regen_rate']}/秒")

    print("\n🎮 控制說明:")
    print("  WASD: 移動")
    print("  Shift + WASD: 衝刺")
    print("  F: 吃蘑菇治療")
    print("  ESC: 退出測試")

    running = True
    while running:
        delta_time = clock.tick(60) / 1000.0  # 60 FPS

        # 處理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_f:
                    # 測試蘑菇治療
                    if player.consume_food("mushroom"):
                        print("🍄 使用蘑菇治療！")
                    else:
                        print("❌ 沒有蘑菇了！")

        # 處理輸入
        keys = pygame.key.get_pressed()
        player.handle_input(keys)

        # 更新玩家
        player.update(delta_time, 800, 600)

        # 繪製
        screen.fill((40, 40, 40))

        # 繪製玩家
        player.draw(screen)

        # 繪製狀態資訊
        font = pygame.font.Font(None, 24)

        # 顯示當前狀態
        status_lines = [
            f"生命值: {player.survival_stats.health:.1f}/100",
            f"體力值: {player.survival_stats.energy:.1f}/100",
            f"飢餓度: {player.survival_stats.hunger:.1f}/100",
            f"移動狀態: {'衝刺' if player.is_sprinting else '普通' if player.is_moving else '靜止'}",
            f"位置: ({player.x:.1f}, {player.y:.1f})",
            f"蘑菇數量: {player.inventory.get_item_count('mushroom')}",
        ]

        for i, line in enumerate(status_lines):
            color = (255, 255, 0) if player.is_sprinting and i == 3 else (255, 255, 255)
            text = font.render(line, True, color)
            screen.blit(text, (10, 10 + i * 25))

        # 體力警告
        if player.survival_stats.energy < PLAYER_CONFIG["sprint_threshold"]:
            warning_text = font.render("😴 體力不足，無法衝刺！", True, (255, 100, 100))
            screen.blit(warning_text, (10, 200))

        pygame.display.flip()

    pygame.quit()
    print("✅ 衝刺系統測試完成！")


if __name__ == "__main__":
    test_sprint_system()
