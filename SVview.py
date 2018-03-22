# -*- coding: utf-8 -*-
"""
@author: sota_masuda
python 3.6
"""
import os
import sys
import re
from PyQt5.Qt import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import shapefile
from PyQt5.QtWidgets import QGraphicsPathItem

import SVscene
import SVutil as utl
import OperateINI as inifile

# ズーム倍率（単位は％ floatを使うと誤差がたまるのでintで管理）
#zoomValue = 100

class svView(QGraphicsView):
    def __init__(self):
        super(svView, self).__init__()
        # member
        self._numScheduledScalings = 0
        self.mposShowFlg = True
        self.zoom = 1.0
        self.mposLL = [0.0,0.0]
        self.mposNSEW = ['E','N']
        self.mvObjVector = QPointF(0.0,0.0)
        self.mousePressed = False
        self.prePosition = QPoint()
        self.delta = QPoint()
        self.ratio = 1.0
        self.timerID = 0
        # ズーム倍率（単位は％ floatを使うと誤差がたまるのでintで管理）
        self.zoomValue = 100

        # D&D setting
        self.setAcceptDrops(True)

        # QGraphicsScene setting
        scene = SVscene.svScene(self)
        self.setScene(scene)

        # Generate Base Map
        self.initBaseMap()

    def RevertView(self, ini:inifile):
        # -- revert zooming
        self.scale(ini.zoom, ini.zoom)
        self.zoom = ini.zoom
        # iniに値がある場合のみ設定（それ以外は初期値100を用いる）
        if ini.zoomValue > 0:
            self.zoomValue = ini.zoomValue

        # -- revert scrolling
        sb = QPoint(ini.scrollbar_x, ini.scrollbar_y)
        self.setScrollBarValue(sb.x(), sb.y())

        # -- revert moving of base map
        mv = QPointF(ini.mv_base_x, ini.mv_base_y)
        #cent = self.basicLayer.centerPosParent() #centerPosと挙動同じだった
        cent = self.basicLayer.centerPos()
        cent.setX(cent.x() - mv.x())
        cent.setY(cent.y() - mv.y())
        self.centerOn(cent)
        self.mvObjVector = mv

        '''
        self.centerOn(self.basicLayer.centerPos())
        mv = QPointF(ini.mv_base_x, ini.mv_base_y)
        self.translateBasicLayer(mv.x(), mv.y())
        self.mvObjVector = mv
        '''

    def linkStatusbar(self, stbar: QStatusBar):
        self.statusbar = stbar

    def updateStatusbar(self):
        lon = self.mposLL[0]
        lat = self.mposLL[1]
        EW = self.mposNSEW[0]
        SN = self.mposNSEW[1]
        #nss = self._numScheduledScalings
        #msg = '{:.2f}'.format(lon) + EW + ' ' + '{:.2f}'.format(lat) + SN + ' ' + '{:.2f}'.format(nss)
        zoom = self.zoom
        msg = '{:.2f}'.format(lon) + EW + ' ' + '{:.2f}'.format(lat) + SN + ' ' + '{:.2f}'.format(zoom)
        self.statusbar.showMessage(msg)

    def initBaseMap(self):
        '''initialize basic map'''
        # Basic Layer
        self.basicLayer = BaseMap(self)

        # Map Layer (virtual name)
        self.CreateFeaturesByShps(self.scene().shpFiles)

        # add Item to scene
        self.scene().addItem(self.basicLayer)

        # move point to look
        #self.centerOn(self.basicLayer.centerPos())

    def translateBasicLayer(self,dx,dy):
        if dx > 0.1:
            if dy > 0.1:
                print('translate basemap')
                self.basicLayer.setTransform(self.basicLayer.transform().translate(dx, dy))

    def CreateFeatureObj(self, shpType :int, shape):
        # Point / PointZ / PointM
        if (shpType == 1) or (shpType == 11) or (shpType == 21):
            # gen obj
            obj = Ft_Point(self.basicLayer)
            # set obj
            obj.setShpPointLL(shape)
        # PolyLine / PolylineZ / PolylineM
        elif (shpType == 3) or (shpType == 13) or (shpType == 23):
            # gen obj
            obj = Ft_Polyline(self.basicLayer)
            # set obj
            obj.setShpPolylineLL(shape)
        # Polygon / PolygonZ / PolygonM
        elif (shpType == 5) or (shpType == 15) or (shpType == 25):
            # gen obj
            obj = Ft_Polygon(self.basicLayer)
            # set obj
            obj.setShpPolygonLL(shape)
            return obj


    def CreateFeaturesByShp(self, shpFile):
        # shapeType取得（ファイル内統一 ※Null Shape 除く）
        shpType = shpFile.shapeType

        # Error because of shape type is "Null Shape"
        if shpType == 0:
            print("ERROR : This shapefile has Null Shape data")
            return -1

        # record 単位の処理
        shprecs = shpFile.iterShapeRecords()
        sr_size = shpFile.numRecords
        i = 0
        for sr in shprecs:
            # 進捗表示
            sys.stdout.write("\r%d / 100" % (int(i * 100 / (sr_size - 1))))
            sys.stdout.flush()

            # gen object
            obj = self.CreateFeatureObj(shpType, sr.shape)

            # set attributes(shape ファイルごとに実装しないといけない)
            #for attr in sr.record:
                #attr_str = utl.u_sjis(attr)
                #obj.addAttribute(attr_str)
            # index increment
            i += 1

        sys.stdout.write("\n")


    def CreateFeaturesByShps(self, shpFiles):
        for sf in shpFiles:
            self.CreateFeaturesByShp(sf)

    def keyPressEvent(self, event: QKeyEvent):
        # debug : center on japan
        keymods = QApplication.keyboardModifiers()
        if Qt.Key_Return == event.key():
            if keymods == Qt.ControlModifier:
                # basiclayer move to origin
                # pass
                #self.centerOn(135.0 * self.basicLayer.resolution, 37.0 * self.basicLayer.resolution)
                print('move basemap to origin(0,0) in scene coordinates')
        elif Qt.Key_Up == event.key():
            self.addScrollBarValue(0, -10)
        elif Qt.Key_Down == event.key():
            self.addScrollBarValue(0, 10)
        elif Qt.Key_Left == event.key():
            self.addScrollBarValue(-10, 0)
        elif Qt.Key_Right == event.key():
            self.addScrollBarValue(10, 0)

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
                    # Add Shapefile
                    ret = self.scene().setShapeFile(filepath)
                    if False == ret:
                        QMessageBox.warning(self, 'Warning', "Already Read!!", QMessageBox.Ok)
                    # Add Shape Object on Viewer
                    sf = shapefile.Reader(filepath)
                    self.CreateFeaturesByShp(sf)

            else:
                wmsg = "Format Error\n"
                wmsg += "suppurt [*.shp, -, -]"
                QMessageBox.warning(self,'Warning',wmsg,QMessageBox.Ok)

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
        # ズーム率取得（単位は％）
        self.zoom = self.changeZoomValue(pow(1.8, event.angleDelta().y()/240.0)) / 100.0

        # 与えた座標値(View用)をシーン上の座標値に変換
        p0 = self.mapToScene(event.pos())

        # スケール変更
        self.resetTransform()
        self.scale(self.zoom, self.zoom)

        # シーン上の座標値をViewの座標値に変換
        p1 = self.mapFromScene(p0)

        # ズーム変更前後のマウスカーソル座標の左をスクロールバーに反映
        # これによりマウスカーソル位置を基準にズームしているように見える
        mv = QPoint(p1.x() - event.pos().x(), p1.y() - event.pos().y())
        self.addScrollBarValue(mv.x(), mv.y())

        # update showing message on statusbar
        self.updateStatusbar()

    def changeZoomValue(self, d):
        """ ズーム率の変数を変更 """
        return self.clipZoomValue(self.zoomValue * d)

    def clipZoomValue(self, zv):
        self.zoomValue = max(10, min(zv, 128000))  # 10 - XXXの範囲にする
        zvi = int(self.zoomValue)
        return zvi

    def setScrollBarValue(self, x, y):
        self.horizontalScrollBar().setValue(x)
        self.verticalScrollBar().setValue(y)

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
        if Qt.LeftButton == event.button():
            self.mposShowFlg = False
            # drag用
            self.mousePressed = True
            self.prePosition = event.pos()
            self.delta = QPoint()
            self.ratio = 1.0
            self.timerID = self.startTimer(20)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        # set flg
        if Qt.LeftButton == event.button():
            self.mposShowFlg = True
            self.mousePressed = False
        # super
        super().mouseReleaseEvent(event)

    # ref : https://gist.github.com/Atsushi4/3761749
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.mousePressed:
            self.delta.setX(event.pos().x() - self.prePosition.x())
            self.delta.setY(event.pos().y() - self.prePosition.y())
            self.prePosition = event.pos()
            self.addScrollBarValue(-self.delta.x(), -self.delta.y())
        super().mouseMoveEvent(event)

    def timerEvent(self, event: 'QTimerEvent'):
        #if (self.timerID == event.timerId()) and (True == self.mousePressed):
            #if (self.delta == QPoint()) or (self.ratio < 0.01):
                #self.killTimer(self.timerID)
                #return
            #dx = self.delta.x() * self.ratio
            #dy = self.delta.y() * self.ratio
            #self.addScrollBarValue(dx, dy)
            #self.addScrollBarValue(10, 10)
        super().timerEvent(event)


class BaseMap(QGraphicsRectItem):
    def __init__(self, parent:svView):
        # super initialize
        super(BaseMap, self).__init__()
        self.parentView = parent
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)

        # members
        self.resolution = 10  # pix / 度
        self.meshWid = 1 * self.resolution
        self.baseMapWid = 360 * self.resolution
        self.baseMapHgt = 180 * self.resolution
        self.cur_mv_sta = QPointF(0.0,0.0)
        self.cur_mv_end = QPointF(0.0,0.0)

        # Basic Layer
        self.setRect(0, 0, self.baseMapWid, self.baseMapHgt)
        self.setBrush(QBrush(QColor('white')))
        self.setFlag(QGraphicsItem.ItemIsMovable, enabled=False)

        # Mesh Grid
        # --Latitude(horizontal)
        lats = self.baseMapHgt / self.meshWid
        for ilat in range(int(lats) - 1):
            # create as a child of basicLayer
            grid = QGraphicsLineItem(self)
            grid.setLine(0, 0, self.baseMapWid, 0)
            grid.setPen(self.mkGridPen())
            grid.setTransform(grid.transform().translate(0, self.meshWid * (ilat + 1)))
        # --Longitude(vertical)
        lons = self.baseMapWid / self.meshWid
        for ilon in range(int(lons) - 1):
            # create as a child of basicLayer
            grid = QGraphicsLineItem(self)
            grid.setLine(0, 0, 0, self.baseMapHgt)
            grid.setPen(self.mkGridPen())
            grid.setTransform(grid.transform().translate(self.meshWid * (ilon + 1), 0))

        # Center of The World
        cw = self.rect().center()
        centW = QGraphicsEllipseItem(self)
        cwsize = 2 * self.resolution
        centW.setRect(cw.x(), cw.y(), cwsize, cwsize)
        centW.setTransform(centW.transform().translate(-(cwsize / 2), -(cwsize / 2)))
        centW.setBrush(QBrush(QColor('red')))

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent'):
        # super
        super().mousePressEvent(event)

        # ベース地図の移動ベクトル始点取得
        self.cur_mv_sta = event.scenePos()

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent'):
        # super
        super().mouseReleaseEvent(event)

        # ベース地図の移動ベクトル終点取得
        self.cur_mv_end = event.scenePos()

        # ベース地図の移動ベクトル計算
        mv = self.cur_mv_end
        mv -= self.cur_mv_sta

        # 移動ベクトルの加算（最終的な移動度の更新）
        self.parentView.mvObjVector += mv
        MV = self.parentView.mvObjVector
        #print('X : ' + '{:.2f}'.format(MV.x()))
        #print('Y : ' + '{:.2f}'.format(MV.y()))

    def centerPos(self):
        return self.rect().center()

    def centerPosParent(self):
        c = self.rect().center()
        cp = self.mapToParent(c)
        return cp

    def mkGridPen(self):
        gridpen = QPen(QColor('grey'))
        gridpen.setWidth(0)
        gridpen.setStyle(Qt.DashLine)
        return gridpen

    def updateParent(self, lon:float, lat:float, ew:str, sn:str):
        # update parent info
        self.parentView.mposLL[0] = lon
        self.parentView.mposLL[1] = lat
        self.parentView.mposNSEW[0] = ew
        self.parentView.mposNSEW[1] = sn
        # call "update status bar method"
        self.parentView.updateStatusbar()

    def hoverMoveEvent(self, event: 'QGraphicsSceneHoverEvent'):
        # calculate mouse position on map(Lat Lon)
        cent_local = self.rect().center()
        mpos_local = event.pos()
        diff = QPointF()
        diff.setX(mpos_local.x() - cent_local.x())
        diff.setY(mpos_local.y() - cent_local.y())

        ew = 'E'
        if 0 > diff.x():
            ew = 'W'
        sn = 'S'
        if 0 > diff.y():
            sn = 'N'
        lon = abs(diff.x() / self.resolution)
        lat = abs(diff.y() / self.resolution)
        # update showing message
        self.updateParent(lon,lat,ew,sn)


class Ft_Polygon(QGraphicsPolygonItem):
    def __init__(self, parent:BaseMap):
        super(Ft_Polygon, self).__init__(parent)
        self.attributes = []
        self.shpPointsLL = []
        self.baseMap = parent

    def addAttribute(self, attr:str):
        self.attributes.append(attr)

    def attributes(self):
        return self.attributes

    def setShpPolygonLL(self, shp):
        # part 単位で処理
        bgnIdx = 0
        lastIdx = len(shp.points) - 1
        map_ratio = self.baseMap.resolution
        cw = self.baseMap.centerPos()
        for ipart in range(len(shp.parts) + 1):
            if 0 == ipart:
                continue
            # ------------------
            # update end index
            # ------------------
            endIdx = 0
            if ipart == len(shp.parts):
                endIdx = lastIdx
            else:
                endIdx = shp.parts[ipart]

            # ------------------
            # set a part
            #  --> from bgn to end
            # ------------------
            # set position lat lon
            global_polygon = QPolygonF()
            for ipnt in range(bgnIdx, endIdx):
                sp = shp.points[ipnt]
                ll = (sp[0], sp[1])  # 0:Lon, 1:Lat
                self.shpPointsLL.append(ll)

                # calc translation for mapping to parent
                point = QPointF(sp[0] * map_ratio, sp[1] * map_ratio * (-1))
                global_polygon.append(point)

            # set polygon
            self.setPolygon(global_polygon)
            self.setBrush(QBrush(QColor('orange')))
            self.setPen(self.mkOutlinePen())
            self.setTransform(self.transform().translate(cw.x(), cw.y()))

            # ------------------
            # update bgn index
            # ------------------
            bgnIdx = endIdx


    def mkOutlinePen(self):
        OutLinepen = QPen(QColor('black'))
        OutLinepen.setWidth(0)
        OutLinepen.setStyle(Qt.SolidLine)
        return OutLinepen

class Ft_Polyline(QGraphicsPathItem):
    def __init__(self, parent:BaseMap):
        super(Ft_Polyline, self).__init__(parent)
        self.attributes = []
        self.shpPointsLL = []
        self.baseMap = parent

    def addAttribute(self, attr:str):
        self.attributes.append(attr)

    def attributes(self):
        return self.attributes

    def setShpPolylineLL(self, shp):
        # part 単位で処理
        bgnIdx = 0
        lastIdx = len(shp.points) - 1
        map_ratio = self.baseMap.resolution
        for ipart in range(len(shp.parts) + 1):
            if 0 == ipart:
                continue
            # ------------------
            # update end index
            # ------------------
            endIdx = 0
            if ipart == len(shp.parts):
                endIdx = lastIdx
            else:
                endIdx = shp.parts[ipart]

            # ------------------
            # set a part
            #  --> from bgn to end
            # ------------------
            # set position lat lon
            global_line = QPainterPath()
            # -- zero index
            sp0 = shp.points[bgnIdx]
            point0 = QPointF(sp0[0]*map_ratio, sp0[1]*map_ratio*(-1))
            global_line.moveTo(point0.x(), point0.y())

            # -- from 1 index
            for ipnt in range(bgnIdx, endIdx):
                if bgnIdx == ipnt:
                    continue
                sp = shp.points[ipnt]
                ll = (sp[0], sp[1]) # 0:Lon, 1:Lat
                self.shpPointsLL.append(ll)

                # calc translation for mapping to parent
                point = QPointF(sp[0]*map_ratio, sp[1]*map_ratio*(-1))
                global_line.lineTo(point.x(), point.y())

            # set polyline
            self.setPath(global_line)
            self.setPen(self.mkOutlinePen())
            cw = self.baseMap.centerPos()
            self.setTransform(self.transform().translate(cw.x(),cw.y()))

            # ------------------
            # update bgn index
            # ------------------
            bgnIdx = endIdx


    def mkOutlinePen(self):
        OutLinepen = QPen(QColor('blue'))
        OutLinepen.setWidth(0)
        OutLinepen.setStyle(Qt.SolidLine)
        return OutLinepen

class Ft_Point(QGraphicsEllipseItem):
    def __init__(self, parent:BaseMap):
        super(Ft_Point, self).__init__(parent)
        self.attributes = []
        self.shpPointsLL = []
        self.baseMap = parent

    def addAttribute(self, attr:str):
        self.attributes.append(attr)

    def attributes(self):
        return self.attributes

    def setShpPointLL(self, shp):
        if 0 == len(shp.points):
            return
        # set position lat lon
        global_point = QPointF()
        sp = shp.points[0]
        ll = (sp[0], sp[1])  # 0:Lon, 1:Lat
        self.shpPointsLL.append(ll)

        # calc translation for mapping to parent
        map_ratio = self.baseMap.resolution
        point = QPointF(sp[0] * map_ratio, sp[1] * map_ratio * (-1))
        global_point.setX(point.x())
        global_point.setY(point.y())

        # set ellipse
        self.setRect(global_point.x(), global_point.y(), 0.1, 0.1)
        self.setBrush(QBrush(QColor('green')))
        self.setPen(self.mkOutlinePen())
        cw = self.baseMap.centerPos()
        self.setTransform(self.transform().translate(cw.x(),cw.y()))

    def mkOutlinePen(self):
        OutLinepen = QPen(QColor('black'))
        OutLinepen.setWidth(0)
        OutLinepen.setStyle(Qt.SolidLine)
        return OutLinepen