#!/usr/bin/env python

from vec3 import Vec3
import math
    
class Cloth:
    def __init__(self, origin, iSize, jSize, iDivisions, jDivisions, springK, massPerM2, absGravity):
        self.iSize = iSize
        self.jSize = jSize
        self.iDivisions = iDivisions
        self.jDivisions = jDivisions
        self.pointCount = iDivisions*jDivisions
        self.springK = springK
        self.jointMass = massPerM2*iSize*jSize/(iDivisions*jDivisions)
        self.gravity = Vec3(0.0, 0.0, -absGravity)
        
        self.positions = []
        self.velocities = []
        for j in range(0, self.jDivisions):
            for i in range(0, self.iDivisions):
                position = origin + Vec3(-0.5*iSize + i*iSize/(iDivisions - 1), jSize - j*jSize/(jDivisions - 1), jSize)
                self.positions.append(position)
                self.velocities.append(Vec3(0.0, 0.0, 0.0))

        self.lockedJoints = []
        self.offsets = []
        
        # horizontal and vertical springs (structural)
        horizontalRestingDistance = iSize/(iDivisions - 1)
        verticalRestingDistance = jSize/(jDivisions - 1)
        self.offsets.append((-1, 0, horizontalRestingDistance))
        self.offsets.append((1, 0, horizontalRestingDistance))
        self.offsets.append((0, -1, verticalRestingDistance))
        self.offsets.append((0, 1, verticalRestingDistance))

        # horizontal and vertical double springs (folds)
        self.offsets.append((-2, 0, 2.0*horizontalRestingDistance))
        self.offsets.append((2, 0, 2.0*horizontalRestingDistance))
        self.offsets.append((0, -2, 2.0*verticalRestingDistance))
        self.offsets.append((0, 2, 2.0*verticalRestingDistance))
        
        # diagonal springs (shears)
        diagonalRestingDistance = math.sqrt(horizontalRestingDistance*horizontalRestingDistance + verticalRestingDistance*verticalRestingDistance)
        self.offsets.append((-1, -1, diagonalRestingDistance))
        self.offsets.append((-1, 1, diagonalRestingDistance))
        self.offsets.append((1, -1, diagonalRestingDistance))
        self.offsets.append((1, 1, diagonalRestingDistance))

    # Runge-Kutta 4th order
    def update(self, diffTime):
        for id in range(0, self.pointCount):
            (i, j) = self.getIJ(id);
            if self.isJointLocked(i, j):
                continue
            position = self.positions[id]
            velocity = self.velocities[id]
            k1 = velocity
            k2 = velocity + self.computeDeltaVelocity(i, j, position + k1*0.5*diffTime, 0.5*diffTime)
            k3 = velocity + self.computeDeltaVelocity(i, j, position + k2*0.5*diffTime, 0.5*diffTime)
            k4 = velocity + self.computeDeltaVelocity(i, j, position + k3*diffTime, diffTime)
            velocity = (k1 + k2*2.0 + k3*2.0 + k4)*(1.0/6.0)
            position = position + velocity*diffTime
            self.positions[id] = position
            self.velocities[id] = velocity

    def computeDeltaVelocity(self, i, j, position, diffTime):
        forceAccum = Vec3(0.0, 0.0, 0.0)
        for (offsetI, offsetJ, offsetRestingDistance) in self.offsets:
            neighborId = self.getId(i + offsetI, j + offsetJ)
            if neighborId == -1:
                continue
            neighborPosition = self.positions[neighborId]
            toNeighbor = neighborPosition - position
            distance = toNeighbor.normalize()
            forceAccum += toNeighbor*self.springK*(distance - offsetRestingDistance)
        acceleration = forceAccum*(1.0/self.jointMass) + self.gravity
        deltaVelocity = acceleration*diffTime
        return deltaVelocity
            
    def lockJoint(self, i, j):
        self.lockedJoints.append((i, j))

    def isJointLocked(self, i, j):
        for (lockedI, lockedJ) in self.lockedJoints:
            if lockedI == i and lockedJ == j:
                return True
        return False

    def getIJ(self, id):
        i = int(id%self.iDivisions)
        j = int(id/self.iDivisions)
        return (i, j)

    def getId(self, i, j):
        if i < 0 or i >= self.iDivisions:
            return -1
        if j < 0 or j >= self.jDivisions:
            return -1
        return j*self.iDivisions + i

c = Cloth(Vec3(0.0, 0.0, 0.0), 10, 10, 11, 11, 800, 15, 10)
c.update(0.016)
    
