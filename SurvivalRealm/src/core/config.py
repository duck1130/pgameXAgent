"""
🎮 Survival Realm - 遊戲配置檔案
統一管理所有遊戲參數和常數

作者: 硬漢貓咪開發團隊 🐱
日期: 2025-07-30
版本: 3.1.0 (重構版本)
"""

from enum import Enum
from typing import Dict, Tuple

# ====== 視窗配置參數 ======

WINDOW_CONFIG = {
    "width": 1280,
    "height": 720,
    "title": "Survival Realm - 生存領域",
    "fps": 60,
}

# ====== 顏色定義 ======

COLORS = {
    # 主要系統顏色
    "PRIMARY": (57, 255, 20),  # 生命綠
    "DANGER": (255, 50, 50),  # 血紅
    "WARNING": (255, 165, 0),  # 橙色
    "INFO": (100, 150, 255),  # 天藍
    "SUCCESS": (46, 204, 113),  # 成功綠
    # 背景和UI顏色
    "BACKGROUND": (40, 40, 40),  # 深灰背景
    "UI_PANEL": (60, 60, 60),  # UI面板色
    "UI_BORDER": (100, 100, 100),  # UI邊框色
    # 文字顏色
    "TEXT": (255, 255, 255),  # 白色文字
    "TEXT_DARK": (0, 0, 0),  # 深色文字
    "TEXT_SECONDARY": (200, 200, 200),  # 次要文字
    # 生存狀態顏色
    "HEALTH": (220, 20, 60),  # 生命值色
    "HUNGER": (255, 140, 0),  # 飢餓度色
    "THIRST": (0, 191, 255),  # 口渴度色
    "ENERGY": (255, 215, 0),  # 體力值色
    "SANITY": (138, 43, 226),  # 精神值色
}

# ====== 玩家配置 ======

PLAYER_CONFIG = {
    "speed": 200,  # 像素/秒
    "size": (32, 32),  # 玩家尺寸
    "start_pos": (640, 360),  # 初始位置
    "interaction_range": 50,  # 互動範圍
    "interaction_cooldown": 0.5,  # 互動冷卻時間
}

# ====== 生存狀態參數 ======

SURVIVAL_STATS = {
    "health": {"max": 100, "regen_rate": 0.1, "current": 100},  # 每秒恢復速率
    "hunger": {"max": 100, "decay_rate": 0.2, "current": 100},  # 每秒減少速率
    "thirst": {"max": 100, "decay_rate": 0.3, "current": 100},  # 每秒減少速率
    "energy": {"max": 100, "regen_rate": 0.15, "current": 100},  # 每秒恢復速率
    "sanity": {"max": 100, "decay_rate": 0.05, "current": 100},  # 每秒減少速率
}

# ====== 遊戲狀態枚舉 ======


class GameState(Enum):
    """遊戲狀態管理"""

    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    INVENTORY = "inventory"
    CRAFTING = "crafting"
    SMELTING = "smelting"
    GAME_OVER = "game_over"


class TimeOfDay(Enum):
    """日夜循環狀態"""

    DAWN = "dawn"  # 黎明 05:00-07:00
    DAY = "day"  # 白天 07:00-17:00
    DUSK = "dusk"  # 黃昏 17:00-19:00
    NIGHT = "night"  # 夜晚 19:00-05:00


# ====== 物品系統配置 ======


class ItemType(Enum):
    """物品類型枚舉"""

    RESOURCE = "resource"
    CONSUMABLE = "consumable"
    EQUIPMENT = "equipment"
    VALUABLE = "valuable"
    TOOL = "tool"
    BUILDING = "building"


# ====== 工具效率設定 ======

TOOL_EFFICIENCY = {
    "hand": 1.0,  # 徒手效率
    "axe": 3.0,  # 斧頭砍樹效率
    "pickaxe": 2.5,  # 稿子挖石效率
}

# ====== 製作配方 ======

ITEM_RECIPES = {
    # 基礎工具
    "axe": {"wood": 3, "stone": 2},
    "pickaxe": {"wood": 2, "stone": 3},
    "bucket": {"wood": 4, "stone": 1},
    # 建築物
    "workbench": {"wood": 4},
    "furnace": {"stone": 8},
    # 高級物品 (需要熔爐)
    "iron_ingot": {"iron_ore": 1},
    "iron_sword": {"iron_ingot": 2, "wood": 1},
    "iron_armor": {"iron_ingot": 5},
}

# ====== 礦物生成機率 ======

MINING_CHANCES = {
    "iron_ore": 0.3,  # 30% 機率挖到鐵礦
    "coal": 0.4,  # 40% 機率挖到煤炭
    "rare_gem": 0.05,  # 5% 機率挖到稀有寶石
}

# ====== 世界物件配置 ======

WORLD_OBJECTS = {
    "tree": {"spawn_rate": 0.3, "color": (34, 139, 34), "size": (40, 60), "health": 3},
    "rock": {
        "spawn_rate": 0.2,
        "color": (105, 105, 105),
        "size": (30, 30),
        "health": 2,
    },
    "cave": {"spawn_rate": 0.05, "color": (64, 64, 64), "size": (80, 60)},
    "chest": {"spawn_rate": 0.08, "color": (218, 165, 32), "size": (35, 25)},
    "food": {"spawn_rate": 0.15, "color": (255, 0, 255), "size": (20, 20)},
    "monster": {
        "spawn_rate": 0.15,  # 增加怪物生成機率來測試回合制系統
        "color": (139, 0, 0),
        "size": (35, 35),
        "health": 3,
        "damage": 10,
        "attack_cooldown": 2.0,
    },
    "river": {"spawn_rate": 0.05, "color": (0, 119, 190), "size": (120, 60)},
    "iron_ore": {"spawn_rate": 0.05, "color": (139, 69, 19), "size": (25, 25)},
}

# ====== 世界生成參數 ======

WORLD_CONFIG = {
    "initial_objects": 50,  # 初始物件數量
    "max_objects": 60,  # 最大物件數量
    "spawn_interval": 5.0,  # 生成間隔(秒)
    "safe_zone_radius": 60,  # 玩家周圍安全區域
}

# ====== 時間系統配置 ======

TIME_CONFIG = {
    "time_scale": 1.0,  # 時間倍率 (實時)
    "day_length": 600,  # 一天長度(實際秒) = 10分鐘 (早上5分鐘 + 晚上5分鐘)
}

# ====== UI 配置 ======

import platform


# 根據操作系統選擇字體路徑
def get_font_config():
    """獲取操作系統相應的字體配置"""
    system = platform.system()

    if system == "Windows":
        return {
            "font_path": "C:/Windows/Fonts/msjh.ttc",  # 微軟正黑體
            "font_fallback": [
                "C:/Windows/Fonts/simhei.ttf",  # 黑體
                "C:/Windows/Fonts/simsun.ttc",  # 宋體
                None,  # 系統預設
            ],
        }
    elif system == "Darwin":  # macOS
        return {
            "font_path": "/System/Library/Fonts/PingFang.ttc",  # 蘋方字體（最佳中文字體）
            "font_fallback": [
                "/System/Library/Fonts/Hiragino Sans GB.ttc",  # 冬青黑體簡體中文
                "/System/Library/Fonts/STHeiti Light.ttc",  # 華文黑體
                "/System/Library/Fonts/Supplemental/Songti.ttc",  # 宋體
                "/Library/Fonts/Arial Unicode MS.ttf",  # Arial Unicode MS
                "/System/Library/Fonts/Helvetica.ttc",  # 系統字體
                None,  # 系統預設
            ],
        }
    else:  # Linux 和其他系統
        return {
            "font_path": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "font_fallback": [
                "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # 文泉驛正黑
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # 文泉驛微米黑
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                None,  # 系統預設
            ],
        }


# 獲取字體配置
_font_config = get_font_config()

UI_CONFIG = {
    "font_size": {"large": 24, "medium": 18, "small": 14},
    "font_path": _font_config["font_path"],
    "font_fallback": _font_config["font_fallback"],
    "message_duration": 3.0,  # 訊息顯示時間
    "max_messages": 5,  # 最大訊息數量
    "inventory_size": 20,  # 物品欄大小
}

# ====== 音效配置 ======

AUDIO_CONFIG = {
    "master_volume": 0.7,
    "sfx_volume": 0.8,
    "music_volume": 0.5,
    "sound_files": {
        "interact": "interact.wav",
        "craft": "craft.wav",
        "attack": "attack.wav",
        "pickup": "pickup.wav",
    },
}

# ====== 音樂配置 ======

MUSIC_CONFIG = {
    "music_files": {
        "main_theme": "assets/music/minecraft_background.wav",  # C418 Minecraft 音樂
        "menu_theme": "assets/music/minecraft_background.wav",  # 主選單音樂
        "night_theme": "assets/music/minecraft_night.wav",  # 夜間音樂
        "background_music": "assets/music/minecraft_background.wav",  # 預設背景音樂
    },
    "volume": {
        "master": 0.7,
        "music": 0.4,  # 降低預設音量
        "sfx": 0.8,
    },
    "fade_duration": 1000,  # 淡入淡出時間(毫秒)
    "loop": True,  # 是否循環播放
}
