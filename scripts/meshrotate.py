'''
Created on Jun 25, 2014

@author: Julia M. Winchester

Command line utility for rotating meshes around X/Y/Z axes. It will batch rotate all ascii ply files
in the given directory the supplied number of degrees around the supplied axis. 

Usage: python meshrotate.py <directory> <degrees> <x/y/z> <output addendum>
'''

import plython
import math
import numpy
import os
from sys import argv

dirpath = argv[1]
degrees = argv[2]
axis = argv[3]
addendum = argv[4]

def Check_Zero_Centroid(mesh):
    # Calculates centroid by averaging X Y and Z coordinates
    mesht = numpy.transpose(mesh[0])

    X = numpy.average(mesht[0])
    Y = numpy.average(mesht[1])
    Z = numpy.average(mesht[2])

    centroid = [X,Y,Z]

    # If Centroid isn't at the origin, translates coordinates to origin

    if centroid[0] != 0 or centroid[1] != 0 or centroid[2] != 0:
        mesht[0] = numpy.subtract(mesht[0],centroid[0])
        mesht[1] = numpy.subtract(mesht[1],centroid[1])
        mesht[2] = numpy.subtract(mesht[2],centroid[2])

    # Retransposes mesh to achieve original dimensions
    mesh[0] = numpy.transpose(mesht)
    
    return mesh
    
def RotateMesh(mesh, theta, axis):
    # z rotation matrix using theta supplied in radians
    xrotmat = numpy.matrix([[1,0,0],[0,math.cos(theta),-1*math.sin(theta)],[0,math.sin(theta),math.cos(theta)]])
    yrotmat = numpy.matrix([[math.cos(theta), 0, math.sin(theta)],[0,1,0],[-1*math.sin(theta),0,math.cos(theta)]])
    zrotmat = numpy.matrix([[math.cos(theta),(-1*math.sin(theta)),0],[math.sin(theta),math.cos(theta),0],[0,0,1]])
    specialrotmat = numpy.matrix([[0.98675376,-0.1486028,0.06507106],[-0.15098283,-0.9879753,0.03330231],[-0.05933978,0.0426858,0.99732478]])
    
    meshm = numpy.mat(mesh[0])
    
    if axis == "z":
        rotmat = zrotmat
    if axis == "y":
        rotmat = yrotmat
    if axis == "x":
        rotmat = xrotmat
    if axis == "special":
        rotmat = specialrotmat
    
    # using matrix multiplication, multiplies xyz triplets by rotation matrix to rotate entire xyz point cloud
    for i in range(len(mesh[0])):
        XYZ = numpy.transpose(meshm[i]) 
        XYZprime = rotmat * XYZ
        meshm[i] = numpy.transpose(XYZprime)
    
    mesh[0] = numpy.asarray(meshm)
    
    return mesh

def Main():
    dirpath = argv[1]
    degrees = argv[2]
    axis = argv[3]
    addendum = argv[4]

    radians = math.radians(float(degrees))

    for filename in os.listdir(dirpath):
        if filename[-3:] == "ply":
            mesh = plython.CreateArray(os.path.join(dirpath,filename))
            mesh = Check_Zero_Centroid(mesh)
            mesh = RotateMesh(mesh,radians,axis)
            newfilename = filename[:-4] + addendum + ".ply"
            plython.SaveArray(mesh[0],mesh[2],os.path.join(dirpath,newfilename))
        else:
            print str(filename)+" is not a .ply file. Continuing to next file in directory."
            
if __name__ == "__main__":
    Main()   
    
