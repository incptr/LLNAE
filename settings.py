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
    def __init__(self,size,res):
        
        self.res = res/2160
        
        if size=='half':
            self.nflix_ul = [1920,740]
            self.nflix_br = [1920+1100,740+619]
            self.phrase_ul = [2026,1880]
            self.phrase_br = [2026+1692,1880+103]
            self.trans_ul = [2026,1970]
            self.trans_br = [2026+1692,1970+103]
            self.cursor_pos = [2881,2120]
            self.AP_pos = [3790,1880]
            
        elif size =='full':
            self.nflix_ul = [0,120]
            self.nflix_br = [3040,1700]
            self.phrase_ul = [614,1840]
            self.phrase_br = [3319,1987]
            self.trans_ul = [614,1975] 
            self.trans_br = [3319,2105]
            self.cursor_pos = [1919,2118]
            self.AP_pos = [3763,1878]
    


    