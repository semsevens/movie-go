#-*- coding: utf-8 -*-

import urllib
import urllib.request

def getPageCode(url, headers = { 'Connection': 'Keep-Alive', 'Accept': 'text/html, application/xhtml+xml, */*', 'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko' }):
    request = urllib.request.Request(url, headers = headers)
    #  print('waiting for response: ' + url)
    response = urllib.request.urlopen(request)
    pageCode = response.read().decode('utf-8')
    #  print('response successfully')
    return pageCode
