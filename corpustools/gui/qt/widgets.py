
from itertools import combinations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDialog, QListWidget, QGroupBox, QHBoxLayout,
                            QVBoxLayout, QPushButton, QFrame, QGridLayout,
                            QRadioButton, QLabel, QFormLayout, QLineEdit,
                            QFileDialog, QComboBox, QSizePolicy, QButtonGroup,
                            QGridLayout, QTableWidget, QWidget, QAbstractItemView,
                            QHeaderView)

from .views import TableWidget

from .models import SegmentPairModel, EnvironmentModel

class FileWidget(QFrame):
    def __init__(self,title,filefilter,parent=None):
        QFrame.__init__(self,parent)

        self.title = title

        self.filefilter = filefilter

        pathLayout = QHBoxLayout()
        self.pathEdit = QLineEdit()
        pathButton = QPushButton('Choose file...')
        pathButton.clicked.connect(self.pathSet)
        pathLayout.addWidget(self.pathEdit)
        pathLayout.addWidget(pathButton)
        self.setLayout(pathLayout)

        self.textChanged = self.pathEdit.textChanged

    def pathSet(self):
        filename = QFileDialog.getOpenFileName(self,self.title, filter=self.filefilter)
        if filename:
            self.pathEdit.setText(filename[0])

    def value(self):
        return self.pathEdit.text()

class SaveFileWidget(QFrame):
    def __init__(self,title,filefilter,parent=None):
        QFrame.__init__(self,parent)

        self.title = title

        self.filefilter = filefilter

        pathLayout = QHBoxLayout()
        self.pathEdit = QLineEdit()
        pathButton = QPushButton('Choose file...')
        pathButton.clicked.connect(self.pathSet)
        pathLayout.addWidget(self.pathEdit)
        pathLayout.addWidget(pathButton)
        self.setLayout(pathLayout)

        self.textChanged = self.pathEdit.textChanged

    def pathSet(self):
        filename = QFileDialog.getSaveFileName(self,self.title, filter=self.filefilter)
        if filename:
            self.pathEdit.setText(filename[0])

    def value(self):
        return self.pathEdit.text()

class DirectoryWidget(QFrame):
    def __init__(self,parent=None):
        QFrame.__init__(self,parent)

        pathLayout = QHBoxLayout()
        self.pathEdit = QLineEdit()
        pathButton = QPushButton('Choose directory...')
        pathButton.clicked.connect(self.pathSet)
        pathLayout.addWidget(self.pathEdit)
        pathLayout.addWidget(pathButton)
        self.setLayout(pathLayout)

    def pathSet(self):
        filename = QFileDialog.getExistingDirectory(self,"Choose a directory")
        if filename:
            self.pathEdit.setText(filename)

    def value(self):
        return self.pathEdit.text()

class InventoryBox(QGroupBox):
    consonantColumns = ['Labial','Labiodental','Dental','Alveolar','Alveopalatal','Retroflex',
                    'Palatal','Velar','Uvular','Pharyngeal','Epiglottal','Glottal']

    consonantRows = ['Stop','Nasal','Fricative','Affricate','Approximate','Trill','Tap',
                    'Lateral fricative','Lateral approximate','Lateral flap']

    vowelColumns = ['Front','Near front','Central','Near back','Back']

    vowelRows = ['Close','Near close','Close mid','Mid','Open mid','Near open','Open']

    def __init__(self, title,inventory,parent=None):
        QGroupBox.__init__(self,title,parent)

        self.inventory = inventory
        #find cats
        consColumns = set()
        consRows = set()
        vowColumns = set()
        vowRows = set()
        for s in self.inventory:
            c = s.category
            if c is not None:
                if c[0] == 'Vowel':
                    vowColumns.add(c[2])
                    vowRows.add(c[1])
                elif c[0] == 'Consonant':
                    consColumns.add(c[1])
                    consRows.add(c[2])

        self.btnGroup = QButtonGroup()
        self.btnGroup.setExclusive(False)
        if len(consColumns) and len(vowColumns):
            box = QVBoxLayout()
            smallbox = QHBoxLayout()
            cons = QGroupBox('Consonants')
            consBox = QVBoxLayout()
            consTable = QTableWidget()
            consBox.addWidget(consTable)
            cons.setLayout(consBox)

            consColumns = [ x for x in self.consonantColumns if x in consColumns]
            consColMapping = {x:i for i,x in enumerate(consColumns)}
            consRows = [ x for x in self.consonantRows if x in consRows]
            consRowMapping = {x:i for i,x in enumerate(consRows)}

            consTable.setColumnCount(len(consColumns))
            consTable.setRowCount(len(consRows))
            consTable.setHorizontalHeaderLabels(consColumns)
            consTable.setVerticalHeaderLabels(consRows)
            consTable.resizeRowsToContents()
            consTable.resizeColumnsToContents()
            consTable.setSelectionMode(QAbstractItemView.NoSelection)
            consTable.horizontalHeader().setSectionsClickable(False)
            #consTable.horizontalHeader().resizeSections()
            consTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

            consTable.verticalHeader().setSectionsClickable(False)
            #consTable.verticalHeader().resizeSections()
            consTable.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)


            for i in range(len(consColumns)):
                for j in range(len(consRows)):
                    wid = QWidget()
                    b = QGridLayout()
                    b.setAlignment(Qt.AlignCenter);
                    b.setContentsMargins(0, 0, 0, 0);
                    wid.setLayout(b)
                    consTable.setCellWidget(j,i,wid)

            vow = QGroupBox('Vowels')
            vowBox = QGridLayout()
            vowBox.setAlignment(Qt.AlignTop)
            vowTable = QTableWidget()
            vowBox.addWidget(vowTable)
            vow.setLayout(vowBox)
            vowColumns = [ x for x in self.vowelColumns if x in vowColumns]
            vowColMapping = {x:i for i,x in enumerate(vowColumns)}
            vowRows = [ x for x in self.vowelRows if x in vowRows]
            vowRowMapping = {x:i for i,x in enumerate(vowRows)}

            vowTable.setColumnCount(len(vowColumns))
            vowTable.setRowCount(len(vowRows) + 1)
            vowTable.setHorizontalHeaderLabels(vowColumns)
            vowTable.setVerticalHeaderLabels(vowRows + ['Diphthongs'])
            vowTable.resizeRowsToContents()
            vowTable.resizeColumnsToContents()
            vowTable.setSelectionMode(QAbstractItemView.NoSelection)
            vowTable.horizontalHeader().setSectionsClickable(False)
            #vowTable.horizontalHeader().resizeSections()
            vowTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

            vowTable.verticalHeader().setSectionsClickable(False)
            #vowTable.verticalHeader().resizeSections()
            vowTable.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

            for i in range(len(vowColumns)):
                for j in range(len(vowRows)):
                    wid = QWidget()
                    b = QGridLayout()
                    b.setAlignment(Qt.AlignCenter)
                    b.setContentsMargins(0, 0, 0, 0)
                    wid.setLayout(b)
                    vowTable.setCellWidget(j,i,wid)

            vowTable.setSpan(len(vowRows),0,1,len(vowColumns))
            wid = QWidget()
            diphBox = QHBoxLayout()
            diphBox.setAlignment(Qt.AlignCenter)
            diphBox.setContentsMargins(0, 0, 0, 0)
            wid.setLayout(diphBox)
            vowTable.setCellWidget(len(vowRows),0,wid)

            unk = QGroupBox('Other')
            unkBox = QGridLayout()
            unk.setLayout(unkBox)

            unkRow = 0
            unkCol = -1
            for s in inventory:
                cat = s.category
                btn = QPushButton(s.symbol)
                btn.setCheckable(True)
                btn.setAutoExclusive(False)
                btn.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
                #btn.setMaximumWidth(btn.fontMetrics().boundingRect(s.symbol).width() + 14)
                self.btnGroup.addButton(btn)
                if cat is None:
                    unkCol += 1
                    if unkCol > 11:
                        unkCol = 0
                        unkRow += 1
                    unkBox.addWidget(btn,unkRow,unkCol)

                elif cat[0] == 'Vowel':
                    col = vowColMapping[cat[2]]
                    row = vowRowMapping[cat[1]]
                    if cat[3] == 'Unrounded':
                        colTwo = 0
                    else:
                        colTwo = 1
                    cell = vowTable.cellWidget(row,col)

                    cell.layout().addWidget(btn,0,colTwo)
                elif cat[0] == 'Consonant':
                    col = consColMapping[cat[1]]
                    row = consRowMapping[cat[2]]
                    if cat[3] == 'Voiceless':
                        colTwo = 0
                    else:
                        colTwo = 1
                    cell = consTable.cellWidget(row,col)
                    cell.layout().addWidget(btn,0,colTwo)
                elif cat[0] == 'Diphthong':
                    diphBox.addWidget(btn)
            smallbox.addWidget(cons)

            smallbox.addWidget(vow)
            b = QFrame()
            b.setLayout(smallbox)
            box.addWidget(b)
            box.addWidget(unk)
        else:
            box = QGridLayout()

            row = 0
            col = 0
            for s in inventory:
                btn = QPushButton(s.symbol)
                btn.setCheckable(True)
                btn.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
                btn.setMaximumWidth(btn.fontMetrics().boundingRect(s.symbol).width() + 14)

                box.addWidget(btn,row,col)
                self.btnGroup.addButton(btn)
                col += 1
                if col > 11:
                    col = 0
                    row += 1

        self.setLayout(box)

    def value(self):
        if self.btnGroup.exclusive():
            checked = self.btnGroup.checkedButton()
            if checked is None:
                return ''
            return checked.text()
        else:
            value = []
            for b in self.btnGroup.buttons():
                if b.isChecked():
                    value.append(b.text())
            return value

class FeatureBox(QGroupBox):
    def __init__(self, title,features,parent=None):
        QGroupBox.__init__(self,title,parent)


        layout = QHBoxLayout()
        self.features = features

        self.featureList = QListWidget()

        for f in self.features:
            self.featureList.addItem(f)
        layout.addWidget(self.featureList)

        buttonLayout = QVBoxLayout()
        self.plusButton = QPushButton('Add [+feature]')
        self.minusButton = QPushButton('Add [-feature]')
        self.clearButton = QPushButton('Clear all')

        self.plusButton.clicked.connect(self.addPlus)
        self.minusButton.clicked.connect(self.addMinus)
        self.clearButton.clicked.connect(self.clearAll)

        buttonLayout.addWidget(self.plusButton)
        buttonLayout.addWidget(self.minusButton)
        buttonLayout.addWidget(self.clearButton)

        buttonFrame = QFrame()
        buttonFrame.setLayout(buttonLayout)
        layout.addWidget(buttonFrame)

        self.envList = QListWidget()

        layout.addWidget(self.envList)

        self.setLayout(layout)

    def addPlus(self):
        curFeature = self.featureList.currentItem()
        if curFeature:
            self.envList.addItem('+'+curFeature.text())

    def addMinus(self):
        curFeature = self.featureList.currentItem()
        if curFeature:
            self.envList.addItem('-'+curFeature.text())

    def clearAll(self):
        self.envList.clear()

    def value(self):
        return [self.envList.itemAt(i,0).text() for i in range(self.envList.count())]


class SegmentPairDialog(QDialog):
    def __init__(self, inventory,parent=None):
        QDialog.__init__(self,parent)

        layout = QVBoxLayout()

        segFrame = QFrame()

        segLayout = QHBoxLayout()

        self.segFrame = InventoryBox('Segments',inventory)

        segLayout.addWidget(self.segFrame)

        segFrame.setLayout(segLayout)

        layout.addWidget(segFrame)

        self.acceptButton = QPushButton('Ok')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.cancelButton)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Select segment pair')

    def accept(self):
        selected = self.segFrame.value()
        self.pairs = combinations(selected,2)
        QDialog.accept(self)


class SegmentPairSelectWidget(QGroupBox):
    def __init__(self,inventory,parent=None):
        QGroupBox.__init__(self,'Segments',parent)

        self.inventory = inventory

        vbox = QVBoxLayout()

        self.addButton = QPushButton('Add pair of sounds')
        self.addButton.clicked.connect(self.segPairPopup)
        self.removeButton = QPushButton('Remove selected sound pair')
        self.removeButton.clicked.connect(self.removePair)

        self.table = TableWidget()
        self.table.setModel(SegmentPairModel())

        vbox.addWidget(self.addButton)
        vbox.addWidget(self.removeButton)
        vbox.addWidget(self.table)
        self.setLayout(vbox)

    def segPairPopup(self):
        dialog = SegmentPairDialog(self.inventory)
        result = dialog.exec_()
        if result:
            for p in dialog.pairs:
                self.table.model().addRow(p)

    def removePair(self):
        select = self.table.selectionModel()
        if select.hasSelection():
            selected = [s.row() for s in select.selectedRows()]
            self.table.model().removeRows(selected)

    def value(self):
        return self.table.model().pairs

class EnvironmentDialog(QDialog):
    def __init__(self, inventory,parent=None):
        QDialog.__init__(self,parent)

        self.inventory = inventory
        self.features = inventory[-1].features.keys()

        layout = QVBoxLayout()

        self.envType = QComboBox()
        self.envType.addItem('Segments')
        if len(self.features) > 0:
            self.envType.addItem('Features')
        else:
            layout.addWidget(QLabel('Features for environment selection are not available without a feature system.'))

        self.envType.currentIndexChanged.connect(self.generateFrames)

        layout.addWidget(QLabel('Basis for building environment:'))
        layout.addWidget(self.envType)

        self.lhs = InventoryBox('Left hand side',self.inventory)

        self.rhs = InventoryBox('Right hand side',self.inventory)

        self.envFrame = QFrame()

        self.envLayout = QHBoxLayout()

        self.envLayout.addWidget(self.lhs)
        self.envLayout.addWidget(self.rhs)

        self.envFrame.setLayout(self.envLayout)

        layout.addWidget(self.envFrame)

        self.oneButton = QPushButton('Add')
        self.anotherButton = QPushButton('Add and create another')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.oneButton)
        acLayout.addWidget(self.anotherButton)
        acLayout.addWidget(self.cancelButton)
        self.oneButton.clicked.connect(self.one)
        self.anotherButton.clicked.connect(self.another)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Create environment')


    def createFeatureFrame(self):
        self.lhs.deleteLater()
        self.rhs.deleteLater()

        self.lhs = FeatureBox('Left hand side',self.features)
        self.envLayout.addWidget(self.lhs)

        self.rhs = FeatureBox('Right hand side',self.features)
        self.envLayout.addWidget(self.rhs)

    def createSegmentFrame(self):
        self.lhs.deleteLater()
        self.rhs.deleteLater()
        self.lhs = InventoryBox('Left hand side',self.inventory)
        self.envLayout.addWidget(self.lhs)

        self.rhs = InventoryBox('Right hand side',self.inventory)
        self.envLayout.addWidget(self.rhs)

    def generateFrames(self,ind=0):
        if self.envType.currentText() == 'Segments':
            self.createSegmentFrame()
        elif self.envType.currentText() == 'Features':
            self.createFeatureFrame()

    def one(self):
        self.addOneMore = False
        self.accept()

    def another(self):
        self.addOneMore = True
        self.accept()

    def accept(self):

        self.env = '{}_{}'.format(self.lhs.value(),self.rhs.value())
        QDialog.accept(self)

    def reject(self):
        self.addOneMore = False
        QDialog.reject(self)

class EnvironmentSelectWidget(QGroupBox):
    def __init__(self,inventory,parent=None):
        QGroupBox.__init__(self,'Environments',parent)

        self.inventory = inventory

        vbox = QVBoxLayout()

        self.addButton = QPushButton('Add environment')
        self.addButton.clicked.connect(self.envPopup)
        self.removeButton = QPushButton('Remove selected environments')
        self.removeButton.clicked.connect(self.removeEnv)

        self.table = TableWidget()
        self.table.setModel(EnvironmentModel())

        vbox.addWidget(self.addButton)
        vbox.addWidget(self.removeButton)
        vbox.addWidget(self.table)

        self.setLayout(vbox)

    def envPopup(self):
        dialog = EnvironmentDialog(self.inventory)
        addOneMore = True
        while addOneMore:
            result = dialog.exec_()
            if result:
                self.table.model().addRow([dialog.env])
            addOneMore = dialog.addOneMore

    def removeEnv(self):
        select = self.table.selectionModel()
        if select.hasSelection():
            selected = select.selectedRows()
            for s in selected:
                self.table.model().removeRow(s.row())

    def value(self):
        return [x[0] for x in self.table.model().environments]

class RadioSelectWidget(QGroupBox):
    def __init__(self,title,options, actions=None, enabled=None,parent=None):
        QGroupBox.__init__(self,title,parent)

        self.options = options
        vbox = QVBoxLayout()
        self.widgets = []
        for key in options.keys():
            w = QRadioButton(key)
            if actions is not None:
                w.clicked.connect(actions[key])
            if enabled is not None:
                w.setEnabled(enabled[key])
            self.widgets.append(w)
            vbox.addWidget(w)
        self.widgets[0].setChecked(True)
        self.setLayout(vbox)

    def initialClick(self):
        self.widgets[0].click()

    def value(self):
        for w in self.widgets:
            if w.isChecked():
                return self.options[w.text()]
        return None

    def name(self):
        for w in self.widgets:
            if w.isChecked():
                return w.text()
        return ''

    def disable(self):
        for w in self.widgets:
            w.setEnabled(False)

    def enable(self):
        for w in self.widgets:
            w.setEnabled(True)
