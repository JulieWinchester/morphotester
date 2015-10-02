'''
Created on Feb 1, 2012

This module calculates Dirichlet Normal Energy for a provided 3D mesh (see Bunn
et al. 2011 and Winchester 2015 for further details on method) through 
calcdne() and supporting functions. Morpho.py calls calcdne().

@author: Julia M. Winchester
'''

import implicitfair
import normcore
from numpy import zeros, transpose, nonzero, sqrt, sum, trace, mat, array, dot, isnan, copy
from numpy.linalg import cond
from scipy.sparse import lil_matrix
from scipy.stats import scoreatpercentile
from collections import defaultdict

def vertexfacedict(faces, nvert):  
    vfdict = defaultdict(list)
    
    for findex, face in enumerate(faces):
        for vertex in face:
            vfdict[vertex].append(findex)
        
    return vfdict
        
def edgevertexarray(faces, nvert):
    M = lil_matrix((nvert,nvert))
    
    nedge = 0

    for face in faces:
        v1, v2, v3 = face    
        
        if M[v1,v2] == 0:
            nedge += 1
            M[v1,v2] = nedge
            M[v2,v1] = nedge
            
        if M[v3,v1] == 0:
            nedge += 1
            M[v1,v3] = nedge
            M[v3,v1] = nedge
            
        if M[v2,v3] == 0:
            nedge += 1
            M[v3,v2] = nedge
            M[v2,v3] = nedge
        
    evarray = zeros([nedge,2], int)
    
    nonzeroarray = transpose(nonzero(M))
    
    for entry in nonzeroarray:
        evarray[M[entry[0],entry[1]]-1] = [entry[0],entry[1]]
        
    return evarray 

def boundaryfaces(vfarray, egarray):
    fBoundary = list()
    
    for verts in egarray:
        f1, f2 = [vfarray[vert] for vert in verts]
        cf = [x for x in f2 for y in f1 if x == y]
        
        if len(cf) == 1:
            fBoundary.append(cf[0])
    return fBoundary
 
#def normal(plane): # Returns a 1-dimensional array of XYZ points defining a vector normal to the given plane; expects a list of 3 vertices (consisting of XYZ points) comprising a triangle
#    a = plane[0]
#    b = plane[1]
#    c = plane[2]
#    ab = [(b[0]-a[0]),(b[1]-a[1]),(b[2]-a[2])]
#    ac = [(c[0]-a[0]),(c[1]-a[1]),(c[2]-a[2])]
#    return cross(ab,ac)
#
#def normalmap(vertex,fvarray): # Returns a 2-dimensional array [number-of-faces,3] of normal vectors across a map of triangles. Expects to be provided with an array of faces (in form [face-number,vertex-number,XYZ]). Translation between normal array and face array is: normal[x] = mesh[facenumber]
#    return array([normal(verts) for verts in fvarray])
#
#def normalize(vects):
#    d = sqrt((vects**2).sum(axis=1)) # Square roots of sums of squares of normal vectors, i.e. magnitudes of normal vectors
#    d = [1 if m < spacing(1) else m for m in d]
#    return vects/column_stack((d,d,d)) # each face has its normal vector XYZ divided by that vector's magnitude. this normalizes the vector, i.e. gives it a magnitude of 1.   
#
#def computenormal(varray, faceindex, fvarray, vfarray):
#    nvert = len(varray)
#    
#    fnormal = normalmap(varray,fvarray)
#    
#    # normalize face normals
#    
#    fnormal4 = normalize(fnormal)
#    #d = sqrt((fnormal**2).sum(axis=1)) # Square roots of sums of squares of normal vectors, i.e. magnitudes of normal vectors
#    #d = [1 if m < spacing(1) else m for m in d]
#    #fnormal4 = fnormal/column_stack((d,d,d)) # each face has its normal vector XYZ divided by that vector's magnitude. this normalizes the vector, i.e. gives it a magnitude of 1. 
#    
#    # unit normals of vertices    
#    vnormal = zeros([nvert,3],float)
#    for vindex, faces in vfarray.iteritems():
#        vnormal[vindex] = sum(fnormal4[faces], axis=0)
#        if isnan(fnormal4[faces]).any(): print "nan found during vertex normal creation at vertex #: " + str(vindex)    
#     
#    # normalize vertex normals
#    vnormal4 = normalize(vnormal)
#    
#    #vd = sqrt((vnormal**2).sum(axis=1))   
#    #vd = array([1 if m < spacing(1) else m for m in vd])
#    #vnormal4 = vnormal/column_stack((vd,vd,vd))
#
#    # check for nan values in vnormal4
#    for i, norm in enumerate(vnormal4):
#        if isnan(norm).any():
#            print "nan vnormal 4 entry found"
#            print "corresponding vnormal entry:"
#            print norm
#            print "corresponding d2 entry:"
#            print vd[i]
#    
#    # enforce that normals are outward
#    mvertex = mean(varray,1)    
#    repmvertex = column_stack((mvertex,mvertex,mvertex))            
#    v = varray - repmvertex
#    s = sum((v*vnormal4),0)
#    s2 = 0
#    s3 = 0
#    
#    for i in s:
#        if i > 0:
#            s2 += 1
#        if i < 0:
#            s3 += 1
#    if s2 < s3:
#        print 'Outward normal flipping has occurred'
#        vnormal4 = -vnormal4
#        fnormal4 = -fnormal4
#
#    return [vnormal4, fnormal4]

def energy(face, i, varray, vnormal, conditioncontrolischecked):
    TV1 = array([varray[face[0]],varray[face[1]],varray[face[2]]])
    TV2 = array([vnormal[face[0]],vnormal[face[1]],vnormal[face[2]]])
    
    b1 = TV1[1] - TV1[0]
    b2 = TV1[2] - TV1[0]
    
    g = array(([dot(b1,b1), dot(b1,b2)],[dot(b2,b1), dot(b2,b2)]))
    
    if conditioncontrolischecked == 1:
            if cond(g) > 10**5:
                print "Warning: high matrix condition number at face number " + str(i)
                print "Condition number:  " + str(cond(g))
                return [0,1]
    
    c1 = TV2[1] - TV2[0]
    c2 = TV2[2] - TV2[0]

    fstarh = array(([dot(c1,c1), dot(c1,c2)], [dot(c2,c1), dot(c2,c2)]))

    gm = mat(g) # converts g from an array into a matrix, necessary for inversion and matrix multiplication 
    
    e = trace((gm.I*fstarh)) # multiplying g matrix by fstarh array with "*" results in matrix multiplication 
    facearea = 0.5 * sqrt(g[0,0]*g[1,1]-g[0,1]*g[1,0])
                    
    if isnan(e):
        print "TV2 = "
        print TV2
        print "c1 = " + str(c1)
        print "c2 = " + str(c2)
        print gm.I
        print fstarh
        print e
        
    return [e,facearea]
    
def meshenergy(vertex, faceindex, vnormal, conditioncontrolischecked):    
    energyfarea = array([energy(face,i, vertex, vnormal, conditioncontrolischecked) for i, face in enumerate(faceindex)])
    return [energyfarea[:,0], energyfarea[:,1]] 
    
def totaldne(fBoundary, e, facearea, dooutlierremoval):
    # ignore energy of boundary faces
    e[fBoundary] = 0
    
    # energy density is e(p) * area of polygon        
    edensity = array([x*y for x, y in zip(e, facearea)])
    
    # optional removal of top 0.1% outliers
    if dooutlierremoval == 1:
        ptoneperc = scoreatpercentile(e,99.9)
        for i, energy in enumerate(e):
            if energy > ptoneperc or isnan(energy):
                print "Energy outlier removed. DNE value: " + str(energy) + " Face area: " + str(facearea[i])
                edensity[i] = 0
     
    return sum(edensity)
    

def calcdne(mesh, implicitfairischecked, conditioncontrolischecked, iterationnumber, stepsize, dooutlierremoval):
    varray = mesh[0]
    farray = mesh[2]
    nvert = len(varray)
    
    # optional implicit smooth of mesh
    if implicitfairischecked == 1:
        varray = implicitfair.smooth(copy(varray), farray, int(iterationnumber), float(stepsize))
        if varray == "!":
            return "!"    
    
    # creation of dictionary of vertex keys and face values     
    vfdict = vertexfacedict(farray, nvert)
    # creation of array of vertices per edge
    evarray = edgevertexarray(farray, nvert)
    # list of boundary faces
    fboundary = boundaryfaces(vfdict, evarray)
    # arrays of normalized face normals and vertex normals approximated from adjacent faces
    normals = normcore.computenormal(varray, farray, mesh[1], vfdict)
    # array of e(p) and face area for polygons across mesh
    energyperface = meshenergy(varray, farray, normals[0], conditioncontrolischecked)
    
    # returns e(p) * face area summed over all polygons excepting outliers and boundary faces
    return totaldne(fboundary, energyperface[0], energyperface[1], dooutlierremoval)
   



    
