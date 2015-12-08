import os
from collections import OrderedDict

from .imports import *
from corpustools.phonoprob.phonotactic_probability import (phonotactic_probability,
                                                    phonotactic_probability_all_words)
from corpustools.neighdens.io import load_words_neighden
from corpustools.corpus.classes import Attribute
from corpustools.exceptions import PCTError, PCTPythonError
from .windows import FunctionWorker, FunctionDialog
from .widgets import (RadioSelectWidget, FileWidget, TierWidget, RestrictedContextWidget)
from .corpusgui import AddWordDialog
from corpustools.contextmanagers import (CanonicalVariantContext,
                                        MostFrequentVariantContext)


class PPWorker(FunctionWorker):
    def run(self):
        time.sleep(0.1)
        kwargs = self.kwargs
        self.results = []
        context = kwargs.pop('context')
        if context == RestrictedContextWidget.canonical_value:
            cm = CanonicalVariantContext
        elif context == RestrictedContextWidget.frequent_value:
            cm = MostFrequentVariantContext
        corpus = kwargs['corpusModel'].corpus
        st = kwargs['sequence_type']
        tt = kwargs['type_token']
        att = kwargs.get('attribute', None)
        with cm(corpus, st, tt, att) as c:
            try:
                if 'query' in kwargs:
                    for q in kwargs['query']:
                        res = phonotactic_probability(c, q,
                                            algorithm = kwargs['algorithm'],
                                            probability_type = kwargs['probability_type'],
                                            stop_check = kwargs['stop_check'],
                                            call_back = kwargs['call_back'])
                        if self.stopped:
                            break
                        self.results.append([q,res])
                else:
                    end = kwargs['corpusModel'].beginAddColumn(att)
                    phonotactic_probability_all_words(c,
                                            algorithm = kwargs['algorithm'],
                                            probability_type = kwargs['probability_type'],
                                            #num_cores = kwargs['num_cores'],
                                            stop_check = kwargs['stop_check'],
                                            call_back = kwargs['call_back'])
                    end = kwargs['corpusModel'].endAddColumn(end)
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

class PPDialog(FunctionDialog):
    header = ['Corpus',
                'Word',
                'Algorithm',
                'Probability type',
                'Transcription tier',
                'Frequency type',
                'Pronunciation variants',
                'Phonotactic probability']

    _about = [('This function calculates the phonotactic probability '
                    'of a word based on positional probabilities of single '
                    'segments and biphones derived from a corpus.'),
                    '',
                    'Coded by Michael McAuliffe',
                    '',
                    'References',
                    ('Vitevitch, Michael S. & Paul A. Luce. 2004.'
                    ' A Web-based interface to calculate phonotactic'
                    ' probability for words and nonwords in English.'
                    ' Behavior Research Methods, Instruments, & Computers 36 (3), 481-487')
                    ]

    name = 'phonotactic probability'

    def __init__(self, parent, settings, corpusModel, inventory, showToolTips):
        FunctionDialog.__init__(self, parent, settings, PPWorker())

        self.corpusModel = corpusModel
        self.inventory = inventory
        self.showToolTips = showToolTips

        pplayout = QHBoxLayout()

        algEnabled = {'Vitevitch && Luce':True}
        self.algorithmWidget = RadioSelectWidget('Phonotactic probability algorithm',
                                            OrderedDict([
                                            ('Vitevitch && Luce','vitevitch'),
                                            ]),
                                            {'Vitevitch && Luce':self.vitevitchSelected,
                                            },
                                            algEnabled)

        pplayout.addWidget(self.algorithmWidget)

        queryFrame = QGroupBox('Query')

        vbox = QFormLayout()
        self.compType = None
        self.oneWordRadio = QRadioButton('Calculate for one word')
        self.oneWordRadio.clicked.connect(self.oneWordSelected)
        self.oneWordEdit = QLineEdit()
        self.oneWordEdit.textChanged.connect(self.oneWordRadio.click)

        self.oneNonwordRadio = QRadioButton('Calculate for a word/nonword not in the corpus')
        self.oneNonwordRadio.clicked.connect(self.oneNonwordSelected)
        self.oneNonwordLabel = QLabel('None created')
        self.oneNonword = None
        self.oneNonwordButton = QPushButton('Create word/nonword')
        self.oneNonwordButton.clicked.connect(self.createNonword)

        self.fileRadio = QRadioButton('Calculate for list of words')
        self.fileRadio.clicked.connect(self.fileSelected)
        self.fileWidget = FileWidget('Select a file', 'Text file (*.txt *.csv)')
        self.fileWidget.textChanged.connect(self.fileRadio.click)

        self.allwordsRadio = QRadioButton('Calculate for all words in the corpus')
        self.allwordsRadio.clicked.connect(self.allwordsSelected)
        self.columnEdit = QLineEdit()
        self.columnEdit.setText('Phonotactic probability')
        self.columnEdit.textChanged.connect(self.allwordsRadio.click)


        vbox.addRow(self.oneWordRadio)
        vbox.addRow(self.oneWordEdit)
        vbox.addRow(self.oneNonwordRadio)
        vbox.addRow(self.oneNonwordLabel,self.oneNonwordButton)
        vbox.addRow(self.fileRadio)
        vbox.addRow(self.fileWidget)
        vbox.addRow(self.allwordsRadio)
        vbox.addRow(QLabel('Column name:'),self.columnEdit)

        queryFrame.setLayout(vbox)

        pplayout.addWidget(queryFrame)
        optionFrame = QGroupBox('Options')

        optionLayout = QVBoxLayout()

        self.tierWidget = TierWidget(self.corpusModel.corpus,include_spelling=False)

        optionLayout.addWidget(self.tierWidget)

        self.typeTokenWidget = RadioSelectWidget('Type or token',
                                            OrderedDict([('Count types','type'),
                                            ('Count tokens','token')]))
        actions = None
        self.variantsWidget = RestrictedContextWidget(self.corpusModel.corpus, actions)

        optionLayout.addWidget(self.variantsWidget)

        optionLayout.addWidget(self.typeTokenWidget)

        self.probabilityTypeWidget = RadioSelectWidget('Probability type',
                                            OrderedDict([
                                            ('Biphone','bigram'),
                                            ('Single-phone','unigram')]))

        optionLayout.addWidget(self.probabilityTypeWidget)

        optionFrame.setLayout(optionLayout)

        pplayout.addWidget(optionFrame)

        ppFrame = QFrame()
        ppFrame.setLayout(pplayout)

        self.layout().insertWidget(0,ppFrame)

        self.algorithmWidget.initialClick()
        self.algorithmWidget.initialClick()
        if self.showToolTips:

            self.tierWidget.setToolTip(("<FONT COLOR=black>"
            'Select whether to calculate neighborhood density'
                                ' on the spelling of a word (perhaps more useful for morphological purposes)'
                                ' or any transcription tier of a word (perhaps more useful for phonological purposes),'
                                ' in the corpus.'
            "</FONT>"))

    def createNonword(self):
        dialog = AddWordDialog(self, self.corpusModel.corpus, self.inventory)
        if dialog.exec_():
            self.oneNonword = dialog.word
            self.oneNonwordLabel.setText('{} ({})'.format(str(self.oneNonword),
                                                          str(self.oneNonword.transcription)))
            self.oneNonwordRadio.click()

    def oneWordSelected(self):
        self.compType = 'one'

    def oneNonwordSelected(self):
        self.compType = 'nonword'

    def fileSelected(self):
        self.compType = 'file'

    def allwordsSelected(self):
        self.compType = 'all'

    def generateKwargs(self):
        kwargs = {'corpusModel':self.corpusModel,
                'algorithm': self.algorithmWidget.value(),
                'context': self.variantsWidget.value(),
                'sequence_type':self.tierWidget.value(),
                'type_token':self.typeTokenWidget.value(),
                'probability_type':self.probabilityTypeWidget.value()}

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
                w = self.corpusModel.corpus.find(text)
            except KeyError:
                reply = QMessageBox.critical(self,
                        "Invalid information", "The spelling specified does match any words in the corpus.")
                return
            kwargs['query'] = [w]
        elif self.compType == 'nonword':
            if self.oneNonword is None:
                reply = QMessageBox.critical(self,
                        "Missing information", "Please create a word/nonword.")
                return
            if not getattr(self.oneNonword,kwargs['sequence_type']):
                reply = QMessageBox.critical(self,
                        "Missing information", "Please recreate the word/nonword with '{}' specified.".format(self.tierWidget.displayValue()))
                return
            kwargs['query'] = [self.oneNonword]
        elif self.compType == 'file':
            path = self.fileWidget.value()
            if not path:
                reply = QMessageBox.critical(self,
                        "Missing information", "Please enter a file path.")
                return
            if not os.path.exists(path):
                reply = QMessageBox.critical(self,
                        "Invalid information", "The file path entered was not found.")
                return
            kwargs['query'] = list()
            text = load_words_neighden(path)
            for t in text:
                if isinstance(t,str):
                    try:
                        w = self.corpusModel.corpus.find(t)
                    except KeyError:
                        reply = QMessageBox.critical(self,
                                "Invalid information", "The spelling '{}' was not found in the corpus.".format(t))
                        return
                kwargs['query'].append(w)
        elif self.compType == 'all':
            column = self.columnEdit.text()
            if column == '':
                reply = QMessageBox.critical(self,
                        "Missing information", "Please enter a column name.")
                return
            colName = column.lower().replace(' ','_')
            attribute = Attribute(colName,'numeric',column)
            if column in self.corpusModel.columns:

                msgBox = QMessageBox(QMessageBox.Warning, "Duplicate columns",
                        "'{}' is already the name of a column.  Overwrite?".format(column), QMessageBox.NoButton, self)
                msgBox.addButton("Overwrite", QMessageBox.AcceptRole)
                msgBox.addButton("Cancel", QMessageBox.RejectRole)
                if msgBox.exec_() != QMessageBox.AcceptRole:
                    return
            kwargs['attribute'] = attribute

        return kwargs

    def setResults(self, results):
        self.results = []
        for result in results:
            w, pp = result
            self.results.append([self.corpusModel.corpus.name,str(w),
                        self.algorithmWidget.displayValue().replace('&&','&'),
                        self.probabilityTypeWidget.displayValue(),
                        self.tierWidget.displayValue(),
                        self.typeTokenWidget.value().title(),
                        self.variantsWidget.value().title(),
                        pp])

    def vitevitchSelected(self):
        self.probabilityTypeWidget.enable()
        self.typeTokenWidget.enable()
