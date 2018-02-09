#!/usr/bin/env python

from panda3d.core import GeomVertexFormat
from panda3d.core import Geom, GeomNode, GeomTriangles
from panda3d.core import GeomVertexReader, GeomVertexWriter
from panda3d.core import GeomVertexRewriter, GeomVertexData
from panda3d.core import NodePath
from panda3d.core import LVector3
from direct.task.Task import Task
from cloth import Cloth
from vec3 import Vec3
import math

class ClothGeometry:
    def __init__(self, cloth, name):
        self.cloth = cloth
        clothTexture = loader.loadTexture('tex/1.png')
        nodePath = NodePath(name + ' Holder')
        nodePath.setTexture(clothTexture, 1)
        nodePath.reparentTo(render)

        self.vertexData = GeomVertexData(name + ' Buffer', GeomVertexFormat.getV3n3t2(), Geom.UHDynamic)
        self.vertexData.setNumRows(cloth.pointCount)

        vertex = GeomVertexWriter(self.vertexData, 'vertex')
        normal = GeomVertexWriter(self.vertexData, 'normal')
        texcoord = GeomVertexWriter(self.vertexData, 'texcoord')

        for id in range(0, cloth.pointCount):
            position = cloth.positions[id]
            vertex.addData3f(position.x, position.y, position.z)
            normal.addData3f(0.0, 0.0, 1.0)
            texcoord.addData2f(2.0*(-0.5 + position.x/cloth.iSize), 2.0*(position.y/cloth.jSize))

        mesh = GeomTriangles(Geom.UHStatic)
        for j in range(0, cloth.jDivisions - 1):
            for i in range(0, cloth.iDivisions - 1):
                id0 = i + j*cloth.iDivisions
                id1 = id0 + 1
                id2 = i + (j + 1)*cloth.iDivisions
                id3 = id2 + 1
                mesh.addVertices(id0, id2, id1)
                mesh.addVertices(id0, id1, id2)
                mesh.addVertices(id1, id2, id3)
                mesh.addVertices(id1, id3, id2)
        mesh.closePrimitive()

        geometry = Geom(self.vertexData)
        geometry.addPrimitive(mesh)
        node = GeomNode(name)
        node.addGeom(geometry)
        nodePath.attachNewNode(node)

        self.oldTime = 0.0
        taskMgr.add(self.update, 'Update ' + name)

    def updatePositions(self):
        vertex = GeomVertexWriter(self.vertexData, 'vertex')
        for id in range(0, self.cloth.pointCount):
            position = self.cloth.positions[id]
            vertex.setData3f(position.x, position.y, position.z)
    
    def updateNormals(self):
        normalBuff = GeomVertexWriter(self.vertexData, 'normal')
        for j in range(0, self.cloth.jDivisions):
            for i in range(0, self.cloth.iDivisions):
                id = self.cloth.getId(i, j)
                hMinusId = self.cloth.getId(i - 1, j)
                hMinusId = hMinusId if hMinusId != -1 else id
                hMinusPos = self.cloth.positions[hMinusId]
                
                hPlusId = self.cloth.getId(i + 1, j)
                hPlusId = hPlusId if hPlusId != -1 else id
                hPlusPos = self.cloth.positions[hPlusId]
                
                vMinusId = self.cloth.getId(i, j - 1)
                vMinusId = vMinusId if vMinusId != -1 else id
                vMinusPos = self.cloth.positions[vMinusId]
                
                vPlusId = self.cloth.getId(i, j + 1)
                vPlusId = vPlusId if vPlusId != -1 else id
                vPlusPos = self.cloth.positions[vPlusId]

                hDiff = hPlusPos - hMinusPos
                vDiff = vPlusPos - vMinusPos
                normal = vDiff.cross(hDiff)
                normal.normalize()
                normalBuff.setData3f(normal.x, normal.y, normal.z)                
    
    def update(self, task):
        diffTime = task.time - self.oldTime
        self.oldTime = task.time
        
        diffTime = min(diffTime, 1.0/20.0)
        self.cloth.update(diffTime)
        
        self.updatePositions()
        self.updateNormals()
        return Task.cont
