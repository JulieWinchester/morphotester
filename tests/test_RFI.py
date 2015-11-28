"""
Created on Nov 26, 2015

@author: Julia M. Winchester
"""
import unittest
import RFI
from numpy import array
from copy import copy
import cPickle as pickle

try:
    import Image
except ImportError:
    from PIL import Image

class Test_MeshRFI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open('./tests/testmeshThege58.pkl', 'rb') as input:
            cls._Mesh = pickle.load(input)
        cls._MeshRFI = RFI.MeshRFI(cls._Mesh)
        with open('./tests/testmeshThege58plot.pkl', 'rb') as input:
            cls._plot = pickle.load(input)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_vertex_number_errors(self):
        """Tests for error when number of vertices per triangle does not equal three."""
        Mesh = copy(self.__class__._Mesh)
        Mesh.vertices = array([[0.0,0.0],[0.0,1.0],[1.0,1.0]])
        Mesh.faces = array([[0, 1, 2]])
        Mesh.triverts = array([[[0.0,0.0],[0.0,1.0],[1.0,1.0]]])
        self.assertRaises(IndexError, RFI.MeshRFI, Mesh)
        
    def test_mesh_errors(self):
        """Tests for errors when mesh is inconsistent."""
        Mesh = copy(self.__class__._Mesh)
        Mesh.vertices = array([[0.0,0.0,0.0],[0.0,1.0,0.0],[1.0,1.0,0.0]])
        Mesh.faces = array([0, 1, 2])
        Mesh.triverts = array([[[0.0,1.0,0.0],[0.0,0.0, 0.0],[1.0,1.0, 0.0]]])
        self.assertRaises(ValueError, RFI.MeshRFI, Mesh)
        
    def test_rfi(self):
        """Tests RFI calculation for example mesh."""
        self.assertEqual(self.__class__._MeshRFI.RFI, 2.178, "Relief index not calculated as expected from test mesh.")
    
    def test_surface_area(self):
        """Tests surface area for example mesh."""
        self.assertEqual(self.__class__._MeshRFI.surfarea, 213.537, "3D surface area not calculated as expected from test mesh.")
    
    def test_projection_area(self):
        """Tests 2D projection area for example mesh."""
        self.assertEqual(self.__class__._MeshRFI.projarea, 98.056, "2D projection area not calculated as expected from test mesh.")
    
    def test_plot(self): # uses setUp plot for comparison
        """Tests surface plot for example mesh."""
        self.assertEqual(self.__class__._MeshRFI.imgbuffer.getvalue(), self.__class__._plot.getvalue(), "Surface not plotting as expected.")
    
    def test_reference_colors(self): # uses on the fly plot from setUp mesh
        """Tests for presence of reference colors in plot."""
        imgbuffer = self.__class__._MeshRFI.imgbuffer
        imgbuffer.seek(0)
        imgset = set(Image.open(imgbuffer).getdata())
        self.assertTrue({(0,0,255,255), (255,0,0,255), (0,0,255,255)} <= imgset, "Reference colors not present in surface plot.")
    
    def test_zero_area_plot_error(self):
        """Tests for error for mesh with zero 2D XY area."""
        Mesh = copy(self.__class__._Mesh)
        Mesh.vertices = array([[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0], [0.0,0.0,0.0]])
        Mesh.faces = array([[0, 1, 2], [0, 2, 3]])
        Mesh.triverts = array([[[0.0,1.0,0.0],[0.0,0.0, 0.0],[1.0,1.0, 0.0]], [[0.0,1.0,0.0],[0.0,0.0, 0.0],[1.0,1.0, 0.0]]])
        self.assertRaises(ValueError, RFI.MeshRFI, Mesh)

    def test_area_from_plot(self):
        """Tests 2D projection area for example plot."""
        MeshRFI = copy(self.__class__._MeshRFI)
        MeshRFI.imgbuffer = self.__class__._plot
        MeshRFI._get_2d_area()
        self.assertEqual(MeshRFI.projarea, 98.056, "2D projection area not calculated as expected from test plot.")
        
    def test_red_blue_pixels(self): # uses on the fly plot
        """Tests number of red and blue pixels in plot of test mesh."""
        self.assertEqual(self.__class__._MeshRFI.redpixie, 480, "Unexpected number of red pixels in surface plot from test mesh.")
        self.assertEqual(self.__class__._MeshRFI.bluepixie, 101564, "Unexpected number of blue pixels in surface plot from test mesh.")
                
    def test_pixel_counting(self):
        """Tests pixel counting from test plot."""
        imgbuffer = self.__class__._plot
        imgbuffer.seek(0)
        img = Image.open(imgbuffer).getdata()
        self.assertEqual(self.__class__._MeshRFI._count_pixels(img, (255, 0, 0, 255), (255, 255, 255, 255), (255, 155, 155, 255), (255, 188, 188, 255), (255, 230, 230, 255), (255, 205, 205, 255)), 378436, "Unexpected pixel count from test plot.")
        self.assertEqual(self.__class__._MeshRFI._count_pixels(img, (255, 0, 0, 255), (255, 0, 0, 255), (255, 255, 255, 255), (255, 255, 255, 255), (255, 155, 155, 255), (255, 188, 188, 255), (255, 230, 230, 255), (255, 205, 205, 255)), 378436, "Duplicate colors in color list unexpectedly affect pixel counting.")
        self.assertEqual(self.__class__._MeshRFI._count_pixels(img, (255, 0, 0, 255)), 479, "Unexpected pixel count of single color from test plot.")
        self.assertEqual(self.__class__._MeshRFI._count_pixels(img), 0, "Unexpected non-zero pixel count from test plot with no colors specified to be counted.")

    def test_non_stringio_object_error(self):
        """Test error when non-image object is supplied."""
        MeshRFI = copy(self.__class__._MeshRFI)
        MeshRFI.imgbuffer = 0
        self.assertRaises(TypeError, MeshRFI._get_2d_area)
        
    def test_triangle_area(self):
        """Test triangle area calculation."""
        verts = self.__class__._MeshRFI.Mesh.triverts[0] 
        self.assertEqual(self.__class__._MeshRFI._triangle_area(verts), 6.556493936703974e-06, "Triangle area value not calculated as expected.")
        
    def test_triangle_identical_vertices(self):
        """Test that 0 is returned for triangle area when one or more vertices are identical."""
        verts = self.__class__._MeshRFI.Mesh.triverts[0]
        self.assertEqual(self.__class__._MeshRFI._triangle_area(array([verts[0], verts[0], verts[0]])), 0.0, "A triangle with three identical vertices unexpectedly returns a non-zero area value.")
        self.assertEqual(self.__class__._MeshRFI._triangle_area(array([verts[0], verts[0], verts[1]])), 0.0, "A triangle with two identical vertices unexpectedly returns a non-zero area value.")
        
    def test_triangle_vertex_shuffle(self):
        """Test that triangle area is equal regardless of vertex order."""
        for vert in self.__class__._MeshRFI.Mesh.triverts:
            self.assertAlmostEqual(self.__class__._MeshRFI._triangle_area(vert), self.__class__._MeshRFI._triangle_area(array([vert[0],vert[2],vert[1]])), 10, "Triangle vertex re-ordering unexpectedly modifies triangle area calculation.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()