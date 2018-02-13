#!/usr/bin/env python

from direct.showbase.ShowBase import ShowBase
from panda3d.core import PerspectiveLens
from panda3d.core import Light, AmbientLight, Spotlight
from panda3d.core import NodePath
from panda3d.core import LVector3
from direct.task.Task import Task
from cloth import Cloth
from cloth_geometry import ClothGeometry
from vec3 import Vec3
import math
import time
import sys
import os

base = ShowBase()
base.disableMouse()
base.camera.setPos(-40, -70, 15)
base.camera.lookAt(20, 0, -5)

alight = AmbientLight('alight')
alight.setColor((0.5, 0.5, 0.5, 1))
alnp = render.attachNewNode(alight)
render.setLight(alnp)

slight = Spotlight('slight')
slight.setColor((1, 1, 1, 1))
lens = PerspectiveLens()
slight.setLens(lens)
slnp = render.attachNewNode(slight)
render.setLight(slnp)
slnp.setPos(150, -80, 50)
slnp.lookAt(0, 0, 0)

#Cloth data
iSize = 10
jSize = 10
iDivisions = 11
jDivisions = 11
springK = 800
massPerM2 = 15
gravity = 10

cloth1 = Cloth(Vec3(0.0, -40.0, 0.0), iSize, jSize, iDivisions, jDivisions, springK, massPerM2, gravity)
cloth1.lockJoint(0, 0)
cloth1.lockJoint(iDivisions - 1, 0)
clothGeometry1 = ClothGeometry(cloth1, 'Cloth1')

cloth2 = Cloth(Vec3(0.0, -20.0, 0.0), iSize, jSize, iDivisions, jDivisions, springK, massPerM2, gravity)
cloth2.lockJoint(0, 0)
cloth2.lockJoint((iDivisions - 1)/2, 0)
cloth2.lockJoint(iDivisions - 1, 0)
clothGeometry2 = ClothGeometry(cloth2, 'Cloth2')

cloth3 = Cloth(Vec3(0.0, 0.0, 0.0), iSize, jSize, iDivisions, jDivisions, springK, massPerM2, gravity)
for i in range(0, iDivisions):
    cloth3.lockJoint(i, 0)    
clothGeometry3 = ClothGeometry(cloth3, 'Cloth3')

base.run()
