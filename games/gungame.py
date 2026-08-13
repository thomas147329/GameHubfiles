import tkinter as tk
import random
import math
import time

class GunGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Gun Game")
        self.root.resizable(False, False)
        
        # Game canvas
        self.canvas_width = 800
        self.canvas_height = 600
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg='black')
        self.canvas.pack()
        
        # Game variables
        self.score = 0
        self.ammo = 10
        self.max_ammo = 10
        self.reloading = False
        self.reload_time = 2  # seconds
        self.reload_start = 0
        
        # Player variables
        self.player_x = self.canvas_width // 2
        self.player_y = self.canvas_height // 2
        self.player_radius = 20
        self.angle = 0
        
        # Target variables
        self.targets = []
        self.target_radius = 25
        self.target_spawn_time = 0
        self.target_spawn_delay = 1.5  # seconds
        
        # Bullet variables
        self.bullets = []
        self.bullet_speed = 15
        self.bullet_radius = 4
        
        # UI elements
        self.score_text = self.canvas.create_text(10, 10, text=f"Score: {self.score}", 
                                                  fill='white', font=('Arial', 16), anchor='nw')
        self.ammo_text = self.canvas.create_text(10, 35, text=f"Ammo: {self.ammo}/{self.max_ammo}", 
                                                 fill='white', font=('Arial', 16), anchor='nw')
        self.reload_text = self.canvas.create_text(self.canvas_width // 2, self.canvas_height - 30, 
                                                   text="", fill='yellow', font=('Arial', 14))
        
        # Draw player
        self.player = self.canvas.create_oval(self.player_x - self.player_radius, 
                                              self.player_y - self.player_radius,
                                              self.player_x + self.player_radius, 
                                              self.player_y + self.player_radius,
                                              fill='blue', outline='white', width=2)
        
        # Draw gun
        self.gun = self.canvas.create_line(self.player_x, self.player_y, 
                                           self.player_x + 40, self.player_y, 
                                           fill='white', width=6)
        
        # Bind events
        self.canvas.bind('<Motion>', self.on_mouse_move)
        self.canvas.bind('<Button-1>', self.on_click)
        self.root.bind('<r>', self.start_reload)
        self.root.bind('<R>', self.start_reload)
        
        # Start game loop
        self.last_time = time.time()
        self.update()
    
    def on_mouse_move(self, event):
        # Update angle based on mouse position
        dx = event.x - self.player_x
        dy = event.y - self.player_y
        self.angle = math.atan2(dy, dx)
        
        # Update gun position
        gun_length = 40
        gun_end_x = self.player_x + gun_length * math.cos(self.angle)
        gun_end_y = self.player_y + gun_length * math.sin(self.angle)
        self.canvas.coords(self.gun, self.player_x, self.player_y, gun_end_x, gun_end_y)
    
    def on_click(self, event):
        if self.reloading:
            return
        
        if self.ammo > 0:
            self.shoot()
        else:
            self.start_reload()
    
    def shoot(self):
        # Reduce ammo
        self.ammo -= 1
        self.update_ammo_text()
        
        # Create bullet
        bullet_x = self.player_x + 40 * math.cos(self.angle)
        bullet_y = self.player_y + 40 * math.sin(self.angle)
        
        bullet = {
            'x': bullet_x,
            'y': bullet_y,
            'dx': self.bullet_speed * math.cos(self.angle),
            'dy': self.bullet_speed * math.sin(self.angle),
            'id': self.canvas.create_oval(bullet_x - self.bullet_radius, 
                                         bullet_y - self.bullet_radius,
                                         bullet_x + self.bullet_radius, 
                                         bullet_y + self.bullet_radius,
                                         fill='yellow')
        }
        self.bullets.append(bullet)
    
    def start_reload(self, event=None):
        if not self.reloading and self.ammo < self.max_ammo:
            self.reloading = True
            self.reload_start = time.time()
            self.canvas.itemconfig(self.reload_text, text="Reloading...")
    
    def update_reload(self):
        if self.reloading:
            elapsed = time.time() - self.reload_start
            if elapsed >= self.reload_time:
                self.ammo = self.max_ammo
                self.reloading = False
                self.canvas.itemconfig(self.reload_text, text="")
                self.update_ammo_text()
            else:
                # Show progress
                progress = int((elapsed / self.reload_time) * 100)
                self.canvas.itemconfig(self.reload_text, text=f"Reloading... {progress}%")
    
    def spawn_target(self):
        # Random position
        x = random.randint(self.target_radius, self.canvas_width - self.target_radius)
        y = random.randint(self.target_radius, self.canvas_height - self.target_radius)
        
        # Random color
        colors = ['red', 'green', 'orange', 'purple', 'pink']
        color = random.choice(colors)
        
        target = {
            'x': x,
            'y': y,
            'id': self.canvas.create_oval(x - self.target_radius, y - self.target_radius,
                                         x + self.target_radius, y + self.target_radius,
                                         fill=color, outline='white', width=2)
        }
        self.targets.append(target)
    
    def update_bullets(self):
        bullets_to_remove = []
        
        for bullet in self.bullets:
            # Move bullet
            bullet['x'] += bullet['dx']
            bullet['y'] += bullet['dy']
            self.canvas.coords(bullet['id'], 
                             bullet['x'] - self.bullet_radius, 
                             bullet['y'] - self.bullet_radius,
                             bullet['x'] + self.bullet_radius, 
                             bullet['y'] + self.bullet_radius)
            
            # Check if bullet is out of bounds
            if (bullet['x'] < 0 or bullet['x'] > self.canvas_width or
                bullet['y'] < 0 or bullet['y'] > self.canvas_height):
                bullets_to_remove.append(bullet)
                continue
            
            # Check collision with targets
            for target in self.targets[:]:
                distance = math.sqrt((bullet['x'] - target['x'])**2 + 
                                   (bullet['y'] - target['y'])**2)
                if distance < self.target_radius:
                    # Hit!
                    self.canvas.delete(target['id'])
                    self.targets.remove(target)
                    bullets_to_remove.append(bullet)
                    self.score += 10
                    self.update_score_text()
                    break
        
        # Remove bullets
        for bullet in bullets_to_remove:
            if bullet in self.bullets:
                self.canvas.delete(bullet['id'])
                self.bullets.remove(bullet)
    
    def update_score_text(self):
        self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
    
    def update_ammo_text(self):
        self.canvas.itemconfig(self.ammo_text, text=f"Ammo: {self.ammo}/{self.max_ammo}")
    
    def update(self):
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        # Update reload
        self.update_reload()
        
        # Spawn targets
        self.target_spawn_time += dt
        if self.target_spawn_time >= self.target_spawn_delay:
            self.spawn_target()
            self.target_spawn_time = 0
            
            # Limit number of targets
            if len(self.targets) > 5:
                oldest_target = self.targets.pop(0)
                self.canvas.delete(oldest_target['id'])
        
        # Update bullets
        self.update_bullets()
        
        # Continue game loop
        self.root.after(16, self.update)  # ~60 FPS

def main():
    root = tk.Tk()
    game = GunGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()
