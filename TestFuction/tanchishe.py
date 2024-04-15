import pygame
import sys
import random

def main():
    # 初始化pygame
    pygame.init()

    # 设置窗口大小
    size = width, height = 640, 480
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("贪吃蛇游戏")

    # 定义颜色
    black = (0, 0, 0)
    white = (255, 255, 255)
    red = (255, 0, 0)
    green = (0, 255, 0)

    # 设置帧率
    clock = pygame.time.Clock()
    snake_speed = 15

    # 设置蛇的初始位置
    snake_position = [100, 50]
    snake_body = [[100, 50], [90, 50], [80, 50]]
    food_position = [random.randrange(1, (width//10)) * 10, random.randrange(1, (height//10)) * 10]
    food_spawn = True

    # 设置默认蛇移动方向
    direction = 'RIGHT'
    change_to = direction

    def change_dir(to):
        nonlocal direction
        if to == 'RIGHT' and not direction == 'LEFT':
            direction = 'RIGHT'
        if to == 'LEFT' and not direction == 'RIGHT':
            direction = 'LEFT'
        if to == 'UP' and not direction == 'DOWN':
            direction = 'UP'
        if to == 'DOWN' and not direction == 'UP':
            direction = 'DOWN'

    def game_over():
        pygame.quit()
        sys.exit()

    # 游戏主循环
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    change_dir('RIGHT')
                if event.key == pygame.K_LEFT:
                    change_dir('LEFT')
                if event.key == pygame.K_UP:
                    change_dir('UP')
                if event.key == pygame.K_DOWN:
                    change_dir('DOWN')
            elif event.type == pygame.QUIT:
                game_over()

        # 移动蛇头
        if direction == 'RIGHT':
            snake_position[0] += 10
        if direction == 'LEFT':
            snake_position[0] -= 10
        if direction == 'UP':
            snake_position[1] -= 10
        if direction == 'DOWN':
            snake_position[1] += 10

        # 蛇吃到食物
        snake_body.insert(0, list(snake_position))
        if snake_position == food_position:
            food_spawn = False
        else:
            snake_body.pop()

        # 重新生成食物
        if not food_spawn:
            food_position = [random.randrange(1, (width//10)) * 10, random.randrange(1, (height//10)) * 10]
        food_spawn = True

        # 绘制
        screen.fill(black)
        for pos in snake_body:
            pygame.draw.rect(screen, green, pygame.Rect(pos[0], pos[1], 10, 10))
        pygame.draw.rect(screen, red, pygame.Rect(food_position[0], food_position[1], 10, 10))

        # 检查是否碰到边界
        if snake_position[0] < 0 or snake_position[0] > width-10:
            game_over()
        if snake_position[1] < 0 or snake_position[1] > height-10:
            game_over()

        # 检查蛇是否碰到自己
        for block in snake_body[1:]:
            if snake_position == block:
                game_over()

        pygame.display.update()
        clock.tick(snake_speed)

if __name__ == "__main__":
    main()
