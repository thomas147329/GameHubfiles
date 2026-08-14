import math
import random
import sys

try:
    import pygame
except ImportError:
    print("Pygame is required. Install it with: python3 -m pip install pygame")
    sys.exit(1)

WIDTH, HEIGHT = 1000, 650
FPS = 60
FOV = math.radians(70)
NUM_RAYS = 240
MAX_DEPTH = 900
PLAYER_SPEED = 3.2
TURN_SPEED = 0.045
ENEMY_COUNT = 7

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Halo Arena 3D")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Helvetica", 22, bold=True)
big_font = pygame.font.SysFont("Helvetica", 56, bold=True)

# Simple arena map. # = wall, . = floor
MAP = [
    "################",
    "#..............#",
    "#..##......##..#",
    "#..............#",
    "#......##......#",
    "#..............#",
    "#..##......##..#",
    "#..............#",
    "################",
]
TILE = 70
MAP_W = len(MAP[0])
MAP_H = len(MAP)

player = {"x": 2.5 * TILE, "y": 6.5 * TILE, "angle": -0.15, "health": 100}

walls = []
for row, line in enumerate(MAP):
    for col, cell in enumerate(line):
        if cell == "#":
            walls.append((col * TILE, row * TILE, TILE, TILE))

enemies = []
spawn_points = [(5.5, 1.5), (10.5, 1.5), (13.5, 3.5), (5.5, 3.5),
                (10.5, 5.5), (2.5, 7.0), (13.5, 7.0), (7.5, 7.0)]
for i in range(ENEMY_COUNT):
    sx, sy = spawn_points[i]
    enemies.append({"x": sx * TILE, "y": sy * TILE, "health": 100,
                    "cooldown": random.uniform(0.5, 2.0), "flash": 0})

bullets = []
player_shot_cooldown = 0
score = 0
wave = 1
game_over = False
win = False


def reset_game():
    global bullets, score, wave, game_over, win, player_shot_cooldown
    player.update(x=2.5 * TILE, y=6.5 * TILE, angle=-0.15, health=100)
    bullets = []
    score = 0
    wave = 1
    game_over = False
    win = False
    player_shot_cooldown = 0
    enemies.clear()
    for i in range(ENEMY_COUNT):
        sx, sy = spawn_points[i]
        enemies.append({"x": sx * TILE, "y": sy * TILE, "health": 100,
                        "cooldown": random.uniform(0.5, 2.0), "flash": 0})


def blocked(x, y, radius=16):
    for rx, ry, rw, rh in walls:
        if rx - radius < x < rx + rw + radius and ry - radius < y < ry + rh + radius:
            return True
    return False


def move_player(dx, dy):
    nx = player["x"] + dx
    ny = player["y"] + dy
    if not blocked(nx, player["y"]):
        player["x"] = nx
    if not blocked(player["x"], ny):
        player["y"] = ny


def normalize_angle(a):
    while a > math.pi:
        a -= 2 * math.pi
    while a < -math.pi:
        a += 2 * math.pi
    return a


def shoot_player():
    global player_shot_cooldown
    if player_shot_cooldown > 0 or game_over or win:
        return
    player_shot_cooldown = 0.22
    bullets.append({
        "x": player["x"], "y": player["y"],
        "angle": player["angle"], "speed": 14,
        "owner": "player", "life": 70
    })


def enemy_shoot(enemy):
    angle = math.atan2(player["y"] - enemy["y"], player["x"] - enemy["x"])
    bullets.append({
        "x": enemy["x"], "y": enemy["y"],
        "angle": angle, "speed": 7,
        "owner": "enemy", "life": 100
    })


def update(dt):
    global player_shot_cooldown, score, wave, game_over, win

    if game_over or win:
        return

    player_shot_cooldown = max(0, player_shot_cooldown - dt)

    keys = pygame.key.get_pressed()
    move_x = 0
    move_y = 0
    forward_x = math.cos(player["angle"])
    forward_y = math.sin(player["angle"])
    right_x = -math.sin(player["angle"])
    right_y = math.cos(player["angle"])

    if keys[pygame.K_w]:
        move_x += forward_x
        move_y += forward_y
    if keys[pygame.K_s]:
        move_x -= forward_x
        move_y -= forward_y
    if keys[pygame.K_a]:
        move_x -= right_x
        move_y -= right_y
    if keys[pygame.K_d]:
        move_x -= 0
        move_y -= 0
        move_x += right_x
        move_y += right_y

    length = math.hypot(move_x, move_y)
    if length:
        move_player(move_x / length * PLAYER_SPEED, move_y / length * PLAYER_SPEED)

    if keys[pygame.K_LEFT]:
        player["angle"] -= TURN_SPEED
    if keys[pygame.K_RIGHT]:
        player["angle"] += TURN_SPEED

    # Enemies chase the player and fire periodically.
    for enemy in enemies:
        dx = player["x"] - enemy["x"]
        dy = player["y"] - enemy["y"]
        dist = math.hypot(dx, dy)
        enemy["cooldown"] -= dt
        enemy["flash"] = max(0, enemy["flash"] - dt)
        if dist > 120:
            speed = 0.7 + min(0.8, wave * 0.08)
            nx = enemy["x"] + dx / max(dist, 1) * speed
            ny = enemy["y"] + dy / max(dist, 1) * speed
            if not blocked(nx, enemy["y"], 14):
                enemy["x"] = nx
            if not blocked(enemy["x"], ny, 14):
                enemy["y"] = ny
        if enemy["cooldown"] <= 0 and dist < 650:
            enemy_shoot(enemy)
            enemy["cooldown"] = random.uniform(1.0, 2.4)

    for bullet in bullets[:]:
        bullet["x"] += math.cos(bullet["angle"]) * bullet["speed"]
        bullet["y"] += math.sin(bullet["angle"]) * bullet["speed"]
        bullet["life"] -= 1
        if bullet["life"] <= 0 or blocked(bullet["x"], bullet["y"], 3):
            bullets.remove(bullet)
            continue

        if bullet["owner"] == "player":
            for enemy in enemies[:]:
                if math.hypot(bullet["x"] - enemy["x"], bullet["y"] - enemy["y"]) < 22:
                    enemy["health"] -= 50
                    enemy["flash"] = 0.12
                    if bullet in bullets:
                        bullets.remove(bullet)
                    if enemy["health"] <= 0:
                        enemies.remove(enemy)
                        score += 100
                    break
        else:
            if math.hypot(bullet["x"] - player["x"], bullet["y"] - player["y"]) < 20:
                player["health"] -= 12
                bullets.remove(bullet)
                if player["health"] <= 0:
                    player["health"] = 0
                    game_over = True

    if not enemies:
        wave += 1
        for i in range(ENEMY_COUNT + wave - 1):
            sx, sy = random.choice(spawn_points)
            enemies.append({"x": sx * TILE, "y": sy * TILE,
                            "health": 100, "cooldown": random.uniform(0.5, 2.0), "flash": 0})
        if wave >= 4:
            win = True


def cast_ray(angle):
    step = 4
    dist = 0
    while dist < MAX_DEPTH:
        x = player["x"] + math.cos(angle) * dist
        y = player["y"] + math.sin(angle) * dist
        col = int(x // TILE)
        row = int(y // TILE)
        if row < 0 or row >= MAP_H or col < 0 or col >= MAP_W or MAP[row][col] == "#":
            return max(1, dist)
        dist += step
    return MAX_DEPTH


def project_sprite(x, y, size, color):
    dx = x - player["x"]
    dy = y - player["y"]
    dist = math.hypot(dx, dy)
    angle = normalize_angle(math.atan2(dy, dx) - player["angle"])
    if abs(angle) > FOV / 2 + 0.15 or dist < 10:
        return
    corrected = dist * math.cos(angle)
    if corrected <= 0:
        return
    screen_x = WIDTH / 2 + math.tan(angle) / math.tan(FOV / 2) * WIDTH / 2
    height = min(HEIGHT * 1.4, size * 900 / corrected)
    width = height * 0.65
    y_bottom = HEIGHT / 2 + height * 0.48
    pygame.draw.rect(screen, color, (screen_x - width / 2, y_bottom - height, width, height))
    pygame.draw.rect(screen, (20, 20, 20), (screen_x - width * .32, y_bottom - height * .82, width * .18, height * .12))
    pygame.draw.rect(screen, (20, 20, 20), (screen_x + width * .14, y_bottom - height * .82, width * .18, height * .12))


def draw_world():
    screen.fill((18, 25, 34))
    pygame.draw.rect(screen, (25, 45, 30), (0, HEIGHT // 2, WIDTH, HEIGHT // 2))
    pygame.draw.rect(screen, (35, 48, 60), (0, 0, WIDTH, HEIGHT // 2))

    ray_width = WIDTH / NUM_RAYS
    depths = []
    for ray in range(NUM_RAYS):
        angle = player["angle"] - FOV / 2 + FOV * ray / NUM_RAYS
        depth = cast_ray(angle)
        corrected = depth * math.cos(angle - player["angle"])
        depths.append(corrected)
        wall_height = min(HEIGHT * 2, TILE * HEIGHT / max(corrected, 1))
        shade = max(25, int(210 - corrected * 0.22))
        pygame.draw.rect(screen, (shade // 2, shade, shade),
                         (ray * ray_width, HEIGHT / 2 - wall_height / 2, ray_width + 1, wall_height))

    for enemy in sorted(enemies, key=lambda e: math.hypot(e["x"] - player["x"], e["y"] - player["y"]), reverse=True):
        color = (255, 150, 50) if enemy["flash"] > 0 else (180, 45, 55)
        project_sprite(enemy["x"], enemy["y"], 55, color)

    # Weapon / HUD
    pygame.draw.polygon(screen, (55, 65, 72), [(WIDTH//2-55, HEIGHT), (WIDTH//2-30, HEIGHT-150),
                                                (WIDTH//2+25, HEIGHT-150), (WIDTH//2+60, HEIGHT)])
    pygame.draw.rect(screen, (20, 20, 25), (WIDTH//2-10, HEIGHT-190, 20, 100))
    pygame.draw.line(screen, (220, 240, 220), (WIDTH//2-10, HEIGHT//2), (WIDTH//2+10, HEIGHT//2), 2)
    pygame.draw.line(screen, (220, 240, 220), (WIDTH//2, HEIGHT//2-10), (WIDTH//2, HEIGHT//2+10), 2)

    hud = font.render(f"HEALTH {player['health']}    SCORE {score}    WAVE {wave}", True, (235, 245, 235))
    screen.blit(hud, (20, 18))
    controls = font.render("WASD move   ← → turn   SPACE fire   ESC quit", True, (210, 220, 210))
    screen.blit(controls, (20, HEIGHT - 35))


def draw_end(text, color):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 175))
    screen.blit(overlay, (0, 0))
    label = big_font.render(text, True, color)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
    sub = font.render("Press R to restart or ESC to quit", True, (255, 255, 255))
    screen.blit(sub, sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))


running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                shoot_player()
            elif event.key == pygame.K_r and (game_over or win):
                reset_game()

    update(dt)
    draw_world()
    if game_over:
        draw_end("MISSION FAILED", (240, 70, 70))
    elif win:
        draw_end("ARENA CLEARED", (80, 230, 120))
    pygame.display.flip()

pygame.quit()
