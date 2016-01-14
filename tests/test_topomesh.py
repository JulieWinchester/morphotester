'''
Created on Jan 10, 2016

@author: Julia M. Winchester
'''
import unittest
import topomesh

from copy import deepcopy

class Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._TopoMesh = topomesh.TopoMesh('./tests/Thege58.ply')
        cls._EmptyMesh = topomesh.TopoMesh('')
            
    def test_no_mesh_init(self):
        em = self.__class__._EmptyMesh
        
        variables = [em.DNE, em.DNEscalars, em.conditionfaces, em.boundaryfaces, em.outlierfaces, em.RFI, em.surfarea, em.projarea,
                     em.linelen, em.bluepixie, em.redpixie, em.pixelratio, em.OPCR, em.OPClist, em.OPCscalars]
        
        values = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
        
        self.assertListEqual(variables, values)

    def test_check_for_mesh_error(self):
        self.assertRaises(ValueError, self.__class__._EmptyMesh.check_for_mesh)
    
    def test_no_mesh_generate_DNE(self):
        self.assertRaises(ValueError, self.__class__._EmptyMesh.GenerateDNE, 0, 3, 0.1, 1, 1, 99.9, 1)
    
    def test_no_mesh_generate_RFI(self):
        self.assertRaises(ValueError, self.__class__._EmptyMesh.GenerateRFI)
    
    def test_no_mesh_generate_OPCR(self):
        self.assertRaises(ValueError, self.__class__._EmptyMesh.GenerateOPCR, 5)
    
    def test_mesh_init(self):
        TopoMesh = self.__class__._TopoMesh
        
        variables = [TopoMesh.DNE, TopoMesh.DNEscalars, TopoMesh.conditionfaces, TopoMesh.boundaryfaces, TopoMesh.outlierfaces, 
                     TopoMesh.RFI, TopoMesh.surfarea, TopoMesh.projarea, TopoMesh.linelen, TopoMesh.bluepixie, TopoMesh.redpixie, 
                     TopoMesh.pixelratio, TopoMesh.OPCR, TopoMesh.OPClist, TopoMesh.OPCscalars]
        
        values = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
        
        self.assertListEqual(variables, values)
    
    def test_check_for_mesh_no_error(self):
        self.assertTrue(self.__class__._TopoMesh.check_for_mesh() is None)

    def test_mesh_generate_DNE(self):
        TopoMesh = deepcopy(self.__class__._TopoMesh)
        
        TopoMesh.GenerateDNE(0, 3, 0.1, 1, 1, 99.9, 1)
        
        self.assertEqual(TopoMesh.DNE, 247.938)
        self.assertListEqual(TopoMesh.conditionfaces, [[0, 57378265.013361663], [4, 890184874.13861871], 
                                                       [73, 1343571530.4271412], [5930, 11908732518877564.0], 
                                                       [8778, 4936522.7463389486]])
        self.assertListEqual(TopoMesh.outlierfaces, [[2475, 0.51255744024860683, 0.014741217694888389], 
                                                     [2519, 0.38355601590466476, 0.017083805975653673], 
                                                     [2549, 0.4939614798581129, 0.020016113375423021], 
                                                     [2606, 0.7033905146290047, 0.014266472900058344], 
                                                     [2645, 0.48016566118746151, 0.013878160242070335], 
                                                     [2785, 0.47610433202634916, 0.010602689149740415], 
                                                     [5126, 0.5120896168145993, 0.01564295561914459], 
                                                     [5127, 0.56703207743985229, 0.019506596248359646], 
                                                     [5146, 0.7127229465900683, 0.02282972677513475], 
                                                     [8146, 0.406920260553499, 0.015469911584343965], 
                                                     [8207, 0.39196464438448075, 0.021731371329794746]])
    
    def test_mesh_generate_RFI(self):
        TopoMesh = deepcopy(self.__class__._TopoMesh)
        
        TopoMesh.GenerateRFI()
        
        variables = [TopoMesh.RFI, TopoMesh.surfarea, TopoMesh.projarea, TopoMesh.linelen, TopoMesh.bluepixie, TopoMesh.redpixie, TopoMesh.pixelratio]
        
        values = [2.178, 213.537, 98.056, 14.914499999999999, 101564, 480, 32.183445640148854]
        
        for variable, value in zip(variables, values):
            self.assertEqual(variable, value)
        
    def test_mesh_generate_OPCR(self):
        TopoMesh = deepcopy(self.__class__._TopoMesh)
        
        TopoMesh.GenerateOPCR(5)
        
        self.assertEqual(TopoMesh.OPCR, 76.5)
        self.assertListEqual(TopoMesh.OPClist, [79, 80, 77, 72, 75, 75, 79, 75])

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()