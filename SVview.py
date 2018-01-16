# -*- coding: utf-8 -*-
"""
@author: sota_masuda
python 3.6
"""
import os
import re
from PyQt5.Qt import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import SVscene

class svView(QGraphicsView):
    def __init__(self):
        super(svView, self).__init__()
        # member
        self._numScheduledScalings = 0
        self.mposShowFlg = True

        # D&D setting
        self.setAcceptDrops(True)

        # QGraphicsScene setting
        scene = SVscene.svScene(self)
        #scene.setSceneRect(QRectF(self.geometry()))
        self.setScene(scene)

        # Generate Base Map
        self.initBaseMap()

    def linkStatusbar(self, stbar: QStatusBar):
        self.statusbar = stbar

    def mkGridPen(self):
        gridpen = QPen(QColor('grey'))
        gridpen.setWidth(0)
        gridpen.setStyle(Qt.DashLine)
        return gridpen


    def initBaseMap(self):
        self.resolution = 100 # pix / 度
        self.meshWid = 1*self.resolution
        self.baseMapWid = 360*self.resolution
        self.baseMapHgt = 180*self.resolution

        # Basic Layer
        self.basicLayer = QGraphicsRectItem()
        self.basicLayer.setRect(0, 0, self.baseMapWid, self.baseMapHgt)
        self.basicLayer.setBrush(QBrush(QColor('white')))
        self.basicLayer.setFlag(QGraphicsItem.ItemIsMovable)
        self.scene().addItem(self.basicLayer)

        # Mesh Grid
        # --Latitude(horizontal)
        lats = self.baseMapHgt / self.meshWid
        for ilat in range(int(lats) - 1):
            # create as a child of basicLayer
            grid = QGraphicsLineItem(self.basicLayer)
            grid.setLine(0, 0, self.baseMapWid, 0)
            grid.setPen(self.mkGridPen())
            grid.setTransform(grid.transform().translate(0, self.meshWid*(ilat+1)))
        # --Longitude(vertical)
        lons = self.baseMapWid / self.meshWid
        for ilon in range(int(lons) - 1):
            # create as a child of basicLayer
            grid = QGraphicsLineItem(self.basicLayer)
            grid.setLine(0, 0, 0, self.baseMapHgt)
            grid.setPen(self.mkGridPen())
            grid.setTransform(grid.transform().translate(self.meshWid * (ilon + 1), 0))

        # Center of The World
        cw = self.basicLayer.rect().center()
        centW = QGraphicsEllipseItem(self.basicLayer)
        cwsize = 200
        centW.setRect(cw.x(), cw.y(), cwsize, cwsize)
        centW.setTransform(centW.transform().translate(-(cwsize/2), -(cwsize/2)))
        centW.setBrush(QBrush(QColor('red')))

        # マップ中心がWindowの中心になるように移動
        self.centerOn(cw)



    def keyPressEvent(self, event: QKeyEvent):
        # debug : center on japan
        keymods = QApplication.keyboardModifiers()
        if Qt.Key_Return == event.key():
            if keymods == Qt.ControlModifier:
                # Hyougo Akashi(N37,135E)
                self.centerOn(135.0 * self.meshWid, 37.0 * self.meshWid)
                print('test')


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

    def wheelEvent(self, event: QWheelEvent):
        '''
        参考1：https://wiki.qt.io/Smooth_Zoom_In_QGraphicsView/ja
        参考2：https://gist.github.com/mieki256/1b73aae707cee97fffab544af9bc0637
        '''
        # ズーム率算出
        numDegrees = event.angleDelta().y() / 8
        numSteps = numDegrees / 15
        self._numScheduledScalings += numSteps
        # if reverse wheel
        if 0 > (self._numScheduledScalings * numSteps):
            self._numScheduledScalings = numSteps

        # シーン上の座標値に変換
        p0 = self.mapToScene(event.pos())

        # スケール変更
        factor = 1.0 + (self._numScheduledScalings) / 50.0
        self.scale(factor, factor)

        # シーン上の座標値をViewの座標値に変換
        p1 = self.mapFromScene(p0)

        # ズーム変更前後のマウスカーソル座標の左をスクロールバーに反映
        # これによりマウスカーソル位置を基準にズームしているように見える
        mv = QPoint(p1.x() - event.pos().x(), p1.y() - event.pos().y())
        self.addScrollBarValue(mv.x(), mv.y())


    def addScrollBarValue(self, dx, dy):
        # スクロールバーの現在値を変化させる
        x = self.horizontalScrollBar().value()
        y = self.verticalScrollBar().value()
        self.horizontalScrollBar().setValue(x + dx)
        self.verticalScrollBar().setValue(y + dy)

    def enterEvent(self, a0: QEvent):
        self.setMouseTracking(True)

    def leaveEvent(self, a0: QEvent):
        self.setMouseTracking(False)

    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        if Qt.LeftButton == event.button():
            self.mposShowFlg = False

    def mouseReleaseEvent(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)
        if Qt.LeftButton == event.button():
            self.mposShowFlg = True

    def mouseMoveEvent(self, event: QMouseEvent):
        super().mouseMoveEvent(event)

        # =======================
        # update status bar
        # =======================
        if True == self.mposShowFlg:
            # calc diff(positive X --> East, positive Y --> South)
            mpos = event.pos()
            cw = self.basicLayer.rect().center()
            diff = QPointF(mpos.x() - cw.x(), mpos.y() - cw.y())
            # make message to show
            EW = 'E'
            if 0 > diff.x():
                EW = 'W'
            SN = 'S'
            if 0 > diff.y():
                SN = 'N'
            lon = str(abs(int(diff.x() / self.resolution)))
            lat = str(abs(int(diff.y() / self.resolution)))
            msg = lon + EW + ' ' + lat + SN
            self.statusbar.showMessage(msg)



