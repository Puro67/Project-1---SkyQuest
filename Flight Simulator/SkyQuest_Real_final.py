import pygame
import random
pygame.init()

#Screen display:
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

#Player data:
player = pygame.image.load("Image/Plane.png")
player = pygame.transform.scale(player, (90, 90))
player_x = 100
player_y = 200
player_w = 90
player_h = 90
player_speed = 7
player_hp = 100

#Obstacles
obstacles = []
obs = pygame.image.load("Image/obs1.png")
obs = pygame.transform.scale(obs, (50, 50))
obs_w = 50
obs_h = 50
spawn_timer = 0
spawn_time = random.uniform(1, 3)

# Game state: "menu", "playing" or "game_over"
state = "menu"

# Time limit for the level (seconds)
level_time = 30
time_left = level_time

# ---------------- SUNSET BACKGROUND FOR LEVEL 3 ----------------
sunset_bg = pygame.Surface((WIDTH, HEIGHT))
top_color = (45, 35, 105)
mid_color = (210, 85, 120)
bottom_color = (255, 170, 70)
for y in range(HEIGHT):
    if y < HEIGHT // 2:
        k = y / (HEIGHT // 2)
        c1, c2 = top_color, mid_color
    else:
        k = (y - HEIGHT // 2) / (HEIGHT // 2)
        c1, c2 = mid_color, bottom_color
    color = (int(c1[0] + (c2[0] - c1[0]) * k),
             int(c1[1] + (c2[1] - c1[1]) * k),
             int(c1[2] + (c2[2] - c1[2]) * k))
    pygame.draw.line(sunset_bg, color, (0, y), (WIDTH, y))

# Setting sun: a big glow circle and a smaller sun circle, half hidden by the bottom of the screen
pygame.draw.circle(sunset_bg, (255, 190, 90), (WIDTH - 220, HEIGHT - 70), 150)    # NEW
pygame.draw.circle(sunset_bg, (255, 235, 150), (WIDTH - 220, HEIGHT - 70), 105)   # NEW

# Thin dark clouds (x, y, width, height)
for cx, cy, cw, ch in [(80, 110, 240, 40), (520, 70, 280, 45), (780, 190, 200, 35), (300, 300, 260, 40), (40, 430, 220, 35)]:   # NEW
    pygame.draw.ellipse(sunset_bg, (125, 55, 125), (cx, cy, cw, ch))              # NEW

# Made texts are in the center
def draw_text(text, text_font, color, center):
    img = text_font.render(text, True, color)
    rect = img.get_rect(center=center)
    screen.blit(img, rect)

def start_level():
    global player_x, player_y, spawn_timer, spawn_time, time_left
    player_x = 100
    player_y = 200
    spawn_timer = 0
    spawn_time = random.uniform(1.0, 3.0)
    time_left = level_time
    obstacles.clear()

def reset_game():
    global player_hp
    player_hp = 100
    start_level()

running = True
while running:
#Setup
    dt = clock.tick(60) / 1000

   # Switching state
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                running = False
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if state == "menu":
                    reset_game()
                    state = "playing1"
                elif state == "win1":
                    start_level()
                    state = "playing2"
                elif state == "win2":
                    start_level()
                    state = "playing3"
                elif state in ("win3", "game_over"):
                    state = "menu"


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
    #LEVEL 1
    elif state == "playing1":
        # Countdown
        time_left -= dt
        if time_left <= 0:
            state = "win1"

        #Player Movement
        if pygame.key.get_pressed()[pygame.K_w]:
            player_y -= player_speed
        if pygame.key.get_pressed()[pygame.K_s]:
            player_y += player_speed
        if pygame.key.get_pressed()[pygame.K_d]:
            player_x += player_speed
        if pygame.key.get_pressed()[pygame.K_a]:
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
                "speed": random.randint(200, 400),})

        # Background
        sun = pygame.image.load("Image/Sun.png")
        sun = pygame.transform.scale(sun, (250, 250))
        sun_x = WIDTH - 225
        sun_y = - 40

        cloud = pygame.image.load("Image/whitecloud.png")
        clouds = [
            (pygame.transform.scale(cloud, (250, 170)), -60, 100),
            (pygame.transform.scale(cloud, (130, 90)), 200, 40),
            (pygame.transform.scale(cloud, (200, 140)), 420, 330),
            (pygame.transform.scale(cloud, (180, 120)), 650, 100),
            (pygame.transform.scale(cloud, (270, 190)), 800, 370),
            (pygame.transform.scale(cloud, (150, 100)), 520, 50),
            (pygame.transform.scale(cloud, (200, 140)), 100, 400),
            (pygame.transform.scale(cloud, (120, 80)), 750, 270),]

        # Move obstacles left, hit check, remove old ones
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

        if player_hp <= 0:
            state = "game_over"

        # Display
        screen.fill((90, 190, 245))

        # Draw sun
        screen.blit(sun, (sun_x, sun_y))

        # Draw cloud
        for cloud, x, y in clouds:
            screen.blit(cloud, (x, y))

        # Draw obstacles
        for ob in obstacles:
            screen.blit(obs, (ob["x"], ob["y"]))

        # Draw player
        screen.blit(player, (player_x, player_y))

        # HP
        hp_text = font.render(f"HP: {player_hp}/100", True, (255, 255, 255))
        screen.blit(hp_text, (15, 10))

    # LEVEL 2
    elif state == "playing2":

        # Countdown
        time_left -= dt
        if time_left <= 0:
            state = "win2"

        # Player Movement
        if pygame.key.get_pressed()[pygame.K_w]:
            player_y -= player_speed
        if pygame.key.get_pressed()[pygame.K_s]:
            player_y += player_speed
        if pygame.key.get_pressed()[pygame.K_d]:
            player_x += player_speed
        if pygame.key.get_pressed()[pygame.K_a]:
            player_x -= player_speed

        player_x = max(0, min(WIDTH - 50, player_x))
        player_y = max(0, min(HEIGHT - 70, player_y))

        # Spawn obstacle
        spawn_timer += dt
        if spawn_timer >= spawn_time:
            spawn_timer = 0.0
            spawn_time = random.uniform(0, 1.5)

            obstacles.append({
                "x": WIDTH,
                "y": random.randint(0, HEIGHT - obs_h),
                "speed": random.randint(400, 600)})

        # Move obstacles and check collision
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

        if player_hp <= 0:
            state = "game_over"

        # Background
        screen.fill((35, 40, 65))

        lightning = pygame.image.load("Image/lightning.png")
        lightning1 = pygame.transform.scale(lightning, (450, 500))
        lightning2 = pygame.transform.scale(lightning, (300, 350))


        black_cloud = pygame.image.load("Image/blackcloud.png")

        black_clouds = [
            (pygame.transform.scale(black_cloud, (300, 200)), -50, 0),
            (pygame.transform.scale(black_cloud, (250, 170)), 200, 50),
            (pygame.transform.scale(black_cloud, (350, 230)), 450, -30),
            (pygame.transform.scale(black_cloud, (300, 200)), 750, 50),
            (pygame.transform.scale(black_cloud, (250, 170)), 50, 350),
            (pygame.transform.scale(black_cloud, (350, 230)), 350, 380),
            (pygame.transform.scale(black_cloud, (300, 200)), 700, 350),]

        # Draw dark clouds
        for cloud, x, y in black_clouds:
            screen.blit(cloud, (x, y))

        # Draw lightning
        screen.blit(lightning1, (425, 50))
        screen.blit(lightning2, (-43, 75))

        # Draw obstacles
        for ob in obstacles:
            screen.blit(obs, (ob["x"], ob["y"]))

        # Draw player
        screen.blit(player, (player_x, player_y))

        # HP
        hp_text = font.render(
            f"HP: {player_hp}/100", True, (255, 255, 255))
        screen.blit(hp_text, (15, 10))

    # LEVEL 3
    elif state == "playing3":

        # Countdown
        time_left -= dt
        if time_left <= 0:
            state = "win3"

        # Player Movement
        if pygame.key.get_pressed()[pygame.K_w]:
            player_y -= player_speed
        if pygame.key.get_pressed()[pygame.K_s]:
            player_y += player_speed
        if pygame.key.get_pressed()[pygame.K_d]:
            player_x += player_speed
        if pygame.key.get_pressed()[pygame.K_a]:
            player_x -= player_speed

        player_x = max(0, min(WIDTH - 50, player_x))
        player_y = max(0, min(HEIGHT - 70, player_y))

        # Spawn obstacle (faster than level 2)
        spawn_timer += dt
        if spawn_timer >= spawn_time:
            spawn_timer = 0.0
            spawn_time = random.uniform(0, 0.5)

            obstacles.append({
                "x": WIDTH,
                "y": random.randint(0, HEIGHT - obs_h),
                "speed": random.randint(600, 700)})

        # Move obstacles and check collision
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

        if player_hp <= 0:
            state = "game_over"

        # Background:
        screen.blit(sunset_bg, (0, 0))

        # Draw obstacles
        for ob in obstacles:
            screen.blit(obs, (ob["x"], ob["y"]))

        # Draw player
        screen.blit(player, (player_x, player_y))

        # HP
        hp_text = font.render(f"HP: {player_hp}/100", True, (255, 255, 255))
        screen.blit(hp_text, (15, 10))

# ---------------- GAME OVER ----------------
    elif state == "game_over":
        screen.fill((40, 40, 60))
        draw_text("GAME OVER", title_font, (255, 80, 80), (WIDTH // 2, 230))
        draw_text("Press ENTER or SPACE to get back to main screen", small_font, (255, 255, 255), (WIDTH // 2, 370))

 # ---------------- WIN ----------------
    elif state == "win1":
        screen.fill((30, 90, 60))
        draw_text("LEVEL 1 COMPLETE!", title_font, (255, 255, 255), (WIDTH // 2, 230))
        draw_text("Press ENTER or SPACE to get to the next level", small_font, (255, 255, 255), (WIDTH // 2, 370))

    elif state == "win2":
        screen.fill((30, 90, 60))
        draw_text("LEVEL 2 COMPLETE!", font, (255, 255, 255), (WIDTH // 2, 230))
        draw_text("Press ENTER or SPACE to get to the next level", small_font, (255, 255, 255), (WIDTH // 2, 370))   # CHANGED (text only)

    elif state == "win3":
        screen.fill((30, 90, 60))
        draw_text("CONGRATULATIONS!", font, (255, 215, 0), (WIDTH // 2, 190))
        draw_text("You completed all 3 levels!", font, (255, 255, 255), (WIDTH // 2, 260))
        draw_text("Press ENTER or SPACE to go back to the main screen", small_font, (255, 255, 255), (WIDTH // 2, 370))
    pygame.display.flip()

pygame.quit()
