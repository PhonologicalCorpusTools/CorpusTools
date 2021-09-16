from collections import OrderedDict

from corpustools.exceptions import PCTError, PCTPythonError

from .environments import *

from .imports import *
from .models import ABSegmentsModel
from .windows import FunctionWorker, FunctionDialog
from .widgets import BigramWidget, TierWidget, RadioSelectWidget, ContextWidget, SyllableBigramWidget
from corpustools.contextmanagers import (CanonicalVariantContext, MostFrequentVariantContext,
                                         SeparatedTokensVariantContext,
                                         WeightedVariantContext)

from ..transprob.transitional_probability import calc_trans_prob

from corpustools import __version__


# GUI for the Transitional Probability windows


class TPWorker(FunctionWorker):
    def run(self):
        kwargs = self.kwargs
        self.results = []

        # set up the context, use it and the keyword arguments to call the TP function
        context = kwargs.pop('context')
        if context == ContextWidget.canonical_value:
            cm = CanonicalVariantContext
        elif context == ContextWidget.frequent_value:
            cm = MostFrequentVariantContext
        elif context == ContextWidget.separate_value:
            cm = SeparatedTokensVariantContext
        elif context == ContextWidget.relative_value:
            cm = WeightedVariantContext

        with cm(kwargs['corpus'], kwargs['tier'],
                kwargs['sequence_type'], frequency_threshold=kwargs['frequency_cutoff']) as c:
            try:
                for bigram in kwargs['bigrams']:
                    res = calc_trans_prob(c, bigram, kwargs['wb'], kwargs['dir'])
                    self.results.append(res)
            except PCTError as e:
                self.errorEncountered.emit(e)
                return
            except Exception as e:
                e = PCTPythonError(e)
                self.errorEncountered.emit(e)
                return

        self.dataReady.emit(self.results)


class TPDialog(FunctionDialog):
    header = ['Corpus',
              'PCT ver.',
              'Analysis name',
              'Bigram',
              # 'Segment type',
              'Word boundary',
              'Direction',
              'Sequence type',
              'Tier',
              'Pronunciation variants',
              'Minimum word frequency',
              'Transitional probability']

    _about = [('This function calculates transitional probability' ' of two bigrams')]

    name = 'transitional probability'

    def __init__(self, parent, settings, corpus, inventory, showToolTips):
        FunctionDialog.__init__(self, parent, settings, TPWorker())

        self.corpus = corpus
        self.inventory = inventory
        self.showToolTips = showToolTips

        tpFrame = QFrame()
        self.tpLayout = QHBoxLayout()
        self.bigramLayout = QVBoxLayout()

        self.envWidget = BigramWidget(self.inventory, tplayout=True, wordlist=self.corpus.wordlist)
        self.envWidget.table.setModel(ABSegmentsModel())
        self.bigramLayout.addWidget(self.envWidget)
        self.tpLayout.addLayout(self.bigramLayout)

        tpOptionLayout = QFormLayout()
        optionLayout = QFormLayout()

        ## WIP: A syllable mode for TP
        # modeFrame = QGroupBox('Calculate probability')
        # modeLayout = QVBoxLayout()
        # modeFrame.setLayout(modeLayout)
        #
        # self.modeGroup = QButtonGroup()
        # segMode = QCheckBox('Using segments')
        # segMode.clicked.connect(self.changeMode)
        # segMode.setChecked(True)
        # self.mode = 'segMode'
        # self.modeGroup.addButton(segMode)
        #
        # sylMode = QCheckBox('Using syllables')
        # sylMode.clicked.connect(self.changeMode)
        # self.modeGroup.addButton(sylMode)
        # self.modeGroup.setExclusive(True)
        # self.modeGroup.setId(segMode, 0)
        # self.modeGroup.setId(sylMode, 1)
        #
        # if len(inventory.syllables) == 0:
        #     sylMode.setEnabled(False)
        #
        # modeLayout.addWidget(segMode)
        # modeLayout.addWidget(sylMode)
        # optionLayout.addWidget(modeFrame)

        # Direction
        self.dirWidget = RadioSelectWidget('Direction',
                                           OrderedDict([('P(B|A) Forward', 'forward'),
                                                        ('P(A|B) Backward', 'backward')]))

        tpOptionLayout.addWidget(self.dirWidget)

        # Word boundary
        self.wordBoundaryWidget = RadioSelectWidget('Word boundary',
                                                    OrderedDict([('Word boundaries at the end only (default)',
                                                                  'Word-end only'),
                                                                 ('Keep both word boundaries', 'Both sides'),
                                                                 ('Ignore all word boundaries', 'Ignored')]))
        tpOptionLayout.addWidget(self.wordBoundaryWidget)

        self.variantsWidget = ContextWidget(self.corpus, None)
        tpOptionLayout.addWidget(self.variantsWidget)

        self.tierWidget = TierWidget(corpus, include_spelling=False)
        optionLayout.addWidget(self.tierWidget)

        self.typeTokenWidget = RadioSelectWidget('Type or token frequency',
                                                 OrderedDict([('Count types', 'type'),
                                                              ('Count tokens', 'token')]))
        optionLayout.addWidget(self.typeTokenWidget)

        minFreqFrame = QGroupBox('Minimum frequency')
        box = QFormLayout()
        self.minFreqEdit = QLineEdit()
        self.minFreqEdit.setValidator(QDoubleValidator(float('inf'), 0, 8))
        box.addRow('Minimum word frequency:', self.minFreqEdit)
        minFreqFrame.setLayout(box)
        optionLayout.addWidget(minFreqFrame)

        tpOptionFrame = QGroupBox()
        tpOptionFrame.setLayout(tpOptionLayout)
        optionFrame = QGroupBox()
        optionFrame.setLayout(optionLayout)
        self.tpLayout.addWidget(tpOptionFrame)
        self.tpLayout.addWidget(optionFrame)
        tpFrame.setLayout(self.tpLayout)

        self.layout().insertWidget(0, tpFrame)

        if self.showToolTips:
            # modeFrame.setToolTip(("<FONT COLOR=black>"
            #                       'Choose the unit type for calculating'
            #                       ' transitional probability; either'
            #                       ' between individual segments or'
            #                       ' between syllables.'
            #                       "</FONT>"))
            self.dirWidget.setToolTip(("<FONT COLOR=black>"
                                       'Choose the direction of the algorithm:'
                                       ' for two units AB, forward TP'
                                       ' is the probability of B given A'
                                       ' and backward TP is the probability'
                                       ' of A given B. See Anghelescu (2016)'))
            self.tierWidget.setToolTip(("<FONT COLOR=black>"
                                        'Choose which tier transitional probability should'
                                        ' be calculated over (e.g., the whole transcription'
                                        ' vs. a tier containing only [+voc] segments).'
                                        ' New tiers can be created from the Corpus menu.'
                                        "</FONT>"))
            self.envWidget.setToolTip(("<FONT COLOR=black>"
                                       'Select at lest one pair of segments for'
                                       ' calculating transitional probability.'
                                       ' Each pair will be its own calculation'
                                       "</FONT>"))

    def changeMode(self):
        self.tpLayout.removeWidget(self.envWidget)
        self.envWidget.deleteLater()
        if self.modeGroup.checkedId() == 0:
            self.mode = 'segMode'
            self.envWidget = BigramWidget(self.inventory, tplayout=True)
            self.envWidget.table.setModel(ABSegmentsModel())
            self.tpLayout.insertWidget(0, self.envWidget)
            if self.showToolTips:
                self.envWidget.setToolTip(("<FONT COLOR=black>"
                                           'Select at lest one pair of segments for'
                                           ' calculating transitional probability.'
                                           ' Each pair will be its own calculation'
                                           "</FONT>"))
        else:
            self.mode = 'sylMode'
            self.envWidget = SyllableBigramWidget(self.inventory, tplayout=True)
            self.tpLayout.insertWidget(0, self.envWidget)
            self.envWidget.table.setModel(ABSegmentsModel())
            if self.showToolTips:
                self.envWidget.setToolTip(("<FONT COLOR=black>"
                                           'Select at lest one pair of syllables for'
                                           ' calculating transitional probability.'
                                           ' Each pair will be its own calculation'
                                           "</FONT>"))

    def generateKwargs(self):
        segPairs = self.envWidget.value()
        # if self.mode == 'segMode' and len(segPairs) == 0:
        #     reply = QMessageBox.critical(self, "Missing information", "Please specify at least one bigram.")
        #     return None
        # elif self.mode == 'sylMode' and len(segPairs) == 0:
        #     reply = QMessageBox.critical(self, "Missing information", "Please specify at least two syllables.")
        #     return None

        try:
            f_cutoff = float(self.minFreqEdit.text())
        except ValueError:
            f_cutoff = 0.0

        return {'corpus': self.corpus,
                'context': self.variantsWidget.value(),
                # 'mode': self.mode,
                'bigrams': self.create_bigrams(segPairs),
                'wb': self.wordBoundaryWidget.value(),
                'dir': self.dirWidget.value(),
                'sequence_type': self.typeTokenWidget.value(),
                'frequency_cutoff': f_cutoff,
                'tier': self.tierWidget.value()}

    @staticmethod
    def create_bigrams(pair_list):
        try:
            return [tuple(y for y in x) for x in pair_list]
        except TypeError:
            return pair_list

    @staticmethod
    def get_symbol(i, pair):
        try:
            return pair[i]
        except TypeError:
            if i == 0:
                return pair.lhs
            if i == 1:
                return pair.middle

    def setResults(self, results):
        self.results = []
        seg_pairs = self.create_bigrams(self.envWidget.value())
        try:
            f_cutoff = float(self.minFreqEdit.text())
        except ValueError:
            f_cutoff = 0.0
        # mode = 'Segments' if self.mode == 'segMode' else 'Syllables'
        for i, r in enumerate(results):
            self.results.append({'Corpus': self.corpus.name,
                                 'PCT ver.': __version__,
                                 'Analysis name': 'Transitional probability',
                                 # 'First segment': self.get_symbol(0, seg_pairs[i]),
                                 # 'Second segment': self.get_symbol(1, seg_pairs[i]),
                                 'Bigram': ''.join(seg_pairs[i]),
                                 # if self.mode=='segMode' else ''.join([str(i) for i in seg_pairs[i]]),
                                 'Word boundary': self.wordBoundaryWidget.value().capitalize(),
                                 # 'Segment type': mode,
                                 'Direction': self.dirWidget.value().capitalize(),
                                 'Sequence type': self.typeTokenWidget.value(),
                                 'Tier': self.tierWidget.value(),
                                 'Pronunciation variants': self.variantsWidget.value().capitalize(),
                                 'Minimum word frequency': f_cutoff,
                                 'Transitional probability': r})
