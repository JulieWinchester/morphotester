'''
Created on Sep 2, 2011

This module calculates Orientation Patch Count Rotated for a provided 3D mesh 
(see Evans et al. 2007 and Winchester 2015 for further details on method) 
through calcopcr() and supporting functions. Morpho.py calls calcopcr().

@author: Julia M. Winchester
'''

from numpy import array, zeros, matrix, mat, transpose, asarray, average, subtract, row_stack, arange
from numpy import copy as numcopy
import math

import normcore
import DNE
import collections

def combpairs(inputlist):
    return [(x,y) for x in inputlist for y in inputlist if x < y]

def removesmallpatches(patches, minlengthallowed):
    return [patch for patch in patches if len(patch) >= minlengthallowed]
    
def chunkpatches(colorpairs): # the following functions create colorpatches lists that sequentially list discrete similarly-oriented patches. each patch is listed as a sub-list of all face index numbers included in that patch.
    patcheslist = list()
    for pair in colorpairs:
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

def addpatchestoinfoarray(patches): # Currently unused, returns patch size frequencies as well as minimum and maximum patch sizes
    lengthperpatch = [len(item) for item in patches]
    
    infoarray = zeros([1000,2])
    infoarray[:,0] = arange(0,1000)
    for item in lengthperpatch:
        infoarray[item,1] += 1
    return [infoarray, min(lengthperpatch), max(lengthperpatch)]

def xydegrees(y,x):
    vectangle = math.degrees(math.atan2(y,x))
    if vectangle < 0:
        return vectangle+360
    else:
        return vectangle
    
def anglesortcolor(theta):
    colorlist = ['#FF0000','#964B00','#FFFF00','#00FFFF','#0000FF','#90EE90','#014421','#FFC0CB']
    modtheta = (theta + 22.5) % 360
    group = int(modtheta//45)
    return colorlist[group]

def adjpolypairs(pairdict): # Returns a list of all pairs of adjacent (edge-sharing) polygon faces 
    touching_list = list() #touching list is a list of face-index triangle pairs that share 2 vertices - i.e., that share an edge
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
    
def calcopc(testmesharray, minimumpatchcount):
    vfdict = DNE.vertexfacedict(testmesharray[2], len(testmesharray[0])) 
    Normals = normcore.computenormal(testmesharray[0],testmesharray[2], testmesharray[1], vfdict)[1] #just changed this, it used to be Normal_Map()

    flatfaces = array([i for i, norm in enumerate(Normals) if (norm[0:1] == 0).all()], dtype=int)
    orientation_map = array([xydegrees(norm[1],norm[0]) for norm in Normals])

    color_map = array([anglesortcolor(theta) for theta in orientation_map])
    color_map[flatfaces] = '#000000'
        
    pairdict = collections.defaultdict(list) #pairdict lists, per vertex index, all possible 2-item pairs of face indices that share that vertex 
    for item, locs in vfdict.iteritems():
        pairdict[item] = combpairs(locs)
        
    touching_list = adjpolypairs(pairdict)    
    
    oriented_touching_list = [pair for pair in touching_list if color_map[pair[0]] == color_map[pair[1]]]
    
    colorfacedict = collections.defaultdict(list) # colorfacedict is a dict that lists edge-sharing triangle pairs (by face index) for each color
    for item in oriented_touching_list:
        colorfacedict[color_map[item[0]]].append(item)
  
    minimumpatchcount = int(minimumpatchcount)    
    colorlist = ['#FF0000','#964B00','#FFFF00','#00FFFF','#0000FF','#90EE90','#014421','#FFC0CB']
        
    patches = [chunkpatches(colorfacedict[color]) for color in colorlist]
    # remove patches below minimum length
    patches = [removesmallpatches(subpat,minimumpatchcount) for subpat in patches]
    
    # count number of patches across mesh
    opc = sum([len(subpat) for subpat in patches])
       
    return [opc, [0,1,2], color_map, orientation_map, Normals]

def zrotatemesh(rotmesh, theta): # Rotates mesh vertices around Z axis by theta radians
    zrotmat = matrix([[math.cos(theta),(-1*math.sin(theta)),0],[math.sin(theta),math.cos(theta),0],[0,0,1]])
    
    rottenmesh = numcopy(rotmesh)
    rottenmeshm = mat(rottenmesh[0]).copy()
    rottenmeshm = row_stack([transpose(zrotmat * transpose(vert)) for vert in rottenmeshm]) # Rotate vertices by zrotmat    
    rottenmesh[0] = asarray(rottenmeshm)
    
    return rottenmesh

def centermesh(mesho):
    centroid = [average(mesho[:,0]), average(mesho[:,1]), average(mesho[:,2])]
    return array([subtract(vert,centroid) for vert in mesho])
    
def calcopcr(opcrmesh, minimumpatchcount):
    
    testmesh = numcopy(opcrmesh)
    testmesh[0] = centermesh(testmesh[0]) # Center mesh centroid on coordinate origin

    InitialOPCresult = calcopc(testmesh,minimumpatchcount)
    firstopcresult = [InitialOPCresult[0]]
    color_map = InitialOPCresult[2]
        
    nextopcresults = [calcopc((zrotatemesh(testmesh, math.radians(i*5.625))),minimumpatchcount)[0] for i in range(1,8)]
    OPCrotations = firstopcresult + nextopcresults
    print "OPC values at each rotation:"
    print OPCrotations

    return [average(OPCrotations), [0,1,2], color_map]

      
        
            
            
    