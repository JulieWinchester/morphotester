'''
Created on Dec 12, 2015

@author: Julia M. Winchester
'''
import unittest
import plython
import cPickle as pickle
from numpy import allclose
from copy import copy
import os

class Test_PlythonMesh(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open('./tests/testmeshThege58.pkl', 'rb') as input:
            cls._Mesh = pickle.load(input)
        cls._NullMesh = plython.PlythonMesh()
        cls._AsciiMesh = plython.PlythonMesh('./tests/Thege58.ply')

    def test_init_no_mesh(self):
        EmptyMesh = self.__class__._NullMesh
        self.assertTrue(all(x == None for x in (EmptyMesh.vertices, EmptyMesh.faces, EmptyMesh.triverts, EmptyMesh.mesh)), msg = "On PlythonMesh instantiation without initial mesh file, variables expected to be None type have other type.")
        self.assertTrue(all(x == 0 for x in (EmptyMesh.nface, EmptyMesh.nvert)), msg = "On PlythonMesh instantiation without initial mesh file, variables expected to be zero are non-zero.")
    
    def test_init_mesh(self):
        Mesh = self.__class__._AsciiMesh
        self.assertEqual(Mesh.nface, 10040, "Unexpected number of faces from PlythonMesh instantiated with initial mesh file.")
        self.assertEqual(Mesh.nvert, 5135, "Unexpected number of vertices from PlythonMesh instantiated with initial mesh file.")
        self.assertTrue((Mesh.vertices == self.__class__._Mesh.vertices).all(), msg = 'Unexpected vertices from PlythonMesh instantiated with initial mesh file.')
        self.assertTrue((Mesh.faces == self.__class__._Mesh.faces).all(), msg = 'Unexpected polygons from PlythonMesh instantiated with initial mesh file.')
        self.assertTrue((Mesh.triverts == self.__class__._Mesh.triverts).all(), msg = 'Unexpected vertex-polygon map from PlythonMesh instantiated with initial mesh file.')
        
    def test_create_array(self):
        Mesh = copy(self.__class__._NullMesh)
        Mesh.CreateArray('./tests/Thege58.ply')
        self.assertEqual(Mesh.nface, 10040, "Unexpected number of faces from PlythonMesh CreateArray.")
        self.assertEqual(Mesh.nvert, 5135, "Unexpected number of vertices from PlythonMesh CreateArray.")
        self.assertTrue((Mesh.vertices == self.__class__._Mesh.vertices).all(), msg = 'Unexpected vertices from PlythonMesh CreateArray.')
        self.assertTrue((Mesh.faces == self.__class__._Mesh.faces).all(), msg = 'Unexpected polygons from PlythonMesh CreateArray.')
        self.assertTrue((Mesh.triverts == self.__class__._Mesh.triverts).all(), msg = 'Unexpected vertex-polygon map from PlythonMesh CreateArray.')
        
    def test_binary_ply(self):
        BinMesh = plython.PlythonMesh('./tests/Thege58bin.ply')
        self.assertTrue(allclose(self.__class__._Mesh.vertices, BinMesh.vertices), msg = 'Unexpected differences between mesh vertex data produced from ASCII and binary .PLY files.')
        self.assertTrue(allclose(self.__class__._Mesh.triverts, BinMesh.triverts), msg = 'Unexpected differences between mesh polygon and vertex data produced from ASCII and binary .PLY files.')
        self.assertTrue((self.__class__._Mesh.faces == BinMesh.faces).all(), msg = 'Unexpected differences between mesh polygon data produced from ASCII and binary .PLY files.')
        
    def test_save_array(self):
        self.__class__._Mesh.SaveArray('./tests/temp.ply')
        Mesh = plython.PlythonMesh('./tests/temp.ply')
        self.assertEqual(Mesh.nface, 10040, "Unexpected number of faces from .PLY file written by SaveArray.")
        self.assertEqual(Mesh.nvert, 5135, "Unexpected number of vertices from .PLY file written by SaveArray.")
        self.assertTrue((Mesh.vertices == self.__class__._Mesh.vertices).all(), msg = 'Unexpected vertices from .PLY file written by SaveArray.')
        self.assertTrue((Mesh.faces == self.__class__._Mesh.faces).all(), msg = 'Unexpected polygons from .PLY file written by SaveArray.')
        self.assertTrue((Mesh.triverts == self.__class__._Mesh.triverts).all(), msg = 'Unexpected vertex-polygon map from .PLY file written by SaveArray.')
        os.remove('./tests/temp.ply')
        
    def test_save_fail_no_mesh(self):
        EmptyMesh = self.__class__._NullMesh
        self.assertRaises(ValueError, EmptyMesh.SaveArray, './tests/temp.ply')
    
    def test_save_fail_mesh_inconsistent(self):
        Mesh = copy(self.__class__._AsciiMesh)
        Mesh.vertices[0] = 123.9187
        self.assertRaises(ValueError, Mesh.SaveArray, './tests/temp.ply')
    
    def test_vertices_method(self):
        Mesh = self.__class__._AsciiMesh
        self.assertTrue((Mesh.vertices == Mesh.Vertices()).all(), msg='PlythonMesh.Vertices method returning vertex data different from mesh data.')
        
    def test_triverts_method(self):
        Mesh = self.__class__._AsciiMesh
        self.assertTrue((Mesh.triverts == Mesh.TriVert()).all(), msg='PlythonMesh.TriVert method returning polygon-vertex data different from mesh data.')
    
    def test_triangles_method(self):
        Mesh = self.__class__._AsciiMesh
        self.assertTrue((Mesh.faces == Mesh.Triangles()).all(), msg='PlythonMesh.Triangles method returning polygon data different from mesh data.')
    
    def test_mesh_method(self):
        Mesh = self.__class__._AsciiMesh
        self.assertTrue((Mesh.mesh == Mesh.Mesh()), msg='PlythonMesh.Mesh method returning polygon data different from mesh data.')
    
    def test_empty_mesh_methods(self):
        EmptyMesh = self.__class__._NullMesh
        self.assertEqual(EmptyMesh.Vertices(), None, 'PlythonMesh.Vertices method not returning None for empty mesh as expected.')
        self.assertEqual(EmptyMesh.TriVert(), None, 'PlythonMesh.TriVert method not returning None for empty mesh as expected.')
        self.assertEqual(EmptyMesh.Triangles(), None, 'PlythonMesh.Triangles method not returning None for empty mesh as expected.')
        self.assertEqual(EmptyMesh.Mesh(), None, 'PlythonMesh.Mesh method not returning None for empty mesh as expected.')
        
    def test_string_after(self):
        Mesh = self.__class__._AsciiMesh
        self.assertEqual(Mesh._StringAfter("Hello world", "Hello"), "world")
        
    def test_StringAfter_final_entry_error(self):
        Mesh = self.__class__._AsciiMesh
        self.assertRaises(IndexError, Mesh._StringAfter, "Hello world", "world")
    
    def test_StringAfter_no_entry_error(self):
        Mesh = self.__class__._AsciiMesh
        self.assertRaises(ValueError, Mesh._StringAfter, "Hello world", "goodbye")
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()