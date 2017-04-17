
from .imports import *

from collections import OrderedDict

from corpustools.symbolsim.string_similarity import string_similarity
from corpustools.symbolsim.io import read_pairs_file
from corpustools.exceptions import PCTError, PCTPythonError

from .widgets import (RadioSelectWidget, FileWidget, TierWidget,
                        RestrictedContextWidget)
from .windows import FunctionWorker, FunctionDialog
from .corpusgui import AddWordDialog

from corpustools.contextmanagers import (CanonicalVariantContext,
                                        MostFrequentVariantContext,
                                        SeparatedTokensVariantContext,
                                        WeightedVariantContext)

class SSWorker(FunctionWorker):
    def run(self):
        time.sleep(0.1)
        kwargs = self.kwargs
        context = kwargs.pop('context')
        if context == RestrictedContextWidget.canonical_value:
            cm = CanonicalVariantContext
        elif context == RestrictedContextWidget.frequent_value:
            cm = MostFrequentVariantContext
        corpus = kwargs.pop('corpusModel').corpus
        st = kwargs.pop('sequence_type')
        tt = kwargs.pop('type_token')
        ft = kwargs.pop('frequency_cutoff')
        with cm(corpus, st, tt, frequency_threshold = ft) as c:
            try:
                query = kwargs.pop('query')
                alg = kwargs.pop('algorithm')
                self.results = string_similarity(c,
                                            query, alg,**kwargs)
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

class SSDialog(FunctionDialog):
    header = ['Corpus',
                'First word',
                'Second word',
                'Algorithm',
                'String type',
                'Frequency type',
                'Pronunciation variants',
                'Minimum word frequency',
                'Result']

    _about = [('This function calculates the similarity between words in the corpus,'
                ' based on either their spelling or their transcription. Similarity '
                'is a function of the longest common shared sequences of graphemes '
                'or phonemes (weighted by their frequency of occurrence in the corpus), '
                'subtracting out the non-shared graphemes or phonemes. The spelling '
                'version was originally proposed as a measure of morphological relatedness,'
                ' but is more accurately described as simply a measure of string similarity.'),
                '',
                'Coded by Michael Fry',
                '',
                'References',
                ('Khorsi, A. 2012. On Morphological Relatedness. '
                'Natural Language Engineering, 1-19.'),
                ('Luce, Paul A. & David B. Pisoni. 1998. '
                'Recognizing spoken words: The neighborhood activation model. '
                'Ear Hear 19.1-36.'),
                ('Allen, Blake & Michael Becker. 2014. '
                'Learning alternations from surface forms with sublexical phonology. '
                'Ms. University of British Columbia and Stony Brook University. '
                'See also http://sublexical.phonologist.org/')]

    name = 'string similarity'

    def __init__(self, parent, settings, corpusModel, showToolTips):
        FunctionDialog.__init__(self, parent, settings, SSWorker())

        self.corpusModel = corpusModel
        self.showToolTips = showToolTips

        if not self.corpusModel.corpus.has_transcription:
            self.layout().addWidget(QLabel('Corpus does not have transcription, so not all options are available.'))
        elif self.corpusModel.corpus.specifier is None:
            self.layout().addWidget(QLabel('Corpus does not have a feature system loaded, so not all options are available.'))

        sslayout = QHBoxLayout()

        algEnabled = {'Khorsi':True,
                    'Edit distance':True,
                    'Phonological edit distance':
                        (self.corpusModel.corpus.has_transcription and
                            self.corpusModel.corpus.specifier is not None)}
        self.algorithmWidget = RadioSelectWidget('String similarity algorithm',
                                            OrderedDict([('Edit distance','edit_distance'),
                                            ('Phonological edit distance','phono_edit_distance'),
                                            ('Khorsi','khorsi')]),
                                            {'Khorsi':self.khorsiSelected,
                                            'Edit distance':self.editDistSelected,
                                            'Phonological edit distance':self.phonoEditDistSelected},
                                            algEnabled)


        sslayout.addWidget(self.algorithmWidget)

        compFrame = QGroupBox('Comparison type')

        vbox = QFormLayout()
        self.compType = None
        self.oneWordRadio = QRadioButton('Compare one word to entire corpus')
        self.oneWordRadio.clicked.connect(self.oneWordSelected)
        self.oneWordEdit = QLineEdit()
        self.oneWordEdit.textChanged.connect(self.oneWordRadio.click)

        self.oneNonwordRadio = QRadioButton('Calculate for a word/nonword not in the corpus')
        self.oneNonwordRadio.clicked.connect(self.oneNonwordSelected)
        self.oneNonwordLabel = QLabel('None created')
        self.oneNonword = None
        self.oneNonwordButton = QPushButton('Create word/nonword')
        self.oneNonwordButton.clicked.connect(self.createOneNonword)

        self.twoWordRadio = QRadioButton('Compare a single pair of words to each other')
        self.twoWordRadio.clicked.connect(self.twoWordsSelected)
        self.wordOneEdit = QLineEdit()
        self.wordOneEdit.textChanged.connect(self.twoWordRadio.click)
        self.nonwordOneLabel = QLabel('None created')
        self.nonwordOne = None
        self.nonwordOneButton = QPushButton('Create word/nonword')
        self.nonwordOneButton.clicked.connect(self.createNonwordOne)
        self.wordTwoEdit = QLineEdit()
        self.wordTwoEdit.textChanged.connect(self.twoWordRadio.click)
        self.nonwordTwoLabel = QLabel('None created')
        self.nonwordTwo = None
        self.nonwordTwoButton = QPushButton('Create word/nonword')
        self.nonwordTwoButton.clicked.connect(self.createNonwordTwo)

        self.fileRadio = QRadioButton('Compare a list of pairs of words')
        self.fileRadio.clicked.connect(self.fileSelected)
        self.fileWidget = FileWidget('Select a word pairs file', 'Text file (*.txt *.csv)')
        self.fileWidget.textChanged.connect(self.fileRadio.click)

        self.clearButton = QPushButton('Clear all created words/nonwords')
        self.clearButton.clicked.connect(self.clearCreated)

        vbox.addRow(self.oneWordRadio)
        vbox.addRow(self.oneWordEdit)
        vbox.addRow(self.oneNonwordRadio)
        vbox.addRow(self.oneNonwordLabel,self.oneNonwordButton)

        vbox.addRow(self.twoWordRadio)
        vbox.addRow('Word 1 spelling (if in corpus):',self.wordOneEdit)
        vbox.addRow(self.nonwordOneLabel,self.nonwordOneButton)
        vbox.addRow('Word 2 spelling (if in corpus):',self.wordTwoEdit)
        vbox.addRow(self.nonwordTwoLabel,self.nonwordTwoButton)
        vbox.addRow(self.fileRadio)
        vbox.addRow(self.fileWidget)
        vbox.addRow(self.clearButton)

        compFrame.setLayout(vbox)

        sslayout.addWidget(compFrame)

        optionFrame = QGroupBox('Options')

        optionLayout = QVBoxLayout()

        self.tierWidget = TierWidget(self.corpusModel.corpus,include_spelling=True)

        optionLayout.addWidget(self.tierWidget)

        self.typeTokenWidget = RadioSelectWidget('Type or token',
                                            OrderedDict([('Count types','type'),
                                            ('Count tokens','token')]))
        actions = None
        self.variantsWidget = RestrictedContextWidget(self.corpusModel.corpus, actions)

        optionLayout.addWidget(self.variantsWidget)

        optionLayout.addWidget(self.typeTokenWidget)
    
        ##----------------------
        minFreqFrame = QGroupBox('Minimum frequency')
        box = QFormLayout()
        self.minFreqEdit = QLineEdit()
        box.addRow('Minimum word frequency:',self.minFreqEdit)

        minFreqFrame.setLayout(box)

        optionLayout.addWidget(minFreqFrame)
        ##----------------------
        
        threshFrame = QGroupBox('Return only results between...')

        self.minEdit = QLineEdit()
        self.maxEdit = QLineEdit()

        vbox = QFormLayout()
        vbox.addRow('Minimum:',self.minEdit)
        vbox.addRow('Maximum:',self.maxEdit)

        threshFrame.setLayout(vbox)

        optionLayout.addWidget(threshFrame)

        optionFrame.setLayout(optionLayout)

        sslayout.addWidget(optionFrame)

        ssFrame = QFrame()
        ssFrame.setLayout(sslayout)

        self.layout().insertWidget(0,ssFrame)

        self.algorithmWidget.initialClick()
        if self.showToolTips:
            self.algorithmWidget.setToolTip(("<FONT COLOR=black>"
            'Select which algorithm'
                                        ' to use for calculating similarity. For Khorsi,'
                                        ' a larger number means strings are more similar.'
                                        ' For edit distance, a smaller number means strings'
                                        ' are more similar (with 0 being identical). For more'
                                        ' information, click on \'About this function\'.'
            "</FONT>"))
            compFrame.setToolTip(("<FONT COLOR=black>"
            'Select how you would'
                                ' like to use string similarity. You can 1) calculate the'
                                ' similarity of one word to all other words in the corpus,'
                                ' 2) calculate the similarity of 2 words to each other, 3)'
                                ' calculate the similarity of a list of pairs of words in a text file.'
            "</FONT>"))
            self.typeTokenWidget.setToolTip(("<FONT COLOR=black>"
            'Select which type of frequency to use'
                                    ' for calculating similarity (only relevant for Khorsi). Type '
                                    'frequency means each letter is counted once per word. Token '
                                    'frequency means each letter is counted as many times as its '
                                    'word\'s frequency in the corpus.'
            "</FONT>"))
            self.tierWidget.setToolTip(("<FONT COLOR=black>"
            'Select whether to calculate similarity'
                                ' on the spelling of a word (perhaps more useful for morphological purposes)'
                                ' or any transcription tier of a word (perhaps more useful for phonological purposes),'
                                ' in the corpus.'
            "</FONT>"))
            threshFrame.setToolTip(("<FONT COLOR=black>"
            'Select the range of similarity'
                                ' scores for the algorithm to filter out.  For example, a minimum'
                                ' of -10 for Khorsi or a maximum of 8 for edit distance will likely'
                                ' filter out words that are highly different from each other.'
            "</FONT>"))

    def clearCreated(self):
        self.oneNonWord = None
        self.nonwordOne = None
        self.nonwordTwo = None
        self.oneNonwordLabel.setText('None created')
        self.nonwordOneLabel.setText('None created')
        self.nonwordTwoLabel.setText('None created')
        self.wordOneEdit.setEnabled(True)
        self.wordTwoEdit.setEnabled(True)


    def createOneNonword(self):
        dialog = AddWordDialog(self, self.corpusModel.corpus)
        if dialog.exec_():
            self.oneNonword = dialog.word
            self.oneNonwordLabel.setText('{} ({})'.format(str(self.oneNonword),
                                                          str(self.oneNonword.transcription)))
            self.oneNonwordRadio.click()

    def createNonwordOne(self):
        dialog = AddWordDialog(self, self.corpusModel.corpus)
        if dialog.exec_():
            self.nonwordOne = dialog.word
            self.nonwordOneLabel.setText('{} ({})'.format(str(self.nonwordOne),
                                                          str(self.nonwordOne.transcription)))
            self.twoWordRadio.click()
            self.wordOneEdit.setEnabled(False)

    def createNonwordTwo(self):
        dialog = AddWordDialog(self, self.corpusModel.corpus)
        if dialog.exec_():
            self.nonwordTwo = dialog.word
            self.nonwordTwoLabel.setText('{} ({})'.format(str(self.nonwordTwo),
                                                          str(self.nonwordTwo.transcription)))
            self.twoWordRadio.click()
            self.wordTwoEdit.setEnabled(False)


    def oneWordSelected(self):
        self.compType = 'one'

    def oneNonwordSelected(self):
        self.compType = 'nonword'

    def twoWordsSelected(self):
        self.compType = 'two'

    def fileSelected(self):
        self.compType = 'file'

    def generateKwargs(self):
        from corpustools.corpus.classes import Word
        min_rel = None
        if self.minEdit.text() != '':
            try:
                min_rel = float(self.minEdit.text())
            except ValueError:
                pass
        ##------------------
        try:
            frequency_cutoff = float(self.minFreqEdit.text())
        except ValueError:
            frequency_cutoff = 0.0
        ##-------------------
        max_rel = None
        if self.maxEdit.text() != '':
            try:
                max_rel = float(self.maxEdit.text())
            except ValueError:
                pass
        kwargs = {'corpusModel':self.corpusModel,
                'context': self.variantsWidget.value(),
                'algorithm': self.algorithmWidget.value(),
                'sequence_type':self.tierWidget.value(),
                'type_token': self.typeTokenWidget.value(),
                'frequency_cutoff':frequency_cutoff,
                'min_rel':min_rel,
                'max_rel':max_rel}
        #Error checking
        if self.compType is None:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a comparison type.")
            return
        elif self.compType == 'one':
            text = self.oneWordEdit.text()
            if not text:
                reply = QMessageBox.critical(self,
                        "Missing information", "Please specify a word.")
                return
            try:
                word = self.corpusModel.corpus.find(text)
            except KeyError:
                reply = QMessageBox.critical(self,
                    "Invalid information", "'{}' was not found in corpus.".format(text))
                return
            kwargs['query'] = word
        elif self.compType == 'nonword':

            if self.oneNonword is None:
                reply = QMessageBox.critical(self,
                        "Missing information", "Please create a word/nonword.")
                return
            if not getattr(self.oneNonword,kwargs['sequence_type']):
                reply = QMessageBox.critical(self,
                        "Missing information", "Please recreate the word/nonword with '{}' specified.".format(self.tierWidget.displayValue()))
                return
            kwargs['query'] = self.oneNonword
        elif self.compType == 'two':
            textOne = self.wordOneEdit.text()
            textTwo = self.wordTwoEdit.text()
            if self.nonwordOne is not None:
                if not getattr(self.nonwordOne,kwargs['sequence_type']):
                    reply = QMessageBox.critical(self,
                            "Missing information", "Please recreate word/nonword 1 with '{}' specified.".format(self.tierWidget.displayValue()))
                    return
                wordone = self.nonwordOne
            elif textOne:
                try:
                    wordOne = self.corpusModel.corpus.find(textOne)
                except KeyError:
                    reply = QMessageBox.critical(self,
                        "Invalid information", "'{}' was not found in corpus.".format(textOne))
                    return
            elif not textOne:
                reply = QMessageBox.critical(self,
                            "Missing information", "Please specify either a spelling for word one or create a new word.")
                return

            if self.nonwordTwo is not None:
                if not getattr(self.nonwordTwo,kwargs['sequence_type']):
                    reply = QMessageBox.critical(self,
                            "Missing information", "Please recreate word/nonword 2 with '{}' specified.".format(self.tierWidget.displayValue()))
                    return
                wordTwo = self.nonwordTwo
            elif textTwo:
                try:
                    wordTwo = self.corpusModel.corpus.find(textTwo)
                except KeyError:
                    reply = QMessageBox.critical(self,
                        "Invalid information", "'{}' was not found in corpus.".format(textTwo))
                    return
            elif not textTwo:
                reply = QMessageBox.critical(self,
                            "Missing information", "Please specify either a spelling for word two or create a new word.")
                return

            kwargs['query'] = (wordOne,wordTwo)
        elif self.compType == 'file':
            pairs_path = self.fileWidget.value()
            if not pairs_path:
                reply = QMessageBox.critical(self,
                        "Missing information", "Please enter a file path.")
                return
            if not os.path.exists(pairs_path):
                reply = QMessageBox.critical(self,
                        "Invalid information", "The file path entered was not found.")
                return
            kwargs['query'] = read_pairs_file(pairs_path)
        return kwargs

    def setResults(self, results):
        self.results = list()
        try:
            frequency_cutoff = float(self.minFreqEdit.text())
        except ValueError:
            frequency_cutoff = 0.0
        for result in results:
            w1, w2, similarity = result
            if not isinstance(w1,str):
                w1 = w1.spelling
            if not isinstance(w2,str):
                w2 = w2.spelling
            if self.algorithmWidget.value() != 'khorsi':
                typetoken = 'N/A'
            else:
                typetoken = self.typeTokenWidget.value().title()
            self.results.append([self.corpusModel.corpus.name, w1, w2,
                        self.algorithmWidget.displayValue(),
                        self.tierWidget.displayValue(),
                        typetoken,
                        self.variantsWidget.value().title(), frequency_cutoff,
                         similarity ])

    def khorsiSelected(self):
        self.typeTokenWidget.enable()
        self.tierWidget.setSpellingEnabled(True)

    def editDistSelected(self):
        self.typeTokenWidget.disable()
        self.tierWidget.setSpellingEnabled(True)

    def phonoEditDistSelected(self):
        self.typeTokenWidget.disable()
        self.tierWidget.setSpellingEnabled(False)
