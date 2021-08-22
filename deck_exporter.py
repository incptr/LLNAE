# -*- coding: utf-8 -*-
"""
Created on Wed Aug 18 02:00:51 2021

@author: domen
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Aug 18 00:28:58 2021

@author: domen
"""

# try using langdetect

# import cv2
import pytesseract
import pandas as pd
import numpy as np
import progressbar, time, os
import shutil, os, progressbar
from settings import *
import csv,glob
from LLNAE import NewDeckPopup
try:
    from PIL import Image
except ImportError:
    import Image
    
# # settings
# deck = 'icelandic'
# overwrite = True
# copy_files = True


# def load_deck_config():
#     return
# #--------------------------------------------
#     de = DeckSettings(deck, '', '')
#     de.load_params()
#     original_lang = de.og_lang[:-1]
#     trans_lang = de.trans_lang[:-1]
#     deck_name = de.deck
#     running_index = de.ri
    
#     # print('-- Starting CSV Anki generator v0.1.')
#     data = pd.read_csv('ipa_dict/{}.csv'.format(original_lang))    
#     # print('-- IPA dictionary for language code: {} loaded.'.format(original_lang))
#     data = pd.DataFrame(data)
#     data = data.to_numpy()
#     ipa_words = data[:,0]
#     ipa = data[:,1]

# # settings




class DeckExporter():
    
    def __init__(self,DeckSettings):
        self.deck_set = DeckSettings 
        self.exp_mode = ''
        self.use_ipa = False
        self.open_csv = False
        self.overwrite = False
        self.copy_img = False
        self.load_config()
        self.profile_name = ''
        files = filter( os.path.isfile,
                      glob.glob(self.deck_set.path + 'images/' + '*') )
        files = sorted( files,
                              key = os.path.getmtime) 
        self.exp_length = len(files)
        
    def load_config(self):       
        # to-do enable different user settings/profiles
        with open('exp_settings.cfg') as f:
            cfg = f.readlines()      
        self.exp_mode = cfg[0][:-1]
        self.use_ipa = int(cfg[1])
        self.open_csv = int(cfg[2])
        self.overwrite = int(cfg[3])
        self.copy_img = int(cfg[4])
        
    def save_config(self):
        with open('exp_settings.cfg') as f:
            lines = f.readlines()      
            lines[0] = str(self.exp_mode) + '\n'
            lines[1] = str(self.use_ipa) + '\n'
            lines[2] = str(self.open_csv) + '\n'
            lines[3] = str(self.overwrite) + '\n'
            lines[4] = str(self.copy_img) + '\n'
        with open('exp_settings.cfg','w') as f:
            f.writelines(lines)
            
    def initialize_export(self):
        
        data = pd.read_csv('ipa_dict/{}.csv'.format(self.deck_set.og_lang))    
        # print('-- IPA dictionary for language code: {} loaded.'.format(self.deck_set.og_lang))
        data = pd.DataFrame(data)
        self.data = data.to_numpy()
        self.ipa_words = self.data[:,0]
        self.ipa = self.data[:,1]
        self.running_idx = self.deck_set.ri  
        
        if self.overwrite:
            self.start_idx = 0
            self.edit_mode ='w'
        else:
            with open(self.deck_set.path+'params.cfg') as f:
                self.lines = f.readlines()     
                self.start_idx = int(self.lines[3])+1
            self.edit_mode = 'a'
            
        files = filter( os.path.isfile,
                      glob.glob(self.deck_set.path + 'images/' + '*') )
        files = sorted( files,
                              key = os.path.getmtime) 
        self.exp_length = len(files)
        
        # print('-- Loaded running index value as ' + str(self.running_idx))    
        

        

    
    def finish_export(self):      
        with open(self.deck_set.path+'params.cfg') as f:
            lines = f.readlines()        
            lines[3] = str(self.running_idx) + '\n'
        with open(self.deck_set.path + 'params.cfg','w') as f:
            f.writelines(lines)
    
    
        if self.copy_img:
            self.copy_images()
            
        if self.open_csv:
            # fileName = listbox_1.get(ACTIVE)
            os.system("notepad.exe "  + self.deck_set.path + '{}.csv'.format(self.deck_set.deck))
        return True
    
    def copy_images(self):   
        
        self.new_deck_pop = NewDeckPopup()
        
        if self.profile_name == '':        
            [self.profile_name,ok] = self.new_deck_pop.pop(text='Enter your Anki profile name.',title='Copy files')
        else:
            ok = True
        
        if ok:        
            # print('-- Copying files to Anki directory.')
            self.deck_set.load_params()
            deck_name = self.deck_set.deck
            running_index = self.deck_set.ri
            start_index = self.deck_set.csv_savepoint
            
            if self.overwrite:
                # print('overwrite')
                start_index = 0
                files = filter( os.path.isfile,
                              glob.glob(self.deck_set.path + 'images/' + '*') )
                files = sorted( files,
                                      key = os.path.getmtime)    
            else:
                # fix only partly appending
                files = []        
                for i in range(start_index,running_index+1):
                    # if i == max_index:
                    #     break
                    files.append(self.deck_set.path + 'images/LLNi-{}-{}.png'.format(self.deck_set.deck,i))
                    
            # print(files)
            for f in files:
                
                shutil.copy(f, os.getenv('APPDATA') + '/Anki2/{}/collection.media'.format(self.profile_name))
            return True
        else:
                return False
    
    def convert_to_ipa(self,index):
        
        ipa_tr = ''
        pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'    
        img1 = Image.open(self.deck_set.path + 'phrases/LLNp-{}-{}.png'.format(self.deck_set.deck,index))
        word_list = pytesseract.image_to_string(img1,lang=self.deck_set.og_lang)
        word_list_original = word_list
        blacklist=[',','|','"','-','?','.','«','!','--']
        
        for b in blacklist:
            word_list = word_list.replace(b,'')
    
        words = word_list.split()   
        word_list = ' '.join(words)
        
        img2 = Image.open(self.deck_set.path + 'trans/LLNt-{}-{}.png'.format(self.deck_set.deck,index))
        translation = pytesseract.image_to_string(img2,lang=self.deck_set.trans_lang)
        
        for b in blacklist:
            translation = translation.replace(b,'')
            
        translation = translation.split()
        translation = ' '.join(translation)
        
        if translation == '':
            empty = True
            return [word_list_original,translation,ipa_tr,empty]
        else:
            empty = False
            
            
        if self.use_ipa:          
        
            for word in words:
            
                row = np.where(self.ipa_words == word)[0]
                if row.size > 0:
                    row = int(row[0])
                    new_tr = self.ipa[row]
                else:
                    new_tr = '--'
                ipa_tr = ipa_tr + ' ' + new_tr
            
    
            ipt_tr = ' '.join(ipa_tr)
            ipa_tr = '['+ipa_tr+']'
        else:
            ipa_tr = ' '     
        
            
        return [word_list,translation,ipa_tr,empty]

    