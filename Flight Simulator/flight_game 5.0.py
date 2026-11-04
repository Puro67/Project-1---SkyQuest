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
instruction_font = pygame.font.SysFont("Arial", 20)

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
spawn_time = random.uniform(1.0, 3.0)

# Coins                                                  # NEW
coin_list = []                                           # NEW
coin_r = 15                                              # NEW
coin_speed = 250                                         # NEW
coin_timer = 0                                           # NEW
coin_time = random.uniform(1.0, 2.0)                     # NEW
coins = 0                                                # NEW
level_coins = 0                                          # NEW

# Level number (1, 2 or 3)                               # NEW
level = 1                                                # NEW

# Game state: "menu", "playing" or "game_over"
state = "menu"
# Two more states: "switching" (screen between levels) and "win" (after level 3)   # NEW

# Time limit for the level (seconds)
level_time = 30
time_left = level_time

# Made texts are in the center
def draw_text(text, text_font, color, center):
    img = text_font.render(text, True, color)
    rect = img.get_rect(center=center)
    screen.blit(img, rect)


def reset_game():
    global player_x, player_y, player_hp, spawn_timer, spawn_time
    global time_left, level, coins, level_coins, coin_timer, coin_time    # NEW
    player_x = 100
    player_y = 200
    player_hp = 100
    spawn_timer = 0
    spawn_time = random.uniform(1.0, 3.0)
    time_left = level_time
    obstacles.clear()
    level = 1                                            # NEW
    coins = 0                                            # NEW
    level_coins = 0                                      # NEW
    coin_timer = 0                                       # NEW
    coin_time = random.uniform(1.0, 2.0)                 # NEW
    coin_list.clear()                                    # NEW


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
            if state == "menu" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                reset_game()
                state = "playing"
            elif state == "game_over" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                state = "menu"
            elif state == "win" and event.key in (pygame.K_RETURN, pygame.K_SPACE):    # NEW
                state = "menu"                                                          # NEW
            elif state == "switching":                                                  # NEW
                # R = repair the plane (costs 1 coin, gives 10 HP, HP never goes above 100)
                if event.key == pygame.K_r and coins >= 1 and player_hp < 100:         # NEW
                    coins -= 1                                                          # NEW
                    player_hp = min(100, player_hp + 10)                                # NEW
                # The number key of the next level (2 or 3) starts that level
                if event.unicode == str(level + 1):                                     # NEW
                    level += 1                                                          # NEW
                    player_x = 100                                                      # NEW
                    player_y = 200                                                      # NEW
                    spawn_timer = 0                                                     # NEW
                    time_left = level_time                                              # NEW
                    level_coins = 0                                                     # NEW
                    coin_timer = 0                                                      # NEW
                    obstacles.clear()                                                   # NEW
                    coin_list.clear()                                                   # NEW
                    state = "playing"                                                   # NEW

    keys = pygame.key.get_pressed()

    # ---------------- START SCREEN ----------------
    if state == "menu":
        screen.fill((90, 190, 245))
        draw_text("SKYQUEST", title_font, (255, 255, 255), (WIDTH // 2, 75))
        screen.blit(player, (WIDTH // 2 - 45, 270))

        draw_text("Fly through three levels, dodge obstacles, and collect coins to repair your plane or boost your final score.",
                  instruction_font, (255, 255, 255), (WIDTH // 2, 200))
        draw_text("Keep your plane intact and gather as many coins as you can!",
                  instruction_font, (255, 255, 255), (WIDTH // 2, 250))

        # Ticking line
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            draw_text("Press ENTER or SPACE to start", small_font, (255, 255, 255), (WIDTH // 2, 430))
        draw_text("Moving: W A S D   |   Exit: ESC", small_font, (255, 255, 255), (WIDTH // 2, 520))

    # ---------------- PLAYING ----------------
    elif state == "playing":
        # Countdown
        time_left -= dt
        if time_left <= 0:
            state = "win"
            if level < 3:                                # NEW (not the last level -> switching screen)
                state = "switching"                      # NEW
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
            spawn_time = random.uniform(1.0, 3.0)
            obstacles.append({
                "x": WIDTH,
                "y": random.randint(0, HEIGHT - obs_h),
                "speed": random.randint(200, 400),
            })
            obstacles[-1]["speed"] += (level - 1) * 50   # NEW (higher level = faster obstacle)

        # Spawn coin                                                       # NEW
        coin_timer += dt                                                   # NEW
        if coin_timer >= coin_time:                                        # NEW
            coin_timer = 0.0                                               # NEW
            coin_time = random.uniform(1.0, 2.0)                           # NEW
            coin_list.append({                                             # NEW
                "x": WIDTH,                                                # NEW
                "y": random.randint(coin_r, HEIGHT - coin_r),              # NEW
            })                                                             # NEW

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

        # Move coins, collect check, remove old ones                       # NEW
        for c in coin_list[:]:                                             # NEW
            c["x"] -= coin_speed * dt                                      # NEW
            coin_rect = pygame.Rect(c["x"] - coin_r, c["y"] - coin_r, coin_r * 2, coin_r * 2)   # NEW

            if player_rect.colliderect(coin_rect):                         # NEW
                coins += 1                                                 # NEW
                level_coins += 1                                           # NEW
                coin_list.remove(c)                                        # NEW
            elif c["x"] < -coin_r:                                         # NEW
                coin_list.remove(c)                                        # NEW

        if player_hp <= 0:
            state = "game_over"

        # Display
        screen.fill((90, 190, 245))
        for ob in obstacles:
            screen.blit(obs, (ob["x"], ob["y"]))
        for c in coin_list:                                                # NEW
            pygame.draw.circle(screen, (255, 215, 0), (int(c["x"]), int(c["y"])), coin_r)      # NEW
            pygame.draw.circle(screen, (200, 150, 0), (int(c["x"]), int(c["y"])), coin_r, 3)   # NEW
        screen.blit(player, (player_x, player_y))
        hp_text = font.render(f"HP: {player_hp}/100", True, (255, 255, 255))
        screen.blit(hp_text, (15, 10))
        coin_text = font.render(f"Coins: {coins}", True, (255, 215, 0))    # NEW
        screen.blit(coin_text, (15, 65))                                   # NEW
        draw_text(f"Level {level}", font, (255, 255, 255), (WIDTH // 2, 30))                # NEW
        draw_text(f"Time: {int(time_left) + 1}", font, (255, 255, 255), (WIDTH - 120, 30))  # NEW

    # ---------------- GAME OVER ----------------
    elif state == "game_over":
        screen.fill((40, 40, 60))
        draw_text("GAME OVER", title_font, (255, 80, 80), (WIDTH // 2, 230))
        draw_text("Press ENTER or SPACE to get back to the main screen", small_font, (255, 255, 255), (WIDTH // 2, 370))
    # ---------------- SWITCHING (between two levels) ----------------           # NEW
    elif state == "switching":                                                    # NEW
        screen.fill((30, 30, 60))                                                 # NEW
        draw_text(f"LEVEL {level} COMPLETE!", font, (255, 255, 255), (WIDTH // 2, 100))                       # NEW
        draw_text(f"Coins earned this level: {level_coins}", small_font, (255, 215, 0), (WIDTH // 2, 200))   # NEW
        draw_text(f"Coins: {coins}      HP: {player_hp}/100", small_font, (255, 255, 255), (WIDTH // 2, 250)) # NEW
        draw_text("Press R to repair your plane (1 coin = +10 HP)", small_font, (255, 255, 255), (WIDTH // 2, 330))  # NEW
        draw_text(f"Next: Level {level + 1}", font, (255, 255, 255), (WIDTH // 2, 430))                       # NEW
        draw_text(f"Press {level + 1} to start", small_font, (255, 255, 255), (WIDTH // 2, 500))              # NEW
    # ---------------- WIN ----------------
    elif state == "win":
        screen.fill((30, 90, 60))
        draw_text("LEVEL COMPLETE!", title_font, (255, 255, 255), (WIDTH // 2, 230))
        draw_text(f"Final score: {coins}", font, (255, 215, 0), (WIDTH // 2, 310))     # NEW
        draw_text("Press ENTER or SPACE to get back to main screen", small_font, (255, 255, 255), (WIDTH // 2, 370))
    pygame.display.flip()

pygame.quit()
