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
from pyquery import PyQuery as pq
from hanziconv import HanziConv # https://pypi.python.org/pypi/hanziconv/0.2.1
from re import compile as _Re

_unicode_chr_splitter = _Re( '(?s)((?:[\u2e80-\u9fff])|.)' ).split

def getVerb(tr, typeArray):
    result = {}
    front_word = ''
    back_word = ''
    for typeStr in typeArray:
        typeTd = tr.find('td', class_='katsuyo katsuyo_' + typeStr + '_js')
        accentedWord = typeTd.find('span', class_='accented_word')
        if accentedWord != None:
            front_word += accentedWord.get_text() + '<br>'
        katsuyo_proc_button clearfix
        soundDiv = typeTd.find('div', class_='katsuyo_proc_button clearfix')
        soundDiv
    return result
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
    tr = tbody.find('tr')
    tr.find('tr', class_='katsuyo katsuyo_jisho_js')
    tr.find('tr', class_='katsuyo katsuyo_masu_js')
    tr.find('tr', class_='katsuyo katsuyo_te_js')
    tr.find('tr', class_='katsuyo katsuyo_ta_js')
    tr.find('tr', class_='katsuyo katsuyo_nai_js')
    tr.find('tr', class_='katsuyo katsuyo_nakatta_js')
    tr.find('tr', class_='katsuyo katsuyo_ba_js')
    tr.find('tr', class_='katsuyo katsuyo_shieki_js')
    tr.find('tr', class_='katsuyo katsuyo_ukemi_js')
    tr.find('tr', class_='katsuyo katsuyo_meirei_js')
    tr.find('tr', class_='katsuyo katsuyo_kano_js')
    tr.find('tr', class_='katsuyo katsuyo_ishi_js')

    getVerb(tr, ['jisho', 'masu', 'te', 'ta', 'nai', 'nakatta', 'ba', 'shieki', 'ukemi', 'meirei', 'kano', 'ishi'])

    
    

    return None

