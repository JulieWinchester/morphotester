'''
Created on Jan 7, 2016

@author: Julia M. Winchester
'''
import unittest
import DNE
import cPickle as pickle

from copy import deepcopy
from numpy import array
from numpy.linalg import LinAlgError

class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open('./tests/testmeshThege58.pkl', 'rb') as input:
            cls._Mesh = pickle.load(input)
        with open('./tests/testmeshThege58dne.pkl', 'rb') as input:
            cls._RefMeshDNE = pickle.load(input)
        cls._MeshDNE = DNE.MeshDNE(cls._Mesh, 0, 3, 0.1, 1, 1, 99.9, 1)

    def test_dne_calculation(self):
        self.assertEqual(self.__class__._MeshDNE.DNE, 247.938, msg = "DNE not calculated as expected.")
    
    def test_polygon_values(self):
        self.assertTrue((self.__class__._MeshDNE.e == self.__class__._RefMeshDNE.e).all(), msg = "Polygon energy densities not calculated as expected.")
        self.assertTrue((self.__class__._MeshDNE.facearea == self.__class__._RefMeshDNE.facearea).all(), msg = "Polygon face areas not calculated as expected.")
        self.assertTrue((self.__class__._MeshDNE.equantity == self.__class__._RefMeshDNE.equantity).all(), msg = "Polygon energy quantities not calculated as expected.")
        
    def test_alternate_outlier_removal(self):
        MeshDNE = DNE.MeshDNE(self.__class__._Mesh, 0, 3, 0.1, 1, 1, 99.9, 0)
        self.assertEqual(MeshDNE.DNE, 249.806)
                
    def test_secondary_lists(self):
        self.assertListEqual(self.__class__._MeshDNE.high_condition_faces, self.__class__._RefMeshDNE.high_condition_faces, msg = "List of high condition number faces not built as expected.")
        self.assertListEqual(self.__class__._MeshDNE.outlier_faces, self.__class__._RefMeshDNE.outlier_faces, msg = "List of outlier faces not built as expected.")
        self.assertListEqual(self.__class__._MeshDNE.boundary_faces, self.__class__._RefMeshDNE.boundary_faces, msg = "List of boundary faces not built as expected.")
        self.assertListEqual(self.__class__._MeshDNE.nan_faces, self.__class__._RefMeshDNE.nan_faces, msg = "List of polygon faces with Nan energy values not built as expected.")

    def test_normals(self):
        self.assertTrue((self.__class__._MeshDNE.fnormal == self.__class__._RefMeshDNE.fnormal).all(), msg = "Array of face normal vectors not created as expected.")
        self.assertTrue((self.__class__._MeshDNE.vnormal == self.__class__._RefMeshDNE.vnormal).all(), msg = "Array of approximated vertex normal vectors not created as expected.")

    def test_get_vert_tri_dict_method(self):
        MeshDNE = deepcopy(self.__class__._MeshDNE)
        MeshDNE.Mesh.faces = array([[0, 1, 3], [1, 3, 4], [1, 2, 4], [3, 4, 5]])
        
        solution_dict = {0: [0], 1: [0, 1, 2], 2: [2], 3: [0, 1, 3], 4: [1, 2, 3], 5: [3]}
        
        MeshDNE._get_vert_tri_dict()
        
        self.assertDictEqual(MeshDNE.vert_tri_dict, solution_dict, msg = "Vertex to polygon index dictionary not built as expected.")

    def test_vert_tri_dict_from_mesh(self):
        self.assertDictEqual(self.__class__._MeshDNE.vert_tri_dict, self.__class__._RefMeshDNE.vert_tri_dict, msg = "Vertex to polygon index dictionary not built as expected from reference mesh.")

    def test_get_edge_verts_from_mesh(self):
        self.assertTrue((self.__class__._MeshDNE.edgeverts == self.__class__._RefMeshDNE.edgeverts).all(), msg = "Array of vertex pairs forming polygon edges not built as expected from reference mesh.")
    
    def test_get_edge_verts_non_triangle_error(self):
        MeshDNE = deepcopy(self.__class__._MeshDNE)
        test_cases = [array([[]]), array([[0, 1, 2, 3]]), array([[0, 1]])]
        for test_case in test_cases:
            MeshDNE.Mesh.faces = test_case
            self.assertRaises(ValueError, MeshDNE._get_edge_verts)
            
    def test_get_boundary_faces_method(self):
        MeshDNE = deepcopy(self.__class__._MeshDNE)
        MeshDNE.Mesh.faces = array([[0, 1, 3], [1, 3, 4], [1, 2, 4], [3, 4, 5]])
        MeshDNE.Mesh.nvert = 6
        
        MeshDNE._get_vert_tri_dict()
        MeshDNE._get_edge_verts()
        MeshDNE._get_boundary_faces()
                
        self.assertListEqual(MeshDNE.boundary_faces, [0, 2, 3], msg = "List of boundary faces not built as expected.")

    def test_get_boundary_faces_from_mesh(self):
        self.assertListEqual(self.__class__._MeshDNE.boundary_faces, self.__class__._RefMeshDNE.boundary_faces, msg = "List of boundary faces not built as expected from reference mesh.")
    
    def test_get_boundary_faces_no_polygons(self):
        MeshDNE = deepcopy(self.__class__._MeshDNE)
        MeshDNE.Mesh.faces = array([])
        
        MeshDNE._get_edge_verts()
        MeshDNE._get_boundary_faces()
        
        self.assertListEqual(MeshDNE.boundary_faces, [], msg = "List of boundary faces not built as expected from empty mesh.")
    
    def test_energize_surface(self):
        pass

    def test_energy_function_method(self):
        MeshDNE = self.__class__._MeshDNE
        self.assertEqual(MeshDNE._energy(MeshDNE.Mesh.faces[1], 1), [6.276453180651151, 0.024020901165739069], msg = "Energy from polygon not calculated as expected.")
        
    def test_energy_function_high_cond_with_checking(self):
        MeshDNE = deepcopy(self.__class__._MeshDNE)
        MeshDNE.docondition = 1
        
        self.assertEqual(MeshDNE._energy(MeshDNE.Mesh.faces[5930], 5930), [0, 1], msg = "Calculation of energy from high condition-number polygon (with condition number checking) did not operate as expected.")
    
    def test_energy_function_high_cond_no_checking_error(self):
        MeshDNE = deepcopy(self.__class__._MeshDNE)
        MeshDNE.docondition = 0
        
        self.assertRaises(LinAlgError, MeshDNE._energy, MeshDNE.Mesh.faces[5930], 5930)
    
    def test_sum_dne_method(self):
        MeshDNE = deepcopy(self.__class__._MeshDNE)
        
        MeshDNE.dooutlier = 0
        MeshDNE.e = array(range(1,8))
        MeshDNE.facearea = array(range(2, 9))
        MeshDNE.boundary_faces = [1, 3, 4]
        
        MeshDNE._sumdne()
        
        self.assertEqual(MeshDNE.DNE, 112.0, msg = "Sum DNE method not calculating DNE as expected.")
        
        self.assertTrue((MeshDNE.equantity == array([2, 0, 12, 0, 0, 42, 56])).all(), msg = "Sum DNE method not calculating energy quantities as expected.")

    def test_bad_outlier_percentage_error(self):
        MeshDNE = deepcopy(self.__class__._MeshDNE)
        MeshDNE.outlierperc = 101.0
        
        self.assertRaises(ValueError, MeshDNE.calcdne)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()