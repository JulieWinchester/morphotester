'''
Created on Jun 17, 2012

This module activates MorphoTester, a scientific computing application for measuring
topographic shape of 3D anatomical data. It should be run as a script from the 
command line. It contains the application GUI and calls subsequent modules plython, DNE, RFI, and OPCR. 

@author: Julia M. Winchester
'''

import os
os.environ['ETS_TOOLKIT'] = 'qt4'
os.environ['QT_API'] = 'pyqt'

import sip
sip.setapi('QString', 2)

from numpy import array
from traits.api import HasTraits, Instance
from traitsui.api import View, Item
from mayavi.core.ui.api import MlabSceneModel
from tvtk.pyface.scene_editor import SceneEditor
from PyQt4 import QtGui

import plython
import DNE
import RFI
import OPC
import sys

class MayaviView(HasTraits):    
    scene = Instance(MlabSceneModel, ())
    
    # The layout of the panel created by Traits
    view = View(Item('scene', editor=SceneEditor(), resizable=True, show_label=False), resizable=True)
    
    def __init__(self, model, clearscreen,colortriplet):
        HasTraits.__init__(self)
        # Create some data, and plot it using the embedded scene's engine
        
        if clearscreen == 1:
            self.plot = self.scene.mlab.clf()
        
        if model == 0:
            self.plot = self.scene.mlab.points3d(0,0,0,opacity=0.0)
        else:
            triangles = model[2]
            x, y, z = model[0][:,0], model[0][:,1], model[0][:,2],
                            
            if colortriplet == 0:
                self.plot = self.scene.mlab.triangular_mesh(x, y, z, triangles)
                    
            else: # Currently unused, but could allow for imposing alternate color schemes on mesh
                self.plot = self.scene.mlab.triangular_mesh(x, y, z, triangles)
    
    def VisualizeOPCR(self,hexcolormap,facelength):
        strdictb = {'#000000': 0.0, '#FF0000': 0.167, '#964B00': 0.278, '#FFFF00': 0.388, '#00FFFF': 0.5, '#0000FF': 0.612, '#90EE90': 0.722, '#014421': 0.833, '#FFC0CB': 1.0}
        strdict =  {'#FF0000': 0.0, '#964B00': 0.188, '#FFFF00': 0.314, '#00FFFF': 0.439, '#0000FF': 0.536, '#90EE90': 0.686, '#014421': 0.812, '#FFC0CB': 1.0}
        
        if "#000000" in hexcolormap:
            opcrcolorscalars = array([strdictb[key] for key in hexcolormap])
            
            colors = [(0,0,0,255),(255,0,0,255),(150,75,0,255),(255,255,0,255),(0,255,255,255),(0,0,255,255),(144,238,144,255),(1,68,33,255),(255,192,203,255)]
            arclen = [28,29,28,28,29,28,28,29,28]
            
            opcrcolorlut = [colors[i] for i in range(9) for j in range(arclen[i])]

        else:
            opcrcolorscalars = array([strdict[key] for key in hexcolormap])

            colors = [(255,0,0,255),(150,75,0,255),(255,255,0,255),(0,255,255,255),(0,0,255,255),(144,238,144,255),(1,68,33,255),(255,192,203,255)]
            arclen = [32,32,32,32,31,32,32,32]
            opcrcolorlut = [colors[i] for i in range(8) for j in range(arclen[i])]
        
        cell_data = self.plot.mlab_source.dataset.cell_data
        cell_data.scalars = opcrcolorscalars
        cell_data.scalars.name = 'Cell data'
        cell_data.update()
                
        self.plot2 = self.scene.mlab.pipeline.set_active_attribute(self.plot, cell_scalars='Cell data')
                
        self.plot3 = self.scene.mlab.pipeline.surface(self.plot2)
        
        self.scene.mlab.show()
                
        self.plot3.module_manager.scalar_lut_manager.lut.table = opcrcolorlut
        self.scene.mlab.draw()
        
        return 0         
        
class OutLog:
    def __init__(self, edit, out=None, color=None):
        """(edit, out=None, color=None) -> can write stdout, stderr to a
        QTextEdit.
        edit = QTextEdit
        out = alternate stream ( can be the original sys.stdout )
        color = alternate color (i.e. color stderr a different color)
        """
        self.edit = edit
        self.out = None
        self.color = color

    def write(self, m):
        if self.color:
            tc = self.edit.textColor()
            self.edit.setTextColor(self.color)

        self.edit.moveCursor(QtGui.QTextCursor.End)
        self.edit.insertPlainText( m )

        if self.color:
            self.edit.setTextColor(tc)

        if self.out:
            self.out.write(m)

class MainWidget(QtGui.QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        
        self.initUI()
        
    def initUI(self):
        # Open File and Directory Buttons
        self.openbutton = QtGui.QPushButton("Open File")
        self.opendirbutton = QtGui.QPushButton("Open Directory")
        
        # Tabs for shape metrics and mesh tools
        self.tab_widget = QtGui.QTabWidget()
        
        self.tab1 = QtGui.QWidget()
        self.tab1layout = QtGui.QGridLayout()
        self.tab1layout.setSpacing(10)
        self.tab1.setLayout(self.tab1layout)
        
        self.tab2 = QtGui.QWidget()
        self.tab2layout = QtGui.QGridLayout()
        self.tab2layout.setSpacing(10)
        self.tab2.setLayout(self.tab2layout)
        
        self.tab_widget.addTab(self.tab1, "Shape metrics")
        self.tab_widget.addTab(self.tab2, "Mesh tools")
        
        # Metric toggles and options windows
        self.dnecheck = QtGui.QCheckBox("DNE")
        self.dnecheck.toggle()
        self.dnebutton = QtGui.QPushButton("Options")
        
        self.rficheck = QtGui.QCheckBox("RFI")
        self.rficheck.toggle()
        
        self.opcrcheck = QtGui.QCheckBox("OPCR")
        self.opcrcheck.toggle()
        self.opcrbutton = QtGui.QPushButton("Options")
        
        # Topography calculations buttons
        self.calcfilebutton = QtGui.QPushButton("Process File")
        self.calcdirbutton = QtGui.QPushButton("Process Directory")
        
        self.openlabel = QtGui.QLabel("") # This should be moved

        # DNE options submenu
        self.dneimplicitfaircheck = QtGui.QCheckBox("DNE Implicit Fairing Smooth")
        self.dneiterationlabel = QtGui.QLabel("Iterations")
        self.dneiteration = QtGui.QLineEdit("3")
        self.dnestepsizelabel = QtGui.QLabel("Step size")
        self.dnestepsize = QtGui.QLineEdit("0.1")
        self.dnedooutlierremovalcheck = QtGui.QCheckBox("0.1% Outlier Removal")
        self.dneconditioncontrolcheck = QtGui.QCheckBox("Condition number checking")
        self.dneconditioncontrolcheck.toggle()
        
        # OPCR options submenu
        self.visualizeopcrcheck = QtGui.QCheckBox("Visualize Patches")
        self.opcrlabel = QtGui.QLabel("Minimum Patch Count")
        self.opcrminpatch = QtGui.QLineEdit("3")
        
        # Contents of mesh tools tab
        self.toolslabel = QtGui.QLabel("Mesh tools coming soon.")
        
        # Output log
        self.morpholog = QtGui.QTextEdit()
        self.morpholog.setReadOnly(1)
        
        # 3D view
        self.mayaviview = MayaviView(0,1,0)
        self.threedview = self.mayaviview.edit_traits().control
        
        # GUI behavior
        # Open buttons
        self.openbutton.clicked.connect(self.OpenFileDialog)
        self.opendirbutton.clicked.connect(self.OpenDirDialog)

        # Process mesh and directory buttons
        self.calcfilebutton.clicked.connect(self.CalcFile)
        self.calcdirbutton.clicked.connect(self.CalcDir)
        
        # Options submenu buttons
        self.dnebutton.clicked.connect(self.DNEOptionsPopUp)
        self.opcrbutton.clicked.connect(self.OPCROptionsPopUp)
        
        # UI grid layout
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        
        grid.addWidget(self.openbutton, 0, 0)
        grid.addWidget(self.openlabel, 1, 0)
        grid.addWidget(self.opendirbutton, 0, 1)

        grid.addWidget(self.tab_widget, 2, 0, 14, 2)

        self.tab1layout.addWidget(self.dnecheck, 0, 0)
        self.tab1layout.addWidget(self.dnebutton, 0, 1)
        self.tab1layout.addWidget(self.rficheck, 1, 0)
        self.tab1layout.addWidget(self.opcrcheck, 2, 0)
        self.tab1layout.addWidget(self.opcrbutton, 2, 1)
        
        self.tab1layout.addWidget(self.calcfilebutton, 10,0)
        self.tab1layout.addWidget(self.calcdirbutton, 10,1)
        
        self.tab2layout.addWidget(self.toolslabel, 0, 0)
        
        grid.addWidget(self.morpholog, 16, 0, 2, 4)
        grid.addWidget(self.threedview, 0, 2, 16, 2)
        
        self.setLayout(grid)
        
        self.sizeHint()
        self.setWindowTitle('MorphoTester')
        
        sys.stdout = OutLog(self.morpholog, sys.stdout)
        sys.stderr = OutLog(self.morpholog, sys.stderr, QtGui.QColor(255,0,0))
         
    def OpenFileDialog(self):
        print "Opening file..."
        filepath = QtGui.QFileDialog.getOpenFileName(self, 'Open File', '/')
        
        filename = os.path.split(filepath)[1]
        
        self.openlabel.setText(filename)
        self.mesh = plython.createarray(filepath)
        self.meshfacenumber = len(self.mesh[2])
        self.mayaviview = MayaviView(self.mesh,1,0)
        print "File open!"
        
    def OpenDirDialog(self):
        print "Opening directory..."
        self.dirpath = QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', '/')
        self.openlabel.setText(".."+self.dirpath[-20:])
        self.mayaviview = MayaviView(0,1,0)
           
    def ProcessSurface(self):
        dtaresult = [" "," "," "," "," "," "," "," "," "]
        if self.dnecheck.isChecked() == 1:
            print "Calculating DNE..."
            dneresult = DNE.calcdne(self.mesh, self.dneimplicitfaircheck.isChecked(), self.dneconditioncontrolcheck.isChecked(), self.dneiteration.text(), self.dnestepsize.text(), self.dnedooutlierremovalcheck.isChecked())
            if dneresult == "!":
                print "DNE could not be calculated due to cholesky factorization error."
                dtaresult[0] = "N/A (cholesky error)"
            else: 
                print "DNE calculated."
                dtaresult[0] = str(round(dneresult,3))
                print "DNE = " + dtaresult[0]
            
        if self.rficheck.isChecked() == 1:
            print "Calculating RFI..."
            rfiresult = RFI.calcrfi(self.mesh)
            print "RFI calculated."
            dtaresult[1:3] = str(round(rfiresult[0],3)), str(round(rfiresult[2],3)), str(round(rfiresult[3],3))
            print "RFI (surface area / outline area) = " + dtaresult[1]
            print "Surface area = " + dtaresult[2]
            print "Outline area = " + dtaresult[3]
            
        if self.opcrcheck.isChecked() == 1:
            print "Calculating OPCR..."
            opcrresult = OPC.calcopcr(self.mesh, self.opcrminpatch.text())
            print "OPCR Calculated!"
            dtaresult[4] = str(round(opcrresult[0],3))
            dtaresult[5:7] = [0,1,2] # Unused but could be expanded to pass more information about OPCR
            dtaresult[8] = opcrresult[2]
            print "OPCR = " + dtaresult[4]
            
        return dtaresult
        
    def CalcFile(self):     
        if self.dnecheck.isChecked() == 0 and self.rficheck.isChecked() == 0 and self.opcrcheck.isChecked() == 0:
            print "No topographic variables have been selected for analysis."
            return
        
        dtaresult = self.ProcessSurface()
        
        print "\n--------------------\n"   
        print "RESULTS"
        print "File name: " + self.openlabel.text()
        print "Mesh face number: " + str(self.meshfacenumber)
        if self.dnecheck.isChecked() == 1:
            print "DNE: " + dtaresult[0]
        if self.rficheck.isChecked() == 1:
            print "RFI: " + dtaresult[1]
            print "Surface area: " + dtaresult[2]
            print "Outline area: " + dtaresult[3]           
        if self.opcrcheck.isChecked() == 1:
            print "OPCR: " + dtaresult[4]
        print "\n--------------------"
        if self.visualizeopcrcheck.isChecked() == 1:
            MayaviView.VisualizeOPCR(self.mayaviview,dtaresult[8],len(self.mesh[2]))
        
    def CalcDir(self):        
        if self.dnecheck.isChecked() == 0 and self.rficheck.isChecked() == 0 and self.opcrcheck.isChecked() == 0:
            print "No topographic variables have been selected for analysis."
            return
      
        resultsfile = open(os.path.join(self.dirpath,'morphoresults.txt'),'w')
        resultsfile.write("Filename\tMesh Face Number\tDNE\tRFI\tSurface Area\tOutline Area\tOPCR\n")
           
        for filename in os.listdir(self.dirpath):
            if filename[-3:] == "ply":
                print "Processing " + filename + "..."
                self.mesh = plython.createarray(os.path.join(self.dirpath,filename))
                self.meshfacenumber = len(self.mesh[2])
                fileresult = self.ProcessSurface()
                resultsfile.write(filename+"\t"+ str(self.meshfacenumber) + "\t" + fileresult[0]+"\t"+fileresult[1]+"\t"+fileresult[2]+"\t"+fileresult[3]+"\t"+fileresult[4]+"\n")
                print "\n--------------------\n"
            else:
                print filename + "does not have a .ply extension, skipping to next file."
        resultsfile.close()
        
    def DNEOptionsPopUp(self):
        child = DNEOptionsWindow(self)
        child.show()

    def OPCROptionsPopUp(self):
        child = OPCROptionsWindow(self)
        child.show()
      
class DNEOptionsWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super(DNEOptionsWindow, self).__init__(parent)
        
        self.OKbutton = QtGui.QPushButton("OK")
        self.OKbutton.clicked.connect(self.OKClose)
        
        self.layout = QtGui.QVBoxLayout()
        self.layout.setSpacing(10)
        
        self.hbox = QtGui.QHBoxLayout()
        self.hbox.addWidget(parent.dneiterationlabel)
        self.hbox.addWidget(parent.dneiteration)
        self.hboxwidget = QtGui.QWidget()
        self.hboxwidget.setLayout(self.hbox)
        
        self.hbox2 = QtGui.QHBoxLayout()
        self.hbox2.addWidget(parent.dnestepsizelabel)
        self.hbox2.addWidget(parent.dnestepsize)
        self.hbox2widget = QtGui.QWidget()
        self.hbox2widget.setLayout(self.hbox2)
        
        self.layout.addWidget(parent.dnedooutlierremovalcheck)
        self.layout.addWidget(parent.dneconditioncontrolcheck)
        self.layout.addWidget(parent.dneimplicitfaircheck)
        
        self.layout.addWidget(self.hboxwidget)
        self.layout.addWidget(self.hbox2widget)
        self.layout.addWidget(self.OKbutton) 
        self.setLayout(self.layout)
        
        self.setWindowTitle('DNE Options')
        
    def OKClose(self):
        self.close()
        
class OPCROptionsWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super(OPCROptionsWindow, self).__init__(parent)
           
        self.OKbutton = QtGui.QPushButton("OK")
        self.OKbutton.clicked.connect(self.OKClose)
        
        self.layout = QtGui.QVBoxLayout()
        self.layout.setSpacing(10)
        
        self.hbox = QtGui.QHBoxLayout()
        self.hbox.addWidget(parent.opcrlabel)
        self.hbox.addWidget(parent.opcrminpatch)
        self.hboxwidget = QtGui.QWidget()
        self.hboxwidget.setLayout(self.hbox)
        
        self.layout.addWidget(parent.visualizeopcrcheck)
        self.layout.addWidget(self.hboxwidget)
        self.layout.addWidget(self.OKbutton)
        self.setLayout(self.layout)
        
        self.setWindowTitle('OPCR Options') 
        
    def OKClose(self):
        self.close()              

if __name__ == "__main__":        
    
    window = MainWidget()
    window.show()
    QtGui.qApp.exec_()
    