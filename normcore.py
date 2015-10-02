'''
Created on Oct 1, 2015

Functions for the creation and manipulation of normal vectors.

@author: Julia M. Winchester
'''

from numpy import cross, array, sqrt, column_stack, spacing, zeros, isnan, mean, sum

def normal(plane): # Returns a 1-dimensional array of XYZ points defining a vector normal to the given plane; expects a list of 3 vertices (consisting of XYZ points) comprising a triangle
    a = plane[0]
    b = plane[1]
    c = plane[2]
    ab = [(b[0]-a[0]),(b[1]-a[1]),(b[2]-a[2])]
    ac = [(c[0]-a[0]),(c[1]-a[1]),(c[2]-a[2])]
    return cross(ab,ac)

def normalmap(varray,farray): # Returns a 2-dimensional array [number-of-faces,3] of normal vectors across a map of triangles. Expects to be provided with an array of faces (in form [face-number,vertex-number,XYZ]). Translation between normal array and face array is: normal[x] = mesh[facenumber]
    return array([normal(varray[verts]) for verts in farray])

def normalize(vects):
    d = sqrt((vects**2).sum(axis=1)) # Square roots of sums of squares of normal vectors, i.e. magnitudes of normal vectors
    d = [1 if m < spacing(1) else m for m in d]
    return vects/column_stack((d,d,d)) # each face has its normal vector XYZ divided by that vector's magnitude. this normalizes the vector, i.e. gives it a magnitude of 1.   

def computenormal(varray, faceindex, fvarray, vfarray):
    nvert = len(varray)
    
    fnormal = normalmap(varray,faceindex)
    # normalize face normals
    fnormal4 = normalize(fnormal)
    
    # unit normals of vertices    
    vnormal = zeros([nvert,3],float)
    for vindex, faces in vfarray.iteritems():
        vnormal[vindex] = sum(fnormal4[faces], axis=0)
        if isnan(fnormal4[faces]).any(): print "nan found during vertex normal creation at vertex #: " + str(vindex)    
     
    # normalize vertex normals
    vnormal4 = normalize(vnormal)
    
    # check for nan values in vnormal4
    for i, norm in enumerate(vnormal4):
        if isnan(norm).any():
            print "nan vnormal 4 entry found"
            print "corresponding vnormal entry:"
            print norm
    
    # enforce that normals are outward
    mvertex = mean(varray,1)    
    repmvertex = column_stack((mvertex,mvertex,mvertex))            
    v = varray - repmvertex
    s = sum((v*vnormal4),0)
    s2 = 0
    s3 = 0
    
    for i in s:
        if i > 0:
            s2 += 1
        if i < 0:
            s3 += 1
    if s2 < s3:
        print 'Outward normal flipping has occurred'
        vnormal4 = -vnormal4
        fnormal4 = -fnormal4

    return [vnormal4, fnormal4]