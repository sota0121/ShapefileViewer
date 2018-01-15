# -*- coding: utf-8 -*-
"""
@author: sota_masuda
python 3.6
"""
import configparser

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