
from PyQt5.QtCore import pyqtSignal as Signal,QThread
from PyQt5.QtWidgets import (QDialog, QListWidget, QGroupBox, QHBoxLayout,
                            QVBoxLayout, QPushButton, QFrame, QGridLayout,
                            QRadioButton, QLabel, QFormLayout, QLineEdit,
                            QFileDialog, QComboBox, QCheckBox, QProgressDialog)

from collections import OrderedDict

from .widgets import SegmentPairSelectWidget, RadioSelectWidget, FileWidget

from corpustools.freqalt.freq_of_alt import calc_freq_of_alt

class FAWorker(QThread):
    updateProgress = Signal(str)

    dataReady = Signal(object)

    def __init__(self):
        QThread.__init__(self)

    def setParams(self, kwargs):
        self.kwargs = kwargs

    def run(self):
        kwargs = self.kwargs
        self.results = list()
        if kwargs['pair_behavior'] == 'individual':

            for pair in kwargs['segment_pairs']:
                res = calc_freq_of_alt(kwargs['corpus'], pair[0], pair[1],
                                kwargs['relator_type'], kwargs['count_what'],
                                min_rel=kwargs['min_rel'], max_rel=kwargs['max_rel'],
                                min_pairs_okay=kwargs['include_minimal_pairs'],
                                from_gui=True, phono_align=kwargs['phono_align'],
                                output_filename=kwargs['output_filename'])

                self.results.append(res)
        else:
            raise(NotImplementedError)
            self.results.append(res)
        self.dataReady.emit(self.results)

class FADialog(QDialog):
    header = ['Segment 1',
                'Segment 2',
                'Total words in corpus',
                'Total words with alternations',
                'Frequency of alternation',
                'Type or token',
                'Distance metric',
                'Phonological alignment?']
    def __init__(self, parent, corpus):
        QDialog.__init__(self, parent)

        self.corpus = corpus
        layout = QVBoxLayout()

        falayout = QHBoxLayout()

        self.segPairWidget = SegmentPairSelectWidget(corpus.inventory)

        falayout.addWidget(self.segPairWidget)


        self.algorithmWidget = RadioSelectWidget('String similarity algorithm',
                                            OrderedDict([('Khorsi','khorsi'),
                                            ('Edit distance','edit_distance'),
                                            ('Phonological edit distance','phono_edit_distance')]),
                                            {'Khorsi':self.khorsiSelected,
                                            'Edit distance':self.editDistSelected,
                                            'Phonological edit distance':self.phonoEditDistSelected})


        falayout.addWidget(self.algorithmWidget)

        optionFrame = QGroupBox('Options')

        optionLayout = QVBoxLayout()

        self.typeTokenWidget = RadioSelectWidget('Type or token',
                                            OrderedDict([('Count types','type'),
                                            ('Count tokens','token')]))

        optionLayout.addWidget(self.typeTokenWidget)

        #self.minPairsWidget = RadioSelectWidget('Minimal pairs',
        #                                    {'Ignore minimal pairs':'ignore',
        #                                    'Include minimal pairs':'include'})
        self.minPairsWidget = QCheckBox('Include minimal pairs')

        optionLayout.addWidget(self.minPairsWidget)

        threshFrame = QGroupBox('Threshold values')

        self.minEdit = QLineEdit()
        self.maxEdit = QLineEdit()

        vbox = QFormLayout()
        vbox.addRow('Minimum similarity (Khorsi):',self.minEdit)
        vbox.addRow('Maximum distance (edit distance):',self.maxEdit)

        threshFrame.setLayout(vbox)

        optionLayout.addWidget(threshFrame)

        alignFrame = QGroupBox('Alignment')

        self.alignCheck = QCheckBox('Do phonological alignment')

        vbox = QVBoxLayout()
        vbox.addWidget(self.alignCheck)

        alignFrame.setLayout(vbox)

        optionLayout.addWidget(alignFrame)

        corpusSizeFrame = QGroupBox('Corpus size')

        self.corpusSizeEdit = QLineEdit()

        vbox = QFormLayout()
        vbox.addRow('Subset corpus:',self.corpusSizeEdit)

        corpusSizeFrame.setLayout(vbox)

        optionLayout.addWidget(corpusSizeFrame)

        fileFrame = QGroupBox('Output file')

        self.fileWidget = FileWidget('Select file location','Text files (*.txt)')

        vbox = QHBoxLayout()
        vbox.addWidget(self.fileWidget)

        fileFrame.setLayout(vbox)

        optionLayout.addWidget(fileFrame)

        optionFrame.setLayout(optionLayout)

        falayout.addWidget(optionFrame)

        faframe = QFrame()
        faframe.setLayout(falayout)

        layout.addWidget(faframe)

        self.newTableButton = QPushButton('Calculate frequency of alternation\n(new table)')
        self.oldTableButton = QPushButton('Calculate frequency of alternation\n(add to current table)')
        self.cancelButton = QPushButton('Cancel')
        self.aboutButton = QPushButton('About this function...')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.newTableButton)
        acLayout.addWidget(self.oldTableButton)
        acLayout.addWidget(self.cancelButton)
        acLayout.addWidget(self.aboutButton)
        self.newTableButton.clicked.connect(self.newTable)
        self.oldTableButton.clicked.connect(self.oldTable)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Frequency of alternation')

        self.thread = FAWorker()

    def calcFA(self):
        pair_behaviour = 'individual'
        rel_type = self.algorithmWidget.value()
        if rel_type == 'khorsi':
            max_rel = None
            try:
                min_rel = float(self.minEdit.text())
            except ValueError:
                min_rel = None
        else:
            min_rel = None
            try:
                max_rel = float(self.maxEdit.text())
            except ValueError:
                max_rel = None
        if self.fileWidget.value() != '':
            out_file = self.fileWidget.text()
        else:
            out_file = None
        try:
            n = int(self.corpusSizeEdit.text())
            if n <= 0 or n >= len(self.corpus):
                raise(ValueError)
            else:
                corpus = self.corpus.get_random_subset(n)
        except ValueError:
            corpus = self.corpus
        kwargs = {'corpus':corpus,
                'segment_pairs':self.segPairWidget.value(),
                'relator_type': rel_type,
                'min_rel':min_rel,
                'max_rel':max_rel,
                'include_minimal_pairs':self.minPairsWidget.isChecked(),
                'phono_align':self.alignCheck.isChecked(),
                'pair_behavior':pair_behaviour,
                'count_what':self.typeTokenWidget.value(),
                'output_filename': out_file}
        self.thread.setParams(kwargs)

        dialog = QProgressDialog('Calculating frequency of alternation...','Cancel',0,0)
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
        seg_pairs = self.segPairWidget.value()
        pair_behaviour = 'individual'
        if pair_behaviour == 'individual':
            for i, r in enumerate(results):
                self.results.append([seg_pairs[i][0],seg_pairs[i][1],
                                    r[0],
                                    r[1],
                                    r[2],
                                    self.typeTokenWidget.value(),
                                    self.algorithmWidget.value(),
                                    self.alignCheck.isChecked()])

        else:
            pass

    def newTable(self):
        self.update = False
        self.calcFA()

    def oldTable(self):
        self.update = True
        self.calcFA()

    def about(self):
        pass

    def khorsiSelected(self):
        self.typeTokenWidget.enable()
        self.minEdit.setEnabled(True)
        self.maxEdit.setEnabled(False)

    def editDistSelected(self):
        self.typeTokenWidget.disable()
        self.minEdit.setEnabled(False)
        self.maxEdit.setEnabled(True)

    def phonoEditDistSelected(self):
        self.typeTokenWidget.disable()
        self.minEdit.setEnabled(False)
        self.maxEdit.setEnabled(True)
