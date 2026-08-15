import os
import random
import sys

# Always resolve Minecraft assets relative to this file.
GAME_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(GAME_DIR)

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

# Use integer window dimensions to avoid Ursina/Panda3D float-size warnings.
app = Ursina()
window.size = (2048, 1152)
window.exit_button.visible = False

# Variables
BASE = os.path.join(GAME_DIR, "Assets")
grass_texture = load_texture(os.path.join(BASE, "Textures", "Grass_Block.png"))
stone_texture = load_texture(os.path.join(BASE, "Textures", "Stone_Block.png"))
brick_texture = load_texture(os.path.join(BASE, "Textures", "Brick_Block.png"))
dirt_texture = load_texture(os.path.join(BASE, "Textures", "Dirt_Block.png"))
wood_texture = load_texture(os.path.join(BASE, "Textures", "Wood_Block.png"))
sky_texture = load_texture(os.path.join(BASE, "Textures", "Skybox.png"))
arm_texture = load_texture(os.path.join(BASE, "Textures", "Arm_Texture.png"))
punch_sound = Audio(os.path.join(BASE, "SFX", "Punch_Sound.wav"), loop=False, autoplay=False)
block_pick = 1


def update():
    global block_pick

    if held_keys["left mouse"] or held_keys["right mouse"]:
        hand.active()
    else:
        hand.passive()

    if held_keys["1"]:
        block_pick = 1
    if held_keys["2"]:
        block_pick = 2
    if held_keys["3"]:
        block_pick = 3
    if held_keys["4"]:
        block_pick = 4
    if held_keys["5"]:
        block_pick = 5


class Voxel(Button):
    def __init__(self, position=(0, 0, 0), texture=grass_texture):
        super().__init__(
            parent=scene,
            position=position,
            model=os.path.join(BASE, "Models", "Block"),
            origin_y=0.5,
            texture=texture,
            color=color.color(0, 0, random.uniform(0.9, 1)),
            highlight_color=color.light_gray,
            scale=0.5,
        )

    def input(self, key):
        if not self.hovered:
            return

        if key == "left mouse down":
            punch_sound.play()
            position = self.position + mouse.normal
            if block_pick == 1:
                Voxel(position=position, texture=grass_texture)
            elif block_pick == 2:
                Voxel(position=position, texture=stone_texture)
            elif block_pick == 3:
                Voxel(position=position, texture=brick_texture)
            elif block_pick == 4:
                Voxel(position=position, texture=dirt_texture)
            elif block_pick == 5:
                Voxel(position=position, texture=wood_texture)

        elif key == "right mouse down":
            punch_sound.play()
            destroy(self)


class Sky(Entity):
    def __init__(self):
        super().__init__(
            parent=scene,
            model="Sphere",
            texture=sky_texture,
            scale=150,
            double_sided=True,
        )


class Hand(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model=os.path.join(BASE, "Models", "Arm"),
            texture=arm_texture,
            scale=0.2,
            rotation=Vec3(150, -10, 0),
            position=Vec2(0.4, -0.6),
        )

    def active(self):
        self.position = Vec2(0.3, -0.5)

    def passive(self):
        self.position = Vec2(0.4, -0.6)


# Create the starting world.
for z in range(20):
    for x in range(20):
        Voxel(position=(x, 0, z))

player = FirstPersonController()
sky = Sky()
hand = Hand()

# There is intentionally only ONE app.run() call in this file.
if __name__ == "__main__":
    app.run()
