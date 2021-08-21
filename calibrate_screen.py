# -*- coding: utf-8 -*-
"""
Created on Tue Aug 17 18:34:04 2021

@author: domen
"""

import threading, time, os
from ctypes import windll, Structure, c_long, byref
from pynput.keyboard import Key, Listener


xy = [0,0]

class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]



def queryMousePosition():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return [pt.x,pt.y]


    
def on_press(key):
    global xy
    if key == Key.ctrl_l:
        xy = queryMousePosition()
        print(xy)
        return False
        

    
def on_release(key):
    if key == Key.esc:
        # Stop listener
        print('-- Shutting down.')
        # return False
        
        
def start_calibration():    
        

    print('-- Calibrating positions')

    
    with open('user_settings.cfg') as f:
        cfg_lines = f.readlines()        
        
    for ind,val in enumerate(cfg_lines):
        print('Please mark point #{}'.format(ind))
        with Listener(  
                       on_press=on_press,
                       on_release=on_release) as listener:
                   listener.join() 
        cfg_lines[ind] = '{} {}\n'.format(xy[0],xy[1])
        if ind == 7:
            break
    
    
    with open('user_settings.cfg','w') as f:
        f.writelines(cfg_lines)
        

