
from .imports import *

from collections import OrderedDict

from corpustools.symbolsim.string_similarity import string_similarity
from corpustools.symbolsim.io import read_pairs_file
from .widgets import RadioSelectWidget, FileWidget

from .windows import FunctionWorker

class SSWorker(FunctionWorker):
    def run(self):
        kwargs = self.kwargs
        self.results = string_similarity(kwargs['corpus'], kwargs['query'],
                                        kwargs['relator_type'],
                                        string_type = kwargs['string_type'],
                                        tier_name = kwargs['tier_name'],
                                        count_what = kwargs['count_what'],
                                        min_rel = kwargs['min_rel'],
                                        max_rel = kwargs['max_rel'],
                                        stop_check = kwargs['stop_check'],
                                        call_back = kwargs['call_back'])
        if self.stopped:
            return
        self.dataReady.emit(self.results)

class SSDialog(QDialog):
    header = ['Word 1',
                'Word 2',
                'Result',
                'String type',
                'Type or token',
                'Algorithm type']

    ABOUT = [('This function calculates the similarity between words in the corpus,'
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

    def __init__(self, parent, corpus, showToolTips):
        QDialog.__init__(self, parent)

        self.corpus = corpus
        self.showToolTips = showToolTips
        layout = QVBoxLayout()
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

        stringEnabled = {'Compare spelling':True,
                        'Compare transcription': self.corpus.has_transcription}
        self.stringTypeWidget = RadioSelectWidget('String type',
                                    OrderedDict([('Compare spelling', 'spelling'),
                                    ('Compare transcription','transcription')]),
                                    enabled = stringEnabled)

        optionLayout.addWidget(self.stringTypeWidget)

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

        layout.addWidget(ssFrame)

        self.newTableButton = QPushButton('Calculate string similarity\n(start new results table)')
        self.newTableButton.setDefault(True)
        self.oldTableButton = QPushButton('Calculate string similarity\n(add to current results table)')
        self.cancelButton = QPushButton('Cancel')
        self.aboutButton = QPushButton('About this function...')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.newTableButton)
        acLayout.addWidget(self.oldTableButton)
        acLayout.addWidget(self.cancelButton)
        acLayout.addWidget(self.aboutButton)
        self.newTableButton.clicked.connect(self.newTable)
        self.oldTableButton.clicked.connect(self.oldTable)
        self.aboutButton.clicked.connect(self.about)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

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
            self.stringTypeWidget.setToolTip(("<FONT COLOR=black>"
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

        self.setLayout(layout)

        self.setWindowTitle('String similarity')

        self.thread = SSWorker()

        self.progressDialog = QProgressDialog('Calculating string similarity...','Cancel',0,100, self)
        self.progressDialog.setWindowTitle('Calculating string similarity')
        self.progressDialog.setAutoClose(False)
        self.progressDialog.setAutoReset(False)
        self.progressDialog.canceled.connect(self.thread.stop)
        self.thread.updateProgress.connect(self.updateProgress)
        self.thread.updateProgressText.connect(self.updateProgressText)
        self.thread.dataReady.connect(self.setResults)
        self.thread.dataReady.connect(self.progressDialog.accept)

    def updateProgressText(self, text):
        self.progressDialog.setLabelText(text)
        self.progressDialog.reset()

    def updateProgress(self,progress):
        self.progressDialog.setValue(progress)
        self.progressDialog.repaint()

    def oneWordSelected(self):
        self.compType = 'one'

    def twoWordsSelected(self):
        self.compType = 'two'

    def fileSelected(self):
        self.compType = 'file'

    def calcSS(self):
        from corpustools.corpus.classes import Word
        if self.minEdit.text() == '':
            min_rel = None
        else:
            min_rel = float(self.minEdit.text())
        if self.maxEdit.text() == '':
            max_rel = None
        else:
            max_rel = float(self.maxEdit.text())
        #Error checking
        relType = self.algorithmWidget.value()
        if relType is None:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a string similarity algorithm.")
            return
        typeToken = self.typeTokenWidget.value()
        if typeToken is None and relType == 'khorsi':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify type or token frequency.")
            return
        strType = self.stringTypeWidget.value()
        if strType is None and relType != 'phono_edit_distance':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a string type.")
            return
        kwargs = {'corpus':self.corpus,
                'relator_type': relType,
                'string_type':strType,
                'tier_name':self.stringTypeWidget.value(),
                'count_what':typeToken,
                'min_rel':min_rel,
                'max_rel':max_rel}
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
                from corpustools.corpus.classes import Word
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
                        self.stringTypeWidget.value(), typetoken,
                        self.algorithmWidget.value()])


    def newTable(self):
        self.update = False
        self.calcSS()

    def oldTable(self):
        self.update = True
        self.calcSS()

    def about(self):
        reply = QMessageBox.information(self,
                "About string similarity", '\n'.join(self.ABOUT))

    def khorsiSelected(self):
        self.stringTypeWidget.enable()
        self.typeTokenWidget.enable()

    def editDistSelected(self):
        self.stringTypeWidget.enable()
        self.typeTokenWidget.disable()

    def phonoEditDistSelected(self):
        self.stringTypeWidget.disable()
        self.typeTokenWidget.disable()
