#!/usr/bin/env python

import sys
import os

# Make sure we can include the extra modules
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(current_dir, '..', 'lib'))

import data
import math
import pyglet
import ode

from console import Console

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

roof = ode.GeomPlane(space, (0, -1, 0), -window.height)
floor = ode.GeomPlane(space, (0, 1, 0), 0)
wall_left = ode.GeomPlane(space, (1, 0, 0), 0)
wall_right = ode.GeomPlane(space, (-1, 0, 0), -window.width)

# Player
class Player():
    def __init__(self):
        self.speed_dt = 0

        self.image = pyglet.image.load(data.filepath('yarn.png'))
        self.image.anchor_x = self.image.width / 2
        self.image.anchor_y = self.image.height / 2

        self.sprite = pyglet.sprite.Sprite(self.image, batch=batch)

        self.body = ode.Body(world)
        self.body.setPosition((200, 300, 0))
        self.body.setAngularVel((0, 0, 10))
        self.body.setLinearVel((500, 0, 0))

        self.mass = ode.Mass()
        self.mass.setCylinder(1, 3, self.image.width / 2, 1)
        self.body.setMass(self.mass)

        self.geom = ode.GeomCylinder(space, self.image.width / 2)
        self.geom.setBody(self.body)

        self.joint2d = ode.Plane2DJoint(world)
        self.joint2d.attach(self.body, ode.environment)

        self.update()

    def update(self):
        self.sprite.x, self.sprite.y = self.body.getPosition()[0:2]

        quaternion = list(self.body.getQuaternion())
        quaternion[1] = quaternion[2] = 0
        self.body.setQuaternion(quaternion)

        matrix = self.body.getRotation()
        rotation = math.atan2(matrix[4], matrix[3]) * 180/math.pi - 90
        self.sprite.rotation = rotation

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

physics_dt = 0.0
def update(dt):
    global physics_dt

    player.update()

    physics_dt += dt
    while physics_dt > PHYSICS_STEP:
        space.collide(None, near_callback)
        world.step(PHYSICS_STEP)
        contactgroup.empty()

        physics_dt -= PHYSICS_STEP

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

# Graphics
if DISPLAY_FPS:
    fps_display = pyglet.clock.ClockDisplay()

@window.event
def on_draw():
    window.clear()
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
