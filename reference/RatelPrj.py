# -*- coding: utf-8 -*-
"""

@author: sota_masuda
"""
import os
from pathlib import Path
import sys
import configparser
import math
import time
import shapefile
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

class RatelProject():
    def __init__(self):
        self.prjfileName = "RatelSample.xml"

    def Load(self, prjpath = None):
        # if projectfile exists load
        self.existPrj = 0
        if prjpath == None:
            if os.path.isfile(self.prjfileName):
                self.tree = ET.parse(self.prjfileName)
                self.existPrj = 1
        else:
            if os.path.isfile(prjpath):
                self.tree = ET.parse(prjpath)
                self.prjfilepath = prjpath
                self.existPrj = 1

        # if not exists create
        if self.existPrj == 0:
            self.createPrj()
            self.tree = ET.parse(self.prjfileName)


    def createPrj(self):
        elmShpFiles = ET.Element('shpfiles')
        comment = ET.Comment('add shp file pathes')
        elmShpFiles.append(comment)
        tree = ET.ElementTree(element=elmShpFiles)
        tree.write(self.prjfileName, encoding='utf-8', xml_declaration=True)

    def Output(self):
        self.tree.write(self.prjfileName, encoding='utf-8', xml_declaration=True)

    def addShpPath(self, shppath):
        #node = self.tree.find('shpfiles')
        root = self.tree.getroot()
        subElm = ET.SubElement(root, 'shpfile')
        subElm.text = shppath
        #root.append(subElm)
        # subElmはrootから参照で取得した感じ？
        # root.append()をしてしまうとshppathが二つ分出力されてしまう
        # よって、subElm.text=shppathだけでよい





