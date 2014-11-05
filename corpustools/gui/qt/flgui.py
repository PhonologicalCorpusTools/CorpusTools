
from PyQt5.QtCore import pyqtSignal as Signal,QThread
from PyQt5.QtWidgets import (QDialog, QListWidget, QGroupBox, QHBoxLayout,
                            QVBoxLayout, QPushButton, QFrame, QGridLayout,
                            QRadioButton, QLabel, QFormLayout, QLineEdit,
                            QFileDialog, QComboBox,QProgressDialog, QCheckBox,
                            QMessageBox)

from collections import OrderedDict

from .widgets import SegmentPairSelectWidget, RadioSelectWidget

import corpustools.funcload.functional_load as FL


class FLWorker(QThread):
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
                if kwargs['func_type'] == 'min_pairs':
                    res = FL.minpair_fl(kwargs['corpus'], [pair],
                            kwargs['frequency_cutoff'],
                            kwargs['relative_count'],
                            kwargs['distinguish_homophones'])
                elif kwargs['func_type'] == 'entropy':
                    res = FL.deltah_fl(kwargs['corpus'], [pair],
                            kwargs['frequency_cutoff'],
                            kwargs['type_or_token'])
                self.results.append(res)
        else:
            if kwargs['func_type'] == 'min_pairs':
                res = FL.minpair_fl(kwargs['corpus'],
                            kwargs['segment_pairs'],
                            kwargs['frequency_cutoff'],
                            kwargs['relative_count'],
                            kwargs['distinguish_homophones'])
            elif kwargs['func_type'] == 'entropy':
                res = FL.deltah_fl(kwargs['corpus'],
                        kwargs['segment_pairs'],
                        kwargs['frequency_cutoff'],
                        kwargs['type_or_token'])
            self.results.append(res)
        self.dataReady.emit(self.results)



class FLDialog(QDialog):
    header = ['Segment 1',
                'Segment 2',
                'Type of funcational load',
                'Result',
                'Ignored homophones?',
                'Relative count?',
                'Minimum word frequency',
                'Type or token']

    ABOUT = [('This function calculates the functional load of the contrast'
                    ' between any two segments, based on either the number of minimal'
                    ' pairs or the change in entropy resulting from merging that contrast.'),
                    '',
                    'Coded by Blake Allen',
                    '',
                    'References',
                    ('Surendran, Dinoj & Partha Niyogi. 2003. Measuring'
                    ' the functional load of phonological contrasts.'
                    ' In Tech. Rep. No. TR-2003-12.'),
                    ('Wedel, Andrew, Abby Kaplan & Scott Jackson. 2013.'
                    ' High functional load inhibits phonological contrast'
                    ' loss: A corpus study. Cognition 128.179-86')]

    def __init__(self, parent, corpus, showToolTips):
        QDialog.__init__(self, parent)

        self.corpus = corpus
        self.showToolTips = showToolTips
        layout = QVBoxLayout()

        flFrame = QFrame()
        fllayout = QHBoxLayout()

        self.segPairWidget = SegmentPairSelectWidget(corpus.inventory)

        fllayout.addWidget(self.segPairWidget)

        layout.addWidget(flFrame)

        self.algorithmWidget = RadioSelectWidget('Functional load algorithm',
                                            OrderedDict([('Minimal pairs','min_pairs'),
                                            ('Change in entropy','entropy')]),
                                            {'Minimal pairs': self.minPairsSelected,
                                            'Change in entropy': self.entropySelected})

        fllayout.addWidget(self.algorithmWidget)

        optionLayout = QVBoxLayout()

        self.segPairOptionsWidget = RadioSelectWidget('Multiple segment pair behaviour',
                                                OrderedDict([('All segment pairs together','together'),
                                                ('Each segment pair individually','individual')]))

        optionLayout.addWidget(self.segPairOptionsWidget)

        minFreqFrame = QGroupBox('Minimum frequency')
        box = QFormLayout()
        self.minFreqEdit = QLineEdit()
        box.addRow('Only consider words with frequency of at least:',self.minFreqEdit)

        minFreqFrame.setLayout(box)

        optionLayout.addWidget(minFreqFrame)

        minPairOptionFrame = QGroupBox('Minimal pair options')

        box = QVBoxLayout()

        self.relativeCountWidget = QCheckBox('Use counts relative to number of possible pairs')
        self.homophoneWidget = QCheckBox('Include homophones')

        box.addWidget(self.relativeCountWidget)
        box.addWidget(self.homophoneWidget)

        minPairOptionFrame.setLayout(box)

        optionLayout.addWidget(minPairOptionFrame)

        entropyOptionFrame = QGroupBox('Change in entropy options')

        box = QVBoxLayout()

        self.typeTokenWidget = RadioSelectWidget('Type or token frequencies',
                                                    OrderedDict([('Type','type'),
                                                    ('Token','token')]))

        box.addWidget(self.typeTokenWidget)
        entropyOptionFrame.setLayout(box)
        optionLayout.addWidget(entropyOptionFrame)

        optionFrame = QGroupBox('Options')
        optionFrame.setLayout(optionLayout)

        fllayout.addWidget(optionFrame)
        flFrame.setLayout(fllayout)


        self.newTableButton = QPushButton('Calculate functional load\n(start new results table)')
        self.oldTableButton = QPushButton('Calculate functional load\n(add to current results table)')
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

        if self.showToolTips:
            self.homophoneWidget.setToolTip(("<FONT COLOR=black>"
            'This setting will overcount alternative'
                            ' spellings of the same word, e.g. axel~actual and axle~actual,'
                            ' but will allow you to count e.g. sock~shock twice, once for each'
                            ' meaning of \'sock\' (footwear vs. punch)'
            "</FONT>"))

            self.relativeCountWidget.setToolTip(("<FONT COLOR=black>"
            'The raw count of minimal pairs will'
                            ' be divided by the number of words that include any of the target segments'
                            ' present in the list at the left.'
            "</FONT>"))
            self.segPairOptionsWidget.setToolTip(("<FONT COLOR=black>"
            'Choose either to calculate the'
                                ' functional load of a particular contrast among a group of segments'
                                ' to calculate the functional loads of a series of segment pairs separately.'
            "</FONT>"))
            self.segPairWidget.setToolTip(("<FONT COLOR=black>"
            'Add pairs of sounds whose contrast to collapse.'
                                    ' For example, if you\'re interested in the functional load of the [s]'
                                    ' / [z] contrast, you only need to add that pair. If, though, you\'re'
                                    ' interested in the functional load of the voicing contrast among obstruents,'
                                    ' you may need to add (p, b), (t, d), and (k, g).'
            "</FONT>"))
            self.algorithmWidget.setToolTip(("<FONT COLOR=black>"
            'Calculate the functional load either using'
                            ' the contrast between two sets of segments as a count of minimal pairs'
                            ' or using the decrease in corpus'
                            ' entropy caused by a merger of paired segments in the set.'
            "</FONT>"))
        self.setLayout(layout)

        self.setWindowTitle('Functional load')

        self.thread = FLWorker()

        self.progressDialog = QProgressDialog('Calculating functional load...','Cancel',0,0)
        self.thread.dataReady.connect(self.setResults)
        self.thread.dataReady.connect(self.progressDialog.accept)

    def minPairsSelected(self):
        self.typeTokenWidget.disable()
        self.relativeCountWidget.setEnabled(True)
        self.homophoneWidget.setEnabled(True)

    def entropySelected(self):
        self.typeTokenWidget.enable()
        self.relativeCountWidget.setEnabled(False)
        self.homophoneWidget.setEnabled(False)

    def generateKwargs(self):
        segPairs = self.segPairWidget.value()
        if len(segPairs) == 0:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify at least one segment pair.")
            return None
        try:
            frequency_cutoff = float(self.minFreqEdit.text())
        except ValueError:
            frequency_cutoff = 0.0
        return {'corpus':self.corpus,
                'segment_pairs':segPairs,
                'frequency_cutoff':frequency_cutoff,
                'relative_count':self.relativeCountWidget.isChecked(),
                'distinguish_homophones':self.homophoneWidget.isChecked(),
                'pair_behavior':self.segPairOptionsWidget.value(),
                'type_or_token':self.typeTokenWidget.value(),
                'func_type':self.algorithmWidget.value()}


    def calcFL(self):
        kwargs = self.generateKwargs()
        if kwargs is None:
            return
        self.thread.setParams(kwargs)

        self.thread.start()

        result = self.progressDialog.exec_()
        if result:
            self.accept()
        else:
            self.thread.terminate()


    def setResults(self,results):
        self.results = list()
        seg_pairs = self.segPairWidget.value()
        try:
            frequency_cutoff = float(self.minFreqEdit.text())
        except ValueError:
            frequency_cutoff = 0.0
        if self.segPairOptionsWidget.value() == 'individual':
            for i, r in enumerate(results):
                self.results.append([seg_pairs[i][0],seg_pairs[i][1],
                                    self.algorithmWidget.value(),
                                    r,
                                    self.homophoneWidget.isChecked(),
                                    self.relativeCountWidget.isChecked(),
                                    frequency_cutoff,
                                    self.typeTokenWidget.value()])
        else:
            self.results.append([', '.join(x[0] for x in seg_pairs),
                                ', '.join(x[1] for x in seg_pairs),
                                    self.algorithmWidget.value(),
                                    results[0],
                                    self.homophoneWidget.isChecked(),
                                    self.relativeCountWidget.isChecked(),
                                    frequency_cutoff,
                                    self.typeTokenWidget.value()])

    def newTable(self):
        self.update = False
        self.calcFL()

    def oldTable(self):
        self.update = True
        self.calcFL()

    def about(self):
        reply = QMessageBox.information(self,
                "About functional load", '\n'.join(self.ABOUT))
