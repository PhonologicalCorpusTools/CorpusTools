from collections import OrderedDict
import time
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
from corpustools import __version__

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
        with cm(kwargs['corpus'], kwargs['sequence_type'], kwargs['type_token'], frequency_threshold = kwargs['frequency_cutoff']) as c:
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
              'PCT ver.',
              'Analysis name',
              'First segment',
              'Second segment',
              'Context',
              'Minimum word frequency',
              'Transcription tier',
              'Frequency type',
              'Pronunciation variants',
              'First segment entropy',
              'Second segment entropy',
              'Result',
              'Possible UR',
              'Spurious allophones'
              ]

    _about = [('This function calculates a difference in distribution of two segments'
                    ' based on the Kullback-Leibler measurement of the difference between'
                    ' probability distributions.'),
                    '',
                    'References: ',
                    ('Sharon Peperkamp, Rozenn Le Calvez, Jean-Pierre Nadal, Emmanuel Dupoux. '
                    '2006. The Acquisition of allophonic rules: Statistical learning with linguistic constraints '
                    ' Cognition 101 B31-B41')]

    name = 'Kullback-Leibler'

    def __init__(self, parent, settings, corpus, inventory, showToolTips):
        FunctionDialog.__init__(self, parent, settings, KLWorker())

        self.corpus = corpus
        self.inventory =  inventory
        self.showToolTips = showToolTips

        klframe = QFrame()
        kllayout = QHBoxLayout()

        self.segPairWidget = SegmentPairSelectWidget(self.inventory)
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
        
        ##----------------------
        minFreqFrame = QGroupBox('Minimum frequency')
        box = QFormLayout()
        self.minFreqEdit = QLineEdit()
        self.minFreqEdit.setValidator(QDoubleValidator(float('inf'), 0, 8))
        box.addRow('Minimum word frequency:',self.minFreqEdit)

        minFreqFrame.setLayout(box)

        optionLayout.addWidget(minFreqFrame)
        ##----------------------
        
        kllayout.addLayout(optionLayout)
        klframe.setLayout(kllayout)
        self.layout().insertWidget(0, klframe)

        if self.showToolTips:
            self.contextRadioWidget.setToolTip(("<FONT COLOR=black>"
                                    'This setting selects the environment to consider when calculating KL '
                                    'divergence. Note that the \"both\" option considers both sides simultaneously; '
                                    'it is not a sum of the left and right side scores.'
                                    "</FONT>"))

    def generateKwargs(self):
        kwargs = {}
        segPairs = self.segPairWidget.value()
        if len(segPairs) == 0:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify at least one segment pair.")
            return None
        ##------------------
        try:
            frequency_cutoff = float(self.minFreqEdit.text())
        except ValueError:
            frequency_cutoff = 0.0
        ##-------------------
        kwargs['segment_pairs'] = segPairs
        kwargs['corpus'] = self.corpus
        kwargs['context'] = self.variantsWidget.value()
        kwargs['sequence_type'] = self.tierWidget.value()
        kwargs['type_token'] = self.typeTokenWidget.value()
        kwargs['side'] = self.contextRadioWidget.value()[0]
        kwargs['frequency_cutoff'] = frequency_cutoff
        return kwargs

    def setResults(self,results):
        self.results = []
        seg_pairs = [tuple(y for y in x) for x in self.segPairWidget.value()]
        context = self.contextRadioWidget.displayValue()
        try:
            frequency_cutoff = float(self.minFreqEdit.text())
        except ValueError:
            frequency_cutoff = 0.0
        for i, r in enumerate(results):
            self.results.append({'Corpus': self.corpus.name,
                                'PCT ver.': __version__,#self.corpus._version,
                                'Analysis name': self.name.capitalize(),
                                'First segment': seg_pairs[i][0],
                                'Second segment': seg_pairs[i][1],
                                'Context': context,
                                'Minimum word frequency': frequency_cutoff,
                                'Transcription tier': self.tierWidget.displayValue(),
                                'Frequency type': self.typeTokenWidget.value().title(),
                                'Pronunciation variants': self.variantsWidget.value().title(),
                                'First segment entropy': r[0],
                                'Second segment entropy': r[1],
                                'Result': r[2],
                                'Possible UR': r[3],
                                'Spurious allophones': r[4]})
