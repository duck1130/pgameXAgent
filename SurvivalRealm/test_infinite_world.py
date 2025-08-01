"""
🌍 無限世界探索測試腳本
測試玩家可以無限移動，世界會動態生成新物件

硬漢貓咪開發團隊 🐱
"""

import pygame
import sys
import time
from src.entities.player import Player
from src.world.world_manager import WorldManager
from src.systems.time_manager import TimeManager
from src.systems.camera import camera
from src.core.config import WORLD_CONFIG


def test_infinite_world():
    """測試無限世界系統"""

    print("🌍 測試無限世界探索系統...")

    # 初始化 pygame
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    clock = pygame.time.Clock()

    # 創建遊戲物件
    player = Player(0, 0)  # 從世界中心開始
    world_manager = WorldManager()
    time_manager = TimeManager()

    # 生成初始世界
    world_manager.generate_world()

    print(f"🌱 初始世界:")
    print(f"  物件總數: {len([obj for obj in world_manager.objects if obj.active])}")
    print(f"  玩家起始位置: ({player.x}, {player.y})")

    print(f"\n🎮 控制說明:")
    print(f"  WASD: 移動")
    print(f"  Shift + WASD: 衝刺")
    print(f"  F: 吃蘑菇")
    print(f"  SPACE: 顯示統計")
    print(f"  ESC: 退出")

    running = True
    last_stats_time = 0

    while running:
        delta_time = clock.tick(60) / 1000.0

        # 處理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_f:
                    if player.consume_food("mushroom"):
                        print("🍄 使用蘑菇治療！")
                elif event.key == pygame.K_SPACE:
                    # 顯示統計資訊
                    nearby = len(
                        world_manager.get_nearby_objects(player.x, player.y, 600)
                    )
                    total = len([obj for obj in world_manager.objects if obj.active])
                    print(f"📊 當前統計:")
                    print(f"  玩家位置: ({player.x:.0f}, {player.y:.0f})")
                    print(f"  附近物件: {nearby} 個")
                    print(f"  世界總物件: {total} 個")
                    print(f"  玩家體力: {player.survival_stats.energy:.1f}/100")

        # 處理輸入和更新
        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        player.update(delta_time, 1200, 800)

        # 更新世界（包含動態生成）
        world_manager.update(
            delta_time, player.has_moved_this_turn, player.x, player.y, time_manager
        )

        # 更新相機
        camera.update(
            player.x + player.width // 2, player.y + player.height // 2, delta_time
        )

        # 繪製
        screen.fill((20, 40, 20))  # 深綠色背景

        # 繪製世界物件
        world_manager.draw(screen, camera)

        # 繪製玩家（固定在螢幕中心）
        screen_center_x = screen.get_width() // 2
        screen_center_y = screen.get_height() // 2
        player.draw(screen, screen_center_x, screen_center_y)

        # 繪製UI資訊
        font = pygame.font.Font(None, 24)

        # 玩家資訊
        info_lines = [
            f"位置: ({player.x:.0f}, {player.y:.0f})",
            f"生命: {player.survival_stats.health:.0f}/100",
            f"體力: {player.survival_stats.energy:.0f}/100",
            f"狀態: {'衝刺' if player.is_sprinting else '普通' if player.is_moving else '靜止'}",
        ]

        for i, line in enumerate(info_lines):
            color = (255, 255, 0) if player.is_sprinting and i == 3 else (255, 255, 255)
            text = font.render(line, True, color)
            screen.blit(text, (10, 10 + i * 25))

        # 世界統計
        nearby_count = len(world_manager.get_nearby_objects(player.x, player.y, 600))
        total_count = len([obj for obj in world_manager.objects if obj.active])

        world_info = [
            f"附近物件: {nearby_count}",
            f"世界總物件: {total_count}",
            f"相機位置: ({camera.world_x:.0f}, {camera.world_y:.0f})",
        ]

        for i, line in enumerate(world_info):
            text = font.render(line, True, (200, 200, 255))
            screen.blit(text, (10, 120 + i * 25))

        # 控制提示
        hint_text = font.render(
            "按 SPACE 顯示統計 | 按 F 吃蘑菇 | ESC 退出", True, (180, 180, 180)
        )
        screen.blit(hint_text, (10, screen.get_height() - 30))

        pygame.display.flip()

        # 定期自動顯示統計
        current_time = time.time()
        if current_time - last_stats_time > 5:  # 每5秒顯示一次
            last_stats_time = current_time
            print(
                f"🗺️  探索中... 位置: ({player.x:.0f}, {player.y:.0f}) | 附近物件: {nearby_count} | 總物件: {total_count}"
            )

    pygame.quit()
    print("✅ 無限世界探索測試完成！")


if __name__ == "__main__":
    test_infinite_world()
