"""
Survival Realm - 使用者介面系統
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
        print("載入: 開始載入字體...")
        self.fonts = self._load_fonts()  # 將返回的字體字典賦值給self.fonts
        self.crafting_scroll_offset = 0  # 製作界面滾輪偏移量
        print("UI系統初始化完成！")

    def _get_all_recipes(self):
        """獲取所有配方的統一列表，用於滾輪計算"""
        recipe_categories = {
            "基礎工具": {
                "axe": {
                    "materials": {"wood": 3, "stone": 2},
                    "name": "斧頭",
                    "desc": "砍伐樹木的利器",
                },
                "pickaxe": {
                    "materials": {"wood": 2, "stone": 3},
                    "name": "稿子",
                    "desc": "挖掘石頭和礦物",
                },
                "bucket": {
                    "materials": {"wood": 4, "stone": 1},
                    "name": "木桶",
                    "desc": "更有效地飲用河水",
                },
                "torch": {
                    "materials": {"wood": 1, "coal": 1},
                    "name": "火把",
                    "desc": "照亮黑暗的洞穴",
                },
            },
            "建築設施": {
                "workbench": {
                    "materials": {"wood": 4},
                    "name": "工作台",
                    "desc": "製作高級物品必需",
                },
                "furnace": {
                    "materials": {"stone": 8},
                    "name": "熔爐",
                    "desc": "燒製礦物成錠",
                },
            },
            "戰鬥裝備": {
                "iron_sword": {
                    "materials": {"iron_ingot": 2, "wood": 1},
                    "name": "鐵劍",
                    "desc": "強力的戰鬥武器",
                },
                "iron_armor": {
                    "materials": {"iron_ingot": 5},
                    "name": "鐵甲",
                    "desc": "抵禦怪物攻擊",
                },
            },
        }

        all_recipes = []
        for category_name, recipes in recipe_categories.items():
            for item_id, recipe_data in recipes.items():
                all_recipes.append((category_name, item_id, recipe_data))
        return all_recipes

    def _load_fonts(self) -> dict:
        """載入字體，針對不同操作系統優化 - 智能中文字體選擇"""
        fonts = {}
        font_sizes = UI_CONFIG["font_size"]

        # 主字體路徑
        font_path = UI_CONFIG["font_path"]
        fallback_paths = UI_CONFIG["font_fallback"]

        print("載入: 開始載入字體...")
        print(f"檢測到系統: {self._get_system_name()}")

        # 檢查系統可用字體
        self._check_system_fonts()

        # 智能選擇最佳中文字體
        best_font_path = self._find_best_chinese_font([font_path] + fallback_paths)

        for size_name, size in font_sizes.items():
            font_loaded = False
            loaded_font_info = ""

            # 嘗試最佳字體
            if best_font_path:
                try:
                    if best_font_path is None:
                        fonts[size_name] = pygame.font.Font(None, size)
                        loaded_font_info = "系統預設字體"
                    else:
                        fonts[size_name] = pygame.font.Font(best_font_path, size)
                        loaded_font_info = f"最佳字體: {best_font_path}"

                    font_loaded = True
                    if size_name == "large":  # 只打印一次
                        print(f"{loaded_font_info}")
                except (FileNotFoundError, OSError) as e:
                    if size_name == "large":
                        print(f"最佳字體載入失敗: {best_font_path}")

            # 如果最佳字體失敗，嘗試所有備用字體
            if not font_loaded:
                for i, fallback_path in enumerate([font_path] + fallback_paths):
                    try:
                        if fallback_path is None:
                            fonts[size_name] = pygame.font.Font(None, size)
                            loaded_font_info = "系統預設字體"
                        else:
                            fonts[size_name] = pygame.font.Font(fallback_path, size)
                            loaded_font_info = f"備用字體 {i+1}: {fallback_path}"

                        font_loaded = True
                        if size_name == "large":
                            print(f"{loaded_font_info}")
                        break
                    except (FileNotFoundError, OSError):
                        if size_name == "large":
                            print(f"備用字體 {i+1} 載入失敗: {fallback_path}")
                        continue

            # 如果都失敗，使用系統預設
            if not font_loaded:
                fonts[size_name] = pygame.font.Font(None, size)
                if size_name == "large":
                    print("警告: 所有字體都載入失敗，使用系統預設字體")
                    print("💡 建議安裝支援中文的字體以獲得更好的顯示效果")

        # 測試中文字符顯示
        self._test_chinese_font_support(fonts["medium"])

        return fonts

    def _find_best_chinese_font(self, font_paths: list) -> str:
        """智能選擇最適合的中文字體"""
        import os

        print("載入: 智能選擇最佳中文字體...")

        # 字體優先級（基於中文顯示效果）
        font_priority = {
            # macOS 字體
            "/System/Library/Fonts/Hiragino Sans GB.ttc": 95,  # 冬青黑體簡體 - 最佳
            "/System/Library/Fonts/PingFang.ttc": 90,  # 蘋方 - 優秀
            "/System/Library/Fonts/STHeiti Light.ttc": 85,  # 華文黑體 - 良好
            "/System/Library/Fonts/Supplemental/Songti.ttc": 80,  # 宋體 - 可用
            # Windows 字體
            "C:/Windows/Fonts/msjh.ttc": 95,  # 微軟正黑體 - 最佳
            "C:/Windows/Fonts/msyh.ttc": 90,  # 微軟雅黑 - 優秀
            "C:/Windows/Fonts/simhei.ttf": 85,  # 黑體 - 良好
            "C:/Windows/Fonts/simsun.ttc": 70,  # 宋體 - 可用
            # Linux 字體
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc": 90,  # 文泉驛正黑 - 優秀
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc": 85,  # 文泉驛微米黑 - 良好
        }

        best_font = None
        best_score = 0

        for font_path in font_paths:
            if font_path is None:
                continue

            if os.path.exists(font_path):
                score = font_priority.get(font_path, 50)  # 預設分數 50
                print(f"發現字體: {font_path} (評分: {score})")

                if score > best_score:
                    best_score = score
                    best_font = font_path
            else:
                print(f"字體不存在: {font_path}")

        if best_font:
            print(f"最佳: 選擇最佳字體: {best_font} (評分: {best_score})")
        else:
            print("警告: 未找到合適的中文字體，將使用系統預設")
            best_font = None

        return best_font

    def _check_system_fonts(self) -> None:
        """檢查系統可用字體（所有系統）"""
        import platform
        import os

        system = platform.system()
        print(f"檢查: 檢查 {system} 系統字體...")

        if system == "Darwin":  # macOS
            # macOS 常見中文字體路徑
            common_fonts = [
                ("/System/Library/Fonts/Hiragino Sans GB.ttc", "冬青黑體簡體"),
                ("/System/Library/Fonts/PingFang.ttc", "蘋方"),
                ("/System/Library/Fonts/STHeiti Light.ttc", "華文黑體"),
                ("/System/Library/Fonts/Supplemental/Songti.ttc", "宋體"),
                ("/System/Library/Fonts/Supplemental/STSong.ttf", "華文宋體"),
                ("/System/Library/Fonts/Supplemental/Kaiti.ttc", "楷體"),
                ("/Library/Fonts/Arial Unicode MS.ttf", "Arial Unicode MS"),
            ]
        elif system == "Windows":  # Windows
            common_fonts = [
                ("C:/Windows/Fonts/msjh.ttc", "微軟正黑體"),
                ("C:/Windows/Fonts/msyh.ttc", "微軟雅黑"),
                ("C:/Windows/Fonts/simhei.ttf", "黑體"),
                ("C:/Windows/Fonts/simsun.ttc", "宋體"),
                ("C:/Windows/Fonts/mingliu.ttc", "細明體"),
            ]
        else:  # Linux
            common_fonts = [
                ("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", "文泉驛正黑"),
                ("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", "文泉驛微米黑"),
                ("/usr/share/fonts/truetype/arphic/uming.ttc", "AR PL UMing"),
                ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVu Sans"),
            ]

        available_fonts = []
        for font_path, font_name in common_fonts:
            if os.path.exists(font_path):
                available_fonts.append(font_name)
                print(f"發現字體: {font_name} ({font_path})")
            else:
                print(f"未發現: {font_name} ({font_path})")

        if available_fonts:
            print(f"共發現 {len(available_fonts)} 個中文字體")
        else:
            print("警告: 未發現專用中文字體，將使用系統預設字體")
            print("💡 建議安裝中文字體以獲得更好的顯示效果")

    def _get_system_name(self) -> str:
        """獲取系統名稱"""
        import platform

        system = platform.system()

        system_names = {"Darwin": "macOS", "Windows": "Windows", "Linux": "Linux"}

        return system_names.get(system, system)

    def _test_chinese_font_support(self, font) -> None:
        """測試字體對中文的支援程度 - 增強版"""
        test_chars = [
            ("你好", "基本中文"),
            ("遊戲", "繁體中文"),
            ("生存", "簡體中文"),
            ("製作", "製作相關"),
            ("物品欄", "介面文字"),
            ("", "表情符號"),
            ("", "工具符號"),
            ("武器", "武器符號"),
        ]

        print("測試: 測試中文字體支援...")
        successful_renders = 0

        for char_test, description in test_chars:
            try:
                # 嘗試渲染測試字符
                test_surface = font.render(char_test, True, (255, 255, 255))
                # 如果渲染成功且有實際內容
                if test_surface.get_width() > 0 and test_surface.get_height() > 0:
                    print(f"{description} '{char_test}' 支援良好")
                    successful_renders += 1
                else:
                    print(f"警告: {description} '{char_test}' 可能顯示為方框")
            except Exception as e:
                print(f"{description} '{char_test}' 渲染失敗: {e}")

        # 計算支援率
        support_rate = (successful_renders / len(test_chars)) * 100
        print(
            f"字體中文支援率: {support_rate:.1f}% ({successful_renders}/{len(test_chars)})"
        )

        if support_rate >= 90:
            print("字體中文支援優秀！")
        elif support_rate >= 70:
            print("良好: 字體中文支援良好")
        elif support_rate >= 50:
            print("警告: 字體中文支援一般，部分文字可能顯示異常")
        else:
            print("字體中文支援較差，建議檢查字體配置")

        print("字體測試完成！")

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
        """繪製支持滾輪的製作介面 - 垂直列表佈局"""
        craft_width = 720
        craft_height = 600
        craft_x = (WINDOW_CONFIG["width"] - craft_width) // 2
        craft_y = (WINDOW_CONFIG["height"] - craft_height) // 2

        # 主背景
        bg_rect = pygame.Rect(craft_x, craft_y, craft_width, craft_height)
        pygame.draw.rect(screen, COLORS["UI_PANEL"], bg_rect)
        pygame.draw.rect(screen, COLORS["UI_BORDER"], bg_rect, 3)

        # 標題區域
        title_rect = pygame.Rect(craft_x, craft_y, craft_width, 60)
        pygame.draw.rect(screen, COLORS["INFO"], title_rect)
        pygame.draw.rect(screen, COLORS["UI_BORDER"], title_rect, 3)

        # 標題文字
        self.draw_centered_text(
            screen,
            "製作工坊",
            craft_x + craft_width // 2,
            craft_y + 30,
            (255, 255, 255),
            "large",
        )

        # 配方資料
        recipe_categories = {
            "基礎工具": {
                "axe": {
                    "materials": {"wood": 3, "stone": 2},
                    "name": "斧頭",
                    "desc": "砍伐樹木的利器",
                },
                "pickaxe": {
                    "materials": {"wood": 2, "stone": 3},
                    "name": "稿子",
                    "desc": "挖掘石頭和礦物",
                },
                "bucket": {
                    "materials": {"wood": 4, "stone": 1},
                    "name": "木桶",
                    "desc": "更有效地飲用河水",
                },
                "torch": {
                    "materials": {"wood": 1, "coal": 1},
                    "name": "火把",
                    "desc": "照亮黑暗的洞穴",
                },
            },
            "建築設施": {
                "workbench": {
                    "materials": {"wood": 4},
                    "name": "工作台",
                    "desc": "製作高級物品必需",
                },
                "furnace": {
                    "materials": {"stone": 8},
                    "name": "熔爐",
                    "desc": "燒製礦物成錠",
                },
            },
            "戰鬥裝備": {
                "iron_sword": {
                    "materials": {"iron_ingot": 2, "wood": 1},
                    "name": "鐵劍",
                    "desc": "強力的戰鬥武器",
                },
                "iron_armor": {
                    "materials": {"iron_ingot": 5},
                    "name": "鐵甲",
                    "desc": "抵禦怪物攻擊",
                },
            },
        }

        # 檢查工作台
        has_workbench = self._player_near_workbench(player, world_manager)

        # 內容區域設定
        content_area = pygame.Rect(
            craft_x + 10, craft_y + 70, craft_width - 20, craft_height - 140
        )

        # 計算總內容高度
        total_items = sum(len(recipes) for recipes in recipe_categories.values()) + len(
            recipe_categories
        )
        total_content_height = total_items * 110  # 每個物品 100px + 間距 10px

        # 限制滾輪範圍
        max_scroll = max(0, total_content_height - content_area.height)
        self.crafting_scroll_offset = max(
            0, min(self.crafting_scroll_offset, max_scroll)
        )

        # 設置裁剪區域
        screen.set_clip(content_area)

        # 繪製內容
        current_y = content_area.y - self.crafting_scroll_offset
        recipe_index = 1

        for category_name, recipes in recipe_categories.items():
            # 分類標題
            if current_y > content_area.y - 40 and current_y < content_area.bottom + 40:
                category_rect = pygame.Rect(
                    content_area.x, current_y, content_area.width, 30
                )
                category_color = (
                    COLORS["SUCCESS"]
                    if category_name == "基礎工具"
                    else (
                        COLORS["INFO"]
                        if category_name == "建築設施"
                        else COLORS["WARNING"]
                    )
                )
                pygame.draw.rect(screen, category_color, category_rect)
                pygame.draw.rect(screen, COLORS["UI_BORDER"], category_rect, 2)

                self.draw_centered_text(
                    screen,
                    category_name,
                    content_area.x + content_area.width // 2,
                    current_y + 15,
                    (255, 255, 255),
                    "medium",
                )

            current_y += 40

            # 繪製配方
            for item_id, recipe_data in recipes.items():
                if recipe_index > 8:
                    break

                # 只繪製可見區域的物品
                if current_y + 100 > content_area.y and current_y < content_area.bottom:
                    # 製作條件檢查
                    can_craft_materials = all(
                        player.inventory.has_item(mat, amount)
                        for mat, amount in recipe_data["materials"].items()
                    )

                    is_basic_craft = (
                        item_id in ["workbench"] or category_name == "基礎工具"
                    )
                    can_craft_location = is_basic_craft or has_workbench
                    can_craft = can_craft_materials and can_craft_location

                    # 物品背景
                    item_rect = pygame.Rect(
                        content_area.x, current_y, content_area.width, 100
                    )

                    if can_craft:
                        bg_color = (*COLORS["SUCCESS"], 60)
                        border_color = COLORS["SUCCESS"]
                    elif can_craft_materials and not can_craft_location:
                        bg_color = (*COLORS["WARNING"], 60)
                        border_color = COLORS["WARNING"]
                    else:
                        bg_color = (*COLORS["TEXT_SECONDARY"], 40)
                        border_color = COLORS["TEXT_SECONDARY"]

                    pygame.draw.rect(screen, bg_color, item_rect)
                    pygame.draw.rect(screen, border_color, item_rect, 2)

                    # 數字標籤
                    circle_x = content_area.x + 30
                    circle_y = current_y + 20
                    pygame.draw.circle(
                        screen, (255, 255, 255), (circle_x, circle_y), 15
                    )
                    pygame.draw.circle(
                        screen, COLORS["INFO"], (circle_x, circle_y), 15, 2
                    )
                    self.draw_centered_text(
                        screen,
                        str(recipe_index),
                        circle_x,
                        circle_y,
                        (0, 0, 0),
                        "medium",
                    )

                    # 物品名稱 - 改為黑色以提高可讀性
                    name_color = (0, 0, 0)  # 統一使用黑色，在任何背景下都清晰可見
                    self.draw_text(
                        screen,
                        recipe_data["name"],
                        content_area.x + 60,
                        current_y + 10,
                        name_color,
                        "large",
                    )

                    # 物品描述
                    self.draw_text(
                        screen,
                        recipe_data["desc"],
                        content_area.x + 60,
                        current_y + 35,
                        (220, 220, 220),
                        "medium",
                    )

                    # 材料需求 - 智能截斷以適應窗口
                    materials_parts = []
                    for mat, amount in recipe_data["materials"].items():
                        owned = player.inventory.get_item_count(mat)
                        part = f"{mat}×{amount}"
                        if owned < amount:
                            part += f"({owned})"
                        materials_parts.append(part)

                    materials_text = "需要: " + ", ".join(materials_parts)

                    # 確保文字不超出窗口寬度
                    if len(materials_text) > 45:  # 如果太長就截斷
                        materials_text = materials_text[:42] + "..."

                    self.draw_text(
                        screen,
                        materials_text,
                        content_area.x + 60,
                        current_y + 55,
                        (255, 255, 255),
                        "medium",
                    )

                    # 製作狀態
                    if not is_basic_craft and not has_workbench:
                        self.draw_text(
                            screen,
                            "需要靠近工作台",
                            content_area.x + 60,
                            current_y + 75,
                            (255, 50, 50),
                            "medium",
                        )
                    elif can_craft:
                        self.draw_text(
                            screen,
                            f"按 {recipe_index} 鍵製作",
                            content_area.x + 60,
                            current_y + 75,
                            (50, 255, 50),
                            "medium",
                        )
                    elif not can_craft_materials:
                        self.draw_text(
                            screen,
                            "材料不足",
                            content_area.x + 60,
                            current_y + 75,
                            (255, 100, 100),
                            "medium",
                        )

                current_y += 110
                recipe_index += 1

        # 移除裁剪
        screen.set_clip(None)

        # 滾輪提示
        if max_scroll > 0:
            scroll_text = (
                f"使用滾輪查看更多 ({self.crafting_scroll_offset}/{max_scroll})"
            )
            self.draw_centered_text(
                screen,
                scroll_text,
                craft_x + craft_width // 2,
                craft_y + craft_height - 50,
                (150, 150, 150),
                "small",
            )

        # 底部資訊
        info_y = craft_y + craft_height - 30
        self.draw_text(
            screen,
            "按數字鍵 1-8 製作 | ESC 退出",
            craft_x + 20,
            info_y,
            (255, 255, 100),
            "medium",
        )

        status_text = "工作台可用" if has_workbench else "需要工作台製作高級物品"
        status_color = (100, 255, 100) if has_workbench else (255, 150, 50)
        self.draw_text(
            screen, status_text, craft_x + 400, info_y, status_color, "medium"
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
