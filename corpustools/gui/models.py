from .imports import *
from .widgets import *
from corpustools.exceptions import CorpusIntegrityError
import os
import random
import itertools
from math import ceil as ceiling

class BaseTableModel(QAbstractTableModel):
    columns = []
    rows = []
    allData = []

    def __init__(self, settings, parent = None):
        QAbstractTableModel.__init__(self, parent)
        self.settings = settings

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
        try:
            data = self.rows[row][col]
            if isinstance(data,float):
                data = str(round(data,self.settings['sigfigs']))
            elif isinstance(data,bool):
                if data:
                    data = 'Yes'
                else:
                    data = 'No'
            elif isinstance(data,list):
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
        self.beginInsertRows(QModelIndex(),self.rowCount(),self.rowCount())
        self.rows.append(row)
        self.endInsertRows()

    def addRows(self,rows):
        self.beginInsertRows(QModelIndex(),self.rowCount(),self.rowCount() + len(rows)-1)
        self.rows += rows
        self.endInsertRows()

    def removeRow(self,ind):
        self.beginRemoveRows(QModelIndex(),ind,ind)
        del self.rows[ind]
        self.endRemoveRows()

    def removeRows(self,inds):
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
        self.corpus = corpus

        self.columns = [x for x in self.corpus.attributes]

        self.rows = self.corpus.words

        self.allData = self.rows

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
        f = self.filters[index.row()]
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

        #self.sort(2,Qt.AscendingOrder)

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
            self.endRemoveColumns()

class SegmentPairModel(BaseTableModel):
    def __init__(self,parent = None):
        QAbstractTableModel.__init__(self,parent)

        self.columns = ['Segment 1', 'Segment 2', '']
        self.rows = list()

    def switchRow(self,row):
        seg1,seg2 = self.rows[row]

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
        self.rows = list()

class ResultsModel(BaseTableModel):
    def __init__(self, header, results, settings, parent=None):
        QAbstractTableModel.__init__(self,parent)
        self.settings = settings
        self.columns = header
        self.rows = results

class PhonoSearchResultsModel(BaseTableModel):
    def __init__(self, header, summary_header, results, settings, parent=None):
        QAbstractTableModel.__init__(self,parent)
        self.settings = settings
        self.header = header
        self.summary_header = summary_header
        self.columns = self.header

        self.rows = results
        self.allData = self.rows
        self.summarized = False

    def _summarize(self):
        typefreq = defaultdict(float)
        tokenfreq = defaultdict(float)
        for line in self.allData:
            segs = line[2]
            envs = line[3]
            for i,seg in enumerate(segs):
                segenv = seg,envs[i]
                typefreq[segenv] += 1
                tokenfreq[segenv] += line[0].frequency

        self.rows = list()
        for k,v in sorted(typefreq.items()):
            self.rows.append([k[0],k[1],v, tokenfreq[k]])
        self.columns = self.summary_header

    def setSummarized(self, b):
        if self.summarized == b:
            return
        self.summarized = b
        self.layoutAboutToBeChanged.emit()
        if self.summarized:
            self._summarize()
        else:
            self.rows = self.allData
            self.columns = self.header
        self.layoutChanged.emit()

    def addRows(self,rows):
        self.layoutAboutToBeChanged.emit()
        self.allData += rows
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

    def addFeature(self,feat, default):
        self.layoutAboutToBeChanged.emit()
        self.specifier.add_feature(feat,default=default)
        self.generateData()
        self.layoutChanged.emit()



class InventoryModel(QAbstractTableModel):
    """
    Contains information about the phonological inventory. The __init__ does not seed with any phonemes because these
    are inferred during corpus building when words are added.
    See corpustools.corpus.io.csv.load_corpus_csv()
    See also corpustools.corpus.classes.lexicon.Corpus.add_word()
    See also corpustools.corpus.classes.lexicon.Corpus.update_inventory()
    """

    def __init__(self, inventory):
        super().__init__()
        self.segs = inventory.segs
        self.features = inventory.features
        self.possible_values = inventory.possible_values
        self.classes = inventory.classes
        self.stresses = inventory.stresses
        self.cons_column_data = {}
        self.cons_row_data = {}
        self.vowel_column_data = {}
        self.vowel_row_data = {}
        self.uncategorized = list()
        self.generate_generic_names()
        self.initRowColNames()
        self.sortData()


    def columnCount(self, parent):
        return len(self._data[0]) #any element would do, they should all be the same length

    def rowCount(self, parent):
        return len(self._data)

    def consRowCount(self):
        return len(self.consRows)

    def consColumnCount(self):
        return len(self.consColumns)

    def vowelRowCount(self):
        return len(self.vowelRows)

    def vowelColumnCount(self):
        return len(self.vowelColumns)

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        segs = self._data[index.row()][index.column()]
        return segs

    def setData(self, index, value, role=None):
        if not index.isValid() or role != Qt.EditRole:
            return False
        self._data[index.row()][index.column()] = value #this probably won't work
        self.dataChanged.emit(index, index)
        return True

    def isVoiced(self, seg):
        return seg.features[self.voice_feature[1:]] == self.voice_feature[0]

    def isVowel(self, seg):
        return seg.features[self.vowel_feature[1:]] == self.vowel_feature[0]

    def isRounded(self, seg):
        return seg.features[self.rounded_feature[1:]] == self.rounded_feature[0]

    def initRowColNames(self):
        self.generate_generic_names()
        self.consColumns = set()
        self.consRows = set()
        self.vowelColumns = set()
        self.vowelRows = set()
        self.consList = []
        self.vowelList = []
        self.uncategorized = []

        for s in self.segs.values():
            if s.symbol == '#':
                continue #ignore the word boundary symbol
            try:
                c = self.categorize(s)
            except KeyError:
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

    def headerData(self, row_or_col, orientation, role=None):
        try:
            if orientation == Qt.Horizontal and role == Qt.DisplayRole:
                #return self.cons_column_data[row_or_col]
                return self.all_columns[row_or_col]
            elif orientation == Qt.Vertical and role == Qt.DisplayRole:
                #return self.cons_row_data[row_or_col]
                return self.all_rows[row_or_col]
        except KeyError:
            return QVariant()

    def generateSegmentButton(self,symbol):
        wid = SegmentButton(symbol)#This needs to be a SegmentButton for the i,j segment
        wid.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
        b = QGridLayout()
        b.setAlignment(Qt.AlignCenter)
        b.setContentsMargins(0, 0, 0, 0)
        b.setSpacing(0)
        l = QWidget()
        l.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
        lb = QVBoxLayout()
        lb.setAlignment(Qt.AlignCenter)
        lb.setContentsMargins(0, 0, 0, 0)
        lb.setSpacing(0)
        l.setLayout(lb)
        #l.hide()
        b.addWidget(l,0,0)#, alignment = Qt.AlignCenter)
        r = QWidget()
        r.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
        rb = QVBoxLayout()
        rb.setAlignment(Qt.AlignCenter)
        rb.setContentsMargins(0, 0, 0, 0)
        rb.setSpacing(0)
        r.setLayout(rb)
        #r.hide()
        b.addWidget(r,0,1)#, alignment = Qt.AlignCenter)
        wid.setLayout(b)
        wid.setCheckable(True)
        wid.setAutoExclusive(False)
        wid.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
        self.btnGroup.addButton(wid)
        return wid


    def insertRow(self, index, consonants=True):
        self.beginInsertRows(index, index.row(), index.row())
        if consonants:
            row_data = self.cons_row_data
            row_header_order = self.cons_row_header_order
            headers = self.consRows
            row_count = self.consRowCount()
            column_count = self.consColumnCount()
        else:
            row_data = self.vowel_row_data
            row_header_order = self.vowel_row_header_order
            headers = self.vowelRows
            row_count = self.vowelRowCount()
            column_count = self.vowelColumnCount()
        for row in row_data:
            if row_data[row][0] >= index.row():
                row_data[row][0] += 1

        row_data['Vikings'] = [index.row(), {'sonorant': '+'}, None]
        headers.add('Vikings')
        self.sortData()
        self.dataChanged.emit(self.createIndex(0,0), #topleft
                              self.createIndex(row_count,column_count))#bottom right
        self.endInsertRows()
        return True


    def changeColumnOrder(self, map, consonants=True):
        if consonants:
            column_data = self.cons_column_data
        else:
            column_data = self.vowel_column_data

        for visualIndex,headerName in map.values():
            column_data[headerName][0] = visualIndex

    def changeRowOrder(self, map, consonants=True):
        if consonants:
            row_data = self.cons_row_data
        else:
            row_data = self.vowel_row_data

        for visualIndex, headerName in map.values():
            row_data[headerName][0] = visualIndex

    def sortData(self):

        sorted_cons_col_headers = sorted(list(self.consColumns), key=lambda x: self.cons_column_data[x][0])
        sorted_cons_row_headers = sorted(list(self.consRows), key=lambda x: self.cons_row_data[x][0])
        sorted_vowel_col_headers = sorted(list(self.vowelColumns), key=lambda x: self.vowel_column_data[x][0])
        sorted_vowel_row_headers = sorted(list(self.vowelRows), key=lambda x: self.vowel_row_data[x][0])

        self.cons_column_header_order = {i: name for i, name in enumerate(sorted_cons_col_headers)}
        self.vowel_column_offset = len(self.cons_column_header_order)
        self.vowel_column_header_order = {i+self.vowel_column_offset: name for i, name in enumerate(sorted_vowel_col_headers)}
        self.cons_row_header_order = {i: name for i, name in enumerate(sorted_cons_row_headers)}
        self.vowel_row_offset = len(self.cons_row_header_order)
        self.vowel_row_header_order = {i+self.vowel_row_offset: name for i, name in enumerate(sorted_vowel_row_headers)}

        print(sorted_vowel_row_headers)
        print(self.vowel_row_header_order)
        for key,value in self.vowel_row_data.items():
            print(key, value)

        self.all_columns = {}
        self.all_rows = {}
        self.all_columns.update(self.cons_column_header_order)
        self.all_columns.update(self.vowel_column_header_order)
        self.all_rows.update(self.cons_row_header_order)
        self.all_rows.update(self.vowel_row_header_order)
        col_total = len(self.all_columns)
        row_total = len(self.all_rows)

        self._data = [[None for j in range(col_total)]
                            for k in range(row_total)]

        for row, col in itertools.product(self.cons_row_header_order.keys(), self.cons_column_header_order.keys()):
            row_name = self.cons_row_header_order[row]
            col_name = self.cons_column_header_order[col]
            matches = list()
            for seg, cat in self.consList:
                if row_name in cat and col_name in cat:
                    matches.append(seg)
            self._data[row][col] = ''.join([m.symbol for m in matches])

        for row, col in itertools.product(self.vowel_row_header_order.keys(), self.vowel_column_header_order.keys()):
            row_name = self.vowel_row_header_order[row]
            col_name = self.vowel_column_header_order[col]
            matches = list()
            for seg, cat in self.vowelList:
                if row_name in cat and col_name in cat:
                    matches.append(seg)
            self._data[row][col] = ''.join([m.symbol for m in matches])

    def generate_generic_names(self):
        sample = random.choice(list(self.segs.values()))  # pick an arbitrary segment and examine its features
        if not sample:
            raise CorpusIntegrityError('No segments were found in the inventory')
        if 'consonantal' in sample.features:
            self.generate_generic_hayes()
            self.vowel_feature = '-consonantal'
            self.voice_feature = '+voice'
            self.rounded_feature = '+round'
        elif 'voc' in sample.features:
            self.generate_generic_spe()
            self.vowel_feature = '+voc'
            self.voice_feature = '+voice'
            self.rounded_feature = '+round'
        else:
            pass

    def generate_generic_spe(self):
        pass

    def generate_generic_hayes(self):
        self.cons_column_data['Labial'] = [0, {'consonantal': '+', 'labial': '+', 'coronal': '-'}, None]
        self.cons_column_data['Labiodental'] = [1, {'consonantal': '+', 'labiodental': '+'}, None]
        self.cons_column_data['Dental'] = [2, {'consonantal': '+', 'anterior': '+', 'coronal': '+', 'labial': '-'},
                                       None]
        self.cons_column_data['Alveopalatal'] = [3, {'consonantal': '+', 'anterior': '-', 'coronal': '+',
                                                 'labial': '-'}, None]
        self.cons_column_data['Palatal'] = [4, {'consonantal': '+', 'dorsal': '+', 'coronal': '+', 'labial': '-'},
                                        None]
        self.cons_column_data['Velar'] = [5, {'consonantal': '+', 'dorsal': '+', 'labial': '-'}, None]
        self.cons_column_data['Uvular'] = [6, {'consonantal': '+', 'dorsal': '+', 'back': '+', 'labial': '-'}, None]
        self.cons_column_data['Glottal'] = [7, {'consonantal': '+', 'dorsal': '-', 'coronal': '-', 'labial': '-',
                                            'nasal': '-'}, None]

        self.cons_row_data['Stop'] = [0, {'consonantal': '+', 'sonorant': '-', 'continuant': '-', 'nasal': '-',
                                      'delayed_release': '-'}, None]
        self.cons_row_data['Nasal'] = [1, {'consonantal': '+', 'nasal': '+'}, None]
        self.cons_row_data['Trill'] = [2, {'consonantal': '+', 'trill': '+'}, None]
        self.cons_row_data['Tap'] = [3, {'consonantal': '+', 'tap': '+'}, None]
        self.cons_row_data['Fricative'] = [4, {'consonantal': '+', 'sonorant': '-', 'continuant': '+'}, None]
        self.cons_row_data['Affricate'] = [5, {'consonantal': '+', 'sonorant': '-', 'continuant': '-',
                                           'delayed_release': '+'}, None]
        self.cons_row_data['Approximant'] = [6, {'consonantal': '+', 'sonorant': '+', 'lateral': '-'}, None]
        self.cons_row_data['Lateral approximant'] = [7, {'consonantal': '+', 'sonorant': '+', 'lateral': '+'}, None]

        self.vowel_column_data['Front'] = [0, {'consonantal': '-', 'front': '+', 'back': '-', 'tense': '+'}, None]
        self.vowel_column_data['Near-front'] = [1, {'consonantal': '-', 'front': '+', 'back': '-', 'tense': '-'},
                                          None]
        self.vowel_column_data['Central'] = [2, {'consonantal': '-', 'front': '-', 'back': '-'}, None]
        self.vowel_column_data['Near-back'] = [3, {'consonantal': '-', 'front': '-', 'back': '-', 'tense': '-'}, None]
        self.vowel_column_data['Back'] = [4, {'consonantal': '-', 'front': '-', 'back': '+', 'tense': '+'}, None]

        self.vowel_row_data['High'] = [0, {'consonantal': '-', 'high': '+', 'low': '-', 'tense': '+'}, None]
        self.vowel_row_data['Mid-high'] = [1, {'consonantal': '-', 'high': '-', 'low': '-', 'tense': '+'}, None]
        self.vowel_row_data['Mid-low'] = [2, {'consonantal': '-', 'high': '-', 'low': '-', 'tense': '-'}, None]
        self.vowel_row_data['Low'] = [3, {'consonantal': '-', 'high': '-', 'low': '+', 'tense': '+'}, None]

    def __getstate__(self):
        state = self.__dict__.copy()
        state.update(super().__dict__.copy())
        return state

    def __setstate__(self, state):
        if 'stresses' not in state:
            state['stresses'] = {}
        self.__dict__.update(state)

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
        else:
            category = ['Consonant']
            iterRows = self.cons_row_data
            iterCols = self.cons_column_data

        for row, col in itertools.product(iterRows, iterCols):
            row_index, row_features, row_segs = iterRows[row]
            col_index, col_features, col_segs = iterCols[col]

            if ((row_segs is not None and seg in row_segs) and
                    (col_segs is not None and seg in col_segs)):
                category.extend([col, row])
                break
            elif (all(row_features[key] == seg.features[key] for key in row_features) and
                      all(col_features[key] == seg.features[key] for key in col_features)):
                category.extend([col, row])
                break
        else:
            raise KeyError(seg.symbol) #this function is wrapped in a try/except that will catch this

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

class InventoryDelegate(QItemDelegate):

    def __init__(self):
        super().__init__()

    def setEditor(self, editor, index):
        editor.setValue(index.model().data(index, Qt.EditRole))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.value(), Qt.EditRole)

class ConsonantModel(QSortFilterProxyModel):

    def __init__(self, inventory):
        super().__init__()
        self.setSourceModel(inventory)

    def insertRow(self, index):
        self.sourceModel().insertRow(index)

    def rowCount(self, parent=None):
        return self.sourceModel().consRowCount()

    def columnCount(self, parent=None):
        return self.sourceModel().consColumnCount()

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

class VowelModel(QSortFilterProxyModel):

    def __init__(self, inventory):
        super().__init__()
        self.setSourceModel(inventory)

    def insertRow(self, index):
        self.sourceModel().insertRow(index, consonants=False)

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


