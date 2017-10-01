import urllib.request;
from urllib.parse import quote
from bs4 import BeautifulSoup
import subprocess
import platform
import datetime
import json
import wget

def LookUp(word, data):
    # Eliminate the end of line delimiter
    word = word.splitlines()[0]
    wordUrl = urllib.parse.quote(word, safe='')
    wordUrl = wordUrl.replace('%20','-')
    url="https://dictionary.cambridge.org/us/dictionary/english/{}".format(wordUrl)
    content = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(content, 'lxml')
    result = {}
    front_word = word + '\n'
    back_word = ""
    download_dir = ""
    cnt = 1

    tabEntry = soup.find('div', class_='tabs tabs-entry js-tabs-wrap js-toc')
    english = tabEntry.find('div', class_='tabs__content on', attrs={"data-tab": "ds-american-english"})
    if(english is None):
        english = tabEntry.find('div', class_='tabs__content on', attrs={"data-tab": "ds-british"})
        if(english is None):
            english = tabEntry.find('div', class_='tabs__content on', attrs={"data-tab": "ds-business-english"})

    partOfSpeech = english.find_all('div', class_='entry-body__el clrd js-share-holder')
    for i in range(0,len(partOfSpeech)):
        posgram = partOfSpeech[i].find('span', class_='posgram ico-bg')
        if(posgram is not None):
            pos = posgram.find('span').get_text() # get POS
            front_word += pos + '\n'
            back_word += pos + '\n'
        senseBlock = partOfSpeech[i].find_all('div', class_='sense-block')
        for j in range(0,len(senseBlock)):
            guideWord = senseBlock[j].find('span', class_='guideword') # get the guide word ex.(BREAK)
            if(guideWord is not None):
                guideWordClear = guideWord.find('span').get_text()
                back_word += '\t' + '(' + guideWordClear + ')' + '\n'
            defBlock = senseBlock[j].find_all('div', class_='def-block pad-indent')
            for k in range(0,len(defBlock)):
                # English explain
                explain = defBlock[k].find('b', class_='def').get_text() # get the explain
                if(explain[-2] == ':'):
                    tmp = explain[:-2]
                    explain = tmp + '.' # Replace the colon to dot
                back_word += '\t\t' + str(cnt) + '. ' + explain + '\n'

                # example sentence
                defBody = defBlock[k].find('span', class_='def-body')
                if(defBody is not None):
                    exampleSentence = defBody.find('span', class_='eg').get_text() # get example sentence
                    front_word += str(cnt) + '. ' + exampleSentence + '\n'
                else:
                    front_word += str(cnt) + '. ' + '\n'
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
