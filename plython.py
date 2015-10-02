'''
Created on Sep 1, 2011

Plython opens .ply files and produces simple numpy arrays with polygon vertex and face data. Using 
the createarray() function, this module reads ASCII-format .ply (binary is not supported to date) 
and returns numpy arrays representing position of mesh vertices and connections between vertices
to produce interconnected triangular polygon faces. A savearray() function is also provided to save
arrays of mesh data (formatted similarly to arrays returned by the createarray() function). 

Mesh .ply files are initiated with headers defining basic mesh properties and subsequent lists of 
mesh property data. To read mesh files, the functions included here first retrieve the number of 
polygon vertices and faces from the header. XYZ coordinate triplets for polygon vertices are then 
read and stored as an i x 3 array where i equals number of vertices and assuming triangular polygons. 
After this lists of polygon vertices (identified as indices from the first array) comprising each 
mesh are read and stored in two arrays. One array stores XYZ coordinate triplets for each vertex 
comprising each polygon, producing a j x i x 3 array where i equals vertex number and j equals 
face number. For greater efficiency, this data is also stored in a j x 3 array listing vertex 
indices (from the first array described above) comprising each face. createarray() returns these
three arrays as a list in the order described. 

@author: Julia M. Winchester
'''
from numpy import array

def stringafter(text,phrase): # Returns first discrete word or number after phrase in text, assuming words or numbers separated by whitespace characters
    return text[text.find(phrase)+len(phrase):].split()[0] 

def createarray(filepath): # Returns a list of numpy arrays of vertex XYZ triplets, XYZ triplets per vertex comprising each face, and vertex indices comprising each face
    meshfile = open(filepath, 'r') 
    meshstring = meshfile.read()
    meshfile.close()
    
    nvertex = int(stringafter(meshstring,'element vertex'))
    nface = int(stringafter(meshstring,'element face'))
    
    meshdata = meshstring[meshstring.find('end_header'):].splitlines()[1:]
    vlist = meshdata[0:nvertex]
    flist = meshdata[nvertex:(nvertex+nface)]
    
    varray = array([vertices.split() for vertices in vlist], float)
    farray = array([vertices.split()[1:4] for vertices in flist], int)
    vfarray = array([[varray[vindex] for vindex in vertices] for vertices in farray], float) 
    
    return [varray, vfarray, farray]

def savearray(vertex, faceindex, filename): # Saves an ASCII .ply mesh file given an iterable of XYZ coordinate data for vertices and an iterable of vertex indices for each face (see outputs of createarray() for examples)
    arrayfile = open(filename,'w')
    arrayfile.write("ply\nformat ascii 1.0\nelement vertex "+ str(len(vertex)) + "\n")
    arrayfile.write("property float32 x\nproperty float32 y\nproperty float32 z\nelement face " + str(len(faceindex)) + "\nproperty list uint8 int32 vertex_indices\nend_header\n")
    
    for xyz in vertex:
        arrayfile.write(str(xyz[0])+" "+str(xyz[1])+" "+str(xyz[2])+"\n")
    
    for vertexindices in faceindex:
        arrayfile.write("3 " + str(int(vertexindices[0]))+" "+str(int(vertexindices[1]))+" "+str(int(vertexindices[2]))+"\n")
        
    arrayfile.close()
    
    return
        
    
    
    
    





    


