import urllib.request
from urllib.parse import quote
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import subprocess
import platform
import datetime
import json
import wget
import re
from hanziconv import HanziConv # https://pypi.python.org/pypi/hanziconv/0.2.1
from re import compile as _Re

_unicode_chr_splitter = _Re( '(?s)((?:[\u2e80-\u9fff])|.)' ).split

def LookUp(word, data):
    
    result = {}
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
    needHJSound = False

    # Eliminate the end of line delimiter
    word = word.splitlines()[0]
    wordUrl = urllib.parse.quote(word, safe='')

    jisho_Url = "http://jisho.org/search/{}".format(wordUrl)
    jisho_Content = urllib.request.urlopen(jisho_Url).read()
    jisho_Soup = BeautifulSoup(jisho_Content, 'lxml')

    hj_Url = "https://dict.hjenglish.com/jp/jc/{}".format(wordUrl)
    req = Request(hj_Url, headers={'User-Agent': 'Mozilla/5.0'})
    hj_Content = urllib.request.urlopen(req).read()
    hj_Soup = BeautifulSoup(hj_Content, 'lxml')

    if "download_dir" in data:
        download_dir = data['download_dir']
        
    if word == "":
        return None
        
    wrongSpelling = jisho_Soup.find('div', id='no-matches')
    if wrongSpelling is not None:
        return None
    
    print(" ")
    print('<<'+word+'>>')
    print(" ")

    for i in jisho_Soup.find_all('div', class_='exact_block'):

        firstBlock = i.find('div', class_='concept_light clearfix')
        partJP = firstBlock.find('div', class_='concept_light-wrapper')
        partEN = firstBlock.find('div', class_='concept_light-meanings')
        status = partJP.find('div', class_='concept_light-status')
        if status != None:
            audio = status.find('audio')
            if audio != None and download_dir != "":
                source = audio.find('source')
                if source != None and source['src'] != None:
                    wget.download('http:'+source['src'], out=download_dir+"Jp_"+word+".mp3")
                    # Insert the sound media into the card
                    front_word += "[sound:Jp_"+word+".mp3]"
            else:
                needHJSound = True
        else:
            needHJSound = True

        for j in partJP.find_all('span', class_='furigana'):
            furiCnt = 0
            for child in j.children:
                furiChild.append(child.string)
                furiCnt += 1
            furiList = list(filter(("\n").__ne__, furiChild))
        for j in partJP.find_all('span', class_='text'):
            textCnt = 0
            for child in j.children:
                textChild.append(child.string)
                textCnt += 1
            for k in range(0,len(textChild)):
                for chr in _unicode_chr_splitter( textChild[k] ):
                    if chr != '\n' and chr != ' ' and chr != '':
                        textList.append(chr)
        
        for j in range(0,len(textList)):
            if furiList[j] == None:
                reading += textList[j] 
            else:
                reading += " " + textList[j] + "[" + furiList[j] + "]" 

    wrapper = hj_Soup.find('div', id='wrapper')
    mainBlock = wrapper.find('div', id='main')
    mainContainer = mainBlock.find('div', class_='mian_container main_container')
    wordBlock = mainContainer.find('div', id='headword_jp_1', class_='jp_word_comment')
    wordExt = wordBlock.find('div', class_='word_ext_con clearfix')
    
    #         // This apart is not complete yet
    
    # if needHJSound:
    #     mt10 = wordBlock.find('div', class_='mt10')
    #     jpSound = mt10.find('span', class_='jpSound')
    #     if jpSound != None:
    #         hjSound = jpSound.find('script').get_text()
    #         hjSound = hjSound.replace('GetTTSVoice("','')
    #         hjSound = hjSound.replace('")','')
    #         wget.download(hjSound, out=download_dir+"Jp_"+word+".mp3")
    #         front_word += "[sound:Jp_"+word+".mp3]"

    #         // This apart is not complete yet
    

    for i in range(0,len(textList)):
        front_word += textList[i]
    
    front_word += "<br>"

    partOfSpeech = wordExt.find_all('div', class_='flag big_type tip_content_item')
    posMeaningBlock = wordExt.find_all('ul', class_='tip_content_item jp_definition_com')
    for i in range(0,len(posMeaningBlock)):
        if len(partOfSpeech) != 0:
            front_word += '(' + HanziConv.toTraditional(partOfSpeech[i]['title']) + ')' + '<br>'
            back_word  += '(' + HanziConv.toTraditional(partOfSpeech[i]['title']) + ')' + '<br>'
        posMeaning = posMeaningBlock[i].find_all('li', class_='flag')
        meaningCnt = 1
        for j in range(0,len(posMeaning)):
            meaning = posMeaning[j].find('span', class_='word_comment soundmark_color')
            if meaning == None:
                meaning = posMeaning[j].find('span', class_='jp_explain soundmark_color')
            back_word += str(meaningCnt) + '. ' + meaning.get_text() + '<br>'
            meaningCnt += 1

    result['read_word'] = reading
    result['front_word'] = front_word
    result['back_word'] = HanziConv.toTraditional(back_word)

    return result
