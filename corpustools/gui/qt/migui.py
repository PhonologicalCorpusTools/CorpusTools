

from collections import OrderedDict

from corpustools.mutualinfo.mutual_information import pointwise_mi

from .imports import *
from .widgets import BigramWidget
from .windows import FunctionWorker, FunctionDialog

class MIWorker(FunctionWorker):
    def run(self):
        kwargs = self.kwargs
        self.results = list()
        for pair in kwargs['segment_pairs']:
            try:
                res = pointwise_mi(kwargs['corpus'], pair,
                        sequence_type = kwargs['sequence_type'],
                        stop_check = kwargs['stop_check'],
                        call_back = kwargs['call_back'])
            except Exception as e:
                self.errorEncountered.emit(e)
                return
            if self.stopped:
                return
            self.results.append(res)
        self.dataReady.emit(self.results)



class MIDialog(FunctionDialog):
    header = ['Segment 1',
                'Segment 2',
                'Mutual information',
                'Tier']

    _about = [('This function calculates the mutual information for a bigram'
                    ' of any two segments, based on their unigram and bigram'
                    ' frequencies in the corpus.'),
                    '',
                    'Coded by Blake Allen',
                    '',
                    #'References',
                    ]

    name = 'mutual information'

    def __init__(self, parent, corpus, showToolTips):
        FunctionDialog.__init__(self, parent, MIWorker())

        self.corpus = corpus
        self.showToolTips = showToolTips

        miFrame = QFrame()
        milayout = QHBoxLayout()

        self.segPairWidget = BigramWidget(self.corpus.inventory)

        milayout.addWidget(self.segPairWidget)

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

        optionFrame = QGroupBox('Options')
        optionFrame.setLayout(optionLayout)

        milayout.addWidget(optionFrame)
        miFrame.setLayout(milayout)

        self.layout().insertWidget(0,miFrame)

        if self.showToolTips:
            tierFrame.setToolTip(("<FONT COLOR=black>"
                                    'Choose which tier mutual information should'
                                    ' be calculated over (e.g., the whole transcription'
                                    ' vs. a tier containing only [+voc] segments).'
                                    ' New tiers can be created from the Corpus menu.'
                                    "</FONT>"))
            self.segPairWidget.setToolTip(("<FONT COLOR=black>"
            'Choose bigrams for which to calculate the'
                                ' mutual information of their bigram and unigram probabilities.'
            "</FONT>"))

    def generateKwargs(self):
        segPairs = self.segPairWidget.value()
        if len(segPairs) == 0:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify at least one bigram.")
            return None
        return {'corpus':self.corpus,
                'segment_pairs':[tuple(y for y in x) for x in segPairs],
                'sequence_type': self.tierWidget.currentText()}

    def calc(self):
        kwargs = self.generateKwargs()
        if kwargs is None:
            return
        self.thread.setParams(kwargs)

        self.thread.start()

        result = self.progressDialog.exec_()

        self.progressDialog.reset()
        if result:
            self.accept()

    def setResults(self,results):
        self.results = list()
        seg_pairs = [tuple(y for y in x) for x in self.segPairWidget.value()]
        for i, r in enumerate(results):
            self.results.append([seg_pairs[i][0],seg_pairs[i][1],
                                r,
                                self.tierWidget.currentText()])
