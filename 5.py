import pygame
import random
import sys

pygame.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chicken Shooter")

clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
YELLOW = (255, 220, 50)
BLUE = (50, 150, 255)
GREEN = (50, 220, 100)

font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 70)

player = pygame.Rect(WIDTH // 2 - 30, HEIGHT - 70, 60, 40)
player_speed = 7

bullets = []
bullet_speed = 10

chickens = []
chicken_speed = 2

score = 0
lives = 3
wave = 1

spawn_timer = 0
game_over = False


def create_chicken():
    x = random.randint(30, WIDTH - 60)
    chicken = pygame.Rect(x, -40, 40, 40)
    chickens.append(chicken)


def draw_player():
    pygame.draw.polygon(
        screen,
        BLUE,
        [
            (player.centerx, player.top),
            (player.left, player.bottom),
            (player.centerx, player.bottom - 10),
            (player.right, player.bottom)
        ]
    )


def draw_chicken(chicken):
    pygame.draw.ellipse(screen, WHITE, chicken)

    pygame.draw.circle(
        screen,
        RED,
        (chicken.right - 5, chicken.top + 15),
        8
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (chicken.centerx + 8, chicken.top + 12),
        3
    )

    pygame.draw.polygon(
        screen,
        YELLOW,
        [
            (chicken.centerx + 15, chicken.top + 18),
            (chicken.centerx + 30, chicken.top + 23),
            (chicken.centerx + 15, chicken.top + 27)
        ]
    )

    pygame.draw.line(
        screen,
        YELLOW,
        (chicken.centerx - 8, chicken.bottom - 5),
        (chicken.centerx - 8, chicken.bottom + 8),
        3
    )

    pygame.draw.line(
        screen,
        YELLOW,
        (chicken.centerx + 8, chicken.bottom - 5),
        (chicken.centerx + 8, chicken.bottom + 8),
        3
    )


def reset_game():
    global bullets, chickens, score, lives, wave
    global spawn_timer, chicken_speed, game_over

    bullets = []
    chickens = []

    score = 0
    lives = 3
    wave = 1

    spawn_timer = 0
    chicken_speed = 2

    player.x = WIDTH // 2 - 30
    game_over = False


while True:
    clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE and not game_over:
                bullet = pygame.Rect(
                    player.centerx - 4,
                    player.top - 15,
                    8,
                    15
                )

                bullets.append(bullet)

            if event.key == pygame.K_r and game_over:
                reset_game()

    if not game_over:

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.x -= player_speed

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.x += player_speed

        if player.left < 0:
            player.left = 0

        if player.right > WIDTH:
            player.right = WIDTH

        for bullet in bullets:
            bullet.y -= bullet_speed

        bullets = [
            bullet for bullet in bullets
            if bullet.bottom > 0
        ]

        spawn_timer += 1

        spawn_rate = max(15, 50 - wave * 3)

        if spawn_timer >= spawn_rate:
            create_chicken()
            spawn_timer = 0

        for chicken in chickens:
            chicken.y += chicken_speed

        for chicken in chickens[:]:

            if chicken.top > HEIGHT:

                chickens.remove(chicken)
                lives -= 1

                if lives <= 0:
                    game_over = True

        for bullet in bullets[:]:

            for chicken in chickens[:]:

                if bullet.colliderect(chicken):

                    if bullet in bullets:
                        bullets.remove(bullet)

                    if chicken in chickens:
                        chickens.remove(chicken)

                    score += 10

                    wave = score // 100 + 1
                    chicken_speed = 2 + wave * 0.3

                    break

    screen.fill(BLACK)

    draw_player()

    for bullet in bullets:
        pygame.draw.rect(screen, YELLOW, bullet)

    for chicken in chickens:
        draw_chicken(chicken)

    score_text = font.render(
        f"Score: {score}",
        True,
        WHITE
    )

    lives_text = font.render(
        f"Lives: {lives}",
        True,
        WHITE
    )

    wave_text = font.render(
        f"Wave: {wave}",
        True,
        WHITE
    )

    screen.blit(score_text, (20, 20))
    screen.blit(lives_text, (20, 55))
    screen.blit(wave_text, (20, 90))

    if game_over:

        game_over_text = big_font.render(
            "GAME OVER",
            True,
            RED
        )

        restart_text = font.render(
            "Press R to restart",
            True,
            WHITE
        )

        screen.blit(
            game_over_text,
            (
                WIDTH // 2 - game_over_text.get_width() // 2,
                HEIGHT // 2 - 70
            )
        )

        screen.blit(
            restart_text,
            (
                WIDTH // 2 - restart_text.get_width() // 2,
                HEIGHT // 2 + 10
            )
        )

    pygame.display.flip()