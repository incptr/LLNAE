# -*- coding: utf-8 -*-
"""
Created on Tue Aug 17 18:34:04 2021

@author: domen
"""

from initialize import *
from state_machine import *
from settings import *
import threading, time, os, ctypes

#------------ SETTINGS ---------------    
testing = False
mode = 'manual'
window_mode = 'half'
reading_delay = 5.0
ff_delay = 0.0
time.sleep(1)
res = 2160
deck = 'icelandic'
og_lang = 'isl'
trans_lang = 'nor'
generate_csv_after = True
       
def thread_function(name):
    print('Thread started')
    time.sleep(2)
    print('Thread ended')

if __name__ == "__main__":    
    
        
    wp = WindowSettings(window_mode,res,ff_delay)
    de = DeckSettings(deck, og_lang, trans_lang,testing)
    saver = LLNSaver(de,wp)
    statemachine = StateMachine(saver,mode)   
    

    startup(de)
    statemachine.main_loop()
            

 
    

 

