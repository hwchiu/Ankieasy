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
    url="https://tw.dictionary.search.yahoo.com/search?p={}".format(wordUrl)
    content = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(content, 'lxml')
    result = {}
    front_word = ""
    back_word = ""
    download_dir = ""

    if "download_dir" in data:
        download_dir = data['download_dir']

    if word == "":
        return None

    wrongSpelling = soup.find('div', class_='compText mb-15 fz-m fc-4th')
    if wrongSpelling is not None:
        return None


    # If there is a typo, maybe the Yahoo dict will detect
    checkTypo = soup.find("span", id="term").get_text()
    if checkTypo != word:
        word = checkTypo

    print(" ")
    print('<<'+word+'>>')
    print(" ")
# Get the URL of the sound media
    soup_result = soup.find('span', id='iconStyle')
    if soup_result is not None and download_dir != "":
        sound = json.loads(soup_result.get_text())
        if sound is not None and sound['sound_url_1'] is not None:
            # Download the sound media and store at the specific directory (%username%/collection.media) and with a specific file name (Py_%word%.mp3)
            for soundCnt in range(0,len(sound['sound_url_1'])):
                if bool(sound['sound_url_1'][soundCnt]) == True :
                    wget.download(sound['sound_url_1'][soundCnt]["mp3"], out=download_dir+"Py_"+word+".mp3")
                    front_word += "[sound:Py_"+word+".mp3]"
                    break
    # Insert the sound media into the card
    front_word += word + "<br>"

    explain = soup.find('div', class_='explain')
    partOfSpeech = explain.find_all('div', class_='compTitle')

    # POScont => the content of part of speech
    POScont = explain.find_all('ul', class_='compArticleList')

    for i in range(0,len(POScont)):
        cnt = 1
        if len(partOfSpeech) == 0:
            POSclean = ""
        else:
            POSclean = '(' + partOfSpeech[i].get_text().split('.')[0] + '.)' + "<br>"
        front_word += POSclean
        for j in POScont[i].find_all('span', id='example', class_='example'):
            front_word += str(cnt) + '. '
            for k in range(0,len(j.contents)-1):
                front_word += j.contents[k].string
            front_word += "<br>"
            cnt = cnt + 1
        back_word += POSclean
        for j in POScont[i].find_all('h4'):
            back_word += j.get_text() + '<br>'
    result['front_word'] = front_word
    result['back_word'] = back_word

    return result
