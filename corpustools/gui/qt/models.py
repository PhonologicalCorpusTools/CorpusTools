import os
from collections import Counter

from .imports import *

class BaseTableModel(QAbstractTableModel):
    columns = []
    rows = []
    allData = []

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

    def addRow(self,row):
        self.layoutAboutToBeChanged.emit()
        self.rows.append(row)
        self.layoutChanged.emit()

    def addRows(self,rows):
        self.layoutAboutToBeChanged.emit()
        self.rows += rows
        self.layoutChanged.emit()

    def removeRow(self,ind):
        self.layoutAboutToBeChanged.emit()
        del self.rows[ind]
        self.layoutChanged.emit()

    def removeRows(self,inds):
        inds = sorted(inds, reverse=True)
        self.layoutAboutToBeChanged.emit()
        for i in inds:
            del self.rows[i]
        self.layoutChanged.emit()

class BaseCorpusTableModel(BaseTableModel):
    columns = []
    rows = []
    allData = []

    def sort(self, col, order):
        """sort table by given column number col"""
        self.layoutAboutToBeChanged.emit()
        self.rows = sorted(self.rows,
                key=lambda x: getattr(self.corpus[x],self.columns[col].name))
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
        data = getattr(self.corpus[self.rows[row]],self.columns[col].name)

        if isinstance(data,float):
            data = str(round(data,self.settings['sigfigs']))
        elif not isinstance(data,str):
            data = str(data)
        return data

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns[col].display_name
        return None

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

#class SpontaneousSpeechCorpusModel(QStandardItemModel):
    #def __init__(self,corpus, parent = None):
        #QStandardItemModel.__init__(self, parent)

        #self.corpus = corpus
        #self.setHorizontalHeaderItem (0,QStandardItem('Discourses'))

        #corpusItem = QStandardItem(self.corpus.name)
        #self.appendRow(corpusItem)
        #speakerItem = QStandardItem('s01')
        #corpusItem.appendRow(speakerItem)
        #for d in self.corpus.discourses.values():
            #speakerItem.appendRow(QStandardItem(str(d)))

    #def createLexicon(self,row):
        #d = self.item(row).text()
        #return self.corpus.discourses[d].create_lexicon()

class SpontaneousSpeechCorpusModel(QAbstractItemModel):
    def __init__(self, corpus, parent=None):
        super(SpontaneousSpeechCorpusModel, self).__init__(parent)
        self.corpus = corpus
        self.generateData()

    def generateData(self):

        self._rootNode = TreeItem("Speakers")

        for d in sorted(self.corpus.discourses.values()):
            for i in range(self._rootNode.childCount()):
                if self._rootNode.child(i)._dataItem == d.speaker:
                    node = self._rootNode.child(i)
                    break
            else:
                node = SpontaneousTreeItem(d.speaker, self._rootNode)
            dnode = SpontaneousTreeItem(d,node)

    def createLexicon(self,index):
        d = self.data(index,Qt.DisplayRole)
        return self.corpus.discourses[d].create_lexicon()

    """INPUTS: QModelIndex"""
    """OUTPUT: int"""
    def rowCount(self, parent):
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount()

    """INPUTS: QModelIndex"""
    """OUTPUT: int"""
    def columnCount(self, parent):
        return 1

    """INPUTS: QModelIndex, int"""
    """OUTPUT: QVariant, strings are cast to QString which is a QVariant"""
    def data(self, index, role):

        if not index.isValid():
            return None
        node = index.internalPointer()
        if node is None:
            print(index)

        if role == Qt.DisplayRole:
            if index.column() == 0:
                return node.name()


    """INPUTS: int, Qt::Orientation, int"""
    """OUTPUT: QVariant, strings are cast to QString which is a QVariant"""
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            return "Speakers"



    """INPUTS: QModelIndex"""
    """OUTPUT: int (flag)"""
    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable



    """INPUTS: QModelIndex"""
    """OUTPUT: QModelIndex"""
    """Should return the parent of the node with the given QModelIndex"""
    def parent(self, index):

        node = self.getNode(index)
        parentNode = node.parent()

        if parentNode == self._rootNode:
            return QModelIndex()

        return self.createIndex(parentNode.row(), 0, parentNode)

    """INPUTS: int, int, QModelIndex"""
    """OUTPUT: QModelIndex"""
    """Should return a QModelIndex that corresponds to the given row, column and parent node"""
    def index(self, row, column, parent):

        parentNode = self.getNode(parent)

        childItem = parentNode.child(row)


        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    """CUSTOM"""
    """INPUTS: QModelIndex"""
    def getNode(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node

        return self._rootNode

class DiscourseModel(BaseCorpusTableModel):
    def __init__(self,discourse, settings, parent = None):
        QAbstractTableModel.__init__(self, parent)
        self.settings = settings
        self.corpus = discourse
        self.columns = self.corpus.attributes
        self.rows = self.corpus.keys()
        #self.posToTime = []
        #self.timeToPos = {}
        #for w in self.discourse:
        #    self.timeToPos[w.begin] = len(self.posToTime)
        #    self.posToTime.append(w.begin)
        #    i = QStandardItem(str(w))
        #    i.setFlags(i.flags() | (not Qt.ItemIsEditable))
        #    self.appendRow(i)

        self.sort(2,Qt.AscendingOrder)

    def rowsToTimes(self,rows):
        return [self.rows[x] for x in rows]

    def timesToRows(self, times):
        return [i for i,x in enumerate(self.rows) if x in times]

    def hasAudio(self):
        return self.corpus.has_audio()

    def wordTokenObject(self,row):
        token = self.corpus[self.rows[row]]
        return token

class CorpusModel(BaseCorpusTableModel):
    def __init__(self, corpus, settings, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.settings = settings
        self.corpus = corpus
        self.nonLexHidden = False

        self.columns = self.corpus.attributes

        self.rows = self.corpus.words

        self.allData = self.rows

    def hideNonLexical(self, b):
        self.nonLexHidden = b
        self.layoutAboutToBeChanged.emit()
        self.rows = self.allData
        if b:
            self.rows = [x for x in self.rows if str(self.corpus[x].transcription) != '']
        self.layoutChanged.emit()

    def wordObject(self,row):
        return self.corpus[self.rows[row]]

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns[col].display_name
        return None

    def addWord(self, word):
        self.beginInsertRows(QModelIndex(),self.rowCount(),self.rowCount())
        self.corpus.add_word(word)
        self.rows = self.corpus.words
        self.endInsertRows()

    def replaceWord(self, row, word):
        self.removeWord(self.rows[row])
        self.addWord(word)

    def removeWord(self, word_key):
        row = self.rows.index(word_key)
        self.beginRemoveRows(QModelIndex(),row,row)
        self.corpus.remove_word(word_key)
        self.rows = self.corpus.words
        self.endRemoveRows()

    def addTier(self,attribute, segList):
        if attribute not in self.columns:
            end = True
            self.beginInsertColumns(QModelIndex(),self.columnCount(),self.columnCount())
        else:
            end = False
        self.corpus.add_tier(attribute, segList)
        self.columns = self.corpus.attributes
        if end:
            self.endInsertColumns()

    def addColumn(self, attribute):
        if attribute not in self.columns:
            end = True
            self.beginInsertColumns(QModelIndex(),self.columnCount(),self.columnCount())
        else:
            end = False
        self.corpus.add_attribute(attribute,initialize_defaults=True)
        self.columns = self.corpus.attributes
        if end:
            self.endInsertColumns()

    def addAbstractTier(self,attribute, segList):
        if attribute not in self.columns:
            end = True
            self.beginInsertColumns(QModelIndex(),self.columnCount(),self.columnCount())
        else:
            end = False
        self.corpus.add_abstract_tier(attribute, segList)
        self.columns = self.corpus.attributes
        if end:
            self.endInsertColumns()

    def removeAttributes(self,attributes):
        for a in attributes:
            for i,x in enumerate(self.columns):
                if x.display_name == a:
                    ind = i
                    att = x
                    break
            else:
                return
            self.beginRemoveColumns(QModelIndex(),ind,ind)
            self.corpus.remove_attribute(att)
            self.columns = self.corpus.attributes
            self.endRemoveColumns()

class SegmentPairModel(BaseTableModel):
    def __init__(self,parent = None):
        QAbstractTableModel.__init__(self,parent)

        self.columns = ['Segment 1', 'Segment 2']
        self.rows = list()

class VariantModel(BaseTableModel):
    def __init__(self, wordtokens, parent=None):
        super(VariantModel, self).__init__(parent)

        self.rows = [(k,v) for k,v in Counter(str(x.transcription) for x in wordtokens).items()]

        self.columns = ['Variant', 'Count']

        self.allData = self.rows

        self.sort(1,Qt.DescendingOrder)

class EnvironmentModel(BaseTableModel):
    def __init__(self,parent = None):
        QAbstractTableModel.__init__(self,parent)

        self.columns = ['']
        self.rows = list()

class ResultsModel(BaseTableModel):
    def __init__(self, header, results, settings, parent=None):
        QAbstractTableModel.__init__(self,parent)
        self.settings = settings
        self.columns = header

        self.rows = results

    def data(self, index, role=None):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        data = self.rows[index.row()][index.column()]
        if isinstance(data,float):
            data = str(round(data,self.settings['sigfigs']))
        elif isinstance(data,bool):
            if data:
                data = 'Yes'
            else:
                data = 'No'
        else:
            data = str(data)
        return data



class TreeItem(object):

    def __init__(self, name, parent=None):

        self._name = name
        self._children = []
        self._parent = parent

        if parent is not None:
            parent.addChild(self)

    def addChild(self, child):
        self._children.append(child)

    def insertChild(self, position, child):

        if position < 0 or position > len(self._children):
            return False

        self._children.insert(position, child)
        child._parent = self
        return True

    def removeChild(self, position):

        if position < 0 or position > len(self._children):
            return False

        child = self._children.pop(position)
        child._parent = None

        return True


    def name(self):
        return self._name

    def setName(self, name):
        self._name = name

    def child(self, row):
        return self._children[row]

    def childCount(self):
        return len(self._children)

    def parent(self):
        return self._parent

    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)

class SpontaneousTreeItem(TreeItem):
    def __init__(self, dataItem, parent=None):
        self._dataItem = dataItem
        if self._dataItem is not None:
            self._name = dataItem.name
        else:
            self._name = 'Unknown'
        self._children = []
        self._parent = parent

        if parent is not None:
            parent.addChild(self)

    def __eq__(self,other):
        if not isinstance(other,SpontaneousTreeItem):
            return False
        return self._dataItem == other._dataItem


class FeatureSystemTreeModel(QAbstractItemModel):
    def __init__(self, specifier, parent=None):
        super(FeatureSystemTreeModel, self).__init__(parent)
        self.specifier = specifier
        if specifier is not None:
            self.segments = [s for s in self.specifier]
        else:
            self.segments = list()
        self.generateData()

    def rowCount(self, parent):
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount()

    def columnCount(self, parent):
        return 1

    def data(self, index, role):

        if not index.isValid():
            return None
        node = index.internalPointer()
        if node is None:
            print(index)

        if role == Qt.DisplayRole:
            if index.column() == 0:
                return node.name()

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            return "Segments"

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def parent(self, index):
        node = self.getNode(index)
        parentNode = node.parent()

        if parentNode == self._rootNode:
            return QModelIndex()

        return self.createIndex(parentNode.row(), 0, parentNode)

    def index(self, row, column, parent):
        parentNode = self.getNode(parent)
        childItem = parentNode.child(row)

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def getNode(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node

        return self._rootNode

    def generateData(self):
        self._rootNode = TreeItem("Segment")
        consItem = TreeItem('Consonants', self._rootNode)
        placeItem = TreeItem('Place',consItem)
        placeValues = list()
        mannerItem = TreeItem('Manner',consItem)
        mannerValues = list()
        voiceItem = TreeItem('Voicing',consItem)
        voiceValues = list()

        vowItem = TreeItem('Vowels', self._rootNode)
        heightItem = TreeItem('Height',vowItem)
        heightValues = list()
        backItem = TreeItem('Backness',vowItem)
        backValues = list()
        roundItem = TreeItem('Rounding',vowItem)
        roundValues = list()
        diphItem = TreeItem('Diphthongs',vowItem)

        for s in self.segments:
            cat = s.category
            if cat is None:
                continue
            if cat[0] == 'Consonant':
                place = cat[1]
                manner = cat[2]
                voicing = cat[3]
                if place is None:
                    place = 'Unknown'
                if manner is None:
                    manner = 'Unknown'
                if voicing is None:
                    voicing = 'Unknown'
                for p in placeValues:
                    if p.name() == place:
                        item = p
                        break
                else:
                    item = TreeItem(place,placeItem)
                    placeValues.append(item)
                i = TreeItem(s.symbol,item)

                for m in mannerValues:
                    if m.name() == manner:
                        item = m
                        break
                else:
                    item = TreeItem(manner,mannerItem)
                    mannerValues.append(item)
                i = TreeItem(s.symbol,item)

                for v in voiceValues:
                    if v.name() == voicing:
                        item = v
                        break
                else:
                    item = TreeItem(voicing,voiceItem)
                    voiceValues.append(item)
                i = TreeItem(s.symbol,item)
            elif cat[0] == 'Vowel':
                height = cat[1]
                back = cat[2]
                rounded = cat[3]
                if height is None:
                    height = 'Unknown'
                if back is None:
                    back = 'Unknown'
                if rounded is None:
                    rounded = 'Unknown'

                for v in heightValues:
                    if v.name() == height:
                        item = v
                        break
                else:
                    item = TreeItem(height,heightItem)
                    heightValues.append(item)
                i = TreeItem(s.symbol,item)

                for v in backValues:
                    if v.name() == back:
                        item = v
                        break
                else:
                    item = TreeItem(back, backItem)
                    backValues.append(item)
                i = TreeItem(s.symbol,item)

                for v in roundValues:
                    if v.name() == rounded:
                        item = v
                        break
                else:
                    item = TreeItem(rounded, roundItem)
                    roundValues.append(item)
                i = TreeItem(s.symbol,item)

            elif cat[0] == 'Diphthong':
                i = TreeItem(s.symbol,diphItem)

    def filter(self,segments):
        self.layoutAboutToBeChanged.emit()
        self.segments = [x for x in self.specifier if x in segments]
        self.generateData()
        self.layoutChanged.emit()

    def showAll(self):
        self.layoutAboutToBeChanged.emit()
        self.segments = [s for s in self.specifier]
        self.generateData()
        self.layoutChanged.emit()

    def addSegment(self,seg,feat):
        self.layoutAboutToBeChanged.emit()
        self.specifier.add_segment(seg,feat)
        self.rows.append(self.specifier[seg])
        self.generateData()
        self.layoutChanged.emit()

    def addFeature(self,feat):
        #self.layoutAboutToBeChanged.emit()
        self.specifier.add_feature(feat)
        #self.generateData()
        #self.layoutChanged.emit()



class FeatureSystemTableModel(BaseTableModel):
    def __init__(self, specifier, parent=None):
        QAbstractTableModel.__init__(self,parent)
        self.specifier = specifier
        self.generateData()
        self.sort(0,Qt.AscendingOrder)

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

    def filter(self,segments):
        self.layoutAboutToBeChanged.emit()
        self.rows = [x for x in self.allrows if x[0] in segments]
        self.layoutChanged.emit()

    def showAll(self):
        self.layoutAboutToBeChanged.emit()
        self.rows = self.allrows
        self.layoutChanged.emit()

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
