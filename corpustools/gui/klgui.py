

from math import log
from collections import defaultdict, OrderedDict
import os
from codecs import open

from .imports import *
from .widgets import (SegmentPairSelectWidget, RadioSelectWidget, TierWidget,
                    ContextWidget)
from .windows import FunctionWorker, FunctionDialog
from corpustools.kl.kl import KullbackLeibler

from corpustools.exceptions import PCTError, PCTPythonError

from corpustools.contextmanagers import (CanonicalVariantContext,
                                        MostFrequentVariantContext,
                                        SeparatedTokensVariantContext,
                                        WeightedVariantContext)

class KLWorker(FunctionWorker):
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
        with cm(kwargs['corpus'], kwargs['sequence_type'], kwargs['type_token']) as c:
            try:
                for pair in kwargs['segment_pairs']:
                    res = KullbackLeibler(c,
                                    pair[0], pair[1],
                                    outfile = None,
                                    side = kwargs['side'],
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

class KLDialog(FunctionDialog):
    header = ['Corpus',
                'First segment',
                'Second segment',
                'Context',
                'Transcription tier',
                'Frequency type',
                'Pronunciation variants',
                'First segment entropy',
                'Second segment entropy',
                'Kullback-Leibler divergence',
                'Possible UR',
                'Spurious allophones?'
                ]

    _about = [('This function calculates a difference in distribution of two segments'
                    ' based on the Kullback-Leibler measurement of the difference between'
                    ' probability distributions.'),
                    '',
                    'Coded by Scott Mackie',
                    '',
                    'References',
                    ('Sharon Peperkamp, Rozenn Le Calvez, Jean-Pierre Nadal, Emmanuel Dupoux. '
                    '2006. The Acquisition of allophonic rules: Statistical learning with linguistic constraints '
                    ' Cognition 101 B31-B41')]

    name = 'Kullback-Leibler'

    def __init__(self, parent, settings, corpus, showToolTips):
        FunctionDialog.__init__(self, parent, settings, KLWorker())

        self.corpus = corpus
        self.showToolTips = showToolTips

        klframe = QFrame()
        kllayout = QHBoxLayout()

        self.segPairWidget = SegmentPairSelectWidget(corpus.inventory)
        kllayout.addWidget(self.segPairWidget)
        optionLayout = QFormLayout()

        self.tierWidget = TierWidget(corpus, include_spelling=False)

        optionLayout.addRow(self.tierWidget)

        self.typeTokenWidget = RadioSelectWidget('Type or token frequency',
                                            OrderedDict([('Count types','type'),
                                            ('Count tokens','token')]))

        actions = None
        self.variantsWidget = ContextWidget(self.corpus, actions)

        optionLayout.addWidget(self.variantsWidget)

        optionLayout.addWidget(self.typeTokenWidget)

        self.contextRadioWidget = RadioSelectWidget('Contexts to examine',
                                                    OrderedDict([('Left-hand side only','lhs'),
                                                        ('Right-hand side only', 'rhs'),
                                                        ('Both sides', 'both')]),
                                                        #('All', 'all')]),
                                                        )
        optionLayout.addWidget(self.contextRadioWidget)

        kllayout.addLayout(optionLayout)
        klframe.setLayout(kllayout)
        self.layout().insertWidget(0, klframe)

    def generateKwargs(self):
        kwargs = {}
        segPairs = self.segPairWidget.value()
        if len(segPairs) == 0:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify at least one segment pair.")
            return None
        kwargs['segment_pairs'] = segPairs
        kwargs['corpus'] = self.corpus
        kwargs['context'] = self.variantsWidget.value()
        kwargs['sequence_type'] = self.tierWidget.value()
        kwargs['type_token'] = self.typeTokenWidget.value()
        kwargs['side'] = self.contextRadioWidget.value()[0]

        return kwargs

    def setResults(self,results):
        self.results = []
        seg_pairs = [tuple(y for y in x) for x in self.segPairWidget.value()]
        context = self.contextRadioWidget.displayValue()
        for i, r in enumerate(results):
            self.results.append([self.corpus.name,
                                seg_pairs[i][0],seg_pairs[i][1],
                                context,
                                self.tierWidget.displayValue(),
                                self.typeTokenWidget.value().title(),
                                self.variantsWidget.value().title()]+list(r))
