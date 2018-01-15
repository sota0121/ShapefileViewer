# -*- coding:utf-8 -*-
import os
import sys
from PyQt4 import QtGui, QtCore
import math

# このサイトを参考んした
# http://melpystudio.blog82.fc2.com/blog-entry-147.html?sp

# /////////////////////////////////////////////////////////////////////////////
# 指定したQGraphicsItemの子としてテキストアイテムを追加する                  //
# QGraphicsSimpleTextItemの派生クラス。                                      //
# /////////////////////////////////////////////////////////////////////////////
class TextItem(QtGui.QGraphicsSimpleTextItem):
    Font = QtGui.QFont('Meiryo', 8)  # このアイテムに使用するフォント

    def __init__(self, text, parentItem):
        # このクラスの初期化。-------------------------------------------------
        super(TextItem, self).__init__(text, parentItem)
        self.setFont(self.Font)
        # ---------------------------------------------------------------------


        # テキストを親アイテムの中心に配置する。-------------------------------
        # 親の矩形と自信の矩形から、テキストを置くべきポジションを割り出す。
        parentRect = parentItem.boundingRect()  # 親の矩形範囲
        localRect = self.boundingRect()  # 自身の矩形範囲
        posX = (
            (parentRect.width() - localRect.width()) / 2
            + parentRect.x()
        )
        posY = (
            (parentRect.height() - localRect.height()) / 2
            + parentRect.y()
        )

        # 移動情報をQTransformとしてセットする。
        self.setTransform(
            QtGui.QTransform().translate(posX, posY)
        )
        # ---------------------------------------------------------------------


# /////////////////////////////////////////////////////////////////////////////
#                                                                            //
# /////////////////////////////////////////////////////////////////////////////


# /////////////////////////////////////////////////////////////////////////////
# ビューワとなるメインクラス                                                 //
# /////////////////////////////////////////////////////////////////////////////
class ItemViewer(QtGui.QGraphicsView):
    # イメージのパス。同階層の"image.png"をフルパスで格納している。
    ImageFilePath = os.path.join(os.path.dirname(__file__), 'image.png')

    def __init__(self, parent=None):
        # このクラスの初期化。-------------------------------------------------
        super(ItemViewer, self).__init__(parent)
        self.setWindowTitle('Item Viewer Example')
        self.resize(480, 480)

        self.__pos = None  # マウス操作時の位置情報保持用変数。
        # ---------------------------------------------------------------------

        # 設定変更。-----------------------------------------------------------
        # スクロールバーを非表示にする。
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # アイテムレンダリング時にアンチエイリアスをかける。
        self.setRenderHints(
            QtGui.QPainter.Antialiasing |
            QtGui.QPainter.SmoothPixmapTransform |
            QtGui.QPainter.TextAntialiasing
        )

        # Transformマトリクスを変更する際のアンカーの設定。今回は無しにする。
        self.setTransformationAnchor(QtGui.QGraphicsView.NoAnchor)
        # ---------------------------------------------------------------------

        # QGraphicsSceneを作成し、このビューへセットする。
        self.setScene(
            QtGui.QGraphicsScene(QtCore.QRectF(self.rect()))
        )

        # アイテムを配置する。
        self.initializeItems()

        # シーンの矩形を全てのアイテムの矩形の４倍の大きさに変更する。
        # （これにより、アイテムがビューからはみ出ていなくても
        # 自由に移動出来るようになる)
        self.resizeSceneRect()

    # このビュー付属のシーンをクリアし、各種アイテムを再配置するメソッド。=====
    def initializeItems(self):
        self.scene().clear()  # シーンをクリア

        # 楕円アイテムの作成。-------------------------------------------------
        ellipseItem = QtGui.QGraphicsEllipseItem(20, 20, 120, 120)
        # 楕円アイテムを移動可能に設定。
        ellipseItem.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        # 上部で作成した指定したテキストを任意のアイテム上に配置する
        # オブジェクトを作成。
        ellipseText = TextItem('QGraphicsEllipseItem', ellipseItem)

        # 楕円アイテムに赤のカラーを適用。
        ellipseItem.setBrush(QtGui.QColor(220, 68, 102))

        # シーンにアイテムを追加する。
        self.scene().addItem(ellipseItem)
        # ---------------------------------------------------------------------


        # ラインアイテムの作成。-----------------------------------------------
        lineItem = QtGui.QGraphicsLineItem(160, 70, 280, 82)
        lineItem.setFlags(QtGui.QGraphicsItem.ItemIsMovable)
        lineText = TextItem('QGraphicsLineItem', lineItem)
        # ラインアイテムを(0, -10)座標に移動。
        lineText.setTransform(lineText.transform().translate(0, -10))

        # 青のQPenを作成し、太さを４に指定してラインアイテムに適応。
        pen = QtGui.QPen(QtGui.QColor(110, 140, 223))
        pen.setWidth(4)
        lineItem.setPen(pen)

        self.scene().addItem(lineItem)
        # ---------------------------------------------------------------------


        # パスアイテムを作成。-------------------------------------------------
        # QPainterPathオブジェクトを作成し、パスを作成する。
        path = QtGui.QPainterPath()
        path.addRect(20, 20, 60, 60)
        path.moveTo(0, 0)
        path.cubicTo(99, 0, 50, 50, 99, 99)
        path.cubicTo(0, 99, 50, 50, 0, 0)

        # 設定したパスオブジェクトをQGraphicsPathItemにセットして、実際の
        # アイテムとして描画できるようにする。
        pathItem = QtGui.QGraphicsPathItem(path)
        pathItem.setFlags(QtGui.QGraphicsItem.ItemIsMovable)
        pathItem.setTransform(QtGui.QTransform().translate(300, 30))
        pathText = TextItem('QGraphicsPathItem', pathItem)

        self.scene().addItem(pathItem)
        # ---------------------------------------------------------------------


        # ポリゴン（多角形）アイテムを作成する。-------------------------------
        # QPolygonFで多角形オブジェクトを作成する。
        polygon = QtGui.QPolygonF(
            [
                QtCore.QPointF(60, 0),
                QtCore.QPointF(120, 120),
                QtCore.QPointF(0, 120),
            ]
        )

        # 作成した多角形オブジェクトをQGraphicsPolygonItemにセットして、実際の
        # アイテムとして描画できるようにする。
        polyItem = QtGui.QGraphicsPolygonItem(polygon)
        polyItem.setFlags(QtGui.QGraphicsItem.ItemIsMovable)
        polyItem.setTransform(QtGui.QTransform().translate(160, 160))
        polyText = TextItem('QGraphicsPolygonItem', polyItem)

        self.scene().addItem(polyItem)
        # ---------------------------------------------------------------------


        # 矩形アイテムを作成する。---------------------------------------------
        rectItem = QtGui.QGraphicsRectItem(20, 180, 120, 80)
        rectItem.setFlags(QtGui.QGraphicsItem.ItemIsMovable)
        rectText = TextItem('QGraphicsRectItem', rectItem)

        # グラデーションを作成して矩形アイテムに適応。
        lGradient = QtGui.QLinearGradient(20, 180, 20, 260)
        lGradient.setColorAt(0.0, QtGui.QColor(128, 220, 190))
        lGradient.setColorAt(1.0, QtGui.QColor(68, 160, 122))
        rectItem.setBrush(lGradient)

        # QPenを作成して、矩形アイテムに適応。
        pen = QtGui.QPen(QtGui.QColor(196, 255, 220))
        pen.setWidth(4)
        rectItem.setPen(pen)

        self.scene().addItem(rectItem)
        # ---------------------------------------------------------------------


        # テキストアイテムを作成する。-----------------------------------------
        textItem = QtGui.QGraphicsTextItem('QGraphicsTextItem')
        textItem.setFont(QtGui.QFont('Arial Black', 9))
        textItem.setFlags(QtGui.QGraphicsItem.ItemIsMovable)

        # テキストアイテムはURL指定をして、そのURLを外部アプリで開くよう
        # 設定する事が可能。
        textItem.setOpenExternalLinks(True)
        textItem.setHtml(
            'QGraphicsTextItem'
        )
        textItem.setTransform(QtGui.QTransform().translate(300, 200))

        self.scene().addItem(textItem)
        # ---------------------------------------------------------------------

        # Pixmap（画像）アイテムを作成。---------------------------------------
        pixmapItem = QtGui.QGraphicsPixmapItem(
            QtGui.QPixmap(self.ImageFilePath)
        )
        pixmapRect = pixmapItem.boundingRect()
        # 目標幅 ／ Pixmapの幅からスケール値を換算。
        scaleRatio = 450 / pixmapRect.width()

        pixmapItem.setTransform(
            QtGui.QTransform()
                .translate(20, 300)
                .scale(scaleRatio, scaleRatio)
        )
        pixmapItem.setFlags(QtGui.QGraphicsItem.ItemIsMovable)
        pixmapText = TextItem('QGraphicsPixmapItem', pixmapItem)
        pixmapText.setTransform(
            pixmapText.transform().scale(
                1 / scaleRatio, 1 / scaleRatio,
            )
        )

        self.scene().addItem(pixmapItem)
        # ---------------------------------------------------------------------

    # マウス操作イベントのオーバーライドメソッド。=============================
    # マウスボタンクリック時のイベントのオーバーライド。
    def mousePressEvent(self, event):
        # マウスクリック時にAltキーが押されている場合は、ビュー操作モードの
        # 準備をする。
        if event.modifiers() == QtCore.Qt.AltModifier:
            # 現在のマウスポジションを取得し、クラス変数に保持する。
            self.__pos = event.posF()

            # マウス右ボタンをクリックしている場合はサイズカーソルを設定。
            if event.button() == QtCore.Qt.RightButton:
                cursorShape = QtCore.Qt.SizeAllCursor
            # それ意外の場合はハンドカーソルを設定。
            else:
                cursorShape = QtCore.Qt.OpenHandCursor

            QtGui.qApp.setOverrideCursor(QtGui.QCursor(cursorShape))

        # それ意外の場合はself.__posを空にしてデフォルトの動作を実行。
        else:
            self.__pos = None
            super(ItemViewer, self).mousePressEvent(event)

    # マウスドラッグ中のイベントのオーバーライド。
    def mouseMoveEvent(self, event):
        # self.__pos変数が空（マウスクリック時にAltキーが押されていない）場合
        # デフォルトの動作を実行して終了。
        if not self.__pos:
            super(ItemViewer, self).mouseMoveEvent(event)
            return

        # 現在の情報の取得。---------------------------------------------------
        # 現在のマウス位置。
        curPos = event.posF()
        # 現在のマウス位置からこのビューのシーン用に変換した矩形を割り出す。
        localRect = self.mapToScene(curPos.x(), curPos.y())
        # 現在とマウスクリック時のマウス位置の差分。
        delta = curPos - self.__pos
        # ---------------------------------------------------------------------


        # マウスが右クリックの場合はビュースケールメソッドを実行。
        if event.buttons() == QtCore.Qt.RightButton:
            # 移動差分が正の場合は拡大、負の場合は縮小値を入れる。
            if delta.x() >= 0:
                scaleRatio = 1.05
            else:
                scaleRatio = 0.95

            # ビューのトランスフォームマトリクスを一度ローカルのマウス上の
            # ポイントへ移動後スケールをかけ、再度元の場所に戻す。
            self.setTransform(
                self.transform()
                    .translate(localRect.x(), localRect.y())
                    .scale(scaleRatio, scaleRatio)
                    .translate(-localRect.x(), -localRect.y())
            )
            self.resizeSceneRect()

        # それ意外の場合はパンを実行。
        else:
            # ビューのトランスフォームマトリクスにマウス移動差分を指定した新規
            # トランスフォームマトリクスをかける。
            self.setTransform(
                self.transform() *
                QtGui.QTransform().translate(delta.x(), delta.y())
            )

        # 現在のマウス位置をクラス内変数に保持。
        self.__pos = curPos

    # マウスクリックを話した時に実行するイベントのオーバーライド。
    def mouseReleaseEvent(self, event):
        super(ItemViewer, self).mouseReleaseEvent(event)
        self.__pos = None
        QtGui.qApp.restoreOverrideCursor()

    # =========================================================================


    # キーボード操作のイベントのオーバーライド=================================
    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_A:
            self.fitView()
        else:
            super(ItemViewer, self).keyPressEvent(event)

    # =========================================================================

    def fitView(self):
        self.fitInView(
            self.scene().itemsBoundingRect(), QtCore.Qt.KeepAspectRatio
        )

    # 現在シーンにある全てのアイテムの矩形の任意の倍数の矩形をシーンに適応する。
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
        # =========================================================================


# /////////////////////////////////////////////////////////////////////////////
#                                                                            //
# /////////////////////////////////////////////////////////////////////////////




# いつもの起動コマンド。///////////////////////////////////////////////////////
'''
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    view = ItemViewer()
    view.show()

    sys.exit(app.exec_())
'''
 # /////////////////////////////////////////////////////////////////////////////