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

def getJishoMasu(tr, typeArray, front_word, download_dir):
    result = {}
    back_word = ''
    midashi = tr.find('td', class_='midashi')
    midashiWrapper = midashi.find('div', class_='midashi_wrapper')
    jisho_masu = midashiWrapper.get_text()
    jisho_masu = jisho_masu.split(chr(10))[1]

    jisho_masuCnt = 0
    for typeStr in typeArray:
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
    result['front_word'] = front_word
    return result

def LookUp(word, data, download_dir):
    
    result = {}
    front_word = ''
    back_word = ''
    read_word = ''
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
    thead = table.find('thead')
    theadTr = thead.find('tr')
    midashi = theadTr.find('th', class_='midashi')
    front_word += '[' + midashi.get_text() + ']<br>' # Get the type of the verb

    tbody = table.find('tbody')
    tbodyTr = tbody.find('tr')
    # result = getVerb(tbodyTr, ['jisho', 'masu', 'te', 'ta', 'nai', 'nakatta', 'ba', 'shieki', 'ukemi', 'meirei', 'kano', 'ishi'], front_word, download_dir)
    # result = getVerb(tbodyTr, ['jisho', 'masu'], front_word, download_dir)
    result = getJishoMasu(tbodyTr, ['jisho', 'masu'], front_word, download_dir)
    result['back_word'] = back_word
    result['read_word'] = read_word
    print(result)
    return result

