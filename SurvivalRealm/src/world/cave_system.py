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
    """洞穴房間數據類"""

    depth: int  # 深度層級
    width: int = 800
    height: int = 600
    monsters: List[GameObject] = None
    treasures: List[GameObject] = None
    minerals: List[GameObject] = None
    has_exit: bool = True  # 是否有出口
    darkness_level: float = 0.8  # 黑暗程度 (0.0-1.0)

    def __post_init__(self):
        if self.monsters is None:
            self.monsters = []
        if self.treasures is None:
            self.treasures = []
        if self.minerals is None:
            self.minerals = []


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

        print(f"🕳️ 洞穴{monster_type}生成於 ({x:.0f}, {y:.0f})")

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
    """洞穴系統管理器"""

    def __init__(self):
        self.in_cave = False
        self.current_room = None
        self.player_torch_time = 0  # 玩家火把剩餘時間
        self.darkness_damage_timer = 0

    def enter_cave(self, depth: int = 1) -> CaveRoom:
        """進入洞穴"""
        self.in_cave = True
        self.current_room = self._generate_cave_room(depth)
        print(f"🕳️ 進入洞穴第 {depth} 層")
        return self.current_room

    def exit_cave(self) -> None:
        """退出洞穴"""
        self.in_cave = False
        self.current_room = None
        self.player_torch_time = 0
        print("🌅 返回地表")

    def _generate_cave_room(self, depth: int) -> CaveRoom:
        """生成洞穴房間"""
        room = CaveRoom(depth=depth)

        # 根據深度調整難度
        monster_count = min(depth * 2, 8)
        treasure_count = max(1, depth // 2)
        mineral_count = depth * 3

        # 生成怪物
        for _ in range(monster_count):
            x = random.randint(50, room.width - 100)
            y = random.randint(50, room.height - 100)
            monster_type = random.choice(["cave_monster", "cave_spider"])
            room.monsters.append(CaveMonster(x, y, monster_type))

        # 生成寶箱
        for _ in range(treasure_count):
            x = random.randint(50, room.width - 100)
            y = random.randint(50, room.height - 100)
            room.treasures.append(TreasureChest(x, y))

        # 生成礦物點 (簡化為寶物掉落)
        # 實際遊戲中可以創建特殊的礦物節點

        return room

    def update(self, delta_time: float, player: "Player") -> List[str]:
        """更新洞穴系統"""
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

        # 更新怪物
        if self.current_room:
            player_center_x = player.x + player.width // 2
            player_center_y = player.y + player.height // 2

            for monster in self.current_room.monsters:
                if monster.active:
                    monster.update(
                        delta_time, player_center_x, player_center_y, player_in_darkness
                    )

                    # 檢查怪物主動攻擊
                    if monster.can_attack():
                        # 檢查是否在攻擊範圍內
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
        """繪製洞穴場景"""
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

        # 繪製怪物
        for monster in self.current_room.monsters:
            if monster.active:
                if camera:
                    # 使用相機系統繪製
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
                    # 使用相機系統繪製
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
        """獲取當前洞穴中的所有物件"""
        if not self.in_cave or not self.current_room:
            return []

        objects = []
        objects.extend([m for m in self.current_room.monsters if m.active])
        objects.extend([t for t in self.current_room.treasures if t.active])

        return objects


# 全域洞穴系統實例
cave_system = CaveSystem()
