# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 23:27:24 2021

@author: domen
"""

from PyQt5.QtCore import QObject, QThread, pyqtSignal
import time, pyaudio, wave, pytesseract, csv
from ctypes import windll, Structure, c_long, byref
from pynput.keyboard import Key, Listener
         
class SaveAudioThread(QThread):
    
    def __init__(self,length,index,deck):
        super(SaveAudioThread,self).__init__()
        
        # print('Attempting rec')
        self.ri=index
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 2
        self.RATE = 48000
        self.RECORD_SECONDS = length
        self.WAVE_OUTPUT_FILENAME = "data/{}/audio/LLNa-{}-{}.wav".format(deck,deck,index+1)   
        self.last_word = ''
    
    def record_clip(self):
            
        p = pyaudio.PyAudio()
            # pick rec length based on #letters
        # print(self.WAVE_OUTPUT_FILENAME)
        stream = p.open(format=self.FORMAT,channels=self.CHANNELS,rate=self.RATE,input=True,frames_per_buffer=self.CHUNK)
        
        # print("* recording")        
        frames = []
        
        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            data = stream.read(self.CHUNK)
            frames.append(data)
        
        # print("* {} done recording".format(self.ri))        
        stream.stop_stream()
        stream.close()
        p.terminate()        
        wf = wave.open(self.WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
    def run(self):
        print('Saving audio {}'.format(self.ri))
        self.record_clip()
        
        
        
class SaveImageThread(QThread):
    
    def __init__(self,saver,delay):
        super(SaveImageThread,self).__init__()
        self.saver = saver
        self.delay = delay
    def run(self):
        print('Saving phrase {}'.format(self.saver.de.ri))
        self.saver.save_sentence(self.saver.de.testing,self.delay)
            
            
        

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
        self.audio_threads = []
        self.image_threads = []
        self.audio_id = 0
        self.image_id = 0
        
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
                
                clip_length = self.saver.anticipate_audio()
                
                if clip_length:
                # start audio thread
                    print('-- Detected phrase {}'.format(self.saver.de.ri))
                    
                    if self.saver.wp.use_audio == 'record if possible':                    
                        self.audio_threads.append(SaveAudioThread(clip_length+0.6,self.saver.de.ri,self.saver.de.deck))
                        self.audio_threads[self.audio_id].start() 
                        # print('thread {} launched'.format(self.audio_id))
                        self.audio_id = self.audio_id+1
                    time.sleep(0.2)
                    self.image_threads.append(SaveImageThread(self.saver,1.0))
                    self.image_threads[self.image_id].start()
                    self.image_id = self.image_id+1
                    
                    # self.saver.save_sentence(self.saver.de.testing,1.2)
                    # print("++ Phrase saved.")
                    time.sleep(0.2)
                    self.running_idx = self.running_idx +1
                    self.change_value.emit(self.running_idx)
                
                # self.saver.check_if_phrase_ended()
                # time.sleep(0.1)
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
        

class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]


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
                xy = self.queryMousePosition()
                # print(xy)
                return False     
        
            
        def on_release(key):
            if key == Key.esc:
                return False

        
        with open('app_data/cfg/user_settings.cfg') as f:
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
        
        with open('app_data/cfg/user_settings.cfg','w') as f:
            f.writelines(cfg_lines)
        self.cal_index.emit(8)
    

    
    def run(self):
        self.start_calibration()
        

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

                # if not os.path.isfile(self.deck_exp.deck_set.path + 'phrases/LLNp-{}-{}.png'.format(self.deck_exp.deck_set.deck,ind)):
                #     continue
                [sentence,translation,ipa,empty,favorite,audio] = self.deck_exp.get_export_values(ind)
                
                if not empty:
                    line_1 = '<img src="LLNi-{}-{}.png">'.format(self.deck_exp.deck_set.deck,ind)
                    line_2 = sentence
                    line_3 = translation
                    line_4 = ipa
                    line_5 = favorite
                    line_6 = audio
                        
                    spamwriter.writerow([line_1, line_2, line_3,line_4,line_5,line_6]) 
                else:
                    continue
                    
                prog_idx = prog_idx +1
                self.change_value.emit(int(prog_idx*100/self.deck_exp.exp_length))
                self.output_log.emit('-- exporting card #{} of {}\n'.format(prog_idx,self.deck_exp.exp_length))
    
    def run(self):
        
        self.deck_exp.initialize_export()
        self.export_loop()

        

            