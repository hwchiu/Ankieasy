import urllib.request;
from urllib.parse import quote
from bs4 import BeautifulSoup
import subprocess
import platform
import datetime
import json
import wget
import re

def LookUp(word, data):
    # Eliminate the end of line delimiter
    word = word.splitlines()[0]
    wordUrl = urllib.parse.quote(word, safe='')
    wordUrl = wordUrl.replace('%20','-')
    url="https://dictionary.cambridge.org/us/dictionary/english/{}".format(wordUrl)
    content = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(content, 'lxml')
    result = {}
    front_word = word + '<br>'
    back_word = ''
    download_dir = ''
    guideWordStyleHead = '<font color="yellow"><b>'
    guideWordStyleTail = '</b></font>'
    posStyleHead = '<font color=#00fff9>'
    posStyleTail = '</font>'
    cnt = 1

    if "download_dir" in data:
        download_dir = data['download_dir']

    if word == "":
        return None

    tabEntry = soup.find('div', class_='tabs tabs-entry js-tabs-wrap js-toc')
    if(tabEntry is None):
        return None

    english = tabEntry.find('div', class_='tabs__content on', attrs={"data-tab": "ds-american-english"})
    if(english is None):
        english = tabEntry.find('div', class_='tabs__content on', attrs={"data-tab": "ds-british"})
        if(english is None):
            english = tabEntry.find('div', class_='tabs__content on', attrs={"data-tab": "ds-business-english"})

    partOfSpeech = english.find_all('div', class_='entry-body__el clrd js-share-holder')
    sound = partOfSpeech[0].find('span', attrs={'data-src-mp3':True})

    if(sound is not None and sound['data-src-mp3'] is not None):
        wget.download(sound['data-src-mp3'], out=download_dir+"Py_"+word+".mp3")
        front_word = "[sound:Py_"+word+".mp3]" + front_word
    for i in range(0,len(partOfSpeech)):
        posgram = partOfSpeech[i].find('span', class_='posgram ico-bg')
        if(posgram is not None):
            pos = posgram.find('span').get_text() # get POS
            front_word += posStyleHead + '(' + pos + ')' + posStyleTail + '<br>'
            back_word +=  posStyleHead + '(' + pos + ')' + posStyleTail + '<br>'
        senseBlock = partOfSpeech[i].find_all('div', class_='sense-block')
        for j in range(0,len(senseBlock)):
            guideWord = senseBlock[j].find('span', class_='guideword') # get the guide word ex.(BREAK)
            if(guideWord is not None):
                guideWordClear = guideWord.find('span').get_text()
                back_word += guideWordStyleHead + '(' + guideWordClear + ')' + guideWordStyleTail + '<br>'
            defBlock = senseBlock[j].find_all('div', class_='def-block pad-indent')
            for k in range(0,len(defBlock)):
                # English explain
                explain = defBlock[k].find('b', class_='def').get_text() # get the explain
                if(explain[-2] == ':'):
                    tmp = explain[:-2]
                    explain = tmp + '.' # Replace the colon to dot
                back_word += str(cnt) + '. ' + explain + '<br>'

                # example sentence
                defBody = defBlock[k].find('span', class_='def-body')
                if(defBody is not None):
                    exampleSentence = defBody.find('span', class_='eg').get_text() # get example sentence
                    front_word += str(cnt) + '. ' + exampleSentence + '<br>'
                else:
                    front_word += str(cnt) + '. ' + '<br>'
                cnt += 1

    # Some meaning will reveal the "word" in back_word
    back_word = back_word.replace(word,"___")

    result['front_word'] = front_word
    result['back_word'] = back_word
    print('<<<'+word+'>>>'+'\n')
    print('front_word = '+'\n'+front_word)
    print('back_word = '+'\n'+back_word)
    print('-----------------------------------------')
    return result
