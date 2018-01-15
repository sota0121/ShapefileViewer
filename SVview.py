# -*- coding: utf-8 -*-
"""
@author: sota_masuda
python 3.6
"""
import os
import re
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import SVscene



class svView(QGraphicsView):
    def __init__(self):
        super(svView, self).__init__()
        # D&D setting
        self.setAcceptDrops(True)

        # QGraphicsScene setting
        scene = SVscene.svScene(self)
        #scene.setSceneRect(QRectF(self.geometry()))
        self.setScene(scene)

        # Items setting
        self.initItems()


    def initItems(self):
        # test rect
        item = QGraphicsRectItem()
        maxRect = self.geometry()
        item.setRect(maxRect.x(),maxRect.y(),100, 100)
        item.setBrush(QBrush(QColor("orange")))
        item.setFlag(QGraphicsItem.ItemIsMovable)
        self.scene().addItem(item)

    def dragEnterEvent(self, event: QDragEnterEvent):
        # check mimeData which is able to be accept
        mimeData = event.mimeData()
        if mimeData.hasUrls():
            event.accept()
        else:
            event.ignore()


    def dropEvent(self, event: QDropEvent):
        # check mimeData and add object
        mimeData = event.mimeData()

        for url in mimeData.urls():
            # url -> path
            filepath = str(url.toLocalFile())
            # check ext
            root, ext = os.path.splitext(filepath)
            #if re.match(r'^\.(shp|shx|dbf)$', ext, re.IGNORECASE):
            if re.match(r'^\.(shp)$', ext, re.IGNORECASE):
                if os.path.isfile(filepath):
                    self.scene().setShapeFile(filepath)



    def dragMoveEvent(self, event: QDragMoveEvent):
        # to work dragEnterEvent for QGraphicsView
        pass

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        # to work dragEnterEvent for QGraphicsView
        pass