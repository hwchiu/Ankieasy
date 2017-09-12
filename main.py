#!/usr/bin/env python
import sys
import json
import importlib

def handleProfile(data):
    print(data)
    print('words file:{}'.format(data['file']))
    print('deck file:{}'.format(data['deck']))
    print('collection file:{}'.format(data['collection']))
    print('media file :{}'.format(data['download_dir']))
    print('method :{}'.format(data['method']))
    print('addons:{}'.format(data['add_on'] if 'add_on' in data else 'Basic'))

    dict_module = importlib.import_module('module.{}'.format(data['method'].lower()my_module))

    dict_module.LookUp("QQ")

def load_config(path):
    with open(path, encoding='utf-8') as data_file:
        return json.load(data_file)

if '__main__':
    if len(sys.argv) >= 2:
        config_path = sys.argv[1]
    else:
        config_path = 'config.json'
    data = load_config(config_path)
    for profile in data['profiles']:
        handleProfile(profile)
