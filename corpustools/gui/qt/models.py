
from PyQt5.QtCore import QAbstractTableModel, Qt

class CorpusModel(QAbstractTableModel):
    def __init__(self, corpus, parent=None):
        super(CorpusModel, self).__init__(parent = parent)

        self.corpus = corpus

        self.columns = self.corpus.attributes

        self.rows = self.corpus.words

    def rowCount(self,parent=None):
        return len(self.rows)

    def columnCount(self,parent=None):
        return len(self.columns)

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

    def flags(self, index):
        if not index.isValid():
            return
        return Qt.ItemIsSelectable|Qt.ItemIsEnabled|Qt.ItemIsUserCheckable

    def setData(self, index, value, role):
        if not index.isValid() or role!=Qt.CheckStateRole:
            return False
        self._checked[index.row()][index.column()]=value
        self.dataChanged.emit(index, index)
        return True
