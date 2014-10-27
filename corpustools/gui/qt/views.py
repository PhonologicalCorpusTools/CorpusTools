
from PyQt5.QtWidgets import QTableView, QAbstractItemView, QWidget, QHeaderView

class TableWidget(QTableView):
    def __init__(self,parent=None):
        super(TableWidget, self).__init__(parent=parent)

        self.verticalHeader().hide()

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        #self.setContextMenuPolicy(Qt.CustomContextMenu)
        #self.customContextMenuRequested.connect(self.popup)
        #header = self.horizontalHeader()
        #header.setContextMenuPolicy(Qt.CustomContextMenu)
        #header.customContextMenuRequested.connect( self.showHeaderMenu )
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

class ResultsWindow(QWidget):
    def __init__(self,title,parent=None):
        QWidget.__init__(self,parent)
        self.dataModel = None