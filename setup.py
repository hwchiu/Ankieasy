from setuptools import setup

requirements = [
	'bs4',
	'lxml',
	'decorator',
	'pyaudio',
	'wget',
	'pypiwin32',
	'hanziconv',
	]

setup(
	name = "anki_auto_add",
	version = "1.0",
	author = "Hung-Wei Chiu/Yu-Hsien Yeh",
	author_email = "sppsorrg@gmail.com/ex8600@gmail.com",
	description = ("An tool of how to automatically lookup words and insert into Anki decks"),
	install_requires=requirements
)

