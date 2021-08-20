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

import cv2
import pytesseract
import pandas as pd
import numpy as np
import progressbar, time, os
from settings import *

# settings
deck = 'icelandic'
overwrite = True
copy_files = True



#--------------------------------------------
de = DeckSettings(deck, '', '')
de.load_params()
original_lang = de.og_lang[:-1]
trans_lang = de.trans_lang[:-1]
deck_name = de.deck
running_index = de.ri

print('-- Starting CSV Anki generator v0.1.')
data = pd.read_csv('ipa_dict/{}.csv'.format(original_lang))    
print('-- IPA dictionary for language code: {} loaded.'.format(original_lang))
data = pd.DataFrame(data)
data = data.to_numpy()
ipa_words = data[:,0]
ipa = data[:,1]

# settings



import shutil, os, progressbar
from settings import *

def copy_images(overwrite,deck):   
    
    print('-- Copying files to Anki directory.')
    
    de = DeckSettings(deck, '', '')
    de.load_params()
    original_lang = de.og_lang
    trans_lang = de.trans_lang
    deck_name = de.deck
    running_index = de.ri
    start_index = de.csv_savepoint
    if overwrite:
        start_index = 0
    max_index = 10000
    
    
    files = []
    
    for i in progressbar.progressbar(range(start_index,running_index+1)):
        if i == max_index:
            break
        files.append(de.path + 'images/LLNi-{}-{}.png'.format(deck_name,i))
        
    
    for f in files:
       # print(f)
        shutil.copy(f, 'C:/Users/domen/AppData/Roaming/Anki2/Domenic/collection.media')
        

def Convert_to_ipa(index):
    ipa_tr = ''
    pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    
    if not os.path.isfile(de.path + 'phrases/LLNp-{}-{}.png'.format(deck_name,index)):
        return
    img1 = cv2.imread(de.path + 'phrases/LLNp-{}-{}.png'.format(deck_name,index))
    word_list = pytesseract.image_to_string(img1,lang=original_lang)
    word_list_original = word_list
    blacklist=[',','|','"','-','?','.','«','!','--']
    
    for b in blacklist:
        word_list = word_list.replace(b,'')

    words = word_list.split()   
    word_list = ' '.join(words)
    
    img2 = cv2.imread(de.path + 'trans/LLNt-{}-{}.png'.format(deck_name,index))
    translation = pytesseract.image_to_string(img2,lang=trans_lang)
    
    for b in blacklist:
        translation = translation.replace(b,'')
        
    translation = translation.split()
    translation = ' '.join(translation)
    
    if translation == '':
        empty = True
       # print('-- Phrase {}: sound transcription omitted.'.format(index))
        return [word_list_original,translation,ipa_tr,empty]
    else:
        empty = False
    
    for word in words:
    
        row = np.where(ipa_words == word)[0]
        if row.size > 0:
            row = int(row[0])
            new_tr = ipa[row]
        else:
            new_tr = '--'
        ipa_tr = ipa_tr + ' ' + new_tr
    
    # ipa_tr = ipa_tr.split()
    ipt_tr = ' '.join(ipa_tr)
    ipa_tr = '['+ipa_tr+']'
        
    return [word_list,translation,ipa_tr,empty]
        # print()
        # print(ipa_tr)

def Generate_csv():
    import csv
    index = running_index
    edit_mode = 'a'
    print('-- Loaded running index value as ' + str(index))
    with open(de.path+'params.cfg') as f:
        lines = f.readlines()     
        start = int(lines[3])+1
    if overwrite:
        start = 0
        edit_mode ='w'
    with open(de.path + 'anki_import.csv', edit_mode, newline='',encoding='utf-8') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
       # spamwriter.writerow(['Front', 'Back'])
        print('-- Starting csv writer.')
        time.sleep(2.0)
        
        if start ==  index+1:
            print('-- CSV was already created, save new phrases first.')
            return
        
        for ind in progressbar.progressbar(range(start,index+1)):
          #  print('-- Phrase {}: processing images.'.format(ind))
            sentence,translation,ipa,empty = Convert_to_ipa(ind)
            if not empty:
                line_1 = '<img src="LLNi-{}-{}.png"> '.format(deck_name,ind)
                line_2 = sentence
                line_3= translation
                line_4 = ipa
                spamwriter.writerow([line_1, line_2, line_3,line_4])
                
        with open(de.path+'params.cfg') as f:
            lines = f.readlines()        
            lines[3] = str(running_index) 
        with open(de.path+'params.cfg','w') as f:
            f.writelines(lines)
    
    
Generate_csv()
if copy_files:
    copy_images(overwrite,deck)