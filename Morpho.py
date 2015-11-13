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

class TopoMesh(plython.PlythonMesh):
    """A class for creating and interacting with triangulated polygon meshes and topographic variables.
    
    Class inherits from plython.PlythonMesh. Creates a list of Numpy ndarray objects containing 
    triangulated polygon mesh data if provided with a path to a .ply file. Topographic variables
    are instanced as None and take the data types specified below when generated using the 
    ProcessSurface method. 
    
    Args:
        filepath (str): Path to a .ply polygon mesh file
        
    Attributes:
        mesh (list): Triangulated polygon mesh data. Contains three ndarrays:
            vertex XYZ points, polygons with component vertex indices, and 
            polygons with component vertex XYZ points. 
        nvert (int): Number of vertices in mesh. 
        nface (int): Number of polygons in mesh.
        vertices (ndarray): Vertex XYZ points for mesh.
        faces (ndarray): Polygons with component vertex indices for mesh.
        triverts (ndarray): Polygons with component vertex XYZ points for mesh.
        DNE (float): Total Dirichlet normal energy of mesh. 
        DNEscalars (ndarray): Scalars for visualizing DNE.
        conditionfaces (list): List of polygon face indices with high matrix condition numbers.
        boundaryfaces (list): List of polygon face indices forming mesh edges.
        outlierfaces (list): List of polygon face indices removed as outliers, with DNE values and face areas.
        RFI (float): Relief index of mesh (surface area/projected area).
        surfarea (float): 3D surface area of mesh. 
        projarea (float): 2D surface area of mesh projected on XY plane. 
        OPCR (float): Orientation patch count rotated for mesh. 
        OPClist (list): Orientation patch counts at 8 rotations for mesh.
        OPCscalars: Scalars for visualizing OPC. 
    
    """
    def __init__(self, filepath):
        super(TopoMesh,self).__init__(filepath)
        
        self.DNE = None
        self.DNEscalars = None
        self.conditionfaces = None
        self.boundaryfaces = None
        self.outlierfaces = None
        
        self.RFI = None
        self.surfarea = None
        self.projarea = None
        self.linelen = None
        self.bluepixie = None
        self.redpixie = None
        self.pixelratio = None
        
        self.OPCR = None
        self.OPClist = None
        self.OPCscalars = None
        
    def GenerateDNE(self, dosmooth, smoothit, smoothstep, docondition, dooutlier, outlierperc, outliertype):
        """Calculates Dirichlet normal energy (surface bending) from mesh data.
        
        For details on args, see DNE.MeshDNE class. 
        
        Args:
            doSmooth (bool): If true, do implicit fair smooth. 
            SmoothIt (int): Iterations of smoothing
            SmoothStep (float): Smoothing step size. 
            doCondition (bool): If true, do polygon condition number control. 
            doOutlier (bool): If true, do outlier removal. 
            OutlierPerc (float): Outlier percentile. 
            OutlierType (bool): If true, outliers as energy*area. If false, outliers as energy. 
            
        """
        surfcurv = DNE.MeshDNE(self, dosmooth, smoothit, smoothstep, docondition, dooutlier, outlierperc, outliertype)
        self.DNE = surfcurv.DNE
        self.DNEscalars = surfcurv.equantity
        self.conditionfaces = surfcurv.high_condition_faces
        self.boundaryfaces = surfcurv.boundary_faces
        self.outlierfaces = surfcurv.outlier_faces
          
    def GenerateRFI(self):
        """Calculates relief index (surface relief) from mesh data."""
        surfrelf = RFI.MeshRFI(self)
        self.RFI = surfrelf.RFI
        self.surfarea = surfrelf.surfarea
        self.projarea = surfrelf.projarea
        self.linelen = surfrelf.linelen
        self.bluepixie = surfrelf.bluepixie
        self.redpixie = surfrelf.redpixie
        self.pixelratio = surfrelf.pixelratio
        
    def GenerateOPCR(self, minpatch):
        """Calculates orientation patch count rotated (surface complexity) from mesh data.
        
        For details on args see OPC.MeshOPCR class. 
        
        Args:
            minpatch (int): Minimum size for counting patches.
            
        """
        surfcomp = OPC.MeshOPCR(self, minpatch)
        self.OPCR = surfcomp.OPCR
        self.OPClist = surfcomp.opc_list
        self.OPCscalars = surfcomp.colormap_list[0]  
        
class MainWidget(QtGui.QWidget):
    """ Class for primary UI window."""
    
    def __init__(self):
        super(MainWidget, self).__init__()

        self.initUI()
        
    def initUI(self):
        """ Creates primary UI layout and widgets.
        
        Displays MayaviView 3D viewer pane. Opens submenus for file selection, directory selection,
        and DNE/OPCR options. Executes calculation of topography and visualization of calculated
        topography.
        """
        #=======================================================================
        # Tab layout
        #=======================================================================
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
        
        #=======================================================================
        # UI widgets
        #=======================================================================
        self.openbutton = QtGui.QPushButton("Open File")
        self.opendirbutton = QtGui.QPushButton("Open Directory")
        self.openlabel = QtGui.QLabel("") 
        
        # Topography and options window widgets
        self.dnecheck = QtGui.QCheckBox("DNE")
        self.dnecheck.toggle()
        self.dnebutton = QtGui.QPushButton("Options")
        
        self.rficheck = QtGui.QCheckBox("RFI")
        self.rficheck.toggle()
        
        self.opcrcheck = QtGui.QCheckBox("OPCR")
        self.opcrcheck.toggle()
        self.opcrbutton = QtGui.QPushButton("Options")
        
        # Topography calculation buttons
        self.calcfilebutton = QtGui.QPushButton("Process File")
        self.calcdirbutton = QtGui.QPushButton("Process Directory")
           
        # Contents of mesh tools tab
        self.toolslabel = QtGui.QLabel("Mesh tools coming soon.")
        
        # Output log
        self.morpholog = QtGui.QTextEdit()
        self.morpholog.setReadOnly(1)
        
        # 3D view
        self.mayaviview = MayaviView(0,1)
        self.threedview = self.mayaviview.edit_traits().control
        
        #=======================================================================
        # GUI behavior
        #=======================================================================
        self.openbutton.clicked.connect(self.OpenFileDialog)
        self.opendirbutton.clicked.connect(self.OpenDirDialog)

        self.calcfilebutton.clicked.connect(self.CalcFile)
        self.calcdirbutton.clicked.connect(self.CalcDir)
        
        # Options submenu buttons
        self.DNEOptionsWindow = DNEOptionsWindow(self)
        self.dnebutton.clicked.connect(self.DNEOptionsWindow.show)
        self.OPCROptionsWindow = OPCROptionsWindow(self)
        self.opcrbutton.clicked.connect(self.OPCROptionsWindow.show)
        
        #=======================================================================
        # UI grid layout
        #=======================================================================
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
        """Method for loading .ply surface mesh files."""
        filepath = QtGui.QFileDialog.getOpenFileName(self, 'Open File', '/')
        
        if len(filepath) == 0:
            return
        
        print "Opening file..."
        filename = os.path.split(filepath)[1]
        self.openlabel.setText(filename)
        self.TopoMesh = TopoMesh(filepath)
        self.mayaviview = MayaviView(self.TopoMesh.mesh,1)
        print "File open!"
        
    def OpenDirDialog(self):
        """Method for selecting a directory for batch processing of .ply surface mesh files."""
        self.dirpath = QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', '/')
        
        if len(self.dirpath) == 0:
            return
        
        print "Opening directory..."
        self.openlabel.setText(".."+self.dirpath[-20:])
        self.mayaviview = MayaviView(0,1)
           
    def ProcessSurface(self):
        """Method for processing surface mesh data to acquire topographic variables."""
        
        if self.dnecheck.isChecked() == 1:
            self.TopoMesh.GenerateDNE(self.DNEOptionsWindow.fairvgroup.isChecked(), 
                                      self.DNEOptionsWindow.dneiteration.text(), self.DNEOptionsWindow.dnestepsize.text(), 
                                      self.DNEOptionsWindow.dneconditioncontrolcheck.isChecked(), 
                                      self.DNEOptionsWindow.outliervgroup.isChecked(), self.DNEOptionsWindow.dneoutlierval.text(), 
                                      self.DNEOptionsWindow.dneoutliertype1.isChecked())
                        
        if self.rficheck.isChecked() == 1:
            self.TopoMesh.GenerateRFI()
            
        if self.opcrcheck.isChecked() == 1:
            self.TopoMesh.GenerateOPCR(self.OPCROptionsWindow.opcrminpatch.text())
        
    def CalcFile(self):
        """Method for processing a single surface mesh object. 
        
        Connected to Process File Button."""     
        if self.dnecheck.isChecked() == 0 and self.rficheck.isChecked() == 0 and self.opcrcheck.isChecked() == 0:
            print "No topographic variables have been selected for analysis."
            return
        
        self.ProcessSurface()
        
        if self.dnecheck.isChecked():
            print "\nDNE calculation details:"
            if self.TopoMesh.DNE == "!":
                print "\nDNE could not be calculated due to cholesky factorization error."
            else:
                if self.DNEOptionsWindow.outliervgroup.isChecked():
                    print "\nPolygons removed as outliers:"
                    for face in self.TopoMesh.outlierfaces:
                        print "Polygon: %s\tEnergy: %s\tArea %s" % (face[0], face[1], face[2])
                if self.DNEOptionsWindow.dneconditioncontrolcheck.isChecked():
                    print "\nPolygons removed for high matrix condition numbers:"
                    for face in self.TopoMesh.conditionfaces:
                        print "Polygon: %s\tMatrix condition number: %s" % (face[0], face[1])
                print "\nNumber of edge polygons ignored: %s" % len(self.TopoMesh.boundaryfaces)
        
        print "\n--------------------"   
        print "RESULTS"
        print "File name: %s" % self.openlabel.text()
        print "Mesh face number: %s" % self.TopoMesh.nface
        if self.dnecheck.isChecked():
            if self.TopoMesh.DNE == "!":
                print "\nError (Cholesky factorization error)"
            else:
                print "\nDNE: %s" % self.TopoMesh.DNE
                if self.DNEOptionsWindow.visvgroup.isChecked():
                    MayaviView.VisualizeDNE(self.mayaviview, self.TopoMesh.DNEscalars, self.DNEOptionsWindow.dnerelvischeck.isChecked(),
                                            float(self.DNEOptionsWindow.dneabsminval.text()), 
                                            float(self.DNEOptionsWindow.dneabsmaxval.text()))
        if self.rficheck.isChecked():
            print "\nRFI: %s" % self.TopoMesh.RFI
            print "Surface area: %s" % self.TopoMesh.surfarea
            print "Outline area: %s" % self.TopoMesh.projarea           
        if self.opcrcheck.isChecked():
            print "\nOPCR: %s" % self.TopoMesh.OPCR
            print "OPC at each rotation: %s" % self.TopoMesh.OPClist
            if self.OPCROptionsWindow.visualizeopcrcheck.isChecked():
                MayaviView.VisualizeOPCR(self.mayaviview, self.TopoMesh.OPCscalars, self.TopoMesh.nface)
        print "--------------------"
        if self.OPCROptionsWindow.visualizeopcrcheck.isChecked() and self.DNEOptionsWindow.visvgroup.isChecked() and self.dnecheck.isChecked() and self.opcrcheck.isChecked():
            print "DNE and OPCR visualization both requested. Defaulting to OPCR visualization."
                
    def CalcDir(self): 
        """Method for batch processing a directory of .ply surface mesh files.
        
        Connected to Process Directory button."""       
        if self.dnecheck.isChecked() == 0 and self.rficheck.isChecked() == 0 and self.opcrcheck.isChecked() == 0:
            print "No topographic variables have been selected for analysis."
            return
      
        resultsfile = open(os.path.join(self.dirpath,'morphoresults.txt'),'w')
        resultsfile.write("Filename\tMesh Face Number\tDNE\tRFI\tSurface Area\tOutline Area\tOPCR\n")
           
        for filename in os.listdir(self.dirpath):
            if filename[-3:] == "ply":
                print "Processing " + filename + "..."
                self.TopoMesh = TopoMesh(os.path.join(self.dirpath,filename))
                self.ProcessSurface()
                resultsfile.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (filename, self.TopoMesh.nface, self.TopoMesh.DNE, 
                                                                    self.TopoMesh.RFI, self.TopoMesh.surfarea, 
                                                                    self.TopoMesh.projarea, self.TopoMesh.OPCR))
                print "\n--------------------\n"
            else:
                print filename + "does not have a .ply extension, skipping to next file."
        resultsfile.close()

class MayaviView(HasTraits):    
    """Class for 3D visualization of polygonal meshes and related 2D decorators.
    
    Initializes 3D viewer and displays a 3D polygonal mesh if provided with a data object.
    
    Args:
        plotmesh (bool): If true, plots model from MainWidget.TopoMesh class.
        clearscreen (bool): If true, clears figure before plotting model.  
    
    Attributes:
        Class:
            scene: MlabSceneModel instance.
            view: Mayavi view of scene.
        __init__():
            plot: Mayavi figure plot of visualized mesh.
    """
    scene = Instance(MlabSceneModel, ())
    
    # The layout of the panel created by Traits
    view = View(Item('scene', editor=SceneEditor(), resizable=True, show_label=False), resizable=True)
    
    def __init__(self, model, clearscreen):
        HasTraits.__init__(self)
       
        self.model = model
        self.plot = self.VisualizeMesh(self.model, clearscreen)
        
    def VisualizeMesh(self, model, clearscreen):
        """Method for creating a Mayavi figure plot of visualized 3D polygonal mesh."""
        if clearscreen == 1:
            self.plot = self.scene.mlab.clf()
        
        if model == 0:
            self.plot = self.scene.mlab.points3d(0,0,0,opacity=0.0)
        else:
            triangles = model[2]
            x, y, z = model[0][:,0], model[0][:,1], model[0][:,2]
                            
            self.plot = self.scene.mlab.triangular_mesh(x, y, z, triangles)
                    
        return self.plot

    def Interpolate(self, i, j, steps):
        """Interpolates sets of numbers between designated end point number sets."""
        onestep = steps+1
        ijrange = j.astype(float) - i.astype(float)
        fillarray = rint(array([ijrange/(onestep)*s+i.astype(float) for s in range(onestep)[1:]]))
        if (fillarray < 0).any():
            fillarray = array([abs(x[::-1]) if (x < 0).any() else x for x in fillarray.T]).T
        return fillarray
        
    def RelativeLut(self, lut, lmin, lmax):
        """Given a LUT (255x4 array of colors), creates a new LUT from segment of original LUT using interpolation."""
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
        """Method for visualizing scalar data on polygonal mesh using optional color LUT and linear or log scaling."""
        self.visplot = self.VisualizeMesh(self.model,1)
        
        self.visplot.mlab_source.dataset.cell_data.scalars = scalars
        self.visplot.mlab_source.dataset.cell_data.scalars.name = 'Cell data'
        self.visplot.mlab_source.update()
        
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
        """Visualizes energy density across polygonal mesh."""    
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
            
            abslut = self.plot.module_manager.scalar_lut_manager.lut.table.to_array()
            rellut = self.RelativeLut(abslut, lutmin, lutmax) 
            self.plot3 = self.VisualizeScalars(eve, customlut=rellut, scale='log10')
            
    def VisualizeOPCR(self,hexcolormap,facelength):
        """Visualizes patches across polygonal mesh."""
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

class DNEOptionsWindow(QtGui.QDialog):
    """Submenu for selecting optional parameters for DNE calculation."""
    def __init__(self, parent=None):
        super(DNEOptionsWindow, self).__init__(parent)
        #=======================================================================
        # Submenu layout
        #=======================================================================
        self.layout = QtGui.QVBoxLayout()
        self.layout.setSpacing(25)
        
        #=======================================================================
        # Submenu widgets
        #=======================================================================
        self.OKbutton = QtGui.QPushButton("OK")
        self.OKbutton.clicked.connect(self.OKClose)
        
        # Matrix condition number controls
        self.dneconditioncontrolcheck = QtGui.QCheckBox("Condition number checking")
        self.dneconditioncontrolcheck.toggle()
        
        # Outlier removal controls
        self.dneoutliervallabel = QtGui.QLabel("Percentile")
        self.dneoutlierval = QtGui.QLineEdit("99.9")
        self.dneoutlierval.setFixedWidth(40)
        self.outlierhbox = HBoxWidget([self.dneoutliervallabel, self.dneoutlierval], spacing=6)       
        
        self.dneoutliertype1 = QtGui.QCheckBox("Energy x area")
        self.dneoutliertype1.toggle()
        self.dneoutliertype2 = QtGui.QCheckBox("Energy")
        self.dneoutlierbuttons = QtGui.QButtonGroup()
        self.dneoutlierbuttons.addButton(self.dneoutliertype1)
        self.dneoutlierbuttons.addButton(self.dneoutliertype2)
        self.outliervgroup = VGroupBoxWidget('Outlier removal', [self.dneoutliertype1, self.dneoutliertype2, self.outlierhbox])       
        
        # Smoothing controls
        self.dneiterationlabel = QtGui.QLabel("Iterations")
        self.dneiteration = QtGui.QLineEdit("3")
        self.dneiteration.setFixedWidth(40)
        self.fairithbox = HBoxWidget([self.dneiterationlabel, self.dneiteration])
        
        self.dnestepsizelabel = QtGui.QLabel("Step size")
        self.dnestepsize = QtGui.QLineEdit("0.1")
        self.dnestepsize.setFixedWidth(40)     
        self.fairesthbox = HBoxWidget([self.dnestepsizelabel, self.dnestepsize]) 
        
        self.fairvgroup = VGroupBoxWidget('Implicit fair smooth', [self.fairithbox, self.fairesthbox])
        self.fairvgroup.setChecked(0)
        
        # Visualization control widgets
        self.dneabsmaxlabel = QtGui.QLabel("Max")
        self.dneabsmaxval = QtGui.QLineEdit("1.0")
        self.dneabsmaxval.setFixedWidth(40)
        self.dneabsminlabel = QtGui.QLabel("Min")
        self.dneabsminval = QtGui.QLineEdit("0.0")
        self.dneabsminval.setFixedWidth(40)
        self.vishbox = HBoxWidget([self.dneabsminlabel, self.dneabsminval, self.dneabsmaxlabel, self.dneabsmaxval])                 
        
        self.dnerelvischeck = QtGui.QCheckBox("Relative scale")
        self.dnerelvischeck.toggle()
        self.dneabsvischeck = QtGui.QCheckBox("Absolute scale")
        self.dnevisbuttons = QtGui.QButtonGroup()
        self.dnevisbuttons.addButton(self.dnerelvischeck)
        self.dnevisbuttons.addButton(self.dneabsvischeck)
        self.visvgroup = VGroupBoxWidget('Visualize DNE', [self.dnerelvischeck, self.dneabsvischeck, self.vishbox])
        self.visvgroup.setChecked(0)
           
        #=======================================================================
        # Building the submenu layout
        #=======================================================================
        self.layout.addWidget(self.dneconditioncontrolcheck)
        
        self.layout.addWidget(self.outliervgroup)
        self.layout.addWidget(self.fairvgroup)
        self.layout.addWidget(self.visvgroup)
        
        self.layout.addWidget(self.OKbutton) 
        self.setLayout(self.layout)
        
        self.setSizePolicy(0, 0)
        
        self.setWindowTitle('DNE Options')
        
    def OKClose(self):
        """Closes submenu on OK."""
        self.close()
        
class OPCROptionsWindow(QtGui.QDialog):
    """Submenu for selecting optional parameters for OPCR calculation."""
    def __init__(self, parent=None):
        super(OPCROptionsWindow, self).__init__(parent)
        #=======================================================================
        # Submenu layout
        #=======================================================================
        self.layout = QtGui.QVBoxLayout()
        self.layout.setSpacing(20)
        
        #=======================================================================
        # Submenu widgets
        #=======================================================================
        self.OKbutton = QtGui.QPushButton("OK")
        self.OKbutton.clicked.connect(self.OKClose)
        
        # Visualization and minimum patch size controls
        self.visualizeopcrcheck = QtGui.QCheckBox("Visualize OPCR")
        self.opcrlabel = QtGui.QLabel("Minimum patch count")
        self.opcrminpatch = QtGui.QLineEdit("3")
        self.opcrminpatch.setFixedWidth(40)
        self.minpatchhbox = HBoxWidget([self.opcrlabel, self.opcrminpatch], spacing=15)
        
        #=======================================================================
        # Building the submenu layout
        #=======================================================================
        self.layout.addWidget(self.minpatchhbox)
        self.layout.addWidget(self.visualizeopcrcheck)
        self.layout.addWidget(self.OKbutton)
        self.layout.setContentsMargins(20,20,20,20)
        self.setLayout(self.layout)
        self.setSizePolicy(0, 0)
        
        self.setWindowTitle('OPCR Options') 
        
    def OKClose(self):
        """Closes submenu on OK."""
        self.close() 
        
class HBoxWidget(QtGui.QWidget):
    """Generic class for creating QWidgets with QHBoxLayout with standard properties.
    
    Args:
        widgetlist (list): List of QWidget objects to be displayed.
        indent (int): Left marginal indentation of HBoxWidget.
        spacing (int): Component spacing of HBoxWidget contents.
    """
    def __init__(self, widgetlist, indent=0, spacing=10):
        super(HBoxWidget,self).__init__()
        
        self.initUI(widgetlist, indent, spacing)
    
    def initUI(self, widgetlist, indent, spacing):
        """Adds widgets to and sets layout of HBoxWidget object."""
        self.hbox = QtGui.QHBoxLayout()
        map(lambda x: self.hbox.addWidget(x), widgetlist)
        self.hbox.setContentsMargins(indent,0,0,0)
        self.hbox.setSpacing(spacing)
        self.setLayout(self.hbox)
        
class VGroupBoxWidget(QtGui.QGroupBox):
    """Generic class for creating QGroupBox with QVBoxLayout with standard properties.
    
    Args:
        widgetlist (list): List of QWidget objects to be displayed.
        title (str): Title for QGroupBox.
    """
    def __init__(self, title, widgetlist):
        super(VGroupBoxWidget, self).__init__(title)
        
        self.initUI(widgetlist)
        
    def initUI(self, widgetlist):
        """Adds widgets to and sets layout of VGroupBoxWidget object."""
        self.vbox = QtGui.QVBoxLayout()
        self.vbox.setContentsMargins(10,10,10,10)
        self.vbox.setSpacing(10)
        map(lambda x: self.vbox.addWidget(x), widgetlist)
        self.setLayout(self.vbox)
        self.setCheckable(1)
        self.setStyleSheet('QGroupBox::title {background-color: transparent}')

class OutLog:
    def __init__(self, edit, out=None, color=None):
        """(edit, out=None, color=None) -> can write stdout, stderr to a
        QTextEdit.
        
        Args:
            edit (QTextEdit) = QTextEdit object for writing stdout and stderr to.
            out = Alternate stream (can be the original sys.stdout).
            color = Alternate color (i.e. color stderr, a different color).
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

def main():
    """Main application loop."""
    window = MainWidget()
    window.show()
    sys.exit(QtGui.qApp.exec_())

if __name__ == "__main__":
    main()
    