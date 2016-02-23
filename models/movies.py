#-*- coding: utf-8 -*-

import urllib
import re
from models.nuomi import Nuomi
from models.taobao import Taobao
from models.meituan import Meituan
from functions.file import pickling, unpickling, saveFile
from functions.sort import multipleKeySort
from multiprocessing import Pool, freeze_support

class Movies:

    # user interface

    def getMovies(self):
        return self.movies

    def getLabels(self):
        return self.labels

    def getCinemasName(self):
        return self.main.getCinemasName()

    def getPinyinCn(self):
        return self.pinyinCn

    # initialize

    def __init__(self):
        self.main = Nuomi()
        self.taobao = Taobao()
        self.meituan = Meituan()
        self.platformNames = ['nuomi', 'taobao', 'meituan']
        self.pinyinCn = {'nuomi': u'糯米', 'taobao': u'淘宝', 'meituan': u'美团'}
        self.picklingFile = 'data/pickling.txt'
        self.movies = {}
        self.morningEnd = "13:00"
        self.afternoonEnd = "18:00"
        self.nightEnd = "24:00"
        self.labels = {'a': u'早场', 'b': u'中场', 'c': u'晚场'}


    # main methods

    def data(self):
        return self.movies

    def getData(self):
        self.movies = unpickling(self.picklingFile)
        return self.movies

    def update(self):
        self.movies = {}
        pool = Pool(3)
        pool.apply_async(self.main.update, args=('nuomi',))
        pool.apply_async(self.taobao.update, args=('taobao',))
        pool.apply_async(self.meituan.update, args=('meituan',))
        pool.close()
        pool.join()
        self.movies = self.main.getData()
        self.mergeData(self.taobao)
        self.mergeData(self.meituan)
        self.translate()
        self.save()
        return self.movies

    def translate(self):
        translatedData = []
        for movieId, theMovie in self.movies.items():
            movie = {}
            movie['id'] = movieId
            movie['info'] = theMovie['info']
            rows = []
            for cinemaId, theDates in theMovie['cinemas'].items():
                for theDate, theRows in theDates.items():
                    for theRow in theRows.values():
                        row = {'cinema-id': cinemaId, 'date': theDate}
                        row.update(theRow)
                        row['label'] = self.getLabel(row['start'])
                        platforms = []
                        for platformName in self.platformNames:
                            platform = {}
                            if (platformName + '-price') in row:
                                platform['name'] = platformName
                                platform['price'] = row[platformName + '-price']
                                platform['link'] = row[platformName + '-link']
                                platforms.append(platform)
                        multipleKeySort(platforms, ['price'])
                        row['platforms'] = platforms
                        rows.append(row)
            multipleKeySort(rows, ['date','label', 'cinema-id', 'start'])
            rows = self.rowsToGroup(rows, ['date', 'label', 'cinema-id'])
            movie['data'] = rows
            translatedData.append(movie)
        self.movies = translatedData
        self.addLowest()

    def addLowest(self):
        for movieGroup in self.movies:
            for dateGroup in movieGroup['data']:
                for labelGroup in dateGroup['data']:
                    for cinemaGroup in labelGroup['data']:
                        cinemaGroup['data'].sort(key=lambda x:x['platforms'][0]['price'])
                        cinemaGroup['lowest-price'] = cinemaGroup['data'][0]['platforms'][0]['price']
        for movieGroup in self.movies:
            for dateGroup in movieGroup['data']:
                for labelGroup in dateGroup['data']:
                    labelGroup['data'].sort(key=lambda x:x['lowest-price'])

    # internal methods for translate

    def getLabel(self, time):    # can create a the best judging tree
        if time < self.morningEnd:
            return 'a'
        elif time < self.afternoonEnd:
            return 'b'
        else:
            return 'c'

    def rowsToGroup(self, rows, keys):
        groups = []
        firstKey = keys[0]
        nowValue = rows[0][firstKey]
        group = {}
        group[firstKey] = nowValue
        group['data'] = []
        for row in rows:
            if row[firstKey] == nowValue:
                del row[firstKey]
                group['data'].append(row)
            else:
                groups.append(group)
                nowValue = row[firstKey]
                group = {}
                group[firstKey] = nowValue
                group['data'] = []
                del row[firstKey]
                group['data'].append(row)
        groups.append(group)
        rows = groups
        if len(keys) > 1:
            for group in groups:
                group['data'] = self.rowsToGroup(group['data'], keys[1:])
        return rows

    # internal methods for update

    def save(self):
        pickling(self.picklingFile, self.movies)

    def mergeData(self, obj):
        missMovieCount = 0
        missCinemaCount = 0
        data = obj.getData()
        for movieId, theMovie in data.items():
            movieTitle = obj.mapMovieTitle(movieId)
            targetMovieId = self.main.remapMovieTitle(movieTitle)
            if targetMovieId == -1:
                missMovieCount += 1
                print('targetMovieId Error')
            for cinemaId, theCinema in theMovie['cinemas'].items():
                cinemaName = obj.mapCinemaName(cinemaId)
                targetCinemaId = self.main.remapCinemaName(cinemaName)
                if targetCinemaId not in self.movies[targetMovieId]['cinemas']:
                    for d in self.movies[targetMovieId]['cinemas'].keys():
                        print(d)
                    print('target cinema id : ' + targetCinemaId)
                    self.movies[targetMovieId]['cinemas'][targetCinemaId] = {}
                for date, theRows in theCinema.items():
                    if date not in self.movies[targetMovieId]['cinemas'][targetCinemaId]:
                        for d in self.movies[targetMovieId]['cinemas'][targetCinemaId].keys():
                            print(d)
                        print('target date : ' + date)
                        self.movies[targetMovieId]['cinemas'][targetCinemaId][date] = {}
                    for startKey, theRow in theRows.items():
                        if startKey not in self.movies[targetMovieId]['cinemas'][targetCinemaId][date].keys():
                            for sk in self.movies[targetMovieId]['cinemas'][targetCinemaId][date]:
                                print(sk)
                            print('target: ' + startKey)
                            self.movies[targetMovieId]['cinemas'][targetCinemaId][date][startKey] = {}
                        self.movies[targetMovieId]['cinemas'][targetCinemaId][date][startKey].update(theRow)
        print('missMoive: ' + str(missMovieCount))
        print('missCinema: ' + str(missCinemaCount))
