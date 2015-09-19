import os

from .imports import *

# from .views import TableWidget, SubTreeView
#
# from .models import FeatureSystemTableModel, FeatureSystemTreeModel
#
# from .widgets import InventoryTable, InventoryBox
#
# from .helpgui import HelpDialog



class InventoryManager(QDialog):
    def __init__(self, parent, corpus):
        super().__init__()
        self.corpus = corpus
        layout = QVBoxLayout()

        topmessage = QLabel(text=('You can edit your inventory chart from this window. Double-click on a row or column to edit the '
                      'class of segments which appear in that row or column. You can also single click on a heading to '
                      'highlight the row or column, then drag-and-drop to reorganize the table.'))
        topmessage.setWordWrap(True)
        layout.addWidget(topmessage)

        self.segSelectWidget = InventoryTable2(self, self.corpus.inventory, editable=True)
        segLayout = QVBoxLayout()
        segLayout.addWidget(self.segSelectWidget)
        layout.addLayout(segLayout)

        buttonLayout = QHBoxLayout()
        # add = QPushButton('Add row or column')
        # add.clicked.connect(self.addToTable)
        # remove = QPushButton('Remove row or column')
        # remove.clicked.connect(self.removeFromTable)
        # reorder = QPushButton('Reorder rows or columns')
        # reorder.clicked.connect(self.reorderTable)
        ok_button = QPushButton('OK')
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)

        # buttonLayout.addWidget(add)
        # buttonLayout.addWidget(remove)
        #buttonLayout.addWidget(reorder)
        buttonLayout.addWidget(ok_button)
        buttonLayout.addWidget(cancel_button)

        layout.addLayout(buttonLayout)

        self.setLayout(layout)


    def addToTable(self):
        print('adding')

    def removeFromTable(self):
        print('removing')

    def reorderTable(self):
        print('reordering')

class InventoryTable2(QTableView):

    def __init__(self, parent, inventory, editable):
        super().__init__(parent)
        super(QAbstractTableModel, inventory).__init__(parent)
        #this super() is also called in the __init__ of Inventory, but for some reason must be called a second time here
        #if you comment out the line above, then it raises RuntimeError: super() of Inventory was never called
        self.setModel(inventory)
        self.model().setRowColNames()
        self.horizontalHeader().show()
        # hh = QHeaderView(1, self)
        # hh.setModel(inventory)
        # hh.initialize()
        # self.setHorizontalHeader(hh)
        # self.setVerticalHeader(QHeaderView(2, self))
        # self.verticalHeader().setVisible(True)
        # self.verticalHeader().show()
        # self.horizontalHeader().setVisible(True)
        # self.horizontalHeader().show()
        self.inventory = inventory
        self.editable = editable
        # try:
        #     self.horizontalHeader().setSectionsClickable(True)
        #     #self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        #     self.verticalHeader().setSectionsClickable(True)
        #     #self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        # except AttributeError:
        #     self.horizontalHeader().setClickable(True)
        #     #self.horizontalHeader().setResizeMode(QHeaderView.Fixed)
        #     self.verticalHeader().setClickable(True)
        #     #self.verticalHeader().setResizeMode(QHeaderView.Fixed)
        #
        # #self.setSelectionMode(QAbstractItemView.NoSelection)
        # #self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # #self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)


    def resize(self):
        self.resizeRowsToContents()
        #self.resizeColumnsToContents()
        hor = self.horizontalHeader()
        ver = self.verticalHeader()
        width = ver.sizeHint().width()
        for i in range(hor.count()):
            width += hor.sectionSize(i)
        height = hor.sizeHint().height()
        for i in range(ver.count()):
            height += ver.sectionSize(i)
        self.setFixedSize(width, height)

    def showHorizontalHeaderMenu(self, pos):
        header = self.horizontalHeader()
        col = header.logicalIndexAt(pos.x())

        deleteColAct = QAction(self)
        deleteColAct.setText("Remove column")
        deleteColAct.triggered.connect(lambda : self.userRemoveColumn(col))
        addColAct = QAction(self)
        addColAct.setText("Add column")
        addColAct.triggered.connect(self.userAddColumn)

        menu = QMenu(self)
        #menu.addAction(editAction)
        menu.addAction(addColAct)
        menu.addAction(deleteColAct)

        menu.popup(header.mapToGlobal(pos))

    def showVerticalHeaderMenu(self, pos):
        header = self.verticalHeader()
        row = header.logicalIndexAt(pos.y())

        deleteRowAct = QAction(self)
        deleteRowAct.setText("Remove row")
        deleteRowAct.triggered.connect(lambda row: self.userRemoveRow(row))
        addRowAct = QAction(self)
        addRowAct.setText("Add row")
        addRowAct.triggered.connect(self.userAddRow)

        menu = QMenu(self)
        menu.addAction(deleteRowAct)
        menu.addAction(addRowAct)

        menu.popup(header.mapToGlobal(pos))