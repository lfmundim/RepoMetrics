import time
from collections import OrderedDict
from operator import itemgetter


class Authorship:
    def __init__(self, files):
        self.filesAuthorList = self.GetFileAuthorsList(files)
        self.truckFactor = self.GetTruckFactor()

    def GetAbandonedPercentage(self, filePoints, minimumFileCover=0.5):
        total = 0
        abandoned = 0
        for file in filePoints:
            total += 1
            if(((filePoints[file]['covered'] * 100)/(filePoints[file]['covered'] + filePoints[file]['uncovered'])) < minimumFileCover):
                abandoned += 1
        return (abandoned*100)/total

    def GetTruckFactor(self, minThreshold=0.0, minimumAbandonedPercentageFiles=0.5, minimumFileCover=0.5):
        truckFactors = []
        filePointsByAuthor = {}
        filePoints = {}
        self.fullAuthorList = {}
        for file in self.filesAuthorList:
            filePointsByAuthor[file] = {}
            filePoints[file] = {}
            filePoints[file]['covered'] = 0
            filePoints[file]['uncovered'] = 0
            for author in self.filesAuthorList[file]:
                if author not in filePointsByAuthor[file] and (self.filesAuthorList[file])[author] > minThreshold:
                    (filePointsByAuthor[file])[author] = (self.filesAuthorList[file])[author]
                    filePoints[file]['covered'] += (self.filesAuthorList[file])[author]
                elif (self.filesAuthorList[file])[author] > minThreshold:
                    (filePointsByAuthor[file])[author] += (self.filesAuthorList[file])[author]
                    filePoints[file]['covered'] += (self.filesAuthorList[file])[author]
                if author not in self.fullAuthorList:
                    self.fullAuthorList[author] = 1
                else:
                    self.fullAuthorList[author] += 1
        orderedFullAuthorList = OrderedDict(sorted(self.fullAuthorList.items(), key = itemgetter(1), reverse = True))
        for author in orderedFullAuthorList:
            truckFactors.append(author)
            for file in filePointsByAuthor:
                for someAuthor in filePointsByAuthor[file]:
                    if(someAuthor == author):
                        filePoints[file]['covered'] -= (filePointsByAuthor[file])[someAuthor]
                        filePoints[file]['uncovered'] += (filePointsByAuthor[file])[someAuthor]
            if(self.GetAbandonedPercentage(filePoints, minimumFileCover) < (100*minimumAbandonedPercentageFiles)):
                return truckFactors
        return truckFactors

    def GetFileAuthorsList(self, files, minThreshold=0.0):
        fileAuthorsList = {}
        for file in files:
            fileAuthors = {}
            mods = 0
            for author in files[file]:
                mods += 1
                if author not in fileAuthors:
                    fileAuthors[author] = 1
                else:
                    fileAuthors[author] += 1
            creator = list(fileAuthors.keys())[0]
            for fileAuthor in fileAuthors:
                if fileAuthor == creator:
                    fileAuthors[fileAuthor] = 1 + 0.5*fileAuthors[fileAuthor] - 0.1*(mods-fileAuthors[fileAuthor])
                else:
                    fileAuthors[fileAuthor] = 0.5*fileAuthors[fileAuthor] - 0.1*(mods-fileAuthors[fileAuthor])
            for fileAuthor in fileAuthors:
                ordered = OrderedDict(sorted(fileAuthors.items(), key = itemgetter(1), reverse = True))
                owner = list(ordered.keys())[0]
                fileAuthors[fileAuthor] = fileAuthors[fileAuthor]/fileAuthors[owner]
            ordered = OrderedDict(sorted(fileAuthors.items(), key = itemgetter(1), reverse = True))
            fileAuthorsList[file] = fileAuthors
        return fileAuthorsList
