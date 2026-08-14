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
TILE = 70
PLAYER_SPEED = 3.2
MOUSE_SENSITIVITY = 0.0035
PITCH_SENSITIVITY = 0.006
ENEMY_COUNT = 7

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Halo Arena 3D")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Helvetica", 22, bold=True)
big_font = pygame.font.SysFont("Helvetica", 56, bold=True)

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
MAP_W = len(MAP[0])
MAP_H = len(MAP)

player = {"x": 2.5 * TILE, "y": 6.5 * TILE, "angle": -0.15,
          "pitch": 0.0, "health": 100}

walls = []
for row, line in enumerate(MAP):
    for col, cell in enumerate(line):
        if cell == "#":
            walls.append((col * TILE, row * TILE, TILE, TILE))

enemies = []
spawn_points = [(5.5, 1.5), (10.5, 1.5), (13.5, 3.5), (5.5, 3.5),
                (10.5, 5.5), (2.5, 7.0), (13.5, 7.0), (7.5, 7.0)]

bullets = []
player_shot_cooldown = 0
score = 0
wave = 1
game_over = False
win = False


def spawn_enemies(count):
    enemies.clear()
    for _ in range(count):
        sx, sy = random.choice(spawn_points)
        enemies.append({
            "x": sx * TILE,
            "y": sy * TILE,
            "health": 100,
            "cooldown": random.uniform(0.7, 2.0),
            "flash": 0
        })


spawn_enemies(ENEMY_COUNT)


def reset_game():
    global bullets, score, wave, game_over, win, player_shot_cooldown
    player.update(x=2.5 * TILE, y=6.5 * TILE, angle=-0.15, pitch=0.0, health=100)
    bullets = []
    score = 0
    wave = 1
    game_over = False
    win = False
    player_shot_cooldown = 0
    spawn_enemies(ENEMY_COUNT)


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
    player_shot_cooldown = 0.18
    bullets.append({
        "x": player["x"] + math.cos(player["angle"]) * 28,
        "y": player["y"] + math.sin(player["angle"]) * 28,
        "z": player["pitch"] * 300,
        "angle": player["angle"],
        "vertical": player["pitch"],
        "speed": 18,
        "owner": "player",
        "life": 75,
        "color": (255, 235, 90)
    })


def enemy_shoot(enemy):
    angle = math.atan2(player["y"] - enemy["y"], player["x"] - enemy["x"])
    bullets.append({
        "x": enemy["x"],
        "y": enemy["y"],
        "z": 35,
        "angle": angle,
        "vertical": (player["pitch"] * 250 - 35) / 700,
        "speed": 7,
        "owner": "enemy",
        "life": 110,
        "color": (255, 60, 70)
    })


def update(dt):
    global player_shot_cooldown, score, wave, game_over, win
    if game_over or win:
        return

    player_shot_cooldown = max(0, player_shot_cooldown - dt)
    keys = pygame.key.get_pressed()
    move_x = move_y = 0
    fx, fy = math.cos(player["angle"]), math.sin(player["angle"])
    rx, ry = -math.sin(player["angle"]), math.cos(player["angle"])

    if keys[pygame.K_w]: move_x += fx; move_y += fy
    if keys[pygame.K_s]: move_x -= fx; move_y -= fy
    if keys[pygame.K_a]: move_x -= rx; move_y -= ry
    if keys[pygame.K_d]: move_x += rx; move_y += ry

    length = math.hypot(move_x, move_y)
    if length:
        move_player(move_x / length * PLAYER_SPEED, move_y / length * PLAYER_SPEED)

    for enemy in enemies:
        dx, dy = player["x"] - enemy["x"], player["y"] - enemy["y"]
        dist = math.hypot(dx, dy)
        enemy["cooldown"] -= dt
        enemy["flash"] = max(0, enemy["flash"] - dt)
        if dist > 125:
            speed = 0.7 + min(0.8, wave * 0.08)
            nx = enemy["x"] + dx / max(dist, 1) * speed
            ny = enemy["y"] + dy / max(dist, 1) * speed
            if not blocked(nx, enemy["y"], 14): enemy["x"] = nx
            if not blocked(enemy["x"], ny, 14): enemy["y"] = ny
        if enemy["cooldown"] <= 0 and dist < 700:
            enemy_shoot(enemy)
            enemy["cooldown"] = random.uniform(0.9, 2.2)

    for bullet in bullets[:]:
        bullet["x"] += math.cos(bullet["angle"]) * bullet["speed"]
        bullet["y"] += math.sin(bullet["angle"]) * bullet["speed"]
        bullet["z"] += bullet["vertical"] * bullet["speed"]
        bullet["life"] -= 1

        if bullet["life"] <= 0 or blocked(bullet["x"], bullet["y"], 3):
            if bullet in bullets: bullets.remove(bullet)
            continue

        if bullet["owner"] == "player":
            for enemy in enemies[:]:
                if math.hypot(bullet["x"] - enemy["x"], bullet["y"] - enemy["y"]) < 25 and abs(bullet["z"] - 45) < 70:
                    enemy["health"] -= 50
                    enemy["flash"] = 0.12
                    if bullet in bullets: bullets.remove(bullet)
                    if enemy["health"] <= 0:
                        enemies.remove(enemy)
                        score += 100
                    break
        elif math.hypot(bullet["x"] - player["x"], bullet["y"] - player["y"]) < 22 and abs(bullet["z"] - 35) < 70:
            player["health"] -= 12
            if bullet in bullets: bullets.remove(bullet)
            if player["health"] <= 0:
                player["health"] = 0
                game_over = True

    if not enemies:
        if wave >= 4:
            win = True
        else:
            wave += 1
            spawn_enemies(ENEMY_COUNT + wave - 1)


def cast_ray(angle):
    for dist in range(0, MAX_DEPTH, 4):
        x = player["x"] + math.cos(angle) * dist
        y = player["y"] + math.sin(angle) * dist
        col, row = int(x // TILE), int(y // TILE)
        if row < 0 or row >= MAP_H or col < 0 or col >= MAP_W or MAP[row][col] == "#":
            return max(1, dist)
    return MAX_DEPTH


def project_point(x, y, z, size=20):
    dx, dy = x - player["x"], y - player["y"]
    dist = math.hypot(dx, dy)
    angle = normalize_angle(math.atan2(dy, dx) - player["angle"])
    if abs(angle) > FOV / 2 + 0.15 or dist < 8: return None
    corrected = dist * math.cos(angle)
    if corrected <= 0: return None
    sx = WIDTH / 2 + math.tan(angle) / math.tan(FOV / 2) * WIDTH / 2
    horizon = HEIGHT / 2 + player["pitch"] * 500
    sy = horizon - z * 900 / corrected
    scale = max(2, min(180, size * 900 / corrected))
    return sx, sy, scale


def draw_alien(enemy):
    # Detailed armored alien-like enemy made entirely with pygame primitives.
    head = project_point(enemy["x"], enemy["y"], 115, 42)
    body = project_point(enemy["x"], enemy["y"], 55, 70)
    if not head or not body: return
    sx, sy, hs = head
    bx, by, bs = body
    armor = (90, 115, 125) if enemy["flash"] <= 0 else (255, 190, 70)
    dark = (30, 42, 48)
    skin = (75, 105, 82)
    # legs
    pygame.draw.rect(screen, dark, (bx - bs * .35, by + bs * .45, bs * .22, bs * .65))
    pygame.draw.rect(screen, dark, (bx + bs * .13, by + bs * .45, bs * .22, bs * .65))
    # boots
    pygame.draw.ellipse(screen, (18, 22, 25), (bx - bs * .42, by + bs * 1.0, bs * .32, bs * .16))
    pygame.draw.ellipse(screen, (18, 22, 25), (bx + bs * .10, by + bs * 1.0, bs * .32, bs * .16))
    # torso armor
    pygame.draw.polygon(screen, armor, [(bx-bs*.48,by-bs*.42),(bx+bs*.48,by-bs*.42),
                                         (bx+bs*.35,by+bs*.52),(bx-bs*.35,by+bs*.52)])
    pygame.draw.polygon(screen, dark, [(bx-bs*.22,by-bs*.25),(bx+bs*.22,by-bs*.25),
                                       (bx+bs*.18,by+bs*.18),(bx-bs*.18,by+bs*.18)])
    # arms
    pygame.draw.line(screen, armor, (bx-bs*.45,by-bs*.25), (bx-bs*.75,by+bs*.35), max(3,int(bs*.18)))
    pygame.draw.line(screen, armor, (bx+bs*.45,by-bs*.25), (bx+bs*.75,by+bs*.35), max(3,int(bs*.18)))
    # neck and head
    pygame.draw.rect(screen, dark, (sx-hs*.16, sy+hs*.55, hs*.32, hs*.35))
    pygame.draw.ellipse(screen, skin, (sx-hs*.58, sy-hs*.45, hs*1.16, hs*.95))
    # brow / helmet
    pygame.draw.polygon(screen, dark, [(sx-hs*.62,sy-hs*.12),(sx,sy-hs*.48),(sx+hs*.62,sy-hs*.12),
                                       (sx+hs*.48,sy-hs*.02),(sx-hs*.48,sy-hs*.02)])
    # glowing eyes
    eye = (255, 80, 55)
    pygame.draw.ellipse(screen, eye, (sx-hs*.38,sy-hs*.02,sx-hs*.05,sy+hs*.13))
    pygame.draw.ellipse(screen, eye, (sx+hs*.05,sy-hs*.02,sx+hs*.38,sy+hs*.13))
    # shoulder plates
    pygame.draw.circle(screen, armor, (int(bx-bs*.5),int(by-bs*.3)), max(2,int(bs*.16)))
    pygame.draw.circle(screen, armor, (int(bx+bs*.5),int(by-bs*.3)), max(2,int(bs*.16)))


def project_bullet(bullet):
    p = project_point(bullet["x"], bullet["y"], bullet["z"], 18)
    if not p: return
    sx, sy, size = p
    radius = int(max(3, min(14, size)))
    pygame.draw.circle(screen, bullet["color"], (int(sx), int(sy)), radius)
    pygame.draw.circle(screen, (255, 255, 255), (int(sx), int(sy)), max(1, radius // 3))


def draw_world():
    screen.fill((18, 25, 34))
    horizon = int(HEIGHT / 2 + player["pitch"] * 500)
    pygame.draw.rect(screen, (35, 48, 60), (0, 0, WIDTH, max(0, horizon)))
    pygame.draw.rect(screen, (25, 45, 30), (0, horizon, WIDTH, HEIGHT - horizon))

    ray_width = WIDTH / NUM_RAYS
    for ray in range(NUM_RAYS):
        angle = player["angle"] - FOV / 2 + FOV * ray / NUM_RAYS
        depth = cast_ray(angle)
        corrected = depth * math.cos(angle - player["angle"])
        wall_height = min(HEIGHT * 2, TILE * HEIGHT / max(corrected, 1))
        center = HEIGHT / 2 + player["pitch"] * 500
        shade = max(25, int(210 - corrected * 0.22))
        pygame.draw.rect(screen, (shade // 2, shade, shade),
                         (ray * ray_width, center - wall_height / 2, ray_width + 1, wall_height))

    objects = []
    for enemy in enemies:
        objects.append((math.hypot(enemy["x"]-player["x"], enemy["y"]-player["y"]), 0, enemy))
    for bullet in bullets:
        objects.append((math.hypot(bullet["x"]-player["x"], bullet["y"]-player["y"]), 1, bullet))
    objects.sort(key=lambda item: item[0], reverse=True)

    for _, kind, obj in objects:
        if kind == 0:
            draw_alien(obj)
        else:
            project_bullet(obj)

    # Weapon and HUD
    pygame.draw.polygon(screen, (55, 65, 72), [(WIDTH//2-55, HEIGHT), (WIDTH//2-30, HEIGHT-150),
                                                (WIDTH//2+25, HEIGHT-150), (WIDTH//2+60, HEIGHT)])
    pygame.draw.rect(screen, (20,20,25), (WIDTH//2-10, HEIGHT-190, 20, 100))
    mx, my = pygame.mouse.get_pos()
    pygame.draw.line(screen, (220,240,220), (mx-10,my), (mx+10,my), 2)
    pygame.draw.line(screen, (220,240,220), (mx,my-10), (mx,my+10), 2)
    pygame.draw.circle(screen, (220,240,220), (mx,my), 2)
    hud = font.render(f"HEALTH {player['health']}    SCORE {score}    WAVE {wave}", True, (235,245,235))
    screen.blit(hud, (20,18))
    controls = font.render("WASD move   MOUSE look up/down/turn   LEFT CLICK fire   ESC quit", True, (210,220,210))
    screen.blit(controls, (20,HEIGHT-35))


def draw_end(text, color):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0,0,0,175))
    screen.blit(overlay,(0,0))
    label = big_font.render(text, True, color)
    screen.blit(label, label.get_rect(center=(WIDTH//2,HEIGHT//2-30)))
    sub = font.render("Press R to restart or ESC to quit", True, (255,255,255))
    screen.blit(sub, sub.get_rect(center=(WIDTH//2,HEIGHT//2+40)))


pygame.event.set_grab(True)
pygame.mouse.set_visible(False)

running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r and (game_over or win):
                reset_game()
        elif event.type == pygame.MOUSEMOTION and not game_over and not win:
            player["angle"] += event.rel[0] * MOUSE_SENSITIVITY
            player["pitch"] -= event.rel[1] * PITCH_SENSITIVITY
            player["pitch"] = max(-0.75, min(0.75, player["pitch"]))
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            shoot_player()

    update(dt)
    draw_world()
    if game_over:
        draw_end("MISSION FAILED", (240,70,70))
    elif win:
        draw_end("ARENA CLEARED", (80,230,120))
    pygame.display.flip()

pygame.quit()
