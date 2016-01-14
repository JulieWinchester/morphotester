'''
Created on Jan 10, 2016

@author: Julia M. Winchester
'''
import unittest
import Morpho

from PyQt4.QtTest import QTest
from PyQt4.QtCore import Qt, QPoint

class Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._App = Morpho.MainWidget()
    
    def set_form_to_zero(self):
        App = self.__class__._App
        
        App.dnecheck.setChecked(0)
        App.rficheck.setChecked(0)
        App.opcrcheck.setChecked(0)
        App.openlabel.setText('')
        
        App.tab_widget.setCurrentIndex(0)
        
        App.DNEOptionsWindow.dneconditioncontrolcheck.setChecked(0)
        
        App.DNEOptionsWindow.outliervgroup.setChecked(0)
        App.DNEOptionsWindow.dneoutliertype1.setChecked(1)
        App.DNEOptionsWindow.dneoutlierval.setText('')
        
        App.DNEOptionsWindow.fairvgroup.setChecked(0)
        App.DNEOptionsWindow.dneiteration.setText('')
        App.DNEOptionsWindow.dnestepsize.setText('')
        
        App.DNEOptionsWindow.visvgroup.setChecked(0)
        App.DNEOptionsWindow.dnerelvischeck.setChecked(1)
        App.DNEOptionsWindow.dneabsmaxval.setText('')
        App.DNEOptionsWindow.dneabsminval.setText('')
        
        App.OPCROptionsWindow.visualizeopcrcheck.setChecked(0)
        App.OPCROptionsWindow.opcrminpatch.setText('')
        
    def test_defaults(self):
        App = Morpho.MainWidget()
        
        self.assertTrue(App.dnecheck.isChecked())
        self.assertTrue(App.rficheck.isChecked())
        self.assertTrue(App.opcrcheck.isChecked())
        self.assertEqual(App.openlabel.text(), '')
        
        self.assertTrue(App.DNEOptionsWindow.isHidden())
        
        self.assertTrue(App.DNEOptionsWindow.dneconditioncontrolcheck.isChecked())
        self.assertTrue(App.DNEOptionsWindow.outliervgroup.isChecked())
        self.assertTrue(App.DNEOptionsWindow.dneoutliertype1.isChecked())
        self.assertFalse(App.DNEOptionsWindow.dneoutliertype2.isChecked())
        self.assertEqual(App.DNEOptionsWindow.dneoutlierval.text(), '99.9')
        
        self.assertFalse(App.DNEOptionsWindow.fairvgroup.isChecked())
        self.assertEqual(App.DNEOptionsWindow.dneiteration.text(), '3')
        self.assertEqual(App.DNEOptionsWindow.dnestepsize.text(), '0.1')
        
        self.assertFalse(App.DNEOptionsWindow.visvgroup.isChecked())
        self.assertTrue(App.DNEOptionsWindow.dnerelvischeck.isChecked())
        self.assertFalse(App.DNEOptionsWindow.dneabsvischeck.isChecked())
        self.assertEqual(App.DNEOptionsWindow.dneabsmaxval.text(), '1.0')
        self.assertEqual(App.DNEOptionsWindow.dneabsminval.text(), '0.0')
        
        self.assertTrue(App.OPCROptionsWindow.isHidden())
        
        self.assertFalse(App.OPCROptionsWindow.visualizeopcrcheck.isChecked())
        self.assertEqual(App.OPCROptionsWindow.opcrminpatch.text(), '3')
        
        self.assertEqual(App.mayaviview.model, 0)
        
    def test_dnecheck(self):
        App = self.__class__._App
        self.set_form_to_zero()
        
        QTest.mouseClick(App.dnecheck, Qt.LeftButton, pos=QPoint(2, App.dnecheck.height()/2))
        self.assertTrue(App.dnecheck.isChecked())
        
    def test_rficheck(self):
        App = self.__class__._App
        self.set_form_to_zero()
        
        QTest.mouseClick(App.rficheck, Qt.LeftButton, pos=QPoint(2, App.rficheck.height()/2))
        self.assertTrue(App.rficheck.isChecked())
        
    def test_opcrcheck(self):
        App = self.__class__._App
        self.set_form_to_zero()
        
        QTest.mouseClick(App.opcrcheck, Qt.LeftButton, pos=QPoint(2, App.opcrcheck.height()/2))
        self.assertTrue(App.opcrcheck.isChecked())
    
    def test_main_window_show(self):
        App = self.__class__._App
        App.show()
        self.assertTrue(App.isVisible())
        
    def test_main_window_hide(self):
        App = self.__class__._App
        App.close()
        self.assertTrue(App.isHidden())
        
    def test_DNEOptionsWindow_show(self):
        App = self.__class__._App
        App.DNEOptionsWindow.show()
        self.assertTrue(App.DNEOptionsWindow.isVisible())
        
    def test_DNEOptionsWindow_close(self):
        App = self.__class__._App
        App.DNEOptionsWindow.close()
        self.assertTrue(App.DNEOptionsWindow.isHidden())
        
    def test_conditioncontrolcheck(self):
        App = self.__class__._App
        self.set_form_to_zero()
        
        QTest.mouseClick(App.DNEOptionsWindow.dneconditioncontrolcheck, Qt.LeftButton, pos=QPoint(2, App.DNEOptionsWindow.dneconditioncontrolcheck.height()/2))
        self.assertTrue(App.DNEOptionsWindow.dneconditioncontrolcheck.isChecked())
        
    def test_outlier_group(self):
        App = self.__class__._App
        self.set_form_to_zero()
        
        App.DNEOptionsWindow.outliervgroup.setChecked(1)
        self.assertTrue(App.DNEOptionsWindow.outliervgroup.isChecked())
        
        QTest.mouseClick(App.DNEOptionsWindow.dneoutliertype2, Qt.LeftButton, pos=QPoint(2, App.DNEOptionsWindow.dneoutliertype2.height()/2))
        self.assertTrue(App.DNEOptionsWindow.dneoutliertype2.isChecked())
        self.assertFalse(App.DNEOptionsWindow.dneoutliertype1.isChecked())
        
        QTest.keyClicks(App.DNEOptionsWindow.dneoutlierval, "10.0")
        self.assertEqual(App.DNEOptionsWindow.dneoutlierval.text(), "10.0")
        
    def test_implicit_fair_group(self):
        App = self.__class__._App
        self.set_form_to_zero()
        
        App.DNEOptionsWindow.fairvgroup.setChecked(1)
        self.assertTrue(App.DNEOptionsWindow.fairvgroup.isChecked())
        
        QTest.keyClicks(App.DNEOptionsWindow.dneiteration, "10")
        self.assertEqual(App.DNEOptionsWindow.dneiteration.text(), "10")
        
        QTest.keyClicks(App.DNEOptionsWindow.dnestepsize, "0.5")
        self.assertEqual(App.DNEOptionsWindow.dnestepsize.text(), "0.5")
        
    def test_visualization_group(self):
        App = self.__class__._App
        self.set_form_to_zero()
        
        App.DNEOptionsWindow.visvgroup.setChecked(1)
        self.assertTrue(App.DNEOptionsWindow.visvgroup.isChecked())
        
        QTest.mouseClick(App.DNEOptionsWindow.dneabsvischeck, Qt.LeftButton, pos=QPoint(2, App.DNEOptionsWindow.dneabsvischeck.height()/2))
        self.assertTrue(App.DNEOptionsWindow.dneabsvischeck.isChecked())
        self.assertFalse(App.DNEOptionsWindow.dnerelvischeck.isChecked())
        
        QTest.keyClicks(App.DNEOptionsWindow.dneabsmaxval, "100.0")
        self.assertEqual(App.DNEOptionsWindow.dneabsmaxval.text(), "100.0")
        
        QTest.keyClicks(App.DNEOptionsWindow.dneabsminval, "1.0")
        self.assertEqual(App.DNEOptionsWindow.dneabsminval.text(), "1.0")
        
    def test_OPCROptionsWindow_show(self):
        App = self.__class__._App
        App.OPCROptionsWindow.show()
        self.assertTrue(App.OPCROptionsWindow.isVisible())
    
    def test_OPCROptionsWindow_close(self):
        App = self.__class__._App
        App.OPCROptionsWindow.close()
        self.assertTrue(App.OPCROptionsWindow.isHidden())
        
    def test_visualizeopcrcheck(self):
        App = self.__class__._App
        self.set_form_to_zero()
        
        QTest.mouseClick(App.OPCROptionsWindow.visualizeopcrcheck, Qt.LeftButton, pos=QPoint(2, App. OPCROptionsWindow.visualizeopcrcheck.height()/2))
        self.assertTrue(App.OPCROptionsWindow.visualizeopcrcheck.isChecked())
        
    def test_opcrminpatch_lineedit(self):
        App = self.__class__._App
        self.set_form_to_zero()
        
        QTest.keyClicks(App.OPCROptionsWindow.opcrminpatch, "5")
        self.assertEqual(App.OPCROptionsWindow.opcrminpatch.text(), "5")
        
    def test_set_openlabel(self):
        App = self.__class__._App
        self.set_form_to_zero()
        
        App.openlabel.setText('Hello world')
        self.assertEqual(App.openlabel.text(), 'Hello world')
                        
    def test_process_surface_error(self):
        App = self.__class__._App
        self.set_form_to_zero()
        
        App.dnecheck.setChecked(1)
        self.assertRaises(App.ProcessSurface)
    
    def test_tabs(self):
        App = self.__class__._App
        self.set_form_to_zero()
        
        self.assertEqual(App.tab_widget.currentIndex(), 0)
        App.tab_widget.setCurrentIndex(1)
        self.assertEqual(App.tab_widget.currentIndex(), 1)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()