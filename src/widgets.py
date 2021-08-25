# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 12:18:35 2021

@author: domen
"""
from PyQt5.QtWidgets import QLabel
from PyQt5.QtMultimedia import QMediaContent,QMediaPlayer
from PyQt5.QtCore import QDir,QUrl

class PlayAudioLabel(QLabel):
    
    def __init__(self, widget):
        super(PlayAudioLabel, self).__init__(widget)
        self.main = widget
        self.path = ''
        
    def mousePressEvent(self, event):
        # print('test')
        fullpath = QDir.current().absoluteFilePath(self.path) 
        url = QUrl.fromLocalFile(fullpath)
        content = QMediaContent(url)
        self.player = QMediaPlayer()
        self.player.setMedia(content)
        self.player.play()
        # self.main.get(event.pos())