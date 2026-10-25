import math
import random
import sys
import pygame

# ============================================================
# SKYQUEST - 5-stage airplane survival game
# Requirements: Python 3.10+ and pygame
# Install pygame with: python -m pip install pygame
# Run with: python skyquest.py
# ============================================================

pygame.init()

# Window / game settings
WIDTH, HEIGHT = 1100, 650
FPS = 60
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SkyQuest - Flight Survival")
CLOCK = pygame.time.Clock()

# Fonts
FONT_SMALL = pygame.font.SysFont("arial", 18)
FONT = pygame.font.SysFont("arial", 24)
FONT_MEDIUM = pygame.font.SysFont("arial", 30, bold=True)
FONT_BIG = pygame.font.SysFont("arial", 44, bold=True)

# Colors
WHITE = (245, 248, 255)
BLACK = (15, 20, 30)
NAVY = (13, 25, 45)
BLUE = (55, 145, 225)
LIGHT_BLUE = (130, 205, 255)
GREEN = (65, 205, 130)
YELLOW = (255, 210, 70)
ORANGE = (255, 145, 65)
RED = (245, 75, 80)
GREY = (130, 145, 165)
DARK_GREY = (50, 60, 75)
GOLD = (255, 190, 45)

# Stage configuration: weather and wind are gameplay settings, not live weather.
STAGES = [
    {
        "city": "Hanoi, Vietnam",
        "airport": "Noi Bai International Airport (HAN)",
        "weather": "SUNNY",
        "wind_min": 10,
        "wind_max": 20,
        "wind_mode": "steady",
        "single_birds": 7,
        "flocks": 1,
        "meteors": 1,
        "coins": 5,
        "cloud_cover": False,
        "duration": 30,
    },
    {
        "city": "Beijing, China",
        "airport": "Beijing Capital International Airport (PEK)",
        "weather": "CLOUDY",
        "wind_min": 20,
        "wind_max": 35,
        "wind_mode": "change",
        "single_birds": 10,
        "flocks": 2,
        "meteors": 1,
        "coins": 5,
        "cloud_cover": True,
        "duration": 30,
    },
    {
        "city": "Almaty, Kazakhstan",
        "airport": "Almaty International Airport (ALA)",
        "weather": "STORM",
        "wind_min": 40,
        "wind_max": 70,
        "wind_mode": "gust",
        "single_birds": 13,
        "flocks": 2,
        "meteors": 2,
        "coins": 6,
        "cloud_cover": False,
        "duration": 30,
    },
    {
        "city": "Moscow, Russia",
        "airport": "Sheremetyevo International Airport (SVO)",
        "weather": "SUNNY",
        "wind_min": 45,
        "wind_max": 75,
        "wind_mode": "gust",
        "single_birds": 16,
        "flocks": 3,
        "meteors": 2,
        "coins": 6,
        "cloud_cover": False,
        "duration": 30,
    },
    {
        "city": "Helsinki, Finland",
        "airport": "Helsinki-Vantaa Airport (HEL)",
        "weather": "NIGHT",
        "wind_min": 50,
        "wind_max": 65,
        "wind_mode": "steady",
        "single_birds": 19,
        "flocks": 3,
        "meteors": 3,
        "coins": 7,
        "cloud_cover": False,
        "duration": 30,
    },
]

# A few safe UI/game constants
PLAYER_SIZE = (58, 40)
PLAYER_SPEED = 290
OBSTACLE_DAMAGE = 10
REPAIR_COST_PER_10_HP = 25
STAGE_REWARD = 200
COIN_VALUE = 50
TARGET_COINS = 1500
TARGET_FINAL_HP = 30


def clamp(value, low, high):
    return max(low, min(high, value))


def draw_text(surface, text, font, color, x, y, center=False):
    image = font.render(str(text), True, color)
    rect = image.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(image, rect)
    return rect


def draw_airplane(surface, rect, color=(235, 242, 250)):
    """Draw a simple top-down plane; no external image assets needed."""
    cx, cy = rect.center
    # Wings
    pygame.draw.polygon(
        surface, (95, 175, 235),
        [(cx - 8, cy - 5), (cx - 27, cy - 15), (cx - 24, cy - 3),
         (cx - 17, cy + 5), (cx - 8, cy + 7)]
    )
    pygame.draw.polygon(
        surface, (95, 175, 235),
        [(cx + 8, cy - 5), (cx + 27, cy - 15), (cx + 24, cy - 3),
         (cx + 17, cy + 5), (cx + 8, cy + 7)]
    )
    # Fuselage and tail
    pygame.draw.polygon(
        surface, color,
        [(cx, cy - 20), (cx - 8, cy - 3), (cx - 7, cy + 13),
         (cx, cy + 18), (cx + 7, cy + 13), (cx + 8, cy - 3)]
    )
    pygame.draw.polygon(
        surface, (220, 75, 75),
        [(cx - 5, cy + 9), (cx - 13, cy + 16), (cx - 5, cy + 15),
         (cx + 5, cy + 15), (cx + 13, cy + 16), (cx + 5, cy + 9)]
    )
    pygame.draw.ellipse(surface, (30, 65, 100), (cx - 4, cy - 7, 8, 11))
    pygame.draw.circle(surface, (255, 255, 255), (cx, cy - 14), 2)


def draw_bird(surface, x, y, flock=False):
    """Draw a bird or flock as simple V-shaped silhouettes."""
    count = 5 if flock else 1
    for i in range(count):
        bx = int(x + i * 11)
        by = int(y + (i % 2) * 5)
        color = (38, 48, 60)
        pygame.draw.arc(surface, color, (bx, by, 14, 10), math.pi, math.pi * 1.8, 3)
        pygame.draw.arc(surface, color, (bx + 8, by, 14, 10), math.pi * 1.2, math.pi * 2, 3)


def draw_meteor(surface, x, y):
    x, y = int(x), int(y)
    pygame.draw.line(surface, (255, 125, 70), (x, y - 18), (x, y - 4), 4)
    pygame.draw.circle(surface, (100, 90, 90), (x, y + 3), 9)
    pygame.draw.circle(surface, (165, 145, 125), (x - 3, y), 3)
    pygame.draw.circle(surface, (70, 65, 65), (x + 4, y + 5), 2)


def draw_coin(surface, x, y):
    x, y = int(x), int(y)
    pygame.draw.circle(surface, (180, 120, 10), (x, y), 12)
    pygame.draw.circle(surface, GOLD, (x, y), 9)
    draw_text(surface, "$", FONT_SMALL, (130, 80, 0), x, y - 1, center=True)


def draw_lightning(surface, x, y):
    points = [(x + 4, y), (x - 5, y + 15), (x + 2, y + 15),
              (x - 5, y + 30), (x + 12, y + 10), (x + 4, y + 10)]
    pygame.draw.polygon(surface, YELLOW, points)


def make_obstacle(kind, stage_index):
    if kind == "bird":
        width, height = 30, 20
        y = random.randint(100, HEIGHT - 90)
        return {"kind": kind, "x": WIDTH + 20, "y": y,
                "rect": pygame.Rect(WIDTH + 20, y, width, height),
                "speed": random.randint(180, 270) + stage_index * 22,
                "hit": False}
    if kind == "flock":
        width, height = 65, 25
        y = random.randint(100, HEIGHT - 90)
        return {"kind": kind, "x": WIDTH + 20, "y": y,
                "rect": pygame.Rect(WIDTH + 20, y, width, height),
                "speed": random.randint(190, 260) + stage_index * 22,
                "hit": False}
    if kind == "meteor":
        x = random.randint(100, WIDTH - 40)
        return {"kind": kind, "x": x, "y": -30,
                "rect": pygame.Rect(x - 10, -30, 20, 25),
                "speed": random.randint(190, 260) + stage_index * 20,
                "hit": False}
    if kind == "lightning":
        x = random.randint(90, WIDTH - 80)
        return {"kind": kind, "x": x, "y": -45,
                "rect": pygame.Rect(x - 12, -45, 25, 40),
                "speed": random.randint(280, 380),
                "hit": False}
    return None


def make_coin():
    y = random.randint(100, HEIGHT - 90)
    return {"x": WIDTH + 20, "y": y,
            "rect": pygame.Rect(WIDTH + 20, y, 25, 25),
            "speed": random.randint(190, 240)}


def main():
    state = "intro"
    stage_index = 0
    player = pygame.Rect(130, HEIGHT // 2, *PLAYER_SIZE)
    hp = 100
    coins = 0
    stage_coins = 0
    stage_elapsed = 0.0
    stage_obstacles = []
    stage_collectibles = []
    stage_obstacles_spawned = {"bird": 0, "flock": 0, "meteor": 0}
    wind_strength = 0.0
    wind_direction = 1
    wind_timer = 0.0
    gust_timer = 0.0
    lightning_timer = random.uniform(3.0, 5.0)
    invulnerable_timer = 0.0
    message_timer = 0.0
    end_message = ""
    clouds = []
    rain = []
    stars = []
    for _ in range(9):
        clouds.append([random.randint(0, WIDTH), random.randint(80, HEIGHT - 50),
                       random.randint(90, 180), random.randint(45, 90)])
    for _ in range(130):
        rain.append([random.randint(0, WIDTH), random.randint(0, HEIGHT),
                     random.randint(5, 15)])
    for _ in range(90):
        stars.append((random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 2)))

    def setup_stage(index):
        nonlocal stage_index, player, hp, stage_coins, stage_elapsed
        nonlocal stage_obstacles, stage_collectibles, stage_obstacles_spawned
        nonlocal wind_strength, wind_direction, wind_timer, gust_timer
        nonlocal lightning_timer, invulnerable_timer, message_timer, end_message
        stage_index = index
        stage = STAGES[index]
        player.x = 130
        player.y = HEIGHT // 2
        hp = 100
        stage_coins = 0
        stage_elapsed = 0.0
        stage_obstacles = []
        stage_collectibles = []
        stage_obstacles_spawned = {"bird": 0, "flock": 0, "meteor": 0}
        wind_strength = random.uniform(stage["wind_min"], stage["wind_max"])
        wind_direction = random.choice([-1, 1])
        wind_timer = 0.0
        gust_timer = 0.0
        lightning_timer = random.uniform(2.0, 4.5)
        invulnerable_timer = 1.0
        message_timer = 0.0
        end_message = ""

    def repair_cost(lost_hp):
        # Every lost 10 HP costs 25 coins.
        return int(math.ceil(max(0, 100 - lost_hp) / 10.0) * REPAIR_COST_PER_10_HP)

    def reset_run():
        nonlocal coins
        coins = 0
        setup_stage(0)

    def draw_background(stage, elapsed):
        weather = stage["weather"]
        if weather == "SUNNY":
            SCREEN.fill((92, 190, 245))
            pygame.draw.circle(SCREEN, (255, 226, 95), (WIDTH - 105, 95), 43)
            for cx, cy, cw, ch in clouds[:3]:
                pygame.draw.ellipse(SCREEN, (230, 245, 255), (cx, cy, cw, ch))
        elif weather == "CLOUDY":
            SCREEN.fill((125, 145, 160))
            for cx, cy, cw, ch in clouds:
                pygame.draw.ellipse(SCREEN, (180, 190, 198), (cx, cy, cw, ch))
                pygame.draw.ellipse(SCREEN, (155, 169, 180), (cx + 25, cy + 10, cw, ch))
            # Clouds obscure the upper and lower parts of the play area.
            pygame.draw.rect(SCREEN, (205, 213, 218), (0, 72, WIDTH, 95))
            pygame.draw.rect(SCREEN, (205, 213, 218), (0, HEIGHT - 135, WIDTH, 95))
        elif weather == "STORM":
            SCREEN.fill((45, 55, 75))
            for cx, cy, cw, ch in clouds:
                pygame.draw.ellipse(SCREEN, (65, 72, 90), (cx, cy, cw, ch))
            for x, y, length in rain:
                pygame.draw.line(SCREEN, (165, 195, 220), (x, y), (x - 8, y + length), 2)
        else:  # NIGHT
            SCREEN.fill((8, 15, 38))
            for sx, sy, size in stars:
                pygame.draw.circle(SCREEN, (210, 225, 255), (sx, sy), size)
            pygame.draw.circle(SCREEN, (220, 230, 245), (WIDTH - 120, 105), 35)
            pygame.draw.circle(SCREEN, (8, 15, 38), (WIDTH - 135, 92), 32)
            # Soft dark overlay makes obstacles harder to see.
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 15, 45))
            SCREEN.blit(overlay, (0, 0))

        # HUD background strip
        pygame.draw.rect(SCREEN, (12, 23, 40), (0, 0, WIDTH, 72))
        pygame.draw.line(SCREEN, (95, 125, 160), (0, 72), (WIDTH, 72), 2)

    def draw_hud(stage, remaining):
        draw_text(SCREEN, f"STAGE {stage_index + 1}/5", FONT, WHITE, 18, 12)
        draw_text(SCREEN, stage["weather"], FONT, YELLOW, 180, 12)
        draw_text(SCREEN, f"TIME {max(0, int(remaining)):02d}s", FONT, WHITE, 330, 12)
        draw_text(SCREEN, f"HP {hp}/100", FONT, GREEN if hp > 40 else RED, 475, 12)
        draw_text(SCREEN, f"COINS {coins}", FONT, GOLD, 620, 12)
        direction_text = "RIGHT ->" if wind_direction > 0 else "<- LEFT"
        draw_text(SCREEN, f"WIND {int(wind_strength)}% {direction_text}", FONT_SMALL, LIGHT_BLUE, 805, 8)
        bar = pygame.Rect(805, 34, 180, 12)
        pygame.draw.rect(SCREEN, DARK_GREY, bar, border_radius=6)
        pygame.draw.rect(SCREEN, LIGHT_BLUE, (bar.x, bar.y, int(bar.width * wind_strength / 100), bar.height), border_radius=6)
        draw_text(SCREEN, "WASD / ARROWS to steer", FONT_SMALL, WHITE, 18, HEIGHT - 31)
        draw_text(SCREEN, f"Stage coins: {stage_coins}", FONT_SMALL, GOLD, 290, HEIGHT - 31)
        if gust_timer > 0:
            draw_text(SCREEN, "WIND GUST!", FONT_MEDIUM, ORANGE, WIDTH // 2, 100, center=True)

    def draw_stage_map():
        SCREEN.fill(NAVY)
        draw_text(SCREEN, "SKYQUEST - FLIGHT PLAN", FONT_BIG, WHITE, WIDTH // 2, 65, center=True)
        draw_text(SCREEN, "Fly through all five airports. Save coins and protect your HP.", FONT, LIGHT_BLUE,
                  WIDTH // 2, 118, center=True)
        points = [(100, 300), (320, 230), (540, 300), (760, 230), (990, 300)]
        pygame.draw.lines(SCREEN, (90, 140, 190), False, points, 4)
        for i, (x, y) in enumerate(points):
            color = GREEN if i == 0 else (YELLOW if i == 1 else LIGHT_BLUE)
            pygame.draw.circle(SCREEN, color, (x, y), 20)
            pygame.draw.circle(SCREEN, WHITE, (x, y), 20, 2)
            draw_text(SCREEN, str(i + 1), FONT, NAVY, x, y, center=True)
            city = STAGES[i]["city"]
            draw_text(SCREEN, city, FONT_SMALL, WHITE, x, y + 38, center=True)
            draw_text(SCREEN, STAGES[i]["weather"], FONT_SMALL, YELLOW, x, y + 62, center=True)
        draw_text(SCREEN, "Controls: WASD or arrow keys | Avoid birds, flocks, meteors and lightning.",
                  FONT_SMALL, WHITE, WIDTH // 2, 440, center=True)
        draw_text(SCREEN, "Each stage lasts 30 seconds. Collect coins and land safely.", FONT_SMALL, WHITE,
                  WIDTH // 2, 468, center=True)
        draw_text(SCREEN, "Press SPACE to start", FONT_MEDIUM, GREEN, WIDTH // 2, 545, center=True)
        draw_text(SCREEN, "Press ESC to quit", FONT_SMALL, GREY, WIDTH // 2, 590, center=True)

    def draw_intro():
        SCREEN.fill(NAVY)
        draw_text(SCREEN, "SKYQUEST", FONT_BIG, WHITE, WIDTH // 2, 100, center=True)
        draw_text(SCREEN, "A pilot, five flights, one debt to repay.", FONT_MEDIUM, YELLOW,
                  WIDTH // 2, 175, center=True)
        intro_lines = [
            "You are a pilot who owes a large debt.",
            "Complete five 30-second flights and land at every airport.",
            "Avoid birds, flocks, falling meteors and storm lightning.",
            "Wind pushes your plane, so counter-steer to stay safe.",
            "Earn 200 coins per completed stage and collect 50-coin pickups.",
            "Repair costs 25 coins for every 10 HP lost between stages.",
            "FINAL GOAL: reach Helsinki with at least 1,500 coins and 30 HP.",
        ]
        for i, line in enumerate(intro_lines):
            draw_text(SCREEN, line, FONT, WHITE, WIDTH // 2, 255 + i * 38, center=True)
        draw_text(SCREEN, "Press SPACE to view the route map", FONT_MEDIUM, GREEN,
                  WIDTH // 2, 555, center=True)
        draw_text(SCREEN, "WASD / arrow keys to fly | ESC to quit", FONT_SMALL, GREY,
                  WIDTH // 2, 600, center=True)

    def draw_landing_screen():
        SCREEN.fill(NAVY)
        stage = STAGES[stage_index]
        draw_text(SCREEN, "LANDING SUCCESSFUL!", FONT_BIG, GREEN, WIDTH // 2, 100, center=True)
        draw_text(SCREEN, f"You reached {stage['city']}", FONT_MEDIUM, WHITE, WIDTH // 2, 175, center=True)
        draw_text(SCREEN, f"Stage reward: +{STAGE_REWARD} coins", FONT, GOLD, WIDTH // 2, 240, center=True)
        draw_text(SCREEN, f"Coins collected this stage: {stage_coins}", FONT, GOLD, WIDTH // 2, 280, center=True)
        draw_text(SCREEN, f"Wallet before repairs: {coins}", FONT, WHITE, WIDTH // 2, 320, center=True)
        if stage_index < 4:
            cost = math.ceil((100 - hp) / 10) * REPAIR_COST_PER_10_HP
            cost = max(0, cost)
            draw_text(SCREEN, f"Repair to 100 HP: {cost} coins", FONT, LIGHT_BLUE,
                      WIDTH // 2, 370, center=True)
            draw_text(SCREEN, "Press SPACE to repair and continue", FONT_MEDIUM, GREEN,
                      WIDTH // 2, 465, center=True)
            draw_text(SCREEN, "Press R to restart the whole run", FONT_SMALL, GREY,
                      WIDTH // 2, 520, center=True)
        else:
            draw_text(SCREEN, f"Final HP: {hp}/100", FONT, WHITE, WIDTH // 2, 365, center=True)
            draw_text(SCREEN, f"Final coins: {coins}", FONT, GOLD, WIDTH // 2, 405, center=True)
            if coins >= TARGET_COINS and hp >= TARGET_FINAL_HP:
                draw_text(SCREEN, "YOU COMPLETED SKYQUEST!", FONT_MEDIUM, GREEN,
                          WIDTH // 2, 470, center=True)
                draw_text(SCREEN, "You reached Helsinki, kept enough coins and protected your plane.",
                          FONT_SMALL, WHITE, WIDTH // 2, 515, center=True)
            else:
                missing = []
                if coins < TARGET_COINS:
                    missing.append(f"Need {TARGET_COINS - coins} more coins")
                if hp < TARGET_FINAL_HP:
                    missing.append(f"Need {TARGET_FINAL_HP - hp} more HP")
                draw_text(SCREEN, "Flight complete, but final goal not met.", FONT_MEDIUM, ORANGE,
                          WIDTH // 2, 470, center=True)
                draw_text(SCREEN, " | ".join(missing), FONT_SMALL, WHITE, WIDTH // 2, 515, center=True)
            draw_text(SCREEN, "Press R to play again | ESC to quit", FONT_SMALL, GREY,
                      WIDTH // 2, 570, center=True)

    def draw_game_over():
        SCREEN.fill((35, 12, 22))
        draw_text(SCREEN, "FLIGHT FAILED", FONT_BIG, RED, WIDTH // 2, 150, center=True)
        draw_text(SCREEN, "Your plane has run out of HP.", FONT_MEDIUM, WHITE,
                  WIDTH // 2, 235, center=True)
        draw_text(SCREEN, f"Coins remaining: {coins}", FONT, GOLD, WIDTH // 2, 300, center=True)
        draw_text(SCREEN, "Press R to restart | ESC to quit", FONT, WHITE, WIDTH // 2, 400, center=True)

    running = True
    while running:
        dt = min(CLOCK.tick(FPS) / 1000.0, 0.04)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif state == "intro" and event.key == pygame.K_SPACE:
                    state = "map"
                elif state == "map" and event.key == pygame.K_SPACE:
                    coins = 0
                    setup_stage(0)
                    state = "playing"
                elif state == "landing":
                    if event.key == pygame.K_r:
                        reset_run()
                        state = "playing"
                    elif event.key == pygame.K_SPACE and stage_index < 4:
                        cost = max(0, math.ceil((100 - hp) / 10) * REPAIR_COST_PER_10_HP)
                        if coins >= cost:
                            coins -= cost
                            hp = 100
                            setup_stage(stage_index + 1)
                            state = "playing"
                        else:
                            end_message = f"Not enough coins to repair! Need {cost}, have {coins}."
                    elif event.key == pygame.K_r and stage_index == 4:
                        reset_run()
                        state = "playing"
                elif state == "gameover" and event.key == pygame.K_r:
                    reset_run()
                    state = "playing"

        if state == "intro":
            draw_intro()
        elif state == "map":
            draw_stage_map()
        elif state == "playing":
            stage = STAGES[stage_index]
            stage_elapsed += dt
            invulnerable_timer = max(0.0, invulnerable_timer - dt)
            gust_timer = max(0.0, gust_timer - dt)
            remaining = stage["duration"] - stage_elapsed

            # Wind behavior changes according to the stage.
            wind_timer += dt
            if stage["wind_mode"] == "change" and wind_timer >= 3.5:
                wind_timer = 0.0
                wind_direction *= -1
                wind_strength = random.uniform(stage["wind_min"], stage["wind_max"])
            elif stage["wind_mode"] == "gust" and wind_timer >= random.uniform(2.2, 4.0):
                wind_timer = 0.0
                wind_direction = random.choice([-1, 1])
                wind_strength = random.uniform(stage["wind_min"], stage["wind_max"])
                gust_timer = 1.2
            elif stage["wind_mode"] == "steady":
                wind_strength = (stage["wind_min"] + stage["wind_max"]) / 2

            keys = pygame.key.get_pressed()
            dx = 0
            dy = 0
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx -= PLAYER_SPEED * dt
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx += PLAYER_SPEED * dt
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dy -= PLAYER_SPEED * dt
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dy += PLAYER_SPEED * dt

            # Wind affects horizontal movement every frame.
            wind_multiplier = 1.7 if gust_timer > 0 else 1.0
            player.x += int(dx + wind_direction * wind_strength * wind_multiplier * 0.75 * dt)
            player.y += int(dy)
            player.x = int(clamp(player.x, 15, WIDTH - player.width - 15))
            player.y = int(clamp(player.y, 85, HEIGHT - player.height - 50))

            # Spawn each obstacle type across the 30-second stage.
            for kind in ("bird", "flock", "meteor"):
                target = stage[{"bird": "single_birds", "flock": "flocks", "meteor": "meteors"}[kind]]
                if stage_obstacles_spawned[kind] < target:
                    # Spawn evenly with small random variation.
                    interval = stage["duration"] / target
                    if stage_elapsed >= (stage_obstacles_spawned[kind] * interval +
                                         random.uniform(0.1, min(1.0, interval * 0.3))):
                        stage_obstacles.append(make_obstacle(kind, stage_index))
                        stage_obstacles_spawned[kind] += 1

            # Coins move horizontally across the screen.
            target_coins = stage["coins"]
            if len(stage_collectibles) + sum(1 for _ in []) < target_coins:
                if not hasattr(main, "_coin_spawn_timer"):
                    main._coin_spawn_timer = 0.0
                main._coin_spawn_timer += dt
                if main._coin_spawn_timer >= 3.8 and stage_coins // COIN_VALUE < target_coins:
                    stage_collectibles.append(make_coin())
                    main._coin_spawn_timer = 0.0
            if stage_index == 2:
                lightning_timer -= dt
                if lightning_timer <= 0:
                    stage_obstacles.append(make_obstacle("lightning", stage_index))
                    lightning_timer = random.uniform(3.0, 5.0)

            # Move and collide with obstacles.
            for obstacle in stage_obstacles[:]:
                if obstacle["kind"] in ("bird", "flock"):
                    obstacle["x"] -= obstacle["speed"] * dt
                else:
                    obstacle["y"] += obstacle["speed"] * dt
                obstacle["rect"].x = int(obstacle["x"])
                obstacle["rect"].y = int(obstacle["y"])

                if obstacle["rect"].colliderect(player) and invulnerable_timer <= 0 and not obstacle["hit"]:
                    hp -= OBSTACLE_DAMAGE
                    obstacle["hit"] = True
                    invulnerable_timer = 0.9
                    # Remove after collision, so one object cannot hit repeatedly.
                    stage_obstacles.remove(obstacle)
                    if hp <= 0:
                        hp = 0
                        state = "gameover"
                        break
                elif (obstacle["x"] < -100 or obstacle["y"] > HEIGHT + 80):
                    if obstacle in stage_obstacles:
                        stage_obstacles.remove(obstacle)

            # Move and collect coins.
            for coin in stage_collectibles[:]:
                coin["x"] -= coin["speed"] * dt
                coin["rect"].x = int(coin["x"])
                if coin["rect"].colliderect(player):
                    coins += COIN_VALUE
                    stage_coins += COIN_VALUE
                    stage_collectibles.remove(coin)
                elif coin["x"] < -50:
                    stage_collectibles.remove(coin)

            # Update rain for moving background.
            if stage["weather"] == "STORM":
                for drop in rain:
                    drop[0] -= 130 * dt
                    drop[1] += 360 * dt
                    if drop[1] > HEIGHT:
                        drop[1] = random.randint(-30, 0)
                        drop[0] = random.randint(0, WIDTH)

            draw_background(stage, stage_elapsed)
            # Draw obstacles
            for obstacle in stage_obstacles:
                if obstacle["kind"] in ("bird", "flock"):
                    draw_bird(SCREEN, obstacle["x"], obstacle["y"], obstacle["kind"] == "flock")
                elif obstacle["kind"] == "meteor":
                    draw_meteor(SCREEN, obstacle["x"], obstacle["y"])
                elif obstacle["kind"] == "lightning":
                    draw_lightning(SCREEN, obstacle["x"], obstacle["y"])

            for coin in stage_collectibles:
                draw_coin(SCREEN, coin["x"], coin["y"])

            # Blink plane during brief invulnerability.
            if invulnerable_timer <= 0 or int(invulnerable_timer * 10) % 2 == 0:
                draw_airplane(SCREEN, player)

            draw_hud(stage, remaining)

            if stage_elapsed >= stage["duration"] and state == "playing":
                coins += STAGE_REWARD
                state = "landing"

        elif state == "landing":
            draw_landing_screen()
            if end_message:
                draw_text(SCREEN, end_message, FONT_SMALL, ORANGE, WIDTH // 2, HEIGHT - 35, center=True)
        elif state == "gameover":
            draw_game_over()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
