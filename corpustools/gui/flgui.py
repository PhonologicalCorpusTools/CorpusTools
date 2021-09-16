from collections import OrderedDict
import corpustools.funcload.functional_load as FL
from corpustools.funcload.io import save_minimal_pairs
from pprint import pprint

from .imports import *
from .widgets import (SegmentPairSelectWidget, RadioSelectWidget, TierWidget, ContextWidget, SaveFileWidget)
from .environments import EnvironmentSelectWidget
from .windows import FunctionWorker, FunctionDialog
from corpustools.exceptions import PCTError, PCTPythonError
from corpustools.contextmanagers import (CanonicalVariantContext, MostFrequentVariantContext,
                                         SeparatedTokensVariantContext, WeightedVariantContext)
from corpustools import __version__


class FLWorker(FunctionWorker):
    def run(self):
        kwargs = self.kwargs

        fl_algorithm = kwargs.pop('algorithm')

        context = kwargs.pop('context')
        if context == ContextWidget.canonical_value:
            cm = CanonicalVariantContext
        elif context == ContextWidget.frequent_value:
            cm = MostFrequentVariantContext
        elif context == ContextWidget.separate_value:
            cm = SeparatedTokensVariantContext
        elif context == ContextWidget.relative_value:
            cm = WeightedVariantContext

        with cm(kwargs.pop('corpus'), kwargs.pop('sequence_type'), kwargs.pop('type_token'),
                frequency_threshold=kwargs.pop('frequency_cutoff')) as c:
            try:
                pairs = kwargs.pop('segment_pairs')
                output_filename = kwargs.pop('output_filename', None)

                if fl_algorithm == 'min_pairs':
                    self.results = FL.minpair_fl_speed(c, pairs, **kwargs)

                else:  # use vectorized algorithm for entropy change
                    self.results = FL.deltah_fl_vectorized(c, pairs, **kwargs)

                if output_filename:
                    save_minimal_pairs(output_filename, self.results)

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
    header = ['Corpus',
              'PCT ver.',
              'Analysis name',
              'First segment',
              'Second segment',
              'Algorithm',
              'Distinguished homophones',
              'Minimal pair type',
              'Count',
              'Transcription tier',
              'Frequency type',
              'Pronunciation variants',
              'Minimum word frequency',
              'Environments',
              'Result']

    _about = [('This function calculates the functional load of the contrast '
               'between any two segments, based on either the number of minimal '
               'pairs or the change in entropy resulting from merging that contrast.'),
              '',
              'References: ',
              ('Surendran, Dinoj & Partha Niyogi. 2003. Measuring '
               'the functional load of phonological contrasts. '
               'In Tech. Rep. No. TR-2003-12.'),
              ('Wedel, Andrew, Abby Kaplan & Scott Jackson. 2013. '
               'High functional load inhibits phonological contrast '
               'loss: A corpus study. Cognition 128.179-86')]

    name = 'functional load'

    def __init__(self, parent, settings, corpus, inventory, showToolTips):
        FunctionDialog.__init__(self, parent, settings, FLWorker())

        self.corpus = corpus
        self.inventory = inventory
        self.showToolTips = showToolTips
        self.kwargs = dict()

        mainLayout = QHBoxLayout()
        self.layout().insertLayout(0, mainLayout)

        # Segment selection widget
        self.segPairWidget = SegmentPairSelectWidget(self.inventory, single_segment=True)  # QGroupbox
        mainLayout.addWidget(self.segPairWidget)

        flOptionsLayout = QVBoxLayout()
        mainLayout.addLayout(flOptionsLayout)

        # FL algorithm
        self.algorithmWidget = RadioSelectWidget('Functional load algorithm',
                                                 OrderedDict([('Minimal pairs', 'min_pairs'),
                                                              ('Change in entropy', 'entropy')]),
                                                 {'Minimal pairs': self.minPairsSelected,
                                                  'Change in entropy': self.entropySelected})
        flOptionsLayout.addWidget(self.algorithmWidget)

        # Minimal pair options
        minPairOptionFrame = QGroupBox('Minimal pair options')
        minPairOptionsLayout = QVBoxLayout()
        minPairOptionFrame.setLayout(minPairOptionsLayout)
        flOptionsLayout.addWidget(minPairOptionFrame)

        self.relativeGroup = QGroupBox()
        relativeGroupLayout = QVBoxLayout()
        self.relativeGroup.setLayout(relativeGroupLayout)

        self.relativeCorpusButton = QRadioButton('Output results relative to the entire corpus')
        self.relativeRelevantButton = QRadioButton('Output results relative to number of possible pairs')
        self.relativeRawButton = QRadioButton('Output results as raw counts')

        self.relativeButtonGroup = QButtonGroup()

        self.relativeButtonGroup.addButton(self.relativeCorpusButton)
        relativeGroupLayout.addWidget(self.relativeCorpusButton)

        self.relativeButtonGroup.addButton(self.relativeRelevantButton)
        relativeGroupLayout.addWidget(self.relativeRelevantButton)

        self.relativeButtonGroup.addButton(self.relativeRawButton)
        relativeGroupLayout.addWidget(self.relativeRawButton)

        self.relativeButtonGroup.setExclusive(True)
        self.relativeRawButton.setChecked(True)

        minPairOptionsLayout.addWidget(self.relativeGroup)

        # homophone
        homophoneGroup = QGroupBox()
        homophoneGroupLayout = QVBoxLayout()
        homophoneGroup.setLayout(homophoneGroupLayout)

        self.homophoneRadioButtonGroup = QButtonGroup()
        self.homophoneRadioButtonGroup.setExclusive(True)
        self.distinguishHomophone = QRadioButton('Distinguish homophones')
        self.notDistinguishHomophone = QRadioButton('Do not distinguish homophones')
        self.notDistinguishHomophone.setChecked(True)
        self.homophoneRadioButtonGroup.addButton(self.distinguishHomophone, 0)
        self.homophoneRadioButtonGroup.addButton(self.notDistinguishHomophone, 1)

        homophoneGroupLayout.addWidget(self.distinguishHomophone)
        homophoneGroupLayout.addWidget(self.notDistinguishHomophone)

        minPairOptionsLayout.addWidget(homophoneGroup)

        # minimal pair definition
        definitionGroup = QGroupBox()
        definitionGroupLayout = QVBoxLayout()
        definitionGroup.setLayout(definitionGroupLayout)

        self.definitionRadioButtonGroup = QButtonGroup()
        self.definitionRadioButtonGroup.setExclusive(True)
        self.trueMinimal = QRadioButton('Only count true minimal pairs')
        self.trueMinimal.setChecked(True)
        self.neutralization = QRadioButton('Minimal pairs by neutralization')

        self.definitionRadioButtonGroup.addButton(self.trueMinimal, 0)
        self.definitionRadioButtonGroup.addButton(self.neutralization, 1)

        definitionGroupLayout.addWidget(self.trueMinimal)
        definitionGroupLayout.addWidget(self.neutralization)

        minPairOptionsLayout.addWidget(definitionGroup)

        # Entropy options
        entropyOptionsFrame = QGroupBox('Entropy options')
        entropyOptionsLayout = QVBoxLayout()
        self.entropyRawButton = QRadioButton('Output results as raw change in entropy')
        self.entropyNormalizationButton = QRadioButton('Output results normalized to corpus size')

        normalizationButtonGroup = QButtonGroup()
        normalizationButtonGroup.addButton(self.entropyRawButton)
        normalizationButtonGroup.addButton(self.entropyNormalizationButton)
        normalizationButtonGroup.setExclusive(True)
        self.entropyRawButton.setChecked(True)

        entropyOptionsLayout.addWidget(self.entropyRawButton)
        entropyOptionsLayout.addWidget(self.entropyNormalizationButton)
        entropyOptionsFrame.setLayout(entropyOptionsLayout)
        flOptionsLayout.addWidget(entropyOptionsFrame)

        standardOptionsLayout = QVBoxLayout()
        mainLayout.addLayout(standardOptionsLayout)

        # Tier options
        self.tierWidget = TierWidget(corpus, include_spelling=False)  # QGroupbox
        standardOptionsLayout.addWidget(self.tierWidget)

        # Variants options
        actions = None
        self.variantsWidget = ContextWidget(self.corpus, actions)
        standardOptionsLayout.addWidget(self.variantsWidget)

        self.typeTokenWidget = RadioSelectWidget('Type or token frequencies',
                                                 OrderedDict([('Type', 'type'),
                                                              ('Token', 'token')]))
        standardOptionsLayout.addWidget(self.typeTokenWidget)

        # Frequency options
        minFreqFrame = QGroupBox('Minimum frequency')
        box = QFormLayout()
        self.minFreqEdit = QLineEdit()
        self.minFreqEdit.setValidator(QDoubleValidator(float('inf'), 0, 8))
        self.minFreqEdit.setText('0.0')
        box.addRow('Minimum word frequency:', self.minFreqEdit)
        minFreqFrame.setLayout(box)
        standardOptionsLayout.addWidget(minFreqFrame)

        # File output options
        fileFrame = QGroupBox('Output list of minimal pairs to a file')
        fileLayout = QHBoxLayout()
        fileFrame.setLayout(fileLayout)
        self.saveFileWidget = SaveFileWidget('Select file location', 'Text files (*.txt)')
        fileLayout.addWidget(self.saveFileWidget)
        standardOptionsLayout.addWidget(fileFrame)

        # Environment widgets
        self.envWidget = EnvironmentSelectWidget(self.inventory, middle=False)
        mainLayout.addWidget(self.envWidget)

        self.algorithmWidget.initialClick()

        if self.showToolTips:

            self.entropyRawButton.setToolTip(
                '<FONT COLOR=black>'
                'When calculating change in entropy, this option prevents normalization of the entropy difference by '
                'the pre-neutralization entropy. This is not the method used by Surendran and Niyogi.'
                '</FONT>'
            )

            self.entropyNormalizationButton.setToolTip(
                '<FONT COLOR=black>'
                'When calculating change in entropy, this option will normalize the entropy difference by '
                'the pre-neutralization entropy. This will replicate the Surendran and Niyogi metric'
                '</FONT>'
            )

            self.distinguishHomophone.setToolTip(
                '<FONT COLOR=black>'
                'Separate entries that have the same transcription will be counted separately. E.g. if the corpus consists of the three entries \'scent\' [sɛnt], \'cent\' [sɛnt], and \'bent\' [bɛnt], there will be two minimal pairs for [s]/[b] and three words in the corpus for relativization purposes.'
                '</FONT>'
            )

            self.notDistinguishHomophone.setToolTip(
                '<FONT COLOR=black>'
                'Separate entries that have the same transcription will be counted only once. E.g. if the corpus consists of the three entries \'scent\' [sɛnt], \'cent\' [sɛnt], and \'bent\' [bɛnt], there will be one minimal pair for [s]/[b] and two words in the corpus for relativization purposes.'
                '</FONT>'
            )

            self.relativeRelevantButton.setToolTip(
                '<FONT COLOR=black>'
                'The raw count of minimal pairs will be divided by the number of words that include either of the pair of target segments.'
                '</FONT>'
            )

            self.relativeCorpusButton.setToolTip(
                '<FONT COLOR=black>'
                'The raw count of minimal pairs will be divided by the number of words in the corpus.'
                '</FONT>'
            )

            self.relativeRawButton.setToolTip(
                '<FONT COLOR=black>'
                'The raw count of minimal pairs will not be changed.'
                '</FONT>'
            )

            self.trueMinimal.setToolTip(
                '<FONT COLOR=black>'
                'E.g. \'sass\'~\'sad\' and \'sad\'~\'dad\' would be included as true minimal pairs, but \'sass\'~\'dad\' would not be included.'
                '</FONT>'
            )

            self.neutralization.setToolTip(
                '<FONT COLOR=black>'
                'E.g. \'sass\'~\'sad\', \'sad\'~\'dad\', and \'sass\'~\'dad\' would all be included as minimal pairs by neutralization.'
                '</FONT>'
            )

            self.tierWidget.setToolTip(
                '<FONT COLOR=black>'
                'Choose which tier functional load should be calculated over (e.g., the whole transcription vs. a tier '
                'containing only [+voc] segments). New tiers can be created from the Corpus menu.'
                '</FONT>'
            )

            self.segPairWidget.setToolTip(
                '<FONT COLOR=black>'
                'Select the segments you are interested in. Choose an "individual segment" to get the average functional '
                'load for that segment across all pairs it could occur in. Choose a "pair of segments" to get the '
                'standard functional load of that pair. Choose a "set of segments based on features" to get the functional '
                'load of a particular featural distinction (e.g., the functional load of voicing in obstruents).'
                '</FONT>'
            )

            self.algorithmWidget.setToolTip(
                '<FONT COLOR=black>'
                'Calculate the functional load either using the contrast between two sets of segments as a count of '
                'minimal pairs or using the decrease in corpus entropy caused by a merger of paired segments in the set.'
                '</FONT>'
            )

            self.saveFileWidget.setToolTip(
                '<FONT COLOR=black>'
                'Note that whether "Distinguish homophones" is checked or not, this file will include all minimal pairs '
                'with unique spellings.'
                '</FONT>'
            )

            self.typeTokenWidget.setToolTip(
                '<FONT COLOR=black>'
                'To replicate Surendran & Niyogi, use token frequency.\n'
                'To mimic Wedel et al.\'s minimal pair counts, use type frequency.'
                '</FONT>'
            )

    def minPairsSelected(self):
        self.saveFileWidget.setEnabled(True)

        self.relativeCorpusButton.setEnabled(True)
        self.relativeRelevantButton.setEnabled(True)
        self.relativeRawButton.setEnabled(True)

        self.entropyNormalizationButton.setEnabled(False)
        self.entropyRawButton.setEnabled(False)

        self.typeTokenWidget.setEnabled(False)

        self.distinguishHomophone.setEnabled(True)
        self.notDistinguishHomophone.setEnabled(True)

        self.trueMinimal.setEnabled(True)
        self.neutralization.setEnabled(True)

    def entropySelected(self):
        self.saveFileWidget.setEnabled(False)

        self.relativeCorpusButton.setEnabled(False)
        self.relativeRelevantButton.setEnabled(False)
        self.relativeRawButton.setEnabled(False)

        self.entropyNormalizationButton.setEnabled(True)
        self.entropyRawButton.setEnabled(True)

        self.typeTokenWidget.setEnabled(True)

        self.distinguishHomophone.setEnabled(False)
        self.notDistinguishHomophone.setEnabled(False)

        self.trueMinimal.setEnabled(False)
        self.neutralization.setEnabled(False)

    def generateKwargs(self):
        segPairs = self.segPairWidget.value()
        if len(segPairs) == 0:
            reply = QMessageBox.critical(
                self,
                'Missing information',
                'Please specify at least one segment pair.')
            return

        frequency_cutoff = float(self.minFreqEdit.text())
        alg = self.algorithmWidget.value()
        self.kwargs = {
            'corpus': self.corpus,
            'segment_pairs': segPairs,
            'context': self.variantsWidget.value(),
            'sequence_type': self.tierWidget.value(),
            'frequency_cutoff': frequency_cutoff,
            'type_token': self.typeTokenWidget.value(),
            'algorithm': alg,
            'environment_filter': self.envWidget.value()
        }

        if alg == 'min_pairs':
            out_file = self.saveFileWidget.value()

            if self.relativeRawButton.isChecked():
                self.kwargs['relativization'] = 'raw'
            elif self.relativeRelevantButton.isChecked():
                self.kwargs['relativization'] = 'relevant'
            elif self.relativeCorpusButton.isChecked():
                self.kwargs['relativization'] = 'corpus'

            self.kwargs['distinguish_homophones'] = True if self.homophoneRadioButtonGroup.checkedId() == 0 else False
            self.kwargs['minimal_pair_definition'] = 'true' if self.definitionRadioButtonGroup.checkedId() == 0 else 'neutralization'
            self.kwargs['output_filename'] = out_file if out_file else None
        else:
            self.kwargs['normalization'] = self.entropyNormalizationButton.isChecked()

        return self.kwargs

    def setResults(self, results):
        self.results = []
        try:
            frequency_cutoff = float(self.minFreqEdit.text())
        except ValueError:
            frequency_cutoff = 0.0

        for pair, value, pair_dict in results:

            if len(pair) == 1:
                seg_one = pair[0]
                seg_two = ''
            else:
                seg_one = pair[0]
                seg_two = pair[1]

            if not self.envWidget.displayValue():
                environments = 'None'
            else:
                environments = ' ; '.join([x for x in self.envWidget.displayValue()])

            # minimal pairs
            if self.relativeRawButton.isEnabled():
                if self.relativeRelevantButton.isChecked():
                    count_str = 'Relative to min pairs'
                elif self.relativeCorpusButton.isChecked():
                    count_str = 'Relative to corpus size'
                else:
                    count_str = 'Raw frequency'
            elif self.entropyRawButton.isEnabled():
                if self.entropyRawButton.isChecked():
                    count_str = 'Raw entropy'
                else:
                    count_str = 'Normalized to corpus size'

            self.results.append({'Corpus': self.corpus.name,
                                 'PCT ver.': __version__,  # self.corpus._version,
                                 'Analysis name': self.name.capitalize(),
                                 'First segment': seg_one,
                                 'Second segment': seg_two,
                                 'Algorithm': self.algorithmWidget.displayValue(),
                                 'Distinguished homophones': self.distinguishHomophone.isChecked(),
                                 'Minimal pair type': 'True minimal pairs' if self.trueMinimal.isChecked() else 'Neutralization',
                                 'Count': count_str,  # self.relativeCountWidget.isChecked(),
                                 'Transcription tier': self.tierWidget.displayValue(),
                                 'Frequency type': self.typeTokenWidget.value().title(),
                                 'Pronunciation variants': self.variantsWidget.value().title(),
                                 'Minimum word frequency': frequency_cutoff,
                                 'Environments': environments,
                                 'Result': value})

# ========== old code below ==========


# class FLDialog(FunctionDialog):
#     header = ['Corpus',
#               'PCT ver.',
#               'First segment',
#               'Second segment',
#               'Algorithm',
#               'Distinguished homophones',
#               'Count',
#               'Transcription tier',
#               'Frequency type',
#               'Pronunciation variants',
#               'Minimum word frequency',
#               'Environments',
#               'Result']
#               #'Non-normalized result']
#
#     _about = [('This function calculates the functional load of the contrast'
#                     ' between any two segments, based on either the number of minimal'
#                     ' pairs or the change in entropy resulting from merging that contrast.'),
#                     '',
#                     'References: ',
#                     ('Surendran, Dinoj & Partha Niyogi. 2003. Measuring'
#                     ' the functional load of phonological contrasts.'
#                     ' In Tech. Rep. No. TR-2003-12.'),
#                     ('Wedel, Andrew, Abby Kaplan & Scott Jackson. 2013.'
#                     ' High functional load inhibits phonological contrast'
#                     ' loss: A corpus study. Cognition 128.179-86')]
#
#     name = 'functional load'
#
#     def __init__(self, parent, settings, corpus, inventory, showToolTips):
#         FunctionDialog.__init__(self, parent, settings, FLWorker())
#
#         self.corpus = corpus
#         self.inventory = inventory
#         self.showToolTips = showToolTips
#         self.kwargs = dict()
#
#         mainFrame = QFrame()
#         mainLayout = QHBoxLayout()
#
#         #Set up algorithm options
#         # self.optionsList = QListWidget()
#         # self.optionsList.addItem('Segment selection')
#         # self.optionsList.addItem('Functional load options')
#         # self.optionsList.addItem('Standard options')
#         # self.optionsList.addItem('Envrionments')
#         # mainLayout.addWidget(self.optionsList)
#
#         #Set up segment selection widgets
#         segFrame = QFrame()
#         segPairLayout = QVBoxLayout()
#         segFrame.setLayout(segPairLayout)
#
#         self.segPairWidget = SegmentPairSelectWidget(self.inventory, single_segment=True)
#         segPairLayout.addWidget(self.segPairWidget)
#
#
#         #Set up functional load option widgets
#         flOptionsFrame = QFrame()
#         flOptionsLayout = QVBoxLayout()
#         flOptionsFrame.setLayout(flOptionsLayout)
#
#         #algorithm options
#         algorithmFrame = QGroupBox('Algorithm selection')
#         algorithmLayout = QVBoxLayout()
#         self.algorithmWidget = RadioSelectWidget('Functional load algorithm',
#                                                  OrderedDict([('Minimal pairs', 'min_pairs'),
#                                                               ('Change in entropy', 'entropy')]),
#                                                  {'Minimal pairs': self.minPairsSelected,
#                                                   'Change in entropy': self.entropySelected})
#         algorithmLayout.addWidget(self.algorithmWidget)
#         algorithmFrame.setLayout(algorithmLayout)
#         flOptionsLayout.addWidget(algorithmFrame)
#
#         #miniminal pair options
#         minPairOptionFrame = QGroupBox('Minimal pair options')
#         minPairOptionsLayout = QVBoxLayout()
#         self.relativeCountCorpusWidget = QRadioButton('Output results relative to the entire corpus')
#         self.relativeCountWidget = QRadioButton('Output results relative to number of possible pairs')
#         self.noRelativeCountWidget = QRadioButton('Output results as raw counts')
#         self.relativeButtonGroup = QButtonGroup()
#         self.relativeButtonGroup.addButton(self.relativeCountCorpusWidget)
#         minPairOptionsLayout.addWidget(self.relativeCountCorpusWidget)
#         self.relativeButtonGroup.addButton(self.relativeCountWidget)
#         minPairOptionsLayout.addWidget(self.relativeCountWidget)
#         self.relativeButtonGroup.addButton(self.noRelativeCountWidget)
#         minPairOptionsLayout.addWidget(self.noRelativeCountWidget)
#         self.relativeButtonGroup.setExclusive(True)
#         self.relativeCountCorpusWidget.setChecked(True)
#         self.homophoneWidget = QCheckBox('Distinguish homophones')
#         minPairOptionsLayout.addWidget(self.homophoneWidget)
#         minPairOptionFrame.setLayout(minPairOptionsLayout)
#         flOptionsLayout.addWidget(minPairOptionFrame)
#
#         #entropy options
#         entropyOptionsFrame = QGroupBox('Entropy options')
#         entropyOptionsLayout = QVBoxLayout()
#         self.preventNormalizationWidget = QRadioButton('Output results as raw change in entropy')
#         self.allowNormalizationWidget = QRadioButton('Output results normalized to corpus size')
#         normalizationButtonGroup = QButtonGroup()
#         normalizationButtonGroup.addButton(self.preventNormalizationWidget)
#         normalizationButtonGroup.addButton(self.allowNormalizationWidget)
#         normalizationButtonGroup.setExclusive(True)
#         self.allowNormalizationWidget.setChecked(True)
#         entropyOptionsLayout.addWidget(self.allowNormalizationWidget)
#         entropyOptionsLayout.addWidget(self.preventNormalizationWidget)
#         entropyOptionsFrame.setLayout(entropyOptionsLayout)
#         flOptionsLayout.addWidget(entropyOptionsFrame)
#
#         #file output options
#         fileFrame = QGroupBox('Output list of minimal pairs to a file')
#         fileLayout = QHBoxLayout()
#         fileFrame.setLayout(fileLayout)
#         self.saveFileWidget = SaveFileWidget('Select file location', 'Text files (*.txt)')
#         fileLayout.addWidget(self.saveFileWidget)
#         flOptionsLayout.addWidget(fileFrame)
#
#         #Set up standard option widgets
#         standardOptionsFrame = QFrame()
#         standardOptionsLayout = QVBoxLayout()
#         standardOptionsFrame.setLayout(standardOptionsLayout)
#
#         #tier options
#         self.tierWidget = TierWidget(corpus, include_spelling=False)
#         standardOptionsLayout.addWidget(self.tierWidget)
#
#         #variants options
#         actions = None
#         self.variantsWidget = ContextWidget(self.corpus, actions)
#         standardOptionsLayout.addWidget(self.variantsWidget)
#
#         self.typeTokenWidget = RadioSelectWidget('Type or token frequencies',
#                                                  OrderedDict([('Type', 'type'),
#                                                               ('Token', 'token')]))
#         standardOptionsLayout.addWidget(self.typeTokenWidget)
#
#         #frequency options
#         minFreqFrame = QGroupBox('Minimum frequency')
#         box = QFormLayout()
#         self.minFreqEdit = QLineEdit()
#         box.addRow('Minimum word frequency:', self.minFreqEdit)
#         minFreqFrame.setLayout(box)
#         standardOptionsLayout.addWidget(minFreqFrame)
#
#         #Set up environment widgets
#         environmentsFrame = QFrame()
#         environmentsLayout = QVBoxLayout()
#         environmentsFrame.setLayout(environmentsLayout)
#         self.envWidget = EnvironmentSelectWidget(self.inventory, middle=False)
#         environmentsLayout.addWidget(self.envWidget)
#
#         #Update layout
#         mainLayout.addWidget(segFrame)
#         mainLayout.addWidget(flOptionsFrame)
#         mainLayout.addWidget(standardOptionsFrame)
#         mainLayout.addWidget(environmentsFrame)
#
#         #Set up stacked widgets
#         # self.stackedWidget = QStackedWidget()
#         # self.stackedWidget.addWidget(segFrame)
#         # self.stackedWidget.addWidget(flOptionsFrame)
#         # self.stackedWidget.addWidget(standardOptionsFrame)
#         # self.stackedWidget.addWidget(environmentsFrame)
#         # self.stackedWidget.setCurrentIndex(0)
#         #
#         # mainLayout.addWidget(self.stackedWidget)
#         # self.optionsList.currentRowChanged.connect(self.stackedWidget.setCurrentIndex)
#
#         mainFrame.setLayout(mainLayout)
#         self.layout().insertWidget(0, mainFrame)
#         self.algorithmWidget.initialClick()
#
#         if self.showToolTips:
#
#             self.preventNormalizationWidget.setToolTip(('<FONT COLOR=black>'
#             'When calculating change in entropy, this option prevents normalization of the entropy difference by '
#                         'the pre-neutralization entropy. This is not the method used by Surendran and Niyogi.'
#             '</FONT>'))
#
#             self.allowNormalizationWidget.setToolTip(('<FONT COLOR=black>'
#                                                         'When calculating change in entropy, this option will normalize the entropy difference by '
#                                                         'the pre-neutralization entropy. This will replicate the Surendran and Niyogi metric'
#                                                         '</FONT>'))
#
#             self.homophoneWidget.setToolTip(("<FONT COLOR=black>"
#             'This setting will overcount alternative'
#                             ' spellings of the same word, e.g. axel~actual and axle~actual,'
#                             ' but will allow you to count e.g. sock~shock twice, once for each'
#                             ' meaning of \'sock\' (footwear vs. punch)'
#             "</FONT>"))
#
#             self.relativeCountWidget.setToolTip(("<FONT COLOR=black>"
#             'The raw count of minimal pairs will'
#                             ' be divided by the number of words that include any of the target segments'
#                             ' present in the list at the left.'
#             "</FONT>"))
#             self.relativeCountCorpusWidget.setToolTip(("<FONT COLOR=black>"
#                                                  'The raw count of minimal pairs will'
#                                                  ' be divided by the number of words in the corpus.'
#                                                  "</FONT>"))
#             self.noRelativeCountWidget.setToolTip(("<FONT COLOR=black>"
#                                                  'The raw count of minimal pairs will not be changed.'
#                                                  "</FONT>"))
#             self.tierWidget.setToolTip(("<FONT COLOR=black>"
#                                     'Choose which tier functional load should'
#                                     ' be calculated over (e.g., the whole transcription'
#                                     ' vs. a tier containing only [+voc] segments).'
#                                     ' New tiers can be created from the Corpus menu.'
#                                     "</FONT>"))
#             self.segPairWidget.setToolTip(('<FONT COLOR=black>'
#                             'Select the segments you are interested in. Choose an "individual segment" to get the '
#                             'average functional load for that segment across all pairs it could occur in. Choose a '
#                             '"pair of segments" to get the standard functional load of that pair. Choose a "set of segments'
#                             'based on features" to get the functional load of a particular featural distinction '
#                             '(e.g., the functional load of voicing in obstruents).'
#                             '</FONT>'))
#             self.algorithmWidget.setToolTip(("<FONT COLOR=black>"
#             'Calculate the functional load either using'
#                             ' the contrast between two sets of segments as a count of minimal pairs'
#                             ' or using the decrease in corpus'
#                             ' entropy caused by a merger of paired segments in the set.'
#             "</FONT>"))
#             self.saveFileWidget.setToolTip(("<FONT COLOR=black>"
#             'Note that whether "Distinguish homophones" is checked or not, this file will'
#             ' include all minimal pairs with unique spellings.'
#             "</FONT>"))
#             self.typeTokenWidget.setToolTip('<FONT COLOR=black>To replicate Surendran & Niyogi, use token frequency.\n'
#                                     'To mimic Wedel et al.\'s minimal pair counts, use type frequency.</FONT>')
#
#     def minPairsSelected(self):
#         self.saveFileWidget.setEnabled(True)
#         self.relativeCountWidget.setEnabled(True)
#         self.relativeCountCorpusWidget.setEnabled(True)
#         self.noRelativeCountWidget.setEnabled(True)
#         self.homophoneWidget.setEnabled(True)
#         self.preventNormalizationWidget.setEnabled(False)
#         self.allowNormalizationWidget.setEnabled(False)
#         #self.typeTokenWidget.widgets[0].setChecked(True)
#         self.typeTokenWidget.setEnabled(False)
#
#     def entropySelected(self):
#         self.saveFileWidget.setEnabled(False)
#         self.relativeCountWidget.setEnabled(False)
#         self.relativeCountCorpusWidget.setEnabled(False)
#         self.noRelativeCountWidget.setEnabled(False)
#         self.homophoneWidget.setEnabled(False)
#         self.preventNormalizationWidget.setEnabled(True)
#         self.allowNormalizationWidget.setEnabled(True)
#         # self.typeTokenWidget.widgets[1].setChecked(True)
#         self.typeTokenWidget.setEnabled(True)
#
#     def generateKwargs(self):
#         segPairs = self.segPairWidget.value()
#         if len(segPairs) == 0:
#             reply = QMessageBox.critical(self,
#                     "Missing information", "Please specify at least one segment pair.")
#             return None
#         try:
#             frequency_cutoff = float(self.minFreqEdit.text())
#         except ValueError:
#             frequency_cutoff = 0.0
#         alg = self.algorithmWidget.value()
#         self.kwargs = {'corpus':self.corpus,
#                 'segment_pairs':segPairs,
#                 'context': self.variantsWidget.value(),
#                 'sequence_type': self.tierWidget.value(),
#                 'frequency_cutoff':frequency_cutoff,
#                 'type_token':self.typeTokenWidget.value(),
#                 'algorithm': alg,
#                 'prevent_normalization': self.preventNormalizationWidget.isChecked(),
#                 'environment_filter': self.envWidget.value()}
#         if alg == 'min_pairs':
#             out_file = self.saveFileWidget.value()
#             if out_file == '':
#                 out_file = None
#             self.kwargs['relative_count_to_relevant_sounds'] = self.relativeCountWidget.isChecked()
#             self.kwargs['relative_count_to_whole_corpus'] = self.relativeCountCorpusWidget.isChecked()
#             self.kwargs['distinguish_homophones'] = self.homophoneWidget.isChecked()
#             self.kwargs['output_filename'] = out_file
#
#         return self.kwargs
#
#     def setResults(self, results):
#         self.results = []
#         seg_pairs = self.segPairWidget.value()
#         try:
#             frequency_cutoff = float(self.minFreqEdit.text())
#         except ValueError:
#             frequency_cutoff = 0.0
#         for i, r in enumerate(results):
#             # if isinstance(r, tuple):
#             #     print('this is a tuple ', r)
#             #     r = r[0]
#             seg_one = seg_pairs[i][0]
#             try:
#                 seg_two = seg_pairs[i][1]
#             except IndexError:
#                 seg_two = ''
#
#             if not self.envWidget.displayValue():
#                 environments = 'None'
#             else:
#                 environments = ' ; '.join([x for x in self.envWidget.displayValue()])
#
#             if isinstance(r, float):
#                 r = [r]
#
#
#             pre_normalized = r[-1]
#
#             if self.relativeCountWidget.isEnabled():
#                 if self.relativeCountWidget.isChecked():
#                     count_str = 'Relative to min pairs'
#                 elif self.relativeCountCorpusWidget.isChecked():
#                     count_str = 'Relative to corpus size'
#                 else:
#                     count_str = 'Raw frequency'
#             elif self.preventNormalizationWidget.isEnabled():
#                 if self.preventNormalizationWidget.isChecked():
#                     count_str = 'Raw entropy'
#                 else:
#                     count_str = 'Normalized to corpus size'
#
#             self.results.append({'Corpus': self.corpus.name,
#                                 'PCT ver.': __version__,#self.corpus._version,
#                                 'First segment': seg_one,
#                                 'Second segment': seg_two,
#                                 'Algorithm': self.algorithmWidget.displayValue(),
#                                 'Distinguished homophones': self.homophoneWidget.isChecked(),
#                                 'Count': count_str,# self.relativeCountWidget.isChecked(),
#                                 'Transcription tier': self.tierWidget.displayValue(),
#                                 'Frequency type': self.typeTokenWidget.value().title(),
#                                 'Pronunciation variants': self.variantsWidget.value().title(),
#                                 'Minimum word frequency': frequency_cutoff,
#                                 'Environments': environments,
#                                 #'Non-normalized result': normalized,
#                                 'Result': r[0]})
