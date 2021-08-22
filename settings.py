# -*- coding: utf-8 -*-
"""
Created on Fri Aug 20 12:53:31 2021

@author: domen
"""

  
class DeckSettings():
    def __init__(self,deck,og_lang,trans_lang,testing=False):
        self.deck = deck
        self.og_lang = og_lang
        self.trans_lang = trans_lang
        self.path = 'data/{}/'.format(deck)  
        self.testing = testing
        self.ri = 0
        self.si = 0
        self.description = ''

        
    def load_params(self,selected_deck=''):
        
        if not selected_deck == '':                
            self.deck = selected_deck
            self.path = 'data/{}/'.format(self.deck)
            
        # catch if params.cfg doesnt exist
        with open(self.path+'params.cfg') as f:
            lines = f.readlines()     
        self.ri = int(lines[0])
        self.si = self.ri
        self.og_lang = lines[1][:-1]
        self.trans_lang = lines[2][:-1]
        self.csv_savepoint = int(lines[3][:-1])
        self.description = lines[4]
        
    def save_params(self):
        with open(self.path+'params.cfg') as f:
            lines = f.readlines()      
            lines[1] = self.og_lang + '\n'
            lines[2] = self.trans_lang + '\n'
            lines[0] = str(self.ri) +'\n' 
            lines[4] = self.description 
        with open(self.path+'params.cfg','w') as f:
            f.writelines(lines)
            
    def set_index(self,target=-1):
        with open(self.path+'params.cfg') as f:
            lines = f.readlines()        
            lines[0] = str(target)+'\n'
            lines[3] = '0\n'
        with open(self.path+'params.cfg','w') as f:
            f.writelines(lines)
            
class WindowSettings():
    def __init__(self,size,res,ff_delay):
        self.ff_delay = ff_delay
        self.mode = 'manual'
        self.use_trans = ''            
        self.load_config()
        
    def load_config(self):
        
        def read_cfg(line):
            nums = line.split()
            return [int(nums[0]),int(nums[1])]       
        
        # to-do enable different user settings/profiles
        with open('user_settings.cfg') as f:
            cfg = f.readlines()      
            
        self.nflix_ul = read_cfg(cfg[0])
        self.nflix_br = read_cfg(cfg[1])
        self.phrase_ul = read_cfg(cfg[2])
        self.phrase_br = read_cfg(cfg[3])
        self.trans_ul = read_cfg(cfg[4])
        self.trans_br = read_cfg(cfg[5])
        self.cursor_pos = read_cfg(cfg[6])
        self.AP_pos = read_cfg(cfg[7])
        self.res = int(cfg[8][:-1])/2160
        self.mode = cfg[9][:-1]
        self.use_trans = cfg[10]
        
    def save_config(self):
        with open('user_settings.cfg') as f:
            lines = f.readlines()      
            lines[8] = str(int(self.res*2160)) + '\n'
            lines[9] = self.mode + '\n'
            lines[10] = self.use_trans 
        with open('user_settings.cfg','w') as f:
            f.writelines(lines)
    
            



    