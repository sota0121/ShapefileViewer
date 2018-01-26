# -*- coding: utf-8 -*-
"""
@author: sota_masuda
python 3.6
"""
import configparser
import SVutil as utl

class iniLoader():
    def __init__(self):
        self.x = -1
        self.y = -1
        self.wid = -1
        self.height = -1
        self.zoom = 0.0
        self.scrollbar_x = 0
        self.scrollbar_y = 0
        self.mv_base_x = 0.0
        self.mv_base_y = 0.0
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
            if 'ZOOM' in appsection:
                self.zoom = inifile.getfloat('App', 'ZOOM')
            if 'MV_BASE_X' in appsection:
                self.mv_base_x = inifile.getfloat('App', 'MV_BASE_X')
            if 'MV_BASE_Y' in appsection:
                self.mv_base_y = inifile.getfloat('App', 'MV_BASE_Y')


    def empty(self):
        if -1 == self.x:
            return True
        if -1 == self.y:
            return True
        if -1 == self.wid:
            return True
        if -1 == self.height:
            return True
        if 0.0 == self.zoom:
            return True
        else:
            return False