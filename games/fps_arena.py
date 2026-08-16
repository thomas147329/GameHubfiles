import math
import random
import sys
import pygame

pygame.init()

WIDTH, HEIGHT = 1280, 720
HALF_H = HEIGHT // 2
FOV = math.radians(70)
NUM_RAYS = 320
MAX_DEPTH = 24
MOVE_SPEED = 3.6
ROT_SPEED = 2.2
MOUSE_SENS = 0.0025

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FPS Arena")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24, bold=True)
big_font = pygame.font.SysFont("Arial", 56, bold=True)

# 1 = wall, 0 = empty floor
MAP = [
    "1111111111111111",
    "1000000000000001",
    "1011110111111101",
    "1000010000000101",
    "1011010111110101",
    "1000010100010001",
    "1111010101011111",
    "1000010001000001",
    "1011111101111101",
    "1000000000000001",
    "1111111111111111",
]
MAP_W = len(MAP[0])
MAP_H = len(MAP)

player = [2.5, 1.8]
angle = 0.0
health = 100
score = 0
ammo = 12
shoot_cooldown = 0.0
hurt_flash = 0.0

# Enemies are simple billboard sprites drawn as colored rectangles.
enemies = [
    {"x": 7.5, "y": 3.5, "health": 2, "cooldown": 0.0, "alive": True},
    {"x": 12.5, "y": 5.5, "health": 2, "cooldown": 1.0, "alive": True},
    {"x": 5.5, "y": 7.5, "health": 2, "cooldown": 0.5, "alive": True},
    {"x": 13.2, "y": 8.5, "health": 2, "cooldown": 1.5, "alive": True},
]

pygame.event.set_grab(True)
pygame.mouse.set_visible(False)


def wall_at(x, y):
    mx, my = int(x), int(y)
    if mx < 0 or my < 0 or mx >= MAP_W or my >= MAP_H:
        return True
    return MAP[my][mx] == "1"


def move_player(dx, dy):
    nx = player[0] + dx
    ny = player[1] + dy
    if not wall_at(nx, player[1]):
        player[0] = nx
    if not wall_at(player[0], ny):
        player[1] = ny


def distance(ax, ay, bx, by):
    return math.hypot(ax - bx, ay - by)


def angle_difference(a, b):
    return (a - b + math.pi) % (2 * math.pi) - math.pi


def shoot():
    global ammo, shoot_cooldown, score
    if shoot_cooldown > 0 or ammo <= 0:
        return
    ammo -= 1
    shoot_cooldown = 0.28

    # Hit the closest enemy near the center of the crosshair.
    best = None
    best_dist = 999
    for enemy in enemies:
        if not enemy["alive"]:
            continue
        d = distance(player[0], player[1], enemy["x"], enemy["y"])
        if d > 14:
            continue
        target_angle = math.atan2(enemy["y"] - player[1], enemy["x"] - player[0])
        diff = abs(angle_difference(target_angle, angle))
        if diff < 0.07 and d < best_dist:
            # Check line of sight.
            steps = int(d * 20)
            blocked = False
            for i in range(1, steps):
                t = i / steps
                if wall_at(player[0] + (enemy["x"] - player[0]) * t,
                           player[1] + (enemy["y"] - player[1]) * t):
                    blocked = True
                    break
            if not blocked:
                best = enemy
                best_dist = d

    if best:
        best["health"] -= 1
        if best["health"] <= 0:
            best["alive"] = False
            score += 100


def draw_world():
    # Sky and floor.
    screen.fill((35, 55, 85))
    pygame.draw.rect(screen, (35, 35, 38), (0, HALF_H, WIDTH, HALF_H))

    zbuffer = [MAX_DEPTH] * NUM_RAYS
    ray_width = WIDTH / NUM_RAYS

    for r in range(NUM_RAYS):
        ray_angle = angle - FOV / 2 + FOV * r / NUM_RAYS
        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)
        depth = 0.05
        while depth < MAX_DEPTH:
            x = player[0] + cos_a * depth
            y = player[1] + sin_a * depth
            if wall_at(x, y):
                break
            depth += 0.035

        corrected = depth * math.cos(ray_angle - angle)
        corrected = max(corrected, 0.001)
        zbuffer[r] = corrected
        wall_height = min(HEIGHT * 2, int(HEIGHT / corrected))
        shade = max(35, min(210, int(205 / (1 + corrected * 0.12))))
        pygame.draw.rect(
            screen,
            (shade, shade, shade),
            (int(r * ray_width), HALF_H - wall_height // 2, int(ray_width) + 1, wall_height),
        )

    # Draw enemies from farthest to nearest.
    visible = []
    for enemy in enemies:
        if not enemy["alive"]:
            continue
        dx = enemy["x"] - player[0]
        dy = enemy["y"] - player[1]
        d = math.hypot(dx, dy)
        rel = angle_difference(math.atan2(dy, dx), angle)
        if abs(rel) < FOV * 0.65:
            visible.append((d, rel, enemy))
    visible.sort(reverse=True, key=lambda item: item[0])

    for d, rel, enemy in visible:
        corrected = d * math.cos(rel)
        if corrected <= 0.1:
            continue
        sx = WIDTH / 2 + math.tan(rel) / math.tan(FOV / 2) * WIDTH / 2
        size = max(10, min(500, int(HEIGHT / corrected * 0.7)))
        left = int(sx - size / 2)
        top = HALF_H - size // 2
        center_ray = int((sx / WIDTH) * NUM_RAYS)
        if 0 <= center_ray < NUM_RAYS and corrected < zbuffer[center_ray] + 0.3:
            pygame.draw.rect(screen, (190, 45, 45), (left, top, size, size))
            pygame.draw.rect(screen, (40, 20, 20), (left + size // 5, top + size // 4, size // 7, size // 7))
            pygame.draw.rect(screen, (40, 20, 20), (left + size * 3 // 5, top + size // 4, size // 7, size // 7))
            pygame.draw.rect(screen, (30, 30, 30), (left + size // 4, top + size * 2 // 3, size // 2, max(2, size // 10)))


def draw_hud():
    pygame.draw.rect(screen, (15, 15, 18), (18, HEIGHT - 74, 310, 52))
    pygame.draw.rect(screen, (100, 20, 20), (30, HEIGHT - 60, 130, 18))
    pygame.draw.rect(screen, (30, 190, 70), (30, HEIGHT - 60, max(0, 130 * health // 100), 18))
    screen.blit(font.render(f"HP {health}", True, (255, 255, 255)), (175, HEIGHT - 64))
    screen.blit(font.render(f"AMMO {ammo}/12", True, (255, 255, 255)), (18, 18))
    screen.blit(font.render(f"SCORE {score}", True, (255, 255, 255)), (18, 48))
    screen.blit(font.render("WASD move  •  Mouse aim  •  Left click fire  •  R reload", True, (235, 235, 235)), (WIDTH - 520, HEIGHT - 48))

    # Crosshair.
    cx, cy = WIDTH // 2, HEIGHT // 2
    pygame.draw.line(screen, (255, 255, 255), (cx - 9, cy), (cx + 9, cy), 2)
    pygame.draw.line(screen, (255, 255, 255), (cx, cy - 9), (cx, cy + 9), 2)


def reset_game():
    global player, angle, health, score, ammo
    player = [2.5, 1.8]
    angle = 0.0
    health = 100
    score = 0
    ammo = 12
    for enemy in enemies:
        enemy["health"] = 2
        enemy["alive"] = True


def main():
    global angle, health, ammo, shoot_cooldown, hurt_flash
    running = True
    game_over = False

    while running:
        dt = min(clock.tick(60) / 1000.0, 0.05)
        shoot_cooldown = max(0, shoot_cooldown - dt)
        hurt_flash = max(0, hurt_flash - dt)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r and not game_over:
                    ammo = 12
                if event.key == pygame.K_RETURN and game_over:
                    reset_game()
                    game_over = False
            elif event.type == pygame.MOUSEMOTION and not game_over:
                angle += event.rel[0] * MOUSE_SENS
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
                shoot()

        if not game_over:
            keys = pygame.key.get_pressed()
            forward = 0
            strafe = 0
            if keys[pygame.K_w]: forward += 1
            if keys[pygame.K_s]: forward -= 1
            if keys[pygame.K_d]: strafe += 1
            if keys[pygame.K_a]: strafe -= 1
            length = math.hypot(forward, strafe)
            if length:
                forward /= length
                strafe /= length
                move_player(
                    (math.cos(angle) * forward - math.sin(angle) * strafe) * MOVE_SPEED * dt,
                    (math.sin(angle) * forward + math.cos(angle) * strafe) * MOVE_SPEED * dt,
                )

            for enemy in enemies:
                if not enemy["alive"]:
                    continue
                enemy["cooldown"] -= dt
                d = distance(player[0], player[1], enemy["x"], enemy["y"])
                if d < 8 and enemy["cooldown"] <= 0:
                    enemy["cooldown"] = random.uniform(1.0, 2.0)
                    if random.random() < 0.55:
                        health -= 8
                        hurt_flash = 0.18

            if health <= 0:
                health = 0
                game_over = True

            if all(not enemy["alive"] for enemy in enemies):
                game_over = True

        draw_world()
        draw_hud()

        if hurt_flash:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 0, 0, int(80 * hurt_flash / 0.18)))
            screen.blit(overlay, (0, 0))

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            screen.blit(overlay, (0, 0))
            won = all(not enemy["alive"] for enemy in enemies) and health > 0
            title = "ARENA CLEARED!" if won else "YOU DIED"
            screen.blit(big_font.render(title, True, (255, 255, 255)), (WIDTH // 2 - 230, HEIGHT // 2 - 60))
            screen.blit(font.render(f"Score: {score}   Press ENTER to play again", True, (255, 255, 255)), (WIDTH // 2 - 210, HEIGHT // 2 + 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
