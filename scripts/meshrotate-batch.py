'''
Created on Apr 16, 2015

@author: Julia M. Winchester

Command line utility for creating a "population" of meshes rotated in the X and Y directions independently and combined 
in steps of 2 from 0 to 30 (0 degrees, 2, 4, ..., 30) to create a matrix of 225 meshes of various rotations to check
against topography. 
'''

import plython
import numpy
import math

def Check_Zero_Centroid(cmesh):
    # Calculates centroid by averaging X Y and Z coordinates
    mesht = numpy.transpose(cmesh[0])

    Xc = numpy.average(mesht[0])
    Yc = numpy.average(mesht[1])
    Zc = numpy.average(mesht[2])

    centroid = [Xc,Yc,Zc]

    # If Centroid isn't at the origin, translates coordinates to origin

    if centroid[0] != 0 or centroid[1] != 0 or centroid[2] != 0:
        mesht[0] = numpy.subtract(mesht[0],centroid[0])
        mesht[1] = numpy.subtract(mesht[1],centroid[1])
        mesht[2] = numpy.subtract(mesht[2],centroid[2])

    # Retransposes mesh to achieve original dimensions
    cmesh[0] = numpy.transpose(mesht)
    
    return cmesh

def RotateMesh(rmesh, theta, axis):
    # z rotation matrix using theta supplied in radians
    xrotmat = numpy.matrix([[1,0,0],[0,math.cos(theta),-1*math.sin(theta)],[0,math.sin(theta),math.cos(theta)]])
    yrotmat = numpy.matrix([[math.cos(theta), 0, math.sin(theta)],[0,1,0],[-1*math.sin(theta),0,math.cos(theta)]])
    zrotmat = numpy.matrix([[math.cos(theta),(-1*math.sin(theta)),0],[math.sin(theta),math.cos(theta),0],[0,0,1]])
    
    meshm = numpy.mat(rmesh[0])
    
    if axis == "z":
        rotmat = zrotmat
    if axis == "y":
        rotmat = yrotmat
    if axis == "x":
        rotmat = xrotmat
    
    # using matrix multiplication, multiplies xyz triplets by rotation matrix to rotate entire xyz point cloud
    for i in range(len(rmesh[0])):
        XYZ = numpy.transpose(meshm[i]) 
        XYZprime = rotmat * XYZ
        meshm[i] = numpy.transpose(XYZprime)
    
    rmesh[0] = numpy.asarray(meshm)
    
    return rmesh

# This is an example filename, should be replaced with desired file
filename = "/Users/Username/mesh.ply"

stepsx = [0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30]

stepsy = [0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30]

for x in stepsx:
    for y in stepsy:
        mesh = plython.CreateArray(filename)
        mesh2 = Check_Zero_Centroid(mesh)
        
        newmesh = RotateMesh(mesh2, math.radians(float(x)), "x")
        newmesh2 = Check_Zero_Centroid(newmesh)
        newmesh3 = RotateMesh(newmesh2, math.radians(float(y)), "y")
        newmesh4 = Check_Zero_Centroid(newmesh3)
        plython.SaveArray(newmesh4[0],newmesh4[2],"/Users/Username/mesh-rotx" +str(x)+"-roty" + str(y) + ".ply")
        newmesh = 0
        newmesh2 = 0
        newmesh3 = 0
        newmesh4 = 0
        mesh = 0
        mesh2 = 0


        
