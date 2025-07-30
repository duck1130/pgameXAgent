import pygame
import sys
import random
import os

# 初始化 pygame
pygame.init()

# 遊戲視窗配置
WINDOW_CONFIG = {"width": 800, "height": 600, "title": "敲磚塊遊戲"}

# 字體配置 - 使用系統內建微軟正黑體
FONT_PATH = "C:\\Windows\\Fonts\\msjh.ttc"  # 微軟正黑體絕對路徑
FONT_SIZE_LARGE = 36
FONT_SIZE_SMALL = 24

# 顏色定義
COLORS = {
    "BACKGROUND": (20, 20, 50),
    "PADDLE": (192, 192, 192),
    "BALL": (255, 255, 255),
    "UI_TEXT": (255, 255, 0),
    "BORDER": (100, 100, 100),
}

# 普通磚塊配置
NORMAL_BRICKS = {
    "RED": {"color": (255, 100, 100), "points": 10, "hits_required": 1},
    "ORANGE": {"color": (255, 165, 0), "points": 15, "hits_required": 1},
    "YELLOW": {"color": (255, 255, 100), "points": 20, "hits_required": 1},
    "GREEN": {"color": (100, 255, 100), "points": 25, "hits_required": 1},
    "BLUE": {"color": (100, 100, 255), "points": 30, "hits_required": 1},
}

# 特殊磚塊配置
SPECIAL_BRICKS = {
    "SILVER": {
        "color": (192, 192, 192),
        "points": 50,
        "hits_required": 2,
        "effect": "EXTRA_BALL",
    },
    "GOLD": {
        "color": (255, 215, 0),
        "points": 100,
        "hits_required": 1,
        "effect": "SCORE_MULTIPLIER",
    },
    "PURPLE": {
        "color": (128, 0, 128),
        "points": 75,
        "hits_required": 1,
        "effect": "PADDLE_EXPAND",
    },
    "PINK": {
        "color": (255, 192, 203),
        "points": 60,
        "hits_required": 1,
        "effect": "SLOW_BALL",
    },
    "DARK_BLUE": {
        "color": (0, 0, 139),
        "points": 40,
        "hits_required": 3,
        "effect": None,
    },
}


class Ball:
    """遊戲球體類別"""

    def __init__(self, x, y, speed=5):
        self.x = x
        self.y = y
        self.radius = 8
        self.speed = speed
        self.dx = speed * random.choice([-1, 1])
        self.dy = -speed

    def update(self):
        """更新球體位置"""
        self.x += self.dx
        self.y += self.dy

        # 邊界碰撞檢測
        if self.x <= self.radius or self.x >= WINDOW_CONFIG["width"] - self.radius:
            self.dx = -self.dx
        if self.y <= self.radius:
            self.dy = -self.dy

    def draw(self, screen):
        """繪製球體"""
        pygame.draw.circle(
            screen, COLORS["BALL"], (int(self.x), int(self.y)), self.radius
        )

    def get_rect(self):
        """獲取球體矩形範圍"""
        return pygame.Rect(
            self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2
        )


class Paddle:
    """玩家擋板類別"""

    def __init__(self, x, y):
        self.width = 80
        self.height = 15
        self.x = x - self.width // 2
        self.y = y
        self.speed = 8
        self.original_width = 80
        self.expand_timer = 0

    def update(self, mouse_x):
        """根據滑鼠位置更新擋板"""
        self.x = mouse_x - self.width // 2

        # 限制擋板在螢幕範圍內
        if self.x < 0:
            self.x = 0
        elif self.x > WINDOW_CONFIG["width"] - self.width:
            self.x = WINDOW_CONFIG["width"] - self.width

        # 處理擴展效果計時
        if self.expand_timer > 0:
            self.expand_timer -= 1
            if self.expand_timer <= 0:
                self.width = self.original_width

    def expand(self):
        """擋板擴展特效"""
        self.width = 120
        self.expand_timer = 1200  # 20秒 (60 FPS)

    def draw(self, screen):
        """繪製擋板"""
        color = COLORS["PADDLE"]
        if self.expand_timer > 0:
            # 擴展時變成金色
            color = (255, 215, 0)
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        """獲取擋板矩形範圍"""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Brick:
    """磚塊基礎類別"""

    def __init__(self, x, y, brick_type, brick_data):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 25
        self.brick_type = brick_type
        self.color = brick_data["color"]
        self.points = brick_data["points"]
        self.hits_required = brick_data["hits_required"]
        self.current_hits = 0
        self.is_destroyed = False
        self.special_effect = brick_data.get("effect", None)

    def hit(self):
        """磚塊被擊中"""
        self.current_hits += 1
        if self.current_hits >= self.hits_required:
            self.is_destroyed = True
            return True, self.special_effect
        return False, None

    def draw(self, screen):
        """繪製磚塊"""
        if not self.is_destroyed:
            # 根據被擊中次數調整透明度
            alpha = 255 - (self.current_hits * 80)
            if alpha < 100:
                alpha = 100

            # 創建帶透明度的表面
            brick_surface = pygame.Surface((self.width, self.height))
            brick_surface.set_alpha(alpha)
            brick_surface.fill(self.color)

            screen.blit(brick_surface, (self.x, self.y))

            # 繪製邊框
            pygame.draw.rect(
                screen, (255, 255, 255), (self.x, self.y, self.width, self.height), 1
            )

    def get_rect(self):
        """獲取磚塊矩形範圍"""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class ScoreManager:
    """計分系統管理器"""

    def __init__(self):
        self.current_score = 0
        self.high_score = 0
        self.lives = 3
        self.combo_multiplier = 1.0
        self.combo_count = 0
        self.score_multiplier_timer = 0

    def add_score(self, base_points):
        """增加分數"""
        # 應用連擊和特殊倍數
        final_score = int(base_points * self.combo_multiplier)
        if self.score_multiplier_timer > 0:
            final_score *= 2

        self.current_score += final_score
        self.combo_count += 1
        self.combo_multiplier = min(3.0, 1.0 + (self.combo_count * 0.1))

        # 更新最高分
        if self.current_score > self.high_score:
            self.high_score = self.current_score

    def reset_combo(self):
        """重置連擊"""
        self.combo_count = 0
        self.combo_multiplier = 1.0

    def lose_life(self):
        """失去一條生命"""
        self.lives -= 1
        self.reset_combo()

    def activate_score_multiplier(self):
        """啟動分數倍增器"""
        self.score_multiplier_timer = 900  # 15秒

    def update(self):
        """更新計時器"""
        if self.score_multiplier_timer > 0:
            self.score_multiplier_timer -= 1


class BreakoutGame:
    """主遊戲控制器"""

    def __init__(self):
        self.screen = pygame.display.set_mode(
            (WINDOW_CONFIG["width"], WINDOW_CONFIG["height"])
        )
        pygame.display.set_caption(WINDOW_CONFIG["title"])
        self.clock = pygame.time.Clock()

        # 字體初始化 - 使用絕對路徑載入中文字體
        try:
            if os.path.exists(FONT_PATH):
                self.font = pygame.font.Font(FONT_PATH, FONT_SIZE_LARGE)
                self.small_font = pygame.font.Font(FONT_PATH, FONT_SIZE_SMALL)
                print("成功載入微軟正黑體字體")
            else:
                # 備用字體方案
                self.font = pygame.font.Font(None, FONT_SIZE_LARGE)
                self.small_font = pygame.font.Font(None, FONT_SIZE_SMALL)
                print("警告: 無法找到微軟正黑體，使用預設字體")
        except pygame.error as e:
            print(f"字體載入失敗: {e}，使用預設字體")
            self.font = pygame.font.Font(None, FONT_SIZE_LARGE)
            self.small_font = pygame.font.Font(None, FONT_SIZE_SMALL)

        # 遊戲物件初始化
        self.paddle = Paddle(WINDOW_CONFIG["width"] // 2, WINDOW_CONFIG["height"] - 40)
        self.balls = []
        self.bricks = []
        self.score_manager = ScoreManager()

        # 遊戲狀態
        self.game_state = "WAITING"  # WAITING, PLAYING, GAME_OVER
        self.ball_slow_timer = 0

        self.reset_game()

    def create_bricks(self):
        """創建磚塊陣列"""
        self.bricks = []
        brick_rows = 8
        brick_cols = 12

        for row in range(brick_rows):
            for col in range(brick_cols):
                x = col * 65 + 35
                y = row * 30 + 80

                # 20% 機率生成特殊磚塊
                if random.random() < 0.2:
                    brick_type = random.choice(list(SPECIAL_BRICKS.keys()))
                    brick_data = SPECIAL_BRICKS[brick_type]
                else:
                    brick_type = random.choice(list(NORMAL_BRICKS.keys()))
                    brick_data = NORMAL_BRICKS[brick_type]

                brick = Brick(x, y, brick_type, brick_data)
                self.bricks.append(brick)

    def reset_game(self):
        """重置遊戲"""
        self.create_bricks()
        self.balls = [Ball(WINDOW_CONFIG["width"] // 2, WINDOW_CONFIG["height"] - 100)]
        self.game_state = "WAITING"
        self.ball_slow_timer = 0

    def handle_collisions(self):
        """處理碰撞檢測"""
        for ball in self.balls[:]:  # 使用切片複製列表
            ball_rect = ball.get_rect()

            # 球與擋板碰撞
            paddle_rect = self.paddle.get_rect()
            if ball_rect.colliderect(paddle_rect) and ball.dy > 0:
                # 計算反彈角度
                hit_pos = (ball.x - self.paddle.x) / self.paddle.width
                ball.dx = ball.speed * (hit_pos - 0.5) * 2
                ball.dy = -abs(ball.dy)

            # 球與磚塊碰撞
            for brick in self.bricks[:]:
                if not brick.is_destroyed and ball_rect.colliderect(brick.get_rect()):
                    # 判斷碰撞方向
                    if abs(ball.x - (brick.x + brick.width / 2)) > abs(
                        ball.y - (brick.y + brick.height / 2)
                    ):
                        ball.dx = -ball.dx
                    else:
                        ball.dy = -ball.dy

                    # 處理磚塊被擊中
                    destroyed, effect = brick.hit()
                    if destroyed:
                        self.score_manager.add_score(brick.points)
                        if effect:
                            self.trigger_special_effect(effect)
                    break

            # 檢查球是否掉出底部
            if ball.y > WINDOW_CONFIG["height"]:
                self.balls.remove(ball)
                if not self.balls:  # 沒有球了
                    self.score_manager.lose_life()
                    if self.score_manager.lives <= 0:
                        self.game_state = "GAME_OVER"
                    else:
                        self.balls = [
                            Ball(
                                WINDOW_CONFIG["width"] // 2,
                                WINDOW_CONFIG["height"] - 100,
                            )
                        ]
                        self.game_state = "WAITING"

        # 清理已摧毀的磚塊
        self.bricks = [brick for brick in self.bricks if not brick.is_destroyed]

        # 檢查勝利條件
        if not self.bricks:
            self.score_manager.current_score += 1000  # 通關獎勵
            self.reset_game()

    def trigger_special_effect(self, effect):
        """觸發特殊效果"""
        if effect == "EXTRA_BALL":
            # 增加額外球體
            new_ball = Ball(self.balls[0].x, self.balls[0].y)
            new_ball.dx = -new_ball.dx  # 反方向
            self.balls.append(new_ball)

        elif effect == "SCORE_MULTIPLIER":
            self.score_manager.activate_score_multiplier()

        elif effect == "PADDLE_EXPAND":
            self.paddle.expand()

        elif effect == "SLOW_BALL":
            self.ball_slow_timer = 600  # 10秒
            for ball in self.balls:
                ball.speed = 2.5
                ball.dx = ball.dx / 2
                ball.dy = ball.dy / 2

    def update(self):
        """更新遊戲狀態"""
        if self.game_state == "PLAYING":
            # 更新所有球體
            for ball in self.balls:
                ball.update()

            # 處理球速恢復
            if self.ball_slow_timer > 0:
                self.ball_slow_timer -= 1
                if self.ball_slow_timer <= 0:
                    for ball in self.balls:
                        ball.speed = 5
                        ball.dx = ball.dx * 2
                        ball.dy = ball.dy * 2

            self.handle_collisions()

        # 更新擋板 (滑鼠控制)
        mouse_x, _ = pygame.mouse.get_pos()
        self.paddle.update(mouse_x)

        # 更新計分系統
        self.score_manager.update()

    def draw_ui(self):
        """繪製 UI 介面"""
        # 分數顯示
        score_text = self.font.render(
            f"分數: {self.score_manager.current_score}", True, COLORS["UI_TEXT"]
        )
        self.screen.blit(score_text, (10, 10))

        # 生命值顯示
        lives_text = self.font.render(
            f"生命: {'♥' * self.score_manager.lives}", True, COLORS["UI_TEXT"]
        )
        self.screen.blit(lives_text, (10, 45))

        # 最高分顯示
        high_score_text = self.small_font.render(
            f"最高分: {self.score_manager.high_score}", True, COLORS["UI_TEXT"]
        )
        self.screen.blit(high_score_text, (WINDOW_CONFIG["width"] - 150, 10))

        # 連擊顯示
        if self.score_manager.combo_count > 0:
            combo_text = self.small_font.render(
                f"連擊 x{self.score_manager.combo_count}", True, (255, 100, 100)
            )
            self.screen.blit(combo_text, (WINDOW_CONFIG["width"] - 150, 35))

        # 特殊效果提示
        effects_y = WINDOW_CONFIG["height"] - 80
        if self.score_manager.score_multiplier_timer > 0:
            effect_text = self.small_font.render("分數 x2!", True, (255, 215, 0))
            self.screen.blit(effect_text, (10, effects_y))
            effects_y -= 25

        if self.paddle.expand_timer > 0:
            effect_text = self.small_font.render("擋板擴展!", True, (255, 215, 0))
            self.screen.blit(effect_text, (10, effects_y))
            effects_y -= 25

        if self.ball_slow_timer > 0:
            effect_text = self.small_font.render("球速減慢!", True, (255, 215, 0))
            self.screen.blit(effect_text, (10, effects_y))

        # 遊戲狀態提示
        if self.game_state == "WAITING":
            hint_text = self.font.render("按任意鍵開始遊戲", True, COLORS["UI_TEXT"])
            text_rect = hint_text.get_rect(
                center=(WINDOW_CONFIG["width"] // 2, WINDOW_CONFIG["height"] // 2)
            )
            self.screen.blit(hint_text, text_rect)

        elif self.game_state == "GAME_OVER":
            game_over_text = self.font.render(
                "遊戲結束！按 R 重新開始", True, (255, 100, 100)
            )
            text_rect = game_over_text.get_rect(
                center=(WINDOW_CONFIG["width"] // 2, WINDOW_CONFIG["height"] // 2)
            )
            self.screen.blit(game_over_text, text_rect)

    def draw(self):
        """繪製遊戲畫面"""
        # 清除螢幕
        self.screen.fill(COLORS["BACKGROUND"])

        # 繪製所有磚塊
        for brick in self.bricks:
            brick.draw(self.screen)

        # 繪製擋板
        self.paddle.draw(self.screen)

        # 繪製所有球體
        for ball in self.balls:
            ball.draw(self.screen)

        # 繪製 UI
        self.draw_ui()

        # 更新顯示
        pygame.display.flip()

    def handle_events(self):
        """處理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                if self.game_state == "WAITING":
                    self.game_state = "PLAYING"
                elif self.game_state == "GAME_OVER" and event.key == pygame.K_r:
                    self.score_manager = ScoreManager()
                    self.reset_game()

        return True

    def run(self):
        """主遊戲迴圈"""
        running = True

        while running:
            # 控制幀率
            self.clock.tick(60)

            # 處理事件
            running = self.handle_events()

            # 更新遊戲狀態
            self.update()

            # 繪製畫面
            self.draw()

        pygame.quit()
        sys.exit()


def main():
    """主程式入口"""
    game = BreakoutGame()
    game.run()


if __name__ == "__main__":
    main()
