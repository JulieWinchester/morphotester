'''
Created on Sep 2, 2011

This module calculates relief index (3D surface area/2D area of surface
projected on XY plane) for a provided 3D mesh using the MeshRFI class. 

@author: Julia M. Winchester
'''

import matplotlib
matplotlib.use('AGG')

import matplotlib.pyplot as plt
from StringIO import StringIO
from numpy import sqrt, square, amin, amax, array
from numpy.linalg import det

try:
    import Image
except ImportError:
    from PIL import Image

class MeshRFI(object):
    """Class for calculating and storing relief index values for polygonal mesh data. 
    
    When instanced, this class calculates relief index and associated variables
    and stores them. All attributes below are populated on instantiation.
    
    Args:
        TopoMesh (TopoMesh object): Triangulated polygon mesh data. 
    
    Attributes:
        Mesh (TopoMesh object): Triangulated polygon mesh data. 
        RFI (float): Mesh surface relief index (surfarea/projarea).
        surfarea (float): 3D mesh surface area.
        projarea (float): 2D mesh surface area projected on XY plane.
        linelin (float): Reference line for building pixel/area unit ratio.
        bluepixie (float): Number of blue pixels (mesh) on projected area render.
        redpixie (float): Number of red pixels (reference line) on projected area render.
        pixelratio (float): Pixel/area unit ratio, used for converting number of
                            blue pixels to area units.
        imgbuffer (StringIO object): 2D plot of surface mesh with reference line for
                                    determining projected XY-plane surface area.
    """
    def __init__(self, TopoMesh): 
        self.Mesh = TopoMesh
        self.RFI = None
        self.surfarea = None
        self.projarea = None
        self.linelen = None
        self.bluepixie = None
        self.redpixie = None
        self.pixelratio = None
        self.imgbuffer = None
        
        self.calcrfi()
        
    def calcrfi(self):
        """Calls methods for calculating surface and projected areas, then derives relief index value."""
        self.surfarea = round(sum(self.triangle_area(face) for face in self.Mesh.triverts),3)      
        self._get_projection_area()
        self.RFI = round(self.surfarea/self.projarea, 3)
    
    def _get_projection_area(self):
        """Creates 2D plot of surface mesh and derives projection area from this plot."""
        self._plot_surface()
        self._get_2d_area()
    
    def _plot_surface(self): # Returns pixel length of scalebar and image plot as StringIO file-like object
        """Plots 3D polygonal mesh as 2D raster shape on the XY plane with reference line for area units."""
        xarray = self.Mesh.vertices[:,0]
        yarray = self.Mesh.vertices[:,1]
        
        xaxismin = amin(xarray) - 0.5
        xaxismax = amax(xarray) + 0.5
        yaxismin = amin(yarray) - 0.5
        yaxismax = amax(yarray) + 0.5
        self.linelen = amax(yarray) - amin(yarray) + 1
        
        fig = plt.figure()
        ax = fig.add_subplot(111)
            
        linesquare = matplotlib.patches.Polygon([[xaxismin,yaxismin],[xaxismin,yaxismax]], ec='r',fc='r')
        plt.axis([xaxismin,xaxismax,yaxismin,yaxismax])
        ax.add_patch(linesquare)
    
        ax.set_xscale('linear')
        ax.set_yscale('linear')
        ax.set_aspect(1)
        ax.axis('off')
        
        vert = array([face[:,[0,1]] for face in self.Mesh.triverts]) # makes a copy of self.Mesh.triverts including only XY coordinate points for vertices comprising faces 
           
        polygons = matplotlib.collections.PolyCollection(vert,facecolor='b',edgecolor='b')
            
        ax.add_collection(polygons)
        
        self.imgbuffer = StringIO()
        plt.savefig(self.imgbuffer,format='png')
    
    def _get_2d_area(self): # Receives image plot from StringIO object and returns absolute area covered by mesh as projected on XY plane   
        """Derives 2D surface area of polygonal mesh projected on XY plane given a 2D raster plot and area-unit reference line."""
        self.imgbuffer.seek(0) # Rewind image buffer back to beginning to allow Image.open() to identify it
        img = Image.open(self.imgbuffer).getdata()  
        self.imgbuffer.close()
        
        self.redpixie = self.count_pixels(img, [(255,0,0,255),(255,127,127,255)])
        self.bluepixie = len(list(img)) - self.count_pixels(img, [(255, 0, 0, 255), (255, 255, 255, 255), (255, 155, 155, 255), (255, 188, 188, 255), (255, 230, 230, 255), (255, 205, 205, 255)])    
            
        rope = float(self.linelen)
        redballoon = float(self.redpixie)   
        self.pixelratio = redballoon/rope
        
        self.projarea = round(float(self.bluepixie)*(square(rope)/square(redballoon)), 3)

    def count_pixels(self, image, colorlist): # Returns the number of pixels in a list of RGB+transparency values that match the colors (RGB+transparency) given in colorlist
        """Returns the number of pixels in an image that match listed colors.
        
        Args:
            image (StringIO object): Image string buffer object from which pixels are counted.
            colorlist (list): List of RGB+transparency value color data, pixels in image that
                                match these colors will be counted.
        """
        return sum(list(image).count(color) for color in colorlist)
     
    def triangle_area(self, verts):
        """Returns the area of a triangle defined by vertices.
        
        Args:
            verts(ndarray): A set of three XYZ point triplets forming a triangle. 
        """
        fx = verts[:,0]
        fy = verts[:,1]
        fz = verts[:,2]
        fc = [1,1,1]
        
        a = [fx, fy, fc]
        b = [fy, fz, fc]
        c = [fz, fx, fc]
        
        return 0.5*sqrt(square(det(a))+square(det(b))+square(det(c)))
    




