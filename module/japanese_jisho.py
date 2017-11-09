import urllib.request;
from urllib.parse import quote
from bs4 import BeautifulSoup
import subprocess
import platform
import datetime
import json
import wget
import re
from re import compile as _Re

_unicode_chr_splitter = _Re( '(?s)((?:[\u2e80-\u9fff])|.)' ).split

def LookUp(word, data):
    result = {}

    # Eliminate the end of line delimiter
    word = word.splitlines()[0]
    wordUrl = urllib.parse.quote(word, safe='')
    url="http://jisho.org/search/{}".format(wordUrl)
    content = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(content, 'lxml')
    front_word = ""
    back_word = ""
    furi = ""
    furiChild = []
    furiList = []
    text = ""
    textChild = []
    textList = []
    reading = ""
    cnt = 0
    download_dir = ""

    if "download_dir" in data:
        download_dir = data['download_dir']
        
    if word == "":
        return None
        
    wrongSpelling = soup.find('div', id='no-matches')
    if wrongSpelling is not None:
        return None
    
    print(" ")
    print('<<'+word+'>>')
    print(" ")

    for i in soup.find_all('div', class_='exact_block'):

        firstBlock = i.find('div', class_='concept_light clearfix')
        partJP = firstBlock.find('div', class_='concept_light-wrapper')
        partEN = firstBlock.find('div', class_='concept_light-meanings')
        status = partJP.find('div', class_='concept_light-status')
        if(status != None):
            audio = status.find('audio')
            if audio != None and download_dir != "":
                source = audio.find('source')
                wget.download('http:'+source['src'], out=download_dir+"Jp_"+word+".mp3")
                # Insert the sound media into the card
                front_word += "[sound:Jp_"+word+".mp3]"
        front_word += word + "<br>"
        
        for j in partJP.find_all('span', class_='furigana'):
            furiCnt=0
            for child in j.children:
                furiChild.append(child.string)
                furiCnt = furiCnt + 1
            furiList = list(filter(("\n").__ne__, furiChild))
        for j in partJP.find_all('span', class_='text'):
            textCnt = 0
            for child in j.children:
                textChild.append(child.string)
                textCnt = textCnt + 1
            for k in range(0,len(textChild)):
                for chr in _unicode_chr_splitter( textChild[k] ):
                    if chr != '\n' and chr != ' ' and chr != '':
                        textList.append(chr)
        
        for j in range(0,len(textList)):
            if(furiList[j] == None):
                reading += textList[j] 
            else:
                reading += " " + textList[j] + "[" + furiList[j] + "]" 
        for j in partEN.find_all('div', class_="meanings-wrapper"):
            for k in j.find_all('div', class_="meaning-wrapper"):
                cnt = cnt + 1
                back_word += str(cnt) + '. '
                for q in k.find_all('span', class_="meaning-meaning"):
                    back_word += q.get_text() + '<br>'

    result['read_word'] = reading
    result['front_word'] = front_word
    result['back_word'] = back_word
    return result
