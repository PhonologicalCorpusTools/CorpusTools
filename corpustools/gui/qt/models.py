import os
from collections import Counter

from .imports import *

class SpontaneousSpeechCorpusModel(QStandardItemModel):
    def __init__(self,corpus, parent = None):
        QStandardItemModel.__init__(self, parent)

        self.corpus = corpus
        self.setHorizontalHeaderItem (0,QStandardItem('Discourses'))

        corpusItem = QStandardItem(self.corpus.name)
        self.appendRow(corpusItem)
        speakerItem = QStandardItem('s01')
        corpusItem.appendRow(speakerItem)
        for d in self.corpus.discourses.values():
            speakerItem.appendRow(QStandardItem(str(d)))

    def createLexicon(self,row):
        d = self.item(row).text()
        return self.corpus.discourses[d].create_lexicon()

class DiscourseModel(QStandardItemModel):
    def __init__(self,discourse, parent = None):
        QStandardItemModel.__init__(self, parent)

        self.discourse = discourse
        self.posToTime = []
        self.timeToPos = {}
        for w in self.discourse:
            self.timeToPos[w.begin] = len(self.posToTime)
            self.posToTime.append(w.begin)
            i = QStandardItem(str(w))
            i.setFlags(i.flags() | (not Qt.ItemIsEditable))
            self.appendRow(i)

    def rowsToTimes(self,rows):
        return [self.posToTime[x] for x in rows]

    def timesToRows(self, times):
        return [self.timeToPos[x] for x in times]

    def hasAudio(self):
        return self.discourse.has_audio()

    def wordTokenObject(self,row):
        token = self.discourse[self.posToTime[row]]
        return token

class CorpusModel(QAbstractTableModel):
    def __init__(self, corpus, parent=None):
        super(CorpusModel, self).__init__(parent)

        self.corpus = corpus
        self.nonLexHidden = False

        self.columns = self.corpus.attributes

        self.rows = self.corpus.words

        self.allData = self.rows

    def rowCount(self,parent=None):
        return len(self.rows)

    def columnCount(self,parent=None):
        return len(self.columns)

    def sort(self, col, order):
        """sort table by given column number col"""
        self.layoutAboutToBeChanged.emit()
        self.rows = sorted(self.rows,
                key=lambda x: getattr(self.corpus[x],self.columns[col]))
        if order == Qt.DescendingOrder:
            self.rows.reverse()
        self.layoutChanged.emit()

    def hideNonLexical(self, b):
        self.nonLexHidden = b
        self.layoutAboutToBeChanged.emit()
        self.rows = self.allData
        if b:
            self.rows = [x for x in self.rows if str(self.corpus[x].transcription) != '']
        self.layoutChanged.emit()

    def wordObject(self,row):
        return self.corpus[self.rows[row]]

    def data(self, index, role=None):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        row = index.row()
        col = index.column()
        data = getattr(self.corpus[self.rows[row]],self.columns[col])

        if isinstance(data,float):
            data = str(round(data,3))
        elif not isinstance(data,str):
            data = str(data)
        return data

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns[col]
        return None

    def addTier(self,tierName, segList):
        self.layoutAboutToBeChanged.emit()
        self.corpus.add_tier(tierName, segList)
        self.columns = self.corpus.attributes
        self.layoutChanged.emit()

    def removeTiers(self,tiers):
        self.layoutAboutToBeChanged.emit()
        for t in tiers:
            self.corpus.remove_tier(t)
        self.columns = self.corpus.attributes
        self.layoutChanged.emit()

class SegmentPairModel(QAbstractTableModel):
    def __init__(self,parent = None):
        QAbstractTableModel.__init__(self,parent)

        self.columns = ['Segment 1', 'Segment 2']
        self.pairs = list()

    def rowCount(self,parent=None):
        return len(self.pairs)

    def columnCount(self,parent=None):
        return len(self.columns)

    def data(self, index, role=None):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.pairs[index.row()][index.column()]

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns[col]
        return None

    def addRow(self,pair):
        self.layoutAboutToBeChanged.emit()
        self.pairs.append(pair)
        self.layoutChanged.emit()

    def removeRows(self,inds):
        inds = sorted(inds, reverse=True)
        self.layoutAboutToBeChanged.emit()
        for i in inds:
            del self.pairs[i]
        self.layoutChanged.emit()

class VariantModel(QAbstractTableModel):
    def __init__(self, wordtokens, parent=None):
        super(VariantModel, self).__init__(parent)

        self.rows = [(k,v) for k,v in Counter(str(x.transcription) for x in wordtokens).items()]

        self.columns = ['Variant', 'Count']

        self.allData = self.rows

        self.sort(1,Qt.DescendingOrder)

    def rowCount(self,parent=None):
        return len(self.rows)

    def columnCount(self,parent=None):
        return len(self.columns)

    def sort(self, col, order):
        """sort table by given column number col"""
        self.layoutAboutToBeChanged.emit()
        self.rows = sorted(self.rows,
                key=lambda x: x[col])
        if order == Qt.DescendingOrder:
            self.rows.reverse()
        self.layoutChanged.emit()

    def data(self, index, role=None):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        row = index.row()
        col = index.column()
        data = self.rows[row][col]

        return data

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns[col]
        return None

class EnvironmentModel(QAbstractTableModel):
    def __init__(self,parent = None):
        QAbstractTableModel.__init__(self,parent)

        self.columns = ['']
        self.environments = list()

    def rowCount(self,parent=None):
        return len(self.environments)

    def columnCount(self,parent=None):
        return len(self.columns)

    def data(self, index, role=None):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.environments[index.row()][index.column()]

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns[col]
        return None

    def addRow(self,env):
        self.layoutAboutToBeChanged.emit()
        self.environments.append(env)
        self.layoutChanged.emit()

    def removeRow(self,ind):
        self.layoutAboutToBeChanged.emit()
        del self.environments[ind]
        self.layoutChanged.emit()

class ResultsModel(QAbstractTableModel):
    def __init__(self, header, results, parent=None):
        QAbstractTableModel.__init__(self,parent)

        self.columns = header

        self.results = results

    def rowCount(self,parent=None):
        return len(self.results)

    def columnCount(self,parent=None):
        return len(self.columns)

    def data(self, index, role=None):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        data = self.results[index.row()][index.column()]
        if isinstance(data,float):
            data = str(round(data,3))
        elif isinstance(data,bool):
            if data:
                data = 'Yes'
            else:
                data = 'No'
        else:
            data = str(data)
        return data

    def sort(self, col, order):
        """Sort table by given column number.
        """
        self.layoutAboutToBeChanged.emit()
        self.results = sorted(self.results, key=lambda x: x[col])
        if order == Qt.DescendingOrder:
            self.results.reverse()
        self.layoutChanged.emit()

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns[col]
        #elif role == Qt.SizeHintRole:
        #    return QSize(100,23)
        return QAbstractTableModel.headerData(self, col, orientation, role)


    def addData(self,extra):
        self.layoutAboutToBeChanged.emit()
        self.results += extra
        self.layoutChanged.emit()


class FeatureSystemModel(QAbstractTableModel):
    def __init__(self, specifier, parent=None):
        QAbstractTableModel.__init__(self,parent)
        self.specifier = specifier
        self.generateData()


    def rowCount(self,parent=None):
        return len(self.rows)

    def columnCount(self,parent=None):
        return len(self.columns)

    def data(self, index, role=None):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.rows[index.row()][index.column()]

    def sort(self, col, order):
        """Sort table by given column number.
        """
        self.layoutAboutToBeChanged.emit()
        self.rows = sorted(self.rows, key=lambda x: x[col])
        if order == Qt.DescendingOrder:
            self.rows.reverse()
        self.layoutChanged.emit()

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns[col]
        return QAbstractTableModel.headerData(self, col, orientation, role)

    def filter(self,segments):
        self.layoutAboutToBeChanged.emit()
        self.rows = [x for x in self.allrows if x[0] in segments]
        self.layoutChanged.emit()

    def showAll(self):
        self.layoutAboutToBeChanged.emit()
        self.rows = self.allrows
        self.layoutChanged.emit()

    def generateData(self):
        self.rows = list()
        self.columns = ['symbol']
        if self.specifier is None:
            return
        self.columns += self.specifier.features
        for x in self.specifier.segments:
            if x in ['','#']:
                continue
            self.rows.append([x]+[self.specifier[x,y] for y in self.specifier.features])
        self.allrows = self.rows

    def addSegment(self,seg,feat):
        self.layoutAboutToBeChanged.emit()
        self.specifier.add_segment(seg,feat)
        self.generateData()
        self.layoutChanged.emit()

    def addFeature(self,feat):
        self.layoutAboutToBeChanged.emit()
        self.specifier.add_feature(feat)
        self.generateData()
        self.layoutChanged.emit()
