# Language Learning with Netflix - Anki Exporter
LLNAE is a small app, designed to capture flashcards in the background while watching Netflix with the extension "Language learning with Netflix" for Google Chrome. It can be used in the different modes allowing for manual capturing, following along and quick extraction.

<!-- ![alt text](https://i.ibb.co/GsQJx0C/View.png) ![alt text](https://i.ibb.co/d0NdZVB/rec.png) -->

LLNAE provides a flashcard deck viewer that allows the user to delete and favorite cards as well as an exporter. This generates a csv file that can be directly imported into Anki. Furthermore, it can provide phonetic transcription by searching for words in a IPA dictionary. 



## Requirements
In order for LLNAE to work properly, Google Chrome needs to be run in sandboxing program. This is needed in order to avoid Netflixes screenshot blocking mechanism. A common choice for sandboxing is  [Sandboxie](https://sandboxie-plus.com/downloads/  "Sandboxie").

Furthermore the [Language learning with Netflix](https://chrome.google.com/webstore/detail/language-learning-with-ne/hoombieeljmmljlkjmnheibnpciblicm?hl=en "LLN") extension needs to be installed and active while using Netflix. It can be turned on by a button in the video player after installation. Please note that without this plugin, the modes "follow along" and "fast forward" are not available and general functionality might be affected. 

For the image-to-text processing, Google's [OCR-Tesseract](https://github.com/UB-Mannheim/tesseract/wiki "Tesseract") is used. When following the installation, please make sure to install the language packs and writing systems that you want to utilize. The language settings in LLNAE are abbreviated with the same notation that Tesseract uses. If you create new decks, make sure to give it the proper values (e.g. 'isl' corresponds to Icelandic, 'nor' to Norwegian). 

## Installation

## Setup

## Using the app




