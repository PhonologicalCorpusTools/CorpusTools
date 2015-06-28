

from collections import OrderedDict

import corpustools.funcload.functional_load as FL

from .imports import *
from .widgets import (SegmentPairSelectWidget, RadioSelectWidget, TierWidget,
                    ContextWidget)
from .windows import FunctionWorker, FunctionDialog

from corpustools.exceptions import PCTError, PCTPythonError

from corpustools.contextmanagers import (CanonicalVariantContext,
                                        MostFrequentVariantContext,
                                        SeparatedTokensVariantContext,
                                        WeightedVariantContext)

class FLWorker(FunctionWorker):
    def run(self):
        time.sleep(0.1)
        kwargs = self.kwargs
        self.results = []
        context = kwargs.pop('context')
        if kwargs.pop('algorithm') == 'min_pairs':
            func = FL.minpair_fl
        else:
            func = FL.deltah_fl
        if context == ContextWidget.canonical_value:
            cm = CanonicalVariantContext
        elif context == ContextWidget.frequent_value:
            cm = MostFrequentVariantContext
        elif context == ContextWidget.separate_value:
            cm = SeparatedTokensVariantContext
        elif context == ContextWidget.relative_value:
            cm = WeightedVariantContext
        with cm(kwargs.pop('corpus'),
                kwargs.pop('sequence_type'),
                kwargs.pop('type_token'),
                frequency_threshold = kwargs.pop('frequency_cutoff')) as c:
            try:
                pairs = kwargs.pop('segment_pairs')
                for pair in pairs:
                    if isinstance(pair[0], (list, tuple)):
                        in_list = list(zip(pair[0], pair[1]))
                    else:
                        in_list = [pair]
                    res = func(c, in_list, **kwargs)
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



class FLDialog(FunctionDialog):
    header = ['Segment 1',
                'Segment 2',
                'Transcription tier',
                'Type of functional load',
                'Result',
                'Distinguished homophones?',
                'Relative count?',
                'Minimum word frequency',
                'Type or token']

    _about = [('This function calculates the functional load of the contrast'
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

    name = 'functional load'

    def __init__(self, parent, settings, corpus, showToolTips):
        FunctionDialog.__init__(self, parent, settings, FLWorker())

        self.corpus = corpus
        self.showToolTips = showToolTips

        flFrame = QFrame()
        fllayout = QHBoxLayout()

        self.segPairWidget = SegmentPairSelectWidget(corpus.inventory)

        fllayout.addWidget(self.segPairWidget)

        secondPane = QFrame()

        l = QVBoxLayout()

        self.algorithmWidget = RadioSelectWidget('Functional load algorithm',
                                            OrderedDict([('Minimal pairs','min_pairs'),
                                            ('Change in entropy','entropy')]),
                                            {'Minimal pairs': self.minPairsSelected,
                                            'Change in entropy': self.entropySelected})

        l.addWidget(self.algorithmWidget)

        secondPane.setLayout(l)

        fllayout.addWidget(secondPane)

        optionLayout = QVBoxLayout()

        self.tierWidget = TierWidget(corpus,include_spelling=False)

        optionLayout.addWidget(self.tierWidget)

        self.typeTokenWidget = RadioSelectWidget('Type or token frequencies',
                                                    OrderedDict([('Type','type'),
                                                    ('Token','token')]))
        actions = {ContextWidget.canonical: lambda : self.typeTokenWidget.setEnabled(True),
                  ContextWidget.frequent: lambda : self.typeTokenWidget.setEnabled(True),
                  ContextWidget.separate: lambda : self.typeTokenWidget.setEnabled(False),
                  ContextWidget.relative: lambda : self.typeTokenWidget.setEnabled(False)}
        self.variantsWidget = ContextWidget(self.corpus, actions)

        optionLayout.addWidget(self.variantsWidget)

        minFreqFrame = QGroupBox('Minimum frequency')
        box = QFormLayout()
        self.minFreqEdit = QLineEdit()
        box.addRow('Minimum word frequency:',self.minFreqEdit)

        minFreqFrame.setLayout(box)

        optionLayout.addWidget(minFreqFrame)

        minPairOptionFrame = QGroupBox('Minimal pair options')

        box = QVBoxLayout()

        self.relativeCountWidget = QCheckBox('Use counts relative to number of possible pairs')
        self.relativeCountWidget.setChecked(True)
        self.homophoneWidget = QCheckBox('Distinguish homophones')

        box.addWidget(self.relativeCountWidget)
        box.addWidget(self.homophoneWidget)

        minPairOptionFrame.setLayout(box)

        l.addWidget(minPairOptionFrame)

        entropyOptionFrame = QGroupBox('Change in entropy options')

        box = QVBoxLayout()


        box.addWidget(self.typeTokenWidget)
        entropyOptionFrame.setLayout(box)
        l.addWidget(entropyOptionFrame)

        optionFrame = QGroupBox('Options')
        optionFrame.setLayout(optionLayout)

        fllayout.addWidget(optionFrame)
        flFrame.setLayout(fllayout)

        self.layout().insertWidget(0,flFrame)

        self.algorithmWidget.initialClick()
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
            self.tierWidget.setToolTip(("<FONT COLOR=black>"
                                    'Choose which tier functional load should'
                                    ' be calculated over (e.g., the whole transcription'
                                    ' vs. a tier containing only [+voc] segments).'
                                    ' New tiers can be created from the Corpus menu.'
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

    def typesSelected(self):
        self.typeTokenWidget.setOptions(OrderedDict([('Count types','type'),
                                            ('Count tokens','token')]))

    def tokensSelected(self):
        self.typeTokenWidget.setOptions(OrderedDict([
                    ('Use most frequent pronunciation as the type','most_frequent_type'),
                    ('Use most frequent pronunciation for all tokens','most_frequent_token'),
                    ('Use raw counts of each pronunciation (token frequency)','count_token'),
                    ('Use relative counts of each pronunciation (type frequency)','relative_type')]))

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
        alg = self.algorithmWidget.value()
        kwargs = {'corpus':self.corpus,
                'segment_pairs':segPairs,
                'context': self.variantsWidget.value(),
                'sequence_type': self.tierWidget.value(),
                'frequency_cutoff':frequency_cutoff,
                'type_token':self.typeTokenWidget.value(),
                'algorithm': alg}
        if alg == 'min_pairs':
            kwargs['relative_count'] = self.relativeCountWidget.isChecked()
            kwargs['distinguish_homophones'] = self.homophoneWidget.isChecked()
        return kwargs

    def setResults(self,results):
        self.results = list()
        seg_pairs = self.segPairWidget.value()
        try:
            frequency_cutoff = float(self.minFreqEdit.text())
        except ValueError:
            frequency_cutoff = 0.0
        for i, r in enumerate(results):
            if isinstance(r, tuple):
                r = r[0]
            self.results.append([seg_pairs[i][0],seg_pairs[i][1],
                                self.tierWidget.displayValue(),
                                self.algorithmWidget.displayValue(),
                                r,
                                self.homophoneWidget.isChecked(),
                                self.relativeCountWidget.isChecked(),
                                frequency_cutoff,
                                self.typeTokenWidget.value()])
