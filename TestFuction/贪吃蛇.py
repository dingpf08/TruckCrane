import pygame
import sys
import random
import time

def main():
    # 初始化pygame
    def init_pygame():
        pygame.init()
        pygame.display.set_caption('贪吃蛇')

    # 设置颜色
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    BLACK = (0, 0, 0)

    # 设置游戏窗口大小
    WIDTH, HEIGHT = 640, 480
    CELL_SIZE = 10

    # 定义蛇的初始位置和速度
    def snake_initial_position_and_speed():
        snake_pos = [WIDTH // 2, HEIGHT // 2]
        snake_speed = [CELL_SIZE, 0]
        return snake_pos, snake_speed

    # 定义食物的初始位置
    def food_initial_position():
        return [random.randrange(1, (WIDTH // CELL_SIZE)) * CELL_SIZE,
                random.randrange(1, (HEIGHT // CELL_SIZE)) * CELL_SIZE]

    # 游戏结束函数
    def game_over(screen):
        my_font = pygame.font.SysFont('times new roman', 90)
        game_over_surface = my_font.render('游戏结束', True, RED)
        game_over_rect = game_over_surface.get_rect()
        game_over_rect.midtop = (WIDTH / 2, HEIGHT / 4)
        screen.fill(BLACK)
        screen.blit(game_over_surface, game_over_rect)
        pygame.display.flip()
        time.sleep(2)
        pygame.quit()
        sys.exit()

    # 更新蛇的位置
    def update_snake_position(snake_head, snake_speed, snake_body):
        new_head = [snake_head[0] + snake_speed[0], snake_head[1] + snake_speed[1]]
        snake_body.append(new_head)
        return new_head, snake_body

    # 画蛇和食物
    def draw_snake_and_food(screen, snake_body, food_pos):
        for pos in snake_body:
            pygame.draw.rect(screen, GREEN, pygame.Rect(pos[0], pos[1], CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, WHITE, pygame.Rect(food_pos[0], food_pos[1], CELL_SIZE, CELL_SIZE))

    # 检查蛇是否撞到边界或自己
    def check_collision(snake_head, snake_body, width, height):
        head_x, head_y = snake_head
        if head_x < 0 or head_x >= width or head_y < 0 or head_y >= height:
            return True
        for block in snake_body[1:]:
            if snake_head == block:
                return True
        return False

    init_pygame()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    snake_pos, snake_speed = snake_initial_position_and_speed()
    snake_body = [snake_pos]
    food_pos = food_initial_position()
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake_speed[1] == 0:
                    snake_speed = [0, -CELL_SIZE]
                elif event.key == pygame.K_DOWN and snake_speed[1] == 0:
                    snake_speed = [0, CELL_SIZE]
                elif event.key == pygame.K_LEFT and snake_speed[0] == 0:
                    snake_speed = [-CELL_SIZE, 0]
                elif event.key == pygame.K_RIGHT and snake_speed[0] == 0:
                    snake_speed = [CELL_SIZE, 0]

        snake_pos, snake_body = update_snake_position(snake_pos, snake_speed, snake_body)

        if snake_pos == food_pos:
            food_pos = food_initial_position()
        else:
            snake_body.pop(0)

        screen.fill(BLACK)
        draw_snake_and_food(screen, snake_body, food_pos)
        pygame.display.update()

        if check_collision(snake_pos, snake_body, WIDTH, HEIGHT):
            game_over(screen)

        clock.tick(10)

if __name__ == "__main__":
    main()
