
from .imports import *

from collections import OrderedDict

from .widgets import SegmentPairSelectWidget, RadioSelectWidget, FileWidget, SaveFileWidget, TierWidget

from .windows import FunctionWorker, FunctionDialog

from corpustools.freqalt.freq_of_alt import calc_freq_of_alt

class FAWorker(FunctionWorker):
    def run(self):
        kwargs = self.kwargs
        self.results = list()
        if kwargs['pair_behavior'] == 'individual':

            for pair in kwargs['segment_pairs']:
                try:
                    res = calc_freq_of_alt(kwargs['corpus'], pair[0], pair[1],
                                kwargs['relator_type'], kwargs['count_what'],
                                sequence_type = kwargs['sequence_type'],
                                min_rel=kwargs['min_rel'], max_rel=kwargs['max_rel'],
                                min_pairs_okay=kwargs['include_minimal_pairs'],
                                from_gui=True, phono_align=kwargs['phono_align'],
                                output_filename=kwargs['output_filename'],
                                stop_check = kwargs['stop_check'],
                                call_back = kwargs['call_back'])
                except Exception as e:
                    self.errorEncountered.emit(e)
                    return
                if self.stopped:
                    return
                self.results.append(res)
        else:
            raise(NotImplementedError)
            self.results.append(res)
        self.dataReady.emit(self.results)

class FADialog(FunctionDialog):
    header = ['Segment 1',
                'Segment 2',
                'Transcription tier',
                'Total words in corpus',
                'Total words with alternations',
                'Frequency of alternation',
                'Type or token',
                'Distance metric',
                'Phonological alignment?']

    _about = [('This function calculates the frequency of alternation '
                    'of two segments'),
                    '',
                    'Coded by Michael Fry',
                    #'',
                    #'References',
                    #('Surendran, Dinoj & Partha Niyogi. 2003. Measuring'
                    #' the functional load of phonological contrasts.'
                    #' In Tech. Rep. No. TR-2003-12.'),
                    #('Wedel, Andrew, Abby Kaplan & Scott Jackson. 2013.'
                    #' High functional load inhibits phonological contrast'
                    #' loss: A corpus study. Cognition 128.179-86')
                    ]

    name = 'frequency of alternation'

    def __init__(self, parent, corpus, showToolTips):
        FunctionDialog.__init__(self, parent, FAWorker())

        self.corpus = corpus
        self.showToolTips = showToolTips

        falayout = QHBoxLayout()

        self.segPairWidget = SegmentPairSelectWidget(corpus.inventory)

        falayout.addWidget(self.segPairWidget)


        self.algorithmWidget = RadioSelectWidget('String similarity algorithm',
                                            OrderedDict([('Khorsi','khorsi'),
                                            ('Edit distance','edit_distance'),
                                            ('Phonological edit distance','phono_edit_distance')]),
                                            {'Khorsi':self.khorsiSelected,
                                            'Edit distance':self.editDistSelected,
                                            'Phonological edit distance':self.phonoEditDistSelected})


        falayout.addWidget(self.algorithmWidget)

        optionFrame = QGroupBox('Options')

        optionLayout = QVBoxLayout()

        self.tierWidget = TierWidget(corpus,include_spelling=False)

        optionLayout.addWidget(self.tierWidget)

        self.typeTokenWidget = RadioSelectWidget('Type or token',
                                            OrderedDict([('Count types','type'),
                                            ('Count tokens','token')]))

        optionLayout.addWidget(self.typeTokenWidget)

        self.minPairsWidget = QCheckBox('Include minimal pairs')

        optionLayout.addWidget(self.minPairsWidget)

        threshFrame = QGroupBox('Threshold values')

        self.minEdit = QLineEdit()
        self.minEdit.setText('-15')
        self.maxEdit = QLineEdit()
        self.maxEdit.setText('6')

        vbox = QFormLayout()
        vbox.addRow('Minimum similarity (Khorsi):',self.minEdit)
        vbox.addRow('Maximum distance (edit distance):',self.maxEdit)

        threshFrame.setLayout(vbox)

        optionLayout.addWidget(threshFrame)

        alignFrame = QGroupBox('Alignment')

        self.alignCheck = QCheckBox('Do phonological alignment')

        vbox = QVBoxLayout()
        vbox.addWidget(self.alignCheck)

        alignFrame.setLayout(vbox)

        optionLayout.addWidget(alignFrame)

        corpusSizeFrame = QGroupBox('Corpus size')

        self.corpusSizeEdit = QLineEdit()

        vbox = QFormLayout()
        vbox.addRow('Subset corpus:',self.corpusSizeEdit)

        corpusSizeFrame.setLayout(vbox)

        optionLayout.addWidget(corpusSizeFrame)

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
                                        ' use for calculating the similarity of words. This '
                                        'is used to determine if two words could be considered'
                                        ' an example of an alternation. For more information, '
                                        'refer to "About this function" on the string similarity analysis option.'
            "</FONT>"))
            self.segPairWidget.setToolTip(("<FONT COLOR=black>"
            'Select the two sounds you wish to check for alternations.'
            "</FONT>"))

            self.tierWidget.setToolTip(("<FONT COLOR=black>"
                                    'Choose which tier frequency of alternation should'
                                    ' be calculated over (e.g., the whole transcription'
                                    ' vs. a tier containing only [+voc] segments).'
                                    ' New tiers can be created from the Corpus menu.'
                                    "</FONT>"))
            self.typeTokenWidget.setToolTip(("<FONT COLOR=black>"
            'Select which type of frequency to use'
                                    ' for calculating similarity (only relevant for Khorsi). Type'
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
                            ' or maximum distance needed in order to consider two words to be'
                            ' considered a potential example of an alternation.'
            "</FONT>"))
            corpusSizeFrame.setToolTip(("<FONT COLOR=black>"
            'Select this option to only '
                                        'calculate frequency of alternation over a randomly-'
                                        'selected subset of your corpus. This may be useful '
                                        'for large corpora where calculating frequency of alternation '
                                        'takes a very long time, or for doing Monte Carlo techniques. '
                                        'Leave blank to use the entire corpus. Enter an integer to '
                                        'get a subset of that exact size. Enter a decimal number to '
                                        'get a proportionally sized subset, e.g. 0.25 will '
                                        'get a subset that is a quarter the size of your original corpus.'
            "</FONT>"))
            self.fileWidget.setToolTip(("<FONT COLOR=black>"
            'Enter a filename for the list '
                                'of words with an alternation of the target two sounds to be outputted'
                                ' to.  This is recommended as a means of double checking the quality '
                                'of alternations as determined by the algorithm.'
            "</FONT>"))

        self.algorithmWidget.initialClick()

    def generateKwargs(self):
        pairBehaviour = 'individual'
        kwargs = {'include_minimal_pairs':self.minPairsWidget.isChecked(),
                    'phono_align':self.alignCheck.isChecked(),
                    'count_what':self.typeTokenWidget.value()}
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
        if self.fileWidget.value() != '':
            out_file = self.fileWidget.value()
        else:
            out_file = None
        kwargs['sequence_type'] = self.tierWidget.value()
        kwargs['relator_type'] = rel_type
        kwargs['corpus'] = corpus
        kwargs['min_rel'] = min_rel
        kwargs['max_rel'] = max_rel
        kwargs['pair_behavior'] = pairBehaviour
        kwargs['output_filename'] = out_file
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

    def setResults(self, results):
        self.results = list()
        seg_pairs = self.segPairWidget.value()
        pair_behaviour = 'individual'
        if pair_behaviour == 'individual':
            for i, r in enumerate(results):
                self.results.append([seg_pairs[i][0],seg_pairs[i][1],
                                    self.tierWidget.displayValue(),
                                    r[0],
                                    r[1],
                                    r[2],
                                    self.typeTokenWidget.value(),
                                    self.algorithmWidget.displayValue(),
                                    self.alignCheck.isChecked()])

        else:
            pass

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
