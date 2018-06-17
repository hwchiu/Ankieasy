import urllib.request
from urllib.parse import quote
from bs4 import BeautifulSoup
import ssl
import subprocess
import platform
import datetime
import json
import re

def LookUp(word, data, download_dir):

    # Eliminate the end of line delimiter
    word = word.splitlines()[0]
    wordUrl = urllib.parse.quote(word, safe='')
    wordUrl = wordUrl.replace('%20','-')
    wordUrl = wordUrl.replace('%27','-')
    wordUrl = wordUrl.replace('%28','-')
    wordUrl = wordUrl.replace('%29','-')
    wordUrl = wordUrl.replace('%2F','-')
    wordUrl = wordUrl.replace('--','-')
    if wordUrl[-1] == '-':
        wordUrl = wordUrl[:-1]
    
    url='https://dictionary.cambridge.org/us/dictionary/english/{}'.format(wordUrl)

    opener=urllib.request.build_opener()
    opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
    urllib.request.install_opener(opener)
    ssl._create_default_https_context = ssl._create_unverified_context

    content = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(content, 'lxml')
    result = {}
    front_word = word + '<br>'
    back_word = ''
    guideWordStyleHead = '<font color="yellow"><b>'
    guideWordStyleTail = '</b></font>'
    posStyleHead = '<font color=#00fff9>'
    posStyleTail = '</font>'

    if word == '':
        return None

    entryBox = soup.find('div', class_ = 'entrybox english')
    if entryBox is None:
        return None
    englishTab = entryBox.find('div', id = 'dataset-american-english')
    if englishTab is None:
        englishTab = entryBox.find('div', id = 'dataset-british')
    elif englishTab is None:
        englishTab = entryBox.find('div', id = 'dataset-business-english')
    elif englishTab is None:
        return None
    
    partOfSpeech = englishTab.find_all('div', class_='entry-body__el clrd js-share-holder')
    for i in range(0,len(partOfSpeech)):
        sound = partOfSpeech[i].find('span', attrs={'data-src-mp3':True})

        if sound is not None and bool(download_dir) != False:
            try:
                urllib.request.urlretrieve(sound['data-src-mp3'], download_dir+'Py_'+word+'.mp3')
                front_word = '[sound:Py_'+word+'.mp3]' + front_word
            except urllib.error.HTTPError as err:
                print("HTTP Error:", err)
        
        posgram = partOfSpeech[i].find('span', class_='posgram ico-bg')
        if posgram is not None:
            pos = posgram.find('span').get_text() # get POS
            front_word += posStyleHead + '(' + pos + ')' + posStyleTail + '<br>'
            back_word +=  posStyleHead + '(' + pos + ')' + posStyleTail + '<br>'
        senseBlock = partOfSpeech[i].find_all('div', class_='sense-block')
        cnt = 1
        for j in range(0,len(senseBlock)):
            guideWord = senseBlock[j].find('span', class_='guideword') # get the guide word ex.(BREAK)
            if guideWord is not None:
                guideWordClear = guideWord.find('span').get_text()
                back_word += guideWordStyleHead + '(' + guideWordClear + ')' + guideWordStyleTail + '<br>'
            defBlock = senseBlock[j].find_all('div', class_='def-block pad-indent')
            for k in range(0,len(defBlock)):
                # English explain
                explain = defBlock[k].find('b', class_='def').get_text() # get the explain
                if explain[-2] == ':':
                    tmp = explain[:-2]
                    explain = tmp + '.'     # Replace the colon to dot
                if len(defBlock) != 1:    # If the part of speech has more than one meaning, number the meaning list
                    front_word += str(cnt) + '. '
                    back_word += str(cnt) + '. '
                back_word += explain + '<br>'

                # example sentence
                defBody = defBlock[k].find('span', class_='def-body')
                if defBody is not None:
                    exampleSentence = defBody.find('span', class_='eg').get_text() # get example sentence
                    front_word += exampleSentence
                front_word += '<br>'
                cnt += 1

    # Some meaning will reveal the 'word' in back_word
    back_word = back_word.replace(word,'___')

    result['front_word'] = front_word
    result['back_word'] = back_word
    print('<<<'+word+'>>>'+'\n')
    print('front_word = '+'\n'+front_word)
    print('back_word = '+'\n'+back_word)
    print('-----------------------------------------')
    return result
