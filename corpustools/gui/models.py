from PyQt5.QtCore import QVariant
import random
import itertools
import collections
from .widgets import *
from corpustools.corpus.classes.lexicon import Segment, Inventory
from corpustools.exceptions import CorpusIntegrityError
from collections import defaultdict
from .imports import *

class BaseTableModel(QAbstractTableModel):

    def __init__(self, settings, parent = None):
        self.columns = []
        self.rows = []
        self.allData = []
        QAbstractTableModel.__init__(self, parent)
        self.settings = settings

    def rowCount(self, parent = None):
        return len(self.rows)

    def columnCount(self, parent = None):
        return len(self.columns)

    def sort(self, col, order):
        """sort table by given column number col"""
        self.layoutAboutToBeChanged.emit()
        self.rows = sorted(self.rows,
                key=lambda x: x[col])
        if order == Qt.DescendingOrder:
            self.rows.reverse()
        self.layoutChanged.emit()

    def data(self, index, role = None):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        row = index.row()
        col = index.column()
        try:
            data = self.rows[row][col]
            if isinstance(data,float):
                data = str(round(data,self.settings['sigfigs']))
            elif isinstance(data,bool):
                if data:
                    data = 'Yes'
                else:
                    data = 'No'
            elif isinstance(data,(list, tuple)):
                data = ', '.join(data)
            else:
                data = str(data)
        except IndexError:
            data = ''

        return data

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns[col]
        return None

    def addRow(self,row):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        if isinstance(row[0], dict):
            self.rows.append([row[header] for header in self.columns])
        else:
            self.rows.append(row)
        self.endInsertRows()

    def addRows(self,rows):
        self.beginInsertRows(QModelIndex(),self.rowCount(),self.rowCount() + len(rows)-1)
        for row in rows:
            if isinstance(row, dict):
                self.rows.append([row[header] for header in self.columns])
            else:
                self.rows.append(row)
        self.endInsertRows()

    def removeRow(self,ind):
        self.beginRemoveRows(QModelIndex(),ind,ind)
        del self.rows[ind]
        self.endRemoveRows()

    def removeRows(self, inds):
        inds = sorted(inds, reverse=True)
        for i in inds:
            self.beginRemoveRows(QModelIndex(),i,i)
            del self.rows[i]
            self.endRemoveRows()

class BaseCorpusTableModel(BaseTableModel):
    columns = []
    rows = []
    allData = []

    def __init__(self, corpus, settings, parent = None):
        BaseTableModel.__init__(self, settings, parent)
        try:
           discourses = corpus.discourses
        except AttributeError:
            discourses = list()

        if hasattr(corpus, 'lexicon'):
            corpus = corpus.lexicon
        self.corpus = corpus
        self.corpus.discourses = discourses
        self.columns = self.corpus.attributes
        self.columns.sort(key=self.column_sort)
        self.rows = self.corpus.words
        self.allData = self.rows

    def column_sort(self, x):
        att_type = x.att_type
        if att_type == 'spelling':
            return 0
        elif att_type == 'tier':
            return 1
        elif att_type == 'factor':
            return 2
        elif att_type == 'numeric':
            return 3
        else:
            return 4

    def sort(self, col, order):
        """sort table by given column number col"""
        self.layoutAboutToBeChanged.emit()
        try:
            self.rows = sorted(self.rows,
                    key=lambda x: getattr(self.corpus[x],
                                        self.columns[col].name))
        except TypeError:
            self.rows = sorted(self.rows,
                    key=lambda x: getattr(self.corpus[x],
                                self.coerce_to_float(self.columns[col].name)))
        if order == Qt.DescendingOrder:
            self.rows.reverse()
        self.layoutChanged.emit()

    def coerce_to_float(self, val):
        try:
            return float(val)
        except ValueError:
            return 0.0

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
    #conditionalMapping = {'__eq__': '==',
    #                      '__neq__': '!=',
    #                      '__gt__': '>',
    #                      '__gte__': '>=',
    #                      '__lt__': '<',
    #                      '__lte__': '<='}

    conditionalMapping = {operator.eq: '==',
                          operator.ne: '!=',
                          operator.gt: '>',
                          operator.ge: '>=',
                          operator.lt: '<',
                          operator.le: '<='}

    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)

        self.columns = ['']
        self.filters = list()

    def rowCount(self, parent=None):
        return len(self.filters)

    def columnCount(self, parent=None):
        return len(self.columns)

    def data(self, index, role=None):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        f = self.filters[index.row()]
        if f[0].att_type == 'numeric':
            return_data = ' '.join([str(f[0]), self.conditionalMapping[f[1]], str(f[2])])
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

    def addRow(self, env):
        self.layoutAboutToBeChanged.emit()
        self.filters.append(env)
        self.layoutChanged.emit()

    def removeRow(self, ind):
        self.layoutAboutToBeChanged.emit()
        del self.filters[ind]
        self.layoutChanged.emit()


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
        # if node is None:
        #     print(index)

        if role == Qt.DisplayRole:
            #if index.column() == 0:
            if node.name() is None:
                return 'All speakers'
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
        self.columns.sort(key=self.column_sort)
        self.rows = [x for x in list(self.corpus.words)]
        self.rows.sort()

    def rowsToTimes(self,rows):
        return [self.rows[x] for x in rows]

    def timesToRows(self, times):
        return [i for i,x in enumerate(self.rows) if x in times]

    def hasAudio(self):
        return self.corpus.has_audio

    def audioPath(self):
        return self.corpus.wav_path

    def wordTokenObject(self,row):
        token = self.corpus[self.rows[row]]
        return token

class CorpusModel(BaseCorpusTableModel):
    def __init__(self, corpus, settings, parent=None):
        BaseCorpusTableModel.__init__(self, corpus, settings, parent)
        self.nonLexHidden = False

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
        self.columns = [x for x in self.corpus.attributes]
        self.columns.sort(key=self.column_sort)
        if end:
            self.endInsertColumns()

    def beginAddColumn(self, attribute):
        if attribute not in self.columns:
            end = True
            self.beginInsertColumns(QModelIndex(),self.columnCount(),self.columnCount())
        else:
            end = False
        return end

    def endAddColumn(self, end = False):
        self.columns = [x for x in self.corpus.attributes]
        self.columns.sort(key=self.column_sort)
        if end:
            self.endInsertColumns()

    def addColumn(self, attribute):
        end = self.beginAddColumn(attribute)
        self.corpus.add_attribute(attribute,initialize_defaults=True)
        self.endAddColumn(end)

    def addCountColumn(self, attribute, sequenceType, segList):
        if attribute not in self.columns:
            end = True
            self.beginInsertColumns(QModelIndex(),self.columnCount(),self.columnCount())
        else:
            end = False
        self.corpus.add_count_attribute(attribute, sequenceType, segList)
        self.columns = [x for x in self.corpus.attributes]
        self.columns.sort(key=self.column_sort)
        if end:
            self.endInsertColumns()


    def addAbstractTier(self,attribute, segList):
        if attribute not in self.columns:
            end = True
            self.beginInsertColumns(QModelIndex(),self.columnCount(),self.columnCount())
        else:
            end = False
        self.corpus.add_abstract_tier(attribute, segList)
        self.columns = [x for x in self.corpus.attributes]
        self.columns.sort(key=self.column_sort)
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
            self.columns = [x for x in self.corpus.attributes]
            self.columns.sort(key=self.column_sort)
            self.endRemoveColumns()

class SegmentPairModel(BaseTableModel):
    def __init__(self,parent = None):
        QAbstractTableModel.__init__(self,parent)

        self.columns = ['Segment 1', 'Segment 2', '']
        self.rows = []

    def switchRow(self,row):
        try: # Only swap rows with 2 elements
            seg1,seg2 = self.rows[row]
        except ValueError:
            return

        self.rows[row] = (seg2, seg1)
        self.dataChanged.emit(self.createIndex(row,0), self.createIndex(row,1))


class VariantModel(BaseTableModel):
    def __init__(self, word, parent=None):
        super(VariantModel, self).__init__(parent)

        self.rows = [(k,v) for k,v in word.variants().items()]

        self.columns = ['Variant', 'Count']

        self.allData = self.rows

        self.sort(1,Qt.DescendingOrder)

class EnvironmentModel(BaseTableModel):
    def __init__(self,parent = None):
        QAbstractTableModel.__init__(self,parent)

        self.columns = ['']
        self.rows = []

class ResultsModel(BaseTableModel):
    def __init__(self, header, results, settings, parent=None):
        QAbstractTableModel.__init__(self,parent)
        self.settings = settings
        headerDynamic = []
        headerStatic = []
        headerIdx = -1
        for currHeader in header:
            headerIdx += 1
            currRow = 0
            stop = 0
            while stop is not 1 and currRow+1 < len(results):
                cv = results[currRow][currHeader]
                nv = results[currRow+1][currHeader]
                if cv != nv:
                    stop = 1
                currRow +=1
            if stop == 0:
                headerStatic.append(headerIdx)
            else:
                headerDynamic.append(headerIdx)

        newHeader = []
        for headerIdx in (headerDynamic + headerStatic):
            newHeader.append(header[headerIdx])

        orderResults = settings.__getitem__('resultsDisplay')
        if orderResults['unique_first']:
            self.columns = newHeader
        else:
            self.columns = header
        currRows = []
        for row in results:
            currRow = []
            for currHeader in self.columns:
                currRow.append(row[currHeader])
            currRows.append(currRow)
        self.rows = currRows


class PhonoSearchResultsModel(BaseTableModel):
    def __init__(self, header, summary_header, results, settings, parent=None):
        QAbstractTableModel.__init__(self,parent)
        self.settings = settings
        self.header = header
        self.summary_header = summary_header
        self.columns = self.header
        self.allData = results
        # self.summarizedAllData = list()
        # self.setSummarizedData()
        self.rows = [[data[h] for h in self.header] for data in self.allData]
        self.summarized = False

    def _summarize(self):
        typefreq = defaultdict(float)
        tokenfreq = defaultdict(float)

        for line in self.allData:
            segs = line['Segment']
            envs = line['Environment']
            for i,seg in enumerate(segs):
                segenv = seg,envs[i]
                typefreq[segenv] += 1
                tokenfreq[segenv] += line['Word'].frequency

        self.rows = list()
        for k,v in sorted(typefreq.items()):
            self.rows.append([k[0],k[1],v, tokenfreq[k]])
            #this row formatting doesn't match the dictionary-style results used elsewhere, which might be a problem,
            #but the results are fixed in the right order currently
        self.columns = self.summary_header

    def _summarize2(self):

        self.rows = [[data[h] for h in self.summary_header] for data in self.summarizedAllData]
        self.columns = self.summary_header

    def setSummarizedData(self):
        self.summarizedAllData = list()
        for line in self.allData:
            mini_dict = dict()
            mini_dict['Segment'] = line['Segment']
            mini_dict['Environment'] = line['Environment']
            mini_dict['Type frequency'] = len(line['Segment'])
            mini_dict['Token frequency'] = sum([line['Word'].frequency for s in line['Segment']])
            self.summarizedAllData.append(mini_dict)

    def setSummarized(self, b):
        if self.summarized == b:
            return
        self.summarized = b
        self.layoutAboutToBeChanged.emit()
        if self.summarized:
            self._summarize()
        else:
            self.rows = [[data[h] for h in self.header] for data in self.allData]
            self.columns = self.header

        self.layoutChanged.emit()

    def addRows(self,rows):
        self.layoutAboutToBeChanged.emit()
        self.allData.extend(rows)
        if self.summarized:
            self._summarize()
        self.layoutChanged.emit()

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
            self.segments = []
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
        # if node is None:
        #     print(index)

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
        placeValues = []
        mannerItem = TreeItem('Manner',consItem)
        mannerValues = []
        voiceItem = TreeItem('Voicing',consItem)
        voiceValues = []

        vowItem = TreeItem('Vowels', self._rootNode)
        heightItem = TreeItem('Height',vowItem)
        heightValues = []
        backItem = TreeItem('Backness',vowItem)
        backValues = []
        roundItem = TreeItem('Rounding',vowItem)
        roundValues = []
        diphItem = TreeItem('Diphthongs',vowItem)

        for s in self.segments:
            cat = self.specifier.categorize(s)
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

    def addFeature(self,feat, default):
        self.layoutAboutToBeChanged.emit()
        self.specifier.add_feature(feat,default=default)
        self.generateData()
        self.layoutChanged.emit()

class InventoryModel(QAbstractTableModel):
    """
    See corpustools.corpus.io.csv.load_corpus_csv()
    See also corpustools.corpus.classes.lexicon.Corpus.add_word()
    See also corpustools.corpus.classes.lexicon.Corpus.update_inventory()
    """

    modelResetSignal = Signal(bool)

    def __init__(self, inventory, copy_mode=False):
        super().__init__()

        if copy_mode:
            self.setAttributes(inventory)
            return

        self.initDefaults()
        self.segs = inventory.segs
        self.features = inventory.features
        self.possible_values = inventory.possible_values
        self.stresses = inventory.stresses
        self.syllables = inventory.syllables
        self.stress_types = inventory.stress_types
        self.tone_types = inventory.tone_types


        if not self.cons_column_data:
            self.reGenerateNames()
              
        self.generateGenericNames()
        self.categorizeInventory()
        self.sortData()
        self.filterGenericNames()
        self.isNew = False


    def initDefaults(self):
        for attribute, default_value in Inventory.inventory_attributes.items():
            if isinstance(default_value, list):
                setattr(self, attribute, [x for x in default_value])
            elif isinstance(default_value, dict):
                setattr(self, attribute, default_value.copy())
            else:
                setattr(self, attribute, default_value)

    def __eq__(self, other):
        if not isinstance(other, InventoryModel):
            return False
        for attr in Inventory.inventory_attributes:
            try:
                if not getattr(self, attr) == getattr(other, attr):
                    return False
            except AttributeError:
                return False
        else:
            return True

    def setAttributes(self, source):
        for attribute, default_value in Inventory.inventory_attributes.items():
            try:
                setattr(self, attribute, getattr(source, attribute))
            except AttributeError:
                if isinstance(default_value, list):
                    setattr(self, attribute, [x for x in default_value])
                elif isinstance(default_value, dict):
                    setattr(self, attribute, default_value.copy())
                else:
                    setattr(self, attribute, default_value)

    def set_major_class_features(self, source):
        self.cons_features = source.cons_features if hasattr(source, 'cons_features') else None
        self.vowel_features = source.vowel_features if hasattr(source, 'vowel_features') else None
        self.voice_feature = source.voice_feature if hasattr(source,'voice_feature') else None
        self.rounded_feature = source.round_feature if hasattr(source, 'round_feature') else None
        self.diph_feature = source.diph_feature if hasattr(source, 'diph_feature') else None

    def columnCount(self, parent=None):
        return len(self._data[0])  # any element would do, they should all be the same length

    def rowCount(self, parent=None):
        return len(self._data)

    def consRowCount(self):
        return len(self.consRows)

    def consColumnCount(self):
        return len(self.consColumns)

    def vowelRowCount(self):
        return len(self.vowelRows)

    def vowelColumnCount(self):
        return len(self.vowelColumns)

    def updateFromCopy(self, copy):
        self.setAttributes(copy)
        self.modelReset()

    def updateFeatures(self, specifier, preserve_features = False):
        for seg in self.segs:
            if seg == '#':
                continue
            if seg not in specifier:
                specifier[seg] = {feature.lower():'n' for feature in specifier.features}
            self.segs[seg].features = specifier.specify(seg)

        self.features = specifier.features
        self.possible_values = specifier.possible_values
        self.modelReset(preserve_features=preserve_features)

    def updateInventory(self, new_segs):
        self.segs = {symbol: Segment(symbol) for symbol in new_segs}

    def changeColumnSpecs(self, index, features, new_section_name, consonants=True):
        if consonants:
            name = self.cons_column_header_order[index]
            self.cons_column_data.pop(name)
            self.cons_column_data[new_section_name] = [index, {f[1:]: f[0] for f in features}, None]
            self.consColumns.remove(name)
            self.consColumns.add(new_section_name)
        else:
            index += self.vowel_column_offset
            name = self.vowel_column_header_order[index]
            self.vowel_column_data.pop(name)
            self.vowel_column_data[new_section_name] = [index, {f[1:]: f[0] for f in features}, None]
            self.vowelColumns.remove(name)
            self.vowelColumns.add(new_section_name)
        self.modelReset()
        return True

    def changeRowSpecs(self, index, features, new_section_name, consonants=True):
        if consonants:
            name = self.cons_row_header_order[index]
            self.cons_row_data.pop(name)
            self.cons_row_data[new_section_name] = [index, {f[1:]: f[0] for f in features}, None]
            self.consRows.remove(name)
            self.consRows.add(new_section_name)
        else:
            index += self.vowel_row_offset
            name = self.vowel_row_header_order[index]
            self.vowel_row_data.pop(name)
            self.vowel_row_data[new_section_name] = [index, {f[1:]: f[0] for f in features}, None]
            self.vowelRows.remove(name)
            self.vowelRows.add(new_section_name)
        self.modelReset()
        return True

    def getPartialCategorization(self, seg):

        cons_category = list()
        for row, col in itertools.product(self.cons_row_data, self.cons_column_data):
            row_index, row_features, row_segs = self.cons_row_data[row]
            col_index, col_features, col_segs = self.cons_column_data[col]

            if (all(row_features[key] == seg.features[key] for key in row_features)):
                cons_category.append(row)
            elif all(col_features[key] == seg.features[key] for key in col_features):
                cons_category.append(col)

        if not cons_category:
            cons_category.append('None')
        else:
            cons_category = list(set(cons_category))

        vowel_category = list()
        for row, col in itertools.product(self.vowel_row_data, self.vowel_column_data):
            row_index, row_features, row_segs = self.vowel_row_data[row]
            col_index, col_features, col_segs = self.vowel_column_data[col]

            if (all(row_features[key] == seg.features[key] for key in row_features)):
                vowel_category.append(row)
            elif all(col_features[key] == seg.features[key] for key in col_features):
                vowel_category.append(col)

        if not vowel_category:
            vowel_category.append('None')
        else:
            vowel_category = list(set(vowel_category))

        cons_category = ','.join(cons_category)
        vowel_category = ','.join(vowel_category)
        return 'Consonant matches:\n{}\nVowel matches:\n{}'.format(cons_category, vowel_category)


    def data(self, index, role=None):
        if not index.isValid():
            return QVariant()
        info = self._data[index.row()][index.column()]
        #checking for "if not info" might be causing problems because info can return an empty string
        #empty strings are used as padding to make every row in the model the same length
        # if not info:
        #     print('no info')
        #     return QVariant()
        if role == Qt.DisplayRole:
            return info
        else:
            return QVariant()

    def setData(self, index, value, role=None):
        if not index.isValid() or role != Qt.EditRole:
            return False
        self._data[index.row()][index.column()] = value  # this probably won't work
        self.dataChanged.emit(index, index)
        return True

    def isVoiced(self, seg):
        return False if self.voice_feature is None else seg.features[self.voice_feature[1:]] == self.voice_feature[0]

    def isVowel(self, seg):
        #return False if self.vowel_features is None else seg.features[self.vowel_features[1:]] == self.vowel_features[0]
        if self.vowel_features is None or self.vowel_features[0] is None:
            return False
        return all(seg.features[feature[1:]] == feature[0] for feature in self.vowel_features)

    def isCons(self, seg):
        #return False if self.vowel_features is None else seg.features[self.vowel_features[1:]] == self.vowel_features[0]
        if self.cons_features is None or self.cons_features[0] is None:
            return False
        return all(seg.features[feature[1:]] == feature[0] for feature in self.cons_features)

    def isRounded(self, seg):
        return False if self.rounded_feature is None else seg.features[self.rounded_feature[1:]] == self.rounded_feature[0]

    def isDiphthong(self, seg):
        return False if self.diph_feature is None else seg.features[self.diph_feature[1:]] == self.diph_feature[0]

    def categorizeInventory(self):

        # initialize some variables to avoid duplication when doing modelReset()
        self.vowelList = list()
        self.consList = list()
        self.uncategorized = list()

        for s in self.segs.values():
            if s.symbol in self.non_segment_symbols:
                self.uncategorized.append(s)
                continue  #ignore the word boundary symbol
            try:
                c = self.categorize(s)
            except KeyError:
                #self.categorize will raise a KeyError if no categories are matched
                c = None
                self.uncategorized.append(s)
            if c is not None:
                if c[0] == 'Vowel':
                    self.vowelColumns.add(c[1])
                    self.vowelRows.add(c[2])
                    self.vowelList.append((s, c))
                elif c[0] == 'Consonant':
                    self.consColumns.add(c[1])
                    self.consRows.add(c[2])
                    self.consList.append((s, c))
        if not self.consColumns:
            self.consColumns.add('Column 1')
            self.cons_column_data = {'Column 1': [0, {}, None]}
        if not self.consRows:
            self.consRows.add('Row 1')
            self.cons_row_data = {'Row 1': [0,{},None]}
        if not self.vowelColumns:
            self.vowelColumns.add('Column 1')
            self.vowel_column_data = {'Column 1': [0, {}, None]}
        if not self.vowelRows:
            self.vowelRows.add('Row 1')
            self.vowel_row_data = {'Row 1': [0,{},None]}


    def headerData(self, row_or_col, orientation, role=None):
        try:
            if orientation == Qt.Horizontal and role == Qt.DisplayRole:
                return self.all_columns[row_or_col]
            elif orientation == Qt.Vertical and role == Qt.DisplayRole:
                return self.all_rows[row_or_col]
        except KeyError:
            return QVariant()

    def generateSegmentButton(self, symbol):
        wid = SegmentButton(symbol)  # This needs to be a SegmentButton for the i,j segment
        wid.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        b = QGridLayout()
        b.setAlignment(Qt.AlignCenter)
        b.setContentsMargins(0, 0, 0, 0)
        b.setSpacing(0)
        l = QWidget()
        l.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        lb = QVBoxLayout()
        lb.setAlignment(Qt.AlignCenter)
        lb.setContentsMargins(0, 0, 0, 0)
        lb.setSpacing(0)
        l.setLayout(lb)
        # l.hide()
        b.addWidget(l, 0, 0)  #, alignment = Qt.AlignCenter)
        r = QWidget()
        r.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        rb = QVBoxLayout()
        rb.setAlignment(Qt.AlignCenter)
        rb.setContentsMargins(0, 0, 0, 0)
        rb.setSpacing(0)
        r.setLayout(rb)
        #r.hide()
        b.addWidget(r, 0, 1)  #, alignment = Qt.AlignCenter)
        wid.setLayout(b)
        wid.setCheckable(True)
        wid.setAutoExclusive(False)
        wid.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.btnGroup.addButton(wid)
        return wid

    def removeColumn(self, index, consonants=True):
        if consonants:
            column_data = self.cons_column_data
            headers = self.consColumns
        else:
            column_data = self.vowel_column_data
            headers = self.vowelColumns

        if len(column_data) == 1:
            return #do not delete the last remaining column

        for key, value in column_data.items():
            if value[0] == index.column():
                target = key
                continue
            if value[0] >= index.column():
                column_data[key][0] -= 1

        column_data.pop(target)
        headers.remove(target)
        self.modelReset()
        return True


    def removeRow(self, index, consonants=True):

        if consonants:
            row_data = self.cons_row_data
            headers = self.consRows
        else:
            row_data = self.vowel_row_data
            headers = self.vowelRows

        if len(row_data) == 1:
            return #don't delete the last remaining row

        for key, value in row_data.items():
            if value[0] == index.row():
                target = key
                continue
            if value[0] >= index.row():
                row_data[key][0] -= 1
        row_data.pop(target)
        headers.remove(target)
        self.modelReset()
        return True

    def insertColumn(self, index, consonants=True):

        if consonants:
            column_data = self.cons_column_data
            headers = self.consColumns
            basic_features = {}
        else:
            column_data = self.vowel_column_data
            headers = self.vowelColumns
            basic_features = {}

        for key, value in column_data.items():
            if value[0] >= index.column():
                column_data[key][0] += 1

        n = 1
        while True:
            new_name = 'New Column {}'.format(n)
            if new_name in column_data.keys():
                n += 1
                continue
            else:
                column_data[new_name] = [index.column(), basic_features, None]
                headers.add(new_name)
                break
        self.modelReset()
        return True

    def insertRow(self, index, consonants=True):

        if consonants:
            row_data = self.cons_row_data
            headers = self.consRows
            basic_features = {}
        else:
            row_data = self.vowel_row_data
            headers = self.vowelRows
            basic_features = {}
        for key, value in row_data.items():
            if value[0] >= index.row():
                row_data[key][0] += 1
        n = 1
        while True:
            new_name = 'New Row {}'.format(n)
            if new_name in row_data.keys():
                n += 1
                continue
            else:
                row_data[new_name] = [index.row(), basic_features, None]
                headers.add(new_name)
                break
        self.modelReset()
        return True

    def modelReset(self, *args, **kwargs):
        self.modelAboutToBeReset.emit()
        preserve_features = kwargs.pop('preserve_features', False)
        if not preserve_features:
            self.categorizeInventory()
        self.sortData()
        self.filterGenericNames()
        self.endResetModel()
        self.modelResetSignal.emit(True)

    def changeColumnOrder(self, map, consonants=True):
        if consonants:
            column_data = self.cons_column_data
        else:
            column_data = self.vowel_column_data

        for visualIndex, headerName in map.values():
            if visualIndex == -1:
                continue
            column_data[headerName][0] = visualIndex
        self.modelReset()


    def changeRowOrder(self, map, consonants=True):
        if consonants:
            row_data = self.cons_row_data
        else:
            row_data = self.vowel_row_data

        for visualIndex, headerName in map.values():
            if visualIndex == -1:
                continue
            row_data[headerName][0] = visualIndex
        self.modelReset()

    def reGenerateNames(self):
        self.consRows = set()
        self.vowelRows = set()
        self.consColumns = set()
        self.vowelColumns = set()
        self.generateGenericNames()
        self.modelReset()

    def filterGenericNames(self):
        if not self.filterNames:
            return

        self.cons_column_data = {key: value for (key, value) in self.cons_column_data.items()
                                 if key in self.cons_column_header_order.values()}
        sorted_columns = sorted([(k, v) for k, v in self.cons_column_data.items()], key=lambda x: x[1][0])
        for i, key_value in enumerate(sorted_columns):
            key, value = key_value
            self.cons_column_data[key][0] = i

        self.vowel_column_data = {key: value for (key, value) in self.vowel_column_data.items()
                                  if key in self.vowel_column_header_order.values()}
        sorted_columns = sorted([(k, v) for k, v in self.vowel_column_data.items()], key=lambda x: x[1][0])
        for i, key_value in enumerate(sorted_columns):
            key, value = key_value
            self.vowel_column_data[key][0] = i

        self.cons_row_data = {key: value for (key, value) in self.cons_row_data.items()
                              if key in self.cons_row_header_order.values()}
        sorted_rows = sorted([(k, v) for k, v in self.cons_row_data.items()], key=lambda x: x[1][0])
        for i, key_value in enumerate(sorted_rows):
            key, value = key_value
            self.cons_row_data[key][0] = i

        self.vowel_row_data = {key: value for (key, value) in self.vowel_row_data.items()
                               if key in self.vowel_row_header_order.values()}
        sorted_rows = sorted([(k, v) for k, v in self.vowel_row_data.items()], key=lambda x: x[1][0])
        for i, key_value in enumerate(sorted_rows):
            key, value = key_value
            self.vowel_row_data[key][0] = i

    def getHeaderOrder(self, orientation, cons_or_vowel):
        if orientation == Qt.Horizontal:
            if cons_or_vowel == 'cons':
                data = self.consColumns
            else:
                data = self.VowelColumns
        elif orientation == Qt.Vertical:
            if cons_or_vowel == 'cons':
                data = self.consRows
            else:
                data = self.vowelRows
        else:
            raise ValueError('The orientation value passed to Inventory.getHeaderOrder is not valid')
        return sorted(data)

    def sortData(self):
        sorted_cons_col_headers = sorted(list(self.consColumns), key=lambda x: self.cons_column_data[x][0])
        sorted_cons_row_headers = sorted(list(self.consRows), key=lambda x: self.cons_row_data[x][0])
        sorted_vowel_col_headers = sorted(list(self.vowelColumns), key=lambda x: self.vowel_column_data[x][0])
        sorted_vowel_row_headers = sorted(list(self.vowelRows), key=lambda x: self.vowel_row_data[x][0])
        self.cons_column_header_order = {i: name for i, name in enumerate(sorted_cons_col_headers)}
        self.vowel_column_offset = len(self.cons_column_header_order)
        self.vowel_column_header_order = {i + self.vowel_column_offset: name for i, name in enumerate(sorted_vowel_col_headers)}
        self.cons_row_header_order = {i: name for i, name in enumerate(sorted_cons_row_headers)}
        self.vowel_row_offset = len(self.cons_row_header_order)
        self.vowel_row_header_order = {i + self.vowel_row_offset: name for i, name in
                                       enumerate(sorted_vowel_row_headers)}
        self.all_columns = {}
        self.all_rows = {}
        self.all_columns.update(self.cons_column_header_order)
        self.all_columns.update(self.vowel_column_header_order)
        self.all_rows.update(self.cons_row_header_order)
        self.all_rows.update(self.vowel_row_header_order)

        col_total = max(len(self.all_columns), len(self.uncategorized))
        row_total = len(self.all_rows) + 1  # add one row for uncategorized

        self._data = [[None for j in range(col_total)] for k in range(row_total)]

        #ADD IN UNCATEGORIZED DATA
        for j in range(len(self._data[-1])):
            try:
                seg = self.uncategorized[j]
                self._data[-1][j] = seg.symbol
            except IndexError:  #passed the end of self.uncategorized (not self._data)
                self._data[-1][j] = ''

        #ADD IN CONSONANT DATA
        for row, col in itertools.product(self.cons_row_header_order.keys(),
                                          self.cons_column_header_order.keys()):
            row_name = self.cons_row_header_order[row]
            col_name = self.cons_column_header_order[col]
            matches = list()
            for seg, cat in self.consList:
                if row_name in cat and col_name in cat:
                    matches.append(seg)
            self._data[row][col] = ','.join([m.symbol for m in matches])

        #ADD IN VOWEL DATA
        for row, col in itertools.product(self.vowel_row_header_order.keys(),
                                          self.vowel_column_header_order.keys()):
            row_name = self.vowel_row_header_order[row]
            col_name = self.vowel_column_header_order[col]
            matches = list()
            for seg, cat in self.vowelList:
                if row_name in cat and col_name in cat:
                    matches.append(seg)
            self._data[row][col] = ','.join([m.symbol for m in matches])

    def resetCategories(self):
        self.cons_column_data = {'Column 1': [0, {}, None]}
        self.cons_row_data = {'Row 1': [0, {}, None]}
        self.vowel_column_data = {'Column 1': [0, {}, None]}
        self.vowel_row_data = {'Row 1': [0, {}, None]}
        self.consRows = set()
        self.vowelRows = set()
        self.consColumns = set()
        self.vowelColumns = set()
        self.uncategorized = list()
        self.filterNames = False
        self.modelReset()

    def generateGenericNames(self):
        try:
            sample = random.choice([seg for seg in self.segs.values() if not seg.symbol == '#'])
            # pick an arbitrary segment and examine its features; they all should have the same feature list
        except IndexError:
            raise CorpusIntegrityError('No segments were found in the inventory')
        if all([feature in sample.features for feature in self.minimum_features['hayes']]):
            self.generateGenericHayes()
            self.cons_features = ['+consonantal']
            self.vowel_features = ['-consonantal']
            self.voice_feature = '+voice'
            self.rounded_feature = '+round'
            self.diph_feature = '+diphthong'
            self.filterNames = True
        elif all([feature in sample.features for feature in self.minimum_features['spe']]):
            self.generateGenericSpe()
            self.cons_features = ['-voc']
            self.vowel_features = ['+voc']
            self.voice_feature = '+voice'
            self.rounded_feature = '+round'
            self.diph_feature = None
            self.filterNames = True
        else:
            self.cons_column_data = {'Column 1' : [0, {}, None]}
            self.cons_row_data = {'Row 1' : [0, {}, None]}
            self.vowel_column_data = {'Column 1': [0, {}, None]}
            self.vowel_row_data = {'Row 1' : [0, {}, None]}
            self.filterNames = False

    def generateGenericSpe(self):
        self.cons_column_data = dict()
        self.cons_column_data['Labial'] = [0,{'voc':'-','ant':'+','cor':'-','high':'-','low':'-','back':'-'},None]
        self.cons_column_data['Dental'] = [1,{'voc':'-','ant':'+','cor':'+','high':'-','low':'-','back':'-'},None]
        self.cons_column_data['Alveolar'] = [2,{'voc':'-','ant':'-','cor':'+','high':'+','low':'-','back':'-'},None]
        self.cons_column_data['Palatal'] = [3,{'voc':'-','ant':'-','cor':'-','high':'+','low':'-','back':'-'},None]
        self.cons_column_data['Velar'] = [4,{'voc':'-','ant':'-','cor':'-','high':'+','low':'-','back':'+'},None]
        self.cons_column_data['Uvular'] = [5,{'voc':'-','ant':'-','cor':'-','high':'-','low':'-','back':'+'},None]

        self.cons_row_data = dict()
        self.cons_row_data['Stop'] = [0,{'voc':'-','cont':'-','nasal':'-','son':'-'},None]
        self.cons_row_data['Nasal'] = [1,{'voc':'-','nasal':'+'},None]
        self.cons_row_data['Fricative'] = [2,{'voc':'-','cont':'+','nasal':'-','son':'-'},None]
        self.cons_row_data['Lateral'] = [3,{'voc':'-','lat':'+'},None]

        self.vowel_row_data = dict()
        self.vowel_row_data['High'] = [0,{'voc':'+','high':'+','low':'-'},None]
        self.vowel_row_data['Mid'] = [1,{'voc': '+', 'high': '-', 'low': '-'}, None]
        self.vowel_row_data['Low'] = [2, {'voc': '+', 'high': '-', 'low': '+'}, None]

        self.vowel_column_data = dict()
        self.vowel_column_data['Front'] = [0,{'voc':'+','back':'-'},None]
        self.vowel_column_data['Back'] = [1,{'voc':'+','back': '+'}, None]

    def generateGenericHayes(self):
        self.cons_column_data = dict()
        self.cons_column_data['Labial'] = [0,{'consonantal':'+','labial':'+','coronal':'-','labiodental': '-'}, None]
        self.cons_column_data['Labiodental'] = [1,{'consonantal': '+', 'labiodental': '+'}, None]
        self.cons_column_data['Dental'] = [2,{'consonantal':'+','anterior':'+','coronal':'+','labial':'-',
                                              'labiodental': '-'},None]
        self.cons_column_data['Alveopalatal'] = [3,{'consonantal':'+','anterior':'-','coronal':'+','labial': '-'}, None]
        self.cons_column_data['Palatal'] = [4,{'consonantal': '+','dorsal': '+','coronal':'+','labial':'-'},None]
        self.cons_column_data['Velar'] = [5,{'consonantal':'+','dorsal':'+','labial':'-'}, None]
        self.cons_column_data['Uvular'] = [6, {'consonantal':'+','dorsal':'+','back':'+','labial':'-'},None]
        self.cons_column_data['Glottal'] = [7,{'consonantal':'+','dorsal':'-','coronal':'-','labial':'-','nasal':'-'},None]

        self.cons_row_data = dict()
        self.cons_row_data['Stop'] = [0,{'consonantal':'+','sonorant':'-','continuant':'-','delayed_release':'-'}, None]
        self.cons_row_data['Nasal'] = [1,{'consonantal': '+', 'nasal': '+'}, None]
        self.cons_row_data['Trill'] = [2,{'consonantal': '+', 'trill': '+'}, None]
        self.cons_row_data['Tap'] = [3,{'consonantal': '+', 'tap': '+'}, None]
        self.cons_row_data['Fricative'] = [4,{'consonantal':'+','sonorant':'-','continuant':'+'},None]
        self.cons_row_data['Affricate'] = [5,{'consonantal':'+','continuant': '-','delayed_release': '+'}, None]
        self.cons_row_data['Approximant'] = [6, {'consonantal':'+','sonorant':'+','lateral':'-','nasal': '-'},None]
        self.cons_row_data['Lateral approximant'] = [7,{'consonantal':'+','sonorant':'+','lateral':'+'},None]

        self.vowel_column_data = dict()
        self.vowel_column_data['Front'] = [0, {'consonantal': '-', 'front': '+', 'back': '-'}, None]
        self.vowel_column_data['Central'] = [2, {'consonantal': '-', 'front': '-', 'back': '-'}, None]
        self.vowel_column_data['Back'] = [4, {'consonantal': '-', 'front': '-', 'back': '+'}, None]

        self.vowel_row_data = dict()
        self.vowel_row_data['High'] = [0, {'consonantal': '-', 'high': '+', 'low': '-'}, None]
        self.vowel_row_data['Mid'] = [1, {'consonantal': '-', 'high': '-', 'low': '-'}, None]
        self.vowel_row_data['Low'] = [3, {'consonantal': '-', 'high': '-', 'low': '+',}, None]

    def getSortedHeaders(self, orientation, cons_or_vowel):
        if orientation == Qt.Horizontal:
            if cons_or_vowel == 'cons':
                data = self.cons_column_header_order
            else:
                data = self.vowel_column_header_order
        elif orientation == Qt.Vertical:
            if cons_or_vowel == 'cons':
                data = self.cons_row_header_order
            else:
                data = self.vowel_row_header_order
        else:
            raise TypeError('The orientation value passed to Inventory.getHeaderOrder is not valid')

        return [data[header] for header in sorted(list(data.keys()))]

    def getColumnSpecs(self, name, consonants):
        if consonants:
            column_data = self.cons_column_data
        else:
            column_data = self.vowel_column_data
        return column_data[name]

    def getRowSpecs(self, name, consonants):
        if consonants:
            row_data = self.cons_row_data
        else:
            row_data = self.vowel_row_data
        return row_data[name]

    def getColumnHeader(self, index, consonants):
        if consonants:
            col_data = self.cons_column_data
            headers = self.consColumns
        else:
            col_data = self.vowel_column_data
            headers = self.vowelColumns
        sorted_headers = sorted(list(headers), key=lambda x: col_data[x][0])
        return sorted_headers[index]

    def getRowHeader(self, index, consonants):
        if consonants:
            row_data = self.cons_row_data
            headers = self.consRows
        else:
            row_data = self.vowel_row_data
            headers = self.vowelRows
        sorted_headers = sorted(list(headers), key=lambda x: row_data[x][0])
        return sorted_headers[index]

    def __getstate__(self):
        state = self.__dict__.copy()
        state.update(super().__dict__.copy())
        return state

    def __setstate__(self, state):
        if 'stresses' not in state:
            state['stresses'] = {}

        self.__dict__.update(state)

    def __repr__(self):
        return '\n'.join([','.join([str(item) for item in row]) for row in self._data])

    def __len__(self):
        return len(self.segs.keys())

    def keys(self):
        return self.segs.keys()

    def values(self):
        return self.segs.values()

    def items(self):
        return self.segs.items()

    def __getitem__(self, key):
        if isinstance(key, slice):
            return sorted(self.segs.keys())[key]
        return self.segs[key]

    def __setitem__(self, key, value):
        self.segs[key] = value

    def __iter__(self):
        for k in sorted(self.segs.keys()):
            yield self.segs[k]

    def __contains__(self, item):
        if isinstance(item, str):
            return item in self.segs.keys()
        elif isinstance(item, Segment):
            return item.symbol in self.segs.keys()
        return False

    def valid_feature_strings(self):
        strings = list()
        for v in self.possible_values:
            for f in self.features:
                strings.append(v + f)
        return strings

    def get_segs(self):
        return [v for v in self.segs.values() if not v in self.non_segment_symbols]

    def partition_by_feature(self, features, others=None):

        partitions = dict()
        for signs in itertools.product(self.possible_values, repeat=len(features)):
            partitions[signs] = list()

        for signs in partitions:
            matches = [s+f for (s,f) in zip(signs, features)]
            for symbol,seg in self.segs.items():
                if symbol in self.non_segment_symbols:
                    continue
                for match in matches:
                    if seg.features[match[1:]] == match[0]:
                        if not others:
                            partitions[signs].append(symbol)
                        else:
                            for other in others:
                                if seg.features[other[1:]] != other[0]:
                                    break
                            else:
                                partitions[signs].append(symbol)

        return {k:v for (k,v) in partitions.items() if v}


    def find_min_feature_pairs(self, features, others=None):
        """
        Find sets of segments that differ only in certain features,
        optionally limited by a feature specification

        Parameters
        ----------
        features : list
            List of features (i.e. 'back' or 'round')
        others : list, optional
            Feature specification to limit sets

        Returns
        -------
        dict
            Dictionary with keys that correspond to the values of ``features``
            and values that are the set of segments with those feature values
        """
        output = collections.defaultdict(list)
        redundant = self.get_redundant_features(features, others)
        for seg1, seg2 in itertools.combinations(self.get_segs(), 2):
            if not seg1.feature_match(others):
                continue
            if seg1.minimal_difference(seg2, features + redundant):
                break
            seg1_key = tuple(seg1[f] for f in features)
            seg2_key = tuple(seg2[f] for f in features)
            if seg1 not in output[seg1_key]: output[seg1_key].append(seg1)
            if seg2 not in output[seg2_key]: output[seg2_key].append(seg2)
        return output

    def get_redundant_features(self, features, others=None):
        """
        Autodetects redundent _features, with the ability to subset
        the segments

        Parameters
        ----------
        features : list
            List of features to find other features that consistently
            co-vary with them
        others : list, optional
            Feature specification that specifies a subset to look at

        Returns
        -------
        list
            List of redundant features
        """
        redundant_features = []
        if isinstance(features, str):
            features = [features]
        if others is None:
            others = []
        other_feature_names = [x[1:] for x in others]
        for f in self.features:
            if f in features:
                continue
            if f in other_feature_names:
                continue
            feature_values = collections.defaultdict(set)
            for seg in self:
                if others is not None:
                    if not seg.feature_match(others):
                        continue
                if seg == '#':
                    continue
                value = tuple(seg[x] for x in features)
                other_value = seg[f]
                feature_values[value].add(other_value)
                if any(len(x) > 1 for x in feature_values.values()):
                    break
            if any(len(x) > 1 for x in feature_values.values()):
                continue
            redundant_features.append(f)
        return redundant_features

    def get_consonants(self):
        return [seg for seg in self.get_segs() if self.isCons(seg)]

    def get_vowels(self):
        return [seg for seg in self.get_segs() if self.isVowel(seg)]


    def features_to_segments(self, feature_description):
        """
        Given a feature description, return the segments in the inventory
        that match that feature description

        Feature descriptions should be either lists, such as
        ['+feature1', '-feature2'] or strings that can be separated into
        lists by ',', such as '+feature1,-feature2'.

        Parameters
        ----------
        feature_description : string or list
            Feature values that specify the segments, see above for format

        Returns
        -------
        list of Segments
            Segments that match the feature description

        """
        segments = []
        if isinstance(feature_description, str):
            feature_description = feature_description.split(',')
        for k, v in self.segs.items():
            if v.feature_match(feature_description):
                segments.append(k)
        return segments

    def categorize(self, seg):
        if self.isVowel(seg):
            category = ['Vowel']
            iterRows = self.vowel_row_data
            iterCols = self.vowel_column_data
        elif self.isCons(seg):
            category = ['Consonant']
            iterRows = self.cons_row_data
            iterCols = self.cons_column_data
        else:
            raise KeyError #function is wrapped in a try/except which will catch this

        for row, col in itertools.product(iterRows, iterCols):
            row_index, row_features, row_segs = iterRows[row]
            col_index, col_features, col_segs = iterCols[col]

            if ((not row_features) or (not col_features)):
                continue #should ignore rows or cols without features - they will remain blank

            if ((row_segs is not None and seg in row_segs) and
                    (col_segs is not None and seg in col_segs)):
                category.extend([col, row])
                break
            elif (all(row_features[key] == seg.features[key] for key in row_features) and
                      all(col_features[key] == seg.features[key] for key in col_features)):
                category.extend([col, row])
                break

        else:
            raise KeyError(seg.symbol)  # this function is wrapped in a try/except that will catch this

        if self.isVowel(seg):
            if self.isRounded(seg):
                category.append('Rounded')
            else:
                category.append('Unrounded')

        else:
            if self.isVoiced(seg):
                category.append('Voiced')
            else:
                category.append('Voiceless')
        return category

class ConsonantModel(QSortFilterProxyModel):

    def __init__(self, inventory):
        super().__init__()
        self.setSourceModel(inventory)

    def getColumnHeader(self, index, consonants):
        return self.sourceModel().getColumnHeader(index, consonants=consonants)

    def getColumnSpecs(self, name, consonants):
        return self.sourceModel().getColumnSpecs(name, consonants=consonants)

    def getRowHeader(self, index, consonants):
        return self.sourceModel().getRowHeader(index, consonants=consonants)

    def getRowSpecs(self, name, consonants):
        return self.sourceModel().getRowSpecs(name, consonants=consonants)

    def features(self):
        return self.sourceModel().features

    def possible_values(self):
        return self.sourceModel().possible_values

    def insertRow(self, index):
        self.sourceModel().insertRow(index)

    def insertColumn(self, index):
        self.sourceModel().insertColumn(index)

    def removeColumn(self, index):
        self.sourceModel().removeColumn(index)

    def removeRow(self, index):
        self.sourceModel().removeRow(index)

    def rowCount(self, parent=None):
        return self.sourceModel().consRowCount()

    def columnCount(self, parent=None):
        return self.sourceModel().consColumnCount()

    def updateColumn(self, index, features):
        self.sourceModel().changeColumnSpecs(index, features)

    def filterAcceptsColumn(self, column, parent = None):
        header = self.sourceModel().headerData(column, Qt.Horizontal, Qt.DisplayRole)
        if header == QVariant():
            return False
        if header in self.sourceModel().consColumns:
            return True
        else:
            return False

    def filterAcceptsRow(self, row, parent = None):
        header = self.sourceModel().headerData(row, Qt.Vertical, Qt.DisplayRole)
        if header == QVariant():
            return False
        if header in self.sourceModel().consRows:
            return True
        else:
            return False

class UncategorizedModel(QAbstractTableModel):

    def __init__(self, inventory, col_max = 5):
        super().__init__()
        self.sourceInventory = inventory
        self.inventory = inventory._data[-1]
        self.non_segment_symbols = inventory.non_segment_symbols
        self._data = list()
        self.col_max = col_max
        self.organizeData()
        self.modelReset()

    def organizeData(self):
        info = self.sourceInventory._data[-1]
        info = [i for i in info if i is not None]
        info.sort()
        row = list()
        for row_num,i in enumerate(info):
            row.append(i)
            if len(row) == self.col_max:
                self._data.append(row)
                row = list()
        if row: #might be a leftover if len(row)<self.col_max on last loop
            while len(row) < self.col_max:
                row.append('')#make every row of equal length
            self._data.append(row)

    @Slot(bool)
    def modelReset(self):
        self.modelAboutToBeReset.emit()
        self._data = list()
        self.organizeData()
        self.endResetModel()

    def data(self, index, role=None):
        if not index.isValid():
            return QVariant()
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
        else:
            return QVariant()

    def getPartialCategorization(self, seg):

        if seg in self.sourceInventory.non_segment_symbols:
            windowTitle = 'Non-segment symbol'
            text= ('This is a non-segment symbol (probably a boundary symbol). As such, it has no phonological '
                           'features and cannot be sorted into a chart.')
        else:
            seg = self.sourceInventory.segs[seg]
            features = [value + key for (key, value) in seg.features.items()]
            features.sort(key=lambda x: x[1])
            features = '\n'.join(features)
            partials = self.sourceInventory.getPartialCategorization(seg)
            windowTitle = 'Feature matches'
            text = '{}\n\nThe segment /{}/ has these features:\n\n{}'.format(partials, seg.symbol, features)

        return windowTitle, text

    def features(self):
        return self.sourceInventory.features

    def possible_values(self):
        return self.sourceInventory.possible_values

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return self.col_max


class VowelModel(QSortFilterProxyModel):

    def __init__(self, inventory):
        super().__init__()
        self.setSourceModel(inventory)

    def features(self):
        return self.sourceModel().features

    def possible_values(self):
        return self.sourceModel().possible_values


    def getColumnHeader(self, index, consonants):
        return self.sourceModel().getColumnHeader(index, consonants=consonants)


    def getColumnSpecs(self, name, consonants):
        return self.sourceModel().getColumnSpecs(name, consonants=consonants)


    def getRowHeader(self, index, consonants):
        return self.sourceModel().getRowHeader(index, consonants=consonants)


    def getRowSpecs(self, name, consonants):
        return self.sourceModel().getRowSpecs(name, consonants=consonants)

    def insertRow(self, index):
        self.sourceModel().insertRow(index, consonants=False)

    def insertColumn(self,index):
        self.sourceModel().insertColumn(index, consonants=False)

    def removeRow(self, index):
        self.sourceModel().removeRow(index, consonants=False)

    def removeColumn(self, index):
        self.sourceModel().removeColumn(index, consonants=False)

    def rowCount(self, parent=None):
        return self.sourceModel().vowelRowCount()

    def columnCount(self, parent=None):
        return self.sourceModel().vowelColumnCount()

    def filterAcceptsColumn(self, column, parent = None):
        if column < self.sourceModel().vowel_column_offset:
            return False
        else:
            return True

    def filterAcceptsRow(self, row, parent = None):
        if row < self.sourceModel().vowel_row_offset:
            return False
        else:
            return True