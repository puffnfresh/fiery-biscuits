#!/usr/bin/python
import math
import ode
import pyglet
import data

DEFAULT_DENSITY = 1.0

class PhysicsObject(object):
    def __init__(self, world, space, batch, filename):
        self.world = world
        self.space = space
        self.batch = batch
        self.filename = filename

        self.image = pyglet.image.load(data.filepath(filename))
        self.image.anchor_x = self.image.width / 2
        self.image.anchor_y = self.image.height / 2

        self.sprite = pyglet.sprite.Sprite(self.image, batch=self.batch)

        self.body = ode.Body(self.world)
        self.mass = None
        self.geom = None

        self.joint2d = ode.Plane2DJoint(world)
        self.joint2d.attach(self.body, ode.environment)

        self.update()

    def setDensity(self, density):
        pass

    def getBody(self):
        return self.body

    def getMass(self):
        return self.mass

    def getGeom(self):
        return self.geom

    def getSprite(self):
        return self.sprite

    def update(self):
        quaternion = list(self.body.getQuaternion())
        quaternion[1] = quaternion[2] = 0
        self.body.setQuaternion(quaternion)

        matrix = self.body.getRotation()
        rotation = math.atan2(matrix[4], matrix[3]) * 180/math.pi - 90
        self.sprite.rotation = rotation

class PhysicsBox(PhysicsObject):
    def __init__(self, world, space, batch, filename):
        super(PhysicsBox, self).__init__(world, space, batch, filename)

        self.mass = ode.Mass()
        self.mass.setBox(DEFAULT_DENSITY, self.image.width / 2, self.image.height / 2, 1)
        self.body.setMass(self.mass)

        self.geom = ode.GeomBox(self.space, (self.image.width, self.image.height, 1.0))
        self.geom.setBody(self.body)

class PhysicsCylinder(PhysicsObject):
    def __init__(self, world, space, batch, filename):
        super(PhysicsCylinder, self).__init__(world, space, batch, filename)

        self.mass = ode.Mass()
        self.mass.setCylinder(DEFAULT_DENSITY, 3, self.image.width / 2, 1.0)
        self.body.setMass(self.mass)

        self.geom = ode.GeomCylinder(self.space, self.image.width / 2)
        self.geom.setBody(self.body)
