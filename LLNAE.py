# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'old.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from settings import WindowSettings,DeckSettings
from calibrate_screen import *
from LLNSaver import *
from state_machine import *

class DeckViewer():
    def __init__(self,DeckSettings):
        self.deck_set = DeckSettings
        self.empty = True
        self.idx = 1
        self.n_cards = 0
        self.card_number = 1
        self.im_path =''
        self.ph_path =''
        self.sub_path =''
        
    def check_favorite(self):
        favorite = False
        
        with open(self.deck_set.path+'favorites.cfg') as f:
            lines = f.readlines()
            
        for line in lines:            
            vals = line.split(' ')
            indx = int(vals[0])
            if indx == self.idx:                
                favorite = int(vals[1])
        return favorite
        
    def save_favorite(self,val):
        with open(self.deck_set.path+'favorites.cfg') as f:
            lines = f.readlines()   
        for indx in lines:
            if indx == self.idx:
                favorite = indx.split(' ')
                favorite[1] = val
                lines[indx] = favorite[0] + ' ' + str(favorite[1])
        
        with open(self.deck_set.path+'favorites.cfg','w') as f:
            f.writelines(lines)
            
        
        
    def load_picture(self,mode=''):
        
        start_idx = self.idx
        
        if mode == 'init':
            list_of_files = filter( os.path.isfile,
                          glob.glob(self.deck_set.path + 'images/' + '*') )
            list_of_files = sorted( list_of_files,
                                  key = os.path.getmtime)
            
            start_idx = list_of_files[0]       
            start_idx = int(start_idx[28+len(self.deck_set.deck):-4])

        
        self.im_path = self.deck_set.path + 'images/LLNi-{}-{}.png'.format(self.deck_set.deck,start_idx)
        self.ph_path = self.deck_set.path + 'phrases/LLNp-{}-{}.png'.format(self.deck_set.deck,start_idx)
        self.sub_path = self.deck_set.path + 'trans/LLNt-{}-{}.png'.format(self.deck_set.deck,start_idx)
        
        self.idx = max(start_idx,0) 
        idx = self.idx
        

        
        if os.path.isfile(self.im_path) and os.path.isfile(self.ph_path) and os.path.isfile(self.sub_path):
            return [self.im_path,self.ph_path,self.sub_path,idx]
        else:
            return ['','','',idx]
        
    def get_next_picture(self,direction=0,mode='standard',deletion=0):
        
        # loop around 0->-1 
        
        # get first and last index
        list_of_files = filter( os.path.isfile,
                      glob.glob(self.deck_set.path + 'images/' + '*') )
        list_of_files = sorted( list_of_files,
                              key = os.path.getmtime)
        
        first_index = list_of_files[0]     
        first_index = int(first_index[28+len(self.deck_set.deck):-4])
        
        last_index = list_of_files[-1]
        last_index = int(last_index[28+len(self.deck_set.deck):-4])
        
        start_idx = self.idx
        img_found = False
        
        while not img_found:
            
            if start_idx == first_index and direction == -1:
                start_idx = last_index
                self.im_path = self.deck_set.path + 'images/LLNi-{}-{}.png'.format(self.deck_set.deck,start_idx)
                self.ph_path = self.deck_set.path + 'phrases/LLNp-{}-{}.png'.format(self.deck_set.deck,start_idx)
                self.sub_path = self.deck_set.path + 'trans/LLNt-{}-{}.png'.format(self.deck_set.deck,start_idx)
                self.card_number = self.n_cards
                break
            
            elif start_idx == last_index and direction == 1:
                start_idx = first_index
                self.im_path = self.deck_set.path + 'images/LLNi-{}-{}.png'.format(self.deck_set.deck,start_idx)
                self.ph_path = self.deck_set.path + 'phrases/LLNp-{}-{}.png'.format(self.deck_set.deck,start_idx)
                self.sub_path = self.deck_set.path + 'trans/LLNt-{}-{}.png'.format(self.deck_set.deck,start_idx)
                self.card_number = 1
                break
            
            start_idx = start_idx+direction
            self.im_path = self.deck_set.path + 'images/LLNi-{}-{}.png'.format(self.deck_set.deck,start_idx)
            self.ph_path = self.deck_set.path + 'phrases/LLNp-{}-{}.png'.format(self.deck_set.deck,start_idx)
            self.sub_path = self.deck_set.path + 'trans/LLNt-{}-{}.png'.format(self.deck_set.deck,start_idx)
            
            if os.path.isfile(self.im_path) and os.path.isfile(self.ph_path) and os.path.isfile(self.sub_path):
                img_found = True
                self.card_number = self.card_number + direction - deletion
        
        self.idx = start_idx

        if os.path.isfile(self.im_path) and os.path.isfile(self.ph_path) and os.path.isfile(self.sub_path):
            return [self.im_path,self.ph_path,self.sub_path,self.idx]
        else:
            return ['','','',self.idx]
        



class StateMachineWorker(QObject):
    
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    def __init__(self,state_machine):
        super(StateMachineWorker, self).__init__()
        self.sm = state_machine        

    def run(self):

        self.sm.mode_loop()
        return


class Ui_MainWindow(object):
    
    #----------------- VIEWER --------------------------
    
    def reset_msg_clicked(self,choice):
        

        # reload values in statemachine and deckviewer
        if choice.text() == 'OK':                
            self.deck_viewer.deck_set.set_index(0)
            self.sm.saver.de.set_index(0)
            
            dir = self.deck_viewer.deck_set.path + 'images'
            for f in os.listdir(dir):
                os.remove(os.path.join(dir, f))
            dir = self.deck_viewer.deck_set.path + 'phrases'
            for f in os.listdir(dir):
                os.remove(os.path.join(dir, f))
            dir = self.deck_viewer.deck_set.path + 'trans'
            for f in os.listdir(dir):
                os.remove(os.path.join(dir, f))
            print('++ Index reset to 0. All images deleted')
            
            self.deckPhoto.setPixmap(QtGui.QPixmap('app_data/images/blank.png'))
            self.deckPhraseLabel.setPixmap(QtGui.QPixmap('app_data/images/white.png'))
            self.deckSubLabel.setPixmap(QtGui.QPixmap('app_data/images/white.png'))
            self.label_7.setText('Card #{} of {}'.format(0,0))
            
        else:
            print('-- Aborted')
            
    def delete_phrase_clicked(self):  
      
        os.remove(self.deck_viewer.im_path)
        os.remove(self.deck_viewer.ph_path)
        os.remove(self.deck_viewer.sub_path)
        self.deck_viewer.n_cards = self.deck_viewer.n_cards -1
        [im_path,ph_path,sub_path,idx] = self.deck_viewer.get_next_picture(direction=1,deletion = 1)  
        if not im_path == '':
            self.deckPhoto.setPixmap(QtGui.QPixmap(im_path))
            self.deckPhraseLabel.setPixmap(QtGui.QPixmap(ph_path))
            self.deckSubLabel.setPixmap(QtGui.QPixmap(sub_path))
        self.label_7.setText('Card #{} of {}'.format(self.deck_viewer.card_number,self.deck_viewer.n_cards))
        
        
    
    def reset_deck_clicked(self):
        
        qm = QMessageBox()
        qm.setWindowTitle('Warning')
        qm.setText('Are you sure you want to delete all {} flashcards?'.format(self.deck_viewer.n_cards))
        qm.setIcon(QMessageBox.Question)
        qm.setStandardButtons(QMessageBox.Ok|QMessageBox.Cancel)
        qm.buttonClicked.connect(self.reset_msg_clicked)
        x = qm.exec_()
    
    def next_image_clicked(self):
        
        [im_path,ph_path,sub_path,idx] = self.deck_viewer.get_next_picture(direction=1)
        
        if not im_path == '':
            self.deckPhoto.setPixmap(QtGui.QPixmap(im_path))
            self.deckPhraseLabel.setPixmap(QtGui.QPixmap(ph_path))
            self.deckSubLabel.setPixmap(QtGui.QPixmap(sub_path))
            
            self.label_7.setText('Card #{} of {}'.format(self.deck_viewer.card_number,self.deck_viewer.n_cards))
            
            fav_val = self.deck_viewer.check_favorite()
            if fav_val:
                    self.label_2.resize(25,25)
                    self.importantCardCheck.setChecked(True)                 
            else:                
                    self.label_2.resize(25,0)
                    self.importantCardCheck.setChecked(False)
            
    
    def prev_image_clicked(self):
        
        [im_path,ph_path,sub_path,idx] = self.deck_viewer.get_next_picture(direction=-1)
        
        if not im_path == '':
            self.deckPhoto.setPixmap(QtGui.QPixmap(im_path))
            self.deckPhraseLabel.setPixmap(QtGui.QPixmap(ph_path))
            self.deckSubLabel.setPixmap(QtGui.QPixmap(sub_path))
            
            self.label_7.setText('Card #{} of {}'.format(self.deck_viewer.card_number,self.deck_viewer.n_cards))
        
            fav_val = self.deck_viewer.check_favorite()
            if fav_val:
                    self.label_2.resize(25,25)
                    self.importantCardCheck.setChecked(True)                   
            else:                
                    self.label_2.resize(25,0)
                    self.importantCardCheck.setChecked(False)
        
    def update_show_translation(self):
        if self.showTranslationCheck.isChecked():
            self.deckSubLabel.setPixmap(QtGui.QPixmap(self.deck_viewer.sub_path))
        else:                
            self.deckSubLabel.clear()

    def update_favorite(self):
        if self.importantCardCheck.isChecked():
            with open(self.deck_viewer.im_path) as f:
                f.fileinfo = {'favorite': 'yes'}
                self.label_2.resize(25,25)
                
        else:                
            with open(self.deck_viewer.im_path) as f:
                f.fileinfo = {'favorite': 'no'}
                self.label_2.resize(25,0)
                
                    
        self.deck_viewer.save_favorite(self.importantCardCheck.isChecked())
            
    #----------------- RECORDER --------------------------
    
    
    def update_deck_select(self):
        selected_deck =  self.deckSelectBox.currentText()
        if not selected_deck == '-':
            self.sm.saver.de.load_params(selected_deck)
            self.selected_deck = selected_deck
            self.valid_deck = True
            print(self.sm.saver.de.og_lang)
            self.originalLanguageLineEdit.setText(self.sm.saver.de.og_lang)
            self.translationLineEdit.setText(self.sm.saver.de.trans_lang)
            print('Valid deck selected')
        else:
            self.valid_deck = False
            print('Invalid deck selected')
            
    def update_recording_mode(self):
        self.sm.mode = self.recordingModeBox.currentText()
        print(self.sm.mode)
              
    def update_resolution(self):
        self.sm.saver.wp.res = int(self.resolutionBox.currentText())/2160
        print('New res: {}'.format(self.sm.saver.wp.res))
    

        
    
    # widget triggers
    def reportProgress(self, n):
        self.stepLabel.setText(f"Long-Running Step: {n}")
    
    def runLongTask(self):
        """Long-running task in 5 steps."""
        for i in range(5):
            sleep(1)
            self.reportProgress(i + 1)
            
    # def deck_select_clicked(self):
        


    def new_deck_clicked(self):
        return
    
    def calibrate_clicked(self):
        # calibrate_popup = calibrateDialog('Text',self)
        start_calibration()
        self.update_user_cfg()
        
    def deck_select_clicked(self):
        self.deck_viewer = DeckViewer(self.sm.saver.de)
        [im_path,ph_path,sub_path,idx] = self.deck_viewer.load_picture(mode='init')
        
        if not im_path == '':
            self.deckPhoto.setPixmap(QtGui.QPixmap(im_path))
            self.deckPhraseLabel.setPixmap(QtGui.QPixmap(ph_path))
            self.deckSubLabel.setPixmap(QtGui.QPixmap(sub_path))
            
        list_of_files = filter( os.path.isfile,
                      glob.glob(self.deck_viewer.deck_set.path + 'images/' + '*') )
        list_of_files = sorted( list_of_files,
                              key = os.path.getmtime)
        self.deck_viewer.n_cards = len(list_of_files)
        self.label_7.setText('Card #1 of {}'.format(self.deck_viewer.n_cards))
        
            
            
        return
        
    def stop_recording_clicked(self):
        self.sm_worker.sm.shutdown_req = True
        if not isinstance(self.sm_worker.sm.listener, list):
            self.sm_worker.sm.listener.stop()        
        
        self.startRecorderButton.setEnabled(True)
        self.stopRecorderButton.setEnabled(False)
        
    def start_recording_clicked(self):
        if self.valid_deck:
            print('Attempting to start recording in {} mode'.format(self.sm.mode))
            # create record thread
            self.sm.shutdown_req = False
            self.sm_worker = StateMachineWorker(self.sm)
            self.sm_worker.moveToThread(self.qthread)
            self.qthread.started.connect(self.sm_worker.run)
            self.sm_worker.finished.connect(self.qthread.quit)
            self.sm_worker.finished.connect(self.sm_worker.deleteLater)
            self.qthread.finished.connect(self.qthread.deleteLater)
            self.sm_worker.progress.connect(self.reportProgress)
            self.qthread.start()
            
            self.startRecorderButton.setEnabled(False)
            self.stopRecorderButton.setEnabled(True)
            
        else:
            print('Select a valid deck first.')
            
        

        
    def load_decks(self,MainWindow):
        _translate = QtCore.QCoreApplication.translate
        deck_list = next(os.walk('data/'))[1]
        # print(deck_list)
        for idx,deck in enumerate(deck_list):
            self.deckSelectBox.addItem(deck)
            self.deckSelectBox.setItemText(idx+1, _translate("MainWindow", str(deck)))
    
    def update_user_cfg(self,profile=0):
        
        def create_cfg_str(val1,val2=['','']):
            x0 = val1[0]
            y0 = val1[1]
            x1 = val1[0]
            y1 = val2[1]
            return  '{}:{}-{}:{}'.format(x0,y0,x1,y1)   
    
        self.videoPositionLineEdit.setText(create_cfg_str(self.sm.saver.wp.nflix_ul,self.sm.saver.wp.nflix_br))
        self.phrasePositionLineEdit.setText(create_cfg_str(self.sm.saver.wp.phrase_ul,self.sm.saver.wp.phrase_br))
        self.subtitlePositionLineEdit.setText(create_cfg_str(self.sm.saver.wp.trans_ul,self.sm.saver.wp.trans_br))
        self.cursorApPositionLineEdit.setText(create_cfg_str(self.sm.saver.wp.cursor_pos,self.sm.saver.wp.AP_pos))
            


    #----------------- INITIALIZE  --------------------------
        
    def initialize_settings(self):
        # load in user config
        # load in decks
        self.valid_deck = False
        self.selected_deck = '-'
        self.load_decks(self)
        self.qthread = QThread()
        return
    
    def init_events(self):
        # create instances
        self.win_set = WindowSettings('full','1080',0)
        self.deck_set = DeckSettings('', '', '',False)        
        self.saver = LLNSaver(self.deck_set,self.win_set)
        self.sm = StateMachine(self.saver,self.win_set.mode)  
        
        self.initialize_settings()
        
        
        # buttons
        self.calibrateButton.clicked.connect(self.calibrate_clicked)
        self.startRecorderButton.clicked.connect(self.start_recording_clicked)
        self.stopRecorderButton.clicked.connect(self.stop_recording_clicked)
        self.selectDeckButton.clicked.connect(self.deck_select_clicked)
        self.nextImageButton.clicked.connect(self.next_image_clicked)       
        self.previousImageButton.clicked.connect(self.prev_image_clicked)   
        self.resetDeckButton.clicked.connect(self.reset_deck_clicked)
        self.deletePhraseButton.clicked.connect(self.delete_phrase_clicked)
        
        # boxes
        self.resolutionBox.currentIndexChanged.connect(self.update_resolution)
        self.recordingModeBox.currentIndexChanged.connect(self.update_recording_mode)
        self.deckSelectBox.currentIndexChanged.connect(self.update_deck_select)
        
        # checks
        self.showTranslationCheck.stateChanged.connect(self.update_show_translation)
        self.importantCardCheck.stateChanged.connect(self.update_favorite)
        
        
        
    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(430, 923)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setEnabled(True)
        self.tabWidget.setGeometry(QtCore.QRect(20, 200, 391, 701))
        self.tabWidget.setDocumentMode(False)
        self.tabWidget.setObjectName("tabWidget")
        self.recordTab = QtWidgets.QWidget()
        self.recordTab.setObjectName("recordTab")
        self.frame = QtWidgets.QFrame(self.recordTab)
        self.frame.setGeometry(QtCore.QRect(20, 20, 371, 641))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.groupBox = QtWidgets.QGroupBox(self.frame)
        self.groupBox.setGeometry(QtCore.QRect(0, 180, 371, 231))
        self.groupBox.setObjectName("groupBox")
        self.label_19 = QtWidgets.QLabel(self.groupBox)
        self.label_19.setGeometry(QtCore.QRect(20, 70, 131, 21))
        self.label_19.setObjectName("label_19")
        self.label_8 = QtWidgets.QLabel(self.groupBox)
        self.label_8.setGeometry(QtCore.QRect(20, 130, 171, 19))
        self.label_8.setObjectName("label_8")
        self.label_16 = QtWidgets.QLabel(self.groupBox)
        self.label_16.setGeometry(QtCore.QRect(20, 40, 111, 21))
        self.label_16.setObjectName("label_16")
        self.label_21 = QtWidgets.QLabel(self.groupBox)
        self.label_21.setGeometry(QtCore.QRect(20, 100, 141, 21))
        self.label_21.setObjectName("label_21")
        self.subtitlePositionLineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.subtitlePositionLineEdit.setGeometry(QtCore.QRect(200, 100, 121, 25))
        self.subtitlePositionLineEdit.setObjectName("subtitlePositionLineEdit")
        self.cursorApPositionLineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.cursorApPositionLineEdit.setGeometry(QtCore.QRect(200, 130, 121, 25))
        self.cursorApPositionLineEdit.setObjectName("cursorApPositionLineEdit")
        self.videoPositionLineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.videoPositionLineEdit.setGeometry(QtCore.QRect(200, 40, 121, 25))
        self.videoPositionLineEdit.setObjectName("videoPositionLineEdit")
        self.phrasePositionLineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.phrasePositionLineEdit.setGeometry(QtCore.QRect(200, 70, 121, 25))
        self.phrasePositionLineEdit.setObjectName("phrasePositionLineEdit")
        self.splitter = QtWidgets.QSplitter(self.groupBox)
        self.splitter.setGeometry(QtCore.QRect(20, 180, 301, 34))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.trySettingsButton = QtWidgets.QPushButton(self.splitter)
        self.trySettingsButton.setObjectName("trySettingsButton")
        self.calibrateButton = QtWidgets.QPushButton(self.splitter)
        self.calibrateButton.setObjectName("calibrateButton")
        self.groupBox_2 = QtWidgets.QGroupBox(self.frame)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 420, 371, 111))
        self.groupBox_2.setObjectName("groupBox_2")
        self.resolutionBox = QtWidgets.QComboBox(self.groupBox_2)
        self.resolutionBox.setGeometry(QtCore.QRect(170, 40, 141, 21))
        self.resolutionBox.setObjectName("resolutionBox")
        self.resolutionBox.addItem("")
        self.resolutionBox.addItem("")
        self.label_15 = QtWidgets.QLabel(self.groupBox_2)
        self.label_15.setGeometry(QtCore.QRect(10, 40, 81, 16))
        self.label_15.setObjectName("label_15")
        self.recordingModeBox = QtWidgets.QComboBox(self.groupBox_2)
        self.recordingModeBox.setGeometry(QtCore.QRect(170, 70, 141, 25))
        self.recordingModeBox.setObjectName("recordingModeBox")
        self.recordingModeBox.addItem("")
        self.recordingModeBox.addItem("")
        self.recordingModeBox.addItem("")
        self.label_17 = QtWidgets.QLabel(self.groupBox_2)
        self.label_17.setGeometry(QtCore.QRect(10, 70, 141, 21))
        self.label_17.setObjectName("label_17")
        self.groupBox_3 = QtWidgets.QGroupBox(self.frame)
        self.groupBox_3.setGeometry(QtCore.QRect(0, 10, 371, 161))
        self.groupBox_3.setObjectName("groupBox_3")
        self.translationLineEdit = QtWidgets.QLineEdit(self.groupBox_3)
        self.translationLineEdit.setGeometry(QtCore.QRect(202, 60, 121, 25))
        self.translationLineEdit.setObjectName("translationLineEdit")
        self.label_10 = QtWidgets.QLabel(self.groupBox_3)
        self.label_10.setGeometry(QtCore.QRect(20, 60, 171, 19))
        self.label_10.setObjectName("label_10")
        self.originalLanguageLineEdit = QtWidgets.QLineEdit(self.groupBox_3)
        self.originalLanguageLineEdit.setGeometry(QtCore.QRect(202, 30, 121, 25))
        self.originalLanguageLineEdit.setObjectName("originalLanguageLineEdit")
        self.label_9 = QtWidgets.QLabel(self.groupBox_3)
        self.label_9.setGeometry(QtCore.QRect(20, 40, 171, 19))
        self.label_9.setObjectName("label_9")
        self.applyDeckChangesButton = QtWidgets.QPushButton(self.groupBox_3)
        self.applyDeckChangesButton.setGeometry(QtCore.QRect(20, 100, 148, 34))
        self.applyDeckChangesButton.setObjectName("applyDeckChangesButton")
        self.label_18 = QtWidgets.QLabel(self.frame)
        self.label_18.setGeometry(QtCore.QRect(20, 520, 141, 21))
        self.label_18.setObjectName("label_18")
        self.subtitleModeBox = QtWidgets.QComboBox(self.frame)
        self.subtitleModeBox.setGeometry(QtCore.QRect(180, 520, 141, 25))
        self.subtitleModeBox.setObjectName("subtitleModeBox")
        self.subtitleModeBox.addItem("")
        self.subtitleModeBox.addItem("")
        self.splitter_8 = QtWidgets.QSplitter(self.frame)
        self.splitter_8.setGeometry(QtCore.QRect(20, 570, 301, 34))
        self.splitter_8.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_8.setObjectName("splitter_8")
        self.startRecorderButton = QtWidgets.QPushButton(self.splitter_8)
        self.startRecorderButton.setObjectName("startRecorderButton")
        self.stopRecorderButton = QtWidgets.QPushButton(self.splitter_8)
        self.stopRecorderButton.setObjectName("stopRecorderButton")
        self.tabWidget.addTab(self.recordTab, "")
        self.viewTab = QtWidgets.QWidget()
        self.viewTab.setObjectName("viewTab")
        self.label_7 = QtWidgets.QLabel(self.viewTab)
        self.label_7.setGeometry(QtCore.QRect(140, 370, 111, 20))
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.deckSubLabel = QtWidgets.QLabel(self.viewTab)
        self.deckSubLabel.setGeometry(QtCore.QRect(30, 260, 331, 31))
        self.deckSubLabel.setText("")
        self.deckSubLabel.setPixmap(QtGui.QPixmap("data/c.png"))
        self.deckSubLabel.setScaledContents(True)
        self.deckSubLabel.setObjectName("deckSubLabel")
        self.deckPhoto = QtWidgets.QLabel(self.viewTab)
        self.deckPhoto.setGeometry(QtCore.QRect(20, 40, 351, 171))
        self.deckPhoto.setText("")
        self.deckPhoto.setPixmap(QtGui.QPixmap("data/a.png"))
        self.deckPhoto.setScaledContents(True)
        self.deckPhoto.setObjectName("deckPhoto")
        self.deckPhraseLabel = QtWidgets.QLabel(self.viewTab)
        self.deckPhraseLabel.setGeometry(QtCore.QRect(30, 220, 331, 31))
        self.deckPhraseLabel.setText("")
        self.deckPhraseLabel.setPixmap(QtGui.QPixmap("data/b.png"))
        self.deckPhraseLabel.setScaledContents(True)
        self.deckPhraseLabel.setObjectName("deckPhraseLabel")
        self.groupBox_4 = QtWidgets.QGroupBox(self.viewTab)
        self.groupBox_4.setEnabled(True)
        self.groupBox_4.setGeometry(QtCore.QRect(0, 410, 381, 91))
        self.groupBox_4.setObjectName("groupBox_4")
        self.showTranslationCheck = QtWidgets.QCheckBox(self.groupBox_4)
        self.showTranslationCheck.setGeometry(QtCore.QRect(10, 30, 211, 23))
        self.showTranslationCheck.setChecked(True)
        self.showTranslationCheck.setObjectName("showTranslationCheck")
        self.importantCardCheck = QtWidgets.QCheckBox(self.groupBox_4)
        self.importantCardCheck.setGeometry(QtCore.QRect(10, 50, 251, 23))
        self.importantCardCheck.setObjectName("importantCardCheck")
        self.label = QtWidgets.QLabel(self.viewTab)
        self.label.setGeometry(QtCore.QRect(10, 510, 131, 19))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.viewTab)
        self.label_2.setEnabled(True)
        self.label_2.setGeometry(QtCore.QRect(20, 40, 0, 25))
        self.label_2.setAutoFillBackground(False)
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap("app_data/images/star.png"))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName("label_2")
        self.deckDescriptionTextEdit = QtWidgets.QPlainTextEdit(self.viewTab)
        self.deckDescriptionTextEdit.setGeometry(QtCore.QRect(10, 546, 371, 111))
        self.deckDescriptionTextEdit.setObjectName("deckDescriptionTextEdit")
        self.previousImageButton = QtWidgets.QPushButton(self.viewTab)
        self.previousImageButton.setGeometry(QtCore.QRect(10, 310, 61, 34))
        self.previousImageButton.setObjectName("previousImageButton")
        self.nextImageButton = QtWidgets.QPushButton(self.viewTab)
        self.nextImageButton.setGeometry(QtCore.QRect(314, 310, 61, 34))
        self.nextImageButton.setObjectName("nextImageButton")
        self.splitter_10 = QtWidgets.QSplitter(self.viewTab)
        self.splitter_10.setGeometry(QtCore.QRect(80, 310, 224, 34))
        self.splitter_10.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_10.setObjectName("splitter_10")
        self.deletePhraseButton = QtWidgets.QPushButton(self.splitter_10)
        self.deletePhraseButton.setObjectName("deletePhraseButton")
        self.resetDeckButton = QtWidgets.QPushButton(self.splitter_10)
        self.resetDeckButton.setObjectName("resetDeckButton")
        self.tabWidget.addTab(self.viewTab, "")
        self.exportTab = QtWidgets.QWidget()
        self.exportTab.setObjectName("exportTab")
        self.groupBox_5 = QtWidgets.QGroupBox(self.exportTab)
        self.groupBox_5.setGeometry(QtCore.QRect(10, 20, 371, 371))
        self.groupBox_5.setObjectName("groupBox_5")
        self.ankiCardStyleBox = QtWidgets.QComboBox(self.groupBox_5)
        self.ankiCardStyleBox.setGeometry(QtCore.QRect(201, 40, 141, 25))
        self.ankiCardStyleBox.setObjectName("ankiCardStyleBox")
        self.ankiCardStyleBox.addItem("")
        self.ankiCardStyleBox.addItem("")
        self.label_3 = QtWidgets.QLabel(self.groupBox_5)
        self.label_3.setGeometry(QtCore.QRect(10, 40, 151, 19))
        self.label_3.setObjectName("label_3")
        self.searchForIpaCheck = QtWidgets.QCheckBox(self.groupBox_5)
        self.searchForIpaCheck.setGeometry(QtCore.QRect(10, 210, 251, 23))
        self.searchForIpaCheck.setChecked(True)
        self.searchForIpaCheck.setObjectName("searchForIpaCheck")
        self.openCsvAfterwardsCheck = QtWidgets.QCheckBox(self.groupBox_5)
        self.openCsvAfterwardsCheck.setGeometry(QtCore.QRect(10, 230, 251, 23))
        self.openCsvAfterwardsCheck.setObjectName("openCsvAfterwardsCheck")
        self.overwriteCsvCheck = QtWidgets.QCheckBox(self.groupBox_5)
        self.overwriteCsvCheck.setGeometry(QtCore.QRect(10, 250, 251, 23))
        self.overwriteCsvCheck.setObjectName("overwriteCsvCheck")
        self.copyImagesToAnkiCheck = QtWidgets.QCheckBox(self.groupBox_5)
        self.copyImagesToAnkiCheck.setGeometry(QtCore.QRect(10, 270, 361, 23))
        self.copyImagesToAnkiCheck.setChecked(True)
        self.copyImagesToAnkiCheck.setObjectName("copyImagesToAnkiCheck")
        self.cardStyleDescriptionTextEdit = QtWidgets.QTextEdit(self.groupBox_5)
        self.cardStyleDescriptionTextEdit.setGeometry(QtCore.QRect(10, 80, 331, 107))
        self.cardStyleDescriptionTextEdit.setReadOnly(True)
        self.cardStyleDescriptionTextEdit.setObjectName("cardStyleDescriptionTextEdit")
        self.splitter_11 = QtWidgets.QSplitter(self.groupBox_5)
        self.splitter_11.setGeometry(QtCore.QRect(10, 310, 331, 34))
        self.splitter_11.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_11.setObjectName("splitter_11")
        self.exportCsvButton = QtWidgets.QPushButton(self.splitter_11)
        self.exportCsvButton.setObjectName("exportCsvButton")
        self.importIntoAnkiButton = QtWidgets.QPushButton(self.splitter_11)
        self.importIntoAnkiButton.setObjectName("importIntoAnkiButton")
        self.label_5 = QtWidgets.QLabel(self.exportTab)
        self.label_5.setEnabled(False)
        self.label_5.setGeometry(QtCore.QRect(20, 400, 68, 19))
        self.label_5.setObjectName("label_5")
        self.exportProgressBar = QtWidgets.QProgressBar(self.exportTab)
        self.exportProgressBar.setEnabled(False)
        self.exportProgressBar.setGeometry(QtCore.QRect(20, 430, 331, 23))
        self.exportProgressBar.setProperty("value", 0)
        self.exportProgressBar.setTextVisible(False)
        self.exportProgressBar.setInvertedAppearance(False)
        self.exportProgressBar.setObjectName("exportProgressBar")
        self.logOutputTextEdit = QtWidgets.QTextEdit(self.exportTab)
        self.logOutputTextEdit.setGeometry(QtCore.QRect(20, 466, 331, 171))
        self.logOutputTextEdit.setReadOnly(True)
        self.logOutputTextEdit.setObjectName("logOutputTextEdit")
        self.tabWidget.addTab(self.exportTab, "")
        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        self.label_11.setGeometry(QtCore.QRect(20, 120, 211, 19))
        self.label_11.setObjectName("label_11")
        self.label_12 = QtWidgets.QLabel(self.centralwidget)
        self.label_12.setGeometry(QtCore.QRect(40, 30, 361, 51))
        font = QtGui.QFont()
        font.setFamily("Microsoft JhengHei UI")
        font.setPointSize(24)
        font.setBold(True)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.label_12.setFont(font)
        self.label_12.setAlignment(QtCore.Qt.AlignCenter)
        self.label_12.setObjectName("label_12")
        self.deckSelectBox = QtWidgets.QComboBox(self.centralwidget)
        self.deckSelectBox.setGeometry(QtCore.QRect(20, 155, 161, 24))
        self.deckSelectBox.setObjectName("deckSelectBox")
        self.deckSelectBox.addItem("")
        self.newDeckButton = QtWidgets.QPushButton(self.centralwidget)
        self.newDeckButton.setEnabled(True)
        self.stopRecorderButton.setEnabled(False)
        self.newDeckButton.setGeometry(QtCore.QRect(190, 150, 108, 34))
        self.newDeckButton.setObjectName("newDeckButton")
        self.selectDeckButton = QtWidgets.QPushButton(self.centralwidget)
        self.selectDeckButton.setGeometry(QtCore.QRect(300, 150, 108, 34))
        self.selectDeckButton.setObjectName("selectDeckButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionCopy = QtWidgets.QAction(MainWindow)
        self.actionCopy.setObjectName("actionCopy")
        self.actionPaste = QtWidgets.QAction(MainWindow)
        self.actionPaste.setObjectName("actionPaste")
        self.actionExport_Deck = QtWidgets.QAction(MainWindow)
        self.actionExport_Deck.setObjectName("actionExport_Deck")

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "LLN - Anki Exporter"))
        self.groupBox.setTitle(_translate("MainWindow", "Positioning"))
        self.label_19.setText(_translate("MainWindow", "Phrase start/end"))
        self.label_8.setText(_translate("MainWindow", "Cursor/AP positions"))
        self.label_16.setText(_translate("MainWindow", "Video start/end"))
        self.label_21.setText(_translate("MainWindow", "Subtitle start/end"))
        self.trySettingsButton.setText(_translate("MainWindow", "Load Profile"))
        self.calibrateButton.setText(_translate("MainWindow", "Calibrate"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Recording"))
        self.resolutionBox.setItemText(0, _translate("MainWindow", "1080"))
        self.resolutionBox.setItemText(1, _translate("MainWindow", "2160"))
        self.label_15.setText(_translate("MainWindow", "Resolution"))
        self.recordingModeBox.setItemText(0, _translate("MainWindow", "manual"))
        self.recordingModeBox.setItemText(1, _translate("MainWindow", "follow along"))
        self.recordingModeBox.setItemText(2, _translate("MainWindow", "fast forward"))
        self.label_17.setText(_translate("MainWindow", "Recording mode"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Deck "))
        self.label_10.setText(_translate("MainWindow", "Translation"))
        self.label_9.setText(_translate("MainWindow", "Original language"))
        self.applyDeckChangesButton.setText(_translate("MainWindow", "Apply"))
        self.label_18.setText(_translate("MainWindow", "Subtitle mode"))
        self.subtitleModeBox.setItemText(0, _translate("MainWindow", "use translation"))
        self.subtitleModeBox.setItemText(1, _translate("MainWindow", "ignore translation"))
        self.startRecorderButton.setText(_translate("MainWindow", "Start Recorder"))
        self.stopRecorderButton.setText(_translate("MainWindow", "Stop Recorder"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.recordTab), _translate("MainWindow", "Record"))
        self.label_7.setText(_translate("MainWindow", "Card # of "))
        self.groupBox_4.setTitle(_translate("MainWindow", "Settings"))
        self.showTranslationCheck.setText(_translate("MainWindow", "Show translation"))
        self.importantCardCheck.setText(_translate("MainWindow", "Mark current card as important"))
        self.label.setText(_translate("MainWindow", "Deck description"))
        self.previousImageButton.setText(_translate("MainWindow", "<"))
        self.nextImageButton.setText(_translate("MainWindow", ">"))
        self.deletePhraseButton.setText(_translate("MainWindow", "Delete Phrase"))
        self.resetDeckButton.setText(_translate("MainWindow", "Reset Deck"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.viewTab), _translate("MainWindow", "View"))
        self.groupBox_5.setTitle(_translate("MainWindow", "Settings"))
        self.ankiCardStyleBox.setItemText(0, _translate("MainWindow", "Standard"))
        self.ankiCardStyleBox.setItemText(1, _translate("MainWindow", "Monolingual"))
        self.label_3.setText(_translate("MainWindow", "Anki card style"))
        self.searchForIpaCheck.setText(_translate("MainWindow", "Find words in IPA dictionary"))
        self.openCsvAfterwardsCheck.setText(_translate("MainWindow", "Open csv file after completion"))
        self.overwriteCsvCheck.setText(_translate("MainWindow", "Overwrite existing csv"))
        self.copyImagesToAnkiCheck.setText(_translate("MainWindow", "Copy images directly to Anki directory"))
        self.cardStyleDescriptionTextEdit.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">The standard card style includes the image, phrase, translation, favorites and IPA transcription. Mongolingual doesn\'t filter out missing translations (like sounds or single subtitle).</span></p></body></html>"))
        self.exportCsvButton.setText(_translate("MainWindow", "Export to CSV"))
        self.importIntoAnkiButton.setText(_translate("MainWindow", "Import into Anki"))
        self.label_5.setText(_translate("MainWindow", "Progress"))
        self.logOutputTextEdit.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.exportTab), _translate("MainWindow", "Export"))
        self.label_11.setText(_translate("MainWindow", "Select or create a deck"))
        self.label_12.setText(_translate("MainWindow", "LLN Anki Exporter v0.1"))
        self.deckSelectBox.setItemText(0, _translate("MainWindow", "-"))
        self.newDeckButton.setText(_translate("MainWindow", "New Deck"))
        self.selectDeckButton.setText(_translate("MainWindow", "Select"))
        self.actionCopy.setText(_translate("MainWindow", "Copy"))
        self.actionPaste.setText(_translate("MainWindow", "Paste"))
        self.actionExport_Deck.setText(_translate("MainWindow", "Export .."))
        self.actionExport_Deck.setStatusTip(_translate("MainWindow", "Export current deck to csv."))
        self.actionExport_Deck.setShortcut(_translate("MainWindow", "Ctrl+E"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.init_events()
    ui.update_user_cfg()
    MainWindow.show()
    sys.exit(app.exec_())

