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
from struct import unpack
    
class PlythonMesh(object):
    """A class for creating and interacting with triangulated polygon meshes.
    
    Creates a list of Numpy ndarray objects containing triangulated polygon 
    mesh data if provided with a path to a .ply file. 
    
    Args:
        filepath (str): Path to a .ply polygon mesh file. 
        
    Attributes:
        mesh (list): Triangulated polygon mesh data. Contains three ndarrays:
            vertex XYZ points, polygons with component vertex XYZ points, 
            and polygons with component vertex indices. 
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
        
        
        datamode = self._StringAfter(meshstring, 'format')
        self.nvert = int(self._StringAfter(meshstring,'element vertex'))
        self.nface = int(self._StringAfter(meshstring,'element face'))
        
        if datamode == "ascii" or datamode == "ASCII":
            self.vertices, self.faces, self.triverts = self._read_ascii(meshstring)
        else:
            self.vertices, self.faces, self.triverts = self._read_bin(meshstring, datamode)
        
        self.mesh = [self.vertices, self.triverts, self.faces]
        
        self.check_mesh_consistency()
    
    def _read_ascii(self, meshstring):
        """Reads ASCII mesh data."""
        meshdata = meshstring[meshstring.find('end_header'):].splitlines()[1:]
        
        if len(meshdata) < self.nvert:
            raise EOFError('Unexpected end of .PLY file in list of vertices.')
        
        vlist = meshdata[0:self.nvert]
        
        if len(meshdata[self.nvert:]) < self.nface:
            raise EOFError('Unexpected end of .PLY in list of polygon vertex indices.')
        
        flist = meshdata[self.nvert:(self.nvert+self.nface)]
        
        if flist[0][0] != '3':
            raise ValueError('Non-triangular polygons found within .PLY file.')
        
        varray = array([vertices.split() for vertices in vlist], float)
        farray = array([vertices.split()[1:4] for vertices in flist], int)
        vfarray = array([[varray[vindex] for vindex in vertices] for vertices in farray], float)
        
        return varray, farray, vfarray 
    
    def _read_bin(self, meshstring, mode):
        """Reads binary mesh data."""
        if mode == "binary_little_endian":
            byteorder = "<"
        elif mode == "binary_big_endian":
            byteorder = ">"
        
        meshdata = meshstring[meshstring.find('end_header')+11:]
        
        # Expected number of bytes for vertex data, assumes 3 XYZ coordinate float values
        vertbytes = self.nvert*3*4
        # Expected number of bytes for face data, assumes unsigned char (= 3) and 3 integer vertex index values 
        facebytes = self.nface*(3*4+1)
        
        if len(meshdata) < vertbytes:
            raise EOFError('Unexpected end of .PLY file in list of vertices.')
        
        vertdata = meshdata[0:vertbytes]
        
        if len(meshdata[vertbytes:]) < facebytes:
            raise EOFError('Unexpected end of .PLY in list of polygon vertex indices.')
        
        facedata = meshdata[vertbytes:vertbytes+facebytes]
        
        if unpack(byteorder+'B', facedata[0])[0] != 3:
            raise ValueError('Non-triangular polygons found within .PLY file.')
        
        vert_xyz_split = [vertdata[i:i+4] for i in range(0, vertbytes, 4)]
        vert_xyz_points = map(lambda x: unpack(byteorder+'f', x)[0], vert_xyz_split)
        vert_array = array(vert_xyz_points)
        vert_array = vert_array.reshape([self.nvert,3])
        
        face_split = [facedata[i:i+13] for i in range(0, facebytes, 13)]
        face_index_split = [[face[i:i+4] for i in range(1, len(face), 4)] for face in face_split]
        face_index_value = [[unpack(byteorder+'i', index)[0] for index in face] for face in face_index_split]
        face_array = array(face_index_value)
        face_array = face_array.reshape([self.nface,3])
        
        vert_face_array = array([[vert_array[vertex] for vertex in face] for face in face_array], float)
        
        return vert_array, face_array, vert_face_array
    
    def check_mesh_consistency(self):
        """Checks mesh data produced by CreateArray for consistency, raises exceptions if mesh is inconsistent or nonexistent."""
        if self.vertices is None or self.faces is None or self.triverts is None:
            raise ValueError('Mesh data is missing.')
        if len(self.vertices) != self.nvert or len(self.faces) != self.nface or len(self.triverts) != self.nface:
            raise ValueError('Unexpected vertex, face, or face-vertex index length, mesh is inconsistent.')
        for i, trivert in enumerate(self.triverts):
            if (trivert != self.vertices[self.faces[i]]).any():
                raise ValueError("Mesh vertex and face arrays do not contain identical vertices, mesh is inconsistent.")
        
    def SaveArray(self, filepath): 
        """Saves mesh as an ASCII .ply format triangulated surface file.
        
        Args:
            filepath (str): Path to a .ply polygon mesh file to be created.
        
        """
        self.check_mesh_consistency()
        
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
        return self.vertices
    
    def TriVert(self):
        """Returns polygons with component vertex XYZ data points."""
        return self.triverts
    
    def Triangles(self):
        """Returns polygons with component vertex indices."""
        return self.faces
    
    def Mesh(self):
        """Returns triangulated polygon mesh data."""
        return self.mesh
    
    def _StringAfter(self,text,phrase): 
        """Internal method for finding first discrete word or number (separated by spaces) after phrase in text."""
        try:
            return text[text.index(phrase)+len(phrase):].split()[0]         
        except (ValueError, IndexError) as err:
            err.args += ('Phrase %s is not in text %s, is longer than text, or is last element in text.' % (phrase, text),)
            raise

    
