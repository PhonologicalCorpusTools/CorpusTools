from collections import OrderedDict

from .imports import *
from .widgets import (SegmentPairSelectWidget, RadioSelectWidget,
                      SaveFileWidget, TierWidget,
                    RestrictedContextWidget)
from .windows import FunctionWorker, FunctionDialog
from corpustools.freqalt.freq_of_alt import calc_freq_of_alt
from corpustools.exceptions import PCTError, PCTPythonError
from corpustools.contextmanagers import (CanonicalVariantContext,
                                        MostFrequentVariantContext)
import time

class FAWorker(FunctionWorker):
    def run(self):
        time.sleep(0.1)
        kwargs = self.kwargs
        self.results = []
        context = kwargs.pop('context')
        if context == RestrictedContextWidget.canonical_value:
            cm = CanonicalVariantContext
        elif context == RestrictedContextWidget.frequent_value:
            cm = MostFrequentVariantContext
        corpus = kwargs.pop('corpus')
        st = kwargs.pop('sequence_type')
        tt = kwargs.pop('type_token')
        ft = kwargs.pop('frequency_cutoff')
        with cm(corpus, st, tt, frequency_threshold = ft) as c:
            try:
                for pair in kwargs['segment_pairs']:
                    res = calc_freq_of_alt(c, pair[0], pair[1],
                                kwargs['algorithm'],
                                min_rel=kwargs['min_rel'], max_rel=kwargs['max_rel'],
                                min_pairs_okay=kwargs['include_minimal_pairs'],
                                from_gui = True, phono_align=kwargs['phono_align'],
                                output_filename=kwargs['output_filename'],
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

class FADialog(FunctionDialog):
    header = ['Corpus',
                'PCT ver.'
                'Analysis name',
                'First segment',
                'Second segment',
                'Algorithm',
                'Phonologically aligned',
                'Transcription tier',
                'Frequency type',
                'Pronunciation variants',
                'Minimum word frequency',
                'Total words in corpus',
                'Total words with alternations',
                'Result']

    _about = [('This function calculates the frequency of alternation '
                    'of two segments. In general, an alternation is seen when'
                    ' different segments occur in corresponding positions of'
                    ' two related words. For example, [s]/[ʃ] in the words'
                    ' [dəpɹɛs] and [dəpɹɛʃәn]. Predictable alternations are'
                    ' often used for analyzing segments as either contrastive'
                    ' or allophonic.'),
                    '',
                    'References: ',
                    ('Johnson, Keith & Babel, Molly. 2010. On the perceptual'
                    ' basis of distinctive _features: Evidence from the perception'
                    ' fricatives by Dutch and English Speakers. Journal of'
                    ' Phonetics. 38:127-136'),
                    ('Lu, Yu-an. 2012. The role of alternation in phonological'
                    ' relationships. Stony Brook Univeristy. Doctoral Dissteration')]

    name = 'frequency of alternation'

    def __init__(self, parent, settings, corpus, inventory, showToolTips):
        FunctionDialog.__init__(self, parent, settings, FAWorker())

        self.corpus = corpus
        self.inventory = inventory
        self.showToolTips = showToolTips

        if not self.corpus.has_transcription:
            self.layout().addWidget(QLabel('Corpus does not have transcription, so not all options are available.'))
        elif self.corpus.specifier is None:
            self.layout().addWidget(QLabel('Corpus does not have a feature system loaded, so not all options are available.'))

        falayout = QHBoxLayout()

        self.segPairWidget = SegmentPairSelectWidget(self.inventory, features = False)

        falayout.addWidget(self.segPairWidget)

        algEnabled = {'Khorsi':True,
                    'Edit distance':True,
                    'Phonological edit distance':
                        (self.corpus.has_transcription and
                            self.corpus.specifier is not None)}
        self.algorithmWidget = RadioSelectWidget('String similarity algorithm',
                                            OrderedDict([('Edit distance','edit_distance'),
                                            ('Phonological edit distance','phono_edit_distance'),
                                            ('Khorsi','khorsi')]),
                                            {'Khorsi':self.khorsiSelected,
                                            'Edit distance':self.editDistSelected,
                                            'Phonological edit distance':self.phonoEditDistSelected},
                                            algEnabled)

        midlayout = QFormLayout()
        midlayout.addWidget(self.algorithmWidget)

        threshFrame = QGroupBox('Threshold values')

        self.minEdit = QLineEdit()
        self.minEdit.setText('-15')
        self.maxEdit = QLineEdit()
        self.maxEdit.setText('6')

        vbox = QFormLayout()
        vbox.addRow('Minimum similarity (Khorsi):',self.minEdit)
        vbox.addRow('Maximum distance (edit distance):',self.maxEdit)

        threshFrame.setLayout(vbox)

        midlayout.addWidget(threshFrame)

        falayout.addLayout(midlayout)
        optionFrame = QGroupBox('Options')

        optionLayout = QVBoxLayout()

        self.tierWidget = TierWidget(corpus,include_spelling=False)

        optionLayout.addWidget(self.tierWidget)

        self.typeTokenWidget = RadioSelectWidget('Type or token',
                                            OrderedDict([('Count types','type'),
                                            ('Count tokens','token')]))

        actions = None
        self.variantsWidget = RestrictedContextWidget(self.corpus, actions)

        optionLayout.addWidget(self.variantsWidget)
        optionLayout.addWidget(self.typeTokenWidget)

        self.minPairsWidget = QCheckBox('Include minimal pairs')

        optionLayout.addWidget(self.minPairsWidget)

        self.alignCheck = QCheckBox('Phonologically align words')

        optionLayout.addWidget(self.alignCheck)

        corpusSizeFrame = QGroupBox('Corpus size')

        self.corpusSizeEdit = QLineEdit()

        vbox = QFormLayout()
        vbox.addRow('Subset corpus:',self.corpusSizeEdit)

        corpusSizeFrame.setLayout(vbox)

        optionLayout.addWidget(corpusSizeFrame)
        
        ##----------------------
        minFreqFrame = QGroupBox('Minimum frequency')
        box = QFormLayout()
        self.minFreqEdit = QLineEdit()
        box.addRow('Minimum word frequency:',self.minFreqEdit)

        minFreqFrame.setLayout(box)

        optionLayout.addWidget(minFreqFrame)
        ##----------------------
        
        fileFrame = QGroupBox('Output file (if desired)')

        self.fileWidget = SaveFileWidget('Select file location','Text files (*.txt)')

        vbox = QHBoxLayout()
        vbox.addWidget(self.fileWidget)

        fileFrame.setLayout(vbox)

        optionLayout.addWidget(fileFrame)

        optionFrame.setLayout(optionLayout)

        falayout.addWidget(optionFrame)

        faframe = QFrame()
        faframe.setLayout(falayout)

        self.layout().insertWidget(0, faframe)

        self.algorithmWidget.initialClick()
        if self.showToolTips:
            self.algorithmWidget.setToolTip(("<FONT COLOR=black>"
            'Select which algorithm to'
                                        ' use for calculating the distance between words. This '
                                        'is used to determine if two words should be considered'
                                        ' an example of an alternation. For more information, '
                                        'refer to "About this function" from the string similarity analysis.'
            "</FONT>"))
            self.segPairWidget.setToolTip(("<FONT COLOR=black>"
            'Select two sounds which may be in alternation.'
            "</FONT>"))

            self.tierWidget.setToolTip(("<FONT COLOR=black>"
                                    'Choose which tier frequency of alternation should'
                                    ' be calculated over (e.g. the whole transcription'
                                    ' or a tier containing only [+voc] segments).'
                                    ' New tiers can be created from the Corpus menu.'
                                    "</FONT>"))
            self.typeTokenWidget.setToolTip(("<FONT COLOR=black>"
            'Select which type of frequency to use'
                                    ' for calculating distance (only relevant for Khorsi). Type'
                                    ' frequency means each letter is counted once per word. Token '
                                    'frequency means each letter is counted as many times as its '
                                    'words frequency in the corpus.'
            "</FONT>"))
            self.minPairsWidget.setToolTip(("<FONT COLOR=black>"
            'Select whether to include minimal'
                                    ' pairs as possible alternations. For example, if you possess'
                                    ' knowledge that minimal pairs should never be counted as an'
                                    ' alternation in the corpus, select "ignore minimal pairs".'
            "</FONT>"))
            threshFrame.setToolTip(("<FONT COLOR=black>"
            'These values set the minimum similarity'
                            ' or maximum distance needed in order for two words to be'
                            ' considered a potential alternation.'
            "</FONT>"))

            corpusSizeFrame.setToolTip(("<FONT COLOR=black>"
            'Select this option to only '
                                        'calculate frequency of alternation over a randomly-'
                                        'selected subset of your corpus. This may be useful '
                                        'for large corpora where calculating frequency of alternation '
                                        'takes a very long time, or for doing Monte Carlo techniques. '
                                        'Leave this blank to use the entire corpus. Enter an integer to '
                                        'get a subset of that exact size. Enter a decimal number to '
                                        'get a proportionally sized subset, e.g. 0.25 will '
                                        'get a subset that is a quarter the size of your original corpus.'
            "</FONT>"))

            self.alignCheck.setToolTip(("<FONT COLOR=black>"
            'Select this option to use '
                                        'PCTs phonological aligner. This is an automated check '
                                        'which attempts to ensure that the two target phonemes are aligned '
                                        '(occur in corresponding positions) in the word pair currently being '
                                        'evaluated as an alternation.'
            "</FONT>"))

            self.fileWidget.setToolTip(("<FONT COLOR=black>"
            'Enter a filename for the list '
                                'of words with a potential alternation of the target two sounds to be outputted'
                                ' to.  This is recommended as a means of double checking the quality '
                                'of alternations as determined by the algorithm.'
            "</FONT>"))

        self.algorithmWidget.initialClick()

    def generateKwargs(self):
        pairBehaviour = 'individual'
        kwargs = {'include_minimal_pairs':self.minPairsWidget.isChecked(),
                    'phono_align':self.alignCheck.isChecked(),
                    'type_token':self.typeTokenWidget.value()}
        segPairs = self.segPairWidget.value()
        if len(segPairs) == 0:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify at least one segment pair.")
            return None
        kwargs['segment_pairs'] = segPairs
        rel_type = self.algorithmWidget.value()
        if rel_type == 'khorsi':
            max_rel = None
            try:
                min_rel = float(self.minEdit.text())
            except ValueError:
                min_rel = None
        else:
            min_rel = None
            try:
                max_rel = float(self.maxEdit.text())
            except ValueError:
                max_rel = None
        try:
            n = int(self.corpusSizeEdit.text())
            if n <= 0 or n >= len(self.corpus):
                raise(ValueError)
            else:
                corpus = self.corpus.get_random_subset(n)
        except ValueError:
            corpus = self.corpus
        ##------------------
        try:
            frequency_cutoff = float(self.minFreqEdit.text())
        except ValueError:
            frequency_cutoff = 0.0
        ##-------------------
        if self.fileWidget.value() != '':
            out_file = self.fileWidget.value()
        else:
            out_file = None
        kwargs['sequence_type'] = self.tierWidget.value()
        kwargs['context'] = self.variantsWidget.value()
        kwargs['algorithm'] = rel_type
        kwargs['corpus'] = corpus
        kwargs['min_rel'] = min_rel
        kwargs['max_rel'] = max_rel
        kwargs['pair_behavior'] = pairBehaviour
        kwargs['frequency_cutoff'] = frequency_cutoff
        kwargs['output_filename'] = out_file
        return kwargs

    def setResults(self, results):
        self.results = []
        seg_pairs = self.segPairWidget.value()
        try:
            frequency_cutoff = float(self.minFreqEdit.text())
        except ValueError:
            frequency_cutoff = 0.0
        for i, r in enumerate(results):
            self.results.append({'Corpus': self.corpus.name,
                                'First segment': seg_pairs[i][0],
                                'Second segment': seg_pairs[i][1],
                                'Algorithm': self.algorithmWidget.displayValue(),
                                'Phonologically aligned': self.alignCheck.isChecked(),
                                'Transcription tier': self.tierWidget.displayValue(),
                                'Frequency type': self.typeTokenWidget.value().title(),
                                'Pronunciation variants': self.variantsWidget.value().title(),
                                'Minimum word frequency': frequency_cutoff,
                                'Total words in corpus': r[0],
                                'Total words with alternations': r[1],
                                'Result': r[2]})

    def khorsiSelected(self):
        self.typeTokenWidget.enable()
        self.minEdit.setEnabled(True)
        self.maxEdit.setEnabled(False)

    def editDistSelected(self):
        self.typeTokenWidget.disable()
        self.minEdit.setEnabled(False)
        self.maxEdit.setEnabled(True)

    def phonoEditDistSelected(self):
        self.typeTokenWidget.disable()
        self.minEdit.setEnabled(False)
        self.maxEdit.setEnabled(True)
