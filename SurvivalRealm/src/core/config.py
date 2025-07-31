"""
🎮 Survival Realm - 遊戲配置檔案
統一管理所有遊戲參數和常數

作者: 硬漢貓咪開發團隊 🐱
日期: 2025-07-30
版本: 3.1.0 (重構版本)
"""

from enum import Enum

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
    "steel_pickaxe": 4.0,  # 鋼稿效率更高
    "diamond_pickaxe": 6.0,  # 鑽石稿效率最高
    "bucket": 1.0,  # 木桶（水相關）
}

# ====== 製作配方 ======

ITEM_RECIPES = {
    # 基礎工具
    "axe": {"wood": 3, "stone": 2},
    "pickaxe": {"wood": 2, "stone": 3},
    "bucket": {"wood": 2, "iron_ingot": 1},
    # 武器裝備
    "iron_sword": {"iron_ingot": 2, "wood": 1},
    "iron_armor": {"iron_ingot": 5},
    "steel_sword": {"steel_ingot": 2, "wood": 1},  # 新增：鋼劍
    "steel_armor": {"steel_ingot": 6},  # 新增：鋼甲
    # 建築物件
    "workbench": {"wood": 4},
    "furnace": {"stone": 8},
    "chest": {"wood": 6, "iron_ingot": 1},  # 新增：寶箱製作
    "storage_chest": {"wood": 8, "iron_ingot": 2},  # 新增：大型儲存箱
    # 探險工具
    "torch": {"wood": 1, "coal": 1},  # 新增：火把（洞穴探險用）
    "rope": {"plant_fiber": 3},  # 新增：繩索
    "cave_lamp": {"iron_ingot": 1, "coal": 2, "wood": 1},  # 新增：洞穴燈
    # 進階工具
    "steel_pickaxe": {"steel_ingot": 3, "wood": 2},  # 新增：鋼稿
    "diamond_pickaxe": {"diamond": 3, "wood": 2},  # 新增：鑽石稿
    # 防護道具
    "health_potion": {"berry": 3, "mushroom": 2},  # 新增：生命藥水
    "energy_potion": {"fruit": 2, "plant_fiber": 1},  # 新增：體力藥水
}

# ====== 燒製配方 ======

SMELTING_RECIPES = {
    "iron_ingot": {"material": "iron_ore", "fuel": ["coal", "wood"]},
    "steel_ingot": {
        "material": "iron_ingot",
        "fuel": ["coal"],
    },  # 新增：鋼錠（需要煤炭）
    "copper_ingot": {"material": "copper_ore", "fuel": ["coal", "wood"]},  # 新增：銅錠
}

# ====== 挖礦機率配置 ======

MINING_CHANCES = {
    "iron_ore": 0.3,  # 30% 機率獲得鐵礦石
    "coal": 0.4,  # 40% 機率獲得煤炭
    "copper_ore": 0.2,  # 新增：20% 機率獲得銅礦石
    "silver_ore": 0.1,  # 新增：10% 機率獲得銀礦石
    "gold_ore": 0.05,  # 新增：5% 機率獲得金礦石
    "diamond": 0.02,  # 新增：2% 機率獲得鑽石
}

# ====== 洞穴探險配置 ======

CAVE_CONFIG = {
    "min_depth": 3,  # 最小深度層數
    "max_depth": 7,  # 最大深度層數
    "room_size": {"width": 800, "height": 600},  # 洞穴房間大小
    "monster_spawn_rate": 0.5,  # 🔥 增加洞穴內怪物生成率（0.4 -> 0.5）
    "treasure_spawn_rate": 0.6,  # 💎 大幅增加寶藏生成率（0.25 -> 0.6）
    "mineral_spawn_rate": 0.9,  # ⛏️ 大幅增加礦物生成率（0.5 -> 0.9）
    "torch_duration": 300,  # 火把持續時間（秒）
    "darkness_damage": 1,  # 黑暗中每秒受到的傷害
    # 🆕 Boss戰系統配置
    "boss_per_level": True,  # 每層都有boss
    "boss_health_multiplier": 3.0,  # boss血量倍數
    "boss_damage_multiplier": 2.0,  # boss傷害倍數
    "key_drop_rate": 1.0,  # boss掉落鑰匙機率（100%）
}

# ====== 世界物件配置 ======

WORLD_OBJECTS = {
    "tree": {
        "spawn_rate": 0.4,  # 🌲 增加樹木生成率（0.3 -> 0.4）
        "color": (34, 139, 34),
        "size": (40, 60),
        "health": 5,
    },
    "rock": {
        "spawn_rate": 0.35,  # ⛰️ 增加石頭生成率（0.25 -> 0.35）
        "color": (128, 128, 128),
        "size": (30, 25),
        "health": 8,
    },
    "food": {
        "spawn_rate": 0.3,  # 🍎 增加食物生成率（0.2 -> 0.3）
        "color": (255, 140, 0),
        "size": (20, 20),
    },
    "river": {
        "spawn_rate": 0.05,  # 降低河流生成率，使其更稀少
        "color": (0, 100, 200),
        "size": (100, 60),
        "is_permanent": True,  # 新增：標記為永久物件，不會重複生成
    },
    "chest": {
        "spawn_rate": 0.08,  # 📦 增加寶箱生成率（0.03 -> 0.08）
        "color": (139, 69, 19),
        "size": (30, 25),
    },
    "cave": {
        "spawn_rate": 0.12,  # 🕳️ 增加洞穴生成率（0.08 -> 0.12）
        "color": (64, 64, 64),
        "size": (80, 60),
        "can_enter": True,  # 新增：可進入標記
    },
    "monster": {
        "spawn_rate": 0.2,  # 👹 增加怪物生成率（0.15 -> 0.2）
        "color": (139, 0, 139),
        "size": (35, 30),
        "health": 15,
        "damage": 8,
        "attack_cooldown": 2.0,
        "attack_range": 40,  # 新增：攻擊範圍
        "chase_range": 120,  # 新增：追擊範圍
        "is_aggressive": True,  # 新增：主動攻擊標記
    },
    "workbench": {
        "spawn_rate": 0.0,  # 不自動生成，需要玩家建造
        "color": (139, 69, 19),
        "size": (60, 40),
    },
    "furnace": {
        "spawn_rate": 0.0,  # 不自動生成，需要玩家建造
        "color": (105, 105, 105),
        "size": (50, 60),
    },
    # 新增洞穴內物件
    "cave_monster": {
        "spawn_rate": 0.0,  # 不在地表生成
        "color": (139, 0, 0),  # 更深的紅色
        "size": (40, 35),
        "health": 25,
        "damage": 12,
        "attack_cooldown": 1.5,
        "attack_range": 50,
        "chase_range": 150,
        "is_aggressive": True,
    },
    "cave_spider": {
        "spawn_rate": 0.0,
        "color": (64, 0, 64),  # 深紫色
        "size": (25, 20),
        "health": 8,
        "damage": 5,
        "attack_cooldown": 1.0,
        "attack_range": 30,
        "chase_range": 80,
        "is_aggressive": True,
    },
    "treasure_chest": {
        "spawn_rate": 0.0,  # 洞穴內特殊寶箱
        "color": (255, 215, 0),  # 金色
        "size": (35, 30),
    },
    # 🆕 Boss系統
    "cave_boss": {
        "spawn_rate": 0.0,  # 不自動生成，特殊生成
        "color": (200, 0, 0),  # 深紅色，比普通怪物更大更恐怖
        "size": (60, 50),  # 比普通怪物大
        "health": 75,  # 基礎血量，會根據層數調整
        "damage": 25,  # 基礎傷害，會根據層數調整
        "attack_cooldown": 1.0,  # 攻擊頻率較高
        "attack_range": 80,  # 更大的攻擊範圍
        "chase_range": 200,  # 更大的追擊範圍
        "is_aggressive": True,
        "is_boss": True,  # 標記為boss
        "experience_reward": 50,  # 擊敗後的經驗獎勵
    },
    # 🔑 深度鑰匙系統
    "depth_key": {
        "spawn_rate": 0.0,  # 只能從boss掉落
        "color": (255, 215, 0),  # 金色鑰匙
        "size": (20, 15),
        "is_key": True,  # 標記為鑰匙物品
    },
}

# ====== 世界生成參數 ======

WORLD_CONFIG = {
    "initial_objects": 100,  # 🚀 增加初始物件數量（50 -> 100）
    "max_objects": 100,  # 📈 增加最大物件數量（60 -> 100）
    "spawn_interval": 1.0,  # ⚡ 減少生成間隔，加快生成速度（5.0 -> 1.0 秒）
    "safe_zone_radius": 60,  # 玩家周圍安全區域
    "river_spawn_limit": 5,  # 新增：世界中河流的最大數量
    "permanent_objects_generated": False,  # 新增：是否已生成永久物件
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
    """獲取操作系統相應的字體配置 - 優化中文顯示"""
    system = platform.system()

    if system == "Windows":
        return {
            "font_path": "C:/Windows/Fonts/msjh.ttc",  # 微軟正黑體
            "font_fallback": [
                "C:/Windows/Fonts/simhei.ttf",  # 黑體
                "C:/Windows/Fonts/simsun.ttc",  # 宋體
                "C:/Windows/Fonts/msyh.ttc",  # 微軟雅黑
                None,  # 系統預設
            ],
        }
    elif system == "Darwin":  # macOS
        return {
            "font_path": "/System/Library/Fonts/Hiragino Sans GB.ttc",  # 🎯 冬青黑體簡體中文（最佳中文顯示）
            "font_fallback": [
                "/System/Library/Fonts/PingFang.ttc",  # 蘋方字體
                "/System/Library/Fonts/STHeiti Light.ttc",  # 華文黑體
                "/System/Library/Fonts/Supplemental/Songti.ttc",  # 宋體
                "/System/Library/Fonts/Supplemental/STSong.ttf",  # 華文宋體
                "/System/Library/Fonts/Supplemental/Kaiti.ttc",  # 楷體
                "/Library/Fonts/Arial Unicode MS.ttf",  # Arial Unicode MS
                "/System/Library/Fonts/Helvetica.ttc",  # 系統字體
                None,  # 系統預設
            ],
        }
    else:  # Linux 和其他系統
        return {
            "font_path": "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # 優先使用文泉驛正黑
            "font_fallback": [
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # 文泉驛微米黑
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
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
