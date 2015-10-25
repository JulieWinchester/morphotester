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

import sys
import sip
sip.setapi('QString', 2)

from numpy import array, amax, amin, rint, empty, nan, isfinite
from traits.api import HasTraits, Instance
from traitsui.api import View, Item
from mayavi.core.ui.api import MlabSceneModel
from tvtk.pyface.scene_editor import SceneEditor
from PyQt4 import QtGui

import plython
import DNE
import RFI
import OPC

class MayaviView(HasTraits):    
    scene = Instance(MlabSceneModel, ())
    
    # The layout of the panel created by Traits
    view = View(Item('scene', editor=SceneEditor(), resizable=True, show_label=False), resizable=True)
    
    def __init__(self, model, clearscreen,colortriplet):
        HasTraits.__init__(self)
        # Create some data, and plot it using the embedded scene's engine
        
        self.model = model
        self.VisualizeMesh(model,clearscreen,colortriplet)
        
    def VisualizeMesh(self, model, clearscreen, colortriplet):
        if clearscreen == 1:
            self.plot = self.scene.mlab.clf()
        
        if model == 0:
            self.plot = self.scene.mlab.points3d(0,0,0,opacity=0.0)
        else:
            triangles = model[2]
            x, y, z = model[0][:,0], model[0][:,1], model[0][:,2],
                            
            
            self.plot = self.scene.mlab.triangular_mesh(x, y, z, triangles)
                    
        return self.plot

    def Interpolate(self, i, j, steps):
        onestep = steps+1
        ijrange = j.astype(float) - i.astype(float)
        fillarray = rint(array([ijrange/(onestep)*s+i.astype(float) for s in range(onestep)[1:]]))
        if (fillarray < 0).any():
            fillarray = array([abs(x[::-1]) if (x < 0).any() else x for x in fillarray.T]).T
        return fillarray
        
    def RelativeLut(self, lut, lmin, lmax): # Original 255-length LUT, proportion of min and max to stretch out
        cutlut = lut[int(round(lmin*255)):int(round(lmax*255))] # Cuts original LUT into a section between min and max
        newlut = empty([len(lut), 4]) # New null LUT of 255 length
        newlut[:] = nan
        for i, nugget in enumerate(cutlut): # Takes each entry in the subset of the original LUT...
            newlut[int(float((len(lut)-1))/float((len(cutlut)-1))*float(i))] = nugget # ... and evenly spaces them within the new null LUT 
        somelut = [i for i, x in enumerate(newlut) if isfinite(x).all()] # Indices of non-null entries in newlut
        pairlut = zip(somelut[:-1], somelut[1:]) # Pairs of non-null newlut entries as so - 1,2; 2,3; 3,4; for filling in between
        for pair in pairlut: # This is going to fill in the null entries between pairs with interpolated values
            if pair[1]-pair[0]-1 < 1:
                continue
            newlut[pair[0]+1:pair[1]] = self.Interpolate(newlut[pair[0]], newlut[pair[1]], (pair[1]-pair[0]-1)) 
        return newlut
    
    def VisualizeScalars(self, scalars, customlut=None, scale='linear', colorbar=1):
        self.visplot = self.VisualizeMesh(self.model,1,0)
        
        cell_data = self.visplot.mlab_source.dataset.cell_data
        cell_data.scalars = scalars
        cell_data.scalars.name = 'Cell data'
        cell_data.update()
        
        self.visplot2 = self.scene.mlab.pipeline.set_active_attribute(self.visplot, cell_scalars='Cell data')
        self.visplot3 = self.scene.mlab.pipeline.surface(self.visplot2)
        
        if customlut is None:
            self.visplot3.module_manager.scalar_lut_manager.lut_mode = 'blue-red'
        else:
            self.visplot3.module_manager.scalar_lut_manager.lut.table = customlut
            
        self.visplot3.module_manager.scalar_lut_manager.lut.scale = scale    
        
        if colorbar:    
            self.scene.mlab.colorbar(object=self.visplot3, orientation='vertical')
        
        self.scene.mlab.draw()

        return self.visplot3
         
    def VisualizeDNE(self, edens, isrelative, absmin, absmax):    
        # For visualizing on log scale, transforms all 0 values (boundary and outlier faces) to lowest non-zero energy on polygon
        apple = sorted(set(edens))[1]
        eve = [apple if x == 0 else x for x in edens]
        emin = amin(eve)
        emax = amax(eve)
        
        if isrelative == 1:
            self.plot3 = self.VisualizeScalars(eve, scale='log10')
        else:    
            eve = [absmin if x<absmin else x for x in eve]            
            eve = [absmax if x>absmax else x for x in eve]   
            
            if absmin < emin:
                lutmin = (emin - absmin)/(absmax - absmin)
            else:
                lutmin = 0.0
            if absmax > emax:
                lutmax = (emax-absmin)/(absmax - absmin)
            else: lutmax = 1.0
            
            abslut = self.plot3.module_manager.scalar_lut_manager.lut.table.to_array()
            rellut = self.RelativeLut(abslut, lutmin, lutmax) 
            self.plot3 = self.VisualizeScalars(eve, customlut=rellut, scale='log10')
            
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
        
        self.plot3 = self.VisualizeScalars(opcrcolorscalars, opcrcolorlut, scale='linear', colorbar=0)        
        
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
        #self.dnevisualizecheck = QtGui.QCheckBox("Visualize DNE")
        self.dnerelvischeck = QtGui.QCheckBox("Relative scale")
        self.dnerelvischeck.toggle()
        self.dneabsvischeck = QtGui.QCheckBox("Absolute scale")
        self.dnevisbuttons = QtGui.QButtonGroup()
        self.dnevisbuttons.addButton(self.dnerelvischeck)
        self.dnevisbuttons.addButton(self.dneabsvischeck)
        self.dneabsmaxlabel = QtGui.QLabel("Max")
        self.dneabsmaxval = QtGui.QLineEdit("1.0")
        self.dneabsmaxval.setFixedWidth(40)
        self.dneabsminlabel = QtGui.QLabel("Min")
        self.dneabsminval = QtGui.QLineEdit("0.0")
        self.dneabsminval.setFixedWidth(40)
        
        self.dneconditioncontrolcheck = QtGui.QCheckBox("Condition number checking")
        self.dneconditioncontrolcheck.toggle()
        
        #self.dnedooutlierremovalcheck = QtGui.QCheckBox("Outlier removal")
        #self.dnedooutlierremovalcheck.toggle()
        self.dneoutliervallabel = QtGui.QLabel("Percentile")
        self.dneoutlierval = QtGui.QLineEdit("99.9")
        self.dneoutlierval.setFixedWidth(40)
        self.dneoutliertype1 = QtGui.QCheckBox("Energy x area")
        self.dneoutliertype1.toggle()
        self.dneoutliertype2 = QtGui.QCheckBox("Energy")
        self.dneoutlierbuttons = QtGui.QButtonGroup()
        self.dneoutlierbuttons.addButton(self.dneoutliertype1)
        self.dneoutlierbuttons.addButton(self.dneoutliertype2)
        
        #self.dneimplicitfaircheck = QtGui.QCheckBox("DNE implicit fairing smooth")
        self.dneiterationlabel = QtGui.QLabel("Iterations")
        self.dneiteration = QtGui.QLineEdit("3")
        self.dneiteration.setFixedWidth(40)
        self.dnestepsizelabel = QtGui.QLabel("Step size")
        self.dnestepsize = QtGui.QLineEdit("0.1")
        self.dnestepsize.setFixedWidth(40)
        
        # OPCR options submenu
        self.visualizeopcrcheck = QtGui.QCheckBox("Visualize OPCR")
        self.opcrlabel = QtGui.QLabel("Minimum patch count")
        self.opcrminpatch = QtGui.QLineEdit("3")
        self.opcrminpatch.setFixedWidth(40)
        
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
        self.DNEOptionsWindow = DNEOptionsWindow(self)
        self.dnebutton.clicked.connect(self.DNEOptionsWindow.show)
        self.OPCROptionsWindow = OPCROptionsWindow(self)
        self.opcrbutton.clicked.connect(self.OPCROptionsWindow.show)
        
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
        
        if len(filepath) == 0:
            return
        
        filename = os.path.split(filepath)[1]
        
        self.openlabel.setText(filename)
        self.mesh = plython.createarray(filepath)
        self.meshfacenumber = len(self.mesh[2])
        self.mayaviview = MayaviView(self.mesh,1,0)
        print "File open!"
        
    def OpenDirDialog(self):
        print "Opening directory..."
        self.dirpath = QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', '/')
        
        if len(self.dirpath) == 0:
            return
        
        self.openlabel.setText(".."+self.dirpath[-20:])
        self.mayaviview = MayaviView(0,1,0)
           
    def ProcessSurface(self):
        dtaresult = [" "," "," "," "," "," "," "," "]
        visinput1 = None
        visinput2 = None 
        
        if self.dnecheck.isChecked() == 1:
            print "Calculating DNE..."
            dneresult = DNE.calcdne(self.mesh, self.DNEOptionsWindow.fairvgroup.isChecked(), self.dneconditioncontrolcheck.isChecked(), self.dneiteration.text(), self.dnestepsize.text(), self.DNEOptionsWindow.outliervgroup.isChecked(), self.dneoutlierval.text(), self.dneoutliertype1.isChecked())
            if dneresult[0] == "!":
                print "DNE could not be calculated due to cholesky factorization error."
                dtaresult[0] = "N/A (cholesky error)"
            else: 
                print "DNE calculated."
                dtaresult[0] = str(round(dneresult[0],3))
                print "DNE = " + dtaresult[0]
                visinput1 = dneresult[1]
            
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
            visinput2 = opcrresult[2]
            print "OPCR = " + dtaresult[4]
            
        return dtaresult, visinput1, visinput2
        
    def CalcFile(self):     
        if self.dnecheck.isChecked() == 0 and self.rficheck.isChecked() == 0 and self.opcrcheck.isChecked() == 0:
            print "No topographic variables have been selected for analysis."
            return
        
        dtaresult, visinput1, visinput2 = self.ProcessSurface()
        
        print "\n--------------------\n"   
        print "RESULTS"
        print "File name: " + self.openlabel.text()
        print "Mesh face number: " + str(self.meshfacenumber)
        if self.dnecheck.isChecked() == 1:
            print "DNE: " + dtaresult[0]
            if self.DNEOptionsWindow.visvgroup.isChecked() == 1:
                MayaviView.VisualizeDNE(self.mayaviview, visinput1, self.dnerelvischeck.isChecked(),float(self.dneabsminval.text()), float(self.dneabsmaxval.text()))
        if self.rficheck.isChecked() == 1:
            print "RFI: " + dtaresult[1]
            print "Surface area: " + dtaresult[2]
            print "Outline area: " + dtaresult[3]           
        if self.opcrcheck.isChecked() == 1:
            print "OPCR: " + dtaresult[4]
            if self.visualizeopcrcheck.isChecked() == 1:
                MayaviView.VisualizeOPCR(self.mayaviview,visinput2,len(self.mesh[2]))
        print "\n--------------------"
        if self.visualizeopcrcheck.isChecked() == 1 and self.DNEOptionsWindow.visvgroup.isChecked() == 1 and self.dnecheck.isChecked() == 1 and self.opcrcheck.isChecked() == 1:
            print "DNE and OPCR visualization both requested. Defaulting to OPCR visualization."
                
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
                fileresult = self.ProcessSurface()[0]
                resultsfile.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (filename, self.meshfacenumber, fileresult[0], fileresult[1], fileresult[2], fileresult[3], fileresult[4]))
                print "\n--------------------\n"
            else:
                print filename + "does not have a .ply extension, skipping to next file."
        resultsfile.close()
        
class HBoxWidget(QtGui.QWidget):
    def __init__(self, widgetlist, indent=0, spacing=10):
        super(HBoxWidget,self).__init__()
        
        self.initUI(widgetlist, indent, spacing)
    
    def initUI(self, widgetlist, indent, spacing):
        self.hbox = QtGui.QHBoxLayout()
        map(lambda x: self.hbox.addWidget(x), widgetlist)
        self.hbox.setContentsMargins(indent,0,0,0)
        self.hbox.setSpacing(spacing)
        self.setLayout(self.hbox)

class VBoxWidget(QtGui.QWidget):
    def __init__(self, widgetlist):
        super(VBoxWidget, self).__init__()
        
        self.initUI(widgetlist)
        
    def initUI(self, widgetlist):
        self.vbox = QtGui.QVBoxLayout()
        self.vbox.setContentsMargins(20,0,0,10)
        self.vbox.setSpacing(8)
        map(lambda x: self.vbox.addWidget(x), widgetlist)
        self.setLayout(self.vbox)
        
class VGroupBoxWidget(QtGui.QGroupBox):
    def __init__(self, title, widgetlist):
        super(VGroupBoxWidget, self).__init__(title)
        
        self.initUI(widgetlist)
        
    def initUI(self, widgetlist):
        self.vbox = QtGui.QVBoxLayout()
        self.vbox.setContentsMargins(10,10,10,10)
        self.vbox.setSpacing(10)
        map(lambda x: self.vbox.addWidget(x), widgetlist)
        self.setLayout(self.vbox)
        self.setCheckable(1)
        self.setStyleSheet('QGroupBox::title {bottom: 1px; background-color: transparent}')

class DNEOptionsWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super(DNEOptionsWindow, self).__init__(parent)
        
        self.OKbutton = QtGui.QPushButton("OK")
        self.OKbutton.clicked.connect(self.OKClose)
        
        self.layout = QtGui.QVBoxLayout()
        self.layout.setSpacing(25)
        
        self.outlierhbox = HBoxWidget([parent.dneoutliervallabel, parent.dneoutlierval], spacing=6)       
        self.outliervgroup = VGroupBoxWidget('Outlier removal', [parent.dneoutliertype1, parent.dneoutliertype2, self.outlierhbox])       
        
        self.fairithbox = HBoxWidget([parent.dneiterationlabel, parent.dneiteration])        
        self.fairesthbox = HBoxWidget([parent.dnestepsizelabel, parent.dnestepsize]) 
        self.fairvgroup = VGroupBoxWidget('Implicit fair smooth', [self.fairithbox, self.fairesthbox])
        self.fairvgroup.setChecked(0)
        
        self.vishbox = HBoxWidget([parent.dneabsminlabel, parent.dneabsminval, parent.dneabsmaxlabel, parent.dneabsmaxval])                 
        self.visvgroup = VGroupBoxWidget('Visualize DNE', [parent.dnerelvischeck, parent.dneabsvischeck, self.vishbox])
        self.visvgroup.setChecked(0)
           
        self.layout.addWidget(parent.dneconditioncontrolcheck)
        
        self.layout.addWidget(self.outliervgroup)
        self.layout.addWidget(self.fairvgroup)
        self.layout.addWidget(self.visvgroup)
        
        self.layout.addWidget(self.OKbutton) 
        self.setLayout(self.layout)
        
        self.setSizePolicy(0, 0)
        
        self.setWindowTitle('DNE Options')
        
    def OKClose(self):
        self.close()
        
class OPCROptionsWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super(OPCROptionsWindow, self).__init__(parent)
           
        self.OKbutton = QtGui.QPushButton("OK")
        self.OKbutton.clicked.connect(self.OKClose)
        
        self.layout = QtGui.QVBoxLayout()
        self.layout.setSpacing(20)
        
        self.minpatchhbox = HBoxWidget([parent.opcrlabel, parent.opcrminpatch], spacing=15)
                
        self.layout.addWidget(self.minpatchhbox)
        self.layout.addWidget(parent.visualizeopcrcheck)
        self.layout.addWidget(self.OKbutton)
        self.layout.setContentsMargins(20,20,20,20)
        self.setLayout(self.layout)
        self.setSizePolicy(0, 0)
        
        self.setWindowTitle('OPCR Options') 
        
    def OKClose(self):
        self.close()              

def main():
    window = MainWidget()
    window.show()
    sys.exit(QtGui.qApp.exec_())

if __name__ == "__main__":
    main()
    