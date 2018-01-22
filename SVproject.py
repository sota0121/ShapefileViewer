# -*- coding: utf-8 -*-
"""
@author: sota_masuda
python 3.6
"""
import os
import xml.etree.ElementTree as ET
import SVutil as utl

class svProject():
    def __init__(self):
        self.prjfileName = "SV_Sample.xml"

    def Load(self, prjpath = None):
        # if projectfile exists load
        self.existPrj = 0
        # プロジェクトファイル名を指定しない場合デフォルト名で取得
        if prjpath == None:
            if os.path.isfile(self.prjfileName):
                self.tree = ET.parse(self.prjfileName)
                self.existPrj = 1
        # 指定名称のプロジェクトファイルをロード・ファイル名を更新
        else:
            if os.path.isfile(prjpath):
                self.tree = ET.parse(prjpath)
                self.prjfilepath = prjpath
                self.existPrj = 1

        # if not exists create
        if self.existPrj == 0:
            self.createPrj()
            self.tree = ET.parse(self.prjfileName)

    def shppaths(self):
        paths = []
        root = self.tree.getroot()
        for path in root.findall('shpfile'):
            paths.append(path.text)
        return paths

    def createPrj(self):
        elmShpFiles = ET.Element('shpfiles')
        comment = ET.Comment('add shp file paths')
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