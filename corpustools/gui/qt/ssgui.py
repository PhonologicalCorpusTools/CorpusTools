
from .imports import *

from collections import OrderedDict

from corpustools.symbolsim.string_similarity import string_similarity
from corpustools.symbolsim.io import read_pairs_file

from .widgets import RadioSelectWidget, FileWidget
from .windows import FunctionWorker, FunctionDialog

class SSWorker(FunctionWorker):
    def run(self):
        kwargs = self.kwargs
        #try:
        #    self.results = string_similarity(**kwargs)
        #except Exception as e:
        #    self.errorEncountered.emit(e)
        #    return
        self.results = string_similarity(**kwargs)
        if self.stopped:
            return
        self.dataReady.emit(self.results)

class SSDialog(FunctionDialog):
    header = ['Word 1',
                'Word 2',
                'String similarity',
                'String type',
                'Type or token',
                'Algorithm type']

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
                'References'
                'Khorsi, A. 2012. On Morphological Relatedness. Natural Language Engineering, 1-19.']

    name = 'string similarity'

    def __init__(self, parent, corpus, showToolTips):
        FunctionDialog.__init__(self, parent, SSWorker())

        self.corpus = corpus
        self.showToolTips = showToolTips

        if not self.corpus.has_transcription:
            layout.addWidget(QLabel('Corpus does not have transcription, so not all options are available.'))

        sslayout = QHBoxLayout()

        algEnabled = {'Khorsi':True,
                    'Edit distance':True,
                    'Phonological edit distance':self.corpus.has_transcription}
        self.algorithmWidget = RadioSelectWidget('String similarity algorithm',
                                            OrderedDict([('Khorsi','khorsi'),
                                            ('Edit distance','edit_distance'),
                                            ('Phonological edit distance','phono_edit_distance')]),
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
        self.twoWordRadio = QRadioButton('Compare a single pair of words to each other')
        self.twoWordRadio.clicked.connect(self.twoWordsSelected)
        self.wordOneEdit = QLineEdit()
        self.wordOneEdit.textChanged.connect(self.twoWordRadio.click)
        self.wordTwoEdit = QLineEdit()
        self.wordTwoEdit.textChanged.connect(self.twoWordRadio.click)
        self.fileRadio = QRadioButton('Compare a list of pairs of words')
        self.fileRadio.clicked.connect(self.fileSelected)
        self.fileWidget = FileWidget('Select a word pairs file', 'Text file (*.txt *.csv)')
        self.fileWidget.textChanged.connect(self.fileRadio.click)

        vbox.addRow(self.oneWordRadio)
        vbox.addRow(self.oneWordEdit)
        vbox.addRow(self.twoWordRadio)
        vbox.addRow('Word 1:',self.wordOneEdit)
        vbox.addRow('Word 2:',self.wordTwoEdit)
        vbox.addRow(self.fileRadio)
        vbox.addRow(self.fileWidget)

        compFrame.setLayout(vbox)

        sslayout.addWidget(compFrame)

        optionFrame = QGroupBox('Options')

        optionLayout = QVBoxLayout()

        self.typeTokenWidget = RadioSelectWidget('Type or token',
                                            {'Count types':'type',
                                            'Count tokens':'token'})

        optionLayout.addWidget(self.typeTokenWidget)
        self.tierWidget = QComboBox()
        self.tierWidget.addItem('spelling')
        if self.corpus.has_transcription:
            self.tierWidget.addItem('transcription')
        for t in self.corpus.tiers:
            self.tierWidget.addItem(t)

        tierFrame = QGroupBox('Tier')

        box = QVBoxLayout()
        box.addWidget(self.tierWidget)
        tierFrame.setLayout(box)

        optionLayout.addWidget(tierFrame)

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
            tierFrame.setToolTip(("<FONT COLOR=black>"
            'Select whether to calculate similarity'
                                ' on the spelling of a word (perhaps more useful for morphological purposes)'
                                ' or transcription of a word (perhaps more useful for phonological purposes).'
            "</FONT>"))
            threshFrame.setToolTip(("<FONT COLOR=black>"
            'Select the range of similarity'
                                ' scores for the algorithm to filter out.  For example, a minimum'
                                ' of -10 for Khorsi or a maximum of 8 for edit distance will likely'
                                ' filter out words that are highly different from each other.'
            "</FONT>"))


    def oneWordSelected(self):
        self.compType = 'one'

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

        max_rel = None
        if self.maxEdit.text() != '':
            try:
                max_rel = float(self.maxEdit.text())
            except ValueError:
                pass
        kwargs = {'corpus':self.corpus,
                'algorithm': self.algorithmWidget.value(),
                'sequence_type':self.tierWidget.currentText(),
                'count_what': self.typeTokenWidget.value(),
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
                word = self.corpus.find(text)
            except KeyError:
                if strType == 'spelling':
                    word = Word(spelling = text)
                else:
                    reply = QMessageBox.critical(self,
                        "Invalid information", "'{}' was not found in corpus.".format(text))
                    return
            kwargs['query'] = word.spelling
        elif self.compType == 'two':
            textOne = self.wordOneEdit.text()
            textTwo = self.wordTwoEdit.text()
            if not textOne or not textTwo:
                reply = QMessageBox.critical(self,
                        "Missing information", "Please specify both words.")
                return
            try:
                wordOne = self.corpus.find(textOne)
            except KeyError:
                from corpustools.corpus.classes import Word
                if strType == 'spelling':
                    wordOne = Word(spelling = textOne)
                else:
                    reply = QMessageBox.critical(self,
                        "Invalid information", "'{}' was not found in corpus.".format(textOne))
                    return
            try:
                wordTwo = self.corpus.find(textTwo)
            except KeyError:
                if strType == 'spelling':
                    wordTwo = Word(spelling = textTwo)
                else:
                    reply = QMessageBox.critical(self,
                        "Invalid information", "'{}' was not found in corpus.".format(textTwo))
                    return

            kwargs['query'] = (wordOne.spelling,wordTwo.spelling)
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
        for result in results:
            w1, w2, similarity = result
            if not isinstance(w1,str):
                w1 = w1.spelling
            if not isinstance(w2,str):
                w2 = w2.spelling
            if self.algorithmWidget.value() != 'khorsi':
                typetoken = 'N/A'
            else:
                typetoken = self.typeTokenWidget.value()
            self.results.append([w1, w2, similarity,
                        self.tierWidget.currentText(), typetoken,
                        self.algorithmWidget.value()])

    def khorsiSelected(self):
        self.stringTypeWidget.enable()
        self.typeTokenWidget.enable()

    def editDistSelected(self):
        self.stringTypeWidget.enable()
        self.typeTokenWidget.disable()

    def phonoEditDistSelected(self):
        self.stringTypeWidget.disable()
        self.typeTokenWidget.disable()
