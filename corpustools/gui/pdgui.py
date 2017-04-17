from collections import OrderedDict

from .imports import *
from .widgets import (EnvironmentSelectWidget,
                    SegmentPairSelectWidget, RadioSelectWidget, TierWidget,
                    ContextWidget)
from .windows import FunctionWorker, FunctionDialog
import itertools

from corpustools.prod.pred_of_dist import (calc_prod, calc_prod_all_envs)

from corpustools.exceptions import PCTError, PCTPythonError

from corpustools.contextmanagers import (CanonicalVariantContext,
                                        MostFrequentVariantContext,
                                        SeparatedTokensVariantContext,
                                        WeightedVariantContext)

class PDWorker(FunctionWorker):
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
                envs = kwargs.pop('envs', None)
                for pair in kwargs['segment_pairs']:
                    if envs is not None:
                        for env in envs:
                            env.middle = set(pair)
                        res = calc_prod(c,
                                envs,
                                kwargs['strict'],
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
                'Entropy']

    ABOUT = ['This function calculates'
                ' the predictability of distribution of two sounds, using the measure of entropy'
                ' (uncertainty). Sounds that are entirely predictably distributed (i.e., in'
                ' complementary distribution, commonly assumed to be allophonic), will have'
                ' an entropy of 0. Sounds that are perfectly overlapping in their distributions'
                ' will have an entropy of 1.',
                '',
                'Coded by Scott Mackie and Blake Allen',
                '',
                'References',
                ('Hall, K.C. 2009. A probabilistic model of phonological'
                ' relationships from contrast to allophony. PhD dissertation,'
                ' The Ohio State University.')]

    name = 'predictability of distribution'
    def __init__(self, parent, settings, corpus, showToolTips):
        FunctionDialog.__init__(self, parent, settings, PDWorker())
        self.corpus = corpus
        self.showToolTips = showToolTips

        pdFrame = QFrame()
        pdlayout = QHBoxLayout()

        self.segPairWidget = SegmentPairSelectWidget(corpus.inventory)

        pdlayout.addWidget(self.segPairWidget)

        #addSegClassButton = QPushButton('Add a class of sounds')
        #addSegClassButton.clicked.connect(self.addSegClass)
        #pdlayout.addWidget(addSegClassButton)

        self.envWidget = EnvironmentSelectWidget(corpus.inventory, middle = False)
        self.envWidget.setTitle('Environments (optional)')
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
                                    ' both. Each of these can be specified using either features or segments.'
                                    ' Not specifying any environments will calculate the predictability of'
                                    ' distribution across all environments based on frequency alone.'
            "</FONT>"))

    def addSegClass(self):
        self.addSegClassWindow = SegmentClassSelector(self, self.corpus)
        results = self.addSegClassWindow.exec_()
        if results:
            for p in self.addSegClassWindow.pairs:
                self.segPairWidget.table.model().addRow(p)
            self.class1name = self.addSegClassWindow.class1features
            self.class2name = self.addSegClassWindow.class2features

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
        kwargs = {}
        segPairs = self.segPairWidget.value()
        if len(segPairs) == 0:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify at least one segment pair.")
            return None
        kwargs['segment_pairs'] = segPairs
        envs = self.envWidget.value()
        if len(envs) > 0:
            kwargs['envs'] = envs
        ##------------------
        try:
            frequency_cutoff = float(self.minFreqEdit.text())
        except ValueError:
            frequency_cutoff = 0.0
        ##-------------------
        kwargs['corpus'] = self.corpus
        kwargs['context'] = self.variantsWidget.value()
        kwargs['sequence_type'] = self.tierWidget.value()
        kwargs['strict'] = self.enforceCheck.isChecked()
        kwargs['type_token'] = self.typeTokenWidget.value()
        kwargs['frequency_cutoff'] = frequency_cutoff
        return kwargs

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
                    self.results.append([self.corpus.name,
                                        seg_pairs[i][0],seg_pairs[i][1],
                                        env,
                                        self.tierWidget.displayValue(),
                                        self.typeTokenWidget.value().title(),
                                        self.variantsWidget.value().title(),
                                        v[2], # freq of seg1
                                        v[3], #freq of seg2
                                        v[1], #total_tokens,
                                        frequency_cutoff,
                                        v[0]] #H
                                        )
            else:
                self.results.append([self.corpus.name,
                                        seg_pairs[i][0],seg_pairs[i][1],
                                        'FREQ-ONLY',
                                        self.tierWidget.displayValue(),
                                        self.typeTokenWidget.value().title(),
                                        self.variantsWidget.value().title(),
                                        r[2], # freq of seg1
                                        r[3], #freq of seg2
                                        r[1], #total_tokens
                                        frequency_cutoff,
                                        r[0]]) #H

