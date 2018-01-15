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
        exitAction.triggered.connect(self.QuitRatel)
        self.addAction(exitAction)
        self.quitBtn.clicked.connect(self.QuitRatel)

        # CreateView
        self.graphicsView = SVview.svView()

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


def main():
    app = QApplication(sys.argv)
    Ratel = MainWindow()
    Ratel.show()
    sys.exit(app.exec_())

# main
if __name__ == '__main__':
    main()