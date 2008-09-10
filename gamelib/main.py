#!/usr/bin/env python
import sys
import os

# Make sure we can include the extra modules
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(current_dir, '..', 'lib'))

import data
import pyglet
import ode

from console import Console
from physics import PhysicsBox, PhysicsCylinder

# Gameplay constants
DISPLAY_FPS = True
GRAVITY = -100.0
PHYSICS_STEP = 0.005
FPS_LIMIT = 0 # 0 for no limit
PLAYER_SPEED = 5.0
PLAYER_SPEED_STEP = 1.0
PLAYER_SPEED_TIME = 25.0 # The amount of times speed should be updated per second
CONSOLE_SPEED = 0.25

# Set up Pyglet
window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

# Set up ODE
world = ode.World()
world.setGravity((0, GRAVITY, 0))
space = ode.Space()
contactgroup = ode.JointGroup()

# Background sprite
background_image = pyglet.image.load(data.filepath('background.png'))
background = pyglet.sprite.Sprite(background_image)

# Physics limits
roof = ode.GeomPlane(space, (0, -1, 0), -background.height)
floor = ode.GeomPlane(space, (0, 1, 0), 0)
wall_left = ode.GeomPlane(space, (1, 0, 0), 0)
wall_right = ode.GeomPlane(space, (-1, 0, 0), -background.width)

# Player
class Player(PhysicsCylinder):
    def __init__(self):
        super(Player, self).__init__(world, space, batch, 'yarn.png')
        self.speed_dt = 0
        
        self.body.setPosition((200, 300, 0))
        self.body.setAngularVel((0, 0, 10))
        self.body.setLinearVel((500, 0, 0))

    def move_left(self, dt):
        self.update_speed(dt, 'left')

    def move_right(self, dt):
        self.update_speed(dt, 'right')

    def update_speed(self, dt, direction):
        zspeed = self.body.getAngularVel()[2]
        if direction == 'left' and zspeed < PLAYER_SPEED:
            zspeed = min(PLAYER_SPEED, zspeed + PLAYER_SPEED_STEP * PLAYER_SPEED_TIME * dt)
        elif direction == 'right' and zspeed > -PLAYER_SPEED:
            zspeed = max(-PLAYER_SPEED, zspeed - PLAYER_SPEED_STEP * PLAYER_SPEED_TIME * dt)
        self.body.setAngularVel((0, 0, zspeed))

player = Player()

# Console
console = Console(window, globals())

# Physics
def near_callback(args, geom1, geom2):
    contacts = ode.collide(geom1, geom2)
    for contact in contacts:
        contact.setMu(ode.Infinity)
        contact.setBounce(1)
        joint = ode.ContactJoint(world, contactgroup, contact)
        joint.attach(geom1.getBody(), geom2.getBody())

# Input
@window.event
def on_text(text):
    if console.is_active():
		console.on_text(text)

@window.event
def on_text_motion(motion):
    if console.is_active():
		console.on_text_motion(motion)

@window.event
def on_key_press(symbol, modifiers):
    key = pyglet.window.key

    # Block all input while console is open (except closing the console)
    if symbol == key.GRAVE:
        console.toggle()
        return
    elif console.is_active():
        return

    if symbol == key.LEFT:
        pyglet.clock.schedule_interval(player.move_left, 1.0 / PLAYER_SPEED_TIME)
    elif symbol == key.RIGHT:
        pyglet.clock.schedule_interval(player.move_right, 1.0 / PLAYER_SPEED_TIME)

@window.event
def on_key_release(symbol, modifers):
    key = pyglet.window.key

    if symbol == key.LEFT:
        pyglet.clock.unschedule(player.move_left)
    elif symbol == key.RIGHT:
        pyglet.clock.unschedule(player.move_right)

# Test sprite
puffnfresh_image = pyglet.image.load(data.filepath("puffnfresh_pixel.gif"))
puffnfresh = pyglet.sprite.Sprite(puffnfresh_image, batch=batch)
puffnfresh_position = (600, 200)
#puffnfresh_geom = ode.GeomBox(space, (puffnfresh_image.width, puffnfresh_image.height, 1.0))
#puffnfresh_geom.setPosition((puffnfresh_position[0] + puffnfresh_image.width / 2, puffnfresh_position[1] + puffnfresh_image.height / 2, 0))

penguin = PhysicsBox(world, space, batch, 'linux_penguin.gif')
penguin.getBody().setPosition((100, 100, 0))

# Main
def get_window_position(position, offset):
    return position[0] + offset[0], position[1] + offset[1]

physics_dt = 0.0
def update(dt):
    player.update()
    penguin.update()
 
    # Position everything but try to keep player in the middle of the screen
    player_pos = player.body.getPosition()[0:2]
    player_offset = (window.width / 2 - player_pos[0], window.height / 2 - player_pos[1])
    window_offset = [0, 0]
    if player_offset[0] > 0:
        window_offset[0] = player_offset[0]
    elif player_offset[0] < -(background_image.width - window.width):
        window_offset[0] = background_image.width - window.width + player_offset[0]

    if player_offset[1] > 0:
        window_offset[1] = player_offset[1]
    elif player_offset[1] < -(background_image.height - window.height):
        window_offset[1] = background_image.height - window.height + player_offset[1]

    object_offset = (player_offset[0] - window_offset[0], player_offset[1] - window_offset[1])

    player.sprite.x, player.sprite.y = window.width / 2 - window_offset[0], window.height / 2 - window_offset[1]
    background.position = object_offset
    puffnfresh.position = get_window_position(puffnfresh_position, object_offset)

    penguin.getSprite().position = get_window_position(penguin.getBody().getPosition(), object_offset)

    # Physics
    global physics_dt

    physics_dt += dt
    while physics_dt > PHYSICS_STEP:
        space.collide(None, near_callback)
        world.step(PHYSICS_STEP)
        contactgroup.empty()

        physics_dt -= PHYSICS_STEP

# Graphics
if DISPLAY_FPS:
    fps_display = pyglet.clock.ClockDisplay()

@window.event
def on_draw():
    window.clear()
    background.draw()
    batch.draw()

    if console.is_active():
        console.layout.draw()

    if DISPLAY_FPS:
        fps_display.draw()

    pyglet.clock.tick()

# Intialisation
def main():
    pyglet.clock.set_fps_limit(FPS_LIMIT)
    pyglet.clock.schedule(update)
    pyglet.app.run()

if __name__ == "__main__":
    main()
