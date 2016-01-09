'''
Created on Dec 21, 2015

@author: Julia M. Winchester
'''
import unittest
import cPickle as pickle
import OPC
import math

from copy import copy


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open('./tests/testmeshThege58.pkl', 'rb') as input:
            cls._Mesh = pickle.load(input)
        with open('./tests/testmeshThege58opc.pkl', 'rb') as input:
            cls._RefMeshOPCR = pickle.load(input)
        cls._MeshOPCR = OPC.MeshOPCR(cls._Mesh, 5)

    def test_mesh_OPCR(self):
        self.assertEqual(76.5, self.__class__._MeshOPCR.OPCR, msg = "OPCR not calculated as expected from test mesh.")

    def test_mesh_initial_OPC(self):
        Mesh = self.__class__._Mesh
        self.assertEqual(79, self.__class__._MeshOPCR._get_opc(Mesh.vertices, Mesh.faces, Mesh.triverts)[0], msg = "Initial OPC value (mesh unrotated) not calculated as expected from test mesh.")

    def test_mesh_patches_list(self): # Might need extra data files to test this
        self.assertListEqual(self.__class__._RefMeshOPCR.patches_list, self.__class__._MeshOPCR.patches_list, msg = "Polygons not sorted into patches as expected during OPCR calculation.")
    
    def test_mesh_color_map_list(self): # Might need extra data files to test this
        a = self.__class__._RefMeshOPCR.colormap_list
        b = self.__class__._MeshOPCR.colormap_list
        self.assertTrue(all((x == y).all() for x, y in zip(a, b)), msg = "Polygons not sorted into orientation (color) groups as expected during OPCR calculation.")
       
    def test_mesh_OPC_list(self):
        self.assertListEqual([79, 80, 77, 72, 75, 75, 79, 75], self.__class__._MeshOPCR.opc_list, msg = "List of OPC values not calculated as expected from test mesh.")
    
    def test_centroid_shift(self):
        # Vertices for an origin-centered triangle
        centered_vertices = [[0.0, 2.0, -1.0], [1.0, -1.0, -1.0], [-1.0, -1.0, -1.0], [0.0, 0.0, 3.0]]
        # Vertices for triangle above after shift of [1, 2, 3]
        shifted_vertices = [[1.0, 4.0, 2.0], [2.0, 1.0, 2.0], [0.0, 1.0, 2.0], [1.0, 2.0, 6.0]]
        self.assertTrue((centered_vertices == self.__class__._MeshOPCR._centermesh(shifted_vertices)).all(), msg = "Mesh centering not performing as expected.")

    def test_vert_tri_dict(self):
        self.assertDictEqual(self.__class__._RefMeshOPCR.vert_tri_dict, self.__class__._MeshOPCR.vert_tri_dict, msg = "Vertex to polygon dictionary not generated as expected during OPCR calculation.")

    def test_mesh_rotation(self):
        MeshOPCR = copy(self.__class__._MeshOPCR)
        MeshOPCR.MeshRotated = copy(MeshOPCR.Mesh)
        MeshOPCR.theta = math.radians(0)
        MeshOPCR._rotatemesh()
        self.assertTrue((MeshOPCR.Mesh.vertices == MeshOPCR.MeshRotated.vertices).all(), msg = "Mesh rotation not performing as expected when theta equals zero degrees.")
        
        MeshOPCR.theta = math.radians(5.625)
        for i in range(1, MeshOPCR.n_rotations):
            MeshOPCR._rotatemesh()
        self.assertTrue((self.__class__._MeshOPCR.MeshRotated.vertices == MeshOPCR.MeshRotated.vertices).all(), msg = "Mesh rotation not performing as expected when theta equals 39.375 degrees.")

    def test_xy_degrees(self):
        vectors = [(0,0), (0,1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
        degrees = [0.0, 0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0]
        for vector, degree in zip(vectors, degrees):
            self.assertEqual(self.__class__._MeshOPCR._xydegrees(vector[0],vector[1]), degree, msg = "Degrees between vector from origin and positive X-axis not calculated as expected. Vector is Y = %s X = %s and degrees should be %s." % (vector[0], vector[1], degree))
    
    def test_sort_to_colors(self):
        colorlist = ['#FF0000','#964B00','#FFFF00','#00FFFF','#0000FF','#90EE90','#014421','#FFC0CB']
        edges = [337.5, 22.5, 67.5, 112.5, 157.5, 202.5, 247.5, 292.5]
        middles = [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0]
        for i, edge in enumerate(edges):
            self.assertEqual(self.__class__._MeshOPCR._sort_to_colors(edge), colorlist[i], msg = "Sorting of degrees to color groups not behaving as expected for %s degrees (boundary of color group), color group should be %s." % (edge, colorlist[i]))
        for i, middle in enumerate(middles):
            self.assertEqual(self.__class__._MeshOPCR._sort_to_colors(middle), colorlist[i], msg = "Sorting of degrees to color groups not behaving as expected for %s degrees (middle of color group), color group should be %s." % (middle, colorlist[i]))
        self.assertEqual(self.__class__._MeshOPCR._sort_to_colors(360.0), colorlist[0], msg = "Sorting of degrees to color groups not behaving as expected for 360 degrees (middle of color group), color group should be #FF0000.")
        
    def test_pair_faces(self):
        test_cases = [[0,1,2], [0,0], [0,0,1]]
        solutions = [[(0, 1), (0, 2), (1, 2)], [], [(0,1)]]
        for test_case, solution in zip(test_cases, solutions):
            self.assertListEqual(self.__class__._MeshOPCR._pair_faces(test_case), solution, msg = "Pairing of values not behaving as expected.")

    def test_adjacent_face_pairing(self):
        no_shared_vertex_case = {}
        one_shared_vertex_case = {0: [(1,2)]}
        one_shared_edge_case = {0: [(1, 2)], 1: [(1, 2), (2, 3), (1, 3)], 2: [(2, 3)]}
        test_cases = [no_shared_vertex_case, one_shared_vertex_case, one_shared_edge_case]
        solutions = [[], [], [(1, 2), (2, 3)]]
        for test_case, solution in zip(test_cases, solutions):
            self.assertListEqual(self.__class__._MeshOPCR._adjacent_face_pairs(test_case), solution, msg = "Pairing of adjacent polygons not operating as expected." ) 

    def test_patch_building(self):
        no_polygons_case = []
        no_polygons_solution = []
        
        two_adjacent_polygons_case = [[1,2]]
        two_adjacent_polygons_solution = [set([1, 2])]
        
        two_patches_case = [[1, 2], [3, 4]]
        two_patches_solution = [set([1, 2]), set([3, 4])]
        
        three_patches_case = [[1, 2], [3, 4], [5, 6]]
        three_patches_solution = [set([1, 2]), set([3, 4]), set([5, 6])]
        
        two_patches_clump_case = [[1,2], [3, 4], [5,6], [2, 3]]
        two_patches_clump_solution = [set([1, 2, 3, 4]), set([5, 6])]
        
        test_cases = [no_polygons_case, two_adjacent_polygons_case, two_patches_case, three_patches_case, two_patches_clump_case]
        solutions = [no_polygons_solution, two_adjacent_polygons_solution, two_patches_solution, three_patches_solution, two_patches_clump_solution]
        
        for test_case, solution in zip(test_cases, solutions):
            self.assertListEqual(self.__class__._MeshOPCR._build_patches(test_case), solution, msg = "Patches not clumped from adjacent polygons as expected.")

    def test_small_patch_culling(self):
        test_case = [set([1, 2, 3, 4]), set([5, 6])]
        self.assertListEqual(self.__class__._MeshOPCR._cull_small_patches(test_case, 3), [set([1, 2, 3, 4])], msg = "Small patch culling not behaving as expected.")
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()