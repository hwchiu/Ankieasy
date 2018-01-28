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
import math
from pyquery import PyQuery as pq
from hanziconv import HanziConv # https://pypi.python.org/pypi/hanziconv/0.2.1
from re import compile as _Re

_unicode_chr_splitter = _Re( '(?s)((?:[\u2e80-\u9fff])|.)' ).split

def getVerb(tr, typeArray, front_word, download_dir):
    result = {}
    back_word = ''
    
    for typeStr in typeArray:
        typeTd = tr.find('td', class_='katsuyo katsuyo_' + typeStr + '_js')
        accentedWord = typeTd.find('span', class_='accented_word')
        if accentedWord != None:
            soundDiv = typeTd.find('div', class_='katsuyo_proc_button clearfix')
            soundStr = soundDiv.find('a', class_='katsuyo_proc_female_button js_proc_female_button')['id']
            # 把數字後兩位數截掉 前面加兩個0 再取後三位
            soundStrNum = ('00' + str(math.floor(int(soundStr[0:soundStr.find('_')])/100)))[-3:]
            soundUrl = 'http://www.gavo.t.u-tokyo.ac.jp/ojad/sound4/mp3/female/'+soundStrNum+'/'+soundStr+'.mp3'
            try:
                urllib.request.urlretrieve(soundUrl, download_dir + soundStr + '.mp3')
                front_word += '[sound:'+soundStr+'.mp3]'
            except urllib.error.HTTPError as err:
                print('OJAD_err=', err)
            front_word += accentedWord.get_text() + '<br>'
    result['front_word'] = front_word
    return result

def getJishoMasu(tr, jisho_masu, front_word, download_dir):
    back_word = ''

    jisho_masuCnt = 0
    for typeStr in ['jisho', 'masu']:
        typeTd = tr.find('td', class_='katsuyo katsuyo_' + typeStr + '_js')
        soundDiv = typeTd.find('div', class_='katsuyo_proc_button clearfix')
        if soundDiv != None:
            soundStr = soundDiv.find('a', class_='katsuyo_proc_female_button js_proc_female_button')['id']
            # 把數字後兩位數截掉 前面加兩個0 再取後三位
            soundStrNum = ('00' + str(math.floor(int(soundStr[0:soundStr.find('_')])/100)))[-3:]
            soundUrl = 'http://www.gavo.t.u-tokyo.ac.jp/ojad/sound4/mp3/female/'+soundStrNum+'/'+soundStr+'.mp3'
            try:
                urllib.request.urlretrieve(soundUrl, download_dir + soundStr + '.mp3')
                front_word += '[sound:'+soundStr+'.mp3]'
            except urllib.error.HTTPError as err:
                print('OJAD_err=', err)
            front_word += jisho_masu.split('・')[jisho_masuCnt] + '<br>'
            jisho_masuCnt += 1
    return front_word

def LookUp(word, data, download_dir):
    
    result = {}
    front_word = ''
    back_word = ''
    cnt = 0

    opener=urllib.request.build_opener()
    opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
    urllib.request.install_opener(opener)
    ssl._create_default_https_context = ssl._create_unverified_context

    # Eliminate the end of line delimiter
    word = word.splitlines()[0]
    wordUrl = urllib.parse.quote(word, safe='')

    ojad_Url = 'http://www.gavo.t.u-tokyo.ac.jp/ojad/search/index/word:{}'.format(wordUrl)
    ojad_Content = urllib.request.urlopen(ojad_Url).read()
    ojad_Soup = BeautifulSoup(ojad_Content, 'lxml')

    hj_Url = 'https://dict.hjenglish.com/jp/jc/{}'.format(wordUrl)
    hj_Content = urllib.request.urlopen(hj_Url).read()
    hj_Soup = BeautifulSoup(hj_Content, 'lxml')

    if word == '':
        return None
    
    print(' ')
    print('<<' + word + '>>')
    print(' ')

    searchResult = ojad_Soup.find('div', id='search_result')
    table = searchResult.find('table', id='word_table', class_='draggable')

    tbody = table.find('tbody')
    tbodyTr = tbody.find('tr') # The default value of tbodyTr is the first row (first <tr>)  
    for tbodyTrIter in tbody.find_all('tr'):
        midashi = tbodyTrIter.find('td', class_='midashi')
        if midashi == None:
            continue
        midashiWrapper = midashi.find('div', class_='midashi_wrapper')
        jisho_masu = midashiWrapper.get_text()
        jisho_masu = jisho_masu.split(chr(10))[1]
        if word == jisho_masu.split('・')[0] or word == jisho_masu.split('・')[1]:
            tbodyTr = tbodyTrIter
            break
    # front_word = getVerb(tbodyTr, ['jisho', 'masu', 'te', 'ta', 'nai', 'nakatta', 'ba', 'shieki', 'ukemi', 'meirei', 'kano', 'ishi'], front_word, download_dir)
    # front_word = getVerb(tbodyTr, ['jisho', 'masu'], front_word, download_dir)
    front_word = getJishoMasu(tbodyTr, jisho_masu, front_word, download_dir)

    thead = table.find('thead')
    theadTr = thead.find('tr')
    midashi = theadTr.find('th', class_='midashi')
    front_word += '[' + midashi.get_text() + ']<br>' # Get the type of the verb

    body = hj_Soup.find('body', attrs={'onload': 'onInit();', 'onmousedown': 'MouseDownOnBody(event);'})
    if body != None:
        wrapper = body.find('div', id='wrapper')
        webboxContent = wrapper.find('div', id='webbox-content')
        mainBlock = webboxContent.find('div', id='main')
        mainContainer = mainBlock.find('div', class_='mian_container main_container')
        
        headwordJpCnt = 1
        headwordJpStr = 'headword_jp_' + str(headwordJpCnt)

        while mainContainer.find('div', id=headwordJpStr, class_='jp_word_comment') != None:
            wordBlock = mainContainer.find('div', id=headwordJpStr, class_='jp_word_comment')
            wordExt = wordBlock.find('div', class_='word_ext_con clearfix')
            partOfSpeech = wordExt.find_all('div', class_='flag big_type tip_content_item')
            posMeaningBlock = wordExt.find_all('ul', class_='tip_content_item jp_definition_com')
            for i in range(0, len(posMeaningBlock)):
                if len(partOfSpeech) >= i+1:
                    back_word  += '(' + HanziConv.toTraditional(partOfSpeech[i]['title']) + ')' + '<br>'
                posMeaning = posMeaningBlock[i].find_all('li', class_='flag')
                meaningCnt = 1
                for j in range(0, len(posMeaning)):
                    meaning = posMeaning[j].find('span', class_='word_comment soundmark_color')
                    if meaning == None:
                        meaning = posMeaning[j].find('span', class_='jp_explain soundmark_color')
                    meaningText = meaning.get_text()
                    if meaningText.find('（') != -1:
                        meaningText = meaningText[0:meaningText.find('（')]  # Truncate the content after '（'
                    meaningText = meaningText.replace('。', '')              # Remove the '。'
                    if len(posMeaning) != 1:  
                        back_word += str(meaningCnt) + '. ' # When there is only one meaning, remove the '1.'
                    back_word += meaningText + '<br>'

                    exSentStr = ''
                    exSentCnt = 0
                    exSentNum = 1 # How many example sentences you want in the card
                    exSentence = posMeaning[j].contents[0]
                    if len(posMeaning[j].contents) >= 2:
                        exSentence = posMeaning[j].contents[1] # The second <div> in <li> in <ul class='tip_content_item jp_definition_com'>
                    for child in exSentence.children:
                        try:
                            exSentStr += child.text
                            if child.name == 'br': # Only take the first example sentence
                                front_word += str(meaningCnt) + '. ' + exSentStr.split('/')[0] + '<br>'
                                back_word += exSentStr.split('/')[1] + '<br>'
                                exSentStr = ''
                                exSentCnt += 1
                                if exSentCnt == exSentNum:
                                    break
                        except:
                            exSentStr += child
                            
                    meaningCnt += 1
            headwordJpCnt += 1
            headwordJpStr = 'headword_jp_' + str(headwordJpCnt)
        result['front_word'] = front_word
        result['back_word'] = HanziConv.toTraditional(back_word)
        result['read_word'] = ''
        print(result)
        return result
    else:
        print('Get information failed!')
        return False

