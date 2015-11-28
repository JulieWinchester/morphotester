'''
Created on Jan 21, 2015

@author: Julia M. Winchester

Script requires meshconv (http://www.cs.princeton.edu/~min/meshconv/) for usage.
'''

import sys
import os

# Replace with desired directory
dirpath = "/Users/Username/meshes"

# Replace with location of meshconv
meshconv = "/Users/Username/meshconv"

for filename in os.listdir(dirpath):
    fullpath = os.path.join(dirpath,filename)
    newfilename = filename[0:-4]
    os.system(meshconv + " " + fullpath + " -c ply -o " + os.path.join(dirpath,newfilename) + "-asc " + "-ascii")
    
