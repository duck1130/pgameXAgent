"""
Survival Realm - 洞穴探險系統
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

if TYPE_CHECKING:
    from ..entities.player import Player

# 引入世界物件類
from .world_objects import Rock

from .game_object import GameObject
from ..core.config import CAVE_CONFIG, WORLD_OBJECTS, WINDOW_CONFIG

# 避免循環引用
if TYPE_CHECKING:
    from ..entities.player import Player


@dataclass
class CaveRoom:
    """地下城房間數據類 - 支援多房間闖關系統"""

    depth: int  # 深度層級
    room_id: int = 0  # 房間編號（每層0-2）
    width: int = 1400  # 更大的地下城房間
    height: int = 1000  # 更大的地下城房間
    room_type: str = "standard"  # 房間類型
    monsters: List[GameObject] = None
    treasures: List[GameObject] = None
    minerals: List[GameObject] = None
    boss: Optional[GameObject] = None  # 每層的Boss
    mini_boss: Optional[GameObject] = None  # 小Boss
    has_exit: bool = True  # 是否有出口
    darkness_level: float = 0.8  # 黑暗程度 (0.0-1.0)
    boss_defeated: bool = False  # Boss是否已被擊敗
    has_key: bool = False  # 是否擁有進入下層的鑰匙
    is_locked: bool = True  # 房間是否被鎖住
    required_key_type: str = "depth_key"  # 需要的鑰匙類型
    doors: List[GameObject] = None  # 房間的門
    enchanting_table: Optional[GameObject] = None  # 附魔台
    completion_reward: Dict[str, int] = None  # 完成獎勵

    def __post_init__(self):
        if self.monsters is None:
            self.monsters = []
        if self.treasures is None:
            self.treasures = []
        if self.minerals is None:
            self.minerals = []
        if self.doors is None:
            self.doors = []
        if self.completion_reward is None:
            self.completion_reward = {}

    def is_room_completed(self) -> bool:
        """檢查房間是否已完成（所有怪物被擊敗）"""
        return (
            len(self.monsters) == 0
            and (self.boss is None or self.boss_defeated)
            and (
                self.mini_boss is None
                or not hasattr(self.mini_boss, "health")
                or self.mini_boss.health <= 0
            )
        )

    def unlock_room(self) -> bool:
        """解鎖房間"""
        if not self.is_locked:
            return True
        self.is_locked = False
        return True


class LockedDoor(GameObject):
    """地下城鎖門 - 需要鑰匙才能通過"""

    def __init__(self, x: float, y: float, required_key: str = "depth_key"):
        config = WORLD_OBJECTS["locked_door"]
        size = config["size"]
        super().__init__(x, y, size[0], size[1])

        self.required_key = required_key
        self.is_locked = True
        self.color = config["color"]

        print(f"🚪 創建鎖門: 位置({x:.1f}, {y:.1f}), 需要鑰匙: {required_key}")

    def interact(self, player) -> bool:
        """嘗試用鑰匙開門"""
        if not self.is_locked:
            return True

        # 檢查玩家是否有所需的鑰匙
        if hasattr(player, "inventory") and hasattr(player.inventory, "has_item"):
            if player.inventory.has_item(self.required_key):
                # 消耗鑰匙
                player.inventory.remove_item(self.required_key, 1)
                self.is_locked = False
                print(f"🔓 門已解鎖！使用了{self.required_key}")
                return True
            else:
                print(f"🔒 門被鎖住了！需要 {self.required_key}")
                return False
        return False

    def draw(self, screen, camera_x: float, camera_y: float):
        """繪製鎖門"""
        screen_x = int(self.x - camera_x + WINDOW_CONFIG["width"] // 2)
        screen_y = int(self.y - camera_y + WINDOW_CONFIG["height"] // 2)

        # 根據鎖定狀態選擇顏色
        door_color = self.color if self.is_locked else (139, 69, 19)  # 棕色為開啟
        lock_color = (255, 215, 0) if self.is_locked else (0, 255, 0)  # 金色鎖/綠色開啟

        # 繪製門
        pygame.draw.rect(
            screen, door_color, (screen_x, screen_y, self.width, self.height)
        )
        pygame.draw.rect(
            screen, (0, 0, 0), (screen_x, screen_y, self.width, self.height), 3
        )

        # 繪製鎖的標誌
        lock_x = screen_x + self.width - 25
        lock_y = screen_y + self.height // 2 - 10
        pygame.draw.circle(screen, lock_color, (lock_x, lock_y), 8)

        if self.is_locked:
            pygame.draw.rect(screen, lock_color, (lock_x - 5, lock_y, 10, 15))


class EnchantingTable(GameObject):
    """附魔台 - 用於附魔裝備"""

    def __init__(self, x: float, y: float):
        config = WORLD_OBJECTS["enchanting_table"]
        size = config["size"]
        super().__init__(x, y, size[0], size[1])

        self.color = config["color"]
        self.enchantment_levels = [1, 2, 3, 4, 5]  # 可用的附魔等級
        self.is_active = True

        print(f"✨ 創建附魔台: 位置({x:.1f}, {y:.1f})")

    def interact(self, player) -> bool:
        """打開附魔界面"""
        print("✨ 打開附魔台！選擇要附魔的裝備...")
        # 這裡會在主遊戲循環中處理附魔界面
        return True

    def enchant_item(self, item_id: str, enchant_level: int, player) -> bool:
        """附魔物品"""
        enchant_config = CAVE_CONFIG["enchant_success_rate"]
        success_rate = enchant_config.get(str(enchant_level), 0.1)

        # 檢查材料需求
        experience_needed = enchant_level * 5
        if not player.inventory.has_item("experience_orb", experience_needed):
            print(f"❌ 經驗不足！需要 {experience_needed} 個經驗球")
            return False

        # 嘗試附魔
        if random.random() <= success_rate:
            # 成功附魔
            enchanted_item_id = f"enchanted_{item_id}"
            player.inventory.remove_item(item_id, 1)
            player.inventory.remove_item("experience_orb", experience_needed)
            player.inventory.add_item(enchanted_item_id, 1)
            print(f"✅ 附魔成功！獲得 {enchanted_item_id}")
            return True
        else:
            # 附魔失敗
            player.inventory.remove_item(
                "experience_orb", experience_needed // 2
            )  # 失敗也消耗一半經驗
            print(f"❌ 附魔失敗！消耗了 {experience_needed // 2} 個經驗球")
            return False

    def draw(self, screen, camera_x: float, camera_y: float):
        """繪製附魔台"""
        screen_x = int(self.x - camera_x + WINDOW_CONFIG["width"] // 2)
        screen_y = int(self.y - camera_y + WINDOW_CONFIG["height"] // 2)

        # 繪製附魔台底座
        pygame.draw.rect(
            screen, self.color, (screen_x, screen_y, self.width, self.height)
        )
        pygame.draw.rect(
            screen, (139, 0, 139), (screen_x, screen_y, self.width, self.height), 3
        )

        # 繪製魔法效果
        for i in range(3):
            effect_x = screen_x + 10 + i * 20
            effect_y = screen_y - 10 - i * 5
            pygame.draw.circle(screen, (255, 255, 0), (effect_x, effect_y), 3)


class EliteMonster(GameObject):
    """精英怪物 - 比普通怪物更強"""

    def __init__(self, x: float, y: float, monster_type: str, depth: int):
        if monster_type == "elite_skeleton":
            config = WORLD_OBJECTS["elite_skeleton"]
        else:
            config = WORLD_OBJECTS["shadow_beast"]

        size = config["size"]
        super().__init__(x, y, size[0], size[1])

        self.monster_type = monster_type
        self.depth = depth

        # 根據深度調整屬性
        depth_multiplier = 1.0 + (depth - 1) * 0.3
        self.max_health = int(config["health"] * depth_multiplier)
        self.health = self.max_health
        self.damage = int(config["damage"] * depth_multiplier)

        self.attack_range = config["attack_range"]
        self.chase_range = config["chase_range"]
        self.attack_cooldown = config["attack_cooldown"]
        self.last_attack = 0

        self.is_elite = True
        self.move_speed = 1.8  # 比普通怪物快
        self.state = "patrolling"  # patrolling, chasing, attacking
        self.color = config["color"]

        print(f"👹 精英{monster_type}出現！深度{depth}層，血量: {self.health}")

    def update(
        self,
        delta_time: float,
        player_x: float,
        player_y: float,
        player_in_darkness: bool,
    ) -> None:
        """更新精英怪物狀態"""
        # 計算與玩家的距離
        distance = math.sqrt((self.x - player_x) ** 2 + (self.y - player_y) ** 2)

        current_time = time.time()

        if (
            distance <= self.attack_range
            and current_time - self.last_attack >= self.attack_cooldown
        ):
            # 攻擊玩家
            self.last_attack = current_time
            self.state = "attacking"
            print(f"💥 精英{self.monster_type}攻擊玩家！造成{self.damage}點傷害")
            return self.damage  # 返回傷害值

        elif distance <= self.chase_range:
            # 追擊玩家
            self.state = "chasing"
            if distance > self.attack_range:
                # 移動向玩家
                direction_x = (player_x - self.x) / distance
                direction_y = (player_y - self.y) / distance

                self.x += direction_x * self.move_speed * delta_time * 60
                self.y += direction_y * self.move_speed * delta_time * 60

        else:
            # 巡邏狀態
            self.state = "patrolling"

        return 0

    def can_attack(self) -> bool:
        """檢查精英怪物是否可以攻擊"""
        current_time = time.time()
        return (
            self.state == "attacking"
            and current_time - self.last_attack >= self.attack_cooldown
        )

    def attack_player(self, player: "Player") -> Optional[Dict]:
        """精英怪物攻擊玩家"""
        if not self.can_attack():
            return None

        current_time = time.time()
        self.last_attack = current_time

        print(f"💥 精英{self.monster_type}攻擊玩家！造成{self.damage}點傷害")

        return {
            "damage": self.damage,
            "monster_type": self.monster_type,
            "is_elite": True,
        }

    def interact(self, player) -> bool:
        """精英怪物互動 - 通常是攻擊"""
        return False  # 精英怪物不需要特殊互動

    def draw(self, screen, camera_x: float, camera_y: float):
        """繪製精英怪物"""
        screen_x = int(self.x - camera_x + WINDOW_CONFIG["width"] // 2)
        screen_y = int(self.y - camera_y + WINDOW_CONFIG["height"] // 2)

        # 繪製精英怪物
        pygame.draw.rect(
            screen, self.color, (screen_x, screen_y, self.width, self.height)
        )
        pygame.draw.rect(
            screen, (255, 255, 255), (screen_x, screen_y, self.width, self.height), 2
        )

        # 繪製精英標記（金色邊框）
        pygame.draw.rect(
            screen,
            (255, 215, 0),
            (screen_x - 2, screen_y - 2, self.width + 4, self.height + 4),
            2,
        )

        # 繪製血量條
        if self.health < self.max_health:
            bar_width = 40
            bar_height = 6
            bar_x = screen_x + (self.width - bar_width) // 2
            bar_y = screen_y - 12

            health_ratio = self.health / self.max_health
            health_width = int(bar_width * health_ratio)

            pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(
                screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height)
            )

    def draw_with_camera_alpha(
        self,
        screen: pygame.Surface,
        screen_x: int,
        screen_y: int,
        darkness_alpha: int = 255,
    ) -> None:
        """使用相機座標和透明度繪製精英怪物"""
        if not self.active:
            return

        # 根據黑暗程度調整顏色
        adjusted_color = tuple(int(c * (darkness_alpha / 255.0)) for c in self.color)

        # 創建螢幕矩形
        screen_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)

        # 繪製精英怪物主體
        pygame.draw.rect(screen, adjusted_color, screen_rect)

        # 繪製白色邊框（也受黑暗影響）
        border_alpha = int(255 * (darkness_alpha / 255.0))
        border_color = (border_alpha, border_alpha, border_alpha)
        pygame.draw.rect(screen, border_color, screen_rect, 2)

        # 繪製精英標記（金色邊框，稍微抗黑暗）
        elite_alpha = min(255, int(darkness_alpha * 1.2))  # 精英標記更顯眼
        gold_color = (
            int(255 * (elite_alpha / 255.0)),
            int(215 * (elite_alpha / 255.0)),
            0,
        )
        elite_rect = pygame.Rect(
            screen_x - 2, screen_y - 2, self.width + 4, self.height + 4
        )
        pygame.draw.rect(screen, gold_color, elite_rect, 2)

        # 繪製血量條（不受黑暗影響，保持可見）
        if self.health < self.max_health:
            bar_width = 40
            bar_height = 6
            bar_x = screen_x + (self.width - bar_width) // 2
            bar_y = screen_y - 12

            health_ratio = self.health / self.max_health
            health_width = int(bar_width * health_ratio)

            # 血量條背景（紅色）
            pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            # 當前血量（綠色）
            pygame.draw.rect(
                screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height)
            )

        # 狀態指示效果
        if self.state == "attacking":
            # 攻擊狀態：紅色光環
            attack_alpha = int(100 * (darkness_alpha / 255.0))
            attack_color = (255, attack_alpha, attack_alpha)
            pygame.draw.circle(
                screen,
                attack_color,
                (screen_x + self.width // 2, screen_y + self.height // 2),
                max(self.width, self.height) // 2 + 5,
                2,
            )
        elif self.state == "chasing":
            # 追擊狀態：黃色光環
            chase_alpha = int(80 * (darkness_alpha / 255.0))
            chase_color = (255, 255, chase_alpha)
            pygame.draw.circle(
                screen,
                chase_color,
                (screen_x + self.width // 2, screen_y + self.height // 2),
                max(self.width, self.height) // 2 + 3,
                1,
            )


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

        print(f"調試: Boss掉落物品: {loot}")
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
    """洞穴寶箱 - 包含更珍貴的物品，支援特殊類型"""

    def __init__(
        self, x: float, y: float, chest_type: str = "treasure_chest", depth: int = 1
    ):
        config = WORLD_OBJECTS[chest_type]
        size = config["size"]
        super().__init__(x, y, size[0], size[1])

        self.chest_type = chest_type
        self.depth = depth  # 記錄深度用於獎勵計算
        self.opened = False
        self.loot = self._generate_treasure()

    def _generate_treasure(self) -> List[Tuple[str, int]]:
        """生成寶箱內容 - 根據深度調整獎勵"""
        loot = []

        # 基於深度的獎勵倍數
        depth_multiplier = 1.0 + (self.depth - 1) * 0.3

        # 第10層超級寶物
        if self.depth >= CAVE_CONFIG["ultra_deep_threshold"]:
            # 第10層必掉稀有物品
            ultra_rare_items = [
                "legendary_sword",
                "ancient_armor",
                "magic_orb",
                "dragon_scale",
            ]
            for item in ultra_rare_items:
                if random.random() < 0.6:  # 60%機率獲得每種傳說物品
                    loot.append((item, 1))

            # 大量高級材料
            premium_materials = [
                "diamond",
                "rare_gem",
                "mythril_ingot",
                "phoenix_feather",
            ]
            for material in premium_materials:
                count = random.randint(3, 8)  # 大量掉落
                loot.append((material, count))

            # 超級藥水
            super_potions = [
                "legendary_health_potion",
                "ultimate_energy_potion",
                "invincibility_potion",
            ]
            for potion in super_potions:
                if random.random() < 0.8:
                    loot.append((potion, random.randint(2, 5)))

            print(f"第{self.depth}層超級寶箱！掉落傳說級物品！")

        # 高級材料 (高機率)
        if random.random() < 0.9:
            materials = ["iron_ingot", "steel_ingot", "copper_ingot"]
            if self.depth >= 5:
                materials.extend(["diamond", "rare_gem", "mythril_ingot"])

            material = random.choice(materials)
            count = max(1, int(random.randint(2, 5) * depth_multiplier))
            loot.append((material, count))

        # 珍貴寶石 (根據深度提高機率和品質)
        gem_chance = 0.5 + (self.depth - 1) * 0.1  # 深度越高機率越高
        if random.random() < gem_chance:
            gems = ["rare_gem", "diamond", "treasure"]
            if self.depth >= 7:
                gems.extend(["legendary_gem", "cosmic_crystal"])

            gem = random.choice(gems)
            count = max(1, int(random.randint(1, 2) * depth_multiplier))
            loot.append((gem, count))

        # 高級裝備 (深度越高越好)
        equipment_chance = 0.3 + (self.depth - 1) * 0.05
        if random.random() < equipment_chance:
            equipment = ["steel_sword", "steel_armor", "diamond_pickaxe"]
            if self.depth >= 5:
                equipment.extend(["enchanted_sword", "dragon_armor"])
            if self.depth >= 8:
                equipment.extend(["legendary_sword", "ancient_armor"])

            item = random.choice(equipment)
            loot.append((item, 1))

        # 藥水 (必掉，深度越高品質越好)
        if random.random() < 0.6:
            potions = ["health_potion", "energy_potion"]
            if self.depth >= 6:
                potions.extend(["greater_health_potion", "greater_energy_potion"])
            if self.depth >= 9:
                potions.extend(["legendary_health_potion", "ultimate_energy_potion"])

            potion = random.choice(potions)
            count = max(1, int(random.randint(1, 3) * depth_multiplier))
            loot.append((potion, count))

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
    """地下城系統管理器 - 支援多房間闖關和鎖門機制"""

    def __init__(self):
        self.in_cave = False
        self.current_room = None
        self.player_torch_time = 0  # 玩家火把剩餘時間
        self.darkness_damage_timer = 0
        self.current_depth = 1  # 當前深度
        self.current_room_id = 0  # 當前房間編號
        self.max_unlocked_depth = 1  # 最大可進入深度
        self.depth_keys = {}  # 擁有的深度鑰匙 {depth: count}
        self.room_progress = {}  # 房間進度 {depth: {room_id: completed}}
        self.player_keys = set()  # 玩家擁有的鑰匙

    def enter_cave(self, depth: int = 1, room_id: int = 0) -> CaveRoom:
        """進入地下城 - 檢查鑰匙權限和房間進度"""
        # 檢查是否有權限進入此深度
        if depth > self.max_unlocked_depth and depth > 1:
            print(f"🔒 需要第{depth-1}層的鑰匙才能進入第{depth}層！")
            return None

        # 檢查房間進度（除了第一個房間）
        if room_id > 0:
            if not self._is_previous_room_completed(depth, room_id):
                print(f"🔒 必須先完成第{depth}層第{room_id}號房間！")
                return None

        self.in_cave = True
        self.current_depth = depth
        self.current_room_id = room_id
        self.current_room = self._generate_cave_room(depth, room_id)
        print(f"🏰 進入地下城第 {depth} 層第 {room_id} 號房間！")
        return self.current_room

    def exit_cave(self) -> None:
        """退出地下城"""
        self.in_cave = False
        self.current_room = None
        self.current_depth = 1
        self.current_room_id = 0
        self.player_torch_time = 0
        print("🌅 返回地表")

    def unlock_next_depth(self, depth: int) -> bool:
        """解鎖下一層深度"""
        if depth >= self.max_unlocked_depth:
            self.max_unlocked_depth = depth + 1
            print(f"🗝️ 解鎖了第{depth + 1}層地下城！")
            return True
        return False

    def add_depth_key(self, depth: int) -> None:
        """添加深度鑰匙"""
        if depth not in self.depth_keys:
            self.depth_keys[depth] = 0
        self.depth_keys[depth] += 1
        self.player_keys.add(f"depth_key_{depth}")
        self.unlock_next_depth(depth)
        print(f"🎉 獲得了第{depth}層鑰匙！可以進入第{depth + 1}層了！")

    def complete_room(self, depth: int, room_id: int) -> bool:
        """完成房間，獲得獎勵"""
        if depth not in self.room_progress:
            self.room_progress[depth] = {}

        self.room_progress[depth][room_id] = True

        # 檢查是否完成了該層的所有房間
        rooms_per_level = CAVE_CONFIG["rooms_per_level"]
        completed_rooms = sum(
            1 for i in range(rooms_per_level) if self.room_progress[depth].get(i, False)
        )

        if completed_rooms >= rooms_per_level:
            print(f"🎊 完成了第{depth}層的所有房間！獲得層級獎勵！")
            # 獲得下一層的鑰匙
            if depth < CAVE_CONFIG["max_depth"]:
                self.add_depth_key(depth)
            return True
        else:
            print(
                f"✅ 完成房間 {depth}-{room_id}！({completed_rooms}/{rooms_per_level})"
            )
            return False

    def _is_previous_room_completed(self, depth: int, room_id: int) -> bool:
        """檢查前一個房間是否已完成"""
        if depth not in self.room_progress:
            return room_id == 0

        return self.room_progress[depth].get(room_id - 1, False)

    def has_key(self, key_type: str) -> bool:
        """檢查是否擁有指定鑰匙"""
        return key_type in self.player_keys

    def use_key(self, key_type: str) -> bool:
        """使用鑰匙"""
        if self.has_key(key_type):
            self.player_keys.remove(key_type)
            return True
        return False

    def _generate_cave_room(self, depth: int, room_id: int = 0) -> CaveRoom:
        """生成地下城房間 - 高密度闖關風格"""
        print(f"🏗️ 生成第{depth}層第{room_id}號房間...")

        # 根據房間編號確定房間類型
        room_type = self._determine_room_type_by_id(depth, room_id)

        room_config = CAVE_CONFIG["room_size"]
        room = CaveRoom(
            depth=depth,
            room_id=room_id,
            width=room_config["width"],
            height=room_config["height"],
            room_type=room_type,
        )

        # ====== 高密度地下城風格 ======
        # 大幅提高密度，充滿挑戰
        base_monster_count = 8  # 大幅增加基礎怪物數量
        base_treasure_count = 4  # 大幅增加基礎寶箱數量
        base_mineral_count = 10  # 大幅增加基礎礦物數量

        # 根據深度大幅增加難度
        depth_multiplier = 1.0 + (depth - 1) * 0.5  # 每層增加50%

        monster_count = int(
            base_monster_count * depth_multiplier * CAVE_CONFIG["monster_spawn_rate"]
        )
        treasure_count = int(
            base_treasure_count * depth_multiplier * CAVE_CONFIG["treasure_spawn_rate"]
        )
        mineral_count = int(
            base_mineral_count * depth_multiplier * CAVE_CONFIG["mineral_spawn_rate"]
        )

        # ====== 地下城深層特殊獎勵 ======
        if depth >= CAVE_CONFIG.get("epic_threshold", 20):
            # 史詩級深度（第20層）
            treasure_count = int(
                treasure_count * CAVE_CONFIG.get("epic_treasure_multiplier", 15.0)
            )
            mineral_count = int(
                mineral_count * CAVE_CONFIG.get("epic_treasure_multiplier", 15.0)
            )
            monster_count = int(monster_count * 1.5)  # 史詩級敵人更多
            print(f"⚡ 第{depth}層是史詩級深度！極限挑戰！")
        elif depth >= CAVE_CONFIG.get("legendary_threshold", 15):
            # 傳說級深度（第15層）
            treasure_count = int(
                treasure_count * CAVE_CONFIG.get("legendary_treasure_multiplier", 8.0)
            )
            mineral_count = int(
                mineral_count * CAVE_CONFIG.get("legendary_treasure_multiplier", 8.0)
            )
            monster_count = int(monster_count * 1.3)
            print(f"🌟 第{depth}層是傳說級深度！稀世珍寶等待勇者！")
        elif depth >= CAVE_CONFIG["ultra_deep_threshold"]:
            # 超深層（第10-14層）
            treasure_count = int(
                treasure_count * CAVE_CONFIG["ultra_deep_treasure_multiplier"]
            )
            mineral_count = int(
                mineral_count * CAVE_CONFIG["ultra_deep_treasure_multiplier"]
            )
            print(f"第{depth}層是超深層！珍貴寶物密度提升！")
        elif depth >= CAVE_CONFIG["deep_layer_threshold"]:
            # 深層（第5-9層）
            treasure_count = int(
                treasure_count * CAVE_CONFIG["deep_treasure_multiplier"]
            )
            mineral_count = int(mineral_count * CAVE_CONFIG["deep_treasure_multiplier"])

        # ====== 地下城房間類型系統 ======
        room_type = self._determine_room_type(depth)
        if room_type == "treasure_room":
            treasure_count *= 3  # 寶藏房間
            monster_count = max(1, monster_count // 2)  # 減少怪物
        elif room_type == "boss_chamber":
            monster_count = 0  # Boss房間沒有普通怪物
            treasure_count *= 2  # 額外獎勵
        elif room_type == "maze":
            monster_count = max(1, monster_count // 3)  # 迷宮房間怪物很少
            mineral_count *= 2  # 但礦物較多

        # ====== 確保地下城的探索感 ======
        # 不像之前那樣保證最小密度，讓某些房間可能很空曠
        self._generate_dungeon_objects(
            room, monster_count, treasure_count, mineral_count, room_type, depth
        )

        print(
            f"第{depth}層地下城({room_type}): 怪物{len(room.monsters)}個, 寶箱{len(room.treasures)}個, 礦物{len(room.minerals)}個"
        )

        # ====== 地下城守護者Boss ======
        if CAVE_CONFIG["boss_per_level"]:
            boss_x, boss_y = self._get_boss_position(room, room_type)
            room.boss = CaveBoss(boss_x, boss_y, depth)
            print(f"第{depth}層地下城守護者就位於 ({boss_x}, {boss_y})")

        return room

    def _ensure_objects_around_spawn(
        self,
        room: CaveRoom,
        monster_count: int,
        treasure_count: int,
        mineral_count: int,
    ) -> None:
        """確保玩家出生點周圍有充足的物件"""
        spawn_x, spawn_y = 100, 100  # 玩家初始位置
        spawn_radius = 200  # 出生點周圍範圍

        # 在出生點周圍生成怪物
        monsters_around_spawn = max(8, monster_count // 3)  # 至少8個怪物在附近
        monster_types = ["cave_monster", "cave_spider"]

        for i in range(monsters_around_spawn):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(80, spawn_radius)  # 不要太近，但要在可見範圍內

            x = spawn_x + distance * math.cos(angle)
            y = spawn_y + distance * math.sin(angle)

            # 確保在房間內
            x = max(30, min(x, room.width - 80))
            y = max(30, min(y, room.height - 80))

            monster_type = random.choice(monster_types)
            room.monsters.append(CaveMonster(x, y, monster_type))

        # 在出生點周圍生成寶箱
        treasures_around_spawn = max(5, treasure_count // 3)

        for i in range(treasures_around_spawn):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(60, spawn_radius)

            x = spawn_x + distance * math.cos(angle)
            y = spawn_y + distance * math.sin(angle)

            x = max(40, min(x, room.width - 90))
            y = max(40, min(y, room.height - 90))

            room.treasures.append(TreasureChest(x, y, "treasure_chest", room.depth))

        # 補充剩餘的物件到房間其他位置
        remaining_monsters = monster_count - monsters_around_spawn
        for i in range(remaining_monsters):
            attempts = 0
            while attempts < 50:
                x = random.randint(30, room.width - 80)
                y = random.randint(30, room.height - 80)

                # 避免與Boss重疊
                if room.boss:
                    boss_distance = math.sqrt(
                        (x - room.boss.x) ** 2 + (y - room.boss.y) ** 2
                    )
                    if boss_distance < 100:
                        attempts += 1
                        continue

                monster_type = random.choice(monster_types)
                room.monsters.append(CaveMonster(x, y, monster_type))
                break

            attempts += 1

        # 生成剩餘寶箱和礦物
        remaining_treasures = treasure_count + mineral_count - treasures_around_spawn
        for i in range(remaining_treasures):
            attempts = 0
            while attempts < 50:
                x = random.randint(20, room.width - 70)
                y = random.randint(20, room.height - 70)

                room.treasures.append(TreasureChest(x, y, "treasure_chest", room.depth))
                break

    def _determine_room_type_by_id(self, depth: int, room_id: int) -> str:
        """根據房間編號確定房間類型 - 三房間系統"""
        rooms_per_level = CAVE_CONFIG["rooms_per_level"]

        if room_id == 0:
            # 第一個房間：標準戰鬥房間或特殊房間
            room_types = ["standard", "elite_chamber", "maze"]
            return random.choice(room_types)
        elif room_id == 1:
            # 第二個房間：資源或特殊功能房間
            if random.random() < CAVE_CONFIG["enchanting_room_chance"]:
                return "enchanting_room"
            room_types = ["treasure_room", "armory", "puzzle_room"]
            return random.choice(room_types)
        elif room_id == 2:
            # 第三個房間：Boss房間
            return "boss_chamber"
        else:
            # 備用房間（如果有更多房間）
            return "standard"

    def _determine_room_type(self, depth: int) -> str:
        """決定地下城房間類型（舊版方法，保持兼容性）"""
        room_types = CAVE_CONFIG.get("room_types", ["standard"])
        special_chance = CAVE_CONFIG.get("special_room_chance", 0.25)

        # 深層更容易出現特殊房間
        if depth >= 15:
            special_chance *= 3.0
        elif depth >= 10:
            special_chance *= 2.0
        elif depth >= 5:
            special_chance *= 1.5

        if random.random() < special_chance:
            # 排除標準房間，選擇特殊房間
            special_rooms = [rt for rt in room_types if rt != "standard"]
            if special_rooms:
                return random.choice(special_rooms)

        return "standard"

    def _get_boss_position(self, room: CaveRoom, room_type: str) -> tuple:
        """根據房間類型決定Boss位置"""
        if room_type == "boss_chamber":
            # Boss房間：Boss在中央
            return (room.width // 2, room.height // 2)
        elif room_type == "treasure_room":
            # 寶藏房間：Boss守護寶藏，在後方
            return (3 * room.width // 4, room.height // 2)
        else:
            # 其他房間：隨機位置，但不在邊緣
            x = random.randint(room.width // 4, 3 * room.width // 4)
            y = random.randint(room.height // 4, 3 * room.height // 4)
            return (x, y)

    def _generate_dungeon_objects(
        self,
        room: CaveRoom,
        monster_count: int,
        treasure_count: int,
        mineral_count: int,
        room_type: str,
        depth: int,
    ) -> None:
        """根據房間類型生成地下城物件 - 支援新房間類型"""
        if room_type == "treasure_room":
            self._generate_treasure_room(room, treasure_count, mineral_count)
        elif room_type == "boss_chamber":
            self._generate_boss_chamber(
                room, monster_count, treasure_count, mineral_count
            )
        elif room_type == "maze":
            self._generate_maze_room(room, monster_count, treasure_count, mineral_count)
        elif room_type == "trap_room":
            self._generate_trap_room(room, monster_count, treasure_count, mineral_count)
        elif room_type == "enchanting_room":
            self._generate_enchanting_room(
                room, monster_count, treasure_count, mineral_count
            )
        elif room_type == "elite_chamber":
            self._generate_elite_chamber(
                room, monster_count, treasure_count, mineral_count, depth
            )
        elif room_type == "puzzle_room":
            self._generate_puzzle_room(
                room, monster_count, treasure_count, mineral_count
            )
        elif room_type == "armory":
            self._generate_armory_room(
                room, monster_count, treasure_count, mineral_count, depth
            )
        else:
            self._generate_standard_room(
                room, monster_count, treasure_count, mineral_count, depth
            )

    def _generate_standard_room(
        self,
        room: CaveRoom,
        monster_count: int,
        treasure_count: int,
        mineral_count: int,
        depth: int,
    ) -> None:
        """生成標準地下城房間 - 高密度版本"""
        # 多種類怪物混合
        monster_types = ["cave_monster", "cave_spider"]
        if depth >= 5:
            monster_types.append("elite_skeleton")
        if depth >= 10:
            monster_types.append("shadow_beast")

        # 高密度怪物生成
        for _ in range(monster_count):
            x = random.randint(50, room.width - 50)
            y = random.randint(50, room.height - 50)
            monster_type = random.choice(monster_types)

            # 小機率生成精英怪物
            if random.random() < CAVE_CONFIG["elite_monster_rate"]:
                elite_type = random.choice(["elite_skeleton", "shadow_beast"])
                room.monsters.append(EliteMonster(x, y, elite_type, depth))
            else:
                room.monsters.append(CaveMonster(x, y, monster_type))

        # 多種寶箱類型
        for _ in range(treasure_count):
            x = random.randint(40, room.width - 40)
            y = random.randint(40, room.height - 40)

            # 根據深度決定寶箱類型
            if depth >= 15:
                chest_type = random.choice(
                    ["treasure_chest", "epic_chest", "legendary_chest"]
                )
            elif depth >= 10:
                chest_type = random.choice(["treasure_chest", "epic_chest"])
            else:
                chest_type = "treasure_chest"

            room.treasures.append(TreasureChest(x, y, chest_type, room.depth))

        # 大量礦物資源
        for _ in range(mineral_count):
            x = random.randint(30, room.width - 30)
            y = random.randint(30, room.height - 30)
            room.minerals.append(Rock(x, y))

        # 添加鎖門（除了第一個房間）
        if room.room_id > 0:
            door_x = room.width - 80
            door_y = room.height // 2
            required_key = f"room_key_{depth}_{room.room_id}"
            door = LockedDoor(door_x, door_y, required_key)
            room.doors.append(door)

    def _generate_treasure_room(
        self, room: CaveRoom, treasure_count: int, mineral_count: int
    ) -> None:
        """生成寶藏房間 - 寶箱集中，少量守衛"""
        # 寶箱集中在房間中央區域
        center_x, center_y = room.width // 2, room.height // 2
        for _ in range(treasure_count):
            x = center_x + random.randint(-100, 100)
            y = center_y + random.randint(-80, 80)
            x = max(40, min(x, room.width - 40))
            y = max(40, min(y, room.height - 40))
            room.treasures.append(TreasureChest(x, y, "treasure_chest", room.depth))

        # 少量強力守衛
        for _ in range(max(1, treasure_count // 3)):
            x = random.randint(50, room.width - 50)
            y = random.randint(50, room.height - 50)
            room.monsters.append(CaveMonster(x, y, "cave_monster"))

    def _generate_enchanting_room(
        self,
        room: CaveRoom,
        monster_count: int,
        treasure_count: int,
        mineral_count: int,
    ) -> None:
        """生成附魔房間 - 有附魔台和少量守護怪物"""
        # 在房間中央放置附魔台
        enchanting_x = room.width // 2
        enchanting_y = room.height // 2
        room.enchanting_table = EnchantingTable(enchanting_x, enchanting_y)

        # 少量精英守護怪物
        guardian_count = max(1, monster_count // 4)
        for _ in range(guardian_count):
            x = random.randint(100, room.width - 100)
            y = random.randint(100, room.height - 100)
            # 確保不會太靠近附魔台
            if abs(x - enchanting_x) < 80 and abs(y - enchanting_y) < 80:
                continue
            room.monsters.append(EliteMonster(x, y, "elite_skeleton", room.depth))

        # 少量高品質寶箱
        for _ in range(treasure_count // 2):
            x = random.randint(60, room.width - 60)
            y = random.randint(60, room.height - 60)
            chest_type = "epic_chest" if room.depth >= 10 else "treasure_chest"
            room.treasures.append(TreasureChest(x, y, chest_type, room.depth))

        # 一些魔法礦物
        for _ in range(mineral_count // 2):
            x = random.randint(40, room.width - 40)
            y = random.randint(40, room.height - 40)
            room.minerals.append(Rock(x, y))  # 可以是魔法礦物

        print("✨ 生成附魔房間完成！")

    def _generate_elite_chamber(
        self,
        room: CaveRoom,
        monster_count: int,
        treasure_count: int,
        mineral_count: int,
        depth: int,
    ) -> None:
        """生成精英房間 - 少量但強力的精英怪物"""
        elite_types = ["elite_skeleton", "shadow_beast"]

        # 生成精英怪物（數量少但強大）
        elite_count = max(2, monster_count // 2)
        for _ in range(elite_count):
            x = random.randint(80, room.width - 80)
            y = random.randint(80, room.height - 80)
            elite_type = random.choice(elite_types)
            room.monsters.append(EliteMonster(x, y, elite_type, depth))

        # 可能有小Boss
        if random.random() < CAVE_CONFIG["mini_boss_rate"]:
            boss_x = room.width // 2 + random.randint(-100, 100)
            boss_y = room.height // 2 + random.randint(-100, 100)
            room.mini_boss = CaveBoss(boss_x, boss_y, depth)

        # 高品質獎勵
        for _ in range(treasure_count):
            x = random.randint(50, room.width - 50)
            y = random.randint(50, room.height - 50)
            if depth >= 15:
                chest_type = "legendary_chest"
            elif depth >= 10:
                chest_type = "epic_chest"
            else:
                chest_type = "treasure_chest"
            room.treasures.append(TreasureChest(x, y, chest_type, depth))

        print("⭐ 生成精英房間完成！")

    def _generate_puzzle_room(
        self,
        room: CaveRoom,
        monster_count: int,
        treasure_count: int,
        mineral_count: int,
    ) -> None:
        """生成謎題房間 - 需要解謎才能獲得獎勵"""
        # 幾個分散的怪物群
        group_centers = [
            (room.width // 4, room.height // 4),
            (3 * room.width // 4, room.height // 4),
            (room.width // 2, 3 * room.height // 4),
        ]

        monsters_per_group = monster_count // 3
        for center_x, center_y in group_centers:
            for _ in range(monsters_per_group):
                x = center_x + random.randint(-60, 60)
                y = center_y + random.randint(-60, 60)
                x = max(50, min(room.width - 50, x))
                y = max(50, min(room.height - 50, y))
                room.monsters.append(CaveMonster(x, y, "cave_monster"))

        # 中央獎勵區域
        center_x, center_y = room.width // 2, room.height // 2
        for _ in range(treasure_count):
            x = center_x + random.randint(-40, 40)
            y = center_y + random.randint(-40, 40)
            room.treasures.append(TreasureChest(x, y, "treasure_chest", room.depth))

        print("🧩 生成謎題房間完成！")

    def _generate_armory_room(
        self,
        room: CaveRoom,
        monster_count: int,
        treasure_count: int,
        mineral_count: int,
        depth: int,
    ) -> None:
        """生成軍械庫 - 大量高級裝備但有重兵把守"""
        # 重兵把守
        for _ in range(monster_count):
            x = random.randint(60, room.width - 60)
            y = random.randint(60, room.height - 60)

            # 軍械庫多為精英守衛
            if random.random() < 0.6:
                elite_type = random.choice(["elite_skeleton", "shadow_beast"])
                room.monsters.append(EliteMonster(x, y, elite_type, depth))
            else:
                room.monsters.append(CaveMonster(x, y, "cave_monster"))

        # 大量裝備寶箱，排列整齊
        rows = 3
        cols = treasure_count // rows
        for row in range(rows):
            for col in range(cols):
                x = (
                    100 + col * (room.width - 200) // (cols - 1)
                    if cols > 1
                    else room.width // 2
                )
                y = (
                    150 + row * (room.height - 300) // (rows - 1)
                    if rows > 1
                    else room.height // 2
                )

                # 軍械庫多為裝備類寶箱
                if depth >= 15:
                    chest_type = random.choice(["epic_chest", "legendary_chest"])
                elif depth >= 10:
                    chest_type = "epic_chest"
                else:
                    chest_type = "treasure_chest"

                room.treasures.append(TreasureChest(x, y, chest_type, depth))

        # 一些稀有礦物
        for _ in range(mineral_count // 2):
            x = random.randint(50, room.width - 50)
            y = random.randint(50, room.height - 50)
            room.minerals.append(Rock(x, y))

        print("⚔️ 生成軍械庫完成！")

    def _generate_boss_chamber(
        self,
        room: CaveRoom,
        monster_count: int,
        treasure_count: int,
        mineral_count: int,
    ) -> None:
        """生成Boss房間 - 有少量小怪和豐富獎勵"""
        # Boss房間可能有少量小怪
        minion_count = max(2, monster_count // 3)
        for _ in range(minion_count):
            x = random.randint(80, room.width - 80)
            y = random.randint(80, room.height - 80)
            # 避免太靠近中央（Boss位置）
            center_x, center_y = room.width // 2, room.height // 2
            if abs(x - center_x) < 100 and abs(y - center_y) < 100:
                continue
            room.monsters.append(CaveMonster(x, y, "cave_monster"))

        # Boss戰勝後的豐富獎勵
        reward_positions = [
            (room.width // 4, room.height // 4),
            (3 * room.width // 4, room.height // 4),
            (room.width // 4, 3 * room.height // 4),
            (3 * room.width // 4, 3 * room.height // 4),
            (room.width // 2, room.height // 6),
            (room.width // 2, 5 * room.height // 6),
        ]

        for i, (x, y) in enumerate(reward_positions[:treasure_count]):
            # Boss房間獎勵更豐富
            if room.depth >= 15:
                chest_type = "legendary_chest"
            elif room.depth >= 10:
                chest_type = "epic_chest"
            else:
                chest_type = "treasure_chest"
            room.treasures.append(TreasureChest(x, y, chest_type, room.depth))

        # 一些稀有礦物
        for _ in range(mineral_count // 2):
            x = random.randint(60, room.width - 60)
            y = random.randint(60, room.height - 60)
            room.minerals.append(Rock(x, y))

        print("👑 生成Boss房間完成！")

    def _generate_maze_room(
        self,
        room: CaveRoom,
        monster_count: int,
        treasure_count: int,
        mineral_count: int,
    ) -> None:
        """生成迷宮房間 - 礦物較多，怪物分散"""
        # 礦物形成"牆壁"般的分佈
        for _ in range(mineral_count):
            if random.random() < 0.3:  # 30%機率在邊緣
                if random.random() < 0.5:
                    x = random.choice(
                        [
                            random.randint(20, 60),
                            random.randint(room.width - 60, room.width - 20),
                        ]
                    )
                    y = random.randint(30, room.height - 30)
                else:
                    x = random.randint(30, room.width - 30)
                    y = random.choice(
                        [
                            random.randint(20, 60),
                            random.randint(room.height - 60, room.height - 20),
                        ]
                    )
            else:
                x = random.randint(30, room.width - 30)
                y = random.randint(30, room.height - 30)
            room.minerals.append(Rock(x, y))

        # 少量怪物分散放置
        for _ in range(monster_count):
            x = random.randint(60, room.width - 60)
            y = random.randint(60, room.height - 60)
            room.monsters.append(CaveMonster(x, y, "cave_monster"))

        # 寶箱隱藏在角落
        for _ in range(treasure_count):
            corner_areas = [
                (random.randint(20, 80), random.randint(20, 80)),
                (
                    random.randint(room.width - 80, room.width - 20),
                    random.randint(20, 80),
                ),
                (
                    random.randint(20, 80),
                    random.randint(room.height - 80, room.height - 20),
                ),
                (
                    random.randint(room.width - 80, room.width - 20),
                    random.randint(room.height - 80, room.height - 20),
                ),
            ]
            x, y = random.choice(corner_areas)
            room.treasures.append(TreasureChest(x, y, "treasure_chest", room.depth))

    def _generate_trap_room(
        self,
        room: CaveRoom,
        monster_count: int,
        treasure_count: int,
        mineral_count: int,
    ) -> None:
        """生成陷阱房間 - 危險但獎勵豐厚"""
        # 中央有誘人的寶箱
        center_x, center_y = room.width // 2, room.height // 2
        room.treasures.append(
            TreasureChest(center_x, center_y, "treasure_chest", room.depth)
        )

        # 周圍有守衛怪物
        guard_positions = [
            (center_x - 80, center_y - 80),
            (center_x + 80, center_y - 80),
            (center_x - 80, center_y + 80),
            (center_x + 80, center_y + 80),
        ]

        for i, (x, y) in enumerate(guard_positions[:monster_count]):
            room.monsters.append(CaveMonster(x, y, "cave_monster"))

        # 其餘寶箱分散放置
        for _ in range(treasure_count - 1):
            x = random.randint(40, room.width - 40)
            y = random.randint(40, room.height - 40)
            room.treasures.append(TreasureChest(x, y, "treasure_chest", room.depth))

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

            # 更新Boss
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
        """繪製洞穴場景 - 包含Boss、高密度物件、視線範圍限制和邊界"""
        if not self.in_cave or not self.current_room:
            return

        # 首先繪製洞穴邊界
        self._draw_cave_boundaries(screen, camera)

        # 計算黑暗程度
        darkness_level = self.current_room.darkness_level
        light_radius = CAVE_CONFIG["darkness_visibility"]  # 默認黑暗中可見距離

        if self.player_torch_time > 0:
            # 有光源時擴大可見範圍
            light_strength = min(1.0, self.player_torch_time / 60.0)  # 1分鐘內逐漸變暗
            darkness_level *= 1.0 - light_strength * 0.7
            light_radius = CAVE_CONFIG["light_radius"]  # 完整照明半徑

        # 繪製黑暗遮罩
        darkness_alpha = int(darkness_level * 200)  # 0-200的透明度
        if darkness_alpha > 0:
            dark_surface = pygame.Surface(
                (WINDOW_CONFIG["width"], WINDOW_CONFIG["height"])
            )
            dark_surface.set_alpha(darkness_alpha)
            dark_surface.fill((0, 0, 0))
            screen.blit(dark_surface, (0, 0))

        # 繪製洞穴物件（只繪製視線範圍內的）
        light_alpha = 255 - darkness_alpha

        # 玩家位置（假設在螢幕中央）
        player_screen_x = WINDOW_CONFIG["width"] // 2
        player_screen_y = WINDOW_CONFIG["height"] // 2

        # 優先繪製Boss（最顯眼）
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

                    # 檢查視線距離
                    distance = math.sqrt(
                        (screen_x - player_screen_x) ** 2
                        + (screen_y - player_screen_y) ** 2
                    )

                    if distance <= light_radius:
                        # 根據距離調整透明度
                        distance_alpha = max(
                            0, min(255, int(255 * (1 - distance / light_radius)))
                        )
                        final_alpha = min(light_alpha, distance_alpha)
                        self.current_room.boss.draw_with_camera_alpha(
                            screen, screen_x, screen_y, final_alpha
                        )
            else:
                # 非相機模式的舊邏輯
                self.current_room.boss.draw_with_camera_alpha(
                    screen,
                    int(self.current_room.boss.x),
                    int(self.current_room.boss.y),
                    light_alpha,
                )

        # 繪製普通怪物（視線範圍限制）
        for monster in self.current_room.monsters:
            if monster.active:
                if camera:
                    if camera.is_visible(
                        monster.x, monster.y, monster.width, monster.height
                    ):
                        screen_x, screen_y = camera.world_to_screen(
                            monster.x, monster.y
                        )

                        # 檢查視線距離
                        distance = math.sqrt(
                            (screen_x - player_screen_x) ** 2
                            + (screen_y - player_screen_y) ** 2
                        )

                        if distance <= light_radius:
                            # 根據距離調整透明度
                            distance_alpha = max(
                                0, min(255, int(255 * (1 - distance / light_radius)))
                            )
                            final_alpha = min(light_alpha, distance_alpha)
                            monster.draw_with_camera_alpha(
                                screen, screen_x, screen_y, final_alpha
                            )
                else:
                    monster.draw(screen, light_alpha)

        # 繪製寶箱（視線範圍限制）
        for treasure in self.current_room.treasures:
            if treasure.active:
                if camera:
                    if camera.is_visible(
                        treasure.x, treasure.y, treasure.width, treasure.height
                    ):
                        screen_x, screen_y = camera.world_to_screen(
                            treasure.x, treasure.y
                        )

                        # 檢查視線距離
                        distance = math.sqrt(
                            (screen_x - player_screen_x) ** 2
                            + (screen_y - player_screen_y) ** 2
                        )

                        if distance <= light_radius:
                            # 根據距離調整透明度 - 寶箱應該更閃亮
                            distance_alpha = max(
                                50, min(255, int(255 * (1 - distance / light_radius)))
                            )
                            final_alpha = min(light_alpha, distance_alpha)
                            treasure.draw_with_camera_alpha(
                                screen, screen_x, screen_y, final_alpha
                            )
                else:
                    treasure.draw(screen, light_alpha)

        # 繪製照明範圍指示器（可選）
        if self.player_torch_time > 0:
            # 繪製光圈效果
            light_surface = pygame.Surface(
                (light_radius * 2, light_radius * 2), pygame.SRCALPHA
            )
            # 從中心到邊緣的漸變光暈
            for r in range(int(light_radius), 0, -5):
                alpha = int(30 * (r / light_radius))  # 漸變透明度
                pygame.draw.circle(
                    light_surface,
                    (255, 255, 150, alpha),
                    (int(light_radius), int(light_radius)),
                    r,
                )

            screen.blit(
                light_surface,
                (player_screen_x - light_radius, player_screen_y - light_radius),
            )

    def _draw_cave_boundaries(self, screen: pygame.Surface, camera=None) -> None:
        """繪製地下城邊界和環境效果"""
        if not self.current_room:
            return

        room_width = CAVE_CONFIG["room_size"]["width"]
        room_height = CAVE_CONFIG["room_size"]["height"]
        room_type = getattr(self.current_room, "room_type", "standard")

        # 根據房間類型選擇顏色主題
        if room_type == "treasure_room":
            wall_color = (120, 100, 60)  # 金黃色調的石牆
            accent_color = (200, 180, 100)  # 金色裝飾
        elif room_type == "boss_chamber":
            wall_color = (100, 40, 40)  # 深紅色石牆
            accent_color = (180, 60, 60)  # 紅色裝飾
        elif room_type == "maze":
            wall_color = (60, 80, 100)  # 藍灰色石牆
            accent_color = (100, 120, 140)  # 藍色裝飾
        elif room_type == "trap_room":
            wall_color = (80, 40, 80)  # 紫色調石牆
            accent_color = (140, 80, 140)  # 紫色裝飾
        else:
            wall_color = (80, 60, 40)  # 標準棕色石牆
            accent_color = (120, 100, 80)  # 淺棕色裝飾

        if camera:
            # 繪製厚實的地下城牆壁
            wall_thickness = 8

            # 左邊界
            left_screen_x, left_screen_y = camera.world_to_screen(0, 0)
            if (
                left_screen_x >= -wall_thickness
                and left_screen_x <= WINDOW_CONFIG["width"] + wall_thickness
            ):
                pygame.draw.line(
                    screen,
                    wall_color,
                    (left_screen_x, 0),
                    (left_screen_x, WINDOW_CONFIG["height"]),
                    wall_thickness,
                )
                # 內側裝飾線
                pygame.draw.line(
                    screen,
                    accent_color,
                    (left_screen_x + wall_thickness // 2, 0),
                    (left_screen_x + wall_thickness // 2, WINDOW_CONFIG["height"]),
                    2,
                )

            # 右邊界
            right_screen_x, right_screen_y = camera.world_to_screen(room_width, 0)
            if (
                right_screen_x >= -wall_thickness
                and right_screen_x <= WINDOW_CONFIG["width"] + wall_thickness
            ):
                pygame.draw.line(
                    screen,
                    wall_color,
                    (right_screen_x, 0),
                    (right_screen_x, WINDOW_CONFIG["height"]),
                    wall_thickness,
                )
                pygame.draw.line(
                    screen,
                    accent_color,
                    (right_screen_x - wall_thickness // 2, 0),
                    (right_screen_x - wall_thickness // 2, WINDOW_CONFIG["height"]),
                    2,
                )

            # 上邊界
            top_screen_x, top_screen_y = camera.world_to_screen(0, 0)
            if (
                top_screen_y >= -wall_thickness
                and top_screen_y <= WINDOW_CONFIG["height"] + wall_thickness
            ):
                pygame.draw.line(
                    screen,
                    wall_color,
                    (0, top_screen_y),
                    (WINDOW_CONFIG["width"], top_screen_y),
                    wall_thickness,
                )
                pygame.draw.line(
                    screen,
                    accent_color,
                    (0, top_screen_y + wall_thickness // 2),
                    (WINDOW_CONFIG["width"], top_screen_y + wall_thickness // 2),
                    2,
                )

            # 下邊界
            bottom_screen_x, bottom_screen_y = camera.world_to_screen(0, room_height)
            if (
                bottom_screen_y >= -wall_thickness
                and bottom_screen_y <= WINDOW_CONFIG["height"] + wall_thickness
            ):
                pygame.draw.line(
                    screen,
                    wall_color,
                    (0, bottom_screen_y),
                    (WINDOW_CONFIG["width"], bottom_screen_y),
                    wall_thickness,
                )
                pygame.draw.line(
                    screen,
                    accent_color,
                    (0, bottom_screen_y - wall_thickness // 2),
                    (WINDOW_CONFIG["width"], bottom_screen_y - wall_thickness // 2),
                    2,
                )

    def _draw_cave_boundaries(self, screen: pygame.Surface, camera=None) -> None:
        """繪製地下城邊界和環境效果"""
        if not self.current_room:
            return

        room_width = CAVE_CONFIG["room_size"]["width"]
        room_height = CAVE_CONFIG["room_size"]["height"]
        room_type = getattr(self.current_room, "room_type", "standard")

        # 根據房間類型選擇顏色主題
        if room_type == "treasure_room":
            wall_color = (120, 100, 60)  # 金黃色調的石牆
            accent_color = (200, 180, 100)  # 金色裝飾
        elif room_type == "boss_chamber":
            wall_color = (100, 40, 40)  # 深紅色石牆
            accent_color = (180, 60, 60)  # 紅色裝飾
        elif room_type == "maze":
            wall_color = (60, 80, 100)  # 藍灰色石牆
            accent_color = (100, 120, 140)  # 藍色裝飾
        elif room_type == "trap_room":
            wall_color = (80, 40, 80)  # 紫色調石牆
            accent_color = (140, 80, 140)  # 紫色裝飾
        else:
            wall_color = (80, 60, 40)  # 標準棕色石牆
            accent_color = (120, 100, 80)  # 淺棕色裝飾

        if camera:
            # 繪製厚實的地下城牆壁
            wall_thickness = 8

            # 左邊界
            left_screen_x, left_screen_y = camera.world_to_screen(0, 0)
            if (
                left_screen_x >= -wall_thickness
                and left_screen_x <= WINDOW_CONFIG["width"] + wall_thickness
            ):
                pygame.draw.line(
                    screen,
                    wall_color,
                    (left_screen_x, 0),
                    (left_screen_x, WINDOW_CONFIG["height"]),
                    wall_thickness,
                )

            # 右邊界
            right_screen_x, right_screen_y = camera.world_to_screen(room_width, 0)
            if (
                right_screen_x >= -wall_thickness
                and right_screen_x <= WINDOW_CONFIG["width"] + wall_thickness
            ):
                pygame.draw.line(
                    screen,
                    wall_color,
                    (right_screen_x, 0),
                    (right_screen_x, WINDOW_CONFIG["height"]),
                    wall_thickness,
                )

            # 上邊界
            top_screen_x, top_screen_y = camera.world_to_screen(0, 0)
            if (
                top_screen_y >= -wall_thickness
                and top_screen_y <= WINDOW_CONFIG["height"] + wall_thickness
            ):
                pygame.draw.line(
                    screen,
                    wall_color,
                    (0, top_screen_y),
                    (WINDOW_CONFIG["width"], top_screen_y),
                    wall_thickness,
                )

            # 下邊界
            bottom_screen_x, bottom_screen_y = camera.world_to_screen(0, room_height)
            if (
                bottom_screen_y >= -wall_thickness
                and bottom_screen_y <= WINDOW_CONFIG["height"] + wall_thickness
            ):
                pygame.draw.line(
                    screen,
                    wall_color,
                    (0, bottom_screen_y),
                    (WINDOW_CONFIG["width"], bottom_screen_y),
                    wall_thickness,
                )

            # 繪製房間類型特殊裝飾
            self._draw_room_decorations(
                screen, camera, room_type, wall_color, accent_color
            )
        else:
            # 非相機模式的簡單邊界
            boundary_color = (100, 100, 100)
            pygame.draw.rect(screen, boundary_color, (0, 0, room_width, room_height), 3)

    def _draw_room_decorations(
        self,
        screen: pygame.Surface,
        camera,
        room_type: str,
        wall_color: tuple,
        accent_color: tuple,
    ) -> None:
        """根據房間類型繪製特殊裝飾"""
        if room_type == "treasure_room":
            self._draw_treasure_room_effects(screen, camera, accent_color)
        elif room_type == "boss_chamber":
            self._draw_boss_chamber_effects(screen, camera, accent_color)
        elif room_type == "maze":
            self._draw_maze_effects(screen, camera, accent_color)
        elif room_type == "trap_room":
            self._draw_trap_room_effects(screen, camera, accent_color)

    def _draw_treasure_room_effects(
        self, screen: pygame.Surface, camera, accent_color: tuple
    ) -> None:
        """繪製寶藏房間的金色光芒效果"""
        room_width = CAVE_CONFIG["room_size"]["width"]
        room_height = CAVE_CONFIG["room_size"]["height"]

        # 在房間中央繪製金色光芒
        center_x, center_y = room_width // 2, room_height // 2
        screen_x, screen_y = camera.world_to_screen(center_x, center_y)

        if (
            0 <= screen_x <= WINDOW_CONFIG["width"]
            and 0 <= screen_y <= WINDOW_CONFIG["height"]
        ):
            # 繪製金色光環
            for i in range(3):
                radius = 30 + i * 20
                alpha = 50 - i * 15
                glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    glow_surface, (*accent_color, alpha), (radius, radius), radius
                )
                screen.blit(glow_surface, (screen_x - radius, screen_y - radius))

    def _draw_boss_chamber_effects(
        self, screen: pygame.Surface, camera, accent_color: tuple
    ) -> None:
        """繪製Boss房間的威壓氣場效果"""
        room_width = CAVE_CONFIG["room_size"]["width"]
        room_height = CAVE_CONFIG["room_size"]["height"]

        # 繪製紅色脈動效果
        center_x, center_y = room_width // 2, room_height // 2
        screen_x, screen_y = camera.world_to_screen(center_x, center_y)

        if (
            0 <= screen_x <= WINDOW_CONFIG["width"]
            and 0 <= screen_y <= WINDOW_CONFIG["height"]
        ):
            # 脈動效果（隨時間變化）
            pulse = int(50 + 30 * math.sin(time.time() * 2))
            danger_surface = pygame.Surface((200, 200), pygame.SRCALPHA)
            pygame.draw.circle(danger_surface, (*accent_color, pulse), (100, 100), 100)
            screen.blit(danger_surface, (screen_x - 100, screen_y - 100))

    def _draw_maze_effects(
        self, screen: pygame.Surface, camera, accent_color: tuple
    ) -> None:
        """繪製迷宮房間的神秘藍光效果"""
        room_width = CAVE_CONFIG["room_size"]["width"]
        room_height = CAVE_CONFIG["room_size"]["height"]

        # 在多個位置繪製小的藍色光點
        light_positions = [
            (room_width // 4, room_height // 4),
            (3 * room_width // 4, room_height // 4),
            (room_width // 4, 3 * room_height // 4),
            (3 * room_width // 4, 3 * room_height // 4),
        ]

        for world_x, world_y in light_positions:
            screen_x, screen_y = camera.world_to_screen(world_x, world_y)
            if (
                0 <= screen_x <= WINDOW_CONFIG["width"]
                and 0 <= screen_y <= WINDOW_CONFIG["height"]
            ):
                mystery_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
                pygame.draw.circle(mystery_surface, (*accent_color, 40), (30, 30), 30)
                screen.blit(mystery_surface, (screen_x - 30, screen_y - 30))

    def _draw_trap_room_effects(
        self, screen: pygame.Surface, camera, accent_color: tuple
    ) -> None:
        """繪製陷阱房間的危險紫色效果"""
        room_width = CAVE_CONFIG["room_size"]["width"]
        room_height = CAVE_CONFIG["room_size"]["height"]

        # 繪製危險的紫色邊緣效果
        corners = [
            (50, 50),
            (room_width - 50, 50),
            (50, room_height - 50),
            (room_width - 50, room_height - 50),
        ]

        for world_x, world_y in corners:
            screen_x, screen_y = camera.world_to_screen(world_x, world_y)
            if (
                0 <= screen_x <= WINDOW_CONFIG["width"]
                and 0 <= screen_y <= WINDOW_CONFIG["height"]
            ):
                warning_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
                pygame.draw.circle(warning_surface, (*accent_color, 60), (20, 20), 20)
                screen.blit(warning_surface, (screen_x - 20, screen_y - 20))

    def _draw_corner_decorations(
        self, screen: pygame.Surface, camera, room_width: int, room_height: int
    ) -> None:
        """繪製洞穴角落的岩石裝飾"""
        corner_color = (60, 40, 30)  # 深棕色岩石
        corner_size = 30

        corners = [
            (0, 0),  # 左上
            (room_width - corner_size, 0),  # 右上
            (0, room_height - corner_size),  # 左下
            (room_width - corner_size, room_height - corner_size),  # 右下
        ]

        for world_x, world_y in corners:
            screen_x, screen_y = camera.world_to_screen(world_x, world_y)

            # 檢查角落是否在螢幕可見範圍內
            if (
                screen_x >= -corner_size
                and screen_x <= WINDOW_CONFIG["width"]
                and screen_y >= -corner_size
                and screen_y <= WINDOW_CONFIG["height"]
            ):

                # 繪製岩石角落
                pygame.draw.rect(
                    screen, corner_color, (screen_x, screen_y, corner_size, corner_size)
                )

                # 添加一些紋理效果
                for i in range(3):
                    offset_x = i * 8
                    offset_y = i * 6
                    if (
                        screen_x + offset_x < WINDOW_CONFIG["width"]
                        and screen_y + offset_y < WINDOW_CONFIG["height"]
                    ):
                        pygame.draw.circle(
                            screen,
                            (70, 50, 40),
                            (screen_x + offset_x + 5, screen_y + offset_y + 5),
                            3,
                        )

    def get_cave_objects(self) -> List[GameObject]:
        """獲取當前洞穴中的所有物件 - 包含Boss"""
        if not self.in_cave or not self.current_room:
            return []

        objects = []

        # 加入Boss（優先級最高）
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
