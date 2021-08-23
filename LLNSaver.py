# -*- coding: utf-8 -*-
"""
Created on Fri Aug 20 12:39:08 2021

@author: domen
"""
import pyautogui
from PIL import Image
import PIL.ImageOps
from pynput.keyboard import Key, Listener
import numpy as np
import time,shutil, pytesseract
from PyQt5.QtCore import QThread

class OCRThread(QThread):
    
    # cal_index = pyqtSignal(int)
 
     def __init__(self,img,lang,path,idx,folder):
         super(OCRThread,self).__init__()
         self.type = folder
         self.img = img
         self.lang = lang
         self.path = path
         self.idx = idx
         
         pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe' 
         
     def convert_to_text(self): 
         # print('convert_to_text')
         print(self.lang)
         # self.img.show()
         
         input_string = pytesseract.image_to_string(self.img,lang=self.lang)         
         words = input_string.split()   
         self.text = ' '.join(words)         
         self.save_text()
         
         # print(word_list)
         
     def save_text(self):
         
        def cut_out(start,end):        
            start = self.text.find(start)
            end = self.text.find(end)
            if start != -1 and end != -1:
              self.text = self.text[start+1:end]
                  
        cut_out('(',')')
        cut_out('{','}')
        cut_out('[',']')

        with open('{}{}.txt'.format(self.path,self.type),'a') as f:
            f.write('{} {} \n'.format(self.idx,self.text))
        
         
     
     def run(self):
         self.convert_to_text()
           


class LLNSaver():
    def __init__(self,de,wp):
        self.de = de
        self.wp = wp
        
    
    def check_if_phrase_started(self,mode='AP'):
        while True:
            im = pyautogui.screenshot()
            left = self.wp.cursor_pos[0] - 15 *self.wp.res
            top = self.wp.cursor_pos[1]
            right =left + 10*self.wp.res
            bottom = top+5*self.wp.res
            im1 = im.crop((left, top, right, bottom))
            pixels = [i for i in im1.getdata()]
            
            #check if tuple of pixel value exists in array-pixel
            phrase_started = (36, 36, 36) in pixels
            # print(phrase_started) #True if exists, False if it doesn't
            if phrase_started:
                return True
            
            if(mode == 'AP'):
                if not self.check_if_running(im):
                    return False
            
    def check_if_phrase_ended(self):
        while True:
            im = pyautogui.screenshot()
            left = self.wp.cursor_pos[0] - 9*self.wp.res
            top = self.wp.cursor_pos[1]
            right =left + 2*self.wp.res
            bottom = top+5*self.wp.res
            im1 = im.crop((left, top, right, bottom))
            pixels = [i for i in im1.getdata()]
            
            #check if tuple of pixel value exists in array-pixel
            phrase  = (36, 36, 36) in pixels
            # print(phrase_started) #True if exists, False if it doesn't
            if not phrase:
                return 
                
        # im1.show()
    
    def check_if_running (self,im):
        left = self.wp.AP_pos[0]
        top = self.wp.AP_pos[1]
        right =left + 10
        bottom = top+10
        im1 = im.crop((left, top, right, bottom))
        pixels = [i for i in im1.getdata()]
        
        #check if tuple of pixel value exists in array-pixel
        pausing = (83, 160, 41) in pixels  
        if not pausing:
            pausing = (20,161,8) in pixels  
        return pausing
    
    def check_for_pause(self,im):
        left = self.wp.AP_pos[0]
        top = self.wp.AP_pos[1]
        right =left + 2
        bottom = top+2
        im1 = im.crop((left, top, right, bottom))
        pixels = [i for i in im1.getdata()]
        
        #check if tuple of pixel value exists in array-pixel
        pausing = (144, 26, 24) in pixels   
        if not pausing:
            pausing = (231, 2, 2) in pixels  
        return pausing
    
    def wait_for_pause(self,delay):
        while True:
            im = pyautogui.screenshot()
            pausing = self.check_for_pause(im)
            # print(pausing) #True if exists, False if it doesn't
            if pausing:
                time.sleep(delay)
                return
        # im1.show()
        
    
    def save_image_parts(self,index):
        im = pyautogui.screenshot()
        width, height = im.size
        
        # Main image
        left = self.wp.nflix_ul[0]
        top = self.wp.nflix_ul[1]
        right = self.wp.nflix_br[0]
        bottom = self.wp.nflix_br[1]
        im1 = im.crop((left, top, right, bottom))
        ratio = (right-left)/(bottom-top)
        newsize = (500, int(500/ratio))
        im1 = im1.resize(newsize)
        im1.save(self.de.path + 'images/LLNi-{}-{}.png'.format(self.de.deck,self.de.ri))
        
        
        
        # Phrase 
        left = self.wp.phrase_ul[0]
        top = self.wp.phrase_ul[1]
        right = self.wp.phrase_br[0]
        bottom = self.wp.phrase_br[1]
        im2 = im.crop((left, top, right, bottom))
        ratio = (right-left)/(bottom-top)
        
        # newsize = (500, int(500/ratio))
        # im2 = im2.resize(newsize)
        im2 = PIL.ImageOps.invert(im2)
        im2.save(self.de.path + 'phrases/LLNp-{}-{}.png'.format(self.de.deck,self.de.ri))
        
        self.ph_thread = OCRThread(im2,self.de.og_lang,self.de.path,self.de.ri,'phrases')
        self.ph_thread.start() 
        
        if self.wp.use_trans == 'ignore translation':
            shutil.copy('app_data/images/white.png', self.de.path + 'trans/LLNt-{}-{}.png'.format(self.de.deck,self.de.ri))
        else:     
            #  Translation
            left = self.wp.trans_ul[0]
            top = self.wp.trans_ul[1]
            right = self.wp.trans_br[0]
            bottom = self.wp.trans_br[1]
            im3 = im.crop((left, top, right, bottom))
            ratio = (right-left)/(bottom-top)
            
            im3 = PIL.ImageOps.invert(im3)
            
            self.tr_thread = OCRThread(im3,self.de.trans_lang,self.de.path,self.de.ri,'trans')
            self.tr_thread.start() 
            
            # newsize = (500, int(500/ratio))
            # im3 = im3.resize(newsize)
        
   
            
            im3.save(self.de.path + 'trans/LLNt-{}-{}.png'.format(self.de.deck,self.de.ri))
        
    def save_sentence(self,testing,delay):
        time.sleep(delay)
                    
        if not testing:
            self.de.ri = self.de.ri+1;
        self.save_image_parts(self.de.ri)
        self.de.save_params()
        
        