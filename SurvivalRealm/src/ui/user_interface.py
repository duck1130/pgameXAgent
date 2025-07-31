"""
🎮 Survival Realm - 使用者介面系統
處理所有UI繪製和顯示

作者: 硬漢貓咪開發團隊 🐱
日期: 2025-07-30
版本: 3.1.0 (重構版本)
"""

import pygame
import time
from typing import List, Tuple, TYPE_CHECKING

from ..core.config import WINDOW_CONFIG, COLORS, SURVIVAL_STATS, UI_CONFIG
from ..systems.inventory import Inventory, ItemType

# 避免循環引用
if TYPE_CHECKING:
    from ..entities.player import Player
    from ..systems.time_manager import TimeManager


class UI:
    """使用者介面管理類"""

    def __init__(self):
        """初始化UI系統"""
        print("🔍 開始載入字體...")
        self.fonts = self._load_fonts()  # 將返回的字體字典賦值給self.fonts
        print("✅ UI系統初始化完成！")

        # 添加滾輪狀態
        self.crafting_scroll_offset = 0  # 製作界面滾輪偏移量

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

            # 處理多行訊息
            lines = message.split("\n")

            for line in lines:
                if line.strip():  # 只繪製非空行
                    # 創建半透明表面
                    text_surface = self.fonts["small"].render(
                        line, True, COLORS["TEXT"]
                    )
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
        """繪製重新設計的製作介面 - 更清晰易懂的佈局"""
        craft_width = 720  # 稍微增加寬度
        craft_height = 600  # 增加高度以容納更明顯的文字
        craft_x = (WINDOW_CONFIG["width"] - craft_width) // 2
        craft_y = (WINDOW_CONFIG["height"] - craft_height) // 2

        # 主背景
        bg_rect = pygame.Rect(craft_x, craft_y, craft_width, craft_height)
        pygame.draw.rect(screen, COLORS["UI_PANEL"], bg_rect)
        pygame.draw.rect(screen, COLORS["UI_BORDER"], bg_rect, 3)

        # 標題區域 - 讓標題更明顯
        title_rect = pygame.Rect(craft_x, craft_y, craft_width, 60)  # 增加高度
        pygame.draw.rect(screen, COLORS["INFO"], title_rect)
        pygame.draw.rect(screen, COLORS["UI_BORDER"], title_rect, 3)  # 加粗邊框

        # 添加標題陰影效果
        self.draw_centered_text(
            screen,
            "🔨 製作工坊 🔨",
            craft_x + craft_width // 2 + 2,
            craft_y + 32,  # 陰影位置
            (0, 0, 0),  # 黑色陰影
            "large",
        )
        self.draw_centered_text(
            screen,
            "🔨 製作工坊 🔨",
            craft_x + craft_width // 2,
            craft_y + 30,
            (255, 255, 255),  # 白色文字
            "large",
        )  # 分類區域的配方，按類型分組
        recipe_categories = {
            "基礎工具": {
                "axe": {
                    "materials": {"wood": 3, "stone": 2},
                    "name": "🪓 斧頭",
                    "desc": "砍伐樹木的利器",
                },
                "pickaxe": {
                    "materials": {"wood": 2, "stone": 3},
                    "name": "⛏️ 稿子",
                    "desc": "挖掘石頭和礦物",
                },
                "bucket": {
                    "materials": {"wood": 4, "stone": 1},
                    "name": "🪣 木桶",
                    "desc": "更有效地飲用河水",
                },
            },
            "建築設施": {
                "workbench": {
                    "materials": {"wood": 4},
                    "name": "🔧 工作台",
                    "desc": "製作高級物品必需",
                },
                "furnace": {
                    "materials": {"stone": 8},
                    "name": "🔥 熔爐",
                    "desc": "燒製礦物成錠",
                },
            },
            "戰鬥裝備": {
                "iron_sword": {
                    "materials": {"iron_ingot": 2, "wood": 1},
                    "name": "⚔️ 鐵劍",
                    "desc": "強力的戰鬥武器",
                },
                "iron_armor": {
                    "materials": {"iron_ingot": 5},
                    "name": "🛡️ 鐵甲",
                    "desc": "抵禦怪物攻擊",
                },
            },
        }

        # 檢查是否靠近工作台
        has_workbench = self._player_near_workbench(player, world_manager)

        # 繪製分類和配方
        content_y = craft_y + 70  # 調整因為標題高度增加
        content_height = craft_height - 130  # 調整對應高度

        # 分為三列顯示不同類別
        col_width = (craft_width - 60) // 3  # 三列，預留邊距
        col_x_positions = [
            craft_x + 20,
            craft_x + 20 + col_width,
            craft_x + 20 + col_width * 2,
        ]

        recipe_index = 1  # 用於數字鍵映射

        for col_idx, (category_name, recipes) in enumerate(recipe_categories.items()):
            if col_idx >= 3:  # 最多三列
                break

            col_x = col_x_positions[col_idx]

            # 分類標題 - 增強視覺效果
            category_rect = pygame.Rect(
                col_x, content_y, col_width - 10, 35
            )  # 增加高度
            category_color = (
                COLORS["SUCCESS"]
                if category_name == "基礎工具"
                else (
                    COLORS["INFO"] if category_name == "建築設施" else COLORS["WARNING"]
                )
            )
            pygame.draw.rect(screen, category_color, category_rect)
            pygame.draw.rect(screen, COLORS["UI_BORDER"], category_rect, 2)  # 加粗邊框

            # 分類標題加陰影效果
            self.draw_centered_text(
                screen,
                category_name,
                col_x + (col_width - 10) // 2 + 1,
                content_y + 19,  # 陰影位置
                (0, 0, 0),  # 黑色陰影
                "medium",
            )
            self.draw_centered_text(
                screen,
                category_name,
                col_x + (col_width - 10) // 2,
                content_y + 17,
                (255, 255, 255),  # 白色文字
                "medium",
            )

            # 繪製該類別的配方
            item_y = content_y + 45  # 調整因為分類標題高度增加
            for item_id, recipe_data in recipes.items():
                if recipe_index > 7:  # 只支持1-7鍵
                    break

                # 檢查材料和製作條件
                can_craft_materials = all(
                    player.inventory.has_item(mat, amount)
                    for mat, amount in recipe_data["materials"].items()
                )

                # 基礎工具和工作台可以隨時製作，其他需要工作台
                is_basic_craft = item_id in ["workbench"] or category_name == "基礎工具"
                can_craft_location = is_basic_craft or has_workbench

                can_craft = can_craft_materials and can_craft_location

                # 配方背景 - 增強對比度
                item_rect = pygame.Rect(
                    col_x, item_y, col_width - 10, 95
                )  # 稍微增加高度
                if can_craft:
                    bg_color = (*COLORS["SUCCESS"], 60)  # 增加透明度
                    border_color = COLORS["SUCCESS"]
                elif can_craft_materials and not can_craft_location:
                    bg_color = (*COLORS["WARNING"], 60)  # 增加透明度
                    border_color = COLORS["WARNING"]
                else:
                    bg_color = (*COLORS["TEXT_SECONDARY"], 40)  # 增加透明度
                    border_color = COLORS["TEXT_SECONDARY"]

                pygame.draw.rect(screen, bg_color, item_rect)
                pygame.draw.rect(
                    screen, border_color, item_rect, 2
                )  # 加粗並使用對應顏色邊框

                # 數字標籤 - 更明顯的設計
                pygame.draw.circle(
                    screen, (255, 255, 255), (col_x + 15, item_y + 15), 12  # 增大圓圈
                )
                pygame.draw.circle(
                    screen, COLORS["INFO"], (col_x + 15, item_y + 15), 12, 2  # 彩色邊框
                )
                self.draw_centered_text(
                    screen,
                    str(recipe_index),
                    col_x + 15,
                    item_y + 15,
                    (0, 0, 0),  # 黑色數字更明顯
                    "medium",  # 增大字體
                )

                # 物品名稱 - 增強對比度和字體大小
                name_color = (
                    (0, 255, 0)  # 亮綠色
                    if can_craft
                    else (
                        (255, 255, 0)  # 亮黃色
                        if can_craft_materials
                        else (200, 200, 200)  # 亮灰色
                    )
                )
                # 添加文字陰影
                self.draw_text(
                    screen,
                    recipe_data["name"],
                    col_x + 31,
                    item_y + 6,
                    (0, 0, 0),  # 黑色陰影
                    "large",  # 增大字體
                )
                self.draw_text(
                    screen,
                    recipe_data["name"],
                    col_x + 30,
                    item_y + 5,
                    name_color,
                    "large",  # 增大字體
                )

                # 物品描述 - 增強可讀性
                self.draw_text(
                    screen,
                    recipe_data["desc"],
                    col_x + 31,
                    item_y + 29,
                    (0, 0, 0),  # 黑色陰影
                    "medium",  # 增大字體
                )
                self.draw_text(
                    screen,
                    recipe_data["desc"],
                    col_x + 30,
                    item_y + 28,
                    (220, 220, 220),  # 亮灰色文字
                    "medium",  # 增大字體
                )

                # 材料需求 - 更明顯的顯示
                materials_y = item_y + 52  # 調整位置
                materials_text = "需要: "
                for i, (mat, amount) in enumerate(recipe_data["materials"].items()):
                    if i > 0:
                        materials_text += ", "
                    owned = player.inventory.get_item_count(mat)
                    materials_text += f"{mat}×{amount}"
                    if owned < amount:
                        materials_text += f"({owned})"

                # 材料文字加陰影
                self.draw_text(
                    screen,
                    materials_text,
                    col_x + 11,
                    materials_y + 1,
                    (0, 0, 0),  # 黑色陰影
                    "medium",  # 增大字體
                )
                self.draw_text(
                    screen,
                    materials_text,
                    col_x + 10,
                    materials_y,
                    (255, 255, 255),  # 白色文字
                    "medium",  # 增大字體
                )

                # 製作條件提示 - 更明顯的狀態顯示
                condition_y = item_y + 74  # 調整位置
                if not is_basic_craft and not has_workbench:
                    # 需要工作台 - 紅色警告
                    self.draw_text(
                        screen,
                        "⚠️ 需要靠近工作台",
                        col_x + 11,
                        condition_y + 1,
                        (0, 0, 0),  # 黑色陰影
                        "medium",
                    )
                    self.draw_text(
                        screen,
                        "⚠️ 需要靠近工作台",
                        col_x + 10,
                        condition_y,
                        (255, 50, 50),  # 亮紅色
                        "medium",
                    )
                elif can_craft:
                    # 可製作 - 亮綠色提示
                    self.draw_text(
                        screen,
                        f"✅ 按 {recipe_index} 鍵製作",
                        col_x + 11,
                        condition_y + 1,
                        (0, 0, 0),  # 黑色陰影
                        "medium",
                    )
                    self.draw_text(
                        screen,
                        f"✅ 按 {recipe_index} 鍵製作",
                        col_x + 10,
                        condition_y,
                        (50, 255, 50),  # 亮綠色
                        "medium",
                    )
                elif not can_craft_materials:
                    # 材料不足 - 紅色提示
                    self.draw_text(
                        screen,
                        "❌ 材料不足",
                        col_x + 11,
                        condition_y + 1,
                        (0, 0, 0),  # 黑色陰影
                        "medium",
                    )
                    self.draw_text(
                        screen,
                        "❌ 材料不足",
                        col_x + 10,
                        condition_y,
                        (255, 100, 100),  # 亮紅色
                        "medium",
                    )

                item_y += 105  # 調整間距以適應新的高度
                recipe_index += 1

        # 底部資訊面板 - 增強視覺效果
        info_panel_y = craft_y + craft_height - 90  # 增加高度
        info_rect = pygame.Rect(craft_x, info_panel_y, craft_width, 90)
        pygame.draw.rect(screen, COLORS["UI_PANEL"], info_rect)
        pygame.draw.rect(screen, COLORS["UI_BORDER"], info_rect, 3)  # 加粗邊框

        # 操作說明 - 更明顯的文字
        self.draw_text(
            screen,
            "🎮 操作說明: 按數字鍵 1-7 製作對應物品 | ESC 退出製作模式",
            craft_x + 21,
            info_panel_y + 16,
            (0, 0, 0),  # 黑色陰影
            "large",  # 增大字體
        )
        self.draw_text(
            screen,
            "🎮 操作說明: 按數字鍵 1-7 製作對應物品 | ESC 退出製作模式",
            craft_x + 20,
            info_panel_y + 15,
            (255, 255, 100),  # 亮黃色文字
            "large",  # 增大字體
        )

        # 狀態提示 - 更明顯的狀態顯示
        if has_workbench:
            status_text = "🔧 工作台可用 - 可製作所有物品"
            status_color = (100, 255, 100)  # 亮綠色
        else:
            status_text = "⚠️ 需要靠近工作台才能製作高級物品"
            status_color = (255, 150, 50)  # 亮橙色

        self.draw_text(
            screen,
            status_text,
            craft_x + 21,
            info_panel_y + 51,
            (0, 0, 0),  # 黑色陰影
            "large",  # 增大字體
        )
        self.draw_text(
            screen,
            status_text,
            craft_x + 20,
            info_panel_y + 50,
            status_color,
            "large",  # 增大字體
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
