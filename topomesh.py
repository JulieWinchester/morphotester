'''
Created on Jan 10, 2016

@author: Julia M. Winchester
'''
import plython
import DNE
import OPC
import RFI
import implicitfair

from collections import defaultdict

class TopoMesh(plython.PlythonMesh):
    """A class for creating and interacting with triangulated polygon meshes and topographic variables.
    
    Class inherits from plython.PlythonMesh. Creates a list of Numpy ndarray objects containing 
    triangulated polygon mesh data if provided with a path to a .ply file. Topographic variables
    are instanced as None and take the data types specified below when generated using the 
    ProcessSurface method. 
    
    Args:
        filepath (str): Path to a .ply polygon mesh file
        
    Attributes:
        mesh (list): Triangulated polygon mesh data. Contains three ndarrays:
            vertex XYZ points, polygons with component vertex XYZ points, 
            and polygons with component vertex indices. 
        nvert (int): Number of vertices in mesh. 
        nface (int): Number of polygons in mesh.
        vertices (ndarray): Vertex XYZ points for mesh.
        faces (ndarray): Polygons with component vertex indices for mesh.
        triverts (ndarray): Polygons with component vertex XYZ points for mesh.
        DNE (float): Total Dirichlet normal energy of mesh. 
        DNEscalars (ndarray): Scalars for visualizing DNE.
        conditionfaces (list): List of polygon face indices with high matrix condition numbers.
        boundaryfaces (list): List of polygon face indices forming mesh edges.
        outlierfaces (list): List of polygon face indices removed as outliers, with DNE values and face areas.
        RFI (float): Relief index of mesh (surface area/projected area).
        surfarea (float): 3D surface area of mesh. 
        projarea (float): 2D surface area of mesh projected on XY plane. 
        OPCR (float): Orientation patch count rotated for mesh. 
        OPClist (list): Orientation patch counts at 8 rotations for mesh.
        OPCscalars: Scalars for visualizing OPC. 
    
    """
    def __init__(self, filepath=""):
        super(TopoMesh,self).__init__(filepath)
        
        self.DNE = None
        self.DNEscalars = None
        self.conditionfaces = None
        self.boundaryfaces = None
        self.outlierfaces = None
        
        self.RFI = None
        self.surfarea = None
        self.projarea = None
        self.linelen = None
        self.bluepixie = None
        self.redpixie = None
        self.pixelratio = None
        
        self.OPCR = None
        self.OPClist = None
        self.OPCscalars = None
        
    def GenerateDNE(self, dosmooth, smoothit, smoothstep, docondition, dooutlier, outlierperc, outliertype, filename):
        """Calculates Dirichlet normal energy (surface bending) from mesh data.
        
        For details on args, see DNE.MeshDNE class. 
        
        Args:
            doSmooth (bool): If true, do implicit fair smooth. 
            SmoothIt (int): Iterations of smoothing
            SmoothStep (float): Smoothing step size. 
            doCondition (bool): If true, do polygon condition number control. 
            doOutlier (bool): If true, do outlier removal. 
            OutlierPerc (float): Outlier percentile. 
            OutlierType (bool): If true, outliers as energy*area. If false, outliers as energy. 
            
        """
        self.check_for_mesh(self.GenerateDNE)
        
        surfcurv = DNE.MeshDNE(self, dosmooth, smoothit, smoothstep, docondition, dooutlier, outlierperc, outliertype, filename)
        self.DNE = surfcurv.DNE
        self.DNEscalars = surfcurv.equantity
        self.conditionfaces = surfcurv.high_condition_faces
        self.boundaryfaces = surfcurv.boundary_faces
        self.outlierfaces = surfcurv.outlier_faces
          
    def GenerateRFI(self):
        """Calculates relief index (surface relief) from mesh data."""
        self.check_for_mesh(self.GenerateRFI)
        
        surfrelf = RFI.MeshRFI(self)
        self.RFI = surfrelf.RFI
        self.surfarea = surfrelf.surfarea
        self.projarea = surfrelf.projarea
        self.linelen = surfrelf.linelen
        self.bluepixie = surfrelf.bluepixie
        self.redpixie = surfrelf.redpixie
        self.pixelratio = surfrelf.pixelratio
        
    def GenerateOPCR(self, minpatch):
        """Calculates orientation patch count rotated (surface complexity) from mesh data.
        
        For details on args see OPC.MeshOPCR class. 
        
        Args:
            minpatch (int): Minimum size for counting patches.
            
        """
        self.check_for_mesh(self.GenerateOPCR)
        
        surfcomp = OPC.MeshOPCR(self, minpatch)
        self.OPCR = surfcomp.OPCR
        self.OPClist = surfcomp.opc_list
        self.OPCscalars = surfcomp.colormap_list[0]
        
    def implicit_fair_mesh(self, iterations, step):
        self.get_vert_tri_dict()
        faired_vertices = implicitfair.smooth(self.vertices, self.faces, iterations, step, self.vert_tri_dict)
        self.vertices = faired_vertices
        self.mesh[0] = faired_vertices
        
        for i in range(len(self.triverts)):
            self.triverts[i] = self.vertices[self.faces[i]]
            
        self.mesh[1] = self.triverts
    
    def get_vert_tri_dict(self):
        """Generates dictionary associating vertex index keys with related polygon index values.""" 
        self.vert_tri_dict = defaultdict(list)
        
        for findex, face in enumerate(self.faces):
            for vertex in face:
                self.vert_tri_dict[vertex].append(findex)
    
    def check_for_mesh(self, function="function"):
        if self.mesh == None:
            raise ValueError('A mesh has not been imported, %s cannot proceed.' % function)
        