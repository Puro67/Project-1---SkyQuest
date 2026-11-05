import math
import os
import random
from typing import List, Optional
import pygame
from db_leaderboard import db_manager

pygame.init()

# ==============================================================================
# PROCEDURAL COIN SYSTEM (Coin & CoinSpawner)
# ==============================================================================
class Coin:
    """Represents an individual collectible coin flying towards the aircraft."""

    def __init__(
        self,
        x: float,
        y: float,
        speed: float = 250.0,
        value: int = 1,
        coin_image: Optional[pygame.Surface] = None,
    ):
        self.x = float(x)
        self.y = float(y)
        self.base_y = float(y)
        self.speed = float(speed)
        self.radius = 16
        self.value = value
        self.collected = False
        self.coin_image = coin_image

        # Floating / shimmer animation timer
        self.bob_timer = random.uniform(0.0, math.pi * 2)

    def update(self, dt: float) -> None:
        """Moves the coin leftward towards the player and applies smooth floating."""
        self.x -= self.speed * dt
        self.bob_timer += dt * 4.0
        self.y = self.base_y + math.sin(self.bob_timer) * 4.0

    def get_hitbox(self) -> pygame.Rect:
        """Returns the rectangular bounding box for collision detection."""
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def draw(self, surface: pygame.Surface) -> None:
        """Renders either the loaded Coin sprite or a drawn vector gold coin."""
        cx, cy = int(self.x), int(self.y)
        r = self.radius

        if self.coin_image is not None:
            rect = self.coin_image.get_rect(center=(cx, cy))
            surface.blit(self.coin_image, rect)
        else:
            # Outer dark gold rim
            pygame.draw.circle(surface, (190, 130, 20), (cx, cy), r)
            # Inner bright gold face
            pygame.draw.circle(surface, (255, 215, 0), (cx, cy), r - 2)
            # Specular sheen highlight
            pygame.draw.circle(surface, (255, 245, 180), (cx - 4, cy - 4), r // 3)
            # Coin symbol
            font = pygame.font.SysFont("arial", 15, bold=True)
            glyph = font.render("$", True, (140, 90, 10))
            surface.blit(glyph, glyph.get_rect(center=(cx, cy)))

    def is_offscreen(self) -> bool:
        """Checks if the coin has moved past the left side of the screen."""
        return self.x < -self.radius * 2


class CoinSpawner:
    """Procedurally spawns coins at randomized intervals ahead of the player."""

    def __init__(
        self,
        screen_width: int = 1000,
        screen_height: int = 600,
        min_interval: float = 1.0,
        max_interval: float = 2.4,
    ):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.min_interval = min_interval
        self.max_interval = max_interval

        self.spawn_timer = 0.0
        self.next_spawn_interval = random.uniform(self.min_interval, self.max_interval)
        self.coins: List[Coin] = []

        # Optional sprite texture loader
        self.coin_image = None
        coin_img_path = os.path.join(os.path.dirname(__file__), "Image", "Coin.png")
        if os.path.exists(coin_img_path):
            try:
                loaded = pygame.image.load(coin_img_path)
                self.coin_image = pygame.transform.scale(loaded, (32, 32))
            except Exception:
                self.coin_image = None

    def reset(self) -> None:
        """Clears all active coins when starting a new flight run."""
        self.coins.clear()
        self.spawn_timer = 0.0
        self.next_spawn_interval = random.uniform(self.min_interval, self.max_interval)

    def update(self, dt: float, obstacles: Optional[List[dict]] = None) -> None:
        """Procedurally advances coin movement and triggers spawns ahead of player."""
        for coin in self.coins:
            coin.update(dt)
        self.coins = [c for c in self.coins if not c.is_offscreen() and not c.collected]

        self.spawn_timer += dt
        if self.spawn_timer >= self.next_spawn_interval:
            self.spawn_timer = 0.0
            self.next_spawn_interval = random.uniform(self.min_interval, self.max_interval)
            self._spawn_procedural_coins(obstacles)

    def _spawn_procedural_coins(self, obstacles: Optional[List[dict]]) -> None:
        """Spawns coins procedurally ahead of the player (single, line, or arc)."""
        spawn_x = self.screen_width + 40
        min_y = 80
        max_y = self.screen_height - 90

        formation = random.choices(["single", "arc", "line"], weights=[0.55, 0.30, 0.15])[0]
        candidate_y = random.randint(min_y, max_y)

        if obstacles:
            for obs in obstacles:
                ox = obs.get("x", 0)
                oy = obs.get("y", 0)
                if abs(ox - spawn_x) < 100 and abs(oy - candidate_y) < 60:
                    candidate_y = (candidate_y + 130) % (max_y - min_y) + min_y

        if formation == "single":
            self.coins.append(Coin(x=spawn_x, y=candidate_y, coin_image=self.coin_image))

        elif formation == "line":
            for i in range(3):
                self.coins.append(Coin(x=spawn_x + i * 42, y=candidate_y, coin_image=self.coin_image))

        elif formation == "arc":
            base_y = max(min_y + 40, min(candidate_y, max_y - 40))
            for i in range(4):
                arc_offset = -math.sin(i / 3.0 * math.pi) * 45
                self.coins.append(
                    Coin(x=spawn_x + i * 40, y=base_y + arc_offset, coin_image=self.coin_image)
                )

    def check_collisions(self, player_rect: pygame.Rect) -> int:
        """Accurate collision detection between aircraft and coins."""
        hitbox = player_rect.inflate(8, 8)
        collected_this_frame = 0

        for coin in self.coins:
            if not coin.collected:
                closest_x = max(hitbox.left, min(coin.x, hitbox.right))
                closest_y = max(hitbox.top, min(coin.y, hitbox.bottom))
                distance = math.hypot(coin.x - closest_x, coin.y - closest_y)

                if distance <= coin.radius:
                    coin.collected = True
                    collected_this_frame += coin.value

        return collected_this_frame

    def draw(self, surface: pygame.Surface) -> None:
        """Renders all active coins on screen."""
        for coin in self.coins:
            if not coin.collected:
                coin.draw(surface)


# ==============================================================================
# SCREEN & DISPLAY SETUP
# ==============================================================================
WIDTH = 1000
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SkyQuest")
clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.SysFont("Arial", 76, bold=True)
header_font = pygame.font.SysFont("Arial", 46, bold=True)
font = pygame.font.SysFont("Arial", 36, bold=True)
small_font = pygame.font.SysFont("Arial", 24)
instruction_font = pygame.font.SysFont("Arial", 18)
mono_font = pygame.font.SysFont("Consolas", 18, bold=True)

# Player data
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
spawn_time = random.uniform(1, 3)

# Coin System & Auto-Repair Tracking
coins = 0
coin_spawner = CoinSpawner(WIDTH, HEIGHT)
repair_flash_timer = 0.0

# Leaderboard & End-Game State
name_input = "Pilot"
last_db_result = None
curr_level = 1

# Game states: "menu", "playing1", "playing2", "playing3", "win1", "win2", "win3", "game_over", "leaderboard"
state = "menu"
previous_state = "menu"

# Time limit for each level (seconds)
level_time = 30
time_left = level_time

# ---------------- PRE-LOADED BACKGROUND ASSETS ----------------
# Level 1 Background
sun = pygame.image.load("Image/Sun.png")
sun = pygame.transform.scale(sun, (250, 250))
sun_x = WIDTH - 225
sun_y = -40

cloud = pygame.image.load("Image/whitecloud.png")
clouds = [
    (pygame.transform.scale(cloud, (250, 170)), -60, 100),
    (pygame.transform.scale(cloud, (130, 90)), 200, 40),
    (pygame.transform.scale(cloud, (200, 140)), 420, 330),
    (pygame.transform.scale(cloud, (180, 120)), 650, 100),
    (pygame.transform.scale(cloud, (270, 190)), 800, 370),
    (pygame.transform.scale(cloud, (150, 100)), 520, 50),
    (pygame.transform.scale(cloud, (200, 140)), 100, 400),
    (pygame.transform.scale(cloud, (120, 80)), 750, 270),
]

# Level 2 Background
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
    (pygame.transform.scale(black_cloud, (300, 200)), 700, 350),
]

# Level 3 Background (Sunset Gradient)
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
    color = (
        int(c1[0] + (c2[0] - c1[0]) * k),
        int(c1[1] + (c2[1] - c1[1]) * k),
        int(c1[2] + (c2[2] - c1[2]) * k),
    )
    pygame.draw.line(sunset_bg, color, (0, y), (WIDTH, y))

pygame.draw.circle(sunset_bg, (255, 190, 90), (WIDTH - 220, HEIGHT - 70), 150)
pygame.draw.circle(sunset_bg, (255, 235, 150), (WIDTH - 220, HEIGHT - 70), 105)

for cx, cy, cw, ch in [
    (80, 110, 240, 40),
    (520, 70, 280, 45),
    (780, 190, 200, 35),
    (300, 300, 260, 40),
    (40, 430, 220, 35),
]:
    pygame.draw.ellipse(sunset_bg, (125, 55, 125), (cx, cy, cw, ch))


# Centered text helper
def draw_text(text, text_font, color, center):
    img = text_font.render(str(text), True, color)
    rect = img.get_rect(center=center)
    screen.blit(img, rect)
    return rect


def check_auto_repair():
    """Requirement: Every 10 HP lost costs 10 coins, automatically restoring HP back to 100."""
    global player_hp, coins, repair_flash_timer
    if player_hp < 100 and coins >= 10:
        missing_hp = 100 - player_hp
        chunks_needed = missing_hp // 10
        chunks_affordable = coins // 10
        chunks_to_repair = min(chunks_needed, chunks_affordable)

        if chunks_to_repair > 0:
            coins -= chunks_to_repair * 10
            player_hp += chunks_to_repair * 10
            repair_flash_timer = 1.4


def calculate_score(run_coins, hp, stages, won=False):
    """Calculates final single-run score: coins, remaining HP, stages, and victory bonus."""
    score = (int(run_coins) * 50) + (max(0, int(hp)) * 10) + (int(stages) * 300)
    if won:
        score += 500
    return max(0, score)


def start_level(level_num=1):
    global player_x, player_y, spawn_timer, spawn_time, time_left, curr_level
    curr_level = level_num
    player_x = 100
    player_y = 200
    spawn_timer = 0
    spawn_time = random.uniform(1.0, 3.0)
    time_left = level_time
    obstacles.clear()
    coin_spawner.reset()
    check_auto_repair()


def reset_game():
    global player_hp, coins, repair_flash_timer, last_db_result
    player_hp = 100
    coins = 0
    repair_flash_timer = 0.0
    last_db_result = None
    start_level(1)


running = True
while running:
    dt = clock.tick(60) / 1000.0

    if repair_flash_timer > 0:
        repair_flash_timer -= dt

    # ---------------- EVENT HANDLING ----------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if state in ("win1", "win2", "win3", "game_over", "leaderboard"):
                    state = "menu"
                else:
                    running = False

            elif state == "menu":
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    reset_game()
                    state = "playing1"
                elif event.key == pygame.K_l:
                    previous_state = "menu"
                    last_db_result = None
                    state = "leaderboard"

            elif state == "win1":
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    start_level(2)
                    state = "playing2"
                elif event.key == pygame.K_l:
                    previous_state = "win1"
                    state = "leaderboard"

            elif state == "win2":
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    start_level(3)
                    state = "playing3"
                elif event.key == pygame.K_l:
                    previous_state = "win2"
                    state = "leaderboard"

            elif state in ("win3", "game_over"):
                # Name input for database leaderboard
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    clean_name = name_input.strip() or "Pilot"
                    stages = 3 if state == "win3" else curr_level
                    won = (state == "win3")
                    final_score = calculate_score(coins, player_hp, stages, won)

                    last_db_result = db_manager.record_run_score(
                        clean_name,
                        final_score,
                        coins,
                        hp=player_hp,
                        stages_cleared=stages,
                        status="VICTORY" if won else "CRASHED",
                    )
                    previous_state = state
                    state = "leaderboard"

                elif event.key == pygame.K_BACKSPACE:
                    name_input = name_input[:-1]
                elif event.key == pygame.K_l:
                    previous_state = state
                    state = "leaderboard"
                elif event.unicode and len(name_input) < 14:
                    if event.unicode.isalnum() or event.unicode in (" ", "-", "_"):
                        name_input += event.unicode.upper()

            elif state == "leaderboard":
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_m):
                    state = "menu"

    # ---------------- START SCREEN ----------------
    if state == "menu":
        screen.fill((90, 190, 245))
        draw_text("SKYQUEST", title_font, (255, 255, 255), (WIDTH // 2, 75))
        screen.blit(player, (WIDTH // 2 - 45, 250))

        draw_text(
            "Fly through three levels, dodge obstacles, and collect coins to auto-repair your plane back to 100 HP!",
            instruction_font,
            (255, 255, 255),
            (WIDTH // 2, 175),
        )
        draw_text(
            "Every 10 HP lost costs 10 coins -> Plane automatically restores back to 100 HP!",
            instruction_font,
            (255, 240, 140),
            (WIDTH // 2, 205),
        )

        if (pygame.time.get_ticks() // 500) % 2 == 0:
            draw_text(
                "Press ENTER or SPACE to start flight",
                small_font,
                (255, 255, 255),
                (WIDTH // 2, 410),
            )
        draw_text(
            "Press [L] to View High Score Leaderboard",
            small_font,
            (255, 215, 0),
            (WIDTH // 2, 460),
        )
        draw_text(
            "Controls: W A S D / Arrow Keys   |   Exit: ESC",
            instruction_font,
            (240, 245, 255),
            (WIDTH // 2, 530),
        )

    # ---------------- PLAYING (LEVELS 1, 2, 3) ----------------
    elif state in ("playing1", "playing2", "playing3"):
        curr_level = 1 if state == "playing1" else (2 if state == "playing2" else 3)
        time_left -= dt

        # Level completion transition
        if time_left <= 0:
            if curr_level == 1:
                state = "win1"
            elif curr_level == 2:
                state = "win2"
            else:
                state = "win3"

        # Player Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            player_y -= player_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            player_y += player_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            player_x += player_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            player_x -= player_speed

        player_x = max(0, min(WIDTH - 50, player_x))
        player_y = max(60, min(HEIGHT - 70, player_y))

        # Spawn obstacles with level-tuned speeds
        spawn_timer += dt
        if spawn_timer >= spawn_time:
            spawn_timer = 0.0
            if curr_level == 1:
                spawn_time = random.uniform(1.0, 3.0)
                obs_speed = random.randint(200, 400)
            elif curr_level == 2:
                spawn_time = random.uniform(0.6, 1.6)
                obs_speed = random.randint(380, 560)
            else:
                spawn_time = random.uniform(0.4, 1.0)
                obs_speed = random.randint(520, 680)

            obstacles.append({
                "x": WIDTH,
                "y": random.randint(70, HEIGHT - obs_h - 10),
                "speed": obs_speed,
            })

        # Update Coin Spawner
        coin_spawner.update(dt, obstacles)

        # Move obstacles & collision check
        player_rect = pygame.Rect(player_x, player_y, player_w, player_h).inflate(-30, -40)

        for ob in obstacles[:]:
            ob["x"] -= ob["speed"] * dt
            ob_rect = pygame.Rect(ob["x"], ob["y"], obs_w, obs_h)

            if player_rect.colliderect(ob_rect):
                player_hp -= 10
                obstacles.remove(ob)
                # Requirement: Every 10 HP lost costs 10 coins, automatically restoring to 100 HP
                check_auto_repair()

                if player_hp <= 0:
                    player_hp = 0
                    state = "game_over"
                    break
            elif ob["x"] < -obs_w:
                obstacles.remove(ob)

        # Coin collision detection & collection
        collected = coin_spawner.check_collisions(player_rect)
        if collected > 0:
            coins += collected
            # Check if newly collected coins can now auto-repair any previously lost HP
            check_auto_repair()

        # Render Background based on level
        if curr_level == 1:
            screen.fill((90, 190, 245))
            screen.blit(sun, (sun_x, sun_y))
            for cloud_surf, x, y in clouds:
                screen.blit(cloud_surf, (x, y))
        elif curr_level == 2:
            screen.fill((35, 40, 65))
            for cloud_surf, x, y in black_clouds:
                screen.blit(cloud_surf, (x, y))
            screen.blit(lightning1, (425, 50))
            screen.blit(lightning2, (-43, 75))
        else:
            screen.blit(sunset_bg, (0, 0))

        # Render Obstacles
        for ob in obstacles:
            screen.blit(obs, (ob["x"], ob["y"]))

        # Render Coins
        coin_spawner.draw(screen)

        # Render Player
        screen.blit(player, (player_x, player_y))

        # HUD Top Banner
        pygame.draw.rect(screen, (20, 30, 48), (0, 0, WIDTH, 54))
        pygame.draw.line(screen, (55, 85, 130), (0, 54), (WIDTH, 54), 2)

        hp_color = (80, 220, 120) if player_hp > 40 else (255, 80, 80)
        screen.blit(font.render(f"HP: {player_hp}/100", True, hp_color), (20, 7))
        screen.blit(font.render(f"Coins: {coins}", True, (255, 215, 0)), (230, 7))
        draw_text(f"LEVEL {curr_level}", font, (255, 255, 255), (WIDTH // 2, 27))
        screen.blit(font.render(f"Time: {int(time_left) + 1}s", True, (130, 205, 255)), (WIDTH - 190, 7))

        # Auto-Repair Visual Flash Notice
        if repair_flash_timer > 0:
            repair_box = pygame.Rect(WIDTH // 2 - 240, 62, 480, 32)
            pygame.draw.rect(screen, (20, 60, 40), repair_box, border_radius=6)
            pygame.draw.rect(screen, (80, 220, 120), repair_box, 2, border_radius=6)
            draw_text("★ AUTO-REPAIR: -10 Coins -> 100 HP RESTORED! ★", instruction_font, (120, 255, 160), repair_box.center)

    # ---------------- LEVEL WINS (1 & 2) ----------------
    elif state == "win1":
        screen.fill((30, 90, 60))
        draw_text("LEVEL 1 COMPLETE!", header_font, (255, 255, 255), (WIDTH // 2, 170))
        draw_text(f"Coins Collected: {coins}  |  Airframe HP: {player_hp}/100", small_font, (255, 215, 0), (WIDTH // 2, 260))
        draw_text("Plane auto-repaired to 100 HP using 10 coins per 10 HP lost.", instruction_font, (200, 245, 220), (WIDTH // 2, 310))
        draw_text("Press ENTER or SPACE to advance to Level 2 (Storm Flight)", small_font, (255, 255, 255), (WIDTH // 2, 410))
        draw_text("Press [L] for Leaderboard", instruction_font, (130, 205, 255), (WIDTH // 2, 480))

    elif state == "win2":
        screen.fill((30, 90, 60))
        draw_text("LEVEL 2 COMPLETE!", header_font, (255, 255, 255), (WIDTH // 2, 170))
        draw_text(f"Storm Conquered! Total Coins: {coins}  |  HP: {player_hp}/100", small_font, (255, 215, 0), (WIDTH // 2, 260))
        draw_text("Plane auto-repaired to 100 HP using 10 coins per 10 HP lost.", instruction_font, (200, 245, 220), (WIDTH // 2, 310))
        draw_text("Press ENTER or SPACE to advance to Final Level 3 (Sunset)", small_font, (255, 255, 255), (WIDTH // 2, 410))
        draw_text("Press [L] for Leaderboard", instruction_font, (130, 205, 255), (WIDTH // 2, 480))

    # ---------------- FINAL VICTORY (WIN 3) ----------------
    elif state == "win3":
        screen.fill((20, 70, 50))
        draw_text("★ MISSION ACCOMPLISHED! ★", header_font, (255, 215, 0), (WIDTH // 2, 70))
        draw_text("You conquered all 3 flight levels!", small_font, (255, 255, 255), (WIDTH // 2, 125))

        calc_sc = calculate_score(coins, player_hp, 3, True)
        card = pygame.Rect(WIDTH // 2 - 270, 160, 540, 130)
        pygame.draw.rect(screen, (28, 48, 40), card, border_radius=10)
        pygame.draw.rect(screen, (255, 215, 0), card, 2, border_radius=10)

        screen.blit(font.render(f"Coins Gathered: {coins}", True, (255, 215, 0)), (card.x + 35, card.y + 18))
        screen.blit(font.render(f"HP: {player_hp}/100", True, (80, 220, 120)), (card.x + 350, card.y + 18))
        screen.blit(font.render(f"TOTAL SCORE: {calc_sc:,} PTS", True, (255, 255, 255)), (card.x + 35, card.y + 70))

        draw_text("ENTER PILOT NAME FOR THE LEADERBOARD:", small_font, (255, 255, 255), (WIDTH // 2, 330))
        in_rect = pygame.Rect(WIDTH // 2 - 180, 360, 360, 48)
        pygame.draw.rect(screen, (15, 25, 40), in_rect, border_radius=8)
        pygame.draw.rect(screen, (255, 215, 0), in_rect, 2, border_radius=8)

        cursor = "|" if (pygame.time.get_ticks() // 450) % 2 == 0 else ""
        draw_text(name_input + cursor, font, (255, 255, 255), in_rect.center)

        draw_text("Press [ENTER] to Save & View Leaderboard", font, (80, 220, 120), (WIDTH // 2, 445))
        draw_text("Press [ESC] to Skip to Main Menu", instruction_font, (170, 190, 210), (WIDTH // 2, 510))

    # ---------------- GAME OVER ----------------
    elif state == "game_over":
        screen.fill((45, 20, 30))
        draw_text("FLIGHT FAILED - AIRFRAME DOWN", header_font, (255, 80, 80), (WIDTH // 2, 70))
        draw_text(f"Plane went down on Level {curr_level}. Out of coins for auto-repair!", instruction_font, (255, 180, 180), (WIDTH // 2, 125))

        calc_sc = calculate_score(coins, 0, curr_level, False)
        card = pygame.Rect(WIDTH // 2 - 270, 155, 540, 125)
        pygame.draw.rect(screen, (30, 25, 40), card, border_radius=10)
        pygame.draw.rect(screen, (255, 80, 80), card, 2, border_radius=10)

        screen.blit(font.render(f"Coins Gathered: {coins}", True, (255, 215, 0)), (card.x + 35, card.y + 18))
        screen.blit(font.render(f"Final Score: {calc_sc:,} PTS", True, (255, 255, 255)), (card.x + 35, card.y + 68))

        draw_text("ENTER PILOT NAME FOR THE LEADERBOARD:", small_font, (255, 255, 255), (WIDTH // 2, 325))
        in_rect = pygame.Rect(WIDTH // 2 - 180, 355, 360, 48)
        pygame.draw.rect(screen, (15, 25, 40), in_rect, border_radius=8)
        pygame.draw.rect(screen, (255, 80, 80), in_rect, 2, border_radius=8)

        cursor = "|" if (pygame.time.get_ticks() // 450) % 2 == 0 else ""
        draw_text(name_input + cursor, font, (255, 255, 255), in_rect.center)

        draw_text("Press [ENTER] to Save & View Leaderboard", font, (80, 220, 120), (WIDTH // 2, 440))
        draw_text("Press [ESC] to Skip to Main Menu", instruction_font, (170, 190, 210), (WIDTH // 2, 505))

    # ---------------- LEADERBOARD DISPLAY ----------------
    elif state == "leaderboard":
        screen.fill((16, 26, 44))
        draw_text("SKYQUEST TOP 10 LEADERBOARD", header_font, (255, 215, 0), (WIDTH // 2, 45))
        draw_text(f"Engine: [{db_manager.active_engine.upper()}] - Personal Best Records", instruction_font, (130, 205, 255), (WIDTH // 2, 85))

        # Result Banner after score submission
        if last_db_result:
            if last_db_result["status"] == "NEW_PERSONAL_BEST":
                msg = f"★ NEW PERSONAL BEST FOR {last_db_result['player_name']}! ★"
                col = (80, 220, 120)
            elif last_db_result["status"] == "NEW_PLAYER_RECORD":
                msg = f"★ FIRST FLIGHT RECORDED FOR {last_db_result['player_name']}! ★"
                col = (255, 215, 0)
            else:
                msg = f"Run score did not beat your personal best ({last_db_result['previous_best']:,} pts)."
                col = (130, 205, 255)
            draw_text(msg, small_font, col, (WIDTH // 2, 114))

        # Leaderboard Table Card
        top_10 = db_manager.fetch_top_10()
        table_rect = pygame.Rect(WIDTH // 2 - 380, 138, 760, 395)
        pygame.draw.rect(screen, (25, 38, 62), table_rect, border_radius=10)
        pygame.draw.rect(screen, (60, 100, 160), table_rect, 2, border_radius=10)

        # Table Header
        hy = table_rect.y + 14
        screen.blit(mono_font.render("RK", True, (130, 205, 255)), (table_rect.x + 20, hy))
        screen.blit(mono_font.render("PILOT CALLSIGN", True, (130, 205, 255)), (table_rect.x + 95, hy))
        screen.blit(mono_font.render("HIGH SCORE", True, (130, 205, 255)), (table_rect.x + 320, hy))
        screen.blit(mono_font.render("COINS", True, (130, 205, 255)), (table_rect.x + 475, hy))
        screen.blit(mono_font.render("DATE", True, (130, 205, 255)), (table_rect.x + 575, hy))
        pygame.draw.line(screen, (60, 100, 160), (table_rect.x + 10, hy + 26), (table_rect.right - 10, hy + 26), 1)

        if not top_10:
            draw_text("No records yet in the database. Complete a run to enter!", small_font, (150, 170, 195), table_rect.center)
        else:
            for idx, entry in enumerate(top_10):
                ry = hy + 35 + idx * 34
                rk_col = (255, 215, 0) if idx == 0 else ((220, 230, 245) if idx == 1 else ((215, 145, 85) if idx == 2 else (160, 180, 200)))
                screen.blit(mono_font.render(f"#{idx+1}", True, rk_col), (table_rect.x + 20, ry))
                screen.blit(mono_font.render(str(entry["player_name"])[:16], True, (255, 255, 255)), (table_rect.x + 95, ry))
                screen.blit(mono_font.render(f"{entry['high_score']:,}", True, (255, 215, 0)), (table_rect.x + 320, ry))
                screen.blit(mono_font.render(str(entry["coins_collected"]), True, (130, 205, 255)), (table_rect.x + 475, ry))
                screen.blit(mono_font.render(str(entry["achieved_at"])[:10], True, (160, 180, 200)), (table_rect.x + 575, ry))

        draw_text("Press [SPACE] or [ENTER] to return to Main Menu", small_font, (130, 205, 255), (WIDTH // 2, 560))

    pygame.display.flip()

pygame.quit()
