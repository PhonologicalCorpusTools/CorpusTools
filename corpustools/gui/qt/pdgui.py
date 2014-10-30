
from PyQt5.QtCore import pyqtSignal as Signal,QThread
from PyQt5.QtWidgets import (QDialog, QListWidget, QGroupBox, QHBoxLayout,
                            QVBoxLayout, QPushButton, QFrame, QGridLayout,
                            QRadioButton, QLabel, QFormLayout, QLineEdit,
                            QFileDialog, QComboBox, QCheckBox, QProgressDialog)

from .widgets import EnvironmentSelectWidget, SegmentPairSelectWidget, RadioSelectWidget

from corpustools.prod.pred_of_dist import calc_prod,calc_prod_all_envs, ExhaustivityError, UniquenessError

class PDWorker(QThread):
    updateProgress = Signal(str)

    dataReady = Signal(object)

    def __init__(self):
        QThread.__init__(self)

    def setParams(self, kwargs):
        self.kwargs = kwargs

    def run(self):
        kwargs = self.kwargs
        self.results = list()
        if 'envs' in kwargs:
            if kwargs['pair_behavior'] == 'individual':

                for pair in kwargs['segment_pairs']:
                    res = calc_prod(kwargs['corpus'], pair[0],pair[1],
                            kwargs['envs'],
                            kwargs['tier'],
                            kwargs['type_token'],
                            kwargs['strict'],
                            True)
                    self.results.append(res)
            else:
                raise(NotImplementedError)
                self.results.append(res)
        else:
            if kwargs['pair_behavior'] == 'individual':

                for pair in kwargs['segment_pairs']:
                    res = calc_prod_all_envs(kwargs['corpus'], pair[0],pair[1],
                            kwargs['tier'],
                            kwargs['type_token'],
                            True)
                    self.results.append(res)
            else:
                raise(NotImplementedError)
                self.results.append(res)
        self.dataReady.emit(self.results)

class PDDialog(QDialog):
    header = ['Corpus',
                'Tier',
                'Sound1',
                'Sound2',
                'Environment',
                'Freq. of Sound1',
                'Freq. of Sound2',
                'Freq. of env.',
                'Entropy',
                'Type or token']
    def __init__(self, parent, corpus):
        QDialog.__init__(self, parent)

        self.corpus = corpus

        layout = QVBoxLayout()

        pdFrame = QFrame()
        pdlayout = QHBoxLayout()

        self.segPairWidget = SegmentPairSelectWidget(corpus.inventory)

        pdlayout.addWidget(self.segPairWidget)

        self.envWidget = EnvironmentSelectWidget(corpus.inventory)
        pdlayout.addWidget(self.envWidget)


        optionLayout = QVBoxLayout()
        self.tierWidget = QComboBox()
        self.tierWidget.addItem('transcription')
        for t in corpus.tiers:
            self.tierWidget.addItem(t)

        tierFrame = QGroupBox('Tier')

        box = QVBoxLayout()
        box.addWidget(self.tierWidget)
        tierFrame.setLayout(box)

        optionLayout.addWidget(tierFrame)

        self.typeTokenWidget = RadioSelectWidget('Type or token',
                                                {'Count types': 'type',
                                                'Count tokens': 'token'})

        optionLayout.addWidget(self.typeTokenWidget)


        checkFrame = QGroupBox('Exhaustivity and uniqueness')

        checkLayout = QVBoxLayout()

        self.enforceCheck = QCheckBox('Enforce enviroment exhaustivity and uniqueness')

        checkLayout.addWidget(self.enforceCheck)

        checkFrame.setLayout(checkLayout)

        optionLayout.addWidget(checkFrame)

        optionFrame = QGroupBox('Options')

        optionFrame.setLayout(optionLayout)

        pdlayout.addWidget(optionFrame)

        pdFrame.setLayout(pdlayout)

        layout.addWidget(pdFrame)

        self.newTableButton = QPushButton('Calculate predictability of distribution\n(start new results table)')
        self.oldTableButton = QPushButton('Calculate predictability of distribution\n(add to current results table)')
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

        self.setWindowTitle('Predictability of distribution')

        self.thread = PDWorker()

    def calcPD(self):
        kwargs = {'corpus':self.corpus,
                'segment_pairs':self.segPairWidget.value(),
                'envs':self.envWidget.value(),
                'tier':self.tierWidget.currentText(),
                'strict':self.enforceCheck.isChecked(),
                'pair_behavior':'individual',#self.segPairOptionsWidget.value(),
                'type_token':self.typeTokenWidget.value()}
        self.thread.setParams(kwargs)

        dialog = QProgressDialog('Calculating predictability of distribution...','Cancel',0,0)
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
        seg_pairs_options = 'individual'
        if seg_pairs_options == 'individual':
            for i, r in enumerate(results):
                if isinstance(r,dict):
                    for env,v in r.items():
                        self.results.append([self.corpus.name,
                                            self.tierWidget.currentText(),
                                            seg_pairs[i][0],seg_pairs[i][1],
                                            env,
                                            v[2], # freq of seg1
                                            v[3], #freq of seg2
                                            v[1], #total_tokens
                                            v[0], #H
                                            self.typeTokenWidget.value()])
                else:
                    self.results.append([self.corpus.name,
                                            self.tierWidget.currentText(),
                                            seg_pairs[i][0],seg_pairs[i][1],
                                            'FREQ-ONLY',
                                            v[2], # freq of seg1
                                            v[3], #freq of seg2
                                            v[1], #total_tokens
                                            v[0], #H
                                            self.typeTokenWidget.value()])

    def newTable(self):
        self.update = False
        self.calcPD()

    def oldTable(self):
        self.update = True
        self.calcPD()

    def about(self):
        pass
