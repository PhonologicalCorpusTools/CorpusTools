
import csv

from PyQt5.QtWidgets import (QTableView, QAbstractItemView, QWidget,
                            QHeaderView, QDockWidget, QPushButton,
                            QVBoxLayout, QFileDialog, QFrame)

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
        #self.horizontalHeader().setMinimumSectionSize(100)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

class ResultsWindow(QWidget):
    def __init__(self, title, dataModel, parent=None):
        QWidget.__init__(self)#, parent)

        layout = QVBoxLayout()
        self.table = TableWidget()
        self.table.setModel(dataModel)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.table)

        self.saveButton = QPushButton('Save to file')
        self.saveButton.clicked.connect(self.save)
        layout.addWidget(self.saveButton)
        #frame = QFrame()
        self.setLayout(layout)
        #self.setWidget(frame)
        self.table.resizeColumnsToContents()
        self.setWindowTitle(title)

    def save(self):
        filename = QFileDialog.getSaveFileName(self,'Choose save file',
                        filter = 'Text files (*.txt *.csv)')
        if filename:

            with open(filename[0], mode='w', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerow(self.table.model().columns)
                for row in self.table.model().data:
                    writer.writerow(row)
