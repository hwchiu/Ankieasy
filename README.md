Introduction
============
AnkiEasy can help you to add a bstch of words into your Anki deck.
You only prepare the words you want to learn and modify the config file and AnkiEasy will lookup those words and make a anki card and insert into your Anki deck.


Usage
=====
1. Install anki application and python3
2. python3 setup.py install ("python setup.py install" for Windows user)
3. Modify the config.json (see below to know more infomation)
4. Close anki application (avoid database lock)
5. python3 main.py ("python main.py" for Windows user)
6. Open anki and check your deck.

Config
======
Config.json is a array of profiles and each profiles contain following fields.
- file : input file which contains words (one word one line)
- deck : Anki deck.
- collcetion: A system path indictes to your anki collection (it's different in different OS)
- download_dir: A system path point to your anki media files.
- dict_source: what language you want to use to lookup.
	- english_yahoo
	- japanese
- card_type: anki card type
	- basic
	- basic_reverse
	- japanse_recognition_recall
