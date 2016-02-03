'''
Created on Feb 1, 2012

This module calculates Dirichlet Normal Energy for a provided 3D mesh using
the MeshDNE class. See Bunn et al. 2011 and Winchester (in review) for 
further details on method.

@author: Julia M. Winchester
'''

import implicitfair
import normcore
from copy import copy as pcopy
from numpy import zeros, transpose, nonzero, sqrt, sum, trace, mat, array, dot, isnan, copy, array_equal
from numpy.linalg import cond, LinAlgError
from scipy.sparse import lil_matrix
from scipy.stats import scoreatpercentile
from collections import defaultdict

class MeshDNE(object):
    """Class for calculating and storing Dirichlet normal energy values for polygonal mesh data. 
    
    When instanced, this class calculates Dirichlet normal energy and associated variables
    and stores them. All attributes listed below are populated on instantiation.
    
    Args:
        TopoMesh (TopoMesh object): Triangulated polygon mesh data. 
        dosmooth (bool): Whether or not mesh should be smoothed prior to DNE 
            calculation. 
        smoothit (int): Number of iterations for smoothing. 
        smoothstep (float): Step size for smoothing
        docondition (bool): Whether or not to perform matrix condition number 
            checking as part of DNE calculation. 
        dooutlier (bool): Whether or not to perform outlier removal as part of 
            DNE calculation.
        outlierperc (float): Percentile above which to remove energy outliers. 
        outliertype (bool): Whether to remove outliers as energy*face values 
            (true) or energy values (false).
    
    Attributes:
        Mesh (TopoMesh object): Triangulated polygon mesh data. 
        vert_tri_dict (dict): Associates vertex index keys with related
            face index values. 
        edgeverts (ndarray): Pairs of vertices that form surface boundary edges.
        fnormal (ndarray): Normalized unit normals of surface polygons. 
        vnormal (ndarray): Normalized approximated unit normals of surface
            vertices (approximated as average of normals of associated faces).
        e (ndarray): Energy density values of surface polygons. 
        facearea (ndarray): Surface polygon areas. 
        equantity (ndarray): e * facearea for surface polygons. 
        DNE (float): Summation of equantity. 
        high_condition_faces (list): Surface polygons with high matrix condition 
            numbers. If condition number check is on, these are not counted 
            toward DNE. 
        outlier_faces (list): Surfaces with outlier energy values. If outlier 
            removal is on, these are not counted toward DNE. 
        boundary_faces (list): Polygons forming mesh edges. Not counted toward
            DNE.
        nan_faces (list): Any polygons resulting in NAN e values.    
    """
    def __init__(self, TopoMesh, dosmooth, smoothit, smoothstep, docondition, dooutlier, outlierperc, outliertype):
        self.Mesh = TopoMesh
        self.dosmooth = dosmooth
        self.smoothit = smoothit
        self.smoothstep = smoothstep
        self.docondition = docondition
        self.dooutlier = dooutlier
        self.outlierperc = float(outlierperc)
        self.outliertype = outliertype
        
        self.vert_tri_dict = None
        self.edgeverts = None
        self.fnormal = None
        self.vnormal = None
        self.e = None
        self.facearea = None
        self.equantity = None
        self.DNE = None
        
        self.high_condition_faces = list()
        self.outlier_faces = list()
        self.boundary_faces = list()
        self.nan_faces = list()
        
        self.calcdne()
        
    def calcdne(self):
        """Method for calculating surface Dirichlet normal energy and populating instance variables."""
        # creation of dictionary of vertex keys and face values     
        self._get_vert_tri_dict()
        
        # optional implicit smooth of mesh
        if self.dosmooth == 1:
            self.Mesh = pcopy(self.Mesh)
            self.Mesh.vertices = implicitfair.smooth(self.Mesh.vertices, self.Mesh.faces, int(self.smoothit), float(self.smoothstep), self.vert_tri_dict)
            if self.Mesh.vertices == "!":
                return "!"    
        
        # creation of array of vertices per edge
        self._get_edge_verts()
        # list of boundary faces
        self._get_boundary_faces()
        
        # arrays of normalized face normals and vertex normals approximated from adjacent faces
        self.vnormal, self.fnormal = normcore.computenormal(self.Mesh.vertices, self.Mesh.faces, self.Mesh.triverts, self.vert_tri_dict)
        # array of e(p) and face area for polygons across mesh
        
        self._energize_surface()
        
        self._sumdne()

    def _energize_surface(self):
        """Calculates energy values and polygon areas across a surface."""    
        energy_and_facearea = array([self._energy(face, i) for i, face in enumerate(self.Mesh.faces)])
        self.e = energy_and_facearea[:,0]
        self.facearea = energy_and_facearea[:,1]

    def _energy(self, face, i):
        """Returns energy value and polygon area for a provided polygon."""
       
        TV1 = array([self.Mesh.vertices[face[0]], self.Mesh.vertices[face[1]], self.Mesh.vertices[face[2]]])
        TV2 = array([self.vnormal[face[0]],self.vnormal[face[1]],self.vnormal[face[2]]])
        
        if array_equal(TV1[0], TV1[1]) or array_equal(TV1[0], TV1[2]) or array_equal(TV1[1], TV1[2]):
            print "Warning: Duplicate vertices in polygon %s." % i
            print "Ignoring this polygon for energy calculation, but editing surface to remove duplicate vertices prior to DNE calculation is encouraged."
            return [0,1]

        b1 = TV1[1] - TV1[0]
        b2 = TV1[2] - TV1[0]
        
        g = array(([dot(b1,b1), dot(b1,b2)],[dot(b2,b1), dot(b2,b2)]))
        
        if self.docondition:
                if cond(g) > 10**5:
                    self.high_condition_faces.append([i, cond(g)])
                    return [0,1]
        
        c1 = TV2[1] - TV2[0]
        c2 = TV2[2] - TV2[0]
    
        fstarh = array(([dot(c1,c1), dot(c1,c2)], [dot(c2,c1), dot(c2,c2)]))
    
        gm = mat(g)  
        
        try:
            gminv = gm.I
        except LinAlgError as err:
            condition = cond(g)
            if condition > 10**5:
                err.args += ('G matrix for polygon %s is singular and an inverse cannot be determined. Condition number is %s, turning condition number checking on will cause this polygon to be ignored for energy calculation.' % (i, cond(g)),)
                raise
            else:
                err.args += ('G matrix for polygon %s is singular and an inverse cannot be determined. Condition number is %s, turning condition number checking on will not cause this polygon to be ignored for energy calculation. Further mesh processing is advised.' % (i, cond(g)),)
                raise
        
        e = trace((gminv*fstarh))
        facearea = 0.5 * sqrt(g[0,0]*g[1,1]-g[0,1]*g[1,0])
                        
        if isnan(e):
            self.nan_faces.append(i)
            
        return [e,facearea]
    
    def _sumdne(self):
        """Sums energy values * face areas, ignoring certain kinds of polygons depending on parameters."""
        # ignore energy of boundary faces
        self.e[self.boundary_faces] = 0
        
        # energy density is e(p) * area of polygon        
        self.equantity = array([x*y for x, y in zip(self.e, self.facearea)])
        
        # optional removal of top outliers, percentile for outliers is user settable
        if self.dooutlier: 
            self._outlierremove()
                                 
        self.DNE = round(sum(self.equantity),3)
    
    def _outlierremove(self):
        """Flags outlier faces based on parameters and removes associated energy values."""
        switcharoo = [self.e, self.equantity]
        percentile = scoreatpercentile(switcharoo[self.outliertype], self.outlierperc)
        for i, energy in enumerate(switcharoo[self.outliertype]):
            if energy > percentile or isnan(energy):
                self.outlier_faces.append([i, energy, self.facearea[i]])
                self.equantity[i] = 0

    def _get_vert_tri_dict(self):
        """Generates dictionary associating vertex index keys with related polygon index values.""" 
        self.vert_tri_dict = defaultdict(list)
        
        for findex, face in enumerate(self.Mesh.faces):
            for vertex in face:
                self.vert_tri_dict[vertex].append(findex)
                        
    def _get_edge_verts(self):
        """Generates pairs of vertices comprising surface edges."""
        M = lil_matrix((self.Mesh.nvert,self.Mesh.nvert))
        
        nedge = 0
    
        for face in self.Mesh.faces:
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
            
        self.edgeverts = zeros([nedge,2], int)
        
        nonzeroarray = transpose(nonzero(M))
        
        for entry in nonzeroarray:
            self.edgeverts[M[entry[0],entry[1]]-1] = [entry[0],entry[1]]
    
    def _get_boundary_faces(self):
        """Generates list of polygons comprising surface edges."""        
        self.boundary_faces = list()
        
        for verts in self.edgeverts:
            f1, f2 = [self.vert_tri_dict[vert] for vert in verts]
            cf = [x for x in f2 for y in f1 if x == y]
            
            if len(cf) == 1:
                self.boundary_faces.append(cf[0])
            
        self.boundary_faces = list(set(self.boundary_faces))
    