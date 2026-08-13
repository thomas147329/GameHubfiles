import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Window Setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Easy Tank Game")
clock = pygame.time.Clock()

# Colors
BACKGROUND_COLOR = (30, 30, 30)
TANK_COLOR = (50, 120, 200)
TURRET_COLOR = (30, 80, 150)
BULLET_COLOR = (255, 200, 0)
TARGET_COLOR = (220, 60, 60)
TEXT_COLOR = (255, 255, 255)

# Game Variables
score = 0
font = pygame.font.SysFont("Arial", 24)

class Tank:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 40
        self.speed = 4
        self.angle = 0  # In degrees

    def move(self, keys):
        # Move up/down/left/right
        if keys[pygame.K_LEFT] and self.x - self.size // 2 > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x + self.size // 2 < WIDTH:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y - self.size // 2 > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y + self.size // 2 < HEIGHT:
            self.y += self.speed

    def update_angle(self, mouse_pos):
        # Aim turret towards the mouse pointer
        rel_x, rel_y = mouse_pos[0] - self.x, mouse_pos[1] - self.y
        self.angle = math.atan2(rel_y, rel_x)

    def draw(self, surface):
        # Draw Tank Base
        tank_rect = pygame.Rect(0, 0, self.size, self.size)
        tank_rect.center = (self.x, self.y)
        pygame.draw.rect(surface, TANK_COLOR, tank_rect, border_radius=5)
        
        # Draw Rotating Turret Barrel
        barrel_len = 30
        end_x = self.x + barrel_len * math.cos(self.angle)
        end_y = self.y + barrel_len * math.sin(self.angle)
        pygame.draw.line(surface, TURRET_COLOR, (self.x, self.y), (end_x, end_y), 8)
        
        # Draw Turret Center
        pygame.draw.circle(surface, TURRET_COLOR, (self.x, self.y), 12)

class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.speed = 8
        # Calculate velocity components based on the tank turret's angle
        self.dx = self.speed * math.cos(angle)
        self.dy = self.speed * math.sin(angle)
        self.radius = 5

    def update(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self, surface):
        pygame.draw.circle(surface, BULLET_COLOR, (int(self.x), int(self.y)), self.radius)

    def is_offscreen(self):
        return self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT

class Target:
    def __init__(self):
        self.size = 30
        self.x = random.randint(self.size, WIDTH - self.size)
        self.y = random.randint(self.size, HEIGHT // 3) # Spawn targets in upper tier
        self.speed_x = random.choice([-2, -1,  1, 2])

    def update(self):
        self.x += self.speed_x
        # Bounce off walls
        if self.x - self.size//2 <= 0 or self.x + self.size//2 >= WIDTH:
            self.speed_x *= -1

    def draw(self, surface):
        target_rect = pygame.Rect(0, 0, self.size, self.size)
        target_rect.center = (self.x, self.y)
        pygame.draw.rect(surface, TARGET_COLOR, target_rect, border_radius=3)

# Entity Instantiation
player_tank = Tank(WIDTH // 2, HEIGHT - 80)
bullets = []
targets = [Target() for _ in range(5)] # Spawn 5 starter targets

# Game Loop
running = True
while running:
    clock.tick(60) # Limits frame rate to 60 FPS
    screen.fill(BACKGROUND_COLOR)

    # Event Processing
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Fire bullet from muzzle position
                bullets.append(Bullet(player_tank.x, player_tank.y, player_tank.angle))

    # Input handling
    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    # Updates
    player_tank.move(keys)
    player_tank.update_angle(mouse_pos)

    # Manage Bullets
    for bullet in bullets[:]:
        bullet.update()
        if bullet.is_offscreen():
            bullets.remove(bullet)

    # Manage Targets
    for target in targets:
        target.update()

    # Collision Detection (Bullet vs Target)
    for bullet in bullets[:]:
        bullet_rect = pygame.Rect(bullet.x - bullet.radius, bullet.y - bullet.radius, bullet.radius * 2, bullet.radius * 2)
        for target in targets[:]:
            target_rect = pygame.Rect(target.x - target.size // 2, target.y - target.size // 2, target.size, target.size)
            
            if bullet_rect.colliderect(target_rect):
                # Safely remove entities if a hit occurs
                if bullet in bullets:
                    bullets.remove(bullet)
                targets.remove(target)
                score += 10
                targets.append(Target()) # Instantly respawn a new target

    # Rendering
    player_tank.draw(screen)
    for bullet in bullets:
        bullet.draw(screen)
    for target in targets:
        target.draw(screen)

    # Draw Score HUD
    score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
    screen.blit(score_text, (15, 15))

    pygame.display.flip()

pygame.quit()
sys.exit()
