# -*- coding: utf-8 -*-
"""
@author: sota_masuda
python 3.6
"""

import shapefile
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import SVproject

class svScene(QGraphicsScene):
    def __init__(self, *argv, **keywords):
        super(svScene, self).__init__(*argv, **keywords)
        self.project = SVproject.svProject()
        self.project.Load()

    def setShapeFile(self, shppath):
        # save shppath
        self.project.addShpPath(shppath)
        # load shapfile
        self.LoadShp(shppath)

    def LoadShp(self, shppath):
        self.sf = shapefile.Reader(shppath)
        #self.

    def OutputPrj(self):
        self.project.Output()
