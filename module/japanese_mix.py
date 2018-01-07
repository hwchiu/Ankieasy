import urllib.request
from urllib.parse import quote
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import subprocess
import platform
import datetime
import json
import re
from hanziconv import HanziConv # https://pypi.python.org/pypi/hanziconv/0.2.1
from re import compile as _Re

_unicode_chr_splitter = _Re( '(?s)((?:[\u2e80-\u9fff])|.)' ).split

def LookUp(word, data, download_dir):
    
    result = {}
    front_word = ''
    back_word = ''
    furi = ''
    furiChild = []
    furiList = []
    text = ''
    textChild = []
    textList = []
    reading = ''
    cnt = 0
    needHJSound = True

    opener=urllib.request.build_opener()
    opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
    urllib.request.install_opener(opener)

    # Eliminate the end of line delimiter
    word = word.splitlines()[0]
    wordUrl = urllib.parse.quote(word, safe='')

    jisho_Url = 'http://jisho.org/search/{}'.format(wordUrl)
    jisho_Content = urllib.request.urlopen(jisho_Url).read()
    jisho_Soup = BeautifulSoup(jisho_Content, 'lxml')

    hj_Url = 'https://dict.hjenglish.com/jp/jc/{}'.format(wordUrl)
    hj_Content = urllib.request.urlopen(hj_Url).read()
    hj_Soup = BeautifulSoup(hj_Content, 'lxml')

    if word == '':
        return None
        
    wrongSpelling = jisho_Soup.find('div', id='no-matches')
    if wrongSpelling is not None:
        return None
    
    print(' ')
    print('<<' + word + '>>')
    print(' ')

    exactBlock = jisho_Soup.find('div', class_='exact_block')
    if exactBlock == None:
        exactBlock = jisho_Soup.find('div', class_='concepts')
    firstBlock = exactBlock.find('div', class_='concept_light clearfix')
    partJP = firstBlock.find('div', class_='concept_light-wrapper')
    partEN = firstBlock.find('div', class_='concept_light-meanings')
    status = partJP.find('div', class_='concept_light-status')
    if status != None:
        audio = status.find('audio')
        if audio != None and bool(download_dir) != False:
            source = audio.find('source')
            if source != None and source['src'] != None:
                try:
                    # Download the sound media to the media folder
                    urllib.request.urlretrieve('http:'+source['src'], download_dir+'Jp_'+word+'.mp3')
                    # Insert the sound media into the card
                    front_word += '[sound:Jp_'+word+'.mp3]'
                    needHJSound = False
                except urllib.error.HTTPError as err:
                    print('Jisho_err=', err)

    furiBlock = partJP.find('span', class_='furigana')
    rubyBlock = furiBlock.find('ruby', class_='furigana-justify')
    if rubyBlock != None:
        furiList = rubyBlock.find('rt').get_text()
    else:
        furiCnt = 0
        for child in furiBlock.children:
            furiChild.append(child.string)
            furiCnt += 1
        furiList = list(filter(('\n').__ne__, furiChild))

    textBlock = partJP.find('span', class_='text')
    textCnt = 0
    for child in textBlock.children:
        textChild.append(child.string)
        textCnt += 1
    for i in range(0, len(textChild)):
        for chr in _unicode_chr_splitter( textChild[i] ):
            if chr != '\n' and chr != ' ' and chr != '':
                textList.append(chr)
    
    if len(furiList) != len(textList):
        reading = ''
    else:
        for i in range(0, len(textList)):
            if furiList[i] == None:
                reading += textList[i] 
            else:
                reading += ' ' + textList[i] + '[' + furiList[i] + ']' 

    for i in range(0, len(textList)):
        front_word += textList[i]
    front_word += '<br>'
    
    body = hj_Soup.find('body')
    if bool(body.attrs) == True:
        wrapper = body.find('div', id='wrapper')
        webboxContent = wrapper.find('div', id='webbox-content')
        mainBlock = webboxContent.find('div', id='main')
        mainContainer = mainBlock.find('div', class_='mian_container main_container')
        
        headwordJpCnt = 1
        headwordJpStr = 'headword_jp_' + str(headwordJpCnt)

        while mainContainer.find('div', id=headwordJpStr, class_='jp_word_comment') != None:
            wordBlock = mainContainer.find('div', id=headwordJpStr, class_='jp_word_comment')
            wordExt = wordBlock.find('div', class_='word_ext_con clearfix')
            
            if needHJSound:
                mt10 = wordBlock.find('div', class_='mt10')
                jpSound = mt10.find('span', class_='jpSound')
                if jpSound != None:
                    hjSound = jpSound.find('script').get_text()
                    if hjSound != None:
                        hjSound = hjSound.replace('GetTTSVoice("','')
                        hjSound = hjSound.replace('")','')
                        hjSound = hjSound.replace(';','')
                        print('hjSound=', hjSound)
                        if hjSound != '' and bool(download_dir) != False:
                            try:
                                urllib.request.urlretrieve(hjSound, download_dir+'Jp_'+word+str(headwordJpCnt)+'.mp3')
                                front_word = '[sound:Jp_'+word+str(headwordJpCnt)+'.mp3]' + front_word
                            except urllib.error.HTTPError as err:
                                print('HJ_err=', err)

            partOfSpeech = wordExt.find_all('div', class_='flag big_type tip_content_item')
            posMeaningBlock = wordExt.find_all('ul', class_='tip_content_item jp_definition_com')
            for i in range(0, len(posMeaningBlock)):
                if len(partOfSpeech) >= i+1:
                    front_word += '(' + HanziConv.toTraditional(partOfSpeech[i]['title']) + ')' + '<br>'
                    back_word  += '(' + HanziConv.toTraditional(partOfSpeech[i]['title']) + ')' + '<br>'
                posMeaning = posMeaningBlock[i].find_all('li', class_='flag')
                meaningCnt = 1
                for j in range(0, len(posMeaning)):
                    meaning = posMeaning[j].find('span', class_='word_comment soundmark_color')
                    if meaning == None:
                        meaning = posMeaning[j].find('span', class_='jp_explain soundmark_color')
                    meaningText = meaning.get_text()                    
                    meaningText = meaningText[0:meaningText.find('（')]  # Truncate the content after '（'
                    meaningText = meaningText.replace('。', '')          # Remove the '。'
                    if len(posMeaning) != 1:
                        back_word += str(meaningCnt) + '. '
                    back_word += meaningText + '<br>'
                    meaningCnt += 1

            headwordJpCnt += 1
            headwordJpStr = 'headword_jp_' + str(headwordJpCnt)
            
        result['read_word'] = reading
        result['front_word'] = front_word
        result['back_word'] = HanziConv.toTraditional(back_word)
        return result
    else:
        print('Get information failed!')
        return False
