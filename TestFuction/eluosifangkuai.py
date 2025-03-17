import pygame
import random

# 定义游戏参数
SCREEN_WIDTH, SCREEN_HEIGHT = 300, 600
BLOCK_SIZE = 30
BOARD_WIDTH, BOARD_HEIGHT = 10, 20
FPS = 10

# 定义颜色
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255),  # 青色
    (0, 0, 255),    # 蓝色
    (255, 127, 0),  # 橙色
    (255, 255, 0),  # 黄色
    (0, 255, 0),    # 绿色
    (255, 0, 255),  # 紫色
    (255, 0, 0),    # 红色
]

# 定义形状
SHAPES = [
    [[1, 1, 1, 1]],  # I形状
    [[1, 1], [1, 1]],  # O形状
    [[0, 1, 0], [1, 1, 1]],  # T形状
    [[0, 1, 1], [1, 1, 0]],  # S形状
    [[1, 1, 0], [0, 1, 1]],  # Z形状
    [[0, 1, 0], [1, 1, 1], [0, 1, 0]],  # J形状
    [[1, 0, 0], [1, 1, 1], [0, 0, 1]],  # L形状
]

# 初始化pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('俄罗斯方块')
clock = pygame.time.Clock()

# 创建游戏板
board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

def new_shape():
    return random.choice(SHAPES)

def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]

def check_collision(board, shape, offset):
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell and (board[y + off_y][x + off_x] or x + off_x >= BOARD_WIDTH or x + off_x < 0 or y + off_y >= BOARD_HEIGHT):
                return True
    return False

def remove_full_rows(board):
    new_board = [row for row in board if not all(row)]
    rows_removed = BOARD_HEIGHT - len(new_board)
    for _ in range(rows_removed):
        new_board.insert(0, [0 for _ in range(BOARD_WIDTH)])
    return new_board

def draw_board(board):
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, COLORS[cell - 1], (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, GRAY, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def draw_shape(shape, offset):
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, COLORS[cell - 1], (x * BLOCK_SIZE + off_x * BLOCK_SIZE, y * BLOCK_SIZE + off_y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, GRAY, (x * BLOCK_SIZE + off_x * BLOCK_SIZE, y * BLOCK_SIZE + off_y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

# 游戏主循环
try:
    running = True
    current_shape = new_shape()
    current_offset = (BOARD_WIDTH // 2 - len(current_shape[0]) // 2, 0)
    fall_speed = 1000  # 每次下落间隔时间（毫秒）
    fall_time = 0

    while running:
        screen.fill(WHITE)
        draw_board(board)
        draw_shape(current_shape, current_offset)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    fall_speed = 100
                elif event.key == pygame.K_t:
                    new_shape = rotate(current_shape)
                    if not check_collision(board, new_shape, current_offset):
                        current_shape = new_shape
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_s:
                        fall_speed = 1000

                    # 更新方块下落
                fall_time += clock.get_rawtime()
                if fall_time > fall_speed:
                    fall_time = 0
                    new_offset = (current_offset[0], current_offset[1] + 1)
                    if not check_collision(board, current_shape, new_offset):
                        current_offset = new_offset
                    else:
                        # 将当前形状的方块固定在游戏板上
                        for y, row in enumerate(current_shape):
                            for x, cell in enumerate(row):
                                if cell:
                                    board[y + current_offset[1]][x + current_offset[0]] = cell
                        board = remove_full_rows(board)
                        current_shape = new_shape()
                        current_offset = (BOARD_WIDTH // 2 - len(current_shape[0]) // 2, 0)
                        if check_collision(board, current_shape, current_offset):
                            running = False  # 游戏结束

                pygame.display.flip()
                clock.tick(FPS)
            except Exception as e:
            print(f"An error occurred: {e}")
        finally:
        pygame.quit()
