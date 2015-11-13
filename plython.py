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
    
class PlythonMesh(object):
    """A class for creating and interacting with triangulated polygon meshes.
    
    Creates a list of Numpy ndarray objects containing triangulated polygon 
    mesh data if provided with a path to a .ply file. 
    
    Args:
        filepath (str): Path to a .ply polygon mesh file. 
        
    Attributes:
        mesh (list): Triangulated polygon mesh data. Contains three ndarrays:
            vertex XYZ points, polygons with component vertex indices, and 
            polygons with component vertex XYZ points. 
        vertices (ndarray): Vertex XYZ points for mesh.
        faces (ndarray): Polygons with component vertex indices for mesh.
        triverts (ndarray): Polygons with component vertex XYZ points for mesh.
        nvert (int): Number of vertices in mesh. 
        nface (int): Number of polygons in mesh.  
    
    """
    def __init__(self, filepath=""):
        self.mesh = None
        self.vertices = None
        self.faces = None
        self.triverts = None
        self.nvert = 0
        self.nface = 0
        
        if filepath is not "":
            self.CreateArray(filepath)
    
    def CreateArray(self, filepath): 
        """Creates triangulated polygon mesh data objects from .ply file.
        
        Args:
            filepath (str): Path to a .ply polygon mesh file.
        
        """
        meshfile = open(filepath, 'r') 
        meshstring = meshfile.read()
        meshfile.close()
        
        nvertex = int(self._StringAfter(meshstring,'element vertex'))
        nface = int(self._StringAfter(meshstring,'element face'))
        
        meshdata = meshstring[meshstring.find('end_header'):].splitlines()[1:]
        vlist = meshdata[0:nvertex]
        flist = meshdata[nvertex:(nvertex+nface)]
        
        varray = array([vertices.split() for vertices in vlist], float)
        farray = array([vertices.split()[1:4] for vertices in flist], int)
        vfarray = array([[varray[vindex] for vindex in vertices] for vertices in farray], float) 
        
        self.mesh = [varray, vfarray, farray]
        self.vertices = varray
        self.faces = farray
        self.triverts = vfarray
        self.nvert = len(varray)
        self.nface = len(farray) 

    def SaveArray(self, filepath): 
        """Saves mesh as an ASCII .ply format triangulated surface file.
        
        Args:
            filepath (str): Path to a .ply polygon mesh file to be created.
        
        """
        arrayfile = open(filepath,'w')
        arrayfile.write("ply\nformat ascii 1.0\nelement vertex %s\n" % self.nvert)
        arrayfile.write("property float32 x\nproperty float32 y\nproperty float32 z\nelement face %s\nproperty list uint8 int32 vertex_indices\nend_header\n" % self.nface)
        
        for xyz in self.Vertices():
            arrayfile.write(str(xyz[0])+" "+str(xyz[1])+" "+str(xyz[2])+"\n")
        
        for vertexindices in self.Triangles():
            arrayfile.write("3 " + str(int(vertexindices[0]))+" "+str(int(vertexindices[1]))+" "+str(int(vertexindices[2]))+"\n")
            
        arrayfile.close()
        
    def Vertices(self):
        """Returns vertex XYZ data points."""
        return self.mesh[0]
    
    def TriVert(self):
        """Returns polygons with component vertex XYZ data points."""
        return self.mesh[1]
    
    def Triangles(self):
        """Returns polygons with component vertex indices."""
        return self.mesh[2]
    
    def Mesh(self):
        """Returns triangulated polygon mesh data."""
        return self.mesh
    
    def _StringAfter(self,text,phrase): 
        """Internal method for finding first discrete word or number (separated by spaces) after phrase in text."""
        return text[text.find(phrase)+len(phrase):].split()[0]         
        
    
