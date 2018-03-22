# -*- coding: utf-8 -*-
"""
@author: sota_masuda
python 3.6
"""
# SYSTEM IMPORT-----------------
import os
import sys

# EXLIB IMPORT-------------------
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import configparser

# THIS PACK IMPORT
import SVview
import OperateINI
import SVutil as utl

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        # D&D setting
        # self.setAcceptDrops(True)

        # Create Buttons
        self.okBtn = QPushButton("OK")
        self.quitBtn = QPushButton("Quit(Ctrl+Q)")

        # set actions to buttons
        # --Exit action => quitBtn
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit App')
        exitAction.triggered.connect(self.QuitWindow)
        self.addAction(exitAction)
        self.quitBtn.clicked.connect(self.QuitWindow)

        # Create Status bar
        self.statusbar = QStatusBar()
        self.statusbar.showMessage('Ready')

        # CreateView
        self.graphicsView = SVview.svView()
        self.graphicsView.linkStatusbar(self.statusbar)

        # layout
        hbox = QHBoxLayout()
        hbox.addWidget(self.okBtn)
        hbox.addWidget(self.quitBtn)
        # widgets
        vbox = QVBoxLayout()
        vbox.addWidget(self.graphicsView)
        vbox.addLayout(hbox)
        vbox.addWidget(self.statusbar)
        self.setLayout(vbox)

        # set window geometry from history
        # --Loadini
        initInfo = OperateINI.iniLoader()
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
        self.setWindowFilePath('ShapefileViewer')
        self.setWindowIcon(QIcon('img/panda_icon.png'))

        # Revert View
        self.graphicsView.RevertView(initInfo)

        # status bar


    def QuitWindow(self):
        self.saveWndInfo()
        self.graphicsView.scene().OutputPrj()
        qApp.quit()

    def saveWndInfo(self):
        # get window size info
        rect = self.geometry()

        # get last zoom
        zoom = self.graphicsView.zoom
        zoomValue = self.graphicsView.zoomValue

        # get last scrollbar
        scrollBar_x = self.graphicsView.horizontalScrollBar().value()
        scrollBar_y = self.graphicsView.verticalScrollBar().value()

        # get move vector of Base map
        mv_base_x = self.graphicsView.mvObjVector.x()
        mv_base_y = self.graphicsView.mvObjVector.y()

        # init value
        inifile = configparser.ConfigParser()
        inifile['App'] = {'WND_X': '-1', 'WND_Y': '-1',
                          'WND_WID': '-1', 'WND_HGT': '-1',
                          'ZOOM': '0.0', 'ZOOM_VAL': '100',
                          'SCROLBAR_X': '0','SCROLBAR_Y':'0',
                          'MV_BASE_X': '0.0','MV_BASE_Y': '0.0'}
        # save
        inifile['App']['WND_X'] = str(rect.x())
        inifile['App']['WND_Y'] = str(rect.y())
        inifile['App']['WND_WID'] = str(rect.width())
        inifile['App']['WND_HGT'] = str(rect.height())
        inifile['App']['ZOOM'] = '{:.2f}'.format(zoom)
        inifile['App']['ZOOM_VAL'] = '{:.2f}'.format(zoomValue)
        inifile['App']['SCROLBAR_X'] = str(scrollBar_x)
        inifile['App']['SCROLBAR_Y'] = str(scrollBar_y)
        inifile['App']['MV_BASE_X'] = '{:.2f}'.format(mv_base_x)
        inifile['App']['MV_BASE_Y'] = '{:.2f}'.format(mv_base_y)
        with open('./config.ini', 'w') as configfile:
            inifile.write(configfile)


def main():
    app = QApplication(sys.argv)
    Ratel = MainWindow()
    Ratel.show()
    sys.exit(app.exec_())

# main
if __name__ == '__main__':
    main()