
from PyQt5.QtCore import QAbstractTableModel, Qt, QSize

class CorpusModel(QAbstractTableModel):
    def __init__(self, corpus, parent=None):
        super(CorpusModel, self).__init__(parent)

        self.corpus = corpus

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

    def addTier(self,tierName, featureList):
        self.layoutAboutToBeChanged.emit()
        self.corpus.add_tier(tierName, featureList)
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
    def __init__(self, header, data, parent=None):
        QAbstractTableModel.__init__(self,parent)

        self.columns = header

        self.data = data

    def rowCount(self,parent=None):
        return len(self.data)

    def columnCount(self,parent=None):
        return len(self.columns)

    def data(self, index, role=None):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        data = self.data[index.row()][index.column()]
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
        self.data = sorted(self.data, key=lambda x: x[col])
        if order == Qt.DescendingOrder:
            self.data.reverse()
        self.layoutChanged.emit()

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns[col]
        #elif role == Qt.SizeHintRole:
        #    return QSize(100,23)
        return QAbstractTableModel.headerData(self, col, orientation, role)


    def addData(self,extra):
        self.layoutAboutToBeChanged.emit()
        self.data += extra
        self.layoutChanged.emit()


class FeatureSystemModel(QAbstractTableModel):
    def __init__(self, specifier, parent=None):
        QAbstractTableModel.__init__(self,parent)
        self.specifier = specifier
        self.generateData()


    def rowCount(self,parent=None):
        return len(self.data)

    def columnCount(self,parent=None):
        return len(self.columns)

    def data(self, index, role=None):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.data[index.row()][index.column()]

    def sort(self, col, order):
        """Sort table by given column number.
        """
        self.layoutAboutToBeChanged.emit()
        self.data = sorted(self.data, key=lambda x: x[col])
        if order == Qt.DescendingOrder:
            self.data.reverse()
        self.layoutChanged.emit()

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns[col]
        return QAbstractTableModel.headerData(self, col, orientation, role)

    def filter(self,segments):
        self.layoutAboutToBeChanged.emit()
        self.data = [x for x in self.alldata if x[0] in segments]
        self.layoutChanged.emit()

    def showAll(self):
        self.layoutAboutToBeChanged.emit()
        self.data = self.alldata
        self.layoutChanged.emit()

    def generateData(self):
        self.data = list()
        self.columns = ['symbol']
        if self.specifier is None:
            return
        self.columns += self.specifier.features
        for x in self.specifier.segments:
            if x in ['','#']:
                continue
            self.data.append([x]+[self.specifier[x,y] for y in self.specifier.features])
        self.alldata = self.data

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
