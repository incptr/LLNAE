# -*- coding: utf-8 -*-
"""
Created on Fri Aug 20 13:11:12 2021

@author: domen
"""
from initialize import *
from LLNSaver import *
from settings import *
import threading, time, os, ctypes

class StateMachine():
    def __init__(self,LLNSaver,mode):
        self.saver = LLNSaver
        self.mode = mode
        self.shutdown_req = False
        self.listener = []
        
    def mode_loop(self):
        # manual mode
  
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
                    print("++ Phrase saved")                    
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
                    pyautogui.press('right')
                
                
        
        
    # def main_loop(self):
    #     def on_release(key):
    #         if key == Key.esc:
    #             # Stop listener
    #             print('-- Shutting down. {} phrase(s) saved.'.format(self.saver.de.ri-self.saver.de.si))
    #             return False
        
    #     def on_press(key):
    #         if key == Key.ctrl_l:
    #             self.saver.save_sentence(self.saver.de.testing,0.0)
    #             print("++ Phrase saved.")
                
    #         elif key == Key.ctrl_r:
    #             print('-- !! WARNING: THIS WILL DELETE ALL IMAGES. CONTINUE (Y/N)?')
    #             delete_query = input()       
                
    #             if delete_query.lower() == 'y':                
    #                 self.saver.de.set_index(-1)
    #                 dir = self.saver.de.path + 'images'
    #                 for f in os.listdir(dir):
    #                     os.remove(os.path.join(dir, f))
    #                 dir = self.saver.de.path + 'phrases'
    #                 for f in os.listdir(dir):
    #                     os.remove(os.path.join(dir, f))
    #                 dir = self.saver.de.path + 'trans'
    #                 for f in os.listdir(dir):
    #                     os.remove(os.path.join(dir, f))
    #                 print('++ Index reset to 0. All images deleted')
    #             else:
    #                 print('-- Aborted')
          
            
    #         elif key == Key.shift:
    #             self.mode = 'ff'
    #             print('-- Switched to fast forward ')
    #             return False
            
    #         elif key == Key.alt_l:
    #             self.mode = 'follow along'
    #             print('-- Switched to follow along')
    #             return False
            
    
    #     while True:
            
    #         if self.mode == 'manual':
    #             # Collect  until released  
    #             with Listener(  
    #                     on_press=on_press,
    #                     on_release=on_release) as listener:
    #                 listener.join()
    #             if self.mode == 'manual':
    #                 break
                
    #         elif self.mode == 'ff':
    #             im = pyautogui.screenshot()
    #             if self.saver.check_if_running(im):
    #                 self.saver.check_if_phrase_started()
    #                 self.saver.save_sentence(self.saver.de.testing,self.saver.wp.ff_delay)
    #                 print("++ Phrase saved.")
    #                 pyautogui.press('right')
                    
    #         elif self.mode == 'follow along':
    #             self.saver.check_if_phrase_started('NAP')
    #             self.saver.save_sentence(self.saver.de.testing,0.0)
    #             print("++ Phrase saved.")
    #             self.saver.check_if_phrase_ended()