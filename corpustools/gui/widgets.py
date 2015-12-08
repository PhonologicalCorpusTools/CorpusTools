import re
import operator
from collections import OrderedDict, namedtuple, defaultdict
from itertools import combinations, product

from .imports import *

from .models import SegmentPairModel, EnvironmentModel, FilterModel

#from .corpusgui import AddTierDialog
from .delegates import SwitchDelegate

from corpustools.corpus.classes import Attribute, EnvironmentFilter
from corpustools.corpus.io.helper import get_corpora_list, corpus_name_to_path, NUMBER_CHARACTERS


def truncate_string(string, length = 10):
    return (string[:length] + '...') if len(string) > length + 3 else string

class TableWidget(QTableView):
    def __init__(self,parent=None):
        super(TableWidget, self).__init__(parent=parent)

        self.verticalHeader().hide()

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.horizontalHeader().setMinimumSectionSize(70)
        try:
            self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        except AttributeError:
            self.horizontalHeader().setResizeMode(QHeaderView.Fixed)

        self.setSortingEnabled(True)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)

        self.clip = QApplication.clipboard()

    def keyPressEvent(self, e):
        if (e.modifiers() & Qt.ControlModifier):
            #selected = self.selectionModel().selectedRows()
            if e.key() == Qt.Key_C: #copy
                #s = '\t'+"\t".join([str(self.table.horizontalHeaderItem(i).text()) for i in xrange(selected[0].leftColumn(), selected[0].rightColumn()+1)])
                #s = s + '\n'
                s = ''

                for r in selected:
                    #s += self.table.verticalHeaderItem(r).text() + '\t'
                    for c in range(self.model().columnCount()):
                        ind = self.model().index(r.row(),c)
                        s += self.model().data(ind,Qt.DisplayRole) + "\t"
                    s = s[:-1] + "\n" #eliminate last '\t'
                self.clip.setText(s)


    def setModel(self,model):
        super(TableWidget, self).setModel(model)
        #self.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)
        #try:
        #    self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        #except AttributeError:
        #    self.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        #self.model().columnsRemoved.connect(self.horizontalHeader().resizeSections)
        #self.resizeColumnsToContents()
        try:
            self.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        except AttributeError:
            self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

    def calcWidth(self):
        header = self.horizontalHeader()
        width = self.horizontalOffset()
        for i in range(header.count()):
            width += header.sectionSize(i)
        return width

class NonScrollingComboBox(QComboBox):
    def __init__(self, parent = None):
        QComboBox.__init__(self, parent)
        self.setFocusPolicy(Qt.StrongFocus)

    def wheelEvent(self, e):
        e.ignore()

class CorpusSelect(QComboBox):
    def __init__(self, parent, settings):
        QComboBox.__init__(self,parent)
        self.settings = settings
        self.addItem('None')

        for i,s in enumerate(get_corpora_list(self.settings['storage'])):
            self.addItem(s)

    def value(self):
        val = self.currentText()
        if val == 'None':
            return ''
        return val

    def path(self):
        if self.value() != '':
            return corpus_name_to_path(self.settings['storage'],self.value())
        return None

class ParsingDialog(QDialog):
    def __init__(self, parent, annotation_type, att_type):
        QDialog.__init__(self, parent)
        self.characters = annotation_type.characters
        self.setWindowTitle('Parsing {}'.format(annotation_type.name))

        layout = QFormLayout()
        self.example = QLabel(' '.join(annotation_type[:5]))
        self.example.setWordWrap(True)
        layout.addRow('Example:', self.example)

        self.punctuationWidget = PunctuationWidget(annotation_type.punctuation)
        self.punctuationWidget.setPunctuation(annotation_type.ignored_characters)
        self.delimiterWidget = QLineEdit()
        self.morphDelimiterWidget = PunctuationWidget(annotation_type.punctuation & set('-='),
                                                        'Morpheme delimiter')
        self.morphDelimiterWidget.setPunctuation(annotation_type.morph_delimiters)
        self.digraphWidget = DigraphWidget()
        self.numberBehaviorSelect = QComboBox()
        self.numberBehaviorSelect.addItem('Same as other characters')
        self.numberBehaviorSelect.addItem('Tone')
        self.numberBehaviorSelect.addItem('Stress')
        self.numberBehaviorSelect.currentIndexChanged.connect(self.updatePunctuation)

        self.digraphWidget.characters = annotation_type.characters
        self.digraphWidget.setDigraphs(annotation_type.digraphs)

        self.punctuationWidget.selectionChanged.connect(self.punctuationChanged)
        delimiter = annotation_type.delimiter
        if delimiter is not None:
            self.delimiterWidget.setText(delimiter)
            self.punctuationWidget.updateButtons([delimiter])
        self.delimiterWidget.textChanged.connect(self.updatePunctuation)
        if att_type == 'tier':
            layout.addRow('Transcription delimiter',self.delimiterWidget)
        layout.addRow(self.morphDelimiterWidget)
        self.morphDelimiterWidget.selectionChanged.connect(self.updatePunctuation)

        if att_type == 'tier':
            if len(self.characters & set(['0','1','2'])):
                layout.addRow('Number parsing', self.numberBehaviorSelect)
            else:
                layout.addRow('Number parsing', QLabel('No numbers'))
        layout.addRow(self.punctuationWidget)
        if att_type == 'tier':
            layout.addRow(self.digraphWidget)

        self.acceptButton = QPushButton('Ok')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.cancelButton)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addRow(acFrame)

        self.setLayout(layout)

    def ignored(self):
        return self.punctuationWidget.value()

    def morphDelimiters(self):
        return self.morphDelimiterWidget.value()

    def transDelimiter(self):
        return self.delimiterWidget.text()

    def numberBehavior(self):
        if self.numberBehaviorSelect.currentIndex() == 0:
            return None
        return self.numberBehaviorSelect.currentText().lower()

    def digraphs(self):
        return self.digraphWidget.value()

    def updatePunctuation(self):
        delimiter = self.delimiterWidget.text()
        if delimiter == '':
            delimiter = []
        else:
            delimiter = [delimiter]
        self.morphDelimiterWidget.updateButtons(delimiter, emit = False)

        delimiter += self.morphDelimiterWidget.value()
        self.punctuationWidget.updateButtons(delimiter)

    def punctuationChanged(self):
        self.digraphWidget.characters = self.characters - \
                                        self.punctuationWidget.value() - \
                                        self.morphDelimiterWidget.value()
        if self.numberBehaviorSelect.currentIndex() != 0:
            self.digraphWidget.characters -= NUMBER_CHARACTERS
        delimiter = self.delimiterWidget.text()
        if delimiter != '':
            self.digraphWidget.characters -= set([delimiter])

class AnnotationTypeWidget(QGroupBox):
    def __init__(self, annotation_type, parent = None,
                ignorable = True):
        #if title is None:
        #    title = 'Annotation type details'
        QGroupBox.__init__(self, annotation_type.name, parent)

        main = QHBoxLayout()

        #main.addWidget(QLabel(annotation_type.name))

        self.annotation_type = annotation_type

        proplayout = QFormLayout()

        self.nameWidget = QLineEdit()

        proplayout.addRow('Name',self.nameWidget)

        self.typeWidget = NonScrollingComboBox()
        self.typeWidget.addItem('Orthography')
        self.typeWidget.addItem('Transcription')
        self.typeWidget.addItem('Other (numeric)')
        self.typeWidget.addItem('Other (character)')
        if ignorable:
            self.typeWidget.addItem('Notes (ignored)')
        self.typeWidget.setCurrentIndex(3)
        proplayout.addRow('Annotation type',self.typeWidget)
        self.typeWidget.currentIndexChanged.connect(self.typeChanged)

        self.associationWidget = RadioSelectWidget('Word association',
                                            OrderedDict([
                                            ('Associate this with the lexical item','type'),
                                            ('Allow this property to vary within lexical items','token'),]))

        proplayout.addRow(self.associationWidget)

        self.delimiterLabel = QLabel('None')
        if self.annotation_type.delimiter is not None:
            self.delimiterLabel.setText(self.annotation_type.delimiter)
        self.morphDelimiterLabel = QLabel('None')

        self.ignoreLabel = QLabel('None')

        self.digraphLabel = QLabel('None')

        self.numberLabel = QLabel('None')

        parselayout = QFormLayout()

        self.editButton = QPushButton('Edit parsing settings')
        self.editButton.clicked.connect(self.editParsingProperties)

        parselayout.addRow('Transcription delimiter', self.delimiterLabel)
        parselayout.addRow('Morpheme delimiter', self.morphDelimiterLabel)
        parselayout.addRow('Number parsing', self.numberLabel)
        parselayout.addRow('Ignored characters', self.ignoreLabel)
        parselayout.addRow('Multicharacter segments',self.digraphLabel)
        parselayout.addRow(self.editButton)

        main.addLayout(proplayout)
        main.addLayout(parselayout)


        if self.annotation_type.token:
            self.associationWidget.click(1)
        if self.annotation_type.anchor:
            self.typeWidget.setCurrentIndex(0)
        elif self.annotation_type.base or self.annotation_type.delimiter is not None:
            self.typeWidget.setCurrentIndex(1)
        elif self.annotation_type.attribute.att_type == 'numeric':
            self.typeWidget.setCurrentIndex(2)
        #self.attributeWidget = AttributeWidget(attribute = self.annotation_type.attribute)

        self.nameWidget.setText(self.annotation_type.attribute.display_name)
        #if show_attribute:
        #    main.addWidget(self.attributeWidget)

        self.setLayout(main)

        self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)


        self.typeChanged()

    def typeChanged(self):
        if self.typeWidget.currentIndex() in [0, 1]:
            self.editButton.setEnabled(True)
            self.updateParsingLabels()
        else:
            self.editButton.setEnabled(False)
        self.suggestName()

    def suggestName(self):
        if self.typeWidget.currentText() == 'Orthography':
            self.nameWidget.setText('Spelling')
        elif self.typeWidget.currentText() == 'Transcription':
            self.nameWidget.setText('Transcription')
        elif self.typeWidget.currentText() == 'Other (numeric)':
            self.nameWidget.setText(self.annotation_type.attribute.display_name)
        elif self.typeWidget.currentText() == 'Other (character)':
            self.nameWidget.setText(self.annotation_type.attribute.display_name)
        elif self.typeWidget.currentText() == 'Notes (ignored)':
            self.nameWidget.setText('Ignored')


    def updateParsingLabels(self):
        if self.typeWidget.currentIndex() == 0:
            self.digraphLabel.setText('N/A')
            self.numberLabel.setText('N/A')
            self.delimiterLabel.setText('N/A')
            self.morphDelimiterLabel.setText('N/A')
        elif self.typeWidget.currentIndex() == 1:
            if self.annotation_type.digraphs:
                self.digraphLabel.setText(truncate_string(' '.join(self.annotation_type.digraphs)))
            else:
                self.digraphLabel.setText('None')
            if self.annotation_type.morph_delimiters:
                self.morphDelimiterLabel.setText(
                        truncate_string(' '.join(
                            self.annotation_type.morph_delimiters
                            )
                        ))
            else:
                self.morphDelimiterLabel.setText('None')
            if self.annotation_type.trans_delimiter:
                self.delimiterLabel.setText(truncate_string(' '.join(self.annotation_type.trans_delimiter)))
            else:
                self.delimiterLabel.setText('None')
            if self.annotation_type.number_behavior:
                self.numberLabel.setText(str(self.annotation_type.number_behavior))
            else:
                self.numberLabel.setText('None')
        if self.annotation_type.ignored_characters:
            self.ignoreLabel.setText(truncate_string(' '.join(self.annotation_type.ignored_characters)))
        else:
            self.ignoreLabel.setText('None')

    def editParsingProperties(self):
        if self.typeWidget.currentText() == 'Orthography':
            atype = 'spelling'
        elif self.typeWidget.currentText() == 'Transcription':
            atype = 'tier'
        else:
            return
        dialog = ParsingDialog(self, self.annotation_type, atype)
        if dialog.exec_():
            self.annotation_type.ignored_characters = dialog.ignored()
            self.annotation_type.digraphs = dialog.digraphs()
            self.annotation_type.morph_delimiters = dialog.morphDelimiters()
            d = dialog.transDelimiter()
            if d == '':
                self.annotation_type.trans_delimiter = None
            else:
                self.annotation_type.trans_delimiter = d
            self.annotation_type.number_behavior = dialog.numberBehavior()
            self.updateParsingLabels()

    def value(self):
        a = self.annotation_type
        a.token = self.associationWidget.value() == 'token'
        display_name = self.nameWidget.text()
        a.anchor = False
        a.base = False
        name = Attribute.sanitize_name(display_name)
        if self.typeWidget.currentText() == 'Orthography':
            a.anchor = True
            a.base = False
            name = 'spelling'
            atype = 'spelling'
        elif self.typeWidget.currentText() == 'Transcription':
            a.anchor = False
            a.base = True
            atype = 'tier'
        elif self.typeWidget.currentText() == 'Other (numeric)':
            atype = 'numeric'
        elif self.typeWidget.currentText() == 'Other (character)':
            atype = 'factor'
        elif self.typeWidget.currentText() == 'Notes (ignored)':
            a.ignored = True
        if not a.ignored:
            a.attribute = Attribute(name, atype, display_name)
        return a

class AttributeWidget(QGroupBox):
    def __init__(self, attribute = None, exclude_tier = False,
                disable_name = False, parent = None):
        QGroupBox.__init__(self, 'Column details', parent)

        main = QFormLayout()

        self.nameWidget = QLineEdit()

        main.addRow('Name of column',self.nameWidget)

        if attribute is not None:
            self.attribute = attribute
            self.nameWidget.setText(attribute.display_name)
        else:
            self.attribute = None

        if disable_name:
            self.nameWidget.setEnabled(False)

        self.typeWidget = NonScrollingComboBox()
        for at in Attribute.ATT_TYPES:
            if exclude_tier and at == 'tier':
                continue
            self.typeWidget.addItem(at.title())

        main.addRow('Type of column',self.typeWidget)

        self.useAs = NonScrollingComboBox()
        self.useAs.addItem('Custom column')
        self.useAs.addItem('Spelling')
        self.useAs.addItem('Transcription')
        self.useAs.addItem('Frequency')
        self.useAs.currentIndexChanged.connect(self.updateUseAs)

        for i in range(self.useAs.count()):
            if attribute is not None and self.useAs.itemText(i).lower() == attribute.name:
                self.useAs.setCurrentIndex(i)
                if attribute.name == 'transcription' and attribute.att_type != 'tier':
                    attribute.att_type = 'tier'

        for i in range(self.typeWidget.count()):
            if attribute is not None and self.typeWidget.itemText(i) == attribute.att_type.title():
                self.typeWidget.setCurrentIndex(i)

        main.addRow('Use column as', self.useAs)

        self.setLayout(main)

        self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)

    def type(self):
        return self.typeWidget.currentText().lower()

    def updateUseAs(self):
        t = self.useAs.currentText().lower()
        if t == 'custom column':
            self.typeWidget.setEnabled(True)
        else:
            for i in range(self.typeWidget.count()):
                if t == 'spelling' and self.typeWidget.itemText(i) == 'Spelling':
                    self.typeWidget.setCurrentIndex(i)
                elif t == 'transcription' and self.typeWidget.itemText(i) == 'Tier':
                    self.typeWidget.setCurrentIndex(i)
                elif t == 'frequency' and self.typeWidget.itemText(i) == 'Numeric':
                    self.typeWidget.setCurrentIndex(i)
            self.typeWidget.setEnabled(False)

    def use(self):
        return self.useAs.currentText().lower()

    def value(self):
        display = self.nameWidget.text()
        cat = self.type()
        use = self.use()
        if use.startswith('custom'):
            name = Attribute.sanitize_name(display)
        else:
            name = use
        att = Attribute(name, cat, display)
        return att

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

class EditInventoryWindow(QDialog):

    def __init__(self, inventory, index, orientation, consonants=True):
        super().__init__()
        row_or_col = 'row' if orientation==Qt.Horizontal else 'column'
        self.setWindowTitle('Edit {} properties'.format(row_or_col))
        layout = QVBoxLayout()
        inventoryBox = QVBoxLayout()
        self.sectionNameLineEdit = QLineEdit()
        inventoryBox.addWidget(self.sectionNameLineEdit)
        temp_inventory = namedtuple('tempInventory', ['features', 'possible_values'])
        temp_inventory.features = inventory.features()
        temp_inventory.possible_values = inventory.possible_values()
        self.feature_box = FeatureBox('Features', temp_inventory)
        if orientation == Qt.Vertical:
            header = inventory.getColumnHeader(index, consonants)
            specs = inventory.getColumnSpecs(header, consonants)
        elif orientation == Qt.Horizontal:
            header = inventory.getRowHeader(index, consonants)
            specs = inventory.getRowSpecs(header, consonants)
        self.sectionNameLineEdit.insert(header)
        for key,value in specs[1].items():
            self.feature_box.envList.addItem(value+key)

        inventoryBox.addWidget(self.feature_box)
        ok_button = QPushButton('OK')
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)
        layout.addLayout(inventoryBox)
        layout.addWidget(ok_button)
        layout.addWidget(cancel_button)
        self.setLayout(layout)

    def accept(self):
        self.features = self.feature_box.value()
        self.section_name = self.sectionNameLineEdit.text()
        QDialog.accept(self)

    def reject(self):
        QDialog.reject(self)

class TierWidget(QGroupBox):
    def __init__(self, corpus, parent = None, include_spelling = False):
        QGroupBox.__init__(self,'Tier',parent)
        self.spellingIncluded = include_spelling
        self.spellingEnabled = include_spelling
        layout = QVBoxLayout()

        self.tierSelect = QComboBox()
        self.atts = list()
        self.spellingName = corpus.attributes[0].display_name
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
            if self.tierSelect.itemText(0) != self.spellingName:
                self.tierSelect.insertItem(0,self.spellingName)
        else:
            if self.tierSelect.itemText(0) == self.spellingName:
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
    selectionChanged = Signal()
    def __init__(self, punctuation, title = 'Punctuation to ignore', parent = None):
        QGroupBox.__init__(self, title, parent)

        self.btnGroup = QButtonGroup()
        self.btnGroup.setExclusive(False)
        layout = QVBoxLayout()
        self.warning = QLabel('None detected (other than any transcription delimiters)')
        if len(punctuation) > 0:
            self.warning.hide()
        layout.addWidget(self.warning)
        box = QGridLayout()

        row = 0
        col = 0
        for s in punctuation:
            btn = QPushButton(s)
            btn.clicked.connect(self.selectionChanged.emit)
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

        if len(punctuation) < 2:
            self.checkAll.hide()
            self.uncheckAll.hide()
        buttonlayout.addWidget(self.checkAll, alignment = Qt.AlignLeft)
        buttonlayout.addWidget(self.uncheckAll, alignment = Qt.AlignLeft)
        buttonframe = QFrame()
        buttonframe.setLayout(buttonlayout)

        layout.addWidget(buttonframe)
        self.setLayout(layout)

    def updateButtons(self, to_ignore, emit = True):
        count_visible = 0
        for b in self.btnGroup.buttons():
            if b.text() in to_ignore:
                b.setChecked(False)
                b.hide()
            else:
                b.show()
            if not b.isHidden():
                count_visible += 1
        if count_visible == 0:
            self.warning.show()
        else:
            self.warning.hide()
        if count_visible < 2:
            self.checkAll.hide()
            self.uncheckAll.hide()
        else:
            self.checkAll.show()
            self.uncheckAll.show()
        if emit:
            self.selectionChanged.emit()

    def setPunctuation(self, punc):
        for b in self.btnGroup.buttons():
            if b.text() in punc:
                b.setChecked(True)
        self.selectionChanged.emit()

    def check(self):
        for b in self.btnGroup.buttons():
            b.setChecked(True)
        self.selectionChanged.emit()

    def uncheck(self):
        for b in self.btnGroup.buttons():
            b.setChecked(False)
        self.selectionChanged.emit()

    def value(self):
        value = []
        for b in self.btnGroup.buttons():
            if b.isChecked():
                t = b.text()
                value.append(t)
        return set(value)

class DigraphDialog(QDialog):
    def __init__(self, characters, parent = None):
        QDialog.__init__(self, parent)
        layout = QFormLayout()
        self.digraphLine = QLineEdit()
        layout.addRow(QLabel('Multicharacter segment'),self.digraphLine)
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
        self.setWindowTitle('Construct segment')

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
        QGroupBox.__init__(self,'Multicharacter segments',parent)
        layout = QVBoxLayout()

        self.editField = QLineEdit()
        layout.addWidget(self.editField)
        self.button = QPushButton('Construct a segment')
        self.button.setAutoDefault(False)
        self.button.clicked.connect(self.construct)
        layout.addWidget(self.button)
        self.setLayout(layout)
        self.characters = list()

    def setDigraphs(self, digraphs):
        self.editField.setText(','.join(digraphs))

    def construct(self):
        if len(self.characters) == 0:
            return
        possible = sorted(self.characters, key = lambda x: x.lower())
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
        if len(values) == 0:
            return []
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

class SegmentButton(QPushButton):
    def sizeHint(self):
        sh = QPushButton.sizeHint(self)
        #sh.setHeight(self.fontMetrics().boundingRect(self.text()).height()+14)
        sh.setHeight(135)
        sh.setWidth(self.fontMetrics().boundingRect(self.text()).width()+14)
        return sh

class FeatureEdit(QLineEdit):
    featureEntered = Signal(list)
    featuresFinalized = Signal(list)
    delimPattern = re.compile('([,; ]+)')

    def __init__(self,inventory, clearOnEnter = True, parent=None):
        QLineEdit.__init__(self, parent)
        self.completer = None
        self.clearOnEnter = clearOnEnter
        self.inventory = inventory
        self.valid_strings = self.inventory.valid_feature_strings()

    def setCompleter(self,completer):
        if self.completer is not None:
            self.disconnect(self.completer,0,0)
        self.completer = completer
        if self.completer is None:
            return
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.activated.connect(self.insertCompletion)

    def features(self):
        if self.text() == '':
            return []
        text = self.delimPattern.split(self.text())
        features = [x for x in text if x in self.valid_strings]
        return features

    def parseText(self):
        m = self.delimPattern.search(self.text())
        if m is None:
            d = ''
        else:
            d = m.group(0)
        text = self.delimPattern.split(self.text())
        return d, text

    def finalize(self):
        if self.text() != '':
            self.featuresFinalized.emit(self.features())
            if self.clearOnEnter:
                self.setText('')
                self.featureEntered.emit([])

    def insertCompletion(self, string):
        d, text = self.parseText()
        text[-1] = string
        text = [x for x in text if x in self.valid_strings]
        self.setText(d.join(text))
        self.featureEntered.emit(text)

    def currentFeature(self):
        return self.delimPattern.split(self.text())[-1]

    def keyPressEvent(self,e):
        if self.completer and self.completer.popup().isVisible():
                if e.key() in ( Qt.Key_Space, Qt.Key_Enter,
                                Qt.Key_Return,Qt.Key_Escape,
                                Qt.Key_Tab,Qt.Key_Backtab):
                    e.ignore()
                    return
        else:
            if e.key() in (Qt.Key_Enter, Qt.Key_Return):
                self.finalize()
                return
        isShortcut=((e.modifiers() & Qt.ControlModifier) and e.key()==Qt.Key_E)
        if (self.completer is None or not isShortcut):
            super().keyPressEvent(e)

        if e.key() in (Qt.Key_Space, Qt.Key_Semicolon, Qt.Key_Comma):
            e.ignore()
            return

        d, text = self.parseText()
        self.featureEntered.emit([x for x in text if x in self.valid_strings])

        completionPrefix = self.currentFeature()

        self.completer.update(completionPrefix)
        self.completer.popup().setCurrentIndex(self.completer.completionModel().index(0, 0))

        cr = self.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(0)
                    + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cr)

class FeatureCompleter(QCompleter):
    def __init__(self,inventory,parent=None):
        QCompleter.__init__(self, parent)
        self.stringList = inventory.valid_feature_strings()
        self.setModel(QStringListModel())

    def update(self,completionText):
        to_filter = completionText.lower()
        filtered = [x for x in self.stringList
                        if x.lower().startswith(to_filter)
                        or x[1:].lower().startswith(to_filter)]
        self.model().setStringList(filtered)
        self.popup().setCurrentIndex(self.model().index(0, 0))

class SegmentSelectionWidget(QWidget):
    def __init__(self, inventory, parent = None, exclusive = False):
        QWidget.__init__(self, parent)
        self.inventory = inventory

        self.searchWidget = FeatureEdit(self.inventory)
        self.completer = FeatureCompleter(self.inventory)
        self.searchWidget.setCompleter(self.completer)

        self.inventoryFrame = InventoryBox('', self.inventory)
        if exclusive:
            self.inventoryFrame.setExclusive(True)

        layout = QVBoxLayout()

        if len(inventory.features) > 0:
            headlayout = QHBoxLayout()
            formlay = QFormLayout()

            formlay.addRow('Select by feature',self.searchWidget)

            formframe = QFrame()

            formframe.setLayout(formlay)
            headlayout.addWidget(formframe)

            self.commitButton = QPushButton('Select highlighted')

            headlayout.addWidget(self.commitButton)

            self.clearAllButton = QPushButton('Clear selections')

            headlayout.addWidget(self.clearAllButton)
            headframe = QFrame()

            headframe.setLayout(headlayout)
            self.commitButton.clicked.connect(self.searchWidget.finalize)
            self.clearAllButton.clicked.connect(self.inventoryFrame.clearAll)

        else:
            headframe = QLabel('No feature matrix associated with this corpus.')

        layout.addWidget(headframe)
        layout.addWidget(self.inventoryFrame)
        self.setLayout(layout)

        self.searchWidget.featureEntered.connect(self.inventoryFrame.highlightSegments)
        self.searchWidget.featuresFinalized.connect(self.inventoryFrame.selectSegmentFeatures)

    def setExclusive(self, b):
        self.inventoryFrame.setExclusive(b)

    def select(self, segments):
        self.inventoryFrame.selectSegments(segments)

    def clearAll(self):
        self.inventoryFrame.clearAll()

    def value(self):
        return self.inventoryFrame.value()

class InventoryBox(QWidget):
    def __init__(self, title, inventory, parent=None):
        QWidget.__init__(self,parent)
        self.btnGroup = QButtonGroup()
        self.btnGroup.setExclusive(False)
        self.inventory = inventory

        self.mainLayout = QHBoxLayout()
        cons = self.makeConsTable()
        vow = self.makeVowelTable()
        unk = self.makeUncategorizedTable()
        self.addTables(cons,vow,unk)
        self.setLayout(self.mainLayout)

    def addTables(self,cons,vow,unk):
        if cons is not None:
            self.mainLayout.addWidget(cons)#, alignment = Qt.AlignLeft | Qt.AlignTop)

        if vow is not None:
            self.mainLayout.addWidget(vow, alignment = Qt.AlignLeft | Qt.AlignTop)

        if unk is not None:
            self.mainLayout.addWidget(unk, alignment = Qt.AlignLeft | Qt.AlignTop)

    def makeConsTable(self):
        cons = QFrame()#This widget is what gets returned from this function
        consBox = QVBoxLayout()
        self.consTable = QTableWidget()
        consBox.addWidget(self.consTable)
        cons.setLayout(consBox)

        self.consTable.setColumnCount(len(self.inventory.consColumns))
        self.consTable.setRowCount(len(self.inventory.consRows))
        horizontal_headers = self.inventory.getSortedHeaders(Qt.Horizontal, 'cons')
        self.consTable.setHorizontalHeaderLabels(horizontal_headers)
        vertical_headers = self.inventory.getSortedHeaders(Qt.Vertical, 'cons')
        self.consTable.setVerticalHeaderLabels(vertical_headers)
        self.consTable.resizeColumnsToContents()

        button_map = defaultdict(list)
        for row, col in product(self.inventory.cons_row_header_order.keys(),
                                        self.inventory.cons_column_header_order.keys()):
            row_name = self.inventory.cons_row_header_order[row]
            col_name = self.inventory.cons_column_header_order[col]
            for seg, cat in self.inventory.consList:
                if row_name in cat and col_name in cat:
                    btn = self.generateSegmentButton(seg.symbol)
                    button_map[(row,col)].append(btn)

        for key,buttons in button_map.items():
            row,col = key
            self.consTable.setCellWidget(row,col,MultiSegmentCell(buttons))

        return cons

    def makeVowelTable(self):
        vowel = QFrame() #This widget gets returned from the function
        vowelBox = QGridLayout()
        vowelBox.setAlignment(Qt.AlignTop)
        self.vowelTable = QTableWidget()

        vowelBox.addWidget(self.vowelTable)
        vowel.setLayout(vowelBox)

        self.vowelTable.setColumnCount(len(self.inventory.vowelColumns))
        self.vowelTable.setRowCount(len(self.inventory.vowelRows))
        horizontal_headers = self.inventory.getSortedHeaders(Qt.Horizontal, 'vowel')
        self.vowelTable.setHorizontalHeaderLabels(horizontal_headers)
        vertical_headers = self.inventory.getSortedHeaders(Qt.Vertical, 'vowel')
        self.vowelTable.setVerticalHeaderLabels(vertical_headers)
        self.vowelTable.resizeColumnsToContents()

        button_map = defaultdict(list)
        for row, col in product(self.inventory.vowel_row_header_order.keys(),
                                self.inventory.vowel_column_header_order.keys()):
            row_name = self.inventory.vowel_row_header_order[row]
            col_name = self.inventory.vowel_column_header_order[col]
            row -= self.inventory.vowel_row_offset
            col -= self.inventory.vowel_column_offset
            for seg, cat in self.inventory.vowelList:
                if row_name in cat and col_name in cat:
                    btn = self.generateSegmentButton(seg.symbol)
                    button_map[(row, col)].append(btn)

        for key, buttons in button_map.items():
            row, col = key
            self.vowelTable.setCellWidget(row, col, MultiSegmentCell(buttons))

        return vowel

    def makeUncategorizedTable(self):
        unk = QGroupBox('Uncategorized')
        unk.setFlat(True)
        # unk.setCheckable(True)
        # unk.setChecked(False)
        # unk.toggled.connect(self.showHideUnk)
        self.unkTable = QGridLayout()
        unk.setLayout(self.unkTable)

        unkRow = 0
        unkCol = -1
        for s in self.inventory.uncategorized:
            btn = SegmentButton(s.symbol)
            btn.setCheckable(True)
            btn.setAutoExclusive(False)
            btn.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
            self.btnGroup.addButton(btn)

            unkCol += 1
            if unkCol > 11:
                unkCol = 0
                unkRow += 1
            self.unkTable.addWidget(btn,unkRow,unkCol)
        return unk

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

    def highlightSegments(self, features):
        segs = self.inventory.features_to_segments(features)
        for btn in self.btnGroup.buttons():
            btn.setStyleSheet("QPushButton{}")
            if features and btn.text() in segs:
                btn.setStyleSheet("QPushButton{background-color: red;}")

    def selectSegmentFeatures(self, features):
        segs = self.inventory.features_to_segments(features)
        self.selectSegments(segs)

    def selectSegments(self, segs):
        if len(segs) > 0:
            for btn in self.btnGroup.buttons():
                if btn.text() in segs:
                    btn.setChecked(True)

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
            return tuple(value)

class MultiSegmentCell(QWidget):

    def __init__(self,buttons,parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.button_names = list()
        for b in buttons:
            layout.addWidget(b)
            self.button_names.append(b.text())

        self.setLayout(layout)

    def __str__(self):
        return ','.join(self.button_names)

class TranscriptionWidget(QGroupBox):
    transcriptionChanged = Signal(object)
    def __init__(self, title,corpus,inventory,parent=None):
        QGroupBox.__init__(self,title,parent)
        self.inventory = inventory
        self.corpus = corpus
        layout = QFormLayout()

        self.transEdit = QLineEdit()
        self.transEdit.textChanged.connect(self.transcriptionChanged.emit)
        self.showInv = QPushButton('Show inventory')
        self.showInv.setAutoDefault(False)
        self.showInv.clicked.connect(self.showHide)
        layout.addRow(self.transEdit,self.showInv)

        self.segments = InventoryBox('Inventory', inventory)
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

class AbstractPairDialog(QDialog):
    rowToAdd = Signal(object)
    def __init__(self, inventory, parent = None):
        QDialog.__init__(self, parent)
        self.inventory = inventory


class FeatureBox(QWidget):
    def __init__(self, title,inventory,parent=None):
        QWidget.__init__(self,parent)

        #self.inventory = inventory
        self.features = inventory.features
        self.values = inventory.possible_values
        layout = QHBoxLayout()

        #layout.setSizeConstraint(QLayout.SetFixedSize)

        self.featureList = QListWidget()

        for f in sorted(self.features):
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
            return list()
        return val

class SegmentPairDialog(QDialog):
    def __init__(self, corpus, parent=None):
        QDialog.__init__(self,parent)

        layout = QVBoxLayout()

        self.inventoryFrame = SegmentSelectionWidget(inventory)

        layout.addWidget(self.inventoryFrame)

        self.setLayout(layout)

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

    def one(self):
        self.addOneMore = False
        self.accept()

    def another(self):
        self.addOneMore = True
        self.accept()

    def reject(self):
        self.addOneMore = False
        QDialog.reject(self)

class SegmentPairDialog(AbstractPairDialog):
    def __init__(self, inventory, parent = None):
        AbstractPairDialog.__init__(self, inventory, parent)
        self.inventoryFrame = SegmentSelectionWidget(inventory)
        self.setLayout(QHBoxLayout())
        self.layout().insertWidget(0, self.inventoryFrame)

        self.setWindowTitle('Select segment pair')

    def reset(self):
        self.inventoryFrame.clearAll()

    def accept(self):
        selected = self.inventoryFrame.value()
        self.rowToAdd.emit(combinations(selected,2))
        QDialog.accept(self)

class SingleSegmentDialog(SegmentPairDialog):
    def __init__(self, inventory, parent = None):
        SegmentPairDialog.__init__(self, inventory, parent)
        self.setWindowTitle('Select individual segments')

    def accept(self):
        selected = self.inventoryFrame.value()
        self.rowToAdd.emit([(x,) for x in selected])
        QDialog.accept(self)


class FeaturePairDialog(AbstractPairDialog):
    def __init__(self, inventory, parent = None):
        AbstractPairDialog.__init__(self, inventory,parent)

        self.setLayout(QVBoxLayout())

        mainlayout = QFormLayout()

        self.featureWidget = FeatureEdit(self.inventory, clearOnEnter = False)
        self.featureWidget.valid_strings = self.inventory.features
        self.featureCompleter = FeatureCompleter(self.inventory)
        self.featureCompleter.stringList = self.inventory.features
        self.featureWidget.setCompleter(self.featureCompleter)
        self.featureWidget.featureEntered.connect(self.updateSegments)

        mainlayout.addRow('Feature to make pairs',self.featureWidget)

        self.searchWidget = FeatureEdit(self.inventory, clearOnEnter = False)
        self.completer = FeatureCompleter(self.inventory)
        self.searchWidget.setCompleter(self.completer)
        self.searchWidget.featureEntered.connect(self.updateSegments)

        mainlayout.addRow('Filter pairs', self.searchWidget)

        self.layout().insertLayout(0,mainlayout)

        seglayout = QHBoxLayout()
        scroll = QScrollArea()
        self.columnFrame = QWidget()
        self.columns = []
        lay = QBoxLayout(QBoxLayout.LeftToRight)
        lay.addStretch()
        self.columnFrame.setLayout(lay)
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.columnFrame)
        scroll.setMinimumWidth(140)
        scroll.setMinimumHeight(140)
        policy = scroll.sizePolicy()
        policy.setVerticalStretch(1)
        scroll.setSizePolicy(policy)
        seglayout.addWidget(scroll)


        self.layout().insertLayout(1, seglayout)

        self.setWindowTitle('Select feature pair')

    def updateSegments(self, features = None):
        for i in reversed(range(self.columnFrame.layout().count()-1)):
            w = self.columnFrame.layout().itemAt(i).widget()
            if w is None:
                del w
                continue
            w.setParent(None)
            w.deleteLater()
        features = self.featureWidget.features()
        if len(features) == 0:
            return
        others = self.searchWidget.features()
        feature_values = self.inventory.find_min_feature_pairs(features, others)
        values = sorted(feature_values.keys())
        if len(values) == 0:
            return
        self.columns = []
        for i, a in reversed(list(enumerate(values))):
            label = [values[i][j] + features[j] for j in range(len(features))]
            c = QGroupBox('Segment set {} ({})'.format(i+1, ', '.join(label)))
            layout = QVBoxLayout()
            label = QLabel('\n'.join(map(str,feature_values[values[i]])))
            layout.addWidget(label)
            c.setLayout(layout)
            self.columns.append(label)
            self.columnFrame.layout().insertWidget(0, c)

    def reset(self):
        self.featureWidget.setText('')
        self.searchWidget.setText('')
        self.updateSegments()

    def accept(self):
        selected = [tuple(x.text().split('\n')) for x in self.columns]
        self.rowToAdd.emit(combinations(selected,2))
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
    def __init__(self,inventory, parent = None, features = True, single_segment = False):
        QGroupBox.__init__(self,'Segments',parent)

        self.inventory = inventory

        vbox = QVBoxLayout()
        self.addSingleButton = QPushButton('Add individual segments')
        self.addSingleButton.clicked.connect(self.singleSegPopup)
        self.addButton = QPushButton('Add pair of segments')
        self.addButton.clicked.connect(self.segPairPopup)
        #self.addSetButton = QPushButton('Add pair of segment sets')
        #self.addSetButton.clicked.connect(self.segSetPairPopup)
        self.addFeatButton = QPushButton('Add pair of features')
        self.addFeatButton.clicked.connect(self.featurePairPopup)
        self.removeButton = QPushButton('Remove selected segment pair')
        self.removeButton.clicked.connect(self.removePair)
        self.addSingleButton.setAutoDefault(False)
        self.addButton.setAutoDefault(False)
        #self.addSetButton.setDefault(False)
        self.addFeatButton.setDefault(False)
        self.addButton.setDefault(False)
        self.removeButton.setAutoDefault(False)
        self.removeButton.setDefault(False)

        self.table = SegPairTableWidget()
        if single_segment:
            vbox.addWidget(self.addSingleButton)
        vbox.addWidget(self.addButton)
        #vbox.addWidget(self.addSetButton)
        if features:
            if len(self.inventory.features) == 0:
                self.addFeatButton.setEnabled(False)
            vbox.addWidget(self.addFeatButton)

        vbox.addWidget(self.removeButton)
        vbox.addWidget(self.table)
        self.setLayout(vbox)

        #self.setFixedWidth(self.minimumSizeHint().width())

    def singleSegPopup(self):
        dialog = SingleSegmentDialog(self.inventory)
        dialog.rowToAdd.connect(self.addPairs)
        addOneMore = True
        while addOneMore:
            dialog.reset()
            result = dialog.exec_()
            addOneMore = dialog.addOneMore

    def featurePairPopup(self):
        dialog = FeaturePairDialog(self.inventory)
        dialog.rowToAdd.connect(self.addPairs)
        addOneMore = True
        while addOneMore:
            dialog.reset()
            result = dialog.exec_()
            addOneMore = dialog.addOneMore


    def segSetPairPopup(self):
        dialog = SegmentSetPairDialog(self.inventory)
        dialog.rowToAdd.connect(self.addPairs)
        addOneMore = True
        while addOneMore:
            dialog.reset()
            result = dialog.exec_()
            addOneMore = dialog.addOneMore

    def segPairPopup(self):
        dialog = SegmentPairDialog(self.inventory)
        dialog.rowToAdd.connect(self.addPairs)
        addOneMore = True
        while addOneMore:
            dialog.reset()
            result = dialog.exec_()
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

class BigramDialog(QDialog):
    rowToAdd = Signal(object)
    def __init__(self, inventory, parent = None):
        QDialog.__init__(self,parent)

        self.inventory = inventory

        layout = QVBoxLayout()

        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.lhsEnvFrame = QGroupBox('Left hand side')

        self.rhsEnvFrame = QGroupBox('Right hand side')

        lhsEnvLayout = QVBoxLayout()

        lhsEnvLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        rhsEnvLayout = QVBoxLayout()

        rhsEnvLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.lhs = SegmentSelectionWidget(self.inventory, exclusive = True)

        self.rhs = SegmentSelectionWidget(self.inventory, exclusive = True)

        lhsEnvLayout.addWidget(self.lhs)
        rhsEnvLayout.addWidget(self.rhs)

        self.lhsEnvFrame.setLayout(lhsEnvLayout)

        self.rhsEnvFrame.setLayout(rhsEnvLayout)
        envFrame = QFrame()

        envLayout = QHBoxLayout()

        envLayout.addWidget(self.lhsEnvFrame)
        envLayout.addWidget(self.rhsEnvFrame)

        envFrame.setLayout(envLayout)

        layout.addWidget(envFrame)

        self.oneButton = QPushButton('Add')
        self.anotherButton = QPushButton('Add and create another')
        self.cancelButton = QPushButton('Cancel')
        self.acLayout = QHBoxLayout()
        self.acLayout.addWidget(self.oneButton, alignment = Qt.AlignLeft)
        self.acLayout.addWidget(self.anotherButton, alignment = Qt.AlignLeft)
        self.acLayout.addWidget(self.cancelButton, alignment = Qt.AlignLeft)
        self.oneButton.clicked.connect(self.one)
        self.anotherButton.clicked.connect(self.another)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(self.acLayout)

        layout.addWidget(acFrame, alignment = Qt.AlignLeft)
        self.addOneMore = False
        self.setLayout(layout)
        #self.setFixedSize(self.sizeHint())
        self.setWindowTitle('Create bigram')

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
        lhs = self.lhs.value()
        rhs = self.rhs.value()

        if lhs == '':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a left hand of the bigram.")
            return
        if rhs == '':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a right hand of the bigram.")
            return

        env = lhs, rhs
        self.rowToAdd.emit([env])
        if not self.addOneMore:
            QDialog.accept(self)
        else:
            self.reset()


class SegFeatSelect(QGroupBox):
    def __init__(self,corpus, title, parent = None, exclusive = False):
        QGroupBox.__init__(self,title,parent)
        self.segExclusive = exclusive
        self.corpus = corpus
        self.inventory = self.corpus.inventory
        self.features = list()
        for i in self.inventory:
            if len(i.features.keys()) > 0:
                self.features = [x for x in i.features.keys()]
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

        self.sel = InventoryBox('',self.corpus)
        self.sel.setExclusive(self.segExclusive)

        layout.addWidget(self.sel)

        self.setLayout(layout)

    def generateFrame(self):
        self.sel.deleteLater()
        if self.typeSelect.currentText() == 'Segments':
            self.sel = InventoryBox('',self.corpus)
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
    rowToAdd = Signal(str)
    def __init__(self, inventory,parent=None):
        QDialog.__init__(self,parent)

        self.inventory = inventory

        layout = QVBoxLayout()

        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.lhsEnvFrame = QGroupBox('Left hand side')

        self.rhsEnvFrame = QGroupBox('Right hand side')

        lhsEnvLayout = QVBoxLayout()

        lhsEnvLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        rhsEnvLayout = QVBoxLayout()

        rhsEnvLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.lhs = SegmentSelectionWidget(self.inventory, exclusive = True)

        self.rhs = SegmentSelectionWidget(self.inventory, exclusive = True)

        lhsEnvLayout.addWidget(self.lhs)
        rhsEnvLayout.addWidget(self.rhs)

        self.lhsEnvFrame.setLayout(lhsEnvLayout)

        self.rhsEnvFrame.setLayout(rhsEnvLayout)
        envFrame = QFrame()

        envLayout = QHBoxLayout()

        envLayout.addWidget(self.lhsEnvFrame)
        envLayout.addWidget(self.rhsEnvFrame)

        envFrame.setLayout(envLayout)

        layout.addWidget(envFrame)

        self.oneButton = QPushButton('Add')
        self.anotherButton = QPushButton('Add and create another')
        self.cancelButton = QPushButton('Cancel')
        self.acLayout = QHBoxLayout()
        self.acLayout.addWidget(self.oneButton, alignment = Qt.AlignLeft)
        self.acLayout.addWidget(self.anotherButton, alignment = Qt.AlignLeft)
        self.acLayout.addWidget(self.cancelButton, alignment = Qt.AlignLeft)
        self.oneButton.clicked.connect(self.one)
        self.anotherButton.clicked.connect(self.another)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(self.acLayout)

        layout.addWidget(acFrame, alignment = Qt.AlignLeft)
        self.addOneMore = False
        self.setLayout(layout)
        #self.setFixedSize(self.sizeHint())
        self.setWindowTitle('Create bigram')

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
        lhs = self.lhs.value()
        rhs = self.rhs.value()

        if lhs == '':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a left hand of the bigram.")
            return
        if rhs == '':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a right hand of the bigram.")
            return

        env = lhs, rhs
        self.rowToAdd.emit([env])
        if not self.addOneMore:
            QDialog.accept(self)
        else:
            self.reset()

class SegmentSetPairDialog(BigramDialog):
    def __init__(self, inventory, parent = None):
        BigramDialog.__init__(self, inventory, parent)
        self.lhsEnvFrame.setTitle('First set')
        self.rhsEnvFrame.setTitle('Second set')
        self.setWindowTitle('Create pairs of segment sets')
        self.lhs.setExclusive(False)
        self.rhs.setExclusive(False)

class SegmentSelectDialog(QDialog):
    def __init__(self, inventory, selected = None, parent=None):
        QDialog.__init__(self,parent)

        layout = QVBoxLayout()

        segFrame = QFrame()

        segLayout = QHBoxLayout()

        self.segFrame = SegmentSelectionWidget(inventory)

        if selected is not None:
            self.segFrame.select(selected)

        segLayout.addWidget(self.segFrame)

        segFrame.setLayout(segLayout)

        layout.addWidget(segFrame)


        self.acceptButton = QPushButton('Ok')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton, alignment = Qt.AlignLeft)
        acLayout.addWidget(self.cancelButton, alignment = Qt.AlignLeft)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame, alignment = Qt.AlignLeft)

        self.setLayout(layout)
        self.setWindowTitle('Select segments')

    def value(self):
        return self.segFrame.value()

    def reset(self):
        self.segFrame.clearAll()


class EnvironmentSegmentWidget(QWidget):
    def __init__(self, inventory, parent = None, middle = False, enabled = True):
        QWidget.__init__(self, parent)
        self.inventory = inventory
        self.segments = set()
        self.enabled = enabled

        self.middle = middle

        layout = QVBoxLayout()
        if self.middle:
            lab = '_\n\n{}'
        else:
            lab = '{}'
        self.mainLabel = QLabel(lab)
        self.mainLabel.setMargin(4)
        self.mainLabel.setFrameShape(QFrame.Box)
        self.mainLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        layout.addWidget(self.mainLabel)

        self.setLayout(layout)

        self.mainLabel.setContextMenuPolicy(Qt.CustomContextMenu)
        self.mainLabel.customContextMenuRequested.connect(self.showMenu)

    def mouseReleaseEvent(self, ev):
        if not self.enabled:
            ev.ignore()
            return
        if ev.button() == Qt.LeftButton:
            self.selectSegments()
            ev.accept()

    def updateLabel(self):
        if self.middle:
            lab = '_\n\n{%s}'
        else:
            lab = '{%s}'
        lab = lab % ', '.join(self.segments)
        self.mainLabel.setText(lab)

    def selectSegments(self):
        dialog = SegmentSelectDialog(self.inventory, self.segments, self)
        if dialog.exec_():
            self.segments = dialog.value()
            self.updateLabel()

    def showMenu(self, pos):
        if self.middle:
            return
        removeAction = QAction(self)
        removeAction.setText('Delete')
        removeAction.triggered.connect(self.deleteLater)

        menu = QMenu(self)
        menu.addAction(removeAction)

        menu.popup(self.mapToGlobal(pos))

    def value(self):
        return self.segments

class EnvironmentWidget(QWidget):
    def __init__(self, inventory, parent = None, middle = True):
        QWidget.__init__(self, parent)
        self.inventory = inventory
        layout = QHBoxLayout()

        self.lhsAddNew = QPushButton('+')

        self.lhsAddNew.clicked.connect(self.addLhs)

        self.lhsWidget = QWidget()

        lhslayout = QHBoxLayout()
        self.lhsWidget.setLayout(lhslayout)

        self.rhsAddNew = QPushButton('+')

        self.rhsAddNew.clicked.connect(self.addRhs)

        self.rhsWidget = QWidget()

        rhslayout = QHBoxLayout()
        self.rhsWidget.setLayout(rhslayout)

        self.middleWidget = EnvironmentSegmentWidget(self.inventory, middle = True, enabled = middle)

        self.removeButton = QPushButton('Remove environment')

        self.removeButton.clicked.connect(self.deleteLater)

        layout.addWidget(self.lhsAddNew)
        layout.addWidget(self.lhsWidget)
        layout.addWidget(self.middleWidget)
        layout.addWidget(self.rhsWidget)
        layout.addWidget(self.rhsAddNew)

        layout.addStretch()

        optionlayout = QVBoxLayout()

        optionlayout.addWidget(self.removeButton)

        layout.addLayout(optionlayout)

        self.setLayout(layout)

    def addLhs(self):
        segWidget = EnvironmentSegmentWidget(self.inventory)
        self.lhsWidget.layout().insertWidget(0,segWidget)

    def addRhs(self):
        segWidget = EnvironmentSegmentWidget(self.inventory)
        self.rhsWidget.layout().addWidget(segWidget)

    def value(self):
        lhs = []
        for ind in range(self.lhsWidget.layout().count()):
            wid = self.lhsWidget.layout().itemAt(ind).widget()
            lhs.append(wid.value())
        rhs = []
        for ind in range(self.rhsWidget.layout().count()):
            wid = self.rhsWidget.layout().itemAt(ind).widget()
            rhs.append(wid.value())
        middle = self.middleWidget.value()

        return EnvironmentFilter(middle, lhs, rhs)

class EnvironmentSelectWidget(QGroupBox):
    def __init__(self, inventory, parent = None, middle = True):
        QGroupBox.__init__(self,'Environments',parent)
        self.middle = middle
        self.inventory = inventory

        layout = QVBoxLayout()

        scroll = QScrollArea()
        self.environmentFrame = QWidget()
        lay = QBoxLayout(QBoxLayout.TopToBottom)
        self.addButton = QPushButton('New environment')
        self.addButton.clicked.connect(self.addNewEnvironment)
        lay.addWidget(self.addButton)
        lay.addStretch()
        self.environmentFrame.setLayout(lay)
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.environmentFrame)
        scroll.setMinimumWidth(140)
        scroll.setMinimumHeight(200)

        policy = scroll.sizePolicy()
        policy.setVerticalStretch(1)
        scroll.setSizePolicy(policy)
        layout.addWidget(scroll)

        self.setLayout(layout)

    def addNewEnvironment(self):
        envWidget = EnvironmentWidget(self.inventory, middle = self.middle)
        pos = self.environmentFrame.layout().count() - 2
        self.environmentFrame.layout().insertWidget(pos,envWidget)

    def value(self):
        envs = []
        for ind in range(self.environmentFrame.layout().count() - 2):
            wid = self.environmentFrame.layout().itemAt(ind).widget()
            envs.append(wid.value())
        return envs


class BigramWidget(QGroupBox):
    def __init__(self,inventory,parent=None):
        QGroupBox.__init__(self,'Bigrams',parent)

        self.inventory = inventory
        vbox = QVBoxLayout()

        self.addButton = QPushButton('Add bigram')
        self.addButton.clicked.connect(self.envPopup)
        self.removeButton = QPushButton('Remove selected bigrams')
        self.removeButton.clicked.connect(self.removeEnv)
        self.addButton.setAutoDefault(False)
        self.addButton.setDefault(False)
        self.removeButton.setAutoDefault(False)
        self.removeButton.setDefault(False)

        self.table = TableWidget()
        self.table.setSortingEnabled(False)

        self.table.horizontalHeader().setSectionsClickable(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setModel(EnvironmentModel())
        #self.table.resizeColumnsToContents()

        vbox.addWidget(self.addButton)
        vbox.addWidget(self.removeButton)
        vbox.addWidget(self.table)

        self.setLayout(vbox)

    def addRows(self, rows):
        if isinstance(rows, list):
            for row in rows:
                self.table.model().addRow([row])
        else:
            self.table.model().addRow([row])

    def envPopup(self):
        dialog = BigramDialog(self.inventory,self)
        dialog.rowToAdd.connect(self.addRows)
        result = dialog.exec_()
        dialog.rowToAdd.disconnect()
        dialog.deleteLater()

    def removeEnv(self):
        select = self.table.selectionModel()
        if select.hasSelection():
            selected = select.selectedRows()
            self.table.model().removeRows([s.row() for s in selected])

    def value(self):
        return [x[0] for x in self.table.model().rows]

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

class RestrictedContextWidget(RadioSelectWidget):
    canonical = 'Use canonical forms only'
    frequent = 'Use most frequent forms only'
    canonical_value = 'canonical form'
    frequent_value = 'most frequent variant'
    def __init__(self, corpus, actions = None, parent = None):
        typetokenEnabled = {self.canonical: corpus.has_transcription,
                    self.frequent: corpus.has_wordtokens}
        RadioSelectWidget.__init__(self,'Pronunciation variants',
                                            OrderedDict([(self.canonical, self.canonical_value),
                                            (self.frequent, self.frequent_value)]),
                                            actions,
                                            typetokenEnabled)

class ContextWidget(RestrictedContextWidget):
    separate = 'Count each word token as a separate entry'
    relative = 'Weight each word type\nby the relative frequency of its variants'
    separate_value = 'separate token variants'
    relative_value = 'relative type variants'
    def __init__(self, corpus, actions = None, parent = None):
        typetokenEnabled = {self.canonical: corpus.has_transcription,
                    self.frequent: corpus.has_wordtokens,
                    self.separate: corpus.has_wordtokens,
                    self.relative: corpus.has_wordtokens}
        RadioSelectWidget.__init__(self,'Pronunciation variants',
                                            OrderedDict([(self.canonical, self.canonical_value),
                                            (self.frequent, self.frequent_value),
                                            (self.separate, self.separate_value),
                                            (self.relative, self.relative_value)
                                            ]),
                                            actions,
                                            typetokenEnabled)

class CreateClassWidget(QDialog):
    def __init__(self, parent, corpus, inventory, class_type=None, default_name=None):
        QDialog.__init__(self, parent)

        self.corpus = corpus
        self.inventory = inventory
        self.class_type = class_type

        self.mainLayout = QVBoxLayout()

        if self.class_type == 'tier':
            explanation = ('You can create Tiers in this window. A Tier is subpart of a word that consists only of '
            'the segments you want, maintaining their original ordering. You can define the properties of the Tier below. '
            'Tiers are commonly created on the basis of a feature class, e.g. all the vowels or of all the obstruents in a word. '
            'PCT will allow you to create Tiers consisting of any arbitrary set of segments.\n'
            'Once created, the Tier will be added as a column in your corpus, and it will be visible in the main window. '
            'You can then select this Tier inside of certain analysis functions.')
        elif self.class_type == 'class':
            explanation = QLabel(('You can create Classes in this window. A Class is simply a set of segments from the inventory '
            'of your corpus. Classes are normally created on the basis of shared phonological _features, in which case they are '
            'usually called  \"natural\" classes. An arbitrary set of segments with no common _features may be called \"unnatural\".\n'
            'PCT allows the creation of classes of either type. Once created, Classes can be selected from within certain analysis functions. '
            'Classes can also be used to organize the inventory chart for your corpus'))
        elif self.class_type == 'inventory':
            self.class_type = 'row or column'
            explanation = ('This window allows you to specify the details of the column or row you selected in your '
                            'inventory. You can change the name, and you can set a filter for which kinds of segments '
                            'should appear in this column or row.')
        else:
            explanation = ''

        explanation = QLabel(explanation)

        explanation.setWordWrap(True)
        self.mainLayout.addWidget(explanation)

        self.nameFrame = QGroupBox('Name of {}'.format(self.class_type))
        self.nameEdit = QLineEdit()
        nameLayout = QFormLayout()
        nameLayout.addRow(self.nameEdit)
        if default_name is not None:
            self.nameEdit.setText(default_name)
        self.nameFrame.setLayout(nameLayout)
        self.mainLayout.addWidget(self.nameFrame)

        self.defineFrame = SegmentSelectionWidget(inventory)

        self.mainLayout.addWidget(self.defineFrame)

        self.createButton = QPushButton('Create {}'.format(self.class_type))
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.createButton)
        acLayout.addWidget(self.cancelButton)
        self.createButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        self.mainLayout.addWidget(acFrame)

        self.setLayout(self.mainLayout)

        self.setWindowTitle('Create {}'.format(self.class_type))

    def generateClass(self):
        previewList = self.defineFrame.value()
        notInPreviewList = [x for x in self.inventory.segs if x not in previewList]
        return previewList, notInPreviewList

    def preview(self):
        inClass, notInClass = self.generateClass()
        reply = QMessageBox.information(self,
                "{} preview".format(self.class_type),
                "Segments included: {}\nSegments excluded: {}".format(', '.join(inClass),
                                                                      ', '.join(notInClass)))

