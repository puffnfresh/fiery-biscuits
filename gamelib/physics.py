import math
import ode
import pyglet
import data

DEFAULT_DENSITY = 0.0001

class StaticObject(object):
    def __init__(self, space, filename, batch=None):
        self.space = space
        self.batch = batch
        self.filename = filename

        self.image = pyglet.image.load(data.filepath(filename))
        self.image.anchor_x = self.image.width / 2
        self.image.anchor_y = self.image.height / 2

        self.sprite = pyglet.sprite.Sprite(self.image, batch=self.batch)

        self.geom = None

    def getImage(self):
        return self.image

    def getGeom(self):
        return self.geom

    def getSprite(self):
        return self.sprite

    def getPosition(self):
        return self.geom.getPosition()

    def setPosition(self, position):
        self.geom.setPosition(position)
        #self.geom.setPosition((position[0] + self.image.width / 2, position[1] + self.image.height / 2, 0))

    def setRotation(self, degrees):
        matrix = self.geom.getRotation()
        matrix[0] = matrix[4] = math.cos(degrees*math.pi/180)
        matrix[3] = math.sin(degrees*math.pi/180)
        matrix[1] = -matrix[3]
        self.geom.setRotation(matrix)

    def remove(self):
        self.space.remove(self.geom)

    def update(self):
        matrix = self.geom.getRotation()
        rotation = math.atan2(matrix[4], matrix[3]) * 180/math.pi - 90
        self.sprite.rotation = rotation

class StaticBox(StaticObject):
    def __init__(self, space, filename, batch=None):
        super(StaticBox, self).__init__(space, filename, batch)
        self.geom = ode.GeomBox(self.space, (self.image.width, self.image.height, 1.0))

class StaticCylinder(StaticObject):
    def __init__(self, space, filename, batch=None):
        super(StaticCylinder, self).__init__(space, filename, batch)
        self.geom = ode.GeomCylinder(self.space, self.image.width / 2)

class PhysicsObject(StaticObject):
    def __init__(self, world, space, filename, batch=None):
        super(PhysicsObject, self).__init__(space, filename, batch)
        self.world = world

        self.body = ode.Body(self.world)
        self.mass = None

        self.joint2d = ode.Plane2DJoint(world)
        self.joint2d.attach(self.body, ode.environment)

        self.update()

    def getBody(self):
        return self.body

    def getMass(self):
        return self.mass

    def getPosition(self):
        return self.body.getPosition()

    def setPosition(self, position):
        return self.body.setPosition(position)

    def setRotation(self, degrees):
        matrix = self.body.getRotation()
        matrix[0] = matrix[4] = math.cos(degrees)
        matrix[3] = math.sin(degrees)
        matrix[1] = -matrix[3]
        self.body.setRotation(matrix)

    def update(self):
        quaternion = list(self.body.getQuaternion())
        quaternion[1] = quaternion[2] = 0
        self.body.setQuaternion(quaternion)

        matrix = self.body.getRotation()
        rotation = math.atan2(matrix[4], matrix[3]) * 180/math.pi - 90
        self.sprite.rotation = rotation

class PhysicsBox(PhysicsObject):
    def __init__(self, world, space, filename, batch=None):
        super(PhysicsBox, self).__init__(world, space, filename, batch)

        self.mass = ode.Mass()
        self.mass.setBox(DEFAULT_DENSITY, self.image.width / 2, self.image.height / 2, 1)
        self.body.setMass(self.mass)

        self.geom = ode.GeomBox(self.space, (self.image.width, self.image.height, 1.0))
        self.geom.setBody(self.body)

class PhysicsCylinder(PhysicsObject):
    def __init__(self, world, space, filename, batch=None):
        super(PhysicsCylinder, self).__init__(world, space, filename, batch)

        self.mass = ode.Mass()
        self.mass.setCylinder(DEFAULT_DENSITY, 3, self.image.width / 2, 1.0)
        self.body.setMass(self.mass)

        self.geom = ode.GeomCylinder(self.space, self.image.width / 2)
        self.geom.setBody(self.body)
