from collections import OrderedDict

from corpustools.mutualinfo.mutual_information import mi_env_filter, pointwise_mi
from .imports import *
from .environments import EnvironmentSelectWidget
from .widgets import (BigramWidget, RadioSelectWidget, TierWidget, ContextWidget, SaveFileWidget)
from .windows import FunctionWorker, FunctionDialog
from corpustools.exceptions import PCTError, PCTPythonError
from corpustools.contextmanagers import (CanonicalVariantContext,
                                        MostFrequentVariantContext,
                                        SeparatedTokensVariantContext,
                                        WeightedVariantContext)
from corpustools import __version__


class MIWorker(FunctionWorker):
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
        with cm(kwargs['corpus'], kwargs['sequence_type'],
                kwargs['type_token'], frequency_threshold=kwargs['frequency_cutoff']) as c:
            try:
                envs = kwargs.pop('envs', None)

                if envs:    # if env is set, c(orpus context) is 'extracted'
                    context_output_path = kwargs.pop('context_output_path')  # context_output_path for env context export
                    c = mi_env_filter(c, envs, context_output_path, word_boundary=kwargs['word_boundary'])
                    kwargs['in_word'] = False

                for pair in kwargs['segment_pairs']:
                    res = pointwise_mi(c, pair,
                                       env_filtered=bool(envs),
                                       word_boundary = kwargs['word_boundary'],
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
              'PCT ver.',
              'Analysis name',
              'First segment',
              'Second segment',
              'Domain',
              'Word boundary',
              'Word boundary in bigram',
              'Transcription tier',
              'Frequency type',
              'Pronunciation variants',
              'Minimum word frequency',
              'Environments',
              'Result']

    _about = [('This function calculates the mutual information for a bigram'
                    ' of any two segments, based on their unigram and bigram'
                    ' frequencies in the corpus.'),
                    '',
                    #'References: ',
                    ]

    name = 'mutual information'

    def __init__(self, parent, settings, corpus, inventory, showToolTips):
        FunctionDialog.__init__(self, parent, settings, MIWorker())

        self.corpus = corpus
        self.inventory = inventory
        self.showToolTips = showToolTips

        miFrame = QFrame()
        milayout = QHBoxLayout()

        self.segPairWidget = BigramWidget(self.inventory, wordlist=self.corpus.wordlist)

        milayout.addWidget(self.segPairWidget)

        optionLayout = QFormLayout()

        ##---------------------- 'Tier widget' in Options panel
        self.tierWidget = TierWidget(corpus,include_spelling=False)

        optionLayout.addRow(self.tierWidget)

        ##---------------------- 'Pronunciation variants' in Options panel
        actions = None
        self.variantsWidget = ContextWidget(self.corpus, actions)

        optionLayout.addWidget(self.variantsWidget)

        ##---------------------- 'Type or token frequency' in Options panel
        self.typeTokenWidget = RadioSelectWidget('Type or token frequency',
                                            OrderedDict([('Count types','type'),
                                            ('Count tokens','token')]))
        optionLayout.addWidget(self.typeTokenWidget)

        ##----------------------
        minFreqFrame = QGroupBox('Minimum frequency')
        box = QFormLayout()
        self.minFreqEdit = QLineEdit()
        self.minFreqEdit.setValidator(QDoubleValidator(float('inf'), 0, 8))
        box.addRow('Minimum word frequency:',self.minFreqEdit)

        minFreqFrame.setLayout(box)

        optionLayout.addWidget(minFreqFrame)
        ##----------------------

        self.wordBoundaryWidget = RadioSelectWidget('Word boundary',
                                                 OrderedDict([('Word boundary at the end only (default)', 'Word-end only'),
                                                              ('Keep both word boundaries', 'Both sides'),
                                                              ('Ignore all word boundaries', 'Ignored')]))
        optionLayout.addWidget(self.wordBoundaryWidget)
        ##----------------------
        self.inWordCheck = QCheckBox('Set domain to word (unordered word-internal pMI)')
        self.inWordCheck.clicked.connect(self.set_inword)

        optionLayout.addWidget(self.inWordCheck)

        # self.halveEdgesCheck = QCheckBox('Halve word boundary count')
        # self.halveEdgesCheck.setChecked(True)
        # optionLayout.addWidget(self.halveEdgesCheck)

        optionFrame = QGroupBox('Options')
        optionFrame.setLayout(optionLayout)

        milayout.addWidget(optionFrame)
        miFrame.setLayout(milayout)

        ##---------------------- Environment selection frame (envFrame): check box, selection widget, WB widget, savefile widget
        envFrame = QGroupBox('Environment (optional)')

        envLayout = QFormLayout()

        self.envCheck = QCheckBox('Set an environment filter')
        self.envCheck.clicked.connect(self.set_env_filters)

        self.envWidget = EnvironmentSelectWidget(inventory, middle=False, single_env=True)
        self.envWidget.setTitle('')
        self.envWidget.setEnabled(False)

        self.envWBWidget = RadioSelectWidget('Should word boundaries be able to count as a member of a bigram?',
                                             OrderedDict([('Yes', True),
                                                          ('No', False)]))
        self.envWBWidget.setEnabled(False)

        fileFrame = QGroupBox('Output list of contexts to a file')
        fileLayout = QHBoxLayout()
        fileFrame.setLayout(fileLayout)
        self.saveFileWidget = SaveFileWidget('Select file location', 'Text files (*.txt)')
        self.saveFileWidget.setEnabled(False)
        fileLayout.addWidget(self.saveFileWidget)

        envLayout.addWidget(self.envCheck)
        envLayout.addWidget(self.envWidget)
        envLayout.addWidget(self.envWBWidget)
        envLayout.addWidget(fileFrame)

        envFrame.setLayout(envLayout)

        milayout.addWidget(envFrame)
        ##----------------------

        self.layout().insertWidget(0, miFrame)

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

            # halveEdgesToolTip = ("<FONT COLOR=black>"
            # 'make the number of edge characters (#) equal to '
            #             'the size of the corpus + 1, rather than double the '
            #             'size of the corpus - 1.'
            # "</FONT>")
            # self.halveEdgesCheck.setToolTip(halveEdgesToolTip)

    def generateKwargs(self):
        self.kwargs = {}
        segPairs = self.segPairWidget.value()
        if len(segPairs) == 0:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify at least one bigram.")
            return None

        if self.envCheck.checkState():
            envs = self.envWidget.value()
            if len(envs) > 0:
                self.kwargs['envs'] = envs
                self.kwargs['display_envs'] = {e: d for (e, d) in zip(envs, self.envWidget.displayValue())}
            else:
                reply = QMessageBox.critical(self,
                                             "Missing information", "Please provide at least one environment filter,\n"
                                                                    "or uncheck 'Set an environment filter.'")
                return None
        ##------------------
        try:
            frequency_cutoff = float(self.minFreqEdit.text())
        except ValueError:
            frequency_cutoff = 0.0
        ##-------------------
        self.kwargs['corpus'] = self.corpus
        self.kwargs['context'] = self.variantsWidget.value()
        self.kwargs['type_token'] = self.typeTokenWidget.value()
        self.kwargs['segment_pairs'] = [tuple(y for y in x) for x in segPairs]
        self.kwargs['in_word'] = self.inWordCheck.isChecked()
        self.kwargs['frequency_cutoff'] = frequency_cutoff
        self.kwargs['sequence_type'] = self.tierWidget.value()
        self.kwargs['context_output_path'] = self.saveFileWidget.value() if self.saveFileWidget.value() != '' else ''
        self.kwargs['env_checked'] = self.envCheck.checkState()  # 0 if env_filter unchecked, 2 if checked.
        self.kwargs['word_boundary'] = self.wordBoundaryWidget.value() if not self.envCheck.checkState() \
            else self.envWBWidget.value()
        return self.kwargs

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
        if not (self.envWidget.displayValue() and self.envCheck.checkState()):
            environments = 'None'
            wb̠output = self.wordBoundaryWidget.value() if self.wordBoundaryWidget.isEnabled() else 'N/A'
            env_wb_output = 'N/A'
        else:
            environments = ' ; '.join([x for x in self.envWidget.displayValue()])
            wb̠output = 'N/A'
            env_wb_output = self.envWBWidget.displayValue()
        for i, r in enumerate(results):
            self.results.append({'Corpus': self.corpus.name,
                                'PCT ver.': __version__,#self.corpus._version,
                                'Analysis name': self.name.capitalize(),
                                'First segment': seg_pairs[i][0],
                                'Second segment': seg_pairs[i][1],
                                'Domain': dom,
                                'Word boundary': wb̠output,
                                'Word boundary in bigram': env_wb_output,
                                'Transcription tier': self.tierWidget.displayValue(),
                                'Frequency type': self.typeTokenWidget.value().title(),
                                'Pronunciation variants': self.variantsWidget.value().title(),
                                'Minimum word frequency': frequency_cutoff,
                                'Environments': environments,
                                'Result': r})

    def set_env_filters(self):
        if self.envCheck.checkState():
            self.envWidget.setEnabled(True)
            self.saveFileWidget.setEnabled(True)
            self.envWBWidget.setEnabled(True)
            self.inWordCheck.setEnabled(False)
            self.inWordCheck.setChecked(False)
        else:
            self.envWidget.setEnabled(False)
            self.saveFileWidget.setEnabled(False)
            self.envWBWidget.setEnabled(False)
            self.inWordCheck.setEnabled(True)
        self.WB_widget_enabler()

    def set_inword(self):
        if self.inWordCheck.checkState():
            self.envCheck.setEnabled(False)
            self.envCheck.setChecked(False)
        else:
            self.envCheck.setEnabled(True)
        self.WB_widget_enabler()

    def WB_widget_enabler(self):
        if not self.envCheck.checkState() and not self.inWordCheck.checkState():
            self.wordBoundaryWidget.setEnabled(True)
        else:
            self.wordBoundaryWidget.setEnabled(False)
