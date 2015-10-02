'''
Created on Oct 2, 2015

A scientific computing application for measuring topographic shape in 3D data.
To run MorphoTester, execute Morpho.py as a script. 

MorphoTester is licensed under the GPL license. See LICENSE.txt for further details. 

@author: Julia M. Winchester
'''

__version__ = '1.0'

__requires__ = ['Image', 'matplotlib', 'mayavi', 'numpy', 'PyQt4', 'scipy', 'sip', 'traits', 'traitsui', 'tvtk']

__all__ = ['Morpho', 'DNE', 'OPCR', 'RFI', "implicitfair", "normcore", "plython", "render"]