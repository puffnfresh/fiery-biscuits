#!/usr/bin/env python
import data
import pyglet
import ode

import console
import physics

# Gameplay constants
BENCHMARK = True
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
world.setERP(0.8)
world.setCFM(0.000001)
space = ode.Space()
contactgroup = ode.JointGroup()

# Background sprite
background = pyglet.sprite.Sprite(pyglet.image.load(data.filepath('background.png')))

# Physics limits
roof = ode.GeomPlane(space, (0, -1, 0), -background.height)
floor = ode.GeomPlane(space, (0, 1, 0), 0)
wall_left = ode.GeomPlane(space, (1, 0, 0), 0)
wall_right = ode.GeomPlane(space, (-1, 0, 0), -background.width)

# Player
class Player(physics.PhysicsCylinder):
    def __init__(self):
        super(Player, self).__init__(world, space, 'yarn.png', batch)
        self.speed_dt = 0
        
        self.body.setPosition((200, 300, 0))
        self.body.setAngularVel((0, 0, 10))
        #self.body.setLinearVel((500, 0, 0))

        self.mass.setCylinder(20, 3, self.image.width / 2, 1.0)
        self.body.setMass(self.mass)

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
window_console = console.Console(window, globals())

# Static overlay
class Overlay(object):
    def __init__(self, filename, position, batch=None):
        self.image = pyglet.image.load(data.filepath(filename))
        self.sprite = pyglet.sprite.Sprite(self.image, batch=batch)
        self.position = position

    def getImage(self):
        return self.image

    def getSprite(self):
        return self.sprite

# Physics
def near_callback(args, geom1, geom2):
    if geom1 == geom2:
        print "fierybiscuits: geom1 == geom2"

    contacts = ode.collide(geom1, geom2)
    for contact in contacts:
        contact.setMode(ode.ContactBounce)
        contact.setMu(ode.Infinity)
        contact.setBounce(0.5)
        joint = ode.ContactJoint(world, contactgroup, contact)
        joint.attach(geom1.getBody(), geom2.getBody())

# Input
@window.event
def on_text(text):
    if window_console.is_active():
		window_console.on_text(text)

@window.event
def on_text_motion(motion):
    if window_console.is_active():
		window_console.on_text_motion(motion)

@window.event
def on_key_press(symbol, modifiers):
    key = pyglet.window.key

    # Block all input while console is open (except closing the console)
    if symbol == key.GRAVE:
        window_console.toggle()
        return
    elif window_console.is_active():
        return

    if symbol == key.LEFT:
        pyglet.clock.schedule_interval(player.move_left, 1.0 / PLAYER_SPEED_TIME)
    elif symbol == key.RIGHT:
        pyglet.clock.schedule_interval(player.move_right, 1.0 / PLAYER_SPEED_TIME)
    elif symbol == key.F5:
        pyglet.image.get_buffer_manager().get_color_buffer().save('screenshot.png')

@window.event
def on_key_release(symbol, modifers):
    key = pyglet.window.key

    if symbol == key.LEFT:
        pyglet.clock.unschedule(player.move_left)
    elif symbol == key.RIGHT:
        pyglet.clock.unschedule(player.move_right)

# Levels 
level_physics = []
level_overlays = []
def create_first_level():
    penguin = physics.PhysicsBox(world, space, 'linux_penguin.gif', batch)
    penguin.getBody().setPosition((100, 100, 0))
    level_physics.append(penguin)
    
    ruler = physics.StaticBox(space, 'ruler.png', batch)
    ruler.setPosition((600, 170, 0))
    ruler.setRotation(60)
    level_physics.append(ruler)

    monitor = physics.StaticBox(space, 'monitor.png', batch)
    monitor.setPosition((1000, 207, 0))
    level_physics.append(monitor)

    puffnfresh = Overlay('puffnfresh_pixel.gif', (600, 230), batch)
    level_overlays.append(puffnfresh)

# Main
def get_window_position(position, offset):
    return position[0] + offset[0], position[1] + offset[1]

physics_dt = 0.0
def update(dt):
    player.update()
 
    # Position everything but try to keep player in the middle of the screen
    player_pos = player.body.getPosition()[0:2]
    player_offset = (window.width / 2 - player_pos[0], window.height / 2 - player_pos[1])
    window_offset = [0, 0]
    if player_offset[0] > 0:
        window_offset[0] = player_offset[0]
    elif player_offset[0] < -(background.image.width - window.width):
        window_offset[0] = background.image.width - window.width + player_offset[0]

    if player_offset[1] > 0:
        window_offset[1] = player_offset[1]
    elif player_offset[1] < -(background.image.height - window.height):
        window_offset[1] = background.image.height - window.height + player_offset[1]

    object_offset = (player_offset[0] - window_offset[0], player_offset[1] - window_offset[1])

    player.sprite.x, player.sprite.y = window.width / 2 - window_offset[0], window.height / 2 - window_offset[1]
    background.position = object_offset

    # Convert world positions to screen positions
    for physics in level_physics:
        physics.update()
        physics.getSprite().position = get_window_position(physics.getPosition(), object_offset)

    for overlay in level_overlays:
        overlay.getSprite().position = get_window_position(overlay.position, object_offset)

    # Physics
    global physics_dt

    physics_dt += dt
    # ODE recomends constant world steps to stop jitter
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

    if window_console.is_active():
        window_console.layout.draw()

    if DISPLAY_FPS:
        fps_display.draw()

    pyglet.clock.tick()

# Intialisation
def main():
    create_first_level()

    pyglet.clock.set_fps_limit(FPS_LIMIT)
    pyglet.clock.schedule(update)
    pyglet.app.run()

if __name__ == "__main__":
    if BENCHMARK:
        import hotshot, hotshot.stats
        prof = hotshot.Profile("benchmark.prof")
        prof.runcall(main)
        prof.close()
        stats = hotshot.stats.load("benchmark.prof")
        stats.sort_stats('time', 'calls')
        stats.print_stats(20)
    else:
        main()
