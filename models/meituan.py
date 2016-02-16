#-*- coding: utf-8 -*-

import re
import urllib
from functions.http import getPageCode
from functions.file import pickling, unpickling
from functions.match import fuzzyMatch

class Meituan:

    # user interface

    def data(self):
        return self.movies

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

    # initialize


    def __init__(self, latest = False):
        self.moviesFile = 'data/meituan-movies.txt'
        self.moviesIdToTitleFile = 'data/meituan-m-id-title.txt'
        self.movieTitleAccuracy = 50
        self.cinemaNameAccuracy = 50
        self.movies = {}
        self.cinemas = ['8186','66','50']
        self.moviesIdToTitle = {}
        self.moviesTitleToId = {}
        self.cinemasNameToId = {}
        self.cinemasIdToName = {'8186': u'首都电影院(悦荟万科广场店)' ,'66': u'大地影院(昌平菓岭店)' ,'50': u'昌平保利影剧院(佳莲时代广场店)' }
        for cinemaId, cinemaName in self.cinemasIdToName.items():
            self.cinemasNameToId[cinemaName] = cinemaId
        self.getData(latest)
        self.save(latest)

    def getData(self, latest = False):
        if latest:
            self.getFlesh()
        else:
            self.getOld()
        return self.movies

    def save(self, latest):
        if latest:
            pickling(self.moviesFile, self.movies)
            pickling(self.moviesIdToTitleFile, self.moviesIdToTitle)

    # internal methods for getData

    def getOld(self):
        self.movies = unpickling(self.moviesFile)
        self.moviesIdToTitle = unpickling(self.moviesIdToTitleFile)
        for movieId, movieTitle in self.moviesIdToTitle.items():
            self.moviesTitleToId[movieTitle] = movieId

    def getFlesh(self):
        try:
            for cinemaId in self.cinemas:
                # t = self.cinemasMap[cinemaId];
                # url = 'http://bj.meituan.com/shop/'+ t
                # pagecode = getPageCode(url)
                # pattern = re.compile("class='field-title'>电话：.*?>(.*?)</div>", re.S)
                # items = re.findall(pattern, pagecode)
                # for item in items:
                #     cinemaTel = item.strip()
                cinemaUrl = self.getCinemaUrl(cinemaId)
                pagecode = getPageCode(cinemaUrl)
                pattern = re.compile('"cat":(.*?)"id":(.*?),.*?"nm":"(.*?)"', re.S)
                items = re.findall(pattern, pagecode)
                for item in items:
                    movieinfo = item[0].strip();
                    movieId = item[1].strip();
                    if movieId not in self.movies: 
                        self.movies[movieId] = {}
                        self.movies[movieId]['cinemas'] = {}
                    self.movies[movieId]['info'] = {}
                    self.movies[movieId]['info']['title'] = item[2].strip()
                    self.moviesIdToTitle[movieId] = self.movies[movieId]['info']['title']
                    self.moviesTitleToId[self.movies[movieId]['info']['title']] = movieId
                    self.movies[movieId]['cinemas'][cinemaId] = {}
                    self.getMovieStatus(movieinfo, self.movies[movieId]['cinemas'][cinemaId])
        except urllib.error.URLError as e:
            if hasattr(e, 'code'):
                print(e.code)
            if hasattr(e, 'reason'):
                print(e.reason)
        
        # for movieId, theMovie in self.movies.items():
        #     for cinemaId, theCinema in theMovie['cinemas'].items():
        #         for Date, theRows in theCinema.items():
        #             for theRow in theRows.values():
        #                 print(theRow)


    def getCinemaUrl(self, cinemaId):
        cinemaUrl = 'http://platform.mobile.meituan.com/open/maoyan/v1/cinema/'+cinemaId+'/movies/shows.json?'
        return cinemaUrl

    def getMovieStatus(self, pagecode, movieStatus):
        dates = {}
        pattern = re.compile('"showDate":"(.*?)"', re.S)
        dates = re.findall(pattern, pagecode)
        for date in dates:
            pattern = re.compile('"dt":"'+date+'","tm":"(.*?)",.*?"seatUrl":"(.*?)","sell":(.*?),"sellPr":"(.*?)",', re.S)
            date = date[5:]
            movieStatus[date] = {}
            infos = re.findall(pattern, pagecode)
            for info in infos:
                status = info[2].strip()
                if(status):   
                    start = info[0].strip()
                    record = movieStatus[date][start[0:2] + start[3:5]] = {}
                    record['start'] = info[0].strip()
                    record['meituan-link'] = info[1].strip()
                    record['meituan-price'] = info[3].strip()[0:2]
        print(movieStatus)
        return movieStatus
