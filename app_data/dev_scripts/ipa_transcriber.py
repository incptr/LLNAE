# -*- coding: utf-8 -*-
"""
Created on Wed Aug 18 00:28:58 2021

@author: domen
"""

import cv2
import pytesseract
import pandas as pd
import numpy as np

# %%import xlsv
data = pd.read_csv('ipa_dict/ipa.csv')    
data = pd.DataFrame(data)
data = data.to_numpy()
ipa_words = data[:,0]
ipa = data[:,1]


# %% read text
with open('index.dm') as ind:
    index = int(ind.readline())
for i in range(index):
    
    ipa_tr = ''
    pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    img = cv2.imread('images/sentence_{}.png'.format(i))
    word_list = pytesseract.image_to_string(img,lang='isl')
    word_list = word_list.replace(',', '')
    word_list = word_list.replace('|', '')
    word_list = word_list.replace('"', '')
    word_list = word_list.replace('„', '')
    words = word_list.split()
    
    for word in words:
    
        row = np.where(ipa_words == word)[0]
        if row.size > 0:
            row = int(row[0])
            new_tr = '['+ipa[row]+']'
        else:
            new_tr = '--'
        ipa_tr = ipa_tr + ' ' + new_tr
   # print(' '.join(words))
    print(ipa_tr)

# print(text)