"""
🎮 Survival Realm - 主遊戲程式
2D RPG 生存遊戲 - 重構版本

作者: 開發團隊
日期: 2025-07-30
版本: 3.1.0 (重構版本)

好了好了，遊戲程式量太大被拆分重構了！
雖然本大爺很不願意承認，但這樣確實更好維護!
"""

import pygame
import sys
import time
from typing import List, Tuple, Optional

# 導入遊戲模組
from src.core.config import WINDOW_CONFIG, COLORS, GameState, UI_CONFIG
from src.entities.player import Player
from src.systems.inventory import item_database
from src.world.world_manager import WorldManager
from src.systems.time_manager import TimeManager
from src.ui.user_interface import UI


class Game:
    """主遊戲類 - 遊戲核心邏輯管理"""

    def __init__(self) -> None:
        """初始化遊戲 - 準備所有必要的系統"""
        print("🚀 初始化 Survival Realm...")

        # 初始化 Pygame
        pygame.init()

        # 建立遊戲視窗
        self.screen = pygame.display.set_mode(
            (WINDOW_CONFIG["width"], WINDOW_CONFIG["height"])
        )
        pygame.display.set_caption(WINDOW_CONFIG["title"])

        # 時鐘控制
        self.clock = pygame.time.Clock()

        # 遊戲狀態
        self.state = GameState.PLAYING
        self.running = True

        # 初始化各個遊戲系統
        self._initialize_systems()

        # 訊息系統
        self.messages: List[Tuple[str, float]] = []
        self.message_duration = UI_CONFIG["message_duration"]

        print("✅ 遊戲初始化完成！")
        self._print_controls()

    def _initialize_systems(self) -> None:
        """初始化所有遊戲系統"""
        # 初始化玩家
        start_x, start_y = WINDOW_CONFIG["width"] // 2, WINDOW_CONFIG["height"] // 2
        self.player = Player(start_x, start_y)

        # 初始化世界管理器
        self.world_manager = WorldManager()

        # 初始化時間管理器
        self.time_manager = TimeManager()

        # 初始化UI系統
        self.ui = UI()

        # 生成初始世界
        self.world_manager.generate_world()

    def _print_controls(self) -> None:
        """打印控制說明"""
        print("📖 遊戲操作說明:")
        print("   WASD - 移動角色")
        print("   E - 與物件互動")
        print("   F - 消耗食物")
        print("   I - 開啟/關閉物品欄")
        print("   C - 製作介面 (需靠近工作臺)")
        print("   S - 燒製介面 (需靠近熔爐)")
        print("   1-5 - 裝備物品或製作")
        print("   ESC - 暫停/繼續遊戲")
        print("   Q - 退出遊戲")

    def handle_events(self) -> None:
        """處理遊戲事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)

    def _handle_keydown(self, key: int) -> None:
        """處理按鍵按下事件"""
        # ESC 鍵 - 狀態切換
        if key == pygame.K_ESCAPE:
            if self.state == GameState.PLAYING:
                self.state = GameState.PAUSED
            elif self.state in [
                GameState.PAUSED,
                GameState.INVENTORY,
                GameState.CRAFTING,
                GameState.SMELTING,
            ]:
                self.state = GameState.PLAYING
                self.player.crafting_mode = False
                self.player.smelting_mode = False

        # Q 鍵 - 快速退出
        elif key == pygame.K_q:
            self.running = False

        # 遊戲進行中的按鍵
        elif self.state == GameState.PLAYING:
            self._handle_gameplay_keys(key)

    def _handle_gameplay_keys(self, key: int) -> None:
        """處理遊戲進行中的按鍵"""
        if key == pygame.K_e:
            # 與世界互動
            message = self.player.interact_with_world(self.world_manager)
            if message:
                self.add_message(message)

        elif key == pygame.K_f:
            # 消耗食物
            if self.player.consume_food():
                self.add_message("消耗食物，恢復飢餓值！")
            else:
                self.add_message("沒有食物可以消耗")

        elif key == pygame.K_i:
            # 切換物品欄
            self.state = (
                GameState.INVENTORY
                if self.state != GameState.INVENTORY
                else GameState.PLAYING
            )

        elif key == pygame.K_c:
            # 製作介面
            self.player.crafting_mode = not self.player.crafting_mode
            self.player.smelting_mode = False
            if self.player.crafting_mode:
                self.state = GameState.CRAFTING
            else:
                self.state = GameState.PLAYING

        elif key == pygame.K_s:
            # 燒製介面
            self.player.smelting_mode = not self.player.smelting_mode
            self.player.crafting_mode = False
            if self.player.smelting_mode:
                self.state = GameState.SMELTING
            else:
                self.state = GameState.PLAYING

        # 數字鍵操作
        elif pygame.K_1 <= key <= pygame.K_5:
            number = key - pygame.K_1 + 1
            self._handle_number_key(number)

    def _handle_number_key(self, number: int) -> None:
        """處理數字鍵操作"""
        if self.state == GameState.CRAFTING:
            # 製作物品
            self._handle_crafting(number)
        elif self.state == GameState.SMELTING:
            # 燒製物品
            self._handle_smelting(number)
        else:
            # 裝備物品
            self._handle_equipment(number)

    def _handle_crafting(self, number: int) -> None:
        """處理製作操作"""
        recipes = ["axe", "pickaxe", "bucket", "workbench", "furnace"]
        if 1 <= number <= len(recipes):
            item_id = recipes[number - 1]
            message = self._craft_item(item_id)
            if message:
                self.add_message(message)

    def _handle_smelting(self, number: int) -> None:
        """處理燒製操作"""
        if number == 1:  # 只有鐵錠可以燒製
            message = self._smelt_item("iron_ingot")
            if message:
                self.add_message(message)

    def _handle_equipment(self, number: int) -> None:
        """處理裝備操作"""
        tools = ["axe", "pickaxe", "bucket", "iron_sword", "iron_armor"]
        if 1 <= number <= len(tools):
            item_id = tools[number - 1]
            if self.player.inventory.has_item(item_id, 1):
                if self.player.equip_item(item_id):
                    item = item_database.get_item(item_id)
                    self.add_message(f"裝備了 {item.name}！")

    def _craft_item(self, item_id: str) -> Optional[str]:
        """製作物品邏輯"""
        from src.core.config import ITEM_RECIPES

        if item_id not in ITEM_RECIPES:
            return "無法製作此物品"

        recipe = ITEM_RECIPES[item_id]

        # 檢查材料
        for material, amount in recipe.items():
            if not self.player.inventory.has_item(material, amount):
                return f"缺少材料: {material} x{amount}"

        # 消耗材料
        for material, amount in recipe.items():
            self.player.inventory.remove_item(material, amount)

        # 添加製作出的物品
        item = item_database.get_item(item_id)
        if item:
            added = self.player.inventory.add_item(item, 1)
            if added > 0:
                return f"製作了 {item.name}！"
            else:
                return "物品欄已滿"

        return "製作失敗"

    def _smelt_item(self, item_id: str) -> Optional[str]:
        """燒製物品邏輯"""
        if item_id == "iron_ingot":
            if not self.player.inventory.has_item("iron_ore", 1):
                return "缺少鐵礦"

            has_fuel = self.player.inventory.has_item(
                "coal", 1
            ) or self.player.inventory.has_item("wood", 1)
            if not has_fuel:
                return "缺少燃料(煤炭或木材)"

            # 消耗材料和燃料
            self.player.inventory.remove_item("iron_ore", 1)
            if self.player.inventory.has_item("coal", 1):
                self.player.inventory.remove_item("coal", 1)
            else:
                self.player.inventory.remove_item("wood", 1)

            # 添加鐵錠
            item = item_database.get_item("iron_ingot")
            if item:
                added = self.player.inventory.add_item(item, 1)
                if added > 0:
                    return "燒製了鐵錠！"
                else:
                    return "物品欄已滿"

        return "無法燒製此物品"

    def add_message(self, message: str) -> None:
        """
        添加遊戲訊息

        Args:
            message (str): 要顯示的訊息
        """
        current_time = time.time()
        self.messages.append((message, current_time))

        # 限制訊息數量
        max_messages = UI_CONFIG["max_messages"]
        if len(self.messages) > max_messages:
            self.messages.pop(0)

    def update(self) -> None:
        """更新遊戲邏輯"""
        if self.state not in [
            GameState.PLAYING,
            GameState.CRAFTING,
            GameState.SMELTING,
        ]:
            return

        # 計算幀時間
        delta_time = self.clock.get_time() / 1000.0

        # 處理玩家輸入（只在遊戲進行時）
        if self.state == GameState.PLAYING:
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)

        # 更新各系統
        self.player.update(delta_time, WINDOW_CONFIG["width"], WINDOW_CONFIG["height"])
        self.world_manager.update(delta_time)
        self.time_manager.update(delta_time)

        # 清理過期訊息
        self._cleanup_messages()

        # 檢查遊戲結束條件
        if not self.player.is_alive():
            self.state = GameState.GAME_OVER

    def _cleanup_messages(self) -> None:
        """清理過期的訊息"""
        current_time = time.time()
        self.messages = [
            (msg, timestamp)
            for msg, timestamp in self.messages
            if current_time - timestamp < self.message_duration
        ]

    def draw(self) -> None:
        """繪製遊戲畫面"""
        # 清空螢幕
        self.screen.fill(COLORS["BACKGROUND"])

        # 根據遊戲狀態繪製不同內容
        if self.state in [GameState.PLAYING, GameState.CRAFTING, GameState.SMELTING]:
            self._draw_gameplay()
        elif self.state == GameState.INVENTORY:
            self._draw_inventory()
        elif self.state == GameState.PAUSED:
            self._draw_pause_screen()
        elif self.state == GameState.GAME_OVER:
            self._draw_game_over_screen()

        # 更新顯示
        pygame.display.flip()

    def _draw_gameplay(self) -> None:
        """繪製遊戲進行畫面"""
        # 繪製世界物件
        self.world_manager.draw(self.screen)

        # 繪製玩家
        self.player.draw(self.screen)

        # 繪製UI
        self.ui.draw_survival_bars(self.screen, self.player)
        self.ui.draw_time_info(self.screen, self.time_manager)
        self.ui.draw_messages(self.screen, self.messages)

        # 繪製製作/燒製介面
        if self.state == GameState.CRAFTING:
            self.ui.draw_crafting_interface(self.screen, self.player)
        elif self.state == GameState.SMELTING:
            self.ui.draw_smelting_interface(self.screen, self.player)

    def _draw_inventory(self) -> None:
        """繪製物品欄畫面"""
        # 先繪製遊戲背景（半透明）
        self._draw_gameplay()

        # 繪製半透明覆蓋層
        overlay = pygame.Surface((WINDOW_CONFIG["width"], WINDOW_CONFIG["height"]))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # 繪製物品欄
        self.ui.draw_inventory(self.screen, self.player.inventory)

    def _draw_pause_screen(self) -> None:
        """繪製暫停畫面"""
        # 半透明覆蓋層
        overlay = pygame.Surface((WINDOW_CONFIG["width"], WINDOW_CONFIG["height"]))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # 暫停文字
        self.ui.draw_centered_text(
            self.screen,
            "遊戲暫停",
            WINDOW_CONFIG["width"] // 2,
            WINDOW_CONFIG["height"] // 2,
            COLORS["TEXT"],
            "large",
        )

        # 提示文字
        self.ui.draw_centered_text(
            self.screen,
            "按 ESC 繼續遊戲",
            WINDOW_CONFIG["width"] // 2,
            WINDOW_CONFIG["height"] // 2 + 50,
            COLORS["TEXT"],
            "medium",
        )

    def _draw_game_over_screen(self) -> None:
        """繪製遊戲結束畫面"""
        # 半透明覆蓋層
        overlay = pygame.Surface((WINDOW_CONFIG["width"], WINDOW_CONFIG["height"]))
        overlay.set_alpha(200)
        overlay.fill((100, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # 遊戲結束文字
        self.ui.draw_centered_text(
            self.screen,
            "遊戲結束",
            WINDOW_CONFIG["width"] // 2,
            WINDOW_CONFIG["height"] // 2,
            COLORS["DANGER"],
            "large",
        )

        # 統計資訊
        stats_text = f"存活天數: {self.time_manager.current_day}"
        self.ui.draw_centered_text(
            self.screen,
            stats_text,
            WINDOW_CONFIG["width"] // 2,
            WINDOW_CONFIG["height"] // 2 + 50,
            COLORS["TEXT"],
            "medium",
        )

        # 重新開始提示
        self.ui.draw_centered_text(
            self.screen,
            "按 Q 鍵退出遊戲",
            WINDOW_CONFIG["width"] // 2,
            WINDOW_CONFIG["height"] // 2 + 100,
            COLORS["TEXT"],
            "small",
        )

    def run(self) -> None:
        """運行遊戲主迴圈"""
        print("🎮 開始遊戲！")

        while self.running:
            # 控制幀率
            self.clock.tick(WINDOW_CONFIG["fps"])

            # 處理事件
            self.handle_events()

            # 更新遊戲邏輯
            self.update()

            # 繪製畫面
            self.draw()

        # 清理資源
        pygame.quit()
        print("👋 遊戲結束，感謝遊玩！")


def main():
    """主函數 - 遊戲入口點"""
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"❌ 遊戲發生錯誤: {e}")
        pygame.quit()
        sys.exit(1)


if __name__ == "__main__":
    main()
