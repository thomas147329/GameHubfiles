import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Window Setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank Game - WASD & Mouse Click")
clock = pygame.time.Clock()

# Colors
BACKGROUND_COLOR = (30, 30, 30)
TANK_COLOR = (50, 120, 200)
TURRET_COLOR = (30, 80, 150)
ENEMY_TANK_COLOR = (200, 60, 60)
ENEMY_TURRET_COLOR = (140, 30, 30)
BULLET_COLOR = (255, 200, 0)
ENEMY_BULLET_COLOR = (255, 100, 100)
TEXT_COLOR = (255, 255, 255)

# Game Variables
score = 0
player_health = 100
game_over = False
font = pygame.font.SysFont("Arial", 24)
large_font = pygame.font.SysFont("Arial", 48)

class Tank:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 40
        self.speed = 4
        self.angle = 0  

    def move(self, keys):
        if keys[pygame.K_a] and self.x - self.size // 2 > 0:
            self.x -= self.speed
        if keys[pygame.K_d] and self.x + self.size // 2 < WIDTH:
            self.x += self.speed
        if keys[pygame.K_w] and self.y - self.size // 2 > HEIGHT // 2: 
            self.y -= self.speed
        if keys[pygame.K_s] and self.y + self.size // 2 < HEIGHT:
            self.y += self.speed

    def update_angle(self, mouse_pos):
        # Fix applied here: using [0] and [1] to extract variables from the tuple
        rel_x = mouse_pos[0] - self.x
        rel_y = mouse_pos[1] - self.y
        self.angle = math.atan2(rel_y, rel_x)

    def draw(self, surface):
        tank_rect = pygame.Rect(0, 0, self.size, self.size)
        tank_rect.center = (self.x, self.y)
        pygame.draw.rect(surface, TANK_COLOR, tank_rect, border_radius=5)
        
        barrel_len = 30
        end_x = self.x + barrel_len * math.cos(self.angle)
        end_y = self.y + barrel_len * math.sin(self.angle)
        pygame.draw.line(surface, TURRET_COLOR, (self.x, self.y), (end_x, end_y), 8)
        pygame.draw.circle(surface, TURRET_COLOR, (self.x, self.y), 12)

class EnemyTank:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 40
        self.speed = 2
        self.angle = 0
        self.shoot_cooldown = 0
        self.shoot_delay = 90 

    def move_and_aim(self, player_x, player_y):
        self.x += self.speed
        if self.x - self.size // 2 <= 0 or self.x + self.size // 2 >= WIDTH:
            self.speed *= -1
        
        rel_x = player_x - self.x
        rel_y = player_y - self.y
        self.angle = math.atan2(rel_y, rel_x)

    def shoot(self, enemy_bullets):
        if self.shoot_cooldown <= 0:
            enemy_bullets.append(Bullet(self.x, self.y, self.angle, ENEMY_BULLET_COLOR, is_enemy=True))
            self.shoot_cooldown = self.shoot_delay
        else:
            self.shoot_cooldown -= 1

    def draw(self, surface):
        tank_rect = pygame.Rect(0, 0, self.size, self.size)
        tank_rect.center = (self.x, self.y)
        pygame.draw.rect(surface, ENEMY_TANK_COLOR, tank_rect, border_radius=5)
        
        barrel_len = 30
        end_x = self.x + barrel_len * math.cos(self.angle)
        end_y = self.y + barrel_len * math.sin(self.angle)
        pygame.draw.line(surface, ENEMY_TURRET_COLOR, (self.x, self.y), (end_x, end_y), 8)
        pygame.draw.circle(surface, ENEMY_TURRET_COLOR, (self.x, self.y), 12)

class Bullet:
    def __init__(self, x, y, angle, color, is_enemy=False):
        self.x = x
        self.y = y
        self.speed = 6 if is_enemy else 8
        self.dx = self.speed * math.cos(angle)
        self.dy = self.speed * math.sin(angle)
        self.radius = 5
        self.color = color

    def update(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def is_offscreen(self):
        return self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT


# Entity Instantiation
player_tank = Tank(WIDTH // 2, HEIGHT - 80)
enemy_tank = EnemyTank(WIDTH // 2, 80)
player_bullets = []
enemy_bullets = []

# Game Loop
running = True
while running:
    clock.tick(60)
    screen.fill(BACKGROUND_COLOR)

    # Event Processing
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            if event.button == 1:
                player_bullets.append(Bullet(player_tank.x, player_tank.y, player_tank.angle, BULLET_COLOR))

    if not game_over:
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        player_tank.move(keys)
        player_tank.update_angle(mouse_pos)
        
        enemy_tank.move_and_aim(player_tank.x, player_tank.y)
        enemy_tank.shoot(enemy_bullets)

        # Handle Bullet Mechanics
        for b in player_bullets[:]:
            b.update()
            if b.is_offscreen():
                player_bullets.remove(b)

        for b in enemy_bullets[:]:
            b.update()
            if b.is_offscreen():
                enemy_bullets.remove(b)

        # Collision Boxes
        p_rect = pygame.Rect(player_tank.x - player_tank.size//2, player_tank.y - player_tank.size//2, player_tank.size, player_tank.size)
        e_rect = pygame.Rect(enemy_tank.x - enemy_tank.size//2, enemy_tank.y - enemy_tank.size//2, enemy_tank.size, enemy_tank.size)

        # Check Player Hits Enemy
        for b in player_bullets[:]:
            if b.get_rect().colliderect(e_rect):
                player_bullets.remove(b)
                score += 10
                enemy_tank.x = random.randint(enemy_tank.size, WIDTH - enemy_tank.size)

        # Check Enemy Hits Player
        for b in enemy_bullets[:]:
            if b.get_rect().colliderect(p_rect):
                enemy_bullets.remove(b)
                player_health -= 20
                if player_health <= 0:
                    player_health = 0
                    game_over = True

    # Render Screen Elements
    if not game_over:
        player_tank.draw(screen)
        enemy_tank.draw(screen)
    
    for b in player_bullets: b.draw(screen)
    for b in enemy_bullets: b.draw(screen)

    # UI Rendering (HUD)
    score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
    health_text = font.render(f"HP: {player_health}%", True, TEXT_COLOR)
    screen.blit(score_text, (15, 15))
    screen.blit(health_text, (WIDTH - 120, 15))

    # Display Game Over Message
    if game_over:
        go_text = large_font.render("GAME OVER", True, ENEMY_TANK_COLOR)
        restart_text = font.render("Close the game to restart!", True, TEXT_COLOR)
        screen.blit(go_text, (WIDTH // 2 - 130, HEIGHT // 2 - 50))
        screen.blit(restart_text, (WIDTH // 2 - 120, HEIGHT // 2 + 10))

    pygame.display.flip()

pygame.quit()
sys.exit()

