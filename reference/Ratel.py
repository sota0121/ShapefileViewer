# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 10:03:16 2017

@author: sota_masuda
"""

import os
from pathlib import Path
import sys
import configparser
import json
import math
import time
import shapefile
from PyQt5.Qt import *
from PyQt5.QtCore import *
import re
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from RatelPrj import RatelProject as RPJ

# //////////////////////////////////////////////////////////////
# *About Encode Decode Error
# http://hikm.hatenablog.com/entry/20130328/1364492471
# *About D&D on QGraphicsView doesnt work
# http://blawat2015.no-ip.com/~mieki256/diary/201506261.html
# http://ur0.pw/GJJT
# https://sites.google.com/site/qoopazero/home/qt/graphicsview_dropevent
# //////////////////////////////////////////////////////////////
'''
class RatelMain(QMainWindow):
    def __init__(self, parent = None):
        super(RatelMain, self).__init__(parent)
        self.initUI()

    def QuitRatel(self):
        self.saveWndInfo()
        qApp.quit()

    def showFileDlg(self):
        # 第二引数はダイアログのタイトル、第三引数は表示するパス
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')

        # fname[0]は選択したファイルのパス（ファイル名を含む）
        if fname[0]:
            # ファイル読み込み
            f = open(fname[0], 'r')

            # テキストエディタにファイル内容書き込み
            with f:
                data = f.read()
                self.opFilePath = data
                print(self.opFilePath)

    def initBar(self):
        # 終了アクション作成
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit App')
        exitAction.triggered.connect(self.QuitRatel)

        # 保存アクション作成
        saveAction = QAction('&Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save Project')
        saveAction.triggered.connect(qApp.quit)  # save関数を作ってconnectする

        # 設定アクション作成
        setAction = QAction('&Settings', self)
        setAction.setShortcut('Ctrl+,')
        setAction.setStatusTip('Open Settings')
        setAction.triggered.connect(self.showFileDlg)

        self.statusBar()

        # メニューバー作成
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(setAction)

    def initUI(self):
        # init menubar, statusbar ... etc
        self.initBar()

        # Loadini
        initInfo = iniLoader()

        # init window info
        if initInfo.empty():
            self.setGeometry(300, 300, 500, 500)
        else:
            x = initInfo.x
            y = initInfo.y
            wid = initInfo.wid
            height = initInfo.height
            self.setGeometry(x, y, wid, height)

        # init title
        self.setWindowFilePath('Ratel')

        # set view and buttons(with vertical)
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        #vbox.addWidget(RatelView(self))
        textbox = QPlainTextEdit()
        ok = QPushButton("OK")
        vbox.addWidget(textbox)
        vbox.addWidget(ok)
        self.setLayout(vbox)

        # set view
        self.graphicsView = RatelView(self)


    def saveWndInfo(self):
        # get window size info
        rect = self.geometry()

        # init value
        inifile = configparser.ConfigParser()
        inifile['App'] = {'WND_X':'-1','WND_Y':'-1',
                          'WND_WID':'-1','WND_HGT':'-1'}

        # save
        inifile['App']['WND_X'] = str(rect.x())
        inifile['App']['WND_Y'] = str(rect.y())
        inifile['App']['WND_WID'] = str(rect.width())
        inifile['App']['WND_HGT'] = str(rect.height())
        with open('./config.ini', 'w') as configfile:
            inifile.write(configfile)

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
        model = self.

'''

class RatelMain(QWidget):
    def __init__(self):
        super(RatelMain, self).__init__()
        self.initUI()

    def initUI(self):
        # D&D setting
        #self.setAcceptDrops(True)

        # Create Buttons
        self.okBtn = QPushButton("OK")
        self.quitBtn = QPushButton("Quit(Ctrl+Q)")

        # set actions to buttons
        # --Exit action => quitBtn
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit App')
        exitAction.triggered.connect(self.QuitRatel)
        self.addAction(exitAction)
        self.quitBtn.clicked.connect(self.QuitRatel)

        # CreateView
        self.graphicsView = RatelView()

        # layout
        hbox = QHBoxLayout()
        hbox.addWidget(self.okBtn)
        hbox.addWidget(self.quitBtn)
        # view and buttons
        vbox = QVBoxLayout()
        vbox.addWidget(self.graphicsView)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        # set window geometry from history
        # --Loadini
        initInfo = iniLoader()

        # --init window info
        if initInfo.empty():
            self.setGeometry(300, 300, 500, 500)
        else:
            x = initInfo.x
            y = initInfo.y
            wid = initInfo.wid
            height = initInfo.height
            self.setGeometry(x, y, wid, height)

        # init title
        self.setWindowFilePath('Ratel')


    def QuitRatel(self):
        self.saveWndInfo()
        self.graphicsView.scene().OutputPrj()
        qApp.quit()

    def saveWndInfo(self):
        # get window size info
        rect = self.geometry()

        # init value
        inifile = configparser.ConfigParser()
        inifile['App'] = {'WND_X': '-1', 'WND_Y': '-1',
                          'WND_WID': '-1', 'WND_HGT': '-1'}
        # save
        inifile['App']['WND_X'] = str(rect.x())
        inifile['App']['WND_Y'] = str(rect.y())
        inifile['App']['WND_WID'] = str(rect.width())
        inifile['App']['WND_HGT'] = str(rect.height())
        with open('./config.ini', 'w') as configfile:
            inifile.write(configfile)



class RatelView(QGraphicsView):
    def __init__(self):
        super(RatelView, self).__init__()
        # D&D setting
        self.setAcceptDrops(True)

        # QGraphicsScene setting
        scene = RatelScene(self)
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

class RatelScene(QGraphicsScene):
    def __init__(self, *argv, **keywords):
        super(RatelScene, self).__init__(*argv, **keywords)
        self.project = RPJ()
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


class iniLoader():
    def __init__(self):
        self.x = -1
        self.y = -1
        self.wid = -1
        self.height = -1
        self.Load()

    def Load(self):
        inifile = configparser.ConfigParser()
        inifile.read('./config.ini')
        if 'App' in inifile:
            appsection = inifile['App']
            if 'WND_X' in appsection:
                self.x = inifile.getint('App', 'WND_X')
            if 'WND_Y' in appsection:
                self.y = inifile.getint('App', 'WND_Y')
            if 'WND_WID' in appsection:
                self.wid = inifile.getint('App', 'WND_WID')
            if 'WND_HGT' in appsection:
                self.height = inifile.getint('App', 'WND_HGT')


    def empty(self):
        if -1 == self.x:
            return True
        if -1 == self.y:
            return True
        if -1 == self.wid:
            return True
        if -1 == self.height:
            return True
        else:
            return False



            # //////////////////////////////////////////////////////////////
def main():
    app = QApplication(sys.argv)
    Ratel = RatelMain()
    Ratel.show()
    sys.exit(app.exec_())

# main
if __name__ == '__main__':
    main()



