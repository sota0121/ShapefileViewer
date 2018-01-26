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
import SVscene
import SVutil as utl
import OperateINI as inifile

# ズーム倍率（単位は％ floatを使うと誤差がたまるのでintで管理）
zoomValue = 100

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

        # -- revert scrolling
        #sb = QPoint(ini.scrollbar_x, ini.scrollbar_y)
        #self.setScrollBarValue(sb.x(), sb.y())

        # -- revert moving of base map
        mv = QPointF(ini.mv_base_x, ini.mv_base_y)
        #cent = self.basicLayer.centerPosParent() #centerPosと挙動同じだった
        cent = self.basicLayer.centerPos()
        cent.setX(cent.x() - mv.x())
        cent.setY(cent.y() - mv.y())
        self.centerOn(cent) #CenterOnによりsetScrollBarが掻き消される
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
        self.CreateFeatures(self.scene().shpFiles)

        # add Item to scene
        self.scene().addItem(self.basicLayer)
        #self.scene().setSceneRect(self.basicLayer.rect())

        # move point to look
        #self.centerOn(self.basicLayer.centerPos())

    def translateBasicLayer(self,dx,dy):
        if dx > 0.1:
            if dy > 0.1:
                print('translate basemap')
                self.basicLayer.setTransform(self.basicLayer.transform().translate(dx, dy))

    def CreateFeatures(self, shpFiles):
        for sf in shpFiles:
            shprecs = sf.iterShapeRecords()
            sr_size = len(sf.shapeRecords())
            i = 0
            for sr in shprecs:
                # 進捗表示
                sys.stdout.write("\r%d / 100" % (int(i * 100 / (sr_size - 1))))
                sys.stdout.flush()
                i += 1
                # gen object
                obj = Ft_Polygon(self.basicLayer)
                # set element points position
                obj.setShpPointsLL(sr.shape.points)
                # set attributes
                for attr in sr.record:
                    attr_str = utl.u_sjis(attr)
                    obj.addAttribute(attr_str)
            sys.stdout.write("\n")

    def keyPressEvent(self, event: QKeyEvent):
        # debug : center on japan
        keymods = QApplication.keyboardModifiers()
        if Qt.Key_Return == event.key():
            if keymods == Qt.ControlModifier:
                # basiclayer move to origin
                # pass
                #self.centerOn(135.0 * self.basicLayer.resolution, 37.0 * self.basicLayer.resolution)
                print('move basemap to origin(0,0) in scene coordinates')

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
        self.zoom = self.changeZoomValue(pow(1.2, event.angleDelta().y()/240.0)) / 100.0

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
        return self.clipZoomValue(zoomValue * d)

    def clipZoomValue(self, zv):
        global zoomValue
        zoomValue = max(10, min(zv, 3200))  # 10 - 3200の範囲にする
        zvi = int(zoomValue)
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
        super().mousePressEvent(event)
        if Qt.LeftButton == event.button():
            self.mposShowFlg = False

    def mouseReleaseEvent(self, event: QMouseEvent):
        # super
        super().mouseReleaseEvent(event)
        # set flg
        if Qt.LeftButton == event.button():
            self.mposShowFlg = True

    def mouseMoveEvent(self, event: QMouseEvent):
        super().mouseMoveEvent(event)
        #event.pos()


class BaseMap(QGraphicsRectItem):
    def __init__(self, parent:svView):
        # super initialize
        super(BaseMap, self).__init__()
        self.parentView = parent
        self.setAcceptHoverEvents(True)

        # members
        self.resolution = 10  # pix / 度
        self.meshWid = 1 * self.resolution
        self.baseMapWid = 360 * self.resolution
        self.baseMapHgt = 180 * self.resolution
        self.cur_mv_sta = QPointF(0.0,0.0)
        self.cur_mv_end = QPointF(0.0,0.0)
        self.mvBgnPoint = QPointF(0, 0)
        self.onDrag = False

        # Basic Layer
        self.setRect(0, 0, self.baseMapWid, self.baseMapHgt)
        self.setBrush(QBrush(QColor('white')))
        self.setFlag(QGraphicsItem.ItemIsMovable)

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

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent'):
        # move base map with scroll bar
        if True == self.onDrag:
            curpos = event.pos()
            # 移動度
            mvvec = curpos
            mvvec -= self.mvBgnPoint
            mvvec.setX((mvvec.x() / self.resolution))
            mvvec.setY((mvvec.y() / self.resolution))
            # 移動開始点の更新
            self.mvBgnPoint = curpos
            # 移動の適用@scroll bar
            self.parentView.addScrollBarValue(int(mvvec.x()),int(mvvec.y()))
            # --------------
            print("vec: " + str(int(mvvec.x())) + ", " + str(int(mvvec.y())))
            # --------------


    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent'):
        # super
        super().mousePressEvent(event)

        # get point
        if Qt.LeftButton == event.button():
            # ドラッグ開始位置
            self.mvBgnPoint = event.pos()
            #bgp = event.pos()
            #self.mvBgnPoint = QPoint(int(bgp.x()),int(bgp.y()))
            # --------
            p = self.mvBgnPoint
            print("START DRAG: " + str(p.x()) + ", " + str(p.y()))
            # --------
            self.onDrag = True
            # ベース地図の移動ベクトル始点取得
            self.cur_mv_sta = event.scenePos()

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent'):
        # super
        super().mouseReleaseEvent(event)

        # release
        if Qt.LeftButton == event.button():
            # ドラッグ終了
            self.onDrag = False
            # ベース地図の移動ベクトル終点取得
            self.cur_mv_end = event.scenePos()

        # ベース地図の移動ベクトル計算
        mv = self.cur_mv_end
        mv -= self.cur_mv_sta

        # 移動ベクトルの加算（最終的な移動度の更新）
        self.parentView.mvObjVector += mv
        #MV = self.parentView.mvObjVector
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

    def setShpPointsLL(self, shpPoints:list):
        # set position lat lon
        global_polygon = QPolygonF()
        for sp in shpPoints:
            ll = (sp[0], sp[1]) # 0:Lon, 1:Lat
            self.shpPointsLL.append(ll)

            # calc translation for mapping to parent
            map_ratio = self.baseMap.resolution
            point = QPointF(sp[0]*map_ratio, sp[1]*map_ratio*(-1))
            global_polygon.append(point)

        # set polygon
        self.setPolygon(global_polygon)
        self.setBrush(QBrush(QColor('orange')))
        self.setPen(self.mkOutlinePen())
        cw = self.baseMap.centerPos()
        self.setTransform(self.transform().translate(cw.x(),cw.y()))


        '''
        cp = self.baseMap.centerPos()
        self.baseMap.resolution
        '''

    def mkOutlinePen(self):
        OutLinepen = QPen(QColor('black'))
        OutLinepen.setWidth(0)
        OutLinepen.setStyle(Qt.SolidLine)
        return OutLinepen



