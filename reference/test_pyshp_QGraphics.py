# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 10:03:16 2017

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


#===================================================================
# Shapeポリゴンクラス
#===================================================================
class QGraphicsShpPolygonItem(QGraphicsPolygonItem):
    def __init__(self):
        super(QGraphicsShpPolygonItem, self).__init__()

    def SetShapeRec(self, shapeRecord):
        self.sr = shapeRecord

    def shpRec(self):
        return self.sr



#===================================================================
# シーンの管理
#===================================================================
class ShapeViewScene(QGraphicsScene):
    def __init__(self, *argv, **keywords):
        super(ShapeViewScene, self).__init__( *argv, **keywords )
        self.__shapeItem        = None
        self.__currentPos       = None
        self.__pressedButton    = None
        self.__AllreadyRead     = 0



    '''
    def shapeItem(self):
        if self.__AllreadyRead == 1:
            return self.__shapeItem
    '''

    def ReadShape(self, filepath):
        self.sf = shapefile.Reader(filepath)
        self.fields = self.sf.fields
        self.__AllreadyRead = 1
        sxmin, symin, sxmax, symax = self.sf.bbox
        self.shpLB = [sxmin, symin]
        self.shpRU = [sxmax, symax]
        self.shpRB = [sxmax, symin]
        self.shpLU = [sxmin, symax]
        self.shpWid = abs(sxmax - sxmin)
        self.shpHeight = abs(symax - symin)
        self.shpCenter = [sxmin + self.shpWid / 2.0, symin + self.shpHeight / 2.0]
        self.CreatePolygon()


    # Shapefileデータからポリゴンを生成する
    def CreatePolygon(self):
        if self.__AllreadyRead == 1:
            shapeRecs = self.sf.iterShapeRecords()
            for sr in shapeRecs:
                # get shape
                sp = sr.shape.points
                item = QGraphicsShpPolygonItem()
                item.SetShapeRec(sr)
                polygon = QPolygonF()
                # gen polygon
                for i in range(len(sp)):
                    lon = sp[i][0] - self.shpCenter[0]  # lon
                    lat = self.shpCenter[1] - sp[i][1]  # lat
                    polygon.append(QPointF(self.width() / 2 + lon * 500 , self.height() / 2 + lat * 500 ))

                # make polygon item
                item.setPolygon(polygon)
                item.setBrush(QBrush(QColor("orange")))
                item.setFlag(QGraphicsItem.ItemIsMovable)
                # add Item to Scene
                self.addItem(item)




    #------------------------------------------------
    # マウスドラッグ中の処理イベント
    # ■参考サイト
    # http://flame-blaze.net/archives/5219
    # Viewクラスに移行すべきかもしれない
    # -----------------------------------------------
    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent'):
        self.__currentPos = event.scenePos()
        self.__pressedButton = event.button()

        if self.__pressedButton == Qt.RightButton:
            cursorShape = Qt.SizeAllCursor
        else:
            cursorShape = Qt.ClosedHandCursor
        qApp.setOverrideCursor(QCursor(cursorShape))


    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent'):
        if not self.__currentPos:
            return

        # 移動度の算出
        cur = event.scenePos()
        value = QPointF()
        value.setX(cur.x() - self.__currentPos.x())
        value.setY(cur.y() - self.__currentPos.y())
        # アイテムの移動処理
        for item in self.items():
            transform = item.transform()
            transform *= QTransform().translate(value.x(), value.y())
            item.setTransform(transform)

        # 現在のマウス位置をクラス内変数に保持
        self.__currentPos = cur


    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent'):
        self.__currentPos       = None
        self.__pressedButton    = None
        qApp.restoreOverrideCursor()
        super(ShapeViewScene, self).mouseReleaseEvent(event)



    # ダブルクリックで地物の情報を出力
    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent'):
        # 現在のマウス位置を取得(マウス位置のアイテムはとれた)
        mpos = event.scenePos()
        curItem = self.itemAt(mpos, QTransform())


        '''
        rec = curItem.sr.record
        for i in range(len(self.fields)):
            if i == 0:
                continue

            print(self.fields[i][0])
            srec = rec[i]
            if srec == '':
                continue

            srec.decode('utf-8')
            print(srec)
        '''









#===================================================================
# ビューの管理
#===================================================================
class ShapeViewer( QGraphicsView ):
    def __init__(self):
        super( ShapeViewer, self ).__init__()
        self.setMouseTracking(True)

        # QGraphicsView の設定
        self.setCacheMode( QGraphicsView.CacheBackground )
        self.setRenderHints( QPainter.Antialiasing |
                             QPainter.SmoothPixmapTransform |
                             QPainter.TextAntialiasing)

        # Trandformマトリクスを変更する際のアンカーの設定。今回はなしにする
        self.setTransformationAnchor(QGraphicsView.NoAnchor)

        # QGraphicsSceneの作成・設定
        scene = ShapeViewScene( self )
        scene.setSceneRect( QRectF(self.rect()) )
        self.setScene(scene)

        # シーンの矩形を全てのアイテムの矩形の4倍の大きさに変更する
        # これにより、アイテムがビューからはみ出ていなくても
        # 自由に移動できるようになる
        self.resizeSceneRect()


    def ReadShape(self, filepath):
        self.scene().ReadShape(filepath)

    def resizeEvent(self, event: QResizeEvent):
        super( ShapeViewer, self ).resizeEvent(event)
        self.scene().setSceneRect(QRectF(self.rect()))

    # 現在のシーンにある全てのアイテムの矩形の任意の倍数の矩形をシーンに適用する
    def resizeSceneRect(self, scaleFactor=4):
        itemRect = self.scene().itemsBoundingRect()
        scaleRatio = self.transform().m11()

        itemRect.adjust(
            -itemRect.width() / scaleRatio * scaleFactor,
            -itemRect.height() / scaleRatio * scaleFactor,
            itemRect.width() / scaleRatio * scaleFactor,
            itemRect.height() / scaleRatio * scaleFactor
        )
        self.setSceneRect(itemRect)


    # マウスホイールでズーム
    # https://stackoverflow.com/questions/19113532/qgraphicsview-zooming-in-and-out-under-mouse-position-using-mouse-wheel
    def wheelEvent(self, event: QWheelEvent):
        """
        Zoom in or out of the view
        """
        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor

        # Save the scene pos
        oldPos = self.mapToScene(event.pos())

        # Zoom
        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
        self.scale(zoomFactor, zoomFactor)

        # Get the new position
        newPos = self.mapToScene(event.pos())

        # Move scene to old positon
        delta_x = newPos.x() - oldPos.x()
        delta_y = newPos.y() - oldPos.y()
        self.translate(delta_x, delta_y)


# //////////////////////////////////////////////////////////////
def main():
    # --------------------------
    # Qt gui 作成
    # --------------------------
    app = QApplication(sys.argv)
    viewer = ShapeViewer()

    # --------------------------
    # 設定ファイル読み込み
    # --------------------------
    inifile = configparser.ConfigParser()
    inifile.read('./config.ini')
    shpDir = inifile.get('Setting', 'ShpDir')
    inifile.set('App', '')
    inifile.write()

    # --------------------------
    # Shapeファイルパス取得
    # --------------------------

    # --------------------------
    # shape データ取得
    # --------------------------
    # 福岡のShapefile path 設定
    #scriptPath = Path(__file__).resolve() # os.path ではなく pathlibを使うのが今風
    #scriptDir = Path(scriptPath)
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    shpfilepath = shpDir + '\\' + 'N03-17_170101.shp'

    # Read
    viewer.ReadShape(shpfilepath)

    # --------------------------
    # shape データ描画
    # --------------------------
    viewer.show()
    sys.exit(app.exec_())

# main
if __name__ == '__main__':
    main()



