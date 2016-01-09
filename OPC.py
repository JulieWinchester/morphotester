'''
Created on Sep 2, 2011

This module calculates Orientation Patch Count Rotated for a provided 3D mesh
through MeshOPCR class. See Evans et al. 2007 and Winchester (in review) for
details on method.  

@author: Julia M. Winchester
'''

from copy import copy as pcopy
from numpy import array, matrix, mat, transpose, average, subtract, row_stack
from numpy import mean as amean
from collections import defaultdict

import math
import normcore

class MeshOPCR(object):
    """Class for calculating and storing Orientation patch count rotated values for polygonal mesh data. 
    
    When instanced, this class calculates OPCR and associated variables
    and stores them. All attributes listed below are populated on instantiation.
    
    Args:
        TopoMesh (TopoMesh object): Triangulated polygon mesh data. 
        minpatch (int): Minimum size in polygons for patches to be counted. 
    
    Attributes:
        Mesh (TopoMesh object): Triangulated polygon mesh data. 
        theta (float): Radians of OPC rotations for OPCR calculation. 
        n_rotations (int, 8): Number of OPC rotations for OPCR calculation.
        opc_list (list): List of OPC at each of 8 rotations. The average
            of these values is OPCR. 
        patches_list (list): List of lists. Contains 8 lists (one per
            rotation), each of which lists all counted surface patches for 
            that rotation.
        colormap_list (list): List of lists. Contains 8 lists (one per
            rotation), each of which lists polygons sorted into colors
            based on XY aspect (direction that polygon faces) for that
            rotation. 
        vert_tri_dict (dict): Associates vertex index keys with related
            face index values. 
        fnormal (ndarray): Normalized unit normals of surface polygons. 
        vnormal (ndarray): Normalized approximated unit normals of surface
            vertices (approximated as average of normals of associated faces).
        OPCR (float): Orientation patch count rotated. Average of opc_list.     
    """
    def __init__(self, TopoMesh, minpatch):
        self.Mesh = TopoMesh
        self.MeshRotated = None
        self.min_patch_size = int(minpatch)
        self.theta = math.radians(5.625)
        self.n_rotations = 8
        self.opc_list = [None, None, None, None, None, None, None, None]
        self.patches_list = [None, None, None, None, None, None, None, None]
        self.colormap_list = [None, None, None, None, None, None, None, None]
        self.vert_tri_dict = None
        self.fnormal = None
        self.vnormal = None
        self.OPCR = None
        
        self.calcopcr()
               
    def calcopcr(self):
        """Method for calculating OPCR and associated variables from surface mesh. Calls internal methods."""
        self.Mesh = pcopy(self.Mesh)
        self.Mesh.vertices = self._centermesh(self.Mesh.vertices)
        self.MeshRotated = pcopy(self.Mesh)
        
        self._get_vert_tri_dict()
        
        self.opc_list[0], self.patches_list[0], self.colormap_list[0] = self._get_opc(self.Mesh.vertices, 
                                                                                      self.Mesh.faces, 
                                                                                      self.Mesh.triverts)
        
        for i in range(1,self.n_rotations):
                self._rotatemesh()
                self.opc_list[i], self.patches_list[i], self.colormap_list[i] = self._get_opc(self.MeshRotated.vertices, 
                                                                                              self.MeshRotated.faces, 
                                                                                              self.MeshRotated.triverts)
        
        self.OPCR = average(self.opc_list)
        
    def _get_opc(self, vertices, faces, triverts):
        """Calculates and returns OPC, list of patches, and list of polygons sorted into color bins by XY aspect."""
        self.vnormal, self.fnormal = normcore.computenormal(vertices, faces, triverts, self.vert_tri_dict)
        
        flatfaces = array([i for i, norm in enumerate(self.fnormal) if (norm[0:1] == 0).all()], dtype=int)
        orientation_map = array([self._xydegrees(norm[1],norm[0]) for norm in self.fnormal])
    
        color_map = array([self._sort_to_colors(aspect_theta) for aspect_theta in orientation_map])
        color_map[flatfaces] = '#000000'
            
        pairdict = defaultdict(list) #lists per vertex all possible pairs of polygons that include that vertex 
        for vertex, faces in self.vert_tri_dict.iteritems():
            pairdict[vertex] = self._pair_faces(faces)
            
        adjacent_face_pairs = self._adjacent_face_pairs(pairdict)    
        
        same_color_pairs = [pair for pair in adjacent_face_pairs if color_map[pair[0]] == color_map[pair[1]]]
        
        color_face_dict = defaultdict(list) # lists adjacent polygon pairs for each color bin
        for item in same_color_pairs:
            color_face_dict[color_map[item[0]]].append(item)
         
        colorlist = ['#FF0000','#964B00','#FFFF00','#00FFFF','#0000FF','#90EE90','#014421','#FFC0CB']
            
        patches = [self._build_patches(color_face_dict[color]) for color in colorlist]

        patches = [self._cull_small_patches(subpat,self.min_patch_size) for subpat in patches]
        
        opc = sum([len(subpat) for subpat in patches])
           
        return [opc, patches, color_map]               

    def _centermesh(self, vert_sequence):
        """Translates mesh centroid to XYZ coordinate origin."""
        centroid = amean(vert_sequence, axis=0)
        return array([subtract(vert,centroid) for vert in vert_sequence])

    def _get_vert_tri_dict(self):
        """Generates dictionary associating vertex index keys with related polygon index values.""" 
        self.vert_tri_dict = defaultdict(list)
        
        for findex, face in enumerate(self.Mesh.faces):
            for vertex in face:
                self.vert_tri_dict[vertex].append(findex)        

    def _rotatemesh(self):
        """Rotates mesh theta radians around Z-axis."""
        zrotmat = matrix([[math.cos(self.theta),(-1*math.sin(self.theta)),0],[math.sin(self.theta),math.cos(self.theta),0],[0,0,1]])
        
        vert_matrix = mat(self.MeshRotated.vertices)
        rotated_verts = row_stack([transpose(zrotmat * transpose(vert)) for vert in vert_matrix])
        self.MeshRotated.vertices = array(rotated_verts)

    def _xydegrees(self, y, x):
        """Given a vector (x,y) returns angle of vector from the positive X-axis."""
        vectangle = math.degrees(math.atan2(y,x))
        if vectangle < 0:
            return vectangle+360
        else:
            return vectangle
        
    def _sort_to_colors(self, aspect_theta):
        """Given a polygon XY aspect angle, returns the appropriate bin for color sorting."""
        colorlist = ['#FF0000','#964B00','#FFFF00','#00FFFF','#0000FF','#90EE90','#014421','#FFC0CB']
        modtheta = (aspect_theta + 22.5) % 360
        group = int(modtheta//45)
        return colorlist[group]
    
    def _pair_faces(self, inputlist):
        """Given a list of numbers, returns all possible pairs of numbers without replication or identical-number pairs."""
        return [(x,y) for x in set(inputlist) for y in set(inputlist) if x < y]
    
    def _adjacent_face_pairs(self, pairdict):
        """Given a list of polygon face pairs sharing vertices, returns the subset of polygon pairs where pair members share an edge.""" 
        touching_list = list() 
        seen = set() 
        seentwice = set()
        for item in pairdict:
            for pair in pairdict[item]:
                if pair in seen:
                    touching_list.append(pair)
                    if pair in seentwice:
                        print "WARNING: POSSIBLE IDENTICAL TRIANGLES AT ", pair
                    else:
                        seentwice.add(pair)
                else:
                    seen.add(pair)
        return touching_list    

    def _build_patches(self, face_pairs): 
        """Given a list of adjacent pairs of polygons on a surface, returns list of all contiguous patches of polygons involving provided pairs."""
        patcheslist = list()
        for pair in face_pairs:
            wassorted = list()
            for i, clumppatch in enumerate(patcheslist):
                if pair[0] in clumppatch or pair[1] in clumppatch:
                    clumppatch.add(pair[0])
                    clumppatch.add(pair[1])
                    wassorted.append(i)
                    continue
            
            if len(wassorted) == 0:
                patcheslist.append(set([pair[0],pair[1]]))
            
            if len(wassorted) > 1:
                tempset = set()
                for sortpair in wassorted:
                    tempset = tempset | patcheslist[sortpair]
                patcheslist[wassorted[0]] = tempset
                for i in wassorted[1:]:
                    del patcheslist[i]
        
        return patcheslist
    
    def _cull_small_patches(self, patches, minsize):
        """Given a list of patches, returns only patches with numbers of polygons equal to or greater than minsize."""
        return [patch for patch in patches if len(patch) >= minsize]
    