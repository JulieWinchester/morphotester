'''
Created on Sep 2, 2011

This module calculates relief index for a provided 3D mesh through the
calcrfi() function and supporting functions. Morpho.py calls calcrfi(). 

@author: Julia M. Winchester
'''

from numpy import sqrt,square,log
from numpy.linalg import det
import render

def trianglearea(verts): # Given a triple set of XYZ coordinate points for triangle vertices, returns triangle area
    fx = verts[:,0]
    fy = verts[:,1]
    fz = verts[:,2]
    fc = [1,1,1]
    
    a = [fx, fy, fc]
    b = [fy, fz, fc]
    c = [fz, fx, fc]
    
    return 0.5*sqrt(square(det(a))+square(det(b))+square(det(c)))

def surfarea(mesharray):    
    return sum(trianglearea(face) for face in mesharray[1])

def calcrfi(mesharray):
    print "Generating surface area..."
    surfarea = sum(trianglearea(face) for face in mesharray[1])
    print "Surface area generated"

    print "Measuring outline area..."
    outlinearea = render.meshprojectionarea(mesharray)
    
    print "Outline area measured"

    rfi = surfarea/outlinearea

    return [rfi, log(rfi), surfarea, outlinearea]






