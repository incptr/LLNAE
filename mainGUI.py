# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'old.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QWidget,QPushButton,QLineEdit, QInputDialog, QApplication, QFormLayout
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from settings import WindowSettings,DeckSettings
from calibrate_screen import *
from LLNSaver import *
from state_machine import *
from deck_viewer import *
from deck_exporter import*
from subprocess import call as open_app
import breeze_resources

# to-do:
    # if no more cards in view tab -> change text to delete metadata:
    # delete all should be yes no again
    # delete deck doesnt get rid of all folders -> check for dead folders at startup
    # include option to ignore image  
    # append csv disabled for now
    # update .apk sentence card
    # dark mode https://stackoverflow.com/questions/48256772/dark-theme-for-qt-widgets
    # if new deck created and folder exist already -> fill in missing files
    # update deck count when choosing next card while recorder is running
    # linux port
    # block unblock calibrate/start recording vice versa
    # convert phrases and subtitle instantly with new thread
    # add light/dark mode to user settings
    # redesign positions etc
    # add looping thread that refreshes deck
    # disable elements when rec started
    # be able to edit subtitle/phrase
    
# class POINT(Structure):
#        _fields_ = [("x", c_long), ("y", c_long)] 


class CalibrationThread(QThread):
    
    cal_index = pyqtSignal(int)
    listener = []
    xy = [0,0]
    
    def __init__(self):
        super(CalibrationThread,self).__init__()


    def queryMousePosition(self):
        pt = POINT()
        windll.user32.GetCursorPos(byref(pt))
        return [pt.x,pt.y]

    def start_calibration(self):   
        
        def on_press(key):
            global xy
            if key == Key.ctrl_l:
                xy = queryMousePosition()
                # print(xy)
                return False     
        
            
        def on_release(key):
            if key == Key.esc:
                return False

        
        with open('user_settings.cfg') as f:
            cfg_lines = f.readlines()        
            
        for ind,val in enumerate(cfg_lines):
            # print('Please mark point #{}'.format(ind))
            
            with Listener(  
                           on_press=on_press,
                           on_release=on_release) as self.listener:
                       self.listener.join() 
            cfg_lines[ind] = '{} {}\n'.format(xy[0],xy[1])
            self.cal_index.emit(ind)
            if ind == 7:
                break    
        
        with open('user_settings.cfg','w') as f:
            f.writelines(cfg_lines)
        self.cal_index.emit(8)
    

    
    def run(self):
        self.start_calibration()
        
        
        

class RecordThread(QThread):
    
    change_value = pyqtSignal(int)
    output_log = pyqtSignal(str)
        
    def __init__(self,LLNSaver,mode):
        super(RecordThread,self).__init__()
        self.saver = LLNSaver
        self.mode = mode
        self.shutdown_req = False
        self.listener = []
        self.running_idx = 0
        
    def mode_loop(self):
        # manual mode
        
        # self.change_value.emit(1)
        # self.output_log.emit('test')
  
        if self.mode == 'manual':
            
            def on_release(key):
                if key == Key.esc:
                    # Stop listener
                    print('-- Shutting down. {} phrase(s) saved.'.format(self.saver.de.ri-self.saver.de.si))
                    return False
            
            def on_press(key):
                if self.shutdown_req:
                    return False
                
                
                if key == Key.ctrl_l:
                    self.saver.save_sentence(self.saver.de.testing,0.0)
                    self.running_idx = self.running_idx +1
                    self.change_value.emit(self.running_idx)
                    time.sleep(0.2)
                    # print("++ Phrase saved")                    
                    return         
            # while not self.shutdown_req:
  
            with Listener(  
                    on_press=on_press,
                    on_release=on_release) as self.listener:
                
                if self.shutdown_req == False:                        
                    self.listener.join()
                else:
                    return
                print('SM shutdown')
                return
                    

        # follow along
        elif self.mode == 'follow along':
            print('-- follow along started')
            while not self.shutdown_req:
                self.saver.check_if_phrase_started('NAP')
                # print("++ Phrase started.")
                self.saver.save_sentence(self.saver.de.testing,0.0)
                print("++ Phrase saved.")
                self.running_idx = self.running_idx +1
                self.change_value.emit(self.running_idx)
                
                time.sleep(0.1)
                self.saver.check_if_phrase_ended()
                time.sleep(0.1)
                # print("++ Phrase ended.")

                    
        # fast forward
        elif self.mode == 'fast forward':
            while not self.shutdown_req:
                im = pyautogui.screenshot()
                if self.saver.check_if_running(im):
                    self.saver.check_if_phrase_started()
                    self.saver.save_sentence(self.saver.de.testing,self.saver.wp.ff_delay)
                    print("++ Phrase saved.")
                    self.running_idx = self.running_idx +1
                    self.change_value.emit(self.running_idx)
                    pyautogui.press('right')
        

    
    def run(self):

        self.mode_loop()

    

class ExportThread(QThread):
    
    change_value = pyqtSignal(int)
    output_log = pyqtSignal(str)
    
    def __init__(self,DeckExporter):
        super(ExportThread,self).__init__()
        self.deck_exp = DeckExporter
        
    def export_loop(self):
        
        with open(self.deck_exp.deck_set.path + '{}.csv'.format(self.deck_exp.deck_set.deck), self.deck_exp.edit_mode, newline='',encoding='utf-8') as csvfile:
            
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            # spamwriter.writerow(['Front', 'Back'])
            # print('-- Starting csv writer.')
            
            if self.deck_exp.start_idx ==  self.deck_exp.running_idx:
                print('-- CSV was already created, save new phrases first.')
                return False
        
            prog_idx = 0
            for ind in range(self.deck_exp.start_idx,self.deck_exp.running_idx+1):

                if not os.path.isfile(self.deck_exp.deck_set.path + 'phrases/LLNp-{}-{}.png'.format(self.deck_exp.deck_set.deck,ind)):
                    continue
                [sentence,translation,ipa,empty,favorite] = self.deck_exp.get_export_values(ind)
                if not empty:
                    line_1 = '<img src="LLNi-{}-{}.png">'.format(self.deck_exp.deck_set.deck,ind)
                    line_2 = sentence
                    line_3 = translation
                    line_4 = ipa
                    line_5 = favorite
                    spamwriter.writerow([line_1, line_2, line_3,line_4,line_5]) 
                    
                prog_idx = prog_idx +1
                self.change_value.emit(int(prog_idx*100/self.deck_exp.exp_length))
                self.output_log.emit('-- exporting card #{} of {}\n'.format(prog_idx,self.deck_exp.exp_length))
    
    def run(self):
        
        self.deck_exp.initialize_export()
        self.export_loop()

        

            
            
            
class NewDeckPopup(QWidget):
    def __init__(self):
        super().__init__()
        

    def pop(self,text,title='New deck'):
        [txt,ok] = QInputDialog.getText(self, title,text)
        if txt == '':
            txt = ' '
        return [txt,ok]


class Ui_MainWindow(object):
    
    # ---------------- HELPER METHODS ------------------    
    def create_deck_files(self,deck_name,og_lang,trans_lang,description):
        
        def check_directory(path,hidden = False):   
            if not os.path.isdir(path):
                os.mkdir(path)
                if hidden:
                    FILE_ATTRIBUTE_HIDDEN = 0x02
                    ret = ctypes.windll.kernel32.SetFileAttributesW(path, FILE_ATTRIBUTE_HIDDEN)
                return False
            else:
                return True       
            
        def create_config():
            with open(base_path+'params.cfg', 'w') as f:
              f.write('%d \n' % 0)
              # original language
              f.write(og_lang +'\n')
              # original language
              f.write(trans_lang +'\n')
              # savepoint csv
              f.write('0\n')
              f.write(description)
              
            with open(base_path+'favorites.cfg', 'w') as f:
                f.write('')
         
        base_path = 'data/{}/'.format(deck_name)  
        
        if os.path.isdir(base_path):
            return False
        
        if not (check_directory(base_path) or \
                check_directory(base_path+'/images') or \
                check_directory(base_path+'/phrases',True) or \
                check_directory(base_path+'/trans',True)):
            # print('folders created')
            pass
        
        if os.path.isfile(base_path+'params.cfg'):
            if not os.stat(base_path+'params.cfg').st_size:
                create_config()
        else:
            create_config()
            
        if os.path.isfile(base_path+'favorites.cfg'):
            if not os.stat(base_path+'favorites.cfg').st_size:
                with open(base_path+'favorites.cfg', 'w') as f:
                    f.write('')
        else:
           with open(base_path+'favorites.cfg', 'w') as f:
               f.write('')
        return True
    #------------------- EXPORTER-----------------------
    
    def calibrate_progress(self,val):
        
        self.statusbar.showMessage('Calibrating point #{}.'.format(val))
        
        if val == 8:
            # print('updating user cfg')
            self.tabWidget.setEnabled(True)
            self.sm.saver.wp.load_config()
            self.update_user_cfg(True) 
            self.statusbar.showMessage('')
            

    
    def calibrate_clicked(self):
        
        self.statusbar.showMessage('Calibrating point #{}.'.format(1))
        
        self.cal_thread = CalibrationThread()
        self.cal_thread.cal_index.connect(self.calibrate_progress)
        self.cal_thread.start()
        
        self.msg = QMessageBox()
        self.msg.setWindowTitle("Calibration")
        self.msg.setText("Hover over the eight points to calibrate. Press left control to confirm a point.")
        x = self.msg.exec_()
        
        self.tabWidget.setEnabled(False)

        
        
    
    def import_clicked(self):
        if(os.path.isfile(self.deck_exp.deck_set.path+'/{}.csv'.format(self.deck_exp.deck_set.deck))): 
            open_app(['C:\\Program Files\\Anki\\anki.exe', self.deck_set.path + '{}.csv'.format(self.deck_set.deck)])
    
    def append_output_log(self,text):
        self.logOutputTextEdit.insertPlainText(text)
    
    
    def setProgressVal(self, val):
        # print('{} received'.format(val))
        
        old = self.exportProgressBar.value()
        new = val
        self.exportProgressBar.setValue(new)
        
        if val == 100:        
            self.importIntoAnkiButton.setEnabled(True)
            self.deck_exp.finish_export()
            self.logOutputTextEdit.insertPlainText('-- saved file to ./data/{}/{}.csv'.format(self.deck_exp.deck_set.deck,self.deck_exp.deck_set.deck))
        else:
            self.importIntoAnkiButton.setEnabled(False)
            
    
    def export_clicked(self):
        self.exp_thread = ExportThread(self.deck_exp)
        self.exportProgressBar.setEnabled(True)
        self.label_5.setEnabled(True)
        self.logOutputTextEdit.setEnabled(True)
        self.exp_thread.change_value.connect(self.setProgressVal)
        self.exp_thread.output_log.connect(self.append_output_log)
        self.exp_thread.start()

        
        
        return
        
        # if self.deck_exp.export():
        #     self.importIntoAnkiButton.setEnabled(True)
        # else:
        #     self.importIntoAnkiButton.setEnabled(False)
    
    def update_exp_mode(self):
        self.deck_exp.exp_mode = self.ankiCardStyleBox.currentText()
        self.deck_exp.save_config() 
        
    def update_use_ipa(self):
        if self.searchForIpaCheck.isChecked():
            self.deck_exp.search_ipa  = 1
        else:                
            self.deck_exp.search_ipa  = 0
        self.deck_exp.save_config()
        
    def update_open_csv(self):
        if self.openCsvAfterwardsCheck.isChecked():
            self.deck_exp.open_csv  = 1
        else:                
            self.deck_exp.open_csv  = 0
        self.deck_exp.save_config()
        
    def update_overwrite_csv(self):
        if self.overwriteCsvCheck.isChecked():
            self.deck_exp.overwrite  = 1
        else:                
            self.deck_exp.overwrite  = 0
        self.deck_exp.save_config()
        
    def update_copy_images(self):
        if self.copyImagesToAnkiCheck.isChecked():
            self.deck_exp.copy_img  = 1
        else:                
            self.deck_exp.copy_img  = 0
        self.deck_exp.save_config()
        

    
    #----------------- VIEWER --------------------------
        
    def reset_deck_clicked(self):
        
        qm = QMessageBox()
        qm.setWindowTitle('Warning')
        qm.setText('Do you want to delete all metadata as well?'.format(self.deck_viewer.n_cards))
        qm.setIcon(QMessageBox.Question)
        qm.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
        qm.buttonClicked.connect(self.reset_msg_clicked)
        x = qm.exec_()
        
    def reinitialize_deck_fields(self):
        self.en_or_disable_viewer(False)
        
        index = self.deckSelectBox.findText(self.deck_viewer.deck_set.deck, QtCore.Qt.MatchFixedString)
        self.deckSelectBox.removeItem(index)
        
        index = max(0,index-1)
        index = min(index,self.deckSelectBox.count())            
        self.deckSelectBox.setCurrentIndex(index) 
        if self.deckSelectBox.count() > 0:
            self.update_deck_load()
        self.deckDescriptionTextEdit.setPlainText('')
        self.originalLanguageLineEdit.setText('')
        self.translationLineEdit.setText('')
    
    def reset_msg_clicked(self,choice):    


        # reload values in statemachine and deckviewer
        if choice.text() == 'No':                
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
            # print('++ Index reset to 0. All images deleted')
            
            self.deckPhoto.setPixmap(QtGui.QPixmap('app_data/images/blank.png'))
            self.deckPhraseLabel.setPixmap(QtGui.QPixmap('app_data/images/dark.png'))
            self.deckSubLabel.setPixmap(QtGui.QPixmap('app_data/images/dark.png'))
            self.label_7.setText('Card #{} of {}'.format(0,0))

            self.en_or_disable_viewer(False)
            self.resetDeckButton.setEnabled(True)
            
        else:
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
                
            dir = self.deck_viewer.deck_set.path
            os.remove(dir + 'params.cfg')
            os.remove(dir + 'favorites.cfg')

            # print('++ Index reset to 0. All images deleted')
            
            self.deckPhoto.setPixmap(QtGui.QPixmap('app_data/images/blank.png'))
            self.deckPhraseLabel.setText('')
            self.deckSubLabel.setText('')
            self.label_7.setText('Card #{} of {}'.format(0,0))

            self.reinitialize_deck_fields()
            
          
    def delete_phrase_clicked(self):  
      
        if self.tabWidget.currentIndex() == 1:
            self.deck_viewer.save_favorite(False)
            os.remove(self.deck_viewer.im_path)
            os.remove(self.deck_viewer.ph_path)
            os.remove(self.deck_viewer.sub_path)
            self.deck_viewer.n_cards = self.deck_viewer.n_cards -1
            [im_path,ph_path,sub_path,idx] = self.deck_viewer.get_next_picture(direction=1,deletion = 1)  
            
            if not im_path == '':
                
                phrase,trans = get_phrase_and_trans(self)
                
                self.deckPhoto.setPixmap(QtGui.QPixmap(im_path))
                self.deckPhraseLabel.setText(phrase)
                self.deckSubLabel.setText(trans)
                
                fav_val = self.deck_viewer.check_favorite()
                if fav_val:
                        self.label_2.resize(25,25)
                        self.importantCardCheck.setChecked(True)                 
                else:                
                        self.label_2.resize(25,0)
                        self.importantCardCheck.setChecked(False)
                        
            self.label_7.setText('Card #{} of {}'.format(self.deck_viewer.card_number,self.deck_viewer.n_cards))
            

                    
            if self.deck_viewer.n_cards > 0:
                self.en_or_disable_viewer(True)
                
            else:
                self.deckPhoto.setPixmap(QtGui.QPixmap('app_data/images/blank.png'))
                self.deckPhraseLabel.setText('')
                self.deckSubLabel.setText('')
                self.label_7.setText('Card #{} of {}'.format(0,0))
                self.en_or_disable_viewer(False)
                self.resetDeckButton.setEnabled(True)
    

        
        
    
    def next_image_clicked(self):
        
        if self.tabWidget.currentIndex() == 1:
            [im_path,ph_path,sub_path,idx] = self.deck_viewer.get_next_picture(direction=1)
            
            if not im_path == '':
                
                phrase,trans = self.get_phrase_and_trans()
                
                self.deckPhoto.setPixmap(QtGui.QPixmap(im_path))
                self.deckPhraseLabel.setText(phrase)
                self.deckSubLabel.setText(trans)
                
                self.label_7.setText('Card #{} of {}'.format(self.deck_viewer.card_number,self.deck_viewer.n_cards))
                
                fav_val = self.deck_viewer.check_favorite()
                if fav_val:
                        self.label_2.resize(25,25)
                        self.importantCardCheck.setChecked(True)                 
                else:                
                        self.label_2.resize(25,0)
                        self.importantCardCheck.setChecked(False)
            
    
    def prev_image_clicked(self):
        
        if self.tabWidget.currentIndex() == 1:
            [im_path,ph_path,sub_path,idx] = self.deck_viewer.get_next_picture(direction=-1)
            
            if not im_path == '':
                
                phrase,trans = self.get_phrase_and_trans()

                self.deckPhoto.setPixmap(QtGui.QPixmap(im_path))
                self.deckPhraseLabel.setText(phrase)
                self.deckSubLabel.setText(trans)                
                
                if self.showTranslationCheck.isChecked(): self.deckSubLabel.setText(trans) 
                
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
        if self.deck_viewer.n_cards > 0 and self.tabWidget.currentIndex() == 1:
        
            if self.importantCardCheck.isChecked():
                self.label_2.resize(25,25)
                    
            else:                
                self.label_2.resize(25,0)
                
                    
            self.deck_viewer.save_favorite(self.importantCardCheck.isChecked())
            
    def update_description(self):
        if self.deckSelectBox.count() > 0:
            if self.deckDescriptionTextEdit.toPlainText() == '':
                return
            else:
                self.sm.saver.de.description = self.deckDescriptionTextEdit.toPlainText()
                self.sm.saver.de.save_params()
            
    def en_or_disable_viewer(self,val):
        
        self.importantCardCheck.setEnabled(val)
        self.previousImageButton.setEnabled(val)
        self.deletePhraseButton.setEnabled(val)
        self.resetDeckButton.setEnabled(val)
        self.nextImageButton.setEnabled(val)
        
            
    #----------------- RECORDER --------------------------    
    
    def minimal_mode_init(self):
        
        if not self.minimal_init:
            
            _translate = QtCore.QCoreApplication.translate
            
            self.mStartRecButton =QtWidgets.QPushButton(self.centralwidget)            
            self.mStartRecButton.setText(_translate("MainWindow", "Start Recorder"))
            self.mStartRecButton.move(10,5)            
            self.mStartRecButton.resize(110,34)
            
            self.mStopRecButton = QtWidgets.QPushButton(self.centralwidget)
            self.mStopRecButton.setText(_translate("MainWindow", "Stop Recorder"))
            self.mStopRecButton.move(120,5)
            self.mStopRecButton.resize(110,34)
            
            self.mCalibrateButton = QtWidgets.QPushButton(self.centralwidget)
            self.mCalibrateButton.setText(_translate("MainWindow", "Calibrate"))
            self.mCalibrateButton.move(10,39)
            self.mCalibrateButton.resize(110,34)
            
            self.mModeButton = QtWidgets.QPushButton(self.centralwidget)
            self.mModeButton.setText(_translate("MainWindow", "Expand"))
            self.mModeButton.move(120,39)
            self.mModeButton.resize(110,34)
            
            self.mCalibrateButton.clicked.connect(self.calibrate_clicked)
            self.mStartRecButton.clicked.connect(self.start_recording_clicked)
            self.mStopRecButton.clicked.connect(self.stop_recording_clicked)
            self.mModeButton.clicked.connect(self.minimal_mode_clicked) 
            
    def minimal_mode_clicked(self):
        
        if self.window_mode == 'full':
            
            self.window_mode = 'minimal'
            self.minimal_mode_init()
            
            self.mStartRecButton.setVisible(True)
            self.mStopRecButton.setVisible(True)
            self.mCalibrateButton.setVisible(True)
            self.mModeButton.setVisible(True)
            
            self.label_12.setText('')   
            self.mw.resize(240,93)
            
        else:
            
            self.mStartRecButton.setVisible(False)
            self.mStopRecButton.setVisible(False)
            self.mCalibrateButton.setVisible(False)
            self.mModeButton.setVisible(False)
            
            self.label_12.setText('LLN Anki Exporter v0.1') 
            
            self.mw.resize(430,923)
            self.window_mode = 'full'
                           
    
    def update_tabs(self):
        self.statusbar.showMessage('')
        tab = self.tabWidget.currentIndex()
        if tab == 0:
            self.update_deck_load()
        if tab == 1:
            self.update_deck_load()
        if tab == 2:
            if(os.path.isfile(self.deck_exp.deck_set.path+'/{}.csv'.format(self.deck_exp.deck_set.deck))):            
                self.importIntoAnkiButton.setEnabled(True)
            else:
                self.importIntoAnkiButton.setEnabled(False)
        
        
    def en_or_disable_recorder(self,val):
        self.deckDescriptionTextEdit.setEnabled(val)
        self.originalLanguageLineEdit.setEnabled(val)
        self.translationLineEdit.setEnabled(val)
        self.applyDeckChangesButton.setEnabled(val)
        self.startRecorderButton.setEnabled(val)
    
    def load_decks(self,MainWindow):
        
        _translate = QtCore.QCoreApplication.translate
        if not os.path.exists('data'):
            os.mkdir('data')
            return
        deck_list = next(os.walk('data/'))[1]
        # print(deck_list)

        for idx,deck in enumerate(deck_list):
            
            if(os.path.isfile('data/{}/params.cfg'.format(deck))):           
                self.deckSelectBox.addItem(deck)
                self.deckSelectBox.setItemText(idx+1, _translate("MainWindow", str(deck)))
            
        if self.deckSelectBox.count() > 0:
            self.update_deck_load()
            self.deckDescriptionTextEdit.setEnabled(True)
    
    
    def update_deck_load(self):
        
        if self.deckSelectBox.count() > 0:
            
            selected_deck =  self.deckSelectBox.currentText()
            if not selected_deck == '-':
                self.sm.saver.de.load_params(selected_deck)
                self.selected_deck = selected_deck
                self.valid_deck = True
                # print(self.sm.saver.de.og_lang)
                self.originalLanguageLineEdit.setText(self.sm.saver.de.og_lang)
                self.translationLineEdit.setText(self.sm.saver.de.trans_lang)
                # print('Valid deck selected')
                self.deck_select_clicked()
            else:
                self.valid_deck = False
                # print('Invalid deck selected')
                
            if self.valid_deck:
                self.originalLanguageLineEdit.setEnabled(True)
                self.translationLineEdit.setEnabled(True)
                self.applyDeckChangesButton.setEnabled(True)
                self.startRecorderButton.setEnabled(True)
                self.deckDescriptionTextEdit.setEnabled(True)
                
                if self.deck_viewer.n_cards > 0:
                    self.en_or_disable_viewer(True)
                    self.exportCsvButton.setEnabled(True)
                else:
                    self.en_or_disable_viewer(False)
                    self.exportCsvButton.setEnabled(False)
                
                


            
            
    def update_recording_mode(self):
        self.sm.mode = self.recordingModeBox.currentText()
        self.sm.saver.wp.mode = self.recordingModeBox.currentText()
        self.sm.saver.wp.save_config()
        # print(self.sm.mode)
              
    def update_resolution(self):
        self.sm.saver.wp.res = int(self.resolutionBox.currentText())/2160
        self.sm.saver.wp.save_config()
        # print('New res: {}'.format(self.sm.saver.wp.res))
        
    def update_subtitle_mode(self):
        self.sm.saver.wp.use_trans = self.subtitleModeBox.currentText()
        self.sm.saver.wp.save_config()
        # print('New res: {}'.format(self.sm.saver.wp.res))
    

        
    
    # widget triggers
    def reportProgress(self, n):
        self.stepLabel.setText(f"Long-Running Step: {n}")
    
    def runLongTask(self):
        """Long-running task in 5 steps."""
        for i in range(5):
            sleep(1)
            self.reportProgress(i + 1)
            
    def apply_deck_clicked(self):
        self.sm.saver.de.og_lang = self.originalLanguageLineEdit.text()
        self.sm.saver.de.trans_lang = self.translationLineEdit.text()
        print(self.sm.saver.de.og_lang )
        print(self.sm.saver.de.trans_lang)
        self.sm.saver.de.save_params()


    def get_phrase_and_trans(self):
        with open(self.deck_set.path+'phrases.txt') as f:
            lines = f.readlines()
            
        for line in lines:            
            vals = line.split(' ')
            indx = int(vals[0])
            if indx == self.deck_viewer.idx:                
                phrase = ' '.join(vals[1:])
                
        with open(self.deck_set.path+'trans.txt') as f:
            lines = f.readlines()
            
        for line in lines:            
            vals = line.split(' ')
            indx = int(vals[0])
            if indx == self.deck_viewer.idx:                
                trans = ' '.join(vals[1:])
                
        return phrase,trans
        
    def deck_select_clicked(self):
        # create DeckViewer instance
        self.deck_viewer = DeckViewer(self.sm.saver.de)
        # create DeckExporter instance
        self.deck_exp = DeckExporter(self.sm.saver.de)
        
        [im_path,ph_path,sub_path,idx] = self.deck_viewer.load_picture(mode='init')
        
        if not im_path == '':
            
            phrase,trans = self.get_phrase_and_trans()

            self.deckPhoto.setPixmap(QtGui.QPixmap(im_path))
            self.deckPhraseLabel.setText(phrase)
            self.deckSubLabel.setText(trans)    
            
            
            
            
        list_of_files = filter( os.path.isfile,
                      glob.glob(self.deck_viewer.deck_set.path + 'images/' + '*') )
        list_of_files = sorted( list_of_files,
                              key = os.path.getmtime)
        self.deck_viewer.n_cards = len(list_of_files)
        
        if self.deck_viewer.n_cards == 0:
            self.deckPhoto.setPixmap(QtGui.QPixmap('app_data/images/blank.png'))
            self.deckPhraseLabel.setText('')
            self.deckSubLabel.setText('')
            self.label_7.setText('Card #{} of {}'.format(0,0))
            self.en_or_disable_viewer(False)
        else:
            self.en_or_disable_viewer(True)
            fav_val = self.deck_viewer.check_favorite()
            if fav_val:
                    self.label_2.resize(25,25)
                    self.importantCardCheck.setChecked(True)                 
            else:                
                    self.label_2.resize(25,0)
                    self.importantCardCheck.setChecked(False)
            
        
        self.label_7.setText('Card #1 of {}'.format(self.deck_viewer.n_cards))
        self.deckDescriptionTextEdit.setPlainText(self.sm.saver.de.description)           
        return
    
    def new_deck_clicked(self):
        _translate = QtCore.QCoreApplication.translate
        self.new_deck_pop = NewDeckPopup()
        [deck_name,ok] = self.new_deck_pop.pop('Enter a deck name.')
        
        if ok:
            [og_lang,ok] = self.new_deck_pop.pop('Enter the original language.')
            if ok:
                [trans_lang,ok] = self.new_deck_pop.pop('Enter the translated language.')
                if ok:
                    [description,ok] = self.new_deck_pop.pop('Enter a description for the deck.')
                    
            if self.create_deck_files(deck_name,og_lang,trans_lang,description):
                self.deckSelectBox.addItem(deck_name)
                index = self.deckSelectBox.findText(deck_name, QtCore.Qt.MatchFixedString)
                self.deckSelectBox.setItemText(index, _translate("MainWindow", str(deck_name)))
                self.deckSelectBox.setCurrentIndex(index)
                self.update_deck_load()
            
        else:
            return


    def stop_recording_clicked(self):
        
        self.rec_thread.shutdown_req = True      
        
        self.startRecorderButton.setEnabled(True)
        self.stopRecorderButton.setEnabled(False)
        self.statusbar.showMessage('Recorder stopped.')
        
    def return_record_progress(self,indx):
        
        self.statusbar.showMessage('Recorder running in {} mode. {} phrase(s) saved since launch'.format(self.sm.mode,indx))
        # print()

        
    def start_recording_clicked(self):
        if self.valid_deck:
            
            self.rec_thread = RecordThread(self.sm.saver,self.sm.mode)
            self.rec_thread.change_value.connect(self.return_record_progress)
            # self.rec_thread.output_log.connect(self.append_output_log)
            self.rec_thread.start()            
            
            self.statusbar.showMessage('Recorder running in {} mode.'.format(self.sm.mode))
            
            self.startRecorderButton.setEnabled(False)
            self.stopRecorderButton.setEnabled(True)
            
        else:
            print('Select a valid deck first.')
            

            
    def load_user_settings(self):       
        
        idx = self.resolutionBox.findText(str(int(self.sm.saver.wp.res*2160)), QtCore.Qt.MatchFixedString)
        self.resolutionBox.setCurrentIndex(idx)
        idx = self.recordingModeBox.findText(self.sm.saver.wp.mode, QtCore.Qt.MatchFixedString)
        self.recordingModeBox.setCurrentIndex(idx)
        idx = self.subtitleModeBox.findText(self.sm.saver.wp.use_trans, QtCore.Qt.MatchFixedString)
        self.subtitleModeBox.setCurrentIndex(idx)
        idx = self.ankiCardStyleBox.findText(self.deck_exp.exp_mode, QtCore.Qt.MatchFixedString)
        self.ankiCardStyleBox.setCurrentIndex(idx)
        
        self.searchForIpaCheck.setChecked(self.deck_exp.use_ipa) 
        self.openCsvAfterwardsCheck.setChecked(self.deck_exp.open_csv) 
        self.overwriteCsvCheck.setChecked(self.deck_exp.overwrite) 
        self.copyImagesToAnkiCheck.setChecked(self.deck_exp.copy_img) 
        
    
    def update_user_cfg(self,profile=0):
        
        def create_cfg_str(val1,val2=['','']):
            x0 = val1[0]
            y0 = val1[1]
            x1 = val2[0]
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
        self.en_or_disable_viewer(False)
        self.en_or_disable_recorder(False)

        self.minimal_init = False
        self.window_mode = 'full'
        self.valid_deck = False
        self.selected_deck = '-'
        self.load_decks(self)
        self.qthread = QThread()
        self.exp_thread_started = False
        self.load_user_settings()    
        
        return
    
    def init_events(self):
        
        # create instances
        self.win_set = WindowSettings('full','1080',0)
        self.deck_set = DeckSettings('', '', '',False)        
        self.saver = LLNSaver(self.deck_set,self.win_set)
        self.sm = StateMachine(self.saver,self.win_set.mode)  
        self.deck_exp = DeckExporter(self.sm.saver.de)        
        
        self.initialize_settings()
        
        # shortcuts
        self.deletePhraseButton.setShortcut("d")
        self.importantCardCheck.setShortcut("f")
        self.previousImageButton.setShortcut("left")
        self.nextImageButton.setShortcut("right")
        
        # buttons
        self.calibrateButton.clicked.connect(self.calibrate_clicked)
        self.startRecorderButton.clicked.connect(self.start_recording_clicked)
        self.stopRecorderButton.clicked.connect(self.stop_recording_clicked)
        self.selectDeckButton.clicked.connect(self.deck_select_clicked)
        self.nextImageButton.clicked.connect(self.next_image_clicked)       
        self.previousImageButton.clicked.connect(self.prev_image_clicked)   
        self.resetDeckButton.clicked.connect(self.reset_deck_clicked)
        self.deletePhraseButton.clicked.connect(self.delete_phrase_clicked)
        self.applyDeckChangesButton.clicked.connect(self.apply_deck_clicked)
        self.newDeckButton.clicked.connect(self.new_deck_clicked)
        self.exportCsvButton.clicked.connect(self.export_clicked)  
        self.importIntoAnkiButton.clicked.connect(self.import_clicked) 
        self.minimalModeButton.clicked.connect(self.minimal_mode_clicked) 
        
        # boxes
        self.resolutionBox.currentIndexChanged.connect(self.update_resolution)
        self.recordingModeBox.currentIndexChanged.connect(self.update_recording_mode)
        self.deckSelectBox.currentIndexChanged.connect(self.update_deck_load)
        self.subtitleModeBox.currentIndexChanged.connect(self.update_subtitle_mode)
        self.ankiCardStyleBox.currentIndexChanged.connect(self.update_exp_mode)
        
        # checks
        self.showTranslationCheck.stateChanged.connect(self.update_show_translation)
        self.importantCardCheck.stateChanged.connect(self.update_favorite)        
        self.searchForIpaCheck.stateChanged.connect(self.update_use_ipa)
        self.openCsvAfterwardsCheck.stateChanged.connect(self.update_open_csv)
        self.overwriteCsvCheck.stateChanged.connect(self.update_overwrite_csv)
        self.copyImagesToAnkiCheck.stateChanged.connect(self.update_copy_images)
        
        # line edit
        self.deckDescriptionTextEdit.textChanged.connect(self.update_description)
        
        # tab
        self.tabWidget.currentChanged.connect(self.update_tabs)
        
        
    
    def setupUi(self, MainWindow):
        
        self.mw =  MainWindow
        
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
        self.minimalModeButton = QtWidgets.QPushButton(self.splitter)
        self.minimalModeButton.setObjectName("minimalModeButton")
        self.calibrateButton = QtWidgets.QPushButton(self.splitter)
        self.calibrateButton.setObjectName("calibrateButton")
        self.groupBox_2 = QtWidgets.QGroupBox(self.frame)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 420, 371, 141))
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
        # self.deckSubLabel.setPixmap(QtGui.QPixmap("data/c.png"))
        # self.deckSubLabel.setScaledContents(True)
        
        self.deckPhoto = QtWidgets.QLabel(self.viewTab)
        self.deckPhoto.setGeometry(QtCore.QRect(20, 25, 341, 171))
        self.deckPhoto.setText("")
        self.deckPhoto.setPixmap(QtGui.QPixmap("data/a.png"))
        self.deckPhoto.setScaledContents(True)
        self.deckPhoto.setObjectName("deckPhoto")
        
        self.deckPhraseLabel = QtWidgets.QLabel(self.viewTab)
        self.deckPhraseLabel.setGeometry(QtCore.QRect(40, 210, 301, 55))
        self.deckPhraseLabel.setText("")
        self.deckPhraseLabel.setFont(QFont('Roboto', 13))
        self.deckPhraseLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.deckPhraseLabel.setWordWrap(True)
        
        self.deckSubLabel = QtWidgets.QLabel(self.viewTab)
        self.deckSubLabel.setGeometry(QtCore.QRect(40, 265, 301, 50))
        self.deckSubLabel.setText("")
        self.deckSubLabel.setFont(QFont('Roboto', 10))
        self.deckSubLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.deckSubLabel.setWordWrap(True);
        self.deckSubLabel.setObjectName("deckSubLabel")
        # self.deckPhraseLabel.setPixmap(QtGui.QPixmap("data/b.png"))
        # self.deckPhraseLabel.setScaledContents(True)
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
        self.logOutputTextEdit.setEnabled(False)
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
        self.minimalModeButton.setText(_translate("MainWindow", "Minimal mode"))
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
        self.ankiCardStyleBox.setItemText(0, _translate("MainWindow", "standard"))
        self.ankiCardStyleBox.setItemText(1, _translate("MainWindow", "monolingual"))
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
        self.newDeckButton.setText(_translate("MainWindow", "New Deck"))
        self.selectDeckButton.setText(_translate("MainWindow", "Load"))
        self.actionCopy.setText(_translate("MainWindow", "Copy"))
        self.actionPaste.setText(_translate("MainWindow", "Paste"))
        self.actionExport_Deck.setText(_translate("MainWindow", "Export .."))
        self.actionExport_Deck.setStatusTip(_translate("MainWindow", "Export current deck to csv."))
        self.actionExport_Deck.setShortcut(_translate("MainWindow", "Ctrl+E"))


if __name__ == "__main__":
    import sys
    
    style = """
        QWidget{
              background: #262D37}
    
    
    """
    from PyQt5.QtCore import QFile, QTextStream
    
    app = QtWidgets.QApplication(sys.argv)
    
    file = QFile(":/dark/stylesheet.qss")
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())
    
    # app.setStyleSheet(style)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.init_events()
    ui.update_user_cfg()
    MainWindow.show()
    sys.exit(app.exec_())

