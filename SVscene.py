# -*- coding: utf-8 -*-
"""
@author: sota_masuda
python 3.6
"""

import shapefile
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import SVproject
import SVutil as utl

class svScene(QGraphicsScene):
    def __init__(self, *argv, **keywords):
        super(svScene, self).__init__(*argv, **keywords)
        self.shpFiles = []

        self.project = SVproject.svProject()
        self.project.Load()
        paths = self.project.shppaths()
        for path in paths:
            self.LoadShp(path)

    def setShapeFile(self, shppath):
        # already read ?
        paths = self.project.shppaths()
        for path in paths:
            if shppath == path:
                return False
        # save shppath
        self.project.addShpPath(shppath)
        # load shapfile
        self.LoadShp(shppath)
        return True

    def LoadShp(self, shppath):
        sf = shapefile.Reader(shppath)
        self.shpFiles.append(sf)

    def OutputPrj(self):
        self.project.Output()
