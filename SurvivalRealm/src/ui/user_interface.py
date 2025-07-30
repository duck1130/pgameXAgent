"""
🎮 Survival Realm - 使用者介面系統
處理所有UI繪製和顯示

作者: 硬漢貓咪開發團隊 🐱
日期: 2025-07-30
版本: 3.1.0 (重構版本)
"""

import pygame
import time
from typing import List, Tuple, Optional, TYPE_CHECKING

from ..core.config import WINDOW_CONFIG, COLORS, SURVIVAL_STATS, UI_CONFIG, ITEM_RECIPES
from ..systems.inventory import Inventory, ItemType

# 避免循環引用
if TYPE_CHECKING:
    from ..entities.player import Player
    from ..systems.time_manager import TimeManager


class UI:
    """使用者介面管理類"""

    def __init__(self) -> None:
        """初始化UI系統"""
        pygame.font.init()

        # 嘗試載入中文字體
        self.fonts = self._load_fonts()

        print("✅ UI系統初始化完成！")

    def _load_fonts(self) -> dict:
        """載入字體，針對不同操作系統優化"""
        fonts = {}
        font_sizes = UI_CONFIG["font_size"]

        # 主字體路徑
        font_path = UI_CONFIG["font_path"]
        fallback_paths = UI_CONFIG["font_fallback"]

        print("🔍 開始載入字體...")
        print(f"🖥️  檢測到系統: {self._get_system_name()}")

        # 檢查系統可用字體
        self._check_system_fonts()

        for size_name, size in font_sizes.items():
            font_loaded = False
            loaded_font_info = ""

            # 嘗試主字體
            try:
                fonts[size_name] = pygame.font.Font(font_path, size)
                font_loaded = True
                loaded_font_info = f"主字體: {font_path}"
                if size_name == "large":  # 只打印一次
                    print(f"✅ {loaded_font_info}")
            except (FileNotFoundError, OSError) as e:
                if size_name == "large":
                    print(f"❌ 主字體載入失敗: {font_path}")

            # 嘗試備用字體
            if not font_loaded:
                for i, fallback_path in enumerate(fallback_paths):
                    try:
                        if fallback_path is None:
                            fonts[size_name] = pygame.font.Font(None, size)
                            loaded_font_info = "系統預設字體"
                        else:
                            fonts[size_name] = pygame.font.Font(fallback_path, size)
                            loaded_font_info = f"備用字體 {i+1}: {fallback_path}"

                        font_loaded = True
                        if size_name == "large":
                            print(f"✅ {loaded_font_info}")
                        break
                    except (FileNotFoundError, OSError):
                        if size_name == "large":
                            print(f"❌ 備用字體 {i+1} 載入失敗: {fallback_path}")
                        continue

            # 如果都失敗，使用系統預設
            if not font_loaded:
                fonts[size_name] = pygame.font.Font(None, size)
                if size_name == "large":
                    print("⚠️  所有字體都載入失敗，使用系統預設字體")
                    print("💡 建議安裝支援中文的字體以獲得更好的顯示效果")

        # 測試中文字符顯示
        self._test_chinese_font_support(fonts["medium"])

        return fonts

    def _check_system_fonts(self) -> None:
        """檢查系統可用字體（僅在 macOS 上）"""
        import platform
        import os

        if platform.system() != "Darwin":
            return

        print("🔎 檢查 macOS 系統字體...")

        # macOS 常見中文字體路徑
        common_fonts = [
            ("/System/Library/Fonts/PingFang.ttc", "蘋方"),
            ("/System/Library/Fonts/Hiragino Sans GB.ttc", "冬青黑體簡體"),
            ("/System/Library/Fonts/STHeiti Light.ttc", "華文黑體"),
            ("/System/Library/Fonts/Supplemental/Songti.ttc", "宋體"),
            ("/Library/Fonts/Arial Unicode MS.ttf", "Arial Unicode MS"),
        ]

        available_fonts = []
        for font_path, font_name in common_fonts:
            if os.path.exists(font_path):
                available_fonts.append(font_name)
                print(f"✅ 發現字體: {font_name}")
            else:
                print(f"❌ 未發現: {font_name}")

        if available_fonts:
            print(f"🎉 共發現 {len(available_fonts)} 個中文字體")
        else:
            print("⚠️  未發現專用中文字體，將使用系統預設字體")

    def _get_system_name(self) -> str:
        """獲取系統名稱"""
        import platform

        system = platform.system()

        system_names = {"Darwin": "macOS", "Windows": "Windows", "Linux": "Linux"}

        return system_names.get(system, system)

    def _test_chinese_font_support(self, font) -> None:
        """測試字體對中文的支援程度"""
        test_chars = ["你好", "遊戲", "生存", "🎮"]

        print("🧪 測試中文字體支援...")

        for char_test in test_chars:
            try:
                # 嘗試渲染測試字符
                test_surface = font.render(char_test, True, (255, 255, 255))
                # 如果渲染成功且有實際內容
                if test_surface.get_width() > 0 and test_surface.get_height() > 0:
                    print(f"✅ 字符 '{char_test}' 支援良好")
                else:
                    print(f"⚠️  字符 '{char_test}' 可能顯示為方框")
            except Exception as e:
                print(f"❌ 字符 '{char_test}' 渲染失敗: {e}")

        print("🎯 字體測試完成！")

    def draw_text(
        self,
        surface: pygame.Surface,
        text: str,
        x: int,
        y: int,
        color: Tuple[int, int, int],
        size: str = "medium",
    ) -> None:
        """
        繪製文字

        Args:
            surface: 繪製表面
            text: 文字內容
            x, y: 位置座標
            color: 文字顏色
            size: 字體大小 ("large", "medium", "small")
        """
        font = self.fonts.get(size, self.fonts["medium"])
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, (x, y))

    def draw_centered_text(
        self,
        surface: pygame.Surface,
        text: str,
        center_x: int,
        center_y: int,
        color: Tuple[int, int, int],
        size: str = "medium",
    ) -> None:
        """
        繪製置中文字

        Args:
            surface: 繪製表面
            text: 文字內容
            center_x, center_y: 中心位置
            color: 文字顏色
            size: 字體大小
        """
        font = self.fonts.get(size, self.fonts["medium"])
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(center_x, center_y))
        surface.blit(text_surface, text_rect)

    def draw_survival_bars(self, screen: pygame.Surface, player: "Player") -> None:
        """
        繪製生存狀態條

        Args:
            screen: pygame螢幕物件
            player: 玩家物件
        """
        bar_width = 200
        bar_height = 20
        bar_spacing = 30
        start_x = 20
        start_y = 20

        stats = player.survival_stats
        stat_data = [
            ("生命值", stats.health, SURVIVAL_STATS["health"]["max"], COLORS["HEALTH"]),
            ("飢餓度", stats.hunger, SURVIVAL_STATS["hunger"]["max"], COLORS["HUNGER"]),
            ("口渴度", stats.thirst, SURVIVAL_STATS["thirst"]["max"], COLORS["THIRST"]),
            ("體力值", stats.energy, SURVIVAL_STATS["energy"]["max"], COLORS["ENERGY"]),
            ("精神值", stats.sanity, SURVIVAL_STATS["sanity"]["max"], COLORS["SANITY"]),
        ]

        for i, (name, current, max_val, color) in enumerate(stat_data):
            y = start_y + i * bar_spacing

            # 繪製背景條
            bg_rect = pygame.Rect(start_x, y, bar_width, bar_height)
            pygame.draw.rect(screen, COLORS["UI_PANEL"], bg_rect)
            pygame.draw.rect(screen, COLORS["UI_BORDER"], bg_rect, 2)

            # 繪製數值條
            fill_width = int((current / max_val) * bar_width)
            if fill_width > 0:
                fill_rect = pygame.Rect(start_x, y, fill_width, bar_height)
                pygame.draw.rect(screen, color, fill_rect)

            # 繪製文字標籤
            text = f"{name}: {int(current)}/{int(max_val)}"
            self.draw_text(
                screen, text, start_x + bar_width + 10, y + 2, COLORS["TEXT"], "small"
            )

        # 繪製玩家狀態
        status_text = player.get_status_text()
        if status_text != "正常":
            self.draw_text(
                screen,
                f"狀態: {status_text}",
                start_x,
                start_y + 5 * bar_spacing,
                COLORS["WARNING"],
                "small",
            )

    def draw_time_info(
        self, screen: pygame.Surface, time_manager: "TimeManager"
    ) -> None:
        """
        繪製時間資訊

        Args:
            screen: pygame螢幕物件
            time_manager: 時間管理器
        """
        time_str = time_manager.get_time_string()
        period_str = time_manager.get_time_period_chinese()

        # 時間顯示
        self.draw_text(
            screen, time_str, WINDOW_CONFIG["width"] - 200, 20, COLORS["TEXT"], "medium"
        )

        # 時段顯示
        self.draw_text(
            screen,
            period_str,
            WINDOW_CONFIG["width"] - 200,
            50,
            COLORS["WARNING"],
            "medium",
        )

    def draw_messages(
        self, screen: pygame.Surface, messages: List[Tuple[str, float]]
    ) -> None:
        """
        繪製遊戲訊息

        Args:
            screen: pygame螢幕物件
            messages: 訊息列表 [(訊息, 時間戳)]
        """
        y_offset = WINDOW_CONFIG["height"] - 150
        message_duration = UI_CONFIG["message_duration"]

        for message, timestamp in messages:
            # 計算透明度（訊息即將消失時變淡）
            current_time = time.time()
            age = current_time - timestamp
            alpha = max(0, min(255, int(255 * (1 - age / message_duration))))

            # 創建半透明表面
            text_surface = self.fonts["small"].render(message, True, COLORS["TEXT"])
            text_surface.set_alpha(alpha)

            screen.blit(text_surface, (20, y_offset))
            y_offset -= 25

    def draw_inventory(self, screen: pygame.Surface, inventory: Inventory) -> None:
        """
        繪製物品欄介面

        Args:
            screen: pygame螢幕物件
            inventory: 物品欄物件
        """
        # 物品欄背景
        inv_width = 400
        inv_height = 350
        inv_x = (WINDOW_CONFIG["width"] - inv_width) // 2
        inv_y = (WINDOW_CONFIG["height"] - inv_height) // 2

        bg_rect = pygame.Rect(inv_x, inv_y, inv_width, inv_height)
        pygame.draw.rect(screen, COLORS["UI_PANEL"], bg_rect)
        pygame.draw.rect(screen, COLORS["UI_BORDER"], bg_rect, 3)

        # 標題
        self.draw_centered_text(
            screen,
            "物品欄",
            inv_x + inv_width // 2,
            inv_y + 25,
            COLORS["TEXT"],
            "large",
        )

        # 繪製物品格子
        self._draw_inventory_slots(screen, inventory, inv_x, inv_y)

        # 繪製物品統計
        self._draw_inventory_stats(screen, inventory, inv_x, inv_y, inv_height)

    def _draw_inventory_slots(
        self, screen: pygame.Surface, inventory: Inventory, inv_x: int, inv_y: int
    ) -> None:
        """繪製物品欄格子"""
        slot_size = 40
        slots_per_row = 5
        slot_spacing = 5
        start_x = inv_x + 30
        start_y = inv_y + 60

        for i in range(inventory.size):
            row = i // slots_per_row
            col = i % slots_per_row

            slot_x = start_x + col * (slot_size + slot_spacing)
            slot_y = start_y + row * (slot_size + slot_spacing)

            slot_rect = pygame.Rect(slot_x, slot_y, slot_size, slot_size)

            # 繪製格子背景
            pygame.draw.rect(screen, COLORS["BACKGROUND"], slot_rect)
            pygame.draw.rect(screen, COLORS["UI_BORDER"], slot_rect, 2)

            # 如果有物品，繪製物品
            if i < len(inventory.slots) and inventory.slots[i]:
                item_stack = inventory.slots[i]
                self._draw_item_icon(screen, item_stack, slot_rect)

    def _draw_item_icon(
        self, screen: pygame.Surface, item_stack, slot_rect: pygame.Rect
    ) -> None:
        """繪製物品圖示"""
        # 根據物品類型選擇顏色
        item_colors = {
            ItemType.RESOURCE: (139, 69, 19),  # 棕色
            ItemType.CONSUMABLE: (255, 140, 0),  # 橙色
            ItemType.EQUIPMENT: (192, 192, 192),  # 銀色
            ItemType.VALUABLE: (255, 215, 0),  # 金色
            ItemType.TOOL: (100, 150, 255),  # 藍色
            ItemType.BUILDING: (128, 128, 128),  # 灰色
        }

        item_color = item_colors.get(item_stack.item.item_type, COLORS["TEXT"])

        # 繪製物品圖示 (簡單的圓形)
        center = (slot_rect.centerx, slot_rect.centery)
        pygame.draw.circle(screen, item_color, center, 12)

        # 繪製數量
        if item_stack.quantity > 1:
            qty_text = f"{item_stack.quantity}"
            self.draw_text(
                screen,
                qty_text,
                slot_rect.right - 15,
                slot_rect.bottom - 15,
                COLORS["TEXT"],
                "small",
            )

    def _draw_inventory_stats(
        self,
        screen: pygame.Surface,
        inventory: Inventory,
        inv_x: int,
        inv_y: int,
        inv_height: int,
    ) -> None:
        """繪製物品統計"""
        info_y = inv_y + inv_height - 80
        self.draw_text(screen, "物品統計:", inv_x + 30, info_y, COLORS["TEXT"], "small")

        # 統計各類物品數量
        item_counts = {}
        for slot in inventory.slots:
            if slot:
                item_id = slot.item.id
                item_counts[item_id] = item_counts.get(item_id, 0) + slot.quantity

        # 顯示重要物品數量
        important_items = {
            "wood": "木材",
            "stone": "石頭",
            "food": "食物",
            "iron_ore": "鐵礦",
            "iron_ingot": "鐵錠",
        }

        y_offset = info_y + 20
        items_per_row = 3
        item_count = 0

        for item_id, chinese_name in important_items.items():
            if item_id in item_counts:
                count = item_counts[item_id]
                text = f"{chinese_name}: {count}"

                x_offset = inv_x + 30 + (item_count % items_per_row) * 120
                row_offset = (item_count // items_per_row) * 20

                self.draw_text(
                    screen,
                    text,
                    x_offset,
                    y_offset + row_offset,
                    COLORS["TEXT_SECONDARY"],
                    "small",
                )
                item_count += 1

    def draw_crafting_interface(
        self, screen: pygame.Surface, player: "Player", world_manager=None
    ) -> None:
        """繪製製作介面"""
        craft_width = 500
        craft_height = 400
        craft_x = (WINDOW_CONFIG["width"] - craft_width) // 2
        craft_y = (WINDOW_CONFIG["height"] - craft_height) // 2

        bg_rect = pygame.Rect(craft_x, craft_y, craft_width, craft_height)
        pygame.draw.rect(screen, COLORS["UI_PANEL"], bg_rect)
        pygame.draw.rect(screen, COLORS["UI_BORDER"], bg_rect, 3)

        # 標題
        self.draw_centered_text(
            screen,
            "製作介面 - 基礎製作",
            craft_x + craft_width // 2,
            craft_y + 25,
            COLORS["TEXT"],
            "large",
        )

        # 顯示可製作的配方
        recipes = {
            "workbench": {"materials": {"wood": 4}, "name": "工作臺", "basic": True},
            "axe": {
                "materials": {"wood": 3, "stone": 2},
                "name": "斧頭",
                "basic": False,
            },
            "pickaxe": {
                "materials": {"wood": 2, "stone": 3},
                "name": "稿子",
                "basic": False,
            },
            "bucket": {
                "materials": {"wood": 4, "stone": 1},
                "name": "木桶",
                "basic": False,
            },
            "furnace": {"materials": {"stone": 8}, "name": "熔爐", "basic": False},
        }

        y_offset = craft_y + 70
        recipe_order = ["axe", "pickaxe", "bucket", "workbench", "furnace"]

        for i, item_id in enumerate(recipe_order):
            recipe_data = recipes[item_id]

            # 檢查是否可以製作
            can_craft = all(
                player.inventory.has_item(mat, amount)
                for mat, amount in recipe_data["materials"].items()
            )

            # 基礎製作 vs 高級製作
            if recipe_data["basic"]:
                color = COLORS["SUCCESS"] if can_craft else COLORS["TEXT_SECONDARY"]
                craft_type = " (基礎)"
            else:
                # 檢查是否靠近工作台
                has_workbench = self._player_near_workbench(player, world_manager)
                if has_workbench and can_craft:
                    color = COLORS["SUCCESS"]
                    craft_type = " (高級)"
                elif has_workbench:
                    color = COLORS["WARNING"]
                    craft_type = " (高級-缺材料)"
                else:
                    color = COLORS["TEXT_SECONDARY"]
                    craft_type = " (需工作台)"

            # 配方名稱
            recipe_text = f"{i+1}. {recipe_data['name']}{craft_type}"
            self.draw_text(screen, recipe_text, craft_x + 30, y_offset, color, "medium")

            # 材料需求
            materials_text = " | ".join(
                [f"{mat}:{amount}" for mat, amount in recipe_data["materials"].items()]
            )
            self.draw_text(
                screen, materials_text, craft_x + 30, y_offset + 25, color, "small"
            )

            y_offset += 60

        # 操作說明
        self.draw_text(
            screen,
            "按對應數字鍵製作物品，ESC退出",
            craft_x + 30,
            craft_y + craft_height - 30,
            COLORS["WARNING"],
            "small",
        )

    def _player_near_workbench(self, player: "Player", world_manager=None) -> bool:
        """檢查玩家是否靠近工作台（UI用）"""
        if world_manager is None:
            return False

        from ..world.world_objects import Workbench

        center_x = player.x + player.width // 2
        center_y = player.y + player.height // 2

        # 檢查世界中的工作台
        workbenches = world_manager.get_objects_by_type(Workbench)
        for workbench in workbenches:
            distance = (
                (workbench.x - center_x) ** 2 + (workbench.y - center_y) ** 2
            ) ** 0.5
            if distance <= 80:  # 80像素範圍內
                return True

        return False

    def draw_smelting_interface(self, screen: pygame.Surface, player: "Player") -> None:
        """繪製燒製介面"""
        craft_width = 400
        craft_height = 250
        craft_x = (WINDOW_CONFIG["width"] - craft_width) // 2
        craft_y = (WINDOW_CONFIG["height"] - craft_height) // 2

        bg_rect = pygame.Rect(craft_x, craft_y, craft_width, craft_height)
        pygame.draw.rect(screen, COLORS["UI_PANEL"], bg_rect)
        pygame.draw.rect(screen, COLORS["UI_BORDER"], bg_rect, 3)

        # 標題
        self.draw_centered_text(
            screen,
            "熔爐 - 燒製",
            craft_x + craft_width // 2,
            craft_y + 25,
            COLORS["TEXT"],
            "large",
        )

        # 燒製配方
        smelting_recipes = {
            "iron_ingot": {"material": "iron_ore", "name": "鐵錠", "fuel": "煤炭/木材"},
        }

        y_offset = craft_y + 70
        for i, (item_id, recipe_data) in enumerate(smelting_recipes.items()):
            has_material = player.inventory.has_item(recipe_data["material"], 1)
            has_fuel = player.inventory.has_item(
                "coal", 1
            ) or player.inventory.has_item("wood", 1)
            can_smelt = has_material and has_fuel

            color = COLORS["SUCCESS"] if can_smelt else COLORS["TEXT_SECONDARY"]

            recipe_text = (
                f"{i+1}. {recipe_data['name']} "
                f"(需要: {recipe_data['material']} + {recipe_data['fuel']})"
            )
            self.draw_text(screen, recipe_text, craft_x + 30, y_offset, color, "medium")

            y_offset += 40

        # 操作說明
        self.draw_text(
            screen,
            "按對應數字鍵燒製物品，ESC退出",
            craft_x + 30,
            craft_y + craft_height - 30,
            COLORS["WARNING"],
            "small",
        )
