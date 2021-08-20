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
        
    def load_params(self):
        with open(self.path+'params.cfg') as f:
            lines = f.readlines()     
        self.ri = int(lines[0])
        self.si = self.ri
        self.og_lang = lines[1]
        self.trans_lang = lines[2]
        self.csv_savepoint = int(lines[3])
        
    def save_params(self):
        with open(self.path+'params.cfg') as f:
            lines = f.readlines()        
            lines[0] = str(self.ri) +'\n' 
        with open(self.path+'params.cfg','w') as f:
            f.writelines(lines)
            
    def set_index(self,target=-1):
        with open(self.path+'params.cfg') as f:
            lines = f.readlines()        
            lines[0] = str(target)+'\n'
            lines[3] = '0'
        with open(self.path+'params.cfg','w') as f:
            f.writelines(lines)
            
class WindowSettings():
    def __init__(self,size,res,ff_delay):
        self.ff_delay = ff_delay
        
        def read_cfg(line):
            nums = line.split()
            return [int(nums[0]),int(nums[1])]
        
        self.res = res/2160
        with open('user_settings.cfg') as f:
            cfg = f.readlines()   
            
        if size=='half':
            
            self.nflix_ul = read_cfg(cfg[0])
            self.nflix_br = read_cfg(cfg[1])
            self.phrase_ul = read_cfg(cfg[2])
            self.phrase_br = read_cfg(cfg[3])
            self.trans_ul = read_cfg(cfg[4])
            self.trans_br = read_cfg(cfg[5])
            self.cursor_pos = read_cfg(cfg[6])
            self.AP_pos = read_cfg(cfg[7])
            
        elif size =='full':
            self.nflix_ul = read_cfg(cfg[8])
            self.nflix_br = read_cfg(cfg[9])
            self.phrase_ul = read_cfg(cfg[10])
            self.phrase_br = read_cfg(cfg[11])
            self.trans_ul = read_cfg(cfg[12])
            self.trans_br = read_cfg(cfg[13])
            self.cursor_pos = read_cfg(cfg[14])
            self.AP_pos = read_cfg(cfg[15])
    


    