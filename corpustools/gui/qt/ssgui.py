
from PyQt5.QtCore import pyqtSignal as Signal,QThread
from PyQt5.QtWidgets import (QDialog, QListWidget, QGroupBox, QHBoxLayout,
                            QVBoxLayout, QPushButton, QFrame, QGridLayout,
                            QRadioButton, QLabel, QFormLayout, QLineEdit,
                            QFileDialog, QComboBox,QProgressDialog, QCheckBox)

from collections import OrderedDict

from corpustools.symbolsim.string_similarity import string_similarity
from corpustools.symbolsim.io import read_pairs_file
from .widgets import RadioSelectWidget, FileWidget

class SSWorker(QThread):
    updateProgress = Signal(str)

    dataReady = Signal(object)

    def __init__(self):
        QThread.__init__(self)

    def setParams(self, kwargs):
        self.kwargs = kwargs

    def run(self):
        kwargs = self.kwargs
        self.results = string_similarity(kwargs['corpus'], kwargs['query'],
                                        kwargs['relator_type'],
                                                string_type = kwargs['string_type'],
                                                tier_name = kwargs['tier_name'],
                                                count_what = kwargs['count_what'],
                                                min_rel = kwargs['min_rel'],
                                                max_rel = kwargs['max_rel'])
        self.dataReady.emit(self.results)

class SSDialog(QDialog):
    header = ['Word 1',
                'Word 2',
                'Result',
                'String type',
                'Type or token',
                'Algorithm type']
    def __init__(self, parent, corpus):
        QDialog.__init__(self, parent)

        self.corpus = corpus
        layout = QVBoxLayout()

        sslayout = QHBoxLayout()

        self.algorithmWidget = RadioSelectWidget('String similarity algorithm',
                                            OrderedDict([('Khorsi','khorsi'),
                                            ('Edit distance','edit_distance'),
                                            ('Phonological edit distance','phono_edit_distance')]),
                                            {'Khorsi':self.khorsiSelected,
                                            'Edit distance':self.editDistSelected,
                                            'Phonological edit distance':self.phonoEditDistSelected})


        sslayout.addWidget(self.algorithmWidget)

        compFrame = QGroupBox('Comparison type')

        vbox = QFormLayout()
        self.compType = None
        self.oneWordRadio = QRadioButton('Compare one word to entire corpus')
        self.oneWordRadio.clicked.connect(self.oneWordSelected)
        self.oneWordEdit = QLineEdit()
        self.oneWordEdit.textChanged.connect(self.oneWordRadio.click)
        self.twoWordRadio = QRadioButton('Compare a single pair of words to each other')
        self.twoWordRadio.clicked.connect(self.twoWordsSelected)
        self.wordOneEdit = QLineEdit()
        self.wordOneEdit.textChanged.connect(self.twoWordRadio.click)
        self.wordTwoEdit = QLineEdit()
        self.wordTwoEdit.textChanged.connect(self.twoWordRadio.click)
        self.fileRadio = QRadioButton('Compare a list of pairs of words')
        self.fileRadio.clicked.connect(self.fileSelected)
        self.fileWidget = FileWidget('Select a word pairs file', 'Text file (*.txt *.csv)')
        self.fileWidget.textChanged.connect(self.fileRadio.click)

        vbox.addRow(self.oneWordRadio)
        vbox.addRow(self.oneWordEdit)
        vbox.addRow(self.twoWordRadio)
        vbox.addRow('Word 1:',self.wordOneEdit)
        vbox.addRow('Word 2:',self.wordTwoEdit)
        vbox.addRow(self.fileRadio)
        vbox.addRow(self.fileWidget)

        compFrame.setLayout(vbox)

        sslayout.addWidget(compFrame)

        optionFrame = QGroupBox('Options')

        optionLayout = QVBoxLayout()

        self.typeTokenWidget = RadioSelectWidget('Type or token',
                                            {'Count types':'type',
                                            'Count tokens':'token'})

        optionLayout.addWidget(self.typeTokenWidget)

        self.stringTypeWidget = RadioSelectWidget('String type',
                                            {'Compare spelling':'spelling',
                                            'Compare transcription':'transcription'})

        optionLayout.addWidget(self.stringTypeWidget)

        threshFrame = QGroupBox('Return only results between...')

        self.minEdit = QLineEdit()
        self.maxEdit = QLineEdit()

        vbox = QFormLayout()
        vbox.addRow('Minimum:',self.minEdit)
        vbox.addRow('Maximum:',self.maxEdit)

        threshFrame.setLayout(vbox)

        optionLayout.addWidget(threshFrame)


        optionFrame.setLayout(optionLayout)

        sslayout.addWidget(optionFrame)

        ssFrame = QFrame()
        ssFrame.setLayout(sslayout)

        layout.addWidget(ssFrame)

        self.newTableButton = QPushButton('Calculate string similarity\n(start new results table)')
        self.oldTableButton = QPushButton('Calculate string similarity\n(add to current results table)')
        self.cancelButton = QPushButton('Cancel')
        self.aboutButton = QPushButton('About this function...')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.newTableButton)
        acLayout.addWidget(self.oldTableButton)
        acLayout.addWidget(self.cancelButton)
        acLayout.addWidget(self.aboutButton)
        self.newTableButton.clicked.connect(self.newTable)
        self.oldTableButton.clicked.connect(self.oldTable)
        self.aboutButton.clicked.connect(self.about)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('String similarity')

        self.thread = SSWorker()

    def oneWordSelected(self):
        self.compType = 'one'

    def twoWordsSelected(self):
        self.compType = 'two'

    def fileSelected(self):
        self.compType = 'file'

    def calcSS(self):
        if self.minEdit.text() == '':
            min_rel = None
        else:
            min_rel = float(self.minEdit.text())
        if self.maxEdit.text() == '':
            max_rel = None
        else:
            max_rel = float(self.maxEdit.text())
        kwargs = {'corpus':self.corpus,
                'relator_type':self.algorithmWidget.value(),
                'string_type':self.stringTypeWidget.value(),
                'tier_name':self.stringTypeWidget.value(),
                'count_what':self.typeTokenWidget.value(),
                'min_rel':min_rel,
                'max_rel':max_rel}
        if self.compType == 'one':
            kwargs['query'] = self.oneWordEdit.text()
        elif self.compType == 'two':
            kwargs['query'] = (self.wordOneEdit.text(),self.wordTwoEdit.text())
        elif self.compType == 'file':
            kwargs['query'] = read_pairs_file(pairs_path)
        self.thread.setParams(kwargs)

        dialog = QProgressDialog('Calculating string similarity...','Cancel',0,0)
        self.thread.dataReady.connect(self.setResults)
        self.thread.dataReady.connect(dialog.accept)

        self.thread.start()

        result = dialog.exec_()
        if result:
            self.accept()
        else:
            self.thread.terminate()

    def setResults(self, results):
        self.results = list()
        for result in results:
            w1, w2, similarity = result
            if not isinstance(w1,str):
                w1 = w1.spelling
            if not isinstance(w2,str):
                w2 = w2.spelling
            if self.algorithmWidget.value() != 'khorsi':
                typetoken = 'N/A'
            else:
                typetoken = self.typeTokenWidget.value()
            self.results.append([w1, w2, similarity,
                        self.stringTypeWidget.value(), typetoken,
                        self.algorithmWidget.value()])


    def newTable(self):
        self.update = False
        self.calcSS()

    def oldTable(self):
        self.update = True
        self.calcSS()

    def about(self):
        pass

    def khorsiSelected(self):
        self.stringTypeWidget.enable()
        self.typeTokenWidget.enable()

    def editDistSelected(self):
        self.stringTypeWidget.enable()
        self.typeTokenWidget.disable()

    def phonoEditDistSelected(self):
        self.stringTypeWidget.disable()
        self.typeTokenWidget.disable()
