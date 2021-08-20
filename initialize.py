# -*- coding: utf-8 -*-
"""
Created on Fri Aug 20 12:12:15 2021

@author: domen
"""
import os, ctypes,glob

def check_directory(path,hidden = False):   
    if not os.path.isdir(path):
        os.mkdir(path)
        if hidden:
            FILE_ATTRIBUTE_HIDDEN = 0x02
            ret = ctypes.windll.kernel32.SetFileAttributesW(path, FILE_ATTRIBUTE_HIDDEN)
        return False
    else:
        return True       
    

    
def startup(de):
        
    def create_config():
        with open(base_path+'params.cfg', 'w') as f:
          # running index, set based on last image name
          ri = -1
          list_of_files = filter( os.path.isfile,
                        glob.glob(de.path + 'images/' + '*') )
          list_of_files = sorted( list_of_files,
                                key = os.path.getmtime)
          if len(list_of_files) > 0:
              list_of_files.sort(key=os.path.getctime)
              last_file = list_of_files[-1]
              # print(last_file)
              ri = int(last_file[28+len(de.deck):-4])
              # print(ri)
          f.write('%d \n' % ri)
          # original language
          f.write(de.og_lang +'\n')
          # original language
          f.write(de.trans_lang +'\n')
          # savepoint csv
          f.write('0')
        print('++ Config created.'.format(de.deck))
    
    print('-- Starting netflix flashcard saver v0.1')
    print('-- This beta version is still in developement and was created by Domenic Geiseler')
    print('-- Welcome to the main menu. You can save a flashcard by pressing space or emitting a phrase by pressing left ctrl. To end the program use the escape key.')
    base_path = 'data/{}/'.format(de.deck)  
    
    if not (check_directory(base_path) or \
            check_directory(base_path+'/images') or \
            check_directory(base_path+'/phrases',True) or \
            check_directory(base_path+'/trans',True)):
        print('++ Not all directories for the deck \'{}\' were found. Metadata created.'.format(de.deck))
    
    if os.path.isfile(base_path+'params.cfg'):
        if not os.stat(base_path+'params.cfg').st_size:
            create_config()
    else:
        create_config()
    
    de.load_params()