#!/usr/bin/env python

import sys
import os

# Make sure we can include the extra modules
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(current_dir, '..', 'lib'))

import data
import pyglet
import ode

# Gameplay constants
GRAVITY = -9.81

# Set up Pyglet
window = pyglet.window.Window()

# Set up ODE
world = ode.World()
world.setGravity((0, GRAVITY, 0))
space = ode.Space()

# Player
player = Object()

@window.event
def on_draw():
    window.clear()

def main():
    pyglet.app.run()
