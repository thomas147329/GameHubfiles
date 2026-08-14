import tkinter as tk
import random

WIDTH, HEIGHT = 900, 650
TILE = 32
COLS, ROWS = 28, 18
TOP = 70

BLOCKS = {
    "grass": ("Grass", "#58a942"),
    "dirt": ("Dirt", "#8a5a32"),
    "stone": ("Stone", "#777777"),
    "wood": ("Wood", "#9b642f"),
    "sand": ("Sand", "#d9c27a"),
    "water": ("Water", "#3d8fd1"),
}

class MinecraftBuilder(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Minecraft Builder")
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.resizable(False, False)
        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT, bg="#87ceeb", highlightthickness=0)
        self.canvas.pack()
        self.selected = "grass"
        self.world = {}
        self.keys = set()
        self.player_x = COLS // 2
        self.player_y = ROWS // 2
        self.build_world()
        self.bind("<KeyPress>", self.key_down)
        self.bind("<KeyRelease>", self.key_up)
        self.focus_force()
        self.draw()
        self.loop()

    def build_world(self):
        for y in range(ROWS):
            for x in range(COLS):
                if y >= ROWS - 3:
                    self.world[(x, y)] = "stone"
                elif y == ROWS - 4:
                    self.world[(x, y)] = "dirt"
                else:
                    self.world[(x, y)] = "grass"
        # Small lake
        for y in range(10, 14):
            for x in range(4, 10):
                self.world[(x, y)] = "water"
        # Trees
        for x, y in [(15, 10), (21, 7), (24, 12)]:
            for yy in range(y - 3, y):
                self.world[(x, yy)] = "wood"
            for yy in range(y - 5, y - 2):
                for xx in range(x - 1, x + 2):
                    self.world[(xx, yy)] = "grass"

    def key_down(self, event):
        key = event.keysym.lower()
        self.keys.add(key)
        number = {"1":"grass", "2":"dirt", "3":"stone", "4":"wood", "5":"sand", "6":"water"}
        if key in number:
            self.selected = number[key]
            self.draw()
        elif key == "space":
            self.place_block()
        elif key == "e":
            self.remove_block()
        elif key == "r":
            self.build_world()
            self.draw()

    def key_up(self, event):
        self.keys.discard(event.keysym.lower())

    def place_block(self):
        x, y = self.player_x, self.player_y + 1
        if 0 <= x < COLS and 0 <= y < ROWS:
            self.world[(x, y)] = self.selected
            self.draw()

    def remove_block(self):
        x, y = self.player_x, self.player_y + 1
        if (x, y) in self.world:
            self.world[(x, y)] = None
            self.draw()

    def move(self):
        dx = 0
        dy = 0
        if "left" in self.keys: dx -= 1
        if "right" in self.keys: dx += 1
        if "up" in self.keys: dy -= 1
        if "down" in self.keys: dy += 1
        nx = max(0, min(COLS - 1, self.player_x + dx))
        ny = max(0, min(ROWS - 1, self.player_y + dy))
        if self.world.get((nx, ny)) is None:
            self.player_x, self.player_y = nx, ny

    def draw(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, WIDTH, TOP, fill="#222831", outline="")
        self.canvas.create_text(20, 20, anchor="nw", text="MINECRAFT BUILDER", fill="white", font=("Helvetica", 24, "bold"))
        self.canvas.create_text(20, 48, anchor="nw", text="Arrows move • SPACE place • E remove • 1-6 blocks • R reset", fill="#cccccc", font=("Helvetica", 11))
        for (x, y), block in self.world.items():
            if block is None:
                continue
            color = BLOCKS[block][1]
            x1, y1 = x * TILE, TOP + y * TILE
            self.canvas.create_rectangle(x1, y1, x1 + TILE, y1 + TILE, fill=color, outline="#333333")
            if block == "grass":
                self.canvas.create_line(x1, y1 + 6, x1 + TILE, y1 + 6, fill="#79d35b", width=3)
            elif block == "wood":
                self.canvas.create_line(x1 + 8, y1, x1 + 8, y1 + TILE, fill="#70431f", width=2)
            elif block == "water":
                self.canvas.create_line(x1 + 4, y1 + 12, x1 + TILE - 4, y1 + 12, fill="#8fd2ff", width=2)
        px = self.player_x * TILE + TILE // 2
        py = TOP + self.player_y * TILE + TILE // 2
        self.canvas.create_rectangle(px - 10, py - 12, px + 10, py + 12, fill="#e8b08b", outline="#222")
        self.canvas.create_rectangle(px - 10, py - 18, px + 10, py - 8, fill="#3b6ee8", outline="#222")
        self.canvas.create_text(WIDTH - 20, 25, anchor="ne", text="Selected: " + BLOCKS[self.selected][0], fill="white", font=("Helvetica", 14, "bold"))

    def loop(self):
        self.move()
        self.draw()
        self.after(120, self.loop)

if __name__ == "__main__":
    MinecraftBuilder().mainloop()
