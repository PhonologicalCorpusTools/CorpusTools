

from collections import OrderedDict

from corpustools.mutualinfo.mutual_information import pointwise_mi

from .imports import *
from .widgets import BigramWidget, TierWidget
from .windows import FunctionWorker, FunctionDialog

class MIWorker(FunctionWorker):
    def run(self):
        kwargs = self.kwargs
        self.results = list()
        for pair in kwargs['segment_pairs']:
            try:
                res = pointwise_mi(kwargs['corpus'], pair,
                        sequence_type = kwargs['sequence_type'],
                        halve_edges = kwargs['halve_edges'],
                        in_word = kwargs['in_word'],
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
                'Transcription tier',
                'Domain',
                'Halved edges',
                'Mutual information']

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

        optionLayout = QFormLayout()

        self.tierWidget = TierWidget(corpus,include_spelling=False)

        optionLayout.addRow(self.tierWidget)

        self.inWordCheck = QCheckBox()
        inWordLabel = QLabel('Set domain to word')

        optionLayout.addRow(inWordLabel,self.inWordCheck)

        self.halveEdgesCheck = QCheckBox()
        self.halveEdgesCheck.setChecked(True)
        halveEdgesLabel = QLabel('Halve word boundary count')
        optionLayout.addRow(halveEdgesLabel,self.halveEdgesCheck)

        optionFrame = QGroupBox('Options')
        optionFrame.setLayout(optionLayout)

        milayout.addWidget(optionFrame)
        miFrame.setLayout(milayout)

        self.layout().insertWidget(0,miFrame)

        if self.showToolTips:
            self.tierWidget.setToolTip(("<FONT COLOR=black>"
                                    'Choose which tier mutual information should'
                                    ' be calculated over (e.g., the whole transcription'
                                    ' vs. a tier containing only [+voc] segments).'
                                    ' New tiers can be created from the Corpus menu.'
                                    "</FONT>"))
            self.segPairWidget.setToolTip(("<FONT COLOR=black>"
            'Choose bigrams for which to calculate the'
                                ' mutual information of their bigram and unigram probabilities.'
            "</FONT>"))
            inwordToolTip = ("<FONT COLOR=black>"
            'Set the domain for counting unigrams/bigrams set to the '
                        'word rather than the unigram/bigram; ignores adjacency '
                        'and word edges (#).'
            "</FONT>")
            self.inWordCheck.setToolTip(inwordToolTip)
            inWordLabel.setToolTip(inwordToolTip)

            halveEdgesToolTip = ("<FONT COLOR=black>"
            'make the number of edge characters (#) equal to '
                        'the size of the corpus + 1, rather than double the '
                        'size of the corpus - 1.'
            "</FONT>")
            halveEdgesLabel.setToolTip(halveEdgesToolTip)
            self.segPairWidget.setToolTip(halveEdgesToolTip)



    def generateKwargs(self):
        segPairs = self.segPairWidget.value()
        if len(segPairs) == 0:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify at least one bigram.")
            return None
        return {'corpus':self.corpus,
                'segment_pairs':[tuple(y for y in x) for x in segPairs],
                'in_word': self.inWordCheck.isChecked(),
                'halve_edges': self.halveEdgesCheck.isChecked(),
                'sequence_type': self.tierWidget.value()}

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
        if self.inWordCheck.isChecked():
            dom = 'Word'
        else:
            dom = 'Unigram/Bigram'
        for i, r in enumerate(results):
            self.results.append([seg_pairs[i][0],seg_pairs[i][1],
                                self.tierWidget.displayValue(),
                                dom, self.halveEdgesCheck.isChecked(),
                                r])
