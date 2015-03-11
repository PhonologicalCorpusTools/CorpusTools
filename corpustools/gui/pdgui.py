
from .imports import *

from collections import OrderedDict

from .widgets import EnvironmentSelectWidget, SegmentPairSelectWidget, RadioSelectWidget,TierWidget

from .windows import FunctionWorker, FunctionDialog

from corpustools.prod.pred_of_dist import (calc_prod, calc_prod_all_envs,
                        calc_prod_wordtokens, calc_prod_wordtokens_all_envs)

from corpustools.exceptions import PCTError, PCTPythonError

class PDWorker(FunctionWorker):
    def run(self):
        time.sleep(0.1)
        kwargs = self.kwargs
        self.results = list()
        if 'envs' in kwargs:
            if kwargs['pair_behavior'] == 'individual':

                for pair in kwargs['segment_pairs']:
                    try:
                        if kwargs['wordtokens']:
                            res = calc_prod_wordtokens(kwargs['corpus'], pair[0],pair[1],
                                kwargs['envs'],
                                kwargs['sequence_type'],
                                kwargs['type_token'],
                                kwargs['strict'],
                                True,
                                stop_check = kwargs['stop_check'],
                                call_back = kwargs['call_back'])
                        else:
                            res = calc_prod(kwargs['corpus'], pair[0],pair[1],
                                kwargs['envs'],
                                kwargs['sequence_type'],
                                kwargs['type_token'],
                                kwargs['strict'],
                                True,
                                stop_check = kwargs['stop_check'],
                                call_back = kwargs['call_back'])
                    except PCTError as e:
                        self.errorEncountered.emit(e)
                        return
                    except Exception as e:
                        e = PCTPythonError(e)
                        self.errorEncountered.emit(e)
                        return
                    if self.stopped:
                        break
                    self.results.append(res)
            else:
                raise(NotImplementedError)
                self.results.append(res)
        else:
            if kwargs['pair_behavior'] == 'individual':

                for pair in kwargs['segment_pairs']:
                    try:
                        if kwargs['wordtokens']:
                            res = calc_prod_wordtokens_all_envs(kwargs['corpus'], pair[0],pair[1],
                                kwargs['sequence_type'],
                                kwargs['type_token'],
                                True,
                                stop_check = kwargs['stop_check'],
                                call_back = kwargs['call_back'])
                        else:
                            res = calc_prod_all_envs(kwargs['corpus'], pair[0],pair[1],
                                kwargs['sequence_type'],
                                kwargs['type_token'],
                                True,
                                stop_check = kwargs['stop_check'],
                                call_back = kwargs['call_back'])
                    except PCTError as e:
                        self.errorEncountered.emit(e)
                        return
                    except Exception as e:
                        e = PCTPythonError(e)
                        self.errorEncountered.emit(e)
                        return
                    if self.stopped:
                        break
                    self.results.append(res)
            else:
                raise(NotImplementedError)
                self.results.append(res)
        if self.stopped:
            self.finishedCancelling.emit()
            return
        self.dataReady.emit(self.results)

class PDDialog(FunctionDialog):
    header = ['Sound1',
                'Sound2',
                'Tier',
                'Environment',
                'Freq. of Sound1',
                'Freq. of Sound2',
                'Freq. of env.',
                'Entropy',
                'Type or token']

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
    def __init__(self, parent, corpus, showToolTips):
        FunctionDialog.__init__(self, parent, PDWorker())

        self.corpus = corpus
        self.showToolTips = showToolTips

        pdFrame = QFrame()
        pdlayout = QHBoxLayout()

        self.segPairWidget = SegmentPairSelectWidget(corpus.inventory)

        pdlayout.addWidget(self.segPairWidget)

        self.envWidget = EnvironmentSelectWidget(corpus.inventory)
        self.envWidget.setTitle('Environments (optional)')
        pdlayout.addWidget(self.envWidget)


        optionLayout = QVBoxLayout()

        typetokenEnabled = {'Word types':self.corpus.has_transcription,
                    'Word tokens':self.corpus.has_wordtokens}
        self.wordtokensWidget = RadioSelectWidget('Analyze word types or tokens',
                                            OrderedDict([('Word types','wordtypes'),
                                            ('Word tokens','wordtokens')
                                            ]),
                                            {'Word types':self.typesSelected,
                                            'Word tokens':self.tokensSelected},
                                            typetokenEnabled)

        optionLayout.addWidget(self.wordtokensWidget)

        self.tierWidget = TierWidget(corpus,include_spelling=False)

        optionLayout.addWidget(self.tierWidget)

        self.typeTokenWidget = RadioSelectWidget('Type or token frequency',
                                            OrderedDict([('Count types','type'),
                                            ('Count tokens','token')]))

        optionLayout.addWidget(self.typeTokenWidget)


        checkFrame = QGroupBox('Exhaustivity and uniqueness')

        checkLayout = QVBoxLayout()

        self.enforceCheck = QCheckBox('Enforce environment\nexhaustivity and uniqueness')
        self.enforceCheck.setChecked(True)

        checkLayout.addWidget(self.enforceCheck)

        checkFrame.setLayout(checkLayout)

        optionLayout.addWidget(checkFrame)

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

        kwargs['corpus'] = self.corpus
        if self.wordtokensWidget.value() == 'wordtokens':
            kwargs['wordtokens'] = True
        else:
            kwargs['wordtokens'] = False
        kwargs['sequence_type'] = self.tierWidget.value()
        kwargs['strict'] = self.enforceCheck.isChecked()
        kwargs['pair_behavior'] = 'individual'
        kwargs['type_token'] = self.typeTokenWidget.value()
        return kwargs

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
        seg_pairs = self.segPairWidget.value()
        seg_pairs_options = 'individual'
        if seg_pairs_options == 'individual':
            for i, r in enumerate(results):
                if isinstance(r,dict):
                    for env,v in r.items():
                        self.results.append([seg_pairs[i][0],seg_pairs[i][1],
                                            self.tierWidget.displayValue(),
                                            env,
                                            v[2], # freq of seg1
                                            v[3], #freq of seg2
                                            v[1], #total_tokens
                                            v[0], #H
                                            self.typeTokenWidget.value()])
                else:
                    self.results.append([seg_pairs[i][0],seg_pairs[i][1],
                                            self.tierWidget.displayValue(),
                                            'FREQ-ONLY',
                                            r[2], # freq of seg1
                                            r[3], #freq of seg2
                                            r[1], #total_tokens
                                            r[0], #H
                                            self.typeTokenWidget.value()])
