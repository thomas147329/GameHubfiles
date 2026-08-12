import tkinter as tk
import random

WIDTH = 800
HEIGHT = 600

PLAYER_SPEED = 8
BULLET_SPEED = 12
ALIEN_BULLET_SPEED = 6
ALIEN_SPEED = 2
ALIEN_DROP = 25

BG = "#050510"
PLAYER_COLOR = "#00ff66"
BULLET_COLOR = "#ffffff"
ALIEN_BULLET_COLOR = "#ff66ff"
ALIEN_COLORS = ["#ff4444", "#ffcc00", "#44ccff"]


class SpaceInvaders(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Space Invaders")
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.resizable(False, False)
        self.configure(bg=BG)

        self.canvas = tk.Canvas(
            self,
            width=WIDTH,
            height=HEIGHT,
            bg=BG,
            highlightthickness=0
        )
        self.canvas.pack()

        self.keys = set()

        self.score = 0
        self.lives = 3
        self.game_over = False
        self.win = False

        self.player_x = WIDTH // 2
        self.player_y = HEIGHT - 60

        self.bullet = None

        # Alien bullets
        self.alien_bullets = []

        self.aliens = []

        self.alien_direction = 1

        self.bind("<KeyPress>", self.key_down)
        self.bind("<KeyRelease>", self.key_up)

        self.focus_force()

        self.create_player()
        self.create_aliens()

        self.update_score()
        self.update_game()


    # -------------------------
    # PLAYER
    # -------------------------

    def create_player(self):

        x = self.player_x
        y = self.player_y

        self.player = self.canvas.create_polygon(
            x, y - 25,
            x - 25, y + 20,
            x + 25, y + 20,
            fill=PLAYER_COLOR,
            outline=""
        )


    def move_player(self):

        if "Left" in self.keys:
            self.player_x -= PLAYER_SPEED

        if "Right" in self.keys:
            self.player_x += PLAYER_SPEED

        self.player_x = max(
            30,
            min(WIDTH - 30, self.player_x)
        )

        self.canvas.coords(
            self.player,
            self.player_x,
            self.player_y - 25,
            self.player_x - 25,
            self.player_y + 20,
            self.player_x + 25,
            self.player_y + 20
        )


    # -------------------------
    # ALIENS
    # -------------------------

    def create_aliens(self):

        start_x = 100
        start_y = 80

        columns = 10
        rows = 4

        for row in range(rows):

            for column in range(columns):

                x = start_x + column * 60
                y = start_y + row * 50

                color = ALIEN_COLORS[
                    row % len(ALIEN_COLORS)
                ]

                alien = self.canvas.create_oval(
                    x - 18,
                    y - 15,
                    x + 18,
                    y + 15,
                    fill=color,
                    outline=""
                )

                self.aliens.append({
                    "id": alien,
                    "x": x,
                    "y": y
                })


    def move_aliens(self):

        if not self.aliens:
            return

        move_x = ALIEN_SPEED * self.alien_direction

        hit_edge = False

        for alien in self.aliens:

            alien["x"] += move_x

            if (
                alien["x"] <= 30
                or alien["x"] >= WIDTH - 30
            ):
                hit_edge = True

        if hit_edge:

            self.alien_direction *= -1

            for alien in self.aliens:
                alien["y"] += ALIEN_DROP

        for alien in self.aliens:

            self.canvas.coords(
                alien["id"],
                alien["x"] - 18,
                alien["y"] - 15,
                alien["x"] + 18,
                alien["y"] + 15
            )


    # -------------------------
    # PLAYER SHOOTING
    # -------------------------

    def shoot(self):

        if self.bullet is not None:
            return

        x = self.player_x
        y = self.player_y - 30

        self.bullet = self.canvas.create_rectangle(
            x - 3,
            y - 10,
            x + 3,
            y,
            fill=BULLET_COLOR,
            outline=""
        )


    def move_bullet(self):

        if self.bullet is None:
            return

        self.canvas.move(
            self.bullet,
            0,
            -BULLET_SPEED
        )

        coords = self.canvas.coords(
            self.bullet
        )

        if not coords:
            return

        if coords[3] < 0:

            self.canvas.delete(
                self.bullet
            )

            self.bullet = None

            return

        self.check_bullet_collision()


    def check_bullet_collision(self):

        if self.bullet is None:
            return

        bullet_box = self.canvas.bbox(
            self.bullet
        )

        if bullet_box is None:
            return

        for alien in self.aliens[:]:

            alien_box = self.canvas.bbox(
                alien["id"]
            )

            if alien_box is None:
                continue

            if self.overlap(
                bullet_box,
                alien_box
            ):

                self.canvas.delete(
                    alien["id"]
                )

                self.aliens.remove(
                    alien
                )

                self.canvas.delete(
                    self.bullet
                )

                self.bullet = None

                self.score += 10

                self.update_score()

                if not self.aliens:
                    self.win_game()

                return


    # -------------------------
    # ALIEN SHOOTING
    # -------------------------

    def alien_shoot(self):

        if not self.aliens:
            return

        # Random chance that an alien fires
        if random.random() > 0.035:
            return

        # Find aliens that are relatively low
        shooters = []

        for alien in self.aliens:

            # Give every alien a chance to shoot
            shooters.append(alien)

        if not shooters:
            return

        alien = random.choice(shooters)

        x = alien["x"]
        y = alien["y"] + 20

        bullet = self.canvas.create_rectangle(
            x - 3,
            y,
            x + 3,
            y + 12,
            fill=ALIEN_BULLET_COLOR,
            outline=""
        )

        self.alien_bullets.append(
            bullet
        )


    def move_alien_bullets(self):

        for bullet in self.alien_bullets[:]:

            self.canvas.move(
                bullet,
                0,
                ALIEN_BULLET_SPEED
            )

            coords = self.canvas.coords(
                bullet
            )

            if not coords:
                self.alien_bullets.remove(
                    bullet
                )
                continue

            # Bullet reached bottom
            if coords[1] > HEIGHT:

                self.canvas.delete(
                    bullet
                )

                self.alien_bullets.remove(
                    bullet
                )

                continue

            self.check_alien_bullet_collision(
                bullet
            )


    def check_alien_bullet_collision(
        self,
        bullet
    ):

        bullet_box = self.canvas.bbox(
            bullet
        )

        player_box = self.canvas.bbox(
            self.player
        )

        if (
            bullet_box
            and player_box
            and self.overlap(
                bullet_box,
                player_box
            )
        ):

            self.canvas.delete(
                bullet
            )

            if bullet in self.alien_bullets:

                self.alien_bullets.remove(
                    bullet
                )

            self.lose_life()


    # -------------------------
    # COLLISION
    # -------------------------

    def overlap(self, a, b):

        return not (
            a[2] < b[0]
            or a[0] > b[2]
            or a[3] < b[1]
            or a[1] > b[3]
        )


    # -------------------------
    # GAME LOOP
    # -------------------------

    def update_game(self):

        if self.game_over or self.win:
            return

        self.move_player()
        self.move_bullet()

        self.move_aliens()

        # Alien shooting
        self.alien_shoot()
        self.move_alien_bullets()

        self.check_alien_attack()

        self.after(
            30,
            self.update_game
        )


    def check_alien_attack(self):

        for alien in self.aliens:

            if alien["y"] >= self.player_y - 20:

                self.lose_life()

                return


    # -------------------------
    # SCORE
    # -------------------------

    def update_score(self):

        self.canvas.delete(
            "score"
        )

        self.canvas.create_text(
            20,
            20,
            anchor="nw",
            text=f"SCORE: {self.score}",
            fill="white",
            font=("Helvetica", 16, "bold"),
            tags="score"
        )

        self.canvas.create_text(
            WIDTH - 20,
            20,
            anchor="ne",
            text=f"LIVES: {self.lives}",
            fill="white",
            font=("Helvetica", 16, "bold"),
            tags="score"
        )


    # -------------------------
    # LIVES
    # -------------------------

    def lose_life(self):

        if self.game_over or self.win:
            return

        self.lives -= 1

        self.update_score()

        if self.lives <= 0:

            self.end_game()

            return

        # Remove existing alien bullets
        for bullet in self.alien_bullets:

            self.canvas.delete(
                bullet
            )

        self.alien_bullets.clear()

        # Move aliens back up
        for alien in self.aliens:

            alien["y"] -= 80

            self.canvas.coords(
                alien["id"],
                alien["x"] - 18,
                alien["y"] - 15,
                alien["x"] + 18,
                alien["y"] + 15
            )


    # -------------------------
    # GAME OVER
    # -------------------------

    def end_game(self):

        self.game_over = True

        self.canvas.create_text(
            WIDTH // 2,
            HEIGHT // 2,
            text="GAME OVER",
            fill="red",
            font=("Helvetica", 50, "bold"),
            tags="gameover"
        )

        self.canvas.create_text(
            WIDTH // 2,
            HEIGHT // 2 + 60,
            text=f"Score: {self.score}",
            fill="white",
            font=("Helvetica", 22),
            tags="gameover"
        )

        self.canvas.create_text(
            WIDTH // 2,
            HEIGHT // 2 + 100,
            text="Press R to restart",
            fill="white",
            font=("Helvetica", 16),
            tags="gameover"
        )


    def win_game(self):

        self.win = True

        self.canvas.create_text(
            WIDTH // 2,
            HEIGHT // 2,
            text="YOU WIN!",
            fill=PLAYER_COLOR,
            font=("Helvetica", 50, "bold"),
            tags="gameover"
        )

        self.canvas.create_text(
            WIDTH // 2,
            HEIGHT // 2 + 60,
            text=f"Score: {self.score}",
            fill="white",
            font=("Helvetica", 22),
            tags="gameover"
        )

        self.canvas.create_text(
            WIDTH // 2,
            HEIGHT // 2 + 100,
            text="Press R to play again",
            fill="white",
            font=("Helvetica", 16),
            tags="gameover"
        )


    # -------------------------
    # KEYBOARD
    # -------------------------

    def key_down(self, event):

        if event.keysym in (
            "Left",
            "Right"
        ):

            self.keys.add(
                event.keysym
            )

        elif event.keysym == "space":

            self.shoot()

        elif event.keysym.lower() == "r":

            if self.game_over or self.win:

                self.restart()


    def key_up(self, event):

        self.keys.discard(
            event.keysym
        )


    # -------------------------
    # RESTART
    # -------------------------

    def restart(self):

        self.canvas.delete(
            "all"
        )

        self.score = 0
        self.lives = 3
        self.game_over = False
        self.win = False

        self.player_x = WIDTH // 2

        self.bullet = None
        self.alien_bullets = []

        self.aliens = []

        self.alien_direction = 1

        self.create_player()
        self.create_aliens()

        self.update_score()
        self.update_game()


if __name__ == "__main__":

    game = SpaceInvaders()
    game.mainloop()
