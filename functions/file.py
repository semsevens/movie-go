#-*- coding: utf-8 -*-

import json

def saveFile(filename, data):
    f_obj = open(filename, 'w', encoding = 'utf-8')
    f_obj.write(data)
    f_obj.close()
    
def pickling(filename, data):
    f = open(filename, 'w', encoding = 'utf-8')
    json.dump(data, f)
    f.close()

def unpickling(filename):
    f = open(filename, 'r', encoding = 'utf-8')
    data = json.load(f)
    f.close()
    return data
