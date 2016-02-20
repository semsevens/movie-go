#-*- coding: utf-8 -*-

import urllib
import re
from functions.http import getPageCode
from functions.file import pickling, unpickling
from functions.match import fuzzyMatch

class Nuomi:

    # user interface

    def mapMovieTitle(self, movieId):
        return self.moviesIdToTitle[movieId]

    def remapMovieTitle(self, movieTitle):
        for targetMovieTitle in self.moviesTitleToId.keys():
            if fuzzyMatch(targetMovieTitle, movieTitle) > self.movieTitleAccuracy:
                return self.moviesTitleToId[targetMovieTitle]
        print(movieTitle)
        return -1

    def mapCinemaName(self, cinemaId):
        return self.cinemasIdToName[cinemaId]

    def remapCinemaName(self, cinemaName):
        for targetCinemaName in self.cinemasNameToId.keys():
            if fuzzyMatch(targetCinemaName, cinemaName) > self.cinemaNameAccuracy:
                return self.cinemasNameToId[targetCinemaName]
        return -1

    def getCinemasName(self):
        return self.cinemasIdToName

    # initialize

    def __init__(self):
        self.moviesFile = 'data/nuomi-movies.txt'
        self.moviesIdToTitleFile = 'data/nuomi-m-id-title.txt'
        self.movieTitleAccuracy = 50
        self.cinemaNameAccuracy = 70
        self.movies = {}
        self.cinemas = ['bba87388c76b25b9bca82266', '89fd4ea32ca31a5ee4e965a5', '610852113eacfcb8c51b7506']
        self.moviesIdToTitle = {}
        self.moviesTitleToId = {}
        self.cinemasNameToId = {}
        self.cinemasIdToName = {'bba87388c76b25b9bca82266': u'大地影院(北京昌平菓岭假日广场店)' ,'89fd4ea32ca31a5ee4e965a5': u'昌平保利影剧院' ,'610852113eacfcb8c51b7506': u'首都电影院(昌平店)' }
        for cinemaId, cinemaName in self.cinemasIdToName.items():
            self.cinemasNameToId[cinemaName] = cinemaId
        self.getData()

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
                cinemaUrl = self.getCinemaUrl(cinemaId)
                pageCode = getPageCode(cinemaUrl)
                # pattern = re.compile('<p class="cb-tel">.*?([\d].*?)</p>', re.S)
                # items = re.findall(pattern, pageCode)
                # cinemaTel = items[0].strip()
                pattern = re.compile('movieId="(.*?)".*?<img src="(.*?)"', re.S)
                items = re.findall(pattern, pageCode)
                for item in items:
                    movieId = item[0]
                    movieImg = item[1]
                    if movieId not in self.movies:
                        self.movies[movieId] = {}
                        self.movies[movieId]['info'] = {}
                        self.movies[movieId]['cinemas'] = {}
                        self.movies[movieId]['info']['img'] = movieImg
                    self.movies[movieId]['cinemas'][cinemaId] = {}
                    movieUrl = self.getMovieUrl(cinemaId, movieId)
                    pageCode = getPageCode(movieUrl)
                    if 'title' not in self.movies[movieId]['info']:
                        self.getMovieInfo(pageCode, self.movies[movieId]['info'])
                        self.moviesIdToTitle[movieId] = self.movies[movieId]['info']['title']
                        self.moviesTitleToId[self.movies[movieId]['info']['title']] = movieId
                    self.getMovieCinema(pageCode, self.movies[movieId]['cinemas'][cinemaId])
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
        cinemaUrl = 'http://bj.nuomi.com/cinema/' + cinemaId
        return cinemaUrl

    def getMovieUrl(self, cinemaId, movieId):
        movieUrl = 'http://bj.nuomi.com/pcindex/main/timetable?cinemaid=' + cinemaId + '&mid=' + movieId + '&needMovieInfo=1&tploption=1&_=1450784678479'
        return movieUrl

    def getMovieInfo(self, pageCode, movieInfo):
        pattern = re.compile('h2>.*?>(.*?)</a>.*?/span>(.*?)</p>.*?/span>(.*?)</p>.*?/span>(.*?)</p>.*?/span>(.*?)</li>.*?/span>(.*?)</li>.*?/span>(.*?)</li>.*?/span>(.*?)</p>', re.S)
        items = re.findall(pattern, pageCode)
        for item in items:
            movieInfo['title'] = item[0].strip()
            movieInfo['director'] = item[1].strip()
            movieInfo['starring'] = item[2].strip()
            movieInfo['type'] = item[3].strip()
            movieInfo['country'] = item[4].strip()
            movieInfo['premiere'] = item[5].strip()
            movieInfo['length'] = item[6].strip()
            plot = item[7].replace('\r\n', '').strip()
            plot = plot.replace(u'>展开<', '')
            plot = plot.replace(u'>收起<', '')
            pattern = re.compile('<.*?>', re.S)
            plot = re.sub(pattern, '', plot)
            movieInfo['plot'] = plot
        return movieInfo

    def getMovieCinema(self, pageCode, movieCinema):
        dates = []
        pattern = re.compile('movie-date" mon="element=.*?([\d\.]*?)"', re.S)
        items = re.findall(pattern, pageCode)
        for item in items:
            temp = item.strip().split('.')
            date = temp[0] + '-' + temp[1]
            dates.append(date)
            movieCinema[date] = {}
        dateIndex = 0;
        maxTime = '-00:00'
        pattern = re.compile('td>(.*?)<.*?time">(.*?)<.*?<td>(.*?)</td>.*?td>(.*?)</td>.*?price">(.*?)</span>.*?del>(.*?)</del>.*?<a href="(.*?)".*?</td>', re.S)
        items = re.findall(pattern, pageCode)
        for item in items:
            startTime = item[0].strip()
            if startTime < maxTime:
                dateIndex = dateIndex + 1
            maxTime = startTime
            record = movieCinema[dates[dateIndex]][startTime[0:2] + startTime[3:5]] = {};
            record['start'] = startTime
            record['end'] = item[1].strip()
            record['version'] = item[2].strip()
            record['room'] = item[3].strip()
            record['nuomi-price'] = item[4].strip().replace('&yen;','')[0:2]
            record['nuomi-link'] = ('http://bj.nuomi.com' + item[6].strip()).replace('&amp;','&')
        return movieCinema
