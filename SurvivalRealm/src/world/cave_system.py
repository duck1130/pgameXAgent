"""
🎮 Survival Realm - 洞穴探險系統
處理洞穴內的探險、怪物戰鬥和寶藏發現

作者: 硬漢貓咪開發團隊 🐱
日期: 2025-07-31
版本: 3.1.0 (洞穴探險擴展)
"""

import pygame
import random
import math
import time
from typing import List, Dict, Optional, Tuple, TYPE_CHECKING
from dataclasses import dataclass

from .game_object import GameObject
from ..core.config import CAVE_CONFIG, WORLD_OBJECTS, WINDOW_CONFIG

# 避免循環引用
if TYPE_CHECKING:
    from ..entities.player import Player


@dataclass
class CaveRoom:
    """洞穴房間數據類 - 支援Boss戰和鑰匙機制"""

    depth: int  # 深度層級
    width: int = 800
    height: int = 600
    monsters: List[GameObject] = None
    treasures: List[GameObject] = None
    minerals: List[GameObject] = None
    boss: Optional[GameObject] = None  # 🆕 每層的Boss
    has_exit: bool = True  # 是否有出口
    darkness_level: float = 0.8  # 黑暗程度 (0.0-1.0)
    boss_defeated: bool = False  # 🆕 Boss是否已被擊敗
    has_key: bool = False  # 🆕 是否擁有進入下層的鑰匙

    def __post_init__(self):
        if self.monsters is None:
            self.monsters = []
        if self.treasures is None:
            self.treasures = []
        if self.minerals is None:
            self.minerals = []


class CaveBoss(GameObject):
    """洞穴Boss - 每層的守護者，必須擊敗才能獲得下層鑰匙"""

    def __init__(self, x: float, y: float, depth: int):
        config = WORLD_OBJECTS["cave_boss"]
        size = config["size"]
        super().__init__(x, y, size[0], size[1])

        self.depth = depth
        self.boss_type = "cave_boss"

        # 根據深度調整Boss屬性
        depth_multiplier = 1.0 + (depth - 1) * 0.5  # 每層+50%難度
        self.max_health = int(
            config["health"] * depth_multiplier * CAVE_CONFIG["boss_health_multiplier"]
        )
        self.health = self.max_health
        self.damage = int(
            config["damage"] * depth_multiplier * CAVE_CONFIG["boss_damage_multiplier"]
        )

        self.attack_range = config["attack_range"]
        self.chase_range = config["chase_range"]
        self.attack_cooldown = config["attack_cooldown"]
        self.last_attack = 0

        # Boss特殊屬性
        self.is_boss = True
        self.move_speed = 2.0  # 比普通怪物快
        self.state = "patrolling"  # patrolling, chasing, attacking, enraged
        self.enrage_threshold = 0.3  # 血量低於30%時暴怒
        self.is_enraged = False

        # Boss戰階段
        self.phase = 1  # 1: 普通, 2: 激怒, 3: 絕望

        print(f"深度{depth}層Boss出現！血量: {self.health}, 傷害: {self.damage}")

    def update(
        self,
        delta_time: float,
        player_x: float,
        player_y: float,
        player_in_darkness: bool,
    ) -> None:
        """更新Boss行為 - 比普通怪物更複雜的AI"""
        if not self.active:
            return

        # 檢查Boss階段轉換
        health_ratio = self.health / self.max_health

        if health_ratio <= 0.2 and self.phase < 3:
            self.phase = 3
            self.is_enraged = True
            self.move_speed = 3.0
            self.attack_cooldown = 0.5
            print(f"Boss進入絕望階段！移動和攻擊速度大幅提升！")
        elif health_ratio <= 0.5 and self.phase < 2:
            self.phase = 2
            self.is_enraged = True
            self.move_speed = 2.5
            self.attack_cooldown = 0.7
            print(f"Boss暴怒了！變得更加危險！")

        # 計算到玩家的距離
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        dx = player_x - center_x
        dy = player_y - center_y
        distance_to_player = math.sqrt(dx**2 + dy**2)

        # Boss有更大的感知範圍
        effective_chase_range = self.chase_range
        if player_in_darkness:
            effective_chase_range *= 1.8  # 黑暗中Boss更恐怖

        if self.is_enraged:
            effective_chase_range *= 1.5  # 憤怒時追擊範圍增加

        # 狀態機邏輯
        if distance_to_player <= self.attack_range:
            self.state = "attacking"
        elif distance_to_player <= effective_chase_range:
            self.state = "chasing"
        else:
            self.state = "patrolling"

        # 執行對應行為
        if self.state == "chasing" or self.state == "attacking":
            self._move_towards_player(dx, dy, distance_to_player, delta_time)

    def _move_towards_player(
        self, dx: float, dy: float, distance: float, delta_time: float
    ) -> None:
        """Boss向玩家移動 - 比普通怪物更聰明"""
        if distance > 0:
            # 正規化方向
            move_x = (dx / distance) * self.move_speed * delta_time * 60
            move_y = (dy / distance) * self.move_speed * delta_time * 60

            # Boss會嘗試包圍玩家（稍微隨機偏移）
            if self.is_enraged and random.random() < 0.3:
                angle_offset = random.uniform(-0.5, 0.5)
                cos_offset = math.cos(angle_offset)
                sin_offset = math.sin(angle_offset)
                new_move_x = move_x * cos_offset - move_y * sin_offset
                new_move_y = move_x * sin_offset + move_y * cos_offset
                move_x, move_y = new_move_x, new_move_y

            # 移動
            self.x += move_x
            self.y += move_y

            # 限制在房間內
            self.x = max(
                10, min(self.x, CAVE_CONFIG["room_size"]["width"] - self.width - 10)
            )
            self.y = max(
                10, min(self.y, CAVE_CONFIG["room_size"]["height"] - self.height - 10)
            )

            # 更新碰撞箱
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)

    def can_attack(self) -> bool:
        """檢查Boss是否可以攻擊"""
        current_time = time.time()
        return (
            self.state == "attacking"
            and current_time - self.last_attack >= self.attack_cooldown
        )

    def attack_player(self, player: "Player") -> Optional[Dict]:
        """Boss攻擊玩家 - 造成更高傷害"""
        if not self.can_attack():
            return None

        self.last_attack = time.time()
        actual_damage = player.take_damage(self.damage)

        # 根據階段提供不同的攻擊訊息
        if self.phase == 3:
            message = f"Boss絕望一擊！造成 {actual_damage} 點巨大傷害！"
        elif self.phase == 2:
            message = f"Boss狂暴攻擊！造成 {actual_damage} 點重傷！"
        else:
            message = f"Boss攻擊！造成 {actual_damage} 點傷害！"

        return {
            "message": message,
            "damage": actual_damage,
        }

    def draw(self, screen: pygame.Surface) -> None:
        """繪製Boss - 兼容基類要求"""
        self.draw_with_camera_alpha(screen, int(self.x), int(self.y), 255)

    def draw_with_camera_alpha(
        self,
        screen: pygame.Surface,
        screen_x: int,
        screen_y: int,
        darkness_alpha: int = 255,
    ) -> None:
        """繪製Boss - 比普通怪物更恐怖的外觀"""
        if not self.active:
            return

        config = WORLD_OBJECTS[self.boss_type]
        base_color = config["color"]

        # 根據階段調整顏色
        if self.phase == 3:
            base_color = (255, 0, 0)  # 絕望階段：純紅色
        elif self.phase == 2:
            base_color = (220, 20, 20)  # 憤怒階段：亮紅色
        elif self.is_enraged:
            base_color = (200, 40, 40)  # 暴怒狀態：暗紅色

        # 根據黑暗程度調整顏色
        adjusted_color = tuple(int(c * (darkness_alpha / 255.0)) for c in base_color)

        # 創建螢幕矩形
        screen_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)

        # 繪製Boss本體（比普通怪物更大更恐怖）
        pygame.draw.ellipse(screen, adjusted_color, screen_rect)

        # Boss光環效果
        if self.is_enraged:
            aura_color = (
                (255, 100, 100, 100) if self.phase >= 2 else (255, 150, 150, 50)
            )
            aura_rect = pygame.Rect(
                screen_x - 5, screen_y - 5, self.width + 10, self.height + 10
            )
            pygame.draw.ellipse(screen, aura_color[:3], aura_rect, 3)

        # Boss眼睛（發出恐怖的紅光）
        eye_color = (255, 0, 0) if self.is_enraged else (255, 50, 50)
        left_eye = (
            int(screen_x + self.width * 0.25),
            int(screen_y + self.height * 0.3),
        )
        right_eye = (
            int(screen_x + self.width * 0.75),
            int(screen_y + self.height * 0.3),
        )

        eye_size = 8 if self.phase >= 2 else 6
        pygame.draw.circle(screen, eye_color, left_eye, eye_size)
        pygame.draw.circle(screen, eye_color, right_eye, eye_size)

        # Boss獠牙
        fang_color = (255, 255, 255)
        fang_points_left = [
            (screen_x + self.width * 0.35, screen_y + self.height * 0.6),
            (screen_x + self.width * 0.3, screen_y + self.height * 0.8),
            (screen_x + self.width * 0.4, screen_y + self.height * 0.7),
        ]
        fang_points_right = [
            (screen_x + self.width * 0.65, screen_y + self.height * 0.6),
            (screen_x + self.width * 0.7, screen_y + self.height * 0.8),
            (screen_x + self.width * 0.6, screen_y + self.height * 0.7),
        ]
        pygame.draw.polygon(screen, fang_color, fang_points_left)
        pygame.draw.polygon(screen, fang_color, fang_points_right)

        # Boss生命值條（更大更顯眼）
        self._draw_boss_health_bar(screen, screen_x, screen_y)

    def _draw_boss_health_bar(
        self, screen: pygame.Surface, screen_x: int, screen_y: int
    ) -> None:
        """繪製Boss專用生命值條"""
        bar_width = 60  # 比普通怪物更寬
        bar_height = 8  # 比普通怪物更高

        # 背景條
        bg_rect = pygame.Rect(screen_x - 10, screen_y - 20, bar_width, bar_height)
        pygame.draw.rect(screen, (60, 60, 60), bg_rect)
        pygame.draw.rect(screen, (255, 255, 255), bg_rect, 2)  # 白色邊框

        # 生命值條
        health_width = int((self.health / self.max_health) * bar_width)
        health_rect = pygame.Rect(
            screen_x - 10, screen_y - 20, health_width, bar_height
        )

        # 根據血量和階段調整顏色
        if self.health < self.max_health * 0.2:
            health_color = (255, 0, 0)  # 危險紅
        elif self.health < self.max_health * 0.5:
            health_color = (255, 165, 0)  # 警告橙
        else:
            health_color = (255, 100, 100)  # Boss紅

        pygame.draw.rect(screen, health_color, health_rect)

        # Boss標記
        font_size = 12
        try:
            font = pygame.font.Font(None, font_size)
        except:
            font = pygame.font.SysFont("Arial", font_size)

        boss_text = f"BOSS - 第{self.depth}層"
        text_surface = font.render(boss_text, True, (255, 255, 255))
        text_x = screen_x + self.width // 2 - text_surface.get_width() // 2
        text_y = screen_y - 35
        screen.blit(text_surface, (text_x, text_y))

    def interact(self, player: "Player") -> Optional[Dict]:
        """與Boss戰鬥"""
        if not self.active:
            return None

        # 玩家攻擊Boss
        damage_to_boss = player.attack_damage
        self.health -= damage_to_boss

        if self.health <= 0:
            self.destroy()
            # Boss死亡掉落鑰匙和豐富獎勵
            drops = self._generate_boss_loot()

            return {
                "message": f"擊敗了第{self.depth}層Boss！獲得下層鑰匙和豐富獎勵！",
                "items": drops,
                "boss_defeated": True,
                "depth": self.depth,
            }

        # Boss還活著，顯示戰鬥狀態
        health_percent = int((self.health / self.max_health) * 100)
        phase_text = ["", "憤怒", "暴怒", "絕望"][min(self.phase, 3)]

        message = f"與第{self.depth}層Boss激戰中！"
        if phase_text:
            message += f" ({phase_text}狀態)"
        message += f" Boss血量: {health_percent}%"

        return {"message": message}

    def _generate_boss_loot(self) -> List[Tuple[str, int]]:
        """生成Boss戰利品 - 包含下層鑰匙"""
        loot = []

        # 100%掉落下層鑰匙
        loot.append(("depth_key", 1))

        # 根據深度提供不同品質的獎勵
        base_reward_multiplier = 1.0 + (self.depth - 1) * 0.3

        # 高級材料（必掉）
        advanced_materials = ["steel_ingot", "diamond", "rare_gem"]
        for material in advanced_materials:
            count = max(1, int(random.randint(2, 4) * base_reward_multiplier))
            loot.append((material, count))

        # 珍貴寶石（高概率）
        if random.random() < 0.8:
            gems = ["diamond", "rare_gem", "treasure"]
            gem = random.choice(gems)
            count = max(1, int(random.randint(1, 3) * base_reward_multiplier))
            loot.append((gem, count))

        # 高級裝備（中等概率）
        if random.random() < 0.6:
            equipment = ["steel_sword", "diamond_pickaxe", "steel_armor"]
            item = random.choice(equipment)
            loot.append((item, 1))

        # 藥水獎勵（必掉）
        potions = ["health_potion", "energy_potion"]
        for potion in potions:
            count = max(2, int(random.randint(3, 5) * base_reward_multiplier))
            loot.append((potion, count))

        # 特殊Boss專屬掉落
        if random.random() < 0.3:
            special_items = ["boss_trophy", "ancient_artifact", "magic_crystal"]
            special = random.choice(special_items)
            loot.append((special, 1))

        print(f"🎁 Boss掉落物品: {loot}")
        return loot


class CaveMonster(GameObject):
    """洞穴怪物 - 比地表怪物更強大且主動攻擊"""

    def __init__(self, x: float, y: float, monster_type: str = "cave_monster"):
        config = WORLD_OBJECTS[monster_type]
        size = config["size"]
        super().__init__(x, y, size[0], size[1])

        self.monster_type = monster_type
        self.health = config["health"]
        self.max_health = self.health
        self.damage = config["damage"]
        self.attack_range = config["attack_range"]
        self.chase_range = config["chase_range"]
        self.attack_cooldown = config["attack_cooldown"]
        self.last_attack = 0

        # 主動攻擊行為
        self.is_aggressive = True
        self.move_speed = 1.5  # 比地表怪物更快
        self.target_player = None
        self.state = "patrolling"  # patrolling, chasing, attacking

        print(f"洞穴{monster_type}生成於 ({x:.0f}, {y:.0f})")

    def update(
        self,
        delta_time: float,
        player_x: float,
        player_y: float,
        player_in_darkness: bool,
    ) -> None:
        """
        更新洞穴怪物行為

        Args:
            delta_time: 幀時間
            player_x, player_y: 玩家位置
            player_in_darkness: 玩家是否在黑暗中
        """
        if not self.active:
            return

        # 計算到玩家的距離
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        dx = player_x - center_x
        dy = player_y - center_y
        distance_to_player = math.sqrt(dx**2 + dy**2)

        # 如果玩家在黑暗中，怪物追擊範圍增加
        effective_chase_range = self.chase_range
        if player_in_darkness:
            effective_chase_range *= 1.5

        # 狀態機邏輯
        if distance_to_player <= self.attack_range:
            self.state = "attacking"
        elif distance_to_player <= effective_chase_range:
            self.state = "chasing"
        else:
            self.state = "patrolling"

        # 執行對應行為
        if self.state == "chasing" or self.state == "attacking":
            self._move_towards_player(dx, dy, distance_to_player, delta_time)

    def _move_towards_player(
        self, dx: float, dy: float, distance: float, delta_time: float
    ) -> None:
        """向玩家移動"""
        if distance > 0:
            # 正規化方向
            move_x = (dx / distance) * self.move_speed * delta_time * 60  # 60 FPS 基準
            move_y = (dy / distance) * self.move_speed * delta_time * 60

            # 移動
            self.x += move_x
            self.y += move_y

            # 限制在房間內
            self.x = max(
                10, min(self.x, CAVE_CONFIG["room_size"]["width"] - self.width - 10)
            )
            self.y = max(
                10, min(self.y, CAVE_CONFIG["room_size"]["height"] - self.height - 10)
            )

            # 更新碰撞箱
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)

    def can_attack(self) -> bool:
        """檢查是否可以攻擊"""
        current_time = time.time()
        return (
            self.state == "attacking"
            and current_time - self.last_attack >= self.attack_cooldown
        )

    def attack_player(self, player: "Player") -> Optional[Dict]:
        """攻擊玩家"""
        if not self.can_attack():
            return None

        self.last_attack = time.time()
        actual_damage = player.take_damage(self.damage)

        monster_names = {"cave_monster": "洞穴怪物", "cave_spider": "洞穴蜘蛛"}

        name = monster_names.get(self.monster_type, "怪物")
        return {
            "message": f"{name}攻擊了你！造成 {actual_damage} 點傷害",
            "damage": actual_damage,
        }

    def draw(self, screen: pygame.Surface, darkness_alpha: int = 255) -> None:
        """繪製洞穴怪物"""
        if not self.active:
            return

        config = WORLD_OBJECTS[self.monster_type]
        base_color = config["color"]

        # 根據黑暗程度調整顏色
        adjusted_color = tuple(int(c * (darkness_alpha / 255.0)) for c in base_color)

        # 繪製怪物本體
        pygame.draw.ellipse(screen, adjusted_color, self.rect)

        # 眼睛（在黑暗中發光）
        eye_color = (
            (255, 50, 50) if self.monster_type == "cave_monster" else (255, 0, 255)
        )
        left_eye = (int(self.x + self.width * 0.3), int(self.y + self.height * 0.3))
        right_eye = (int(self.x + self.width * 0.7), int(self.y + self.height * 0.3))

        eye_size = 4 if self.monster_type == "cave_monster" else 3
        pygame.draw.circle(screen, eye_color, left_eye, eye_size)
        pygame.draw.circle(screen, eye_color, right_eye, eye_size)

        # 生命值條
        if self.health < self.max_health:
            self._draw_health_bar(screen)

    def draw_with_camera_alpha(
        self,
        screen: pygame.Surface,
        screen_x: int,
        screen_y: int,
        darkness_alpha: int = 255,
    ) -> None:
        """使用相機座標和透明度繪製怪物"""
        if not self.active:
            return

        config = WORLD_OBJECTS[self.monster_type]
        base_color = config["color"]

        # 根據黑暗程度調整顏色
        adjusted_color = tuple(int(c * (darkness_alpha / 255.0)) for c in base_color)

        # 創建螢幕矩形
        screen_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)

        # 繪製怪物本體
        pygame.draw.ellipse(screen, adjusted_color, screen_rect)

        # 眼睛（在黑暗中發光）
        eye_color = (
            (255, 50, 50) if self.monster_type == "cave_monster" else (255, 0, 255)
        )
        left_eye = (int(screen_x + self.width * 0.3), int(screen_y + self.height * 0.3))
        right_eye = (
            int(screen_x + self.width * 0.7),
            int(screen_y + self.height * 0.3),
        )

        eye_size = 4 if self.monster_type == "cave_monster" else 3
        pygame.draw.circle(screen, eye_color, left_eye, eye_size)
        pygame.draw.circle(screen, eye_color, right_eye, eye_size)

        # 生命值條
        if self.health < self.max_health:
            self._draw_health_bar_at_position(screen, screen_x, screen_y)

    def _draw_health_bar(self, screen: pygame.Surface) -> None:
        """繪製生命值條"""
        bar_width = 35
        bar_height = 4
        bg_rect = pygame.Rect(self.x, self.y - 12, bar_width, bar_height)
        pygame.draw.rect(screen, (60, 60, 60), bg_rect)

        health_width = int((self.health / self.max_health) * bar_width)
        health_rect = pygame.Rect(self.x, self.y - 12, health_width, bar_height)
        health_color = (255, 0, 0) if self.health < 20 else (255, 255, 0)
        pygame.draw.rect(screen, health_color, health_rect)

    def _draw_health_bar_at_position(
        self, screen: pygame.Surface, screen_x: int, screen_y: int
    ) -> None:
        """在指定位置繪製生命值條"""
        bar_width = 35
        bar_height = 4
        bg_rect = pygame.Rect(screen_x, screen_y - 12, bar_width, bar_height)
        pygame.draw.rect(screen, (60, 60, 60), bg_rect)

        health_width = int((self.health / self.max_health) * bar_width)
        health_rect = pygame.Rect(screen_x, screen_y - 12, health_width, bar_height)
        health_color = (255, 0, 0) if self.health < 20 else (255, 255, 0)
        pygame.draw.rect(screen, health_color, health_rect)

    def interact(self, player: "Player") -> Optional[Dict]:
        """與洞穴怪物戰鬥"""
        if not self.active:
            return None

        # 玩家攻擊怪物
        damage_to_monster = player.attack_damage
        self.health -= damage_to_monster

        if self.health <= 0:
            self.destroy()

            # 洞穴怪物掉落更好的物品
            drops = self._generate_loot()

            monster_names = {"cave_monster": "洞穴怪物", "cave_spider": "洞穴蜘蛛"}
            name = monster_names.get(self.monster_type, "怪物")

            return {"message": f"擊敗了{name}！獲得了豐富的戰利品", "items": drops}

        return {
            "message": f"與洞穴怪物激戰中... 怪物生命值: {self.health}/{self.max_health}"
        }

    def _generate_loot(self) -> List[Tuple[str, int]]:
        """生成戰利品"""
        loot = []

        if self.monster_type == "cave_monster":
            # 洞穴怪物掉落
            if random.random() < 0.8:
                loot.append(("treasure", random.randint(1, 2)))
            if random.random() < 0.6:
                loot.append(("iron_ore", random.randint(2, 4)))
            if random.random() < 0.4:
                loot.append(("coal", random.randint(1, 3)))
            if random.random() < 0.1:
                loot.append(("diamond", 1))

        elif self.monster_type == "cave_spider":
            # 洞穴蜘蛛掉落
            if random.random() < 0.7:
                loot.append(("plant_fiber", random.randint(2, 5)))
            if random.random() < 0.3:
                loot.append(("rare_gem", 1))

        return loot


class TreasureChest(GameObject):
    """洞穴寶箱 - 包含更珍貴的物品"""

    def __init__(self, x: float, y: float, chest_type: str = "treasure_chest"):
        config = WORLD_OBJECTS[chest_type]
        size = config["size"]
        super().__init__(x, y, size[0], size[1])

        self.chest_type = chest_type
        self.opened = False
        self.loot = self._generate_treasure()

    def _generate_treasure(self) -> List[Tuple[str, int]]:
        """生成寶箱內容"""
        loot = []

        # 高級材料 (高機率)
        if random.random() < 0.9:
            materials = ["iron_ingot", "steel_ingot", "copper_ingot"]
            material = random.choice(materials)
            loot.append((material, random.randint(2, 5)))

        # 珍貴寶石 (中等機率)
        if random.random() < 0.5:
            gems = ["rare_gem", "diamond", "treasure"]
            gem = random.choice(gems)
            loot.append((gem, random.randint(1, 2)))

        # 高級裝備 (低機率)
        if random.random() < 0.3:
            equipment = ["steel_sword", "steel_armor", "diamond_pickaxe"]
            item = random.choice(equipment)
            loot.append((item, 1))

        # 藥水 (中等機率)
        if random.random() < 0.6:
            potions = ["health_potion", "energy_potion"]
            potion = random.choice(potions)
            loot.append((potion, random.randint(1, 3)))

        return loot

    def draw(self, screen: pygame.Surface, darkness_alpha: int = 255) -> None:
        """繪製寶箱"""
        if not self.active:
            return

        base_color = WORLD_OBJECTS[self.chest_type]["color"]
        if self.opened:
            base_color = (139, 69, 19)  # 已開啟的顏色

        # 根據黑暗程度調整
        adjusted_color = tuple(int(c * (darkness_alpha / 255.0)) for c in base_color)

        pygame.draw.rect(screen, adjusted_color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)

        # 寶箱發光效果（未開啟時）
        if not self.opened:
            glow_color = (255, 215, 0, 100)  # 金色光暈
            glow_rect = pygame.Rect(
                self.x - 2, self.y - 2, self.width + 4, self.height + 4
            )
            # 創建發光表面
            glow_surface = pygame.Surface(
                (self.width + 4, self.height + 4), pygame.SRCALPHA
            )
            glow_surface.fill(glow_color)
            screen.blit(glow_surface, (self.x - 2, self.y - 2))

    def draw_with_camera_alpha(
        self,
        screen: pygame.Surface,
        screen_x: int,
        screen_y: int,
        darkness_alpha: int = 255,
    ) -> None:
        """使用相機座標和透明度繪製寶箱"""
        if not self.active:
            return

        base_color = WORLD_OBJECTS[self.chest_type]["color"]
        if self.opened:
            base_color = (139, 69, 19)  # 已開啟的顏色

        # 根據黑暗程度調整
        adjusted_color = tuple(int(c * (darkness_alpha / 255.0)) for c in base_color)

        # 創建螢幕矩形
        screen_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)

        pygame.draw.rect(screen, adjusted_color, screen_rect)
        pygame.draw.rect(screen, (0, 0, 0), screen_rect, 2)

        # 寶箱發光效果（未開啟時）
        if not self.opened:
            glow_color = (255, 215, 0, 100)  # 金色光暈
            # 創建發光表面
            glow_surface = pygame.Surface(
                (self.width + 4, self.height + 4), pygame.SRCALPHA
            )
            glow_surface.fill(glow_color)
            screen.blit(glow_surface, (screen_x - 2, screen_y - 2))

    def interact(self, player: "Player") -> Optional[Dict]:
        """打開寶箱"""
        if not self.active or self.opened:
            return {"message": "這個寶箱已經空了"}

        self.opened = True
        if self.loot:
            return {"message": "打開了神秘寶箱！發現了珍貴的寶物！", "items": self.loot}
        else:
            return {"message": "寶箱是空的..."}


class CaveSystem:
    """洞穴系統管理器 - 支援Boss戰和鑰匙進度系統"""

    def __init__(self):
        self.in_cave = False
        self.current_room = None
        self.player_torch_time = 0  # 玩家火把剩餘時間
        self.darkness_damage_timer = 0
        self.current_depth = 1  # 🆕 當前深度
        self.max_unlocked_depth = 1  # 🆕 最大可進入深度
        self.depth_keys = {}  # 🆕 擁有的深度鑰匙 {depth: count}

    def enter_cave(self, depth: int = 1) -> CaveRoom:
        """進入洞穴 - 檢查鑰匙權限"""
        # 檢查是否有權限進入此深度
        if depth > self.max_unlocked_depth and depth > 1:
            print(f"需要第{depth-1}層的鑰匙才能進入第{depth}層！")
            return None

        self.in_cave = True
        self.current_depth = depth
        self.current_room = self._generate_cave_room(depth)
        print(f"進入洞穴第 {depth} 層 - 物件密度極高！")
        return self.current_room

    def exit_cave(self) -> None:
        """退出洞穴"""
        self.in_cave = False
        self.current_room = None
        self.current_depth = 1
        self.player_torch_time = 0
        print("🌅 返回地表")

    def unlock_next_depth(self, depth: int) -> bool:
        """解鎖下一層深度"""
        if depth >= self.max_unlocked_depth:
            self.max_unlocked_depth = depth + 1
            print(f"解鎖了第{depth + 1}層洞穴！")
            return True
        return False

    def add_depth_key(self, depth: int) -> None:
        """添加深度鑰匙"""
        if depth not in self.depth_keys:
            self.depth_keys[depth] = 0
        self.depth_keys[depth] += 1
        self.unlock_next_depth(depth)
        print(f"獲得了第{depth}層鑰匙！可以進入第{depth + 1}層了！")

    def _generate_cave_room(self, depth: int) -> CaveRoom:
        """生成洞穴房間 - 大幅提高密度並加入Boss"""
        room = CaveRoom(depth=depth)

        # 🔥 根據用戶要求，大大提高生成密度
        base_monster_count = 8  # 基礎怪物數量大幅提升（原本最多8個）
        base_treasure_count = 5  # 基礎寶箱數量大幅提升
        base_mineral_count = 12  # 基礎礦物數量大幅提升

        # 根據深度進一步增加密度
        depth_multiplier = 1.0 + (depth - 1) * 0.5

        monster_count = int(
            base_monster_count * depth_multiplier * CAVE_CONFIG["monster_spawn_rate"]
        )
        treasure_count = int(
            base_treasure_count * depth_multiplier * CAVE_CONFIG["treasure_spawn_rate"]
        )
        mineral_count = int(
            base_mineral_count * depth_multiplier * CAVE_CONFIG["mineral_spawn_rate"]
        )

        # 確保最小密度
        monster_count = max(monster_count, 12)  # 至少12個怪物
        treasure_count = max(treasure_count, 6)  # 至少6個寶箱
        mineral_count = max(mineral_count, 15)  # 至少15個礦物點

        print(
            f"第{depth}層生成密度: 怪物{monster_count}個, 寶箱{treasure_count}個, 礦物{mineral_count}個"
        )

        # 🆕 每層都生成一個Boss
        if CAVE_CONFIG["boss_per_level"]:
            # Boss放在房間中央附近的隨機位置
            boss_x = random.randint(room.width // 3, 2 * room.width // 3)
            boss_y = random.randint(room.height // 3, 2 * room.height // 3)
            room.boss = CaveBoss(boss_x, boss_y, depth)
            print(f"第{depth}層Boss已就位於 ({boss_x}, {boss_y})")

        # 生成大量怪物
        monster_types = ["cave_monster", "cave_spider"]
        for i in range(monster_count):
            attempts = 0
            while attempts < 50:  # 防止無限循環
                x = random.randint(30, room.width - 80)
                y = random.randint(30, room.height - 80)

                # 確保不與Boss重疊
                if room.boss:
                    boss_distance = math.sqrt(
                        (x - room.boss.x) ** 2 + (y - room.boss.y) ** 2
                    )
                    if boss_distance < 100:  # 與Boss保持距離
                        attempts += 1
                        continue

                monster_type = random.choice(monster_types)
                # 深層有更多強力怪物
                if depth >= 3 and random.random() < 0.4:
                    monster_type = "cave_monster"  # 更多強力怪物

                room.monsters.append(CaveMonster(x, y, monster_type))
                break

            attempts += 1

        # 生成大量寶箱
        for i in range(treasure_count):
            attempts = 0
            while attempts < 50:
                x = random.randint(40, room.width - 90)
                y = random.randint(40, room.height - 90)

                # 檢查與其他物件的距離
                too_close = False
                if room.boss:
                    boss_distance = math.sqrt(
                        (x - room.boss.x) ** 2 + (y - room.boss.y) ** 2
                    )
                    if boss_distance < 80:
                        too_close = True

                if not too_close:
                    room.treasures.append(TreasureChest(x, y))
                    break

                attempts += 1

        # 生成大量礦物點（用特殊寶箱代表）
        for i in range(mineral_count):
            attempts = 0
            while attempts < 50:
                x = random.randint(20, room.width - 70)
                y = random.randint(20, room.height - 70)

                # 礦物可以離其他物件近一些，使用普通寶箱類型
                room.treasures.append(TreasureChest(x, y, "treasure_chest"))
                break

        print(
            f"第{depth}層房間生成完成！實際數量 - 怪物: {len(room.monsters)}, 寶物: {len(room.treasures)}"
        )
        return room

    def update(self, delta_time: float, player: "Player") -> List[str]:
        """更新洞穴系統 - 包含Boss戰邏輯"""
        messages = []

        if not self.in_cave:
            return messages

        # 更新火把時間
        if self.player_torch_time > 0:
            self.player_torch_time -= delta_time
            if self.player_torch_time <= 0:
                messages.append("火把熄滅了！你陷入了黑暗中...")

        # 檢查玩家是否在黑暗中
        player_in_darkness = self.player_torch_time <= 0

        # 黑暗傷害
        if player_in_darkness:
            self.darkness_damage_timer += delta_time
            if self.darkness_damage_timer >= 1.0:  # 每秒一次傷害
                damage = CAVE_CONFIG["darkness_damage"]
                player.take_damage(damage)
                messages.append(f"黑暗侵蝕著你的身體！受到 {damage} 點傷害")
                self.darkness_damage_timer = 0
        else:
            self.darkness_damage_timer = 0

        # 更新洞穴物件
        if self.current_room:
            player_center_x = player.x + player.width // 2
            player_center_y = player.y + player.height // 2

            # 🆕 更新Boss
            if self.current_room.boss and self.current_room.boss.active:
                self.current_room.boss.update(
                    delta_time, player_center_x, player_center_y, player_in_darkness
                )

                # 檢查Boss主動攻擊
                if self.current_room.boss.can_attack():
                    distance = math.sqrt(
                        (self.current_room.boss.x - player.x) ** 2
                        + (self.current_room.boss.y - player.y) ** 2
                    )
                    if distance <= self.current_room.boss.attack_range:
                        attack_result = self.current_room.boss.attack_player(player)
                        if attack_result:
                            messages.append(attack_result["message"])

            # 更新普通怪物
            for monster in self.current_room.monsters:
                if monster.active:
                    monster.update(
                        delta_time, player_center_x, player_center_y, player_in_darkness
                    )

                    # 檢查怪物主動攻擊
                    if monster.can_attack():
                        distance = math.sqrt(
                            (monster.x - player.x) ** 2 + (monster.y - player.y) ** 2
                        )
                        if distance <= monster.attack_range:
                            attack_result = monster.attack_player(player)
                            if attack_result:
                                messages.append(attack_result["message"])

        return messages

    def use_torch(self, player: "Player") -> bool:
        """使用火把"""
        if player.inventory.has_item("torch", 1):
            player.inventory.remove_item("torch", 1)
            self.player_torch_time += CAVE_CONFIG["torch_duration"]
            return True
        return False

    def use_cave_lamp(self, player: "Player") -> bool:
        """使用洞穴燈"""
        if player.inventory.has_item("cave_lamp", 1):
            # 洞穴燈提供更長時間的照明
            self.player_torch_time += CAVE_CONFIG["torch_duration"] * 2
            return True
        return False

    def draw(self, screen: pygame.Surface, camera=None) -> None:
        """繪製洞穴場景 - 包含Boss和高密度物件"""
        if not self.in_cave or not self.current_room:
            return

        # 計算黑暗程度
        darkness_level = self.current_room.darkness_level
        if self.player_torch_time > 0:
            # 有光源時減少黑暗程度
            light_strength = min(1.0, self.player_torch_time / 60.0)  # 1分鐘內逐漸變暗
            darkness_level *= 1.0 - light_strength * 0.7

        # 繪製黑暗遮罩
        darkness_alpha = int(darkness_level * 200)  # 0-200的透明度
        if darkness_alpha > 0:
            dark_surface = pygame.Surface(
                (WINDOW_CONFIG["width"], WINDOW_CONFIG["height"])
            )
            dark_surface.set_alpha(darkness_alpha)
            dark_surface.fill((0, 0, 0))
            screen.blit(dark_surface, (0, 0))

        # 繪製洞穴物件
        light_alpha = 255 - darkness_alpha

        # 🆕 優先繪製Boss（最顯眼）
        if self.current_room.boss and self.current_room.boss.active:
            if camera:
                if camera.is_visible(
                    self.current_room.boss.x,
                    self.current_room.boss.y,
                    self.current_room.boss.width,
                    self.current_room.boss.height,
                ):
                    screen_x, screen_y = camera.world_to_screen(
                        self.current_room.boss.x, self.current_room.boss.y
                    )
                    self.current_room.boss.draw_with_camera_alpha(
                        screen, screen_x, screen_y, light_alpha
                    )
            else:
                self.current_room.boss.draw_with_camera_alpha(
                    screen,
                    int(self.current_room.boss.x),
                    int(self.current_room.boss.y),
                    light_alpha,
                )

        # 繪製普通怪物
        for monster in self.current_room.monsters:
            if monster.active:
                if camera:
                    if camera.is_visible(
                        monster.x, monster.y, monster.width, monster.height
                    ):
                        screen_x, screen_y = camera.world_to_screen(
                            monster.x, monster.y
                        )
                        monster.draw_with_camera_alpha(
                            screen, screen_x, screen_y, light_alpha
                        )
                else:
                    monster.draw(screen, light_alpha)

        # 繪製寶箱
        for treasure in self.current_room.treasures:
            if treasure.active:
                if camera:
                    if camera.is_visible(
                        treasure.x, treasure.y, treasure.width, treasure.height
                    ):
                        screen_x, screen_y = camera.world_to_screen(
                            treasure.x, treasure.y
                        )
                        treasure.draw_with_camera_alpha(
                            screen, screen_x, screen_y, light_alpha
                        )
                else:
                    treasure.draw(screen, light_alpha)

    def get_cave_objects(self) -> List[GameObject]:
        """獲取當前洞穴中的所有物件 - 包含Boss"""
        if not self.in_cave or not self.current_room:
            return []

        objects = []

        # 🆕 加入Boss（優先級最高）
        if self.current_room.boss and self.current_room.boss.active:
            objects.append(self.current_room.boss)

        # 加入普通怪物
        objects.extend([m for m in self.current_room.monsters if m.active])

        # 加入寶箱
        objects.extend([t for t in self.current_room.treasures if t.active])

        return objects

    def handle_boss_death(self, depth: int) -> None:
        """處理Boss死亡事件"""
        if self.current_room:
            self.current_room.boss_defeated = True
            self.add_depth_key(depth)
            print(f"第{depth}層Boss已被擊敗！解鎖下一層！")


# 全域洞穴系統實例
cave_system = CaveSystem()
