import sys
from itertools import combinations
import operator

from .imports import *

from .views import TableWidget

from .models import SegmentPairModel, EnvironmentModel, FilterModel

from .delegates import SwitchDelegate

class ThumbListWidget(QListWidget):
    def __init__(self, ordering, parent=None):
        super(ThumbListWidget, self).__init__(parent)
        self.ordering = ordering
        #self.setIconSize(QSize(124, 124))
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setAcceptDrops(True)


    def dropEvent(self, event):
        event.setDropAction(Qt.MoveAction)
        super(ThumbListWidget, self).dropEvent(event)

class FactorFilter(QWidget):
    def __init__(self, attribute,parent=None):

        QWidget.__init__(self,parent)

        layout = QHBoxLayout()
        levels = sorted(attribute.range)
        self.sourceWidget = ThumbListWidget(levels)
        for l in levels:
            self.sourceWidget.addItem(l)

        sourceFrame = QGroupBox('Available levels')
        l = QVBoxLayout()
        l.addWidget(self.sourceWidget)
        sourceFrame.setLayout(l)

        layout.addWidget(sourceFrame)

        buttonLayout = QVBoxLayout()
        self.addOneButton = QPushButton('>')
        self.addOneButton.clicked.connect(self.addOne)
        self.addAllButton = QPushButton('>>')
        self.addAllButton.clicked.connect(self.addAll)

        self.clearOneButton = QPushButton('<')
        self.clearOneButton.clicked.connect(self.clearOne)
        self.clearAllButton = QPushButton('<<')
        self.clearAllButton.clicked.connect(self.clearAll)

        buttonLayout.addWidget(self.addOneButton, alignment = Qt.AlignCenter)
        buttonLayout.addWidget(self.addAllButton, alignment = Qt.AlignCenter)
        buttonLayout.addWidget(self.clearOneButton, alignment = Qt.AlignCenter)
        buttonLayout.addWidget(self.clearAllButton, alignment = Qt.AlignCenter)

        buttonFrame = QFrame()
        buttonFrame.setLayout(buttonLayout)
        layout.addWidget(buttonFrame, alignment = Qt.AlignCenter)

        self.targetWidget = ThumbListWidget(levels)

        targetFrame = QGroupBox('Included levels')
        l = QVBoxLayout()
        l.addWidget(self.targetWidget)
        targetFrame.setLayout(l)

        layout.addWidget(targetFrame)

        self.setLayout(layout)

    def addOne(self):
        items = self.sourceWidget.selectedItems()
        for i in items:
            item = self.sourceWidget.takeItem(self.sourceWidget.row(i))
            self.targetWidget.addItem(item)

    def addAll(self):
        items = [self.sourceWidget.item(i) for i in range(self.sourceWidget.count())]
        for i in items:
            item = self.sourceWidget.takeItem(self.sourceWidget.row(i))
            self.targetWidget.addItem(item)

    def clearOne(self):
        items = self.targetWidget.selectedItems()
        for i in items:
            item = self.targetWidget.takeItem(self.targetWidget.row(i))
            self.sourceWidget.addItem(item)

    def clearAll(self):
        items = [self.targetWidget.item(i) for i in range(self.targetWidget.count())]
        for i in items:
            item = self.targetWidget.takeItem(self.targetWidget.row(i))
            self.sourceWidget.addItem(item)

    def value(self):
        items = set([self.targetWidget.item(i).text() for i in range(self.targetWidget.count())])
        return items

class NumericFilter(QWidget):
    conditionalDisplay = ('equals','does not equal','greater than',
                    'greater than or equal to', 'less than',
                    'less than or equal to')
    conditionals = (operator.eq, operator.ne, operator.gt, operator.ge,
                    operator.lt, operator.le)
    def __init__(self,parent=None):

        QWidget.__init__(self,parent)

        layout = QHBoxLayout()

        self.conditionalSelect = QComboBox()
        for c in self.conditionalDisplay:
            self.conditionalSelect.addItem(c)

        layout.addWidget(self.conditionalSelect)

        self.valueEdit = QLineEdit()

        layout.addWidget(self.valueEdit)

        self.setLayout(layout)

    def value(self):
        ind = self.conditionalSelect.currentIndex()

        return self.conditionals[ind], self.valueEdit.text()


class AttributeFilterDialog(QDialog):
    def __init__(self, attributes,parent=None):
        QDialog.__init__(self,parent)

        self.attributes = list()

        layout = QVBoxLayout()

        mainlayout = QHBoxLayout()

        self.selectWidget = QComboBox()
        for a in attributes:
            if a.att_type in ['factor','numeric']:
                self.attributes.append(a)
                self.selectWidget.addItem(a.display_name)

        self.selectWidget.currentIndexChanged.connect(self.updateFrame)

        selectFrame = QGroupBox('Attribute to filter')

        selectlayout = QVBoxLayout()
        selectlayout.addWidget(self.selectWidget)
        selectFrame.setLayout(selectlayout)

        mainlayout.addWidget(selectFrame)


        self.filterWidget = NumericFilter()
        filterLayout = QVBoxLayout()
        filterLayout.addWidget(self.filterWidget)

        self.filterFrame = QGroupBox('Filter')
        self.filterFrame.setLayout(filterLayout)

        mainlayout.addWidget(self.filterFrame)

        mainframe = QFrame()

        mainframe.setLayout(mainlayout)

        layout.addWidget(mainframe)

        self.oneButton = QPushButton('Add')
        self.anotherButton = QPushButton('Add and create another')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.oneButton, alignment = Qt.AlignLeft)
        acLayout.addWidget(self.anotherButton, alignment = Qt.AlignLeft)
        acLayout.addWidget(self.cancelButton, alignment = Qt.AlignLeft)
        self.oneButton.clicked.connect(self.one)
        self.anotherButton.clicked.connect(self.another)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame, alignment = Qt.AlignLeft)

        self.setLayout(layout)
        #self.setFixedSize(self.sizeHint())
        self.setWindowTitle('Create {}'.format(parent.name))

    def updateFrame(self):
        index = self.selectWidget.currentIndex()
        a = self.attributes[index]
        self.filterWidget.deleteLater()
        if a.att_type == 'numeric':
            self.filterWidget = NumericFilter()
            self.filterFrame.layout().addWidget(self.filterWidget)
        elif a.att_type == 'factor':
            self.filterWidget = FactorFilter(a)
            self.filterFrame.layout().addWidget(self.filterWidget)
        self.resize(self.sizeHint())

    def one(self):
        self.addOneMore = False
        self.accept()

    def another(self):
        self.addOneMore = True
        self.accept()

    def accept(self):
        index = self.selectWidget.currentIndex()
        a = self.attributes[index]
        val = self.filterWidget.value()
        if a.att_type == 'numeric':
            comp = val[0]
            try:
                value = float(val[1])
            except ValueError:
                reply = QMessageBox.critical(self,
                        "Invalid information", "Please specify a number.")
                return
            if (comp in [operator.gt, operator.ge] and value > a.range[1]) or \
                (comp in [operator.lt,operator.le] and value < a.range[0]) or \
                (comp in [operator.eq,operator.ne] and (value < a.range[0] or value > a.range[1])):
                reply = QMessageBox.critical(self,
                        "Invalid information", "The value specified ({}) for column '{}' is outside its range of {}-{}.".format(value,str(a),a.range[0],a.range[1]))
                return
            self.filter = (a, comp, value)
        elif a.att_type == 'factor':
            self.filter = (a, val)

        QDialog.accept(self)

    def reject(self):
        self.addOneMore = False
        QDialog.reject(self)

class AttributeFilterWidget(QGroupBox):
    name = 'filter'
    def __init__(self, corpus, parent = None):
        QGroupBox.__init__(self,'Filter corpus',parent)
        self.attributes = corpus.attributes

        vbox = QVBoxLayout()

        self.addButton = QPushButton('Add {}'.format(self.name))
        self.addButton.clicked.connect(self.filtPopup)
        self.removeButton = QPushButton('Remove selected {}s'.format(self.name))
        self.removeButton.clicked.connect(self.removeFilt)
        self.addButton.setAutoDefault(False)
        self.addButton.setDefault(False)
        self.removeButton.setAutoDefault(False)
        self.removeButton.setDefault(False)

        self.table = TableWidget()
        self.table.setSortingEnabled(False)
        try:
            self.table.horizontalHeader().setClickable(False)
            self.table.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        except AttributeError:
            self.table.horizontalHeader().setSectionsClickable(False)
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setModel(FilterModel())
        self.table.resizeColumnsToContents()

        vbox.addWidget(self.addButton)
        vbox.addWidget(self.removeButton)
        vbox.addWidget(self.table)

        self.setLayout(vbox)

    def filtPopup(self):
        dialog = AttributeFilterDialog(self.attributes,self)
        addOneMore = True
        while addOneMore:
            result = dialog.exec_()
            if result:
                self.table.model().addRow([dialog.filter])
            addOneMore = dialog.addOneMore

    def removeFilt(self):
        select = self.table.selectionModel()
        if select.hasSelection():
            selected = select.selectedRows()
            self.table.model().removeRows([s.row() for s in selected])

    def value(self):
        return [x[0] for x in self.table.model().filters]


class TierWidget(QGroupBox):
    def __init__(self, corpus, parent = None, include_spelling = False):
        QGroupBox.__init__(self,'Tier',parent)
        self.spellingIncluded = include_spelling
        self.spellingEnabled = include_spelling
        layout = QVBoxLayout()

        self.tierSelect = QComboBox()
        self.atts = list()
        if include_spelling:
            self.atts.append(corpus.attributes[0])
            self.tierSelect.addItem(corpus.attributes[0].display_name)
        for a in corpus.attributes:
            if corpus.has_transcription and a.att_type == 'tier':
                self.atts.append(a)
                self.tierSelect.addItem(a.display_name)
        layout.addWidget(self.tierSelect)
        self.setLayout(layout)

    def setSpellingEnabled(self, b):
        self.spellingEnabled = b
        if b:
            if self.tierSelect.itemText(0) != 'Spelling':
                self.tierSelect.insertItem(0,'Spelling')
        else:
            if self.tierSelect.itemText(0) == 'Spelling':
                self.tierSelect.removeItem(0)

    def value(self):
        index = self.tierSelect.currentIndex()
        if not self.spellingEnabled and self.spellingIncluded:
            index += 1
        return self.atts[index].name

    def displayValue(self):
        index = self.tierSelect.currentIndex()
        if not self.spellingEnabled and self.spellingIncluded:
            index += 1
        return self.atts[index].display_name

class PunctuationWidget(QGroupBox):
    def __init__(self, punctuation, title = 'Punctuation',parent = None):
        QGroupBox.__init__(self,title,parent)

        self.btnGroup = QButtonGroup()
        self.btnGroup.setExclusive(False)
        layout = QVBoxLayout()
        box = QGridLayout()

        row = 0
        col = 0
        for s in punctuation:
            btn = QPushButton(s)
            btn.setAutoDefault(False)
            btn.setCheckable(True)
            btn.setAutoExclusive(False)
            btn.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
            btn.setMaximumWidth(btn.fontMetrics().boundingRect(s).width() + 14)
            btn.setFocusPolicy(Qt.NoFocus)

            box.addWidget(btn,row,col)
            self.btnGroup.addButton(btn)
            col += 1
            if col > 11:
                col = 0
                row += 1
        boxFrame = QFrame()
        boxFrame.setLayout(box)
        layout.addWidget(boxFrame)

        buttonlayout = QHBoxLayout()
        self.checkAll = QPushButton('Check all')
        self.checkAll.setAutoDefault(False)
        self.checkAll.clicked.connect(self.check)
        self.uncheckAll = QPushButton('Uncheck all')
        self.uncheckAll.setAutoDefault(False)
        self.uncheckAll.clicked.connect(self.uncheck)
        buttonlayout.addWidget(self.checkAll, alignment = Qt.AlignLeft)
        buttonlayout.addWidget(self.uncheckAll, alignment = Qt.AlignLeft)
        buttonframe = QFrame()
        buttonframe.setLayout(buttonlayout)

        layout.addWidget(buttonframe)
        self.setLayout(layout)

    def check(self):
        for b in self.btnGroup.buttons():
            b.setChecked(True)

    def uncheck(self):
        for b in self.btnGroup.buttons():
            b.setChecked(False)

    def value(self):
        value = []
        for b in self.btnGroup.buttons():
            if b.isChecked():
                t = b.text()
                value.append(t)
        return value

class DigraphDialog(QDialog):
    def __init__(self, characters, parent = None):
        QDialog.__init__(self, parent)
        layout = QFormLayout()
        self.digraphLine = QLineEdit()
        layout.addRow(QLabel('Digraph'),self.digraphLine)
        symbolframe = QGroupBox('Characters')
        box = QGridLayout()

        row = 0
        col = 0
        self.buttons = list()
        for s in characters:
            btn = QPushButton(s)
            btn.clicked.connect(self.addCharacter)
            btn.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
            btn.setMaximumWidth(btn.fontMetrics().boundingRect(s).width() + 14)
            self.buttons.append(btn)
            box.addWidget(btn,row,col)
            col += 1
            if col > 11:
                col = 0
                row += 1
        symbolframe.setLayout(box)
        layout.addRow(symbolframe)
        self.oneButton = QPushButton('Add')
        self.anotherButton = QPushButton('Add and create another')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.oneButton, alignment = Qt.AlignLeft)
        acLayout.addWidget(self.anotherButton, alignment = Qt.AlignLeft)
        acLayout.addWidget(self.cancelButton, alignment = Qt.AlignLeft)
        self.oneButton.clicked.connect(self.one)
        self.anotherButton.clicked.connect(self.another)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addRow(acFrame)
        self.setLayout(layout)
        self.setFixedSize(self.sizeHint())
        self.setWindowTitle('Construct Digraph')

    def addCharacter(self):
        self.digraphLine.setText(self.digraphLine.text()+self.sender().text())

    def one(self):
        self.addOneMore = False
        self.accept()

    def another(self):
        self.addOneMore = True
        self.accept()

    def value(self):
        return self.digraphLine.text()

    def reject(self):
        self.addOneMore = False
        QDialog.reject(self)



class DigraphWidget(QGroupBox):
    def __init__(self,parent = None):
        self._parent = parent
        QGroupBox.__init__(self,'Digraphs',parent)
        layout = QVBoxLayout()

        self.editField = QLineEdit()
        layout.addWidget(self.editField)
        self.button = QPushButton('Construct a digraph')
        self.button.setAutoDefault(False)
        self.button.clicked.connect(self.construct)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def construct(self):
        minus = set(self._parent.ignoreList())
        wd, td = self._parent.delimiters()
        delims = []
        if wd is None:
            delims.extend([' ','\t','\n'])
        elif isinstance(wd,list):
            delims.extend(wd)
        else:
            delims.append(wd)
        if td is not None:
            if isinstance(td,list):
                delims.extend(td)
            else:
                delims.append(td)
        minus.update(delims)
        possible = sorted(self._parent.characters - minus, key = lambda x: x.lower())
        dialog = DigraphDialog(possible,self)
        addOneMore = True
        while addOneMore:
            if dialog.exec_():
                v = dialog.value()
                if v != '' and v not in self.value():
                    val = self.value() + [v]
                    self.editField.setText(','.join(val))
            dialog.digraphLine.setText('')
            addOneMore = dialog.addOneMore


    def value(self):
        text = self.editField.text()
        values = [x.strip() for x in text.split(',') if x.strip() != '']
        return values

class FileWidget(QFrame):
    def __init__(self,title,filefilter,parent=None):
        QFrame.__init__(self,parent)

        self.title = title

        self.filefilter = filefilter

        pathLayout = QHBoxLayout()
        self.pathEdit = QLineEdit()
        pathButton = QPushButton('Choose file...')
        pathButton.setAutoDefault(False)
        pathButton.setDefault(False)
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
        pathButton.setAutoDefault(False)
        pathButton.setDefault(False)
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
        pathButton.setAutoDefault(False)
        pathButton.setDefault(False)
        pathButton.clicked.connect(self.pathSet)
        pathLayout.addWidget(self.pathEdit)
        pathLayout.addWidget(pathButton)
        self.setLayout(pathLayout)

        self.textChanged = self.pathEdit.textChanged

    def setPath(self,path):
        self.pathEdit.setText(path)

    def pathSet(self):
        filename = QFileDialog.getExistingDirectory(self,"Choose a directory")
        if filename:
            self.pathEdit.setText(filename)

    def value(self):
        return self.pathEdit.text()

class InventoryTable(QTableWidget):
    def __init__(self):
        QTableWidget.__init__(self)
        self.horizontalHeader().setMinimumSectionSize(70)

        try:
            self.horizontalHeader().setSectionsClickable(False)
            self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
            self.verticalHeader().setSectionsClickable(False)
            self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        except AttributeError:
            self.horizontalHeader().setClickable(False)
            self.horizontalHeader().setResizeMode(QHeaderView.Fixed)
            self.verticalHeader().setClickable(False)
            self.verticalHeader().setResizeMode(QHeaderView.Fixed)

        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

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

class SegmentButton(QPushButton):
    def sizeHint(self):
        sh = QPushButton.sizeHint(self)

        #sh.setHeight(self.fontMetrics().boundingRect(self.text()).height()+14)
        sh.setHeight(35)
        sh.setWidth(self.fontMetrics().boundingRect(self.text()).width()+14)
        return sh


class InventoryBox(QWidget):
    consonantColumns = ['Labial','Labiodental','Dental','Alveolar','Alveopalatal','Retroflex',
                    'Palatal','Velar','Uvular','Pharyngeal','Epiglottal','Glottal']

    consonantRows = ['Stop','Nasal','Fricative','Affricate','Approximate','Trill','Tap',
                    'Lateral fricative','Lateral approximate','Lateral flap']

    vowelColumns = ['Front','Near front','Central','Near back','Back']

    vowelRows = ['Close','Near close','Close mid','Mid','Open mid','Near open','Open']

    def __init__(self, title,inventory,parent=None):
        QWidget.__init__(self,parent)

        self.inventory = inventory
        #find cats
        consColumns = set()
        consRows = set()
        vowColumns = set()
        vowRows = set()
        for s in self.inventory:
            try:
                c = s.category
            except KeyError:
                c = None
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

            box.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            box.setSpacing(0)
            smallbox = QVBoxLayout()
            smallbox.setSizeConstraint(QLayout.SetFixedSize)
            smallbox.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            cons = QGroupBox('Consonants')
            cons.setFlat(True)
            cons.setCheckable(True)
            cons.setChecked(False)
            cons.toggled.connect(self.showHideCons)
            consBox = QVBoxLayout()
            self.consTable = InventoryTable()
            self.consTable.hide()
            consBox.addWidget(self.consTable)
            cons.setLayout(consBox)

            consColumns = [ x for x in self.consonantColumns if x in consColumns]
            consColMapping = {x:i for i,x in enumerate(consColumns)}
            consRows = [ x for x in self.consonantRows if x in consRows]
            consRowMapping = {x:i for i,x in enumerate(consRows)}

            self.consTable.setColumnCount(len(consColumns))
            self.consTable.setRowCount(len(consRows))
            self.consTable.setHorizontalHeaderLabels(consColumns)
            self.consTable.resizeColumnsToContents()
            self.consTable.setVerticalHeaderLabels(consRows)

            for i in range(len(consColumns)):
                for j in range(len(consRows)):
                    wid = QWidget()
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
                    self.consTable.setCellWidget(j,i,wid)

            vow = QGroupBox('Vowels')
            vow.setFlat(True)
            vow.setCheckable(True)
            vow.setChecked(False)
            vow.toggled.connect(self.showHideVow)
            vowBox = QGridLayout()
            vowBox.setAlignment(Qt.AlignTop)
            self.vowTable = InventoryTable()
            self.vowTable.hide()
            vowBox.addWidget(self.vowTable,0, Qt.AlignLeft|Qt.AlignTop)
            vow.setLayout(vowBox)
            vowColumns = [ x for x in self.vowelColumns if x in vowColumns]
            vowColMapping = {x:i for i,x in enumerate(vowColumns)}
            vowRows = [ x for x in self.vowelRows if x in vowRows]
            vowRowMapping = {x:i for i,x in enumerate(vowRows)}

            self.vowTable.setColumnCount(len(vowColumns))
            self.vowTable.setRowCount(len(vowRows) + 1)
            self.vowTable.setHorizontalHeaderLabels(vowColumns)
            self.vowTable.resizeColumnsToContents()
            self.vowTable.setVerticalHeaderLabels(vowRows + ['Diphthongs'])

            for i in range(len(vowColumns)):
                for j in range(len(vowRows)):
                    wid = QWidget()
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
                    self.vowTable.setCellWidget(j,i,wid)

            self.vowTable.setSpan(len(vowRows),0,1,len(vowColumns))
            diphWid = QWidget()
            diphWid.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
            diphBox = QHBoxLayout()
            #diphBox.setAlignment(Qt.AlignCenter)
            diphBox.setContentsMargins(0, 0, 0, 0)
            diphBox.setSpacing(0)
            diphWid.setLayout(diphBox)
            self.vowTable.setCellWidget(len(vowRows),0,diphWid)

            unk = QGroupBox('Other')
            unk.setFlat(True)
            #unk.setCheckable(True)
            #unk.setChecked(False)
            #unk.toggled.connect(self.showHideUnk)
            unkBox = QGridLayout()
            unk.setLayout(unkBox)

            unkRow = 0
            unkCol = -1
            for s in inventory:
                try:
                    cat = s.category
                except KeyError:
                    cat = None
                btn = SegmentButton(s.symbol)
                btn.setCheckable(True)
                btn.setAutoExclusive(False)
                btn.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
                #btn.setMaximumWidth(btn.fontMetrics().boundingRect(s.symbol).width() + 14)
                #btn.setMaximumHeight(btn.fontMetrics().boundingRect(s.symbol).height() + 14)
                #btn.setMinimumWidth(btn.fontMetrics().boundingRect(s.symbol).width() +7)
                #btn.setMinimumHeight(btn.fontMetrics().boundingRect(s.symbol).height() + 14)
                self.btnGroup.addButton(btn)
                if cat is None:
                    unkCol += 1
                    if unkCol > 11:
                        unkCol = 0
                        unkRow += 1
                    unkBox.addWidget(btn,unkRow,unkCol)

                elif cat[0] == 'Vowel':
                    if cat[1] is None or cat[2] is None:
                        continue
                    col = vowColMapping[cat[2]]
                    row = vowRowMapping[cat[1]]
                    if cat[3] == 'Unrounded':
                        colTwo = 0
                    else:
                        colTwo = 1
                    cell = self.vowTable.cellWidget(row,col).layout().itemAtPosition(0,colTwo).widget()

                    cell.show()
                    cell.layout().addWidget(btn)#, alignment = Qt.AlignCenter)
                    cell.setMinimumHeight(cell.sizeHint().height())
                    #vowTable.cellWidget(row,col).setMinimumSize(cell.sizeHint())


                elif cat[0] == 'Consonant':
                    col = consColMapping[cat[1]]
                    row = consRowMapping[cat[2]]
                    if cat[3] == 'Voiceless':
                        colTwo = 0
                    else:
                        colTwo = 1
                    cell = self.consTable.cellWidget(row,col).layout().itemAtPosition(0,colTwo).widget()

                    cell.show()
                    cell.layout().addWidget(btn)#, alignment = Qt.AlignCenter)
                    #cell.setMinimumHeight(cell.sizeHint().height())

                elif cat[0] == 'Diphthong':
                    diphBox.addWidget(btn)

            self.consTable.resize()
            self.vowTable.resize()
            smallbox.addWidget(cons, alignment = Qt.AlignLeft | Qt.AlignTop)

            smallbox.addWidget(vow, alignment = Qt.AlignLeft | Qt.AlignTop)
            b = QFrame()
            b.setLayout(smallbox)
            box.addWidget(b, alignment = Qt.AlignLeft | Qt.AlignTop)
            box.addWidget(unk, alignment = Qt.AlignLeft | Qt.AlignTop)
        else:
            box = QGridLayout()

            row = 0
            col = 0
            for s in inventory:
                btn = SegmentButton(s.symbol)
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

    def showHideCons(self, checked):
        if checked:
            self.consTable.show()
        else:
            self.consTable.hide()

    def showHideVow(self, checked):
        if checked:
            self.vowTable.show()
        else:
            self.vowTable.hide()

    def clearAll(self):
        reexc = self.btnGroup.exclusive()
        if reexc:
            self.setExclusive(False)
        for btn in self.btnGroup.buttons():
            btn.setChecked(False)
        if reexc:
            self.setExclusive(True)

    def setExclusive(self, b):
        self.btnGroup.setExclusive(b)
        for btn in self.btnGroup.buttons():
            btn.setAutoExclusive(b)

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

class TranscriptionWidget(QGroupBox):
    transcriptionChanged = Signal(object)
    def __init__(self, title,inventory,parent=None):
        QGroupBox.__init__(self,title,parent)
        self.inventory = inventory

        layout = QFormLayout()

        self.transEdit = QLineEdit()
        self.transEdit.textChanged.connect(self.transcriptionChanged.emit)
        self.showInv = QPushButton('Show inventory')
        self.showInv.setAutoDefault(False)
        self.showInv.clicked.connect(self.showHide)
        layout.addRow(self.transEdit,self.showInv)

        self.segments = InventoryBox('Inventory',self.inventory)
        for btn in self.segments.btnGroup.buttons():
            btn.setCheckable(False)
            btn.setAutoDefault(False)
            btn.clicked.connect(self.addCharacter)
        self.segments.hide()
        layout.addRow(self.segments)

        self.setLayout(layout)

    def text(self):
        return self.transEdit.text()

    def setText(self, text):
        self.transEdit.setText(text)

    def addCharacter(self):
        t = self.transEdit.text()
        if t != '':
            t += '.'
        self.transEdit.setText(t+self.sender().text())

    def showHide(self):
        if self.segments.isHidden():
            self.segments.show()
            self.showInv.setText('Hide inventory')
        else:
            self.segments.hide()
            self.showInv.setText('Show inventory')
        self.updateGeometry()



class FeatureBox(QWidget):
    def __init__(self, title,inventory,parent=None):
        QWidget.__init__(self,parent)

        self.inventory = inventory
        self.inspectInventory()
        layout = QHBoxLayout()

        #layout.setSizeConstraint(QLayout.SetFixedSize)

        self.featureList = QListWidget()

        for f in self.features:
            self.featureList.addItem(f)
        self.featureList.setFixedWidth(self.featureList.minimumSizeHint().width()+20)
        layout.addWidget(self.featureList)

        buttonLayout = QVBoxLayout()
        buttonLayout.setSpacing(0)
        self.buttons = list()
        for v in self.values:
            b = QPushButton('Add [{}feature]'.format(v))
            b.value = v
            b.clicked.connect(self.addFeature)
            buttonLayout.addWidget(b, alignment = Qt.AlignCenter)
            self.buttons.append(b)

        self.clearOneButton = QPushButton('Remove selected')
        self.clearOneButton.clicked.connect(self.clearOne)
        buttonLayout.addWidget(self.clearOneButton, alignment = Qt.AlignCenter)

        self.clearButton = QPushButton('Remove all')
        self.clearButton.clicked.connect(self.clearAll)
        buttonLayout.addWidget(self.clearButton, alignment = Qt.AlignCenter)

        buttonFrame = QFrame()
        buttonFrame.setLayout(buttonLayout)
        layout.addWidget(buttonFrame, alignment = Qt.AlignCenter)

        self.envList = QListWidget()
        self.envList.setFixedWidth(self.featureList.minimumSizeHint().width()+25)
        self.envList.setSelectionMode(QAbstractItemView.ExtendedSelection)

        layout.addWidget(self.envList)

        self.setLayout(layout)

    def inspectInventory(self):
        self.features = sorted(self.inventory[-1].features.keys())
        self.values = set()
        for v in self.inventory:
            self.values.update(v.features.values())
        self.values = sorted([x for x in self.values if x != ''])

    def addFeature(self):
        curFeature = self.featureList.currentItem()
        if curFeature:
            val = self.sender().value
            feat = curFeature.text()
            key = val+feat
            if key not in self.currentSpecification():
                self.envList.addItem(key)

    def clearOne(self):
        items = self.envList.selectedItems()
        for i in items:
            item = self.envList.takeItem(self.envList.row(i))
            #self.sourceWidget.addItem(item)

    def clearAll(self):
        self.envList.clear()

    def currentSpecification(self):
        return [self.envList.item(i).text() for i in range(self.envList.count())]

    def value(self):
        val = self.currentSpecification()
        if not val:
            return ''
        return '[{}]'.format(','.join(val))


class SegmentPairDialog(QDialog):
    def __init__(self, inventory,parent=None):
        QDialog.__init__(self,parent)

        layout = QVBoxLayout()

        layout.setSizeConstraint(QLayout.SetFixedSize)

        segFrame = QFrame()

        segLayout = QHBoxLayout()

        self.segFrame = InventoryBox('Segments',inventory)

        segLayout.addWidget(self.segFrame)

        segFrame.setLayout(segLayout)

        layout.addWidget(segFrame)


        self.oneButton = QPushButton('Add')
        self.anotherButton = QPushButton('Add and create another')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.oneButton, alignment = Qt.AlignLeft)
        acLayout.addWidget(self.anotherButton, alignment = Qt.AlignLeft)
        acLayout.addWidget(self.cancelButton, alignment = Qt.AlignLeft)
        self.oneButton.clicked.connect(self.one)
        self.anotherButton.clicked.connect(self.another)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame, alignment = Qt.AlignLeft)

        self.setLayout(layout)
        self.setFixedSize(self.sizeHint())
        self.setWindowTitle('Select segment pair')

    def one(self):
        self.addOneMore = False
        self.accept()

    def another(self):
        self.addOneMore = True
        self.accept()

    def reset(self):
        self.segFrame.clearAll()

    def reject(self):
        self.addOneMore = False
        QDialog.reject(self)

    def accept(self):
        selected = self.segFrame.value()
        self.pairs = combinations(selected,2)
        QDialog.accept(self)

class SegPairTableWidget(TableWidget):
    def __init__(self, parent = None):
        TableWidget.__init__(self, parent)
        self.setModel(SegmentPairModel())
        self.setItemDelegateForColumn(2, SwitchDelegate(self))
        self.model().rowsInserted.connect(self.addSwitch)
        self.setSortingEnabled(False)
        self.horizontalHeader().setSectionsClickable(False)

        switch = QPushButton()
        if sys.platform == 'darwin' or sys.platform.startswith('win'):
            icon = QIcon()
            icon.addPixmap(QPixmap(":/Icon/resources/object-flip-horizontal.png"),
                        QIcon.Normal, QIcon.Off)
        else:
            icon = QIcon.fromTheme('object-flip-horizontal')
        switch.setIcon(icon)
        self.horizontalHeader().setDefaultSectionSize(switch.iconSize().width()+16)
        self.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)

    def minimumSizeHint(self):
        sh = TableWidget.minimumSizeHint(self)
        width = self.horizontalOffset()
        header = self.horizontalHeader()
        for i in range(3):
            width += header.sectionSize(i)
        sh.setWidth(width)
        return sh

    def addSwitch(self, index, begin, end):
        self.openPersistentEditor(self.model().index(begin, 2))


class SegmentPairSelectWidget(QGroupBox):
    def __init__(self,inventory,parent=None):
        QGroupBox.__init__(self,'Segments',parent)

        self.inventory = inventory

        vbox = QVBoxLayout()
        self.addButton = QPushButton('Add pair of sounds')
        self.addButton.clicked.connect(self.segPairPopup)
        self.removeButton = QPushButton('Remove selected sound pair')
        self.removeButton.clicked.connect(self.removePair)
        self.addButton.setAutoDefault(False)
        self.addButton.setDefault(False)
        self.removeButton.setAutoDefault(False)
        self.removeButton.setDefault(False)

        self.table = SegPairTableWidget()

        vbox.addWidget(self.addButton)
        vbox.addWidget(self.removeButton)
        vbox.addWidget(self.table)
        self.setLayout(vbox)

        self.setFixedWidth(self.minimumSizeHint().width())

    def segPairPopup(self):
        dialog = SegmentPairDialog(self.inventory)
        addOneMore = True
        while addOneMore:
            dialog.reset()
            result = dialog.exec_()
            if result:
                self.addPairs(dialog.pairs)
            addOneMore = dialog.addOneMore

    def addPairs(self, pairs):
        for p in pairs:
            self.table.model().addRow(p)

    def removePair(self):
        select = self.table.selectionModel()
        if select.hasSelection():
            selected = [s.row() for s in select.selectedRows()]
            self.table.model().removeRows(selected)

    def value(self):
        return self.table.model().rows

class SegFeatSelect(QGroupBox):
    def __init__(self,corpus, title, parent = None, exclusive = False):
        QGroupBox.__init__(self,title,parent)
        self.segExclusive = exclusive
        self.corpus = corpus
        self.inventory = self.corpus.inventory
        self.features = self.inventory[-1].features.keys()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.typeSelect = QComboBox()
        self.typeSelect.addItem('Segments')
        if len(self.features) > 0:
            self.typeSelect.addItem('Features')
        else:
            layout.addWidget(QLabel('Features are not available for selection without a feature system.'))
        self.typeSelect.currentIndexChanged.connect(self.generateFrame)

        layout.addWidget(QLabel('Basis segment selection:'))
        layout.addWidget(self.typeSelect, alignment = Qt.AlignLeft)

        self.sel = InventoryBox('',self.inventory)
        self.sel.setExclusive(self.segExclusive)

        layout.addWidget(self.sel)

        self.setLayout(layout)

    def generateFrame(self):
        self.sel.deleteLater()
        if self.typeSelect.currentText() == 'Segments':
            self.sel = InventoryBox('',self.inventory)
            self.sel.setExclusive(self.segExclusive)
        elif self.typeSelect.currentText() == 'Features':
            self.sel = FeatureBox('',self.inventory)
        self.layout().addWidget(self.sel)

    def value(self):
        return self.sel.value()

    def segments(self):
        if self.typeSelect.currentText() == 'Segments':
            return self.sel.value()
        elif self.typeSelect.currentText() == 'Features':
            return self.corpus.features_to_segments(self.sel.value()[1:-1])

class EnvironmentDialog(QDialog):
    def __init__(self, inventory,parent=None):
        QDialog.__init__(self,parent)

        self.inventory = inventory
        self.features = inventory[-1].features.keys()

        layout = QVBoxLayout()

        layout.setSizeConstraint(QLayout.SetFixedSize)

        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.lhsEnvFrame = QGroupBox('Left hand side')

        self.rhsEnvFrame = QGroupBox('Right hand side')

        self.lhsEnvLayout = QVBoxLayout()

        self.lhsEnvLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.rhsEnvLayout = QVBoxLayout()

        self.rhsEnvLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        if parent.name == 'environment':
            self.lhsEnvType = QComboBox()
            self.rhsEnvType = QComboBox()
            self.lhsEnvType.addItem('Segments')
            self.rhsEnvType.addItem('Segments')
            if len(self.features) > 0:
                self.lhsEnvType.addItem('Features')
                self.rhsEnvType.addItem('Features')
            else:
                layout.addWidget(QLabel('Features for {} selection are not available without a feature system.'.format(parent.name)))

            self.lhsEnvType.currentIndexChanged.connect(self.generateLhsFrame)
            self.rhsEnvType.currentIndexChanged.connect(self.generateRhsFrame)

            self.lhsEnvLayout.addWidget(QLabel('Basis for building {}:'.format(parent.name)))
            self.lhsEnvLayout.addWidget(self.lhsEnvType, alignment = Qt.AlignLeft)

            self.rhsEnvLayout.addWidget(QLabel('Basis for building {}:'.format(parent.name)))
            self.rhsEnvLayout.addWidget(self.rhsEnvType, alignment = Qt.AlignLeft)

        self.lhs = InventoryBox('',self.inventory)
        self.lhs.setExclusive(True)

        self.rhs = InventoryBox('',self.inventory)
        self.rhs.setExclusive(True)

        self.lhsEnvLayout.addWidget(self.lhs)
        self.rhsEnvLayout.addWidget(self.rhs)

        self.lhsEnvFrame.setLayout(self.lhsEnvLayout)

        self.rhsEnvFrame.setLayout(self.rhsEnvLayout)
        envFrame = QFrame()

        envLayout = QHBoxLayout()

        envLayout.addWidget(self.lhsEnvFrame)
        envLayout.addWidget(self.rhsEnvFrame)

        envFrame.setLayout(envLayout)

        layout.addWidget(envFrame)

        self.oneButton = QPushButton('Add')
        self.anotherButton = QPushButton('Add and create another')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.oneButton, alignment = Qt.AlignLeft)
        acLayout.addWidget(self.anotherButton, alignment = Qt.AlignLeft)
        acLayout.addWidget(self.cancelButton, alignment = Qt.AlignLeft)
        self.oneButton.clicked.connect(self.one)
        self.anotherButton.clicked.connect(self.another)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame, alignment = Qt.AlignLeft)

        self.setLayout(layout)
        #self.setFixedSize(self.sizeHint())
        self.setWindowTitle('Create {}'.format(parent.name))

    def generateLhsFrame(self,ind=0):
        self.lhs.deleteLater()
        if self.lhsEnvType.currentText() == 'Segments':
            self.lhs = InventoryBox('',self.inventory)
            self.lhs.setExclusive(True)
        elif self.lhsEnvType.currentText() == 'Features':
            self.lhs = FeatureBox('',self.inventory)
        self.lhsEnvLayout.addWidget(self.lhs)

    def generateRhsFrame(self,ind=0):
        self.rhs.deleteLater()
        if self.rhsEnvType.currentText() == 'Segments':
            self.rhs = InventoryBox('',self.inventory)
            self.rhs.setExclusive(True)
        elif self.rhsEnvType.currentText() == 'Features':
            self.rhs = FeatureBox('',self.inventory)
        self.rhsEnvLayout.addWidget(self.rhs)

    def one(self):
        self.addOneMore = False
        self.accept()

    def another(self):
        self.addOneMore = True
        self.accept()

    def reset(self):
        self.lhs.clearAll()
        self.rhs.clearAll()

    def accept(self):
        if self.parent().name == 'environment':
            self.env = '{}_{}'.format(self.lhs.value(),self.rhs.value())
        else:
            lhs = self.lhs.value()
            if lhs == '':
                reply = QMessageBox.critical(self,
                        "Missing information", "Please specify a left hand of the bigram.")
                return
            rhs = self.rhs.value()
            if rhs == '':
                reply = QMessageBox.critical(self,
                        "Missing information", "Please specify a right hand of the bigram.")
                return

            self.env = '{}{}'.format(lhs,rhs)
        QDialog.accept(self)

    def reject(self):
        self.addOneMore = False
        QDialog.reject(self)

class EnvironmentSelectWidget(QGroupBox):
    name = 'environment'
    def __init__(self,inventory,parent=None):
        QGroupBox.__init__(self,'{}s'.format(self.name.title()),parent)

        self.inventory = inventory

        vbox = QVBoxLayout()

        self.addButton = QPushButton('Add {}'.format(self.name))
        self.addButton.clicked.connect(self.envPopup)
        self.removeButton = QPushButton('Remove selected {}s'.format(self.name))
        self.removeButton.clicked.connect(self.removeEnv)
        self.addButton.setAutoDefault(False)
        self.addButton.setDefault(False)
        self.removeButton.setAutoDefault(False)
        self.removeButton.setDefault(False)

        self.table = TableWidget()
        self.table.setSortingEnabled(False)
        try:
            self.table.horizontalHeader().setClickable(False)
            self.table.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        except AttributeError:
            self.table.horizontalHeader().setSectionsClickable(False)
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setModel(EnvironmentModel())
        #self.table.resizeColumnsToContents()

        vbox.addWidget(self.addButton)
        vbox.addWidget(self.removeButton)
        vbox.addWidget(self.table)

        self.setLayout(vbox)

    def envPopup(self):
        dialog = EnvironmentDialog(self.inventory,self)
        addOneMore = True
        while addOneMore:
            dialog.reset()
            result = dialog.exec_()
            if result:
                self.table.model().addRow([dialog.env])
            addOneMore = dialog.addOneMore

    def removeEnv(self):
        select = self.table.selectionModel()
        if select.hasSelection():
            selected = select.selectedRows()
            self.table.model().removeRows([s.row() for s in selected])

    def value(self):
        return [x[0] for x in self.table.model().rows]

class BigramWidget(EnvironmentSelectWidget):
    name = 'bigram'

class RadioSelectWidget(QGroupBox):
    def __init__(self,title,options, actions=None, enabled=None,parent=None):
        QGroupBox.__init__(self,title,parent)
        self.is_enabled = True
        self.actions = None
        self.enabled = None
        self.setLayout(QFormLayout())
        self.setOptions(options, actions, enabled)

    def initOptions(self):
        self.widgets = []
        for key in self.options.keys():
            w = QRadioButton(key)
            if self.actions is not None:
                w.clicked.connect(self.actions[key])
            if self.enabled is not None:
                w.setEnabled(self.enabled[key])
            if not self.is_enabled:
                w.setEnabled(False)
            self.widgets.append(w)
            self.layout().addRow(w)
        self.widgets[0].setChecked(True)

    def setOptions(self, options, actions = None, enabled = None):
        for i in reversed(range(self.layout().count())):
            w = self.layout().itemAt(i).widget()
            self.layout().removeWidget(w)
            w.setParent(None)
            w.deleteLater()
        self.options = options
        if actions is not None:
            self.actions = actions
        if enabled is not None:
            self.enabled = enabled
        self.initOptions()


    def initialClick(self):
        self.widgets[0].click()

    def click(self,index):
        if index >= len(self.widgets):
            return
        self.widgets[index].click()

    def value(self):
        for w in self.widgets:
            if w.isChecked():
                return self.options[w.text()]
        return None

    def displayValue(self):
        for w in self.widgets:
            if w.isChecked():
                return w.text()
        return ''

    def disable(self):
        self.is_enabled = False
        for w in self.widgets:
            w.setEnabled(False)

    def enable(self):
        self.is_enabled = True
        for w in self.widgets:
            if self.enabled is not None:
                w.setEnabled(self.enabled[key])
            else:
                w.setEnabled(True)
