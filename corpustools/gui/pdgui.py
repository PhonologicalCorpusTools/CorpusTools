from collections import OrderedDict

from .imports import *
from .environments import EnvironmentSelectWidget
from .widgets import (SegmentPairSelectWidget, RadioSelectWidget, TierWidget, ContextWidget)
from .windows import FunctionWorker, FunctionDialog


from corpustools.prod.pred_of_dist import (calc_prod, calc_prod_all_envs)

from corpustools.exceptions import PCTError, PCTPythonError

from corpustools.contextmanagers import (CanonicalVariantContext,
                                        MostFrequentVariantContext,
                                        SeparatedTokensVariantContext,
                                        WeightedVariantContext)
from corpustools import __version__

class PDWorker(FunctionWorker):
    def run(self):
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
        with cm(kwargs['corpus'], kwargs['sequence_type'], kwargs['type_token'],
                frequency_threshold = kwargs['frequency_cutoff']) as c:
            try:
                envs = kwargs.pop('envs', None)
                for pair in kwargs['segment_pairs']:
                    ordered_pair = pair
                    if envs is not None:
                        for env in envs:
                            env.middle = set(pair)
                        res = calc_prod(c,
                                envs,
                                kwargs['strict'],
                                ordered_pair = ordered_pair,
                                all_info = True,
                                stop_check = kwargs['stop_check'],
                                call_back = kwargs['call_back'])
                    else:
                        res = calc_prod_all_envs(c, pair[0], pair[1],
                            all_info = True,
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


class PDDialog(FunctionDialog):
    header = ['Corpus',
              'PCT ver.',
              'Analysis name',
              'First segment',
              'Second segment',
              'Environment',
              'Transcription tier',
              'Frequency type',
              'Pronunciation variants',
              'Frequency of first segment',
              'Frequency of second segment',
              'Frequency of environment',
              'Minimum word frequency',
              'Result']

    _about = ['This function calculates'
                ' the predictability of distribution of two sounds, using the measure of entropy'
                ' (uncertainty). Sounds that are entirely predictably distributed (i.e., in'
                ' complementary distribution, commonly assumed to be allophonic), will have'
                ' an entropy of 0. Sounds that are perfectly overlapping in their distributions'
                ' will have an entropy of 1.',
                '',
                'References: ',
                ('Hall, K.C. 2009. A probabilistic model of phonological'
                ' relationships from contrast to allophony. PhD dissertation,'
                ' The Ohio State University.')]

    name = 'predictability of distribution'
    def __init__(self, parent, settings, corpus, inventory, showToolTips):
        FunctionDialog.__init__(self, parent, settings, PDWorker())
        self.corpus = corpus
        self.inventory = inventory
        self.showToolTips = showToolTips

        pdFrame = QFrame()
        pdlayout = QHBoxLayout()

        self.segPairWidget = SegmentPairSelectWidget(self.inventory)

        pdlayout.addWidget(self.segPairWidget)

        self.envWidget = EnvironmentSelectWidget(inventory, middle = False)

        pdlayout.addWidget(self.envWidget)

        optionLayout = QVBoxLayout()

        self.tierWidget = TierWidget(corpus,include_spelling=False)

        optionLayout.addWidget(self.tierWidget)

        self.typeTokenWidget = RadioSelectWidget('Type or token frequency',
                                            OrderedDict([('Count types','type'),
                                            ('Count tokens','token')]))
        actions = None
        self.variantsWidget = ContextWidget(self.corpus, actions)

        optionLayout.addWidget(self.variantsWidget)

        optionLayout.addWidget(self.typeTokenWidget)

        checkFrame = QGroupBox('Exhaustivity and uniqueness')

        checkLayout = QVBoxLayout()

        self.enforceCheck = QCheckBox('Enforce environment\nexhaustivity and uniqueness')
        self.enforceCheck.setChecked(True)

        checkLayout.addWidget(self.enforceCheck)

        checkFrame.setLayout(checkLayout)

        optionLayout.addWidget(checkFrame)
        
        ##----------------------
        minFreqFrame = QGroupBox('Minimum frequency')
        box = QFormLayout()
        self.minFreqEdit = QLineEdit()
        self.minFreqEdit.setValidator(QDoubleValidator(float('inf'), 0, 8))
        box.addRow('Minimum word frequency:',self.minFreqEdit)

        minFreqFrame.setLayout(box)

        optionLayout.addWidget(minFreqFrame)
        ##----------------------
        
        optionFrame = QGroupBox('Options')

        optionFrame.setLayout(optionLayout)

        pdlayout.addWidget(optionFrame)

        pdFrame.setLayout(pdlayout)

        self.layout().insertWidget(0,pdFrame)

        self.setWindowTitle('Predictability of distribution')

        if self.showToolTips:
            self.segPairWidget.setToolTip(("<FONT COLOR=black>"
                            'Choose pairs of segments whose'
                            ' predictability of distribution you want to calculate. The order of the'
                            ' two sounds is irrelevant. The symbols you see here should automatically'
                            ' match the symbols used anywhere in your corpus.'
                            "</FONT>"))
            self.tierWidget.setToolTip(("<FONT COLOR=black>"
                                    'Choose which tier predictability should'
                                    ' be calculated over (e.g., the whole transcription'
                                    ' vs. a tier containing only [+voc] segments).'
                                    ' New tiers can be created from the Corpus menu.'
            "</FONT>"))
            self.typeTokenWidget.setToolTip(("<FONT COLOR=black>"
            'Choose what kind of frequency should'
                                    ' be used for the calculations. Type frequency'
                                    ' means each word is counted once. Token frequency'
                                    ' means each word is counted as often as it occurs'
                                    ' in the corpus.'
            "</FONT>"))
            self.enforceCheck.setToolTip(("<FONT COLOR=black>"
            'Indicate whether you want the program'
                                    ' to check for exhausitivity and uniqueness.'
                                    ' Checking for exhaustivity'
                                    ' will ensure that you have selected environments'
                                    ' that cover all instances of the two sounds in the'
                                    ' corpus. Checking for uniqueness'
                                    ' will ensure that the environments you'
                                    ' have selected don\'t overlap with one another.'
            "</FONT>"))
            self.envWidget.setToolTip(("<FONT COLOR=black>"
            'This screen allows you to construct multiple'
                                    ' environments in which to calculate predictability'
                                    ' of distribution. For each environment, you can specify'
                                    ' either the left-hand side or the right-hand side, or'
                                    ' both. Each of these can be specified using either _features or segments.'
                                    ' Not specifying any environments will calculate the predictability of'
                                    ' distribution across all environments based on frequency alone.'
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

    def generateKwargs(self):
        self.kwargs = {}
        segPairs = self.segPairWidget.value()
        if len(segPairs) == 0:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify at least one segment pair.")
            return None
        self.kwargs['segment_pairs'] = segPairs
        envs = self.envWidget.value()
        if len(envs) > 0:
            self.kwargs['envs'] = envs
            self.kwargs['display_envs'] = {e:d for (e,d) in zip(envs,self.envWidget.displayValue())}
        ##------------------
        try:
            frequency_cutoff = float(self.minFreqEdit.text())
        except ValueError:
            frequency_cutoff = 0.0
        ##-------------------
        self.kwargs['corpus'] = self.corpus
        self.kwargs['context'] = self.variantsWidget.value()
        self.kwargs['sequence_type'] = self.tierWidget.value()
        self.kwargs['strict'] = self.enforceCheck.isChecked()
        self.kwargs['type_token'] = self.typeTokenWidget.value()
        self.kwargs['frequency_cutoff'] = frequency_cutoff
        return self.kwargs

    def setResults(self,results):
        self.results = []
        seg_pairs = self.segPairWidget.value()
        try:
            frequency_cutoff = float(self.minFreqEdit.text())
        except ValueError:
            frequency_cutoff = 0.0
        for i, r in enumerate(results):
            if isinstance(r,dict):
                for env,v in r.items():
                    try:
                        env = self.kwargs['display_envs'][env]
                    except KeyError as e:
                        pass #a few things, like "AVG", don't have a special display name
                    self.results.append({'Corpus': self.corpus.name,
                                        'PCT ver.': __version__,#self.corpus._version,
                                        'Analysis name': self.name.capitalize(),
                                        'First segment': seg_pairs[i][0],
                                        'Second segment': seg_pairs[i][1],
                                        'Environment': env,
                                        'Transcription tier': self.tierWidget.displayValue(),
                                        'Frequency type': self.typeTokenWidget.value().title(),
                                        'Pronunciation variants': self.variantsWidget.value().title(),
                                        'Frequency of first segment': v[2], # freq of seg1
                                        'Frequency of second segment': v[3], #freq of seg2
                                        'Frequency of environment': v[1], #total_tokens,
                                        'Minimum word frequency': frequency_cutoff,
                                        'Result': v[0]} #H
                                        )
            else:
                self.results.append({'Corpus': self.corpus.name,
                                     'PCT ver.': __version__,#self.corpus._version,
                                     'Analysis name': self.name.capitalize(),
                                     'First segment': seg_pairs[i][0],
                                     'Second segment': seg_pairs[i][1],
                                     'Environment': 'FREQ-ONLY',
                                     'Transcription tier': self.tierWidget.displayValue(),
                                     'Frequency type': self.typeTokenWidget.value().title(),
                                     'Pronunciation variants': self.variantsWidget.value().title(),
                                     'Frequency of first segment': r[2], # freq of seg1
                                     'Frequency of second segment': r[3], #freq of seg2
                                     'Frequency of environment': r[1], #total_tokens,
                                     'Minimum word frequency': frequency_cutoff,
                                     'Result': r[0]} #H
                                     )
