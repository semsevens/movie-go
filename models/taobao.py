#-*- coding: utf-8 -*-

import re
import urllib
from functions.http import getPageCode
from functions.file import pickling, unpickling
from functions.match import fuzzyMatch

class Taobao:

    # user interface

    def mapMovieTitle(self, movieId):
        return self.moviesIdToTitle[movieId]

    def remapMovieTitle(self, movieTitle):
        for targetMovieTitle in self.moviesTitleToId.keys():
            if fuzzyMatch(targetMovieTitle, movieTitle) > self.movieTitleAccuracy:
                return self.moviesTitleToId[targetMovieTitle]

    def mapCinemaName(self, cinemaId):
        return self.cinemasIdToName[cinemaId]

    def remapCinemaName(self, cinemaName):
        for targetCinemaName in self.cinemasNameToId.keys():
            if fuzzyMatch(targetCinemaName, cinemaName) > self.cinemaNameAccuracy:
                return self.cinemasNameToId[targetCinemaName]
        print(cinemaName)
        return -1

    # initialize

    def __init__(self):
        self.moviesFile = 'data/taobao-movies.txt'
        self.moviesIdToTitleFile = 'data/taobao-m-id-title.txt'
        self.movieTitleAccuracy = 50
        self.cinemaNameAccuracy = 70
        self.movies = {}
        self.cinemas = ['15516','4379', '5386']
        self.moviesIdToTitle = {}
        self.moviesTitleToId = {}
        self.cinemasNameToId = {}
        self.cinemasIdToName = {'15516': u'首都电影院昌平店','4379': u'北京昌平保利影剧院','5386': u'北京大地影院菓岭假日广场店'}
        for cinemaId, cinemaName in self.cinemasIdToName.items():
            self.cinemasNameToId[cinemaName] = cinemaId

    def data(self):
        return self.movies

    def getData(self):
        self.movies = unpickling(self.moviesFile)
        self.moviesIdToTitle = unpickling(self.moviesIdToTitleFile)
        for movieId, movieTitle in self.moviesIdToTitle.items():
            self.moviesTitleToId[movieTitle] = movieId
        return self.movies

    def update(self, name):
        print('updating %s ...' % name)
        self.movies = {}
        try:
            for cinemaId in self.cinemas:
                # url = 'https://dianying.taobao.com/cinemaDetail.htm?cinemaId='+cinemaId
                # pageCode = getPageCode(url)
                # pattern = re.compile('<li>联系电话：(.*?)</li>', re.S)
                # items = re.findall(pattern, pageCode)
                # for item in items:
                #     cinemaTel = item.strip()
                cinemaUrl = self.getCinemaUrl(cinemaId)
                c_pageCode = getPageCode(cinemaUrl)
                pattern = re.compile('showId=(.*?)&', re.S)
                items = re.findall(pattern, c_pageCode)
                items = set(items)
                for item in items:
                    movieId = item
                    movieUrl = 'http://dianying.taobao.com/cinemaDetailSchedule.htm?cinemaId='+ cinemaId +'&showId='+ movieId           
                    m_pageCode = getPageCode(movieUrl)
                    if movieId not in self.movies:
                        self.movies[movieId] = {}
                        self.movies[movieId]['info'] = {}
                        self.movies[movieId]['cinemas'] = {}
                        self.getMovieInfo(m_pageCode, self.movies[movieId]['info'])
                        self.moviesIdToTitle[movieId] = self.movies[movieId]['info']['title']
                        self.moviesTitleToId[self.movies[movieId]['info']['title']] = movieId
                    pattern = re.compile('showId='+movieId+'&showDate=(.*?)&', re.S)
                    dates = re.findall(pattern, m_pageCode)
                    dates = set(dates)
                    self.movies[movieId]['cinemas'][cinemaId] = {}
                    for date in dates:
                        url = 'http://dianying.taobao.com/cinemaDetailSchedule.htm?cinemaId='+ cinemaId +'&showId='+ movieId +'&showDate='+date
                        date = date[5:]
                        d_pagecode = getPageCode(url)
                        self.movies[movieId]['cinemas'][cinemaId][date] = {}
                        self.getMovieStatus(d_pagecode, self.movies[movieId]['cinemas'][cinemaId][date])
        except urllib.error.URLError as e:
            if hasattr(e, 'code'):
                print(e.code)
            if hasattr(e, 'reason'):
                print(e.reason)
        self.save()
        print('%s is updated done!' % name)
        return self.movies

    # internal methods for update

    def save(self):
        pickling(self.moviesFile, self.movies)
        pickling(self.moviesIdToTitleFile, self.moviesIdToTitle)

    def getCinemaUrl(self, cinemaId):
        cinemaUrl = 'https://dianying.taobao.com/cinemaDetailSchedule.htm?cinemaId='+ cinemaId
        return cinemaUrl

    def getMovieInfo(self, pageCode, movieInfo):
        pattern = re.compile('src="(.*?)">.*?href=\'#\'>(.*?)<small.*?\'score\'>(.*?)</small>.*看点：(.*?)</li>.*?导演：(.*?)</li>.*?主演：(.*?)</li>.*?类型：(.*?)</li>.*?制片国家/地区：(.*?)</li>.*?语言：(.*?)</li>.*?/ul>', re.S)
        items = re.findall(pattern, pageCode)
        for item in items:
            movieInfo['img'] = item[0].strip()
            movieInfo['title'] = item[1].strip()
            movieInfo['score'] = item[2].strip()
            movieInfo['light'] = item[3].strip()
            movieInfo['director'] = item[4].strip()
            movieInfo['staring'] = item[5].strip()
            movieInfo['type'] = item[6].strip()
            movieInfo['country'] = item[7].strip()
            movieInfo['lang'] = item[8].strip()
        return movieInfo

    def getMovieStatus(self, pageCode, movieStatus):
        pattern= re.compile('class="hall-time".*?bold">(.*?)</em>(.*?)</td>.*?"hall-type">(.*?)</td>.*?"hall-name">(.*?)</td>.*?<label>(.*?)</label>.*?"now">(.*?)</em>.*?"old">(.*?)</del>.*?href="(.*?)">', re.S)
        items = re.findall(pattern, pageCode)
        for item in items:
            start = item[0].strip()
            record = movieStatus[start[0:2] + start[3:5]] = {}
            record['start'] = item[0].strip()
            record['end'] = item[1].strip()
            record['version'] = item[2].strip()
            record['room'] = item[3].strip()
            record['seats'] = item[4].strip()
            record['taobao-price'] = item[5].strip()[0:2]
            # record['now-price'] = item[6].strip()
            record['taobao-link'] = item[7].strip()
        return movieStatus
