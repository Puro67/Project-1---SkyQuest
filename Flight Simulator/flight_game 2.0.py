import pygame
import random
pygame.init()

# Screen display:
WIDTH = 1000
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SkyQuest")
clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.SysFont("Arial", 100, bold=True)
font = pygame.font.SysFont("Arial", 50)
small_font = pygame.font.SysFont("Arial", 30)

# Player data:
player = pygame.image.load("Image/Plane.png")
player = pygame.transform.scale(player, (90, 90))
player_x = 100
player_y = 200
player_w = 90
player_h = 90
player_speed = 7
player_hp = 100

# Obstacles
obstacles = []
obs = pygame.image.load("Image/obs1.png")
obs = pygame.transform.scale(obs, (50, 50))
obs_w = 50
obs_h = 50
spawn_timer = 0

# ---------------- LEVEL SETTINGS ----------------
# Each level has its own numbers. To change a level, just edit its line here.
#   time      = seconds to survive
#   spawn_min / spawn_max = wait time between two obstacles (smaller = more obstacles)
#   speed_min / speed_max = obstacle speed (bigger = faster)
#   bg        = background color (red, green, blue)
LEVELS = {
    1: {"time": 30, "spawn_min": 1.5, "spawn_max": 3.0, "speed_min": 200, "speed_max": 300, "bg": (90, 190, 245)},
    2: {"time": 40, "spawn_min": 1.0, "spawn_max": 2.5, "speed_min": 250, "speed_max": 400, "bg": (240, 150, 90)},
    3: {"time": 50, "spawn_min": 0.6, "spawn_max": 1.8, "speed_min": 300, "speed_max": 500, "bg": (40, 40, 80)},
}
current_level = 1

# Time left in the current level (seconds)
time_left = LEVELS[current_level]["time"]
spawn_time = random.uniform(LEVELS[current_level]["spawn_min"], LEVELS[current_level]["spawn_max"])

# Game state: "menu", "playing", "win" or "game_over"
state = "menu"

# Made texts are in the center
def draw_text(text, text_font, color, center):
    img = text_font.render(text, True, color)
    rect = img.get_rect(center=center)
    screen.blit(img, rect)


def reset_game():
    global player_x, player_y, player_hp, spawn_timer, spawn_time, time_left
    settings = LEVELS[current_level]        # numbers of the chosen level
    player_x = 100
    player_y = 200
    player_hp = 100
    spawn_timer = 0
    spawn_time = random.uniform(settings["spawn_min"], settings["spawn_max"])
    time_left = settings["time"]
    obstacles.clear()


running = True
while running:
    dt = clock.tick(60) / 1000

    # Switching state
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                running = False

            # In the menu, keys 1, 2, 3 choose the level (only for testing for now)
            if state == "menu":
                if event.key == pygame.K_1:
                    current_level = 1
                if event.key == pygame.K_2:
                    current_level = 2
                if event.key == pygame.K_3:
                    current_level = 3

            if state == "menu" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                reset_game()
                state = "playing"
            elif state in ("game_over", "win") and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                state = "menu"

    keys = pygame.key.get_pressed()

    # ---------------- START SCREEN ----------------
    if state == "menu":
        screen.fill((90, 190, 245))
        draw_text("SKYQUEST", title_font, (255, 255, 255), (WIDTH // 2, 200))
        screen.blit(player, (WIDTH // 2 - 45, 270))

        draw_text(f"Level {current_level}   (press 1, 2 or 3 to choose)", small_font, (255, 255, 255), (WIDTH // 2, 390))

        # Ticking line
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            draw_text("Press ENTER or SPACE to start", small_font, (255, 255, 255), (WIDTH // 2, 450))
        draw_text("Moving: W A S D   |   Exit: ESC", small_font, (255, 255, 255), (WIDTH // 2, 530))

    # ---------------- PLAYING ----------------
    elif state == "playing":
        settings = LEVELS[current_level]        # numbers of the current level

        # Player movement
        if keys[pygame.K_w]:
            player_y -= player_speed
        if keys[pygame.K_s]:
            player_y += player_speed
        if keys[pygame.K_d]:
            player_x += player_speed
        if keys[pygame.K_a]:
            player_x -= player_speed

        player_x = max(0, min(WIDTH - 50, player_x))
        player_y = max(0, min(HEIGHT - 70, player_y))

        # Spawn obstacle
        spawn_timer += dt
        if spawn_timer >= spawn_time:
            spawn_timer = 0.0
            spawn_time = random.uniform(settings["spawn_min"], settings["spawn_max"])
            obstacles.append({
                "x": WIDTH,
                "y": random.randint(0, HEIGHT - obs_h),
                "speed": random.randint(settings["speed_min"], settings["speed_max"]),
            })

        # Move obstacles, hit check, remove old ones
        player_rect = pygame.Rect(player_x, player_y, player_w, player_h)
        player_rect = player_rect.inflate(-30, -40)

        for ob in obstacles[:]:
            ob["x"] -= ob["speed"] * dt
            ob_rect = pygame.Rect(ob["x"], ob["y"], obs_w, obs_h)

            if player_rect.colliderect(ob_rect):
                player_hp -= 10
                obstacles.remove(ob)
            elif ob["x"] < -obs_w:
                obstacles.remove(ob)

        # Countdown
        time_left -= dt
        if time_left <= 0:
            state = "win"

        if player_hp <= 0:
            state = "game_over"

        # Display
        screen.fill(settings["bg"])
        for ob in obstacles:
            screen.blit(obs, (ob["x"], ob["y"]))
        screen.blit(player, (player_x, player_y))
        hp_text = font.render(f"HP: {player_hp}/100", True, (255, 255, 255))
        screen.blit(hp_text, (15, 10))
        draw_text(f"Level {current_level}", font, (255, 255, 255), (WIDTH // 2, 30))
        draw_text(f"Time: {int(time_left) + 1}", font, (255, 255, 255), (WIDTH - 120, 30))

    # ---------------- WIN ----------------
    elif state == "win":
        screen.fill((30, 90, 60))
        draw_text("LEVEL COMPLETE!", title_font, (255, 255, 255), (WIDTH // 2, 220))
        draw_text(f"You finished level {current_level}", small_font, (255, 255, 255), (WIDTH // 2, 310))
        draw_text("Press ENTER or SPACE to get back to main screen", small_font, (255, 255, 255), (WIDTH // 2, 400))

    # ---------------- GAME OVER ----------------
    elif state == "game_over":
        screen.fill((40, 40, 60))
        draw_text("GAME OVER", title_font, (255, 80, 80), (WIDTH // 2, 230))
        draw_text("Press ENTER or SPACE to get back to main screen", small_font, (255, 255, 255), (WIDTH // 2, 370))

    pygame.display.flip()

pygame.quit()
