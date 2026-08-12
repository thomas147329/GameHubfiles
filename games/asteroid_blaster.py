import tkinter as tk
import random

WIDTH = 800
HEIGHT = 600

BG = "#050510"
PLAYER = "#66ff99"
BULLET = "#ffffff"
ASTEROID_COLORS = ["#aaaaaa", "#888888", "#666666"]

class AsteroidBlaster(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Asteroid Blaster")
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.resizable(False, False)
        self.configure(bg=BG)

        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT, bg=BG, highlightthickness=0)
        self.canvas.pack()
        self.focus_force()

        self.keys = set()
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.player_x = WIDTH // 2
        self.player_y = HEIGHT - 55
        self.bullets = []
        self.asteroids = []
        self.spawn_timer = 0
        self.speed = 3

        self.bind("<KeyPress>", self.key_down)
        self.bind("<KeyRelease>", self.key_up)

        self.player = self.canvas.create_polygon(
            self.player_x, self.player_y - 25,
            self.player_x - 25, self.player_y + 20,
            self.player_x + 25, self.player_y + 20,
            fill=PLAYER, outline=""
        )

        self.update_score()
        self.game_loop()

    def key_down(self, event):
        self.keys.add(event.keysym)
        if event.keysym == "space":
            self.shoot()
        elif event.keysym.lower() == "r" and self.game_over:
            self.restart()

    def key_up(self, event):
        self.keys.discard(event.keysym)

    def move_player(self):
        if "Left" in self.keys:
            self.player_x -= 8
        if "Right" in self.keys:
            self.player_x += 8
        self.player_x = max(30, min(WIDTH - 30, self.player_x))
        self.canvas.coords(
            self.player,
            self.player_x, self.player_y - 25,
            self.player_x - 25, self.player_y + 20,
            self.player_x + 25, self.player_y + 20
        )

    def shoot(self):
        if len(self.bullets) >= 4 or self.game_over:
            return
        bullet = self.canvas.create_rectangle(
            self.player_x - 3, self.player_y - 35,
            self.player_x + 3, self.player_y - 20,
            fill=BULLET, outline=""
        )
        self.bullets.append(bullet)

    def spawn_asteroid(self):
        x = random.randint(25, WIDTH - 25)
        size = random.randint(14, 28)
        asteroid = self.canvas.create_oval(
            x - size, -size * 2, x + size, 0,
            fill=random.choice(ASTEROID_COLORS), outline="#444444"
        )
        self.asteroids.append({"id": asteroid, "x": x, "y": -size, "size": size,
                               "speed": self.speed + random.uniform(0, 2.5)})

    def overlap(self, a, b):
        return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])

    def move_bullets(self):
        for bullet in self.bullets[:]:
            self.canvas.move(bullet, 0, -12)
            box = self.canvas.bbox(bullet)
            if not box or box[3] < 0:
                self.canvas.delete(bullet)
                self.bullets.remove(bullet)
                continue

            for asteroid in self.asteroids[:]:
                asteroid_box = self.canvas.bbox(asteroid["id"])
                if asteroid_box and self.overlap(box, asteroid_box):
                    self.canvas.delete(bullet)
                    self.canvas.delete(asteroid["id"])
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    self.asteroids.remove(asteroid)
                    self.score += 10
                    self.update_score()
                    break

    def move_asteroids(self):
        player_box = self.canvas.bbox(self.player)
        for asteroid in self.asteroids[:]:
            asteroid["y"] += asteroid["speed"]
            self.canvas.move(asteroid["id"], 0, asteroid["speed"])
            box = self.canvas.bbox(asteroid["id"])

            if box and player_box and self.overlap(box, player_box):
                self.canvas.delete(asteroid["id"])
                self.asteroids.remove(asteroid)
                self.lives -= 1
                self.update_score()
                if self.lives <= 0:
                    self.end_game()
                continue

            if box and box[1] > HEIGHT:
                self.canvas.delete(asteroid["id"])
                self.asteroids.remove(asteroid)

    def update_score(self):
        self.canvas.delete("hud")
        self.canvas.create_text(20, 20, anchor="nw", text=f"SCORE: {self.score}",
                               fill="white", font=("Helvetica", 16, "bold"), tags="hud")
        self.canvas.create_text(WIDTH - 20, 20, anchor="ne", text=f"LIVES: {self.lives}",
                               fill="white", font=("Helvetica", 16, "bold"), tags="hud")

    def game_loop(self):
        if self.game_over:
            return

        self.move_player()
        self.move_bullets()
        self.move_asteroids()

        self.spawn_timer += 1
        interval = max(12, 35 - self.score // 100)
        if self.spawn_timer >= interval:
            self.spawn_timer = 0
            self.spawn_asteroid()

        self.speed = 3 + self.score / 500
        self.after(30, self.game_loop)

    def end_game(self):
        self.game_over = True
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 - 20, text="GAME OVER",
                               fill="#ff4444", font=("Helvetica", 50, "bold"), tags="gameover")
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 45, text=f"Final Score: {self.score}",
                               fill="white", font=("Helvetica", 22), tags="gameover")
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 90, text="Press R to restart",
                               fill="white", font=("Helvetica", 16), tags="gameover")

    def restart(self):
        self.canvas.delete("all")
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.player_x = WIDTH // 2
        self.bullets = []
        self.asteroids = []
        self.spawn_timer = 0
        self.speed = 3

        self.player = self.canvas.create_polygon(
            self.player_x, self.player_y - 25,
            self.player_x - 25, self.player_y + 20,
            self.player_x + 25, self.player_y + 20,
            fill=PLAYER, outline=""
        )
        self.update_score()
        self.game_loop()

if __name__ == "__main__":
    AsteroidBlaster().mainloop()
