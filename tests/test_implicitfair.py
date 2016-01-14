'''
Created on Jan 10, 2016

@author: Moocow
'''
import unittest
import implicitfair

import cPickle as pickle

from collections import defaultdict
from numpy import array, allclose

class Test(unittest.TestCase):


    def test_mesh_smooth(self):
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
        
        vfarray = {0: [0, 2, 4], 1: [0, 1, 2, 3], 2: [0, 1, 4, 5], 3: [1, 3, 5], 4: [2, 3, 4, 5]}

        solution_smoothed_vertices = array([[ 0.68411383,  0.68411383,  0.26803399],
                                            [ 1.31588617,  0.68411383,  0.26803399],
                                            [ 0.68411383,  1.31588617,  0.26803399],
                                            [ 1.31588617,  1.31588617,  0.26803399],
                                            [ 1.        ,  1.        ,  0.92786405]])
        
        test_smoothed_vertices = implicitfair.smooth(varray, farray, 3, 0.1, vfarray)
        
        self.assertTrue(allclose(test_smoothed_vertices, solution_smoothed_vertices), msg = "Reference pyramid mesh not smoothed as expected.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_mesh_smooth']
    unittest.main()