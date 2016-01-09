'''
Created on Jan 9, 2016

@author: Julia M. Winchester
'''
import unittest
import normcore

from numpy import array, allclose

class Test(unittest.TestCase):

    def test_normal(self):
        plane = array([[ 166.585,  918.653,  935.901], [ 611.921,  676.73 ,  417.434], [ 137.632,  619.804,   83.351]])
        self.assertTrue(allclose(normcore.normal(plane), array([51308.109167, 394682.381851, -140092.614883])), msg = "Normal vector not calculated as expected.")
        
    def test_normal_identical_vertices(self):
        plane = array([[ 166.585,  918.653,  935.901], [ 166.585,  918.653,  935.901], [ 137.632,  619.804,   83.351]])
        self.assertTrue((normcore.normal(plane) == array([0.0, 0.0, 0.0])).all(), msg = "Non-zero normal vector unexpectedly returned for plane with duplicate vertices.")

    def test_normalize(self):
        normal = array([[51308.109167, 394682.381851, -140092.614883]])
        self.assertTrue(allclose(normcore.normalize(normal), array([[0.12160073, 0.93540119, -0.3320209]])), msg = "Vector not normalized as expected.")
    
    def test_normalize_error(self):
        self.assertRaises(ValueError, normcore.normalize, array([0.0, 0.0, 0.0]))
        self.assertRaises(ValueError, normcore.normalize, array([[0.0, 0.0]]))
        self.assertRaises(ValueError, normcore.normalize, array([[0.0, 0.0, 0.0, 0.0]]))
        self.assertRaises(ValueError, normcore.normalize, array([[]]))
    
    def test_normalmap(self):
        varray = array([[0.0, 0.0, 0.0],
                        [2.0, 0.0, 0.0],
                        [0.0, 2.0, 0.0],
                        [2.0, 2.0, 0.0],
                        [1.0, 1.0, 2.0]])
        farray = array([[0, 1, 2],
                        [1, 3, 2],
                        [0, 1, 4],
                        [1, 3, 4],
                        [2, 0, 4],
                        [3, 2, 4]])
        solution_norms = array([[ 0.0,  0.0,  4.0],
                                [ 0.0, -0.0,  4.0],
                                [ 0.0, -4.0,  2.0],
                                [ 4.0, -0.0,  2.0],
                                [-4.0,  0.0,  2.0],
                                [ 0.0,  4.0,  2.0]])
        
        self.assertTrue((normcore.normalmap(varray, farray) == solution_norms).all(), msg = "Normal map not generated as expected for reference pyramid mesh.")
    
    def test_computenormal(self):
        varray = array([[0.0, 0.0, 0.0],
                        [2.0, 0.0, 0.0],
                        [0.0, 2.0, 0.0],
                        [2.0, 2.0, 0.0],
                        [1.0, 1.0, 2.0]])
        farray = array([[0, 1, 2],
                        [1, 3, 2],
                        [0, 1, 4],
                        [1, 3, 4],
                        [2, 0, 4],
                        [3, 2, 4]])
        
        fvarray = [varray[verts] for verts in farray]
        
        vfarray = {0: [0, 2, 4], 1: [0, 1, 2, 3], 2: [0, 1, 4, 5], 3: [1, 3, 5], 4: [2, 3, 4, 5]}
        
        solution_normals = [array([[-0.3926533 , -0.3926533 ,  0.83165304],
                                   [ 0.28315849, -0.28315849,  0.91632011],
                                   [-0.28315849,  0.28315849,  0.91632011],
                                   [ 0.3926533 ,  0.3926533 ,  0.83165304],
                                   [ 0.0       ,  0.0       ,  1.0       ]]), 
                            array([[ 0.0       ,  0.0       ,  1.0       ],
                                   [ 0.0       ,  0.0       ,  1.0       ],
                                   [ 0.0       , -0.89442719,  0.4472136 ],
                                   [ 0.89442719,  0.0       ,  0.4472136 ],
                                   [-0.89442719,  0.0       ,  0.4472136 ],
                                   [ 0.0       ,  0.89442719,  0.4472136 ]])]
        
        test_normals = normcore.computenormal(varray, farray, fvarray, vfarray)
        
        self.assertTrue(allclose(test_normals[0], solution_normals[0]), msg = "Approximated vertex normals not calculated as expected from reference pyramid mesh.")
        self.assertTrue(allclose(test_normals[1], solution_normals[1]), msg = "Polygon face normals not calculated as expected from reference pyramid mesh.")
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()