

from collections import OrderedDict

from corpustools.mutualinfo.mutual_information import pointwise_mi

from .imports import *
from .widgets import (BigramWidget, RadioSelectWidget, TierWidget, ContextWidget)
from .windows import FunctionWorker, FunctionDialog

from corpustools.exceptions import PCTError, PCTPythonError

from corpustools.contextmanagers import (CanonicalVariantContext,
                                        MostFrequentVariantContext,
                                        SeparatedTokensVariantContext,
                                        WeightedVariantContext)

class MIWorker(FunctionWorker):
    def run(self):
        time.sleep(0.1)
        kwargs = self.kwargs
        self.results = []
        context = kwargs.pop('context')
        if context == ContextWidget.canonical_value:
            cm = CanonicalVariantContext
        elif context == ContextWidget.frequent_value:
            cm = MostFrequentVariantContext
        elif context == ContextWidget.separate_value:
            cm = SeparatedTokensVariantContext
        elif context == ContextWidget.relative_value:
            cm = WeightedVariantContext
        with cm(kwargs['corpus'], kwargs['sequence_type'], kwargs['type_token'], frequency_threshold = kwargs['frequency_cutoff']) as c:
            try:
                for pair in kwargs['segment_pairs']:
                    res = pointwise_mi(c, pair,
                            halve_edges = kwargs['halve_edges'],
                            in_word = kwargs['in_word'],
                            stop_check = kwargs['stop_check'],
                            call_back = kwargs['call_back'])
                    if self.stopped:
                        break
                    self.results.append(res)
            except PCTError as e:
                self.errorEncountered.emit(e)
                return
            except Exception as e:
                e = PCTPythonError(e)
                self.errorEncountered.emit(e)
                return
        if self.stopped:
            self.finishedCancelling.emit()
            return
        self.dataReady.emit(self.results)



class MIDialog(FunctionDialog):
    header = ['Corpus',
                'First segment',
                'Second segment',
                'Domain',
                'Halved edges',
                'Transcription tier',
                'Frequency type',
                'Pronunciation variants',
                'Minimum word frequency',
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

    def __init__(self, parent, settings, corpus, showToolTips):
        FunctionDialog.__init__(self, parent, settings, MIWorker())

        self.corpus = corpus
        self.showToolTips = showToolTips

        miFrame = QFrame()
        milayout = QHBoxLayout()

        self.segPairWidget = BigramWidget(self.corpus.inventory)

        milayout.addWidget(self.segPairWidget)

        optionLayout = QFormLayout()

        self.tierWidget = TierWidget(corpus,include_spelling=False)

        optionLayout.addRow(self.tierWidget)

        self.typeTokenWidget = RadioSelectWidget('Type or token frequency',
                                            OrderedDict([('Count types','type'),
                                            ('Count tokens','token')]))

        actions = None
        self.variantsWidget = ContextWidget(self.corpus, actions)

        optionLayout.addWidget(self.variantsWidget)

        optionLayout.addWidget(self.typeTokenWidget)
        
        ##----------------------
        minFreqFrame = QGroupBox('Minimum frequency')
        box = QFormLayout()
        self.minFreqEdit = QLineEdit()
        box.addRow('Minimum word frequency:',self.minFreqEdit)

        minFreqFrame.setLayout(box)

        optionLayout.addWidget(minFreqFrame)
        ##----------------------
        
        self.inWordCheck = QCheckBox('Set domain to word')
        optionLayout.addWidget(self.inWordCheck)

        self.halveEdgesCheck = QCheckBox('Halve word boundary count')
        self.halveEdgesCheck.setChecked(True)
        optionLayout.addWidget(self.halveEdgesCheck)

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

            halveEdgesToolTip = ("<FONT COLOR=black>"
            'make the number of edge characters (#) equal to '
                        'the size of the corpus + 1, rather than double the '
                        'size of the corpus - 1.'
            "</FONT>")
            self.halveEdgesCheck.setToolTip(halveEdgesToolTip)

    def generateKwargs(self):
        segPairs = self.segPairWidget.value()
        if len(segPairs) == 0:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify at least one bigram.")
            return None
        ##------------------
        try:
            frequency_cutoff = float(self.minFreqEdit.text())
        except ValueError:
            frequency_cutoff = 0.0
        ##-------------------
        return {'corpus':self.corpus,
                'context': self.variantsWidget.value(),
                'type_token': self.typeTokenWidget.value(),
                'segment_pairs':[tuple(y for y in x) for x in segPairs],
                'in_word': self.inWordCheck.isChecked(),
                'halve_edges': self.halveEdgesCheck.isChecked(),
                'frequency_cutoff':frequency_cutoff,
                'sequence_type': self.tierWidget.value()}

    def setResults(self,results):
        self.results = []
        seg_pairs = [tuple(y for y in x) for x in self.segPairWidget.value()]
        if self.inWordCheck.isChecked():
            dom = 'Word'
        else:
            dom = 'Unigram/Bigram'
        try:
            frequency_cutoff = float(self.minFreqEdit.text())
        except ValueError:
            frequency_cutoff = 0.0
        for i, r in enumerate(results):
            self.results.append([self.corpus.name,
                                seg_pairs[i][0],seg_pairs[i][1],
                                dom, self.halveEdgesCheck.isChecked(),
                                self.tierWidget.displayValue(),
                                self.typeTokenWidget.value().title(),
                                self.variantsWidget.value().title(),
                                frequency_cutoff,
                                r])
