import pygame
import sys
import random
import math

# 初始化pygame
pygame.init()

# 設定視窗大小
width = 600
height = 400
screen = pygame.display.set_mode((width, height))

# 設定視窗標題
pygame.display.set_caption("Pygame可移動方塊")

# 設定顏色
LIGHT_GREEN = (57, 255, 20)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 128, 0)
PINK = (255, 192, 203)

# 螢光色系 - 高亮度高飽和度顏色
NEON_COLORS = [
    (0, 255, 255),  # 螢光青
    (255, 0, 255),  # 螢光洋紅
    (0, 255, 0),  # 螢光綠
    (255, 255, 0),  # 螢光黃
    (255, 0, 127),  # 螢光粉
    (127, 255, 0),  # 螢光青綠
    (255, 127, 0),  # 螢光橙
    (127, 0, 255),  # 螢光紫
]

NEON_BACKGROUNDS = [
    (20, 20, 20),  # 深黑
    (30, 0, 30),  # 深紫
    (0, 30, 30),  # 深青
    (30, 30, 0),  # 深黃
    (50, 0, 50),  # 中紫
    (0, 50, 0),  # 深綠
]

# 主程式迴圈
clock = pygame.time.Clock()

# 設置紅色方塊參數 - 改為正方形
square_size = 60  # 統一寬高為正方形
square_x = 220
square_y = 10
speed = 5

# 距離追蹤變數
total_distance = 0.0  # 累計移動距離
last_x, last_y = square_x, square_y  # 記錄上一幀位置
current_color = RED  # 當前方塊顏色
current_background = LIGHT_GREEN  # 當前背景顏色

# 初始化字體 - 使用絕對路徑載入微軟正黑體
font = pygame.font.Font("C:/Windows/Fonts/msjh.ttc", 24)


def get_random_color():
    """
    隨機選擇一個顏色

    Returns:
        tuple: RGB顏色值
    """
    return random.choice(COLOR_LIST)


def get_random_background():
    """
    隨機選擇背景顏色

    Returns:
        tuple: RGB顏色值
    """
    return random.choice(BACKGROUND_COLOR_LIST)


def get_contrasting_colors():
    """
    獲取有對比度的方塊和背景顏色組合

    Returns:
        tuple: (方塊顏色, 背景顏色)
    """
    square_color = get_random_color()
    background_color = get_random_background()

    # 確保不會選到相同顏色 - 避免看不見方塊
    while square_color == background_color:
        background_color = get_random_background()

    return square_color, background_color


def get_neon_colors():
    """
    獲取螢光色組合

    Returns:
        tuple: (方塊螢光色, 背景深色)
    """
    square_color = random.choice(NEON_COLORS)
    background_color = random.choice(NEON_BACKGROUNDS)

    return square_color, background_color


def calculate_distance(x1, y1, x2, y2):
    """
    計算兩點間的歐幾里德距離

    Args:
        x1, y1 (int): 起始座標
        x2, y2 (int): 結束座標

    Returns:
        float: 兩點間距離
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def update_square_position(x, y, keys):
    """
    更新方塊位置並進行邊界檢測

    Args:
        x (int): 當前X座標
        y (int): 當前Y座標
        keys: 鍵盤按鍵狀態

    Returns:
        tuple: (新X座標, 新Y座標)
    """
    new_x, new_y = x, y

    # WASD 控制移動
    if keys[pygame.K_w]:
        new_y -= speed
    if keys[pygame.K_s]:
        new_y += speed
    if keys[pygame.K_a]:
        new_x -= speed
    if keys[pygame.K_d]:
        new_x += speed

    # 邊界檢測 - 防止方塊移出螢幕
    new_x = max(0, min(new_x, width - square_size))
    new_y = max(0, min(new_y, height - square_size))

    return new_x, new_y


def get_random_offset(max_offset=5):
    """
    生成隨機偏移量供文字亂動使用

    Args:
        max_offset (int): 最大偏移像素

    Returns:
        tuple: (x偏移, y偏移)
    """
    offset_x = random.randint(-max_offset, max_offset)
    offset_y = random.randint(-max_offset, max_offset)
    return offset_x, offset_y


def draw_coordinate_text(screen, x, y):
    """
    在左上角顯示方塊座標 - 添加亂動效果

    Args:
        screen: pygame螢幕物件
        x (int): 方塊X座標
        y (int): 方塊Y座標
    """
    coord_text = f"座標: ({x}, {y})"
    text_surface = font.render(coord_text, True, WHITE)  # 改為白色更顯眼

    # 添加文字亂動效果
    offset_x, offset_y = get_random_offset(3)
    screen.blit(text_surface, (10 + offset_x, 10 + offset_y))


def draw_distance_text(screen, distance):
    """
    在左上角顯示累計移動距離 - 添加亂動效果

    Args:
        screen: pygame螢幕物件
        distance (float): 累計移動距離
    """
    distance_text = f"移動距離: {distance:.1f}"
    text_surface = font.render(distance_text, True, WHITE)  # 改為白色更顯眼

    # 添加文字亂動效果
    offset_x, offset_y = get_random_offset(3)
    screen.blit(text_surface, (10 + offset_x, 40 + offset_y))


while True:
    # 控制幀率
    clock.tick(60)

    # 處理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 鍵盤輸入控制方塊移動
    keys = pygame.key.get_pressed()
    new_x, new_y = update_square_position(square_x, square_y, keys)

    # 計算移動距離
    if new_x != square_x or new_y != square_y:
        frame_distance = calculate_distance(square_x, square_y, new_x, new_y)
        total_distance += frame_distance

        # 檢查是否需要換顏色 - 改為每10格觸發
        if total_distance >= 10:
            current_color, current_background = get_neon_colors()
            total_distance = 0.0  # 重置距離計數器

    square_x, square_y = new_x, new_y

    # 填充背景色 - 使用當前背景顏色
    screen.fill(current_background)

    # 繪製可移動的方形 - 使用當前顏色
    pygame.draw.rect(
        screen, current_color, (square_x, square_y, square_size, square_size)
    )

    # 顯示座標和距離資訊 - 現在會亂動了
    draw_coordinate_text(screen, square_x, square_y)
    draw_distance_text(screen, total_distance)

    # 更新顯示
    pygame.display.flip()
