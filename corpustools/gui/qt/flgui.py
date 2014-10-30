
from PyQt5.QtCore import pyqtSignal as Signal,QThread
from PyQt5.QtWidgets import (QDialog, QListWidget, QGroupBox, QHBoxLayout,
                            QVBoxLayout, QPushButton, QFrame, QGridLayout,
                            QRadioButton, QLabel, QFormLayout, QLineEdit,
                            QFileDialog, QComboBox,QProgressDialog, QCheckBox)

from .widgets import SegmentPairSelectWidget, RadioSelectWidget, ProgressDialog

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
    def __init__(self, parent, corpus):
        QDialog.__init__(self, parent)

        self.corpus = corpus
        layout = QVBoxLayout()

        flFrame = QFrame()
        fllayout = QHBoxLayout()

        self.segPairWidget = SegmentPairSelectWidget(corpus.inventory)

        fllayout.addWidget(self.segPairWidget)

        layout.addWidget(flFrame)

        self.algorithmWidget = RadioSelectWidget('Functional load algorithm',
                                            {'Minimal pairs':'min_pairs',
                                            'Change in entropy':'entropy'})

        fllayout.addWidget(self.algorithmWidget)

        optionLayout = QVBoxLayout()

        self.segPairOptionsWidget = RadioSelectWidget('Multiple segment pair behaviour',
                                                {'All segment pairs together':'together',
                                                'Each segment pair individually':'individual'})

        optionLayout.addWidget(self.segPairOptionsWidget)

        minFreqFrame = QGroupBox('Minimum frequency')
        box = QFormLayout()
        self.minFreqEdit = QLineEdit()
        box.addRow('Only consider words with frequency of at least:',self.minFreqEdit)

        minFreqFrame.setLayout(box)

        optionLayout.addWidget(minFreqFrame)

        minPairOptionFrame = QGroupBox('Minimal pair options')

        box = QVBoxLayout()

        #self.relativeCountWidget = RadioSelectWidget('Relative count',
        #                                            {'Use counts relative to number of possible pairs':True,
        #                                            'Use raw counts':False})

        #self.homophoneWidget = RadioSelectWidget('Homophones',
        #                                        {'Include homophones':True,
        #                                        'Ignore homophones':False})

        self.relativeCountWidget = QCheckBox('Use counts relative to number of possible pairs')
        self.homophoneWidget = QCheckBox('Include homophones')

        box.addWidget(self.relativeCountWidget)
        box.addWidget(self.homophoneWidget)

        minPairOptionFrame.setLayout(box)

        optionLayout.addWidget(minPairOptionFrame)

        entropyOptionFrame = QGroupBox('Change in entropy options')

        box = QVBoxLayout()

        self.typeTokenWidget = RadioSelectWidget('Type or token frequencies',
                                                    {'Type':'type',
                                                    'Token':'token'})

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

        self.setLayout(layout)

        self.setWindowTitle('Functional load')

        self.thread = FLWorker()

    def calcFL(self):
        try:
            frequency_cutoff = float(self.minFreqEdit.text())
        except ValueError:
            frequency_cutoff = 0.0
        kwargs = {'corpus':self.corpus,
                'segment_pairs':self.segPairWidget.value(),
                'frequency_cutoff':frequency_cutoff,
                'relative_count':self.relativeCountWidget.isChecked(),
                'distinguish_homophones':self.homophoneWidget.isChecked(),
                'pair_behavior':self.segPairOptionsWidget.value(),
                'type_or_token':self.typeTokenWidget.value(),
                'func_type':self.algorithmWidget.value()}
        self.thread.setParams(kwargs)

        dialog = QProgressDialog('Calculating functional load...','Cancel',0,0)
        self.thread.dataReady.connect(self.setResults)
        self.thread.dataReady.connect(dialog.accept)

        self.thread.start()

        result = dialog.exec_()
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
        pass
