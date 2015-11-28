'''
Created on May 22, 2015

@author: Julia M. Winchester

Script requires meshconv (http://www.cs.princeton.edu/~min/meshconv/) for usage.
'''

import sys
import os

# Replace with desired directory
dirpath = "/Users/Username/meshes"

# Replace with meshconv.exe
meshconv = "/Users/Username/meshtools/meshconv"

for filename in os.listdir(dirpath):
    fullpath = os.path.join(dirpath,filename)
    os.system("sed -i '' '16,18d' " + fullpath)
    os.system("sed -i '' '$d' " + fullpath)
    os.system("sed -i '' '$d' " + fullpath)
    newfilename = filename[0:-4]
    os.system(meshconv + " " + fullpath + " -c off")