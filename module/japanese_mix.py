import urllib.request
from urllib.parse import quote
from urllib.request import Request, urlopen
import ssl
from bs4 import BeautifulSoup
import subprocess
import platform
import datetime
import json
import re
from hanziconv import HanziConv # https://pypi.python.org/pypi/hanziconv/0.2.1
from re import compile as _Re

_unicode_chr_splitter = _Re( '(?s)((?:[\u2e80-\u9fff])|.)' ).split

def getWord(soup):
    output = ''
    wordText = soup.find('div', class_='word-text')
    h2 = wordText.find('h2')
    if h2 != None:
        output = h2.get_text()
    return output

def getPartOfSpeechBlock(soup, sentenceCnt, front_word, back_word):
    meaning = []
    exampleSentence = {}
    dt = soup.find('dt')
    if dt != None:
        pos = dt.get_text()
        pos = pos.replace(chr(32), '')
        pos = pos.replace(chr(10), '')
        pos = HanziConv.toTraditional(pos)
        front_word += '(' + pos + ')<br>'
        back_word += '(' + pos + ')<br>'
    meaning = getMeaning(soup)                              # list
    exampleSentence = getExampleSentence(soup, sentenceCnt) # dict
    print(exampleSentence)
    for i in range(0, len(meaning)):
        front_word += str(i+1) + '. ' + exampleSentence['JP'][i] + '<br>'
        back_word += str(i+1) + '. ' + meaning[i] + '<br>' + exampleSentence['CH'][i] + '<br>'
    return {'front_word': front_word, 'back_word': back_word}

def getSoundAndTitle(soup, download_dir, word, differentWord):
    output = ''
    diffWordToken = ''
    if differentWord > 1:
        diffWordToken = '_' + str(differentWord)
    print(' ')
    print('<<' + word + diffWordToken + '>>')
    print(' ')
    pronouncesDiv = soup.find('div', class_ = 'pronounces')
    if pronouncesDiv != None:
        pronouncesSpan = pronouncesDiv.find('span', class_ = 'word-audio')
        if pronouncesSpan != None:
            soundUrl = pronouncesSpan['data-src']
            try:
                urllib.request.urlretrieve(soundUrl, download_dir + 'Jp_' + word + diffWordToken + '.mp3')
                output = '[sound:Jp_' + word + diffWordToken + '.mp3]'
            except urllib.error.HTTPError as err:
                print('HJ_err=', err)
    return output

def getMeaning(soup):           # list
    output = []
    for dd in soup.find_all('dd'):
        h3 = dd.find('h3')
        if h3 != None:
            meaning = h3.get_text()
            meaning = meaning.replace(chr(32), '')
            meaning = meaning.replace(chr(10), '')
            output.append(meaning)
    return output

def getExampleSentence(soup, sentenceCnt):   # dict
    output = {}
    output['JP'] = []
    output['CH'] = []
    sentenceJP = ''
    sentenceCH = ''
    for dd in soup.find_all('dd'):
        ul = dd.find('ul')
        if ul != None:
            cnt = 0
            for li in ul.find_all('li'):
                pJP = li.find('p', class_ = 'def-sentence-from')
                pCH = li.find('p', class_ = 'def-sentence-to')
                if pJP != None:
                    sentenceJP = pJP.get_text()
                    sentenceJP = sentenceJP.replace(chr(32), '')
                    sentenceJP = sentenceJP.replace(chr(10), '')
                if pCH != None:
                    sentenceCH = pCH.get_text()
                    sentenceCH = sentenceCH.replace(chr(32), '')
                    sentenceCH = sentenceCH.replace(chr(10), '')
                output['JP'].append(sentenceJP)
                output['CH'].append(sentenceCH)
                cnt += 1
                if cnt == sentenceCnt:
                    break
        if cnt == 0:
            output['JP'].append('')
            output['CH'].append('')
    return output

def LookUp(word, data, download_dir):
    
    result = {}
    front_word = ''
    back_word = ''
    reading = ''
    furi = ''
    furiChild = []
    furiList = []
    text = ''
    textChild = []
    textList = []
    cnt = 0
    needHJSound = True
    sentenceCnt = 1
    differentWord = 1

    opener=urllib.request.build_opener()
    opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
    urllib.request.install_opener(opener)
    ssl._create_default_https_context = ssl._create_unverified_context

    # Eliminate the end of line delimiter
    word = word.splitlines()[0]
    wordUrl = urllib.parse.quote(word, safe='')

    hj_Url = 'https://dict.hjenglish.com/jp/jc/{}'.format(wordUrl)
    hj_Content = urllib.request.urlopen(hj_Url).read()
    hj_Soup = BeautifulSoup(hj_Content, 'lxml')

    if word == '':
        return None
    # print(hj_Soup)
    wordDetailsContent = hj_Soup.find('section', class_ = 'word-details-content')
    if wordDetailsContent != None:
        for wordDetailsPane in wordDetailsContent.find_all('div', class_ = 'word-details-pane'):
            word = getWord(wordDetailsPane)
            front_word += getSoundAndTitle(wordDetailsPane, download_dir, word, differentWord) + word + '<br>'
            detailGroups = wordDetailsPane.find('section', class_ = 'detail-groups')
            if detailGroups != None:
                for posSoup in detailGroups.find_all('dl'):
                    frontAndBack = getPartOfSpeechBlock(posSoup, sentenceCnt, front_word, back_word)
                    front_word = frontAndBack['front_word']
                    back_word = frontAndBack['back_word']
            differentWord += 1
            print('front_word', front_word)
            print('back_word', back_word)
        result['front_word'] = front_word
        result['back_word'] = HanziConv.toTraditional(back_word)
        result['read_word'] = ''
        return result
    elif hj_Soup.find('div', class_ = 'word-suggestions') != None:
        print(' ')
        print('<< Word not found!!! >>')
        print(' ')
        return None