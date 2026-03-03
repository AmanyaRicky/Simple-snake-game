import pygame
import random
import math
import colorsys

pygame.init()

# Window setup
width, height = 600, 400
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake Game - Fully Visible")

# Clock and font
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 25)
big_font = pygame.font.SysFont("arial", 40)

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
red_base = (255, 0, 0)
blue = (0, 100, 255)

snake_block = 20  # visible block size

# Particle class for eating effect
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = random.randint(2,5)
        self.color = (255, random.randint(100,255), 0)
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(-2, 2)
        self.lifetime = 20
    
    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.lifetime -= 1
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

# HSV to RGB converter
def hsv2rgb(h, s, v):
    return tuple(round(i*255) for i in colorsys.hsv_to_rgb(h,s,v))

# Background gradient
def draw_background(frame):
    for y in range(height):
        color = hsv2rgb((y*0.003 + frame*0.002)%1.0, 0.4, 1)
        pygame.draw.line(window, color, (0,y), (width,y))

# Draw snake as visible rainbow blocks
def draw_snake(snake_list, frame):
    for i, block in enumerate(snake_list):
        h = (i*0.05 + frame*0.01) % 1.0
        color = hsv2rgb(h,1,1)
        pygame.draw.rect(window, color, [block[0], block[1], snake_block, snake_block])

# Draw animated food
def draw_food(x, y, frame):
    pulse = int(5*math.sin(frame*0.3))
    pygame.draw.rect(window, red_base, [x-pulse//2, y-pulse//2, snake_block+pulse, snake_block+pulse])

# Display score and level
def show_score_level(score, level, high_score):
    overlay = pygame.Surface((width, 40))
    overlay.set_alpha(160)
    overlay.fill(black)
    window.blit(overlay, (0,0))
    text = font.render(f"Score: {score}  Level: {level}  High Score: {high_score}", True, white)
    window.blit(text, [10,10])

def gameLoop():
    game_over = False
    game_close = False
    paused = False

    x1 = width//2
    y1 = height//2
    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1
    snake_speed = 10

    foodx = random.randrange(0, width - snake_block, snake_block)
    foody = random.randrange(0, height - snake_block, snake_block)

    obstacles = []
    particles = []
    score = 0
    high_score = 0
    level = 1
    frame = 0

    while not game_over:
        while game_close:
            window.fill(black)
            msg = big_font.render("GAME OVER!", True, white)
            window.blit(msg, [width/2 - 120, height/2 - 50])
            msg2 = font.render("Press C-Play Again or Q-Quit", True, white)
            window.blit(msg2, [width/2 - 140, height/2 + 10])
            show_score_level(score, level, high_score)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x1_change == 0:
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_RIGHT and x1_change == 0:
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_UP and y1_change == 0:
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_DOWN and y1_change == 0:
                    y1_change = snake_block
                    x1_change = 0
                elif event.key == pygame.K_p:
                    paused = not paused

        if paused:
            window.fill(black)
            pause_text = big_font.render("PAUSED", True, blue)
            window.blit(pause_text, [width/2 - 70, height/2 - 20])
            pygame.display.update()
            continue

        # Collision with walls
        if x1 >= width or x1 < 0 or y1 >= height or y1 < 0:
            game_close = True

        x1 += x1_change
        y1 += y1_change

        draw_background(frame)

        # Draw obstacles
        for obs in obstacles:
            pygame.draw.rect(window, black, [obs[0], obs[1], snake_block, snake_block])

        draw_food(foodx, foody, frame)

        snake_Head = [x1, y1]
        snake_List.append(snake_Head)
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        # Self collision
        for block in snake_List[:-1]:
            if block == snake_Head:
                game_close = True

        # Obstacle collision
        for obs in obstacles:
            if snake_Head == obs:
                game_close = True

        draw_snake(snake_List, frame)
        show_score_level(score, level, high_score)

        # Move and draw particles
        for p in particles[:]:
            p.move()
            if p.lifetime <= 0:
                particles.remove(p)
            else:
                p.draw(window)

        # Eating food
        if x1 == foodx and y1 == foody:
            foodx = random.randrange(0, width - snake_block, snake_block)
            foody = random.randrange(0, height - snake_block, snake_block)
            Length_of_snake += 1
            score += 1
            if score > high_score:
                high_score = score

            # Particle explosion
            for _ in range(15):
                particles.append(Particle(x1+snake_block/2, y1+snake_block/2))

            if score % 5 == 0:
                snake_speed += 2
                level += 1
                obs_x = random.randrange(0, width - snake_block, snake_block)
                obs_y = random.randrange(0, height - snake_block, snake_block)
                obstacles.append([obs_x, obs_y])

        pygame.display.update()
        frame += 1
        clock.tick(snake_speed)

    pygame.quit()
    quit()

gameLoop()
