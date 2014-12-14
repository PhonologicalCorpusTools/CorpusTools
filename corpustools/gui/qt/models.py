import os
from collections import Counter

from .imports import *

class FilterModel(QAbstractTableModel):
    conditionalMapping = {'__eq__':'==',
                    '__neq__':'!=',
                    '__gt__':'>',
                    '__gte__':'>=',
                    '__lt__':'<',
                    '__lte__':'<='}
    def __init__(self,parent = None):
        QAbstractTableModel.__init__(self,parent)

        self.columns = ['']
        self.filters = list()

    def rowCount(self,parent=None):
        return len(self.filters)

    def columnCount(self,parent=None):
        return len(self.columns)

    def data(self, index, role=None):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        f = self.filters[index.row()][index.column()]
        if f[0].att_type == 'numeric':
            return_data = ' '.join([str(f[0]),self.conditionalMapping[f[1]], str(f[2])])
        else:
            s = ', '.join(f[1])
            if len(s) > 20:
                s = s[:10] + '...' + s[-10:]
            return_data = ' '.join([str(f[0]),s])
        return return_data

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns[col]
        return None

    def addRow(self,env):
        self.layoutAboutToBeChanged.emit()
        self.filters.append(env)
        self.layoutChanged.emit()

    def removeRow(self,ind):
        self.layoutAboutToBeChanged.emit()
        del self.filters[ind]
        self.layoutChanged.emit()

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
                key=lambda x: getattr(self.corpus[x],self.columns[col].name))
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
        data = getattr(self.corpus[self.rows[row]],self.columns[col].name)

        if isinstance(data,float):
            data = str(round(data,3))
        elif not isinstance(data,str):
            data = str(data)
        return data

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns[col].display_name
        return None

    def addTier(self,tierName, segList):
        self.layoutAboutToBeChanged.emit()
        self.corpus.add_tier(tierName, segList)
        self.columns = self.corpus.attributes
        self.layoutChanged.emit()

    def columnAdded(self):
        self.layoutAboutToBeChanged.emit()
        self.columns = self.corpus.attributes
        self.layoutChanged.emit()

    def addAbstractTier(self,tierName, segList):
        self.layoutAboutToBeChanged.emit()
        self.corpus.add_abstract_tier(tierName, segList)
        self.columns = self.corpus.attributes
        self.layoutChanged.emit()

    def removeAttributes(self,attributes):
        self.layoutAboutToBeChanged.emit()
        for a in attributes:
            self.corpus.remove_attribute(a)
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


#class TreeItem(object):
    #def __init__(self, data, parent=None):
        #self.parentItem = parent
        #self.itemData = data
        #self.childItems = []

    #def appendChild(self, item):
        #self.childItems.append(item)

    #def child(self, row):
        #return self.childItems[row]

    #def childCount(self):
        #return len(self.childItems)

    #def columnCount(self):
        #return len(self.itemData)

    #def data(self, column):
        #try:
            #return self.itemData[column]
        #except IndexError:
            #return None

    #def parent(self):
        #return self.parentItem

    #def row(self):
        #if self.parentItem:
            #return self.parentItem.childItems.index(self)

        #return 0

#class FeatureSystemTreeModel(QAbstractItemModel):
    #def __init__(self, specifier, parent=None):
        #QAbstractItemModel.__init__(self,parent)
        #self.specifier = specifier

        #self.rootItem = TreeItem(("Segment"))
        #self.rows = [s for s in self.specifier]
        #self.generateData()

    #def columnCount(self, parent):
        #if parent.isValid():
            #return parent.internalPointer().columnCount()
        #else:
            #return self.rootItem.columnCount()

    #def data(self, index, role):
        #if not index.isValid():
            #return None

        #if role != QtCore.Qt.DisplayRole:
            #return None

        #item = index.internalPointer()

        #return item.data(index.column())

    #def flags(self, index):
        #if not index.isValid():
            #return QtCore.Qt.NoItemFlags

        #return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    #def headerData(self, section, orientation, role):
        #if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            #return self.rootItem.data(section)

        #return None

    #def index(self, row, column, parent):
        #if not self.hasIndex(row, column, parent):
            #return QtCore.QModelIndex()

        #if not parent.isValid():
            #parentItem = self.rootItem
        #else:
            #parentItem = parent.internalPointer()

        #childItem = parentItem.child(row)
        #if childItem:
            #return self.createIndex(row, column, childItem)
        #else:
            #return QtCore.QModelIndex()

    #def setupModelData(self, lines, parent):
        #parents = [parent]
        #indentations = [0]

        #number = 0

        #while number < len(lines):
            #position = 0
            #while position < len(lines[number]):
                #if lines[number][position] != ' ':
                    #break
                #position += 1

            #lineData = lines[number][position:].trimmed()

            #if lineData:
                ## Read the column data from the rest of the line.
                #columnData = [s for s in lineData.split('\t') if s]

                #if position > indentations[-1]:
                    ## The last child of the current parent is now the new
                    ## parent unless the current parent has no children.

                    #if parents[-1].childCount() > 0:
                        #parents.append(parents[-1].child(parents[-1].childCount() - 1))
                        #indentations.append(position)

                #else:
                    #while position < indentations[-1] and len(parents) > 0:
                        #parents.pop()
                        #indentations.pop()

                ## Append a new item to the current parent's list of children.
                #parents[-1].appendChild(TreeItem(columnData, parents[-1]))

            #number += 1
    #def generateData(self):
        #self.clear()
        #consItem = QStandardItem('Consonants')
        #placeItem = QStandardItem('Place')
        #placeValues = list()
        #mannerItem = QStandardItem('Manner')
        #mannerValues = list()
        #voiceItem = QStandardItem('Voicing')
        #voiceValues = list()

        #self.appendRow(consItem)
        #consItem.appendRow(placeItem)
        #consItem.appendRow(mannerItem)
        #consItem.appendRow(voiceItem)

        #vowItem = QStandardItem('Vowels')
        #heightItem = QStandardItem('Height')
        #heightValues = list()
        #backItem = QStandardItem('Backness')
        #backValues = list()
        #roundItem = QStandardItem('Rounding')
        #roundValues = list()
        #diphItem = QStandardItem('Diphthongs')

        #self.appendRow(vowItem)
        #vowItem.appendRow(heightItem)
        #vowItem.appendRow(backItem)
        #vowItem.appendRow(roundItem)
        #vowItem.appendRow(diphItem)

        #for s in self.rows:
            #cat = s.category
            #if cat is None:
                #continue
            #if cat[0] == 'Consonant':
                #place = cat[1]
                #manner = cat[2]
                #voicing = cat[3]
                #if place is None:
                    #place = 'Unknown'
                #if manner is None:
                    #manner = 'Unknown'
                #if voicing is None:
                    #voicing = 'Unknown'
                #for p in placeValues:
                    #if p.text() == place:
                        #item = p
                        #break
                #else:
                    #item = QStandardItem(place)
                    #placeValues.append(item)
                    #placeItem.appendRow(item)
                #item.appendRow(QStandardItem(s.symbol))

                #for m in mannerValues:
                    #if m.text() == manner:
                        #item = m
                        #break
                #else:
                    #item = QStandardItem(manner)
                    #mannerValues.append(item)
                    #mannerItem.appendRow(item)
                #item.appendRow(QStandardItem(s.symbol))

                #for v in voiceValues:
                    #if v.text() == voicing:
                        #item = v
                        #break
                #else:
                    #item = QStandardItem(voicing)
                    #voiceValues.append(item)
                    #voiceItem.appendRow(item)
                #item.appendRow(QStandardItem(s.symbol))
            #elif cat[0] == 'Vowel':
                #height = cat[1]
                #back = cat[2]
                #rounded = cat[3]
                #if height is None:
                    #height = 'Unknown'
                #if back is None:
                    #back = 'Unknown'
                #if rounded is None:
                    #rounded = 'Unknown'

                #for v in heightValues:
                    #if v.text() == height:
                        #item = v
                        #break
                #else:
                    #item = QStandardItem(height)
                    #heightValues.append(item)
                    #heightItem.appendRow(item)
                #item.appendRow(QStandardItem(s.symbol))

                #for v in backValues:
                    #if v.text() == back:
                        #item = v
                        #break
                #else:
                    #item = QStandardItem(back)
                    #backValues.append(item)
                    #backItem.appendRow(item)
                #item.appendRow(QStandardItem(s.symbol))

                #for v in roundValues:
                    #if v.text() == rounded:
                        #item = v
                        #break
                #else:
                    #item = QStandardItem(rounded)
                    #roundValues.append(item)
                    #roundItem.appendRow(item)
                #item.appendRow(QStandardItem(s.symbol))

            #elif cat[0] == 'Diphthong':
                #diphItem.appendRow(QStandardItem(s.symbol))

    #def filter(self,segments):
        #self.layoutAboutToBeChanged.emit()
        #self.rows = [x for x in self.specifier if x in segments]
        #self.generateData()
        #self.layoutChanged.emit()

    #def showAll(self):
        #self.layoutAboutToBeChanged.emit()
        #self.rows = [s for s in self.specifier]
        #self.generateData()
        #self.layoutChanged.emit()

    #def addSegment(self,seg,feat):
        #self.layoutAboutToBeChanged.emit()
        #self.specifier.add_segment(seg,feat)
        #self.rows.append(self.specifier[seg])
        #self.generateData()
        #self.layoutChanged.emit()

    #def addFeature(self,feat):
        #self.layoutAboutToBeChanged.emit()
        #self.specifier.add_feature(feat)
        #self.generateData()
        #self.layoutChanged.emit()



class FeatureSystemTableModel(QAbstractTableModel):
    def __init__(self, specifier, parent=None):
        QAbstractTableModel.__init__(self,parent)
        self.specifier = specifier
        self.generateData()
        self.sort(0,Qt.AscendingOrder)


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
