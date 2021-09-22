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
from corpustools import __version__

class PPWorker(FunctionWorker):
    def run(self):
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
        ft = kwargs['frequency_cutoff']
        log_count = kwargs['log_count']
        with cm(corpus, st, tt, attribute=att, frequency_threshold = ft, log_count=log_count) as c:
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
              'PCT ver.',
              'Word',
              'Analysis name',
              'Algorithm',
              'Probability type',
              'Transcription tier',
              'Frequency type',
              'Log-scaled frequency',
              'Pronunciation variants',
              'Minimum word frequency',
              'Result']

    _about = [('This function calculates the phonotactic probability '
                    'of a word based on positional probabilities of single '
                    'segments and biphones derived from a corpus.'),
                    '',
                    'References: ',
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
        self.oneWordRadio = QRadioButton('Calculate for one word in the corpus\n(Enter spelling)')
        self.oneWordRadio.clicked.connect(self.oneWordSelected)
        self.oneWordRadio.setAutoExclusive(True)
        self.oneWordEdit = QLineEdit()
        self.oneWordEdit.textChanged.connect(self.oneWordRadio.click)
        self.oneWordRadio.setChecked(True)
        self.oneWordRadio.click()

        self.oneNonwordRadio = QRadioButton('Calculate for a word/nonword not in the corpus\n(Enter transcription)')
        self.oneNonwordRadio.clicked.connect(self.oneNonwordSelected)
        self.oneNonwordRadio.setAutoExclusive(True)
        self.oneNonwordLabel = QLabel('None created')
        self.oneNonword = None
        self.oneNonwordButton = QPushButton('Create word/nonword')
        self.oneNonwordButton.clicked.connect(self.createNonword)


        self.fileRadio = QRadioButton('Calculate for list of words\n(Load text file containing spelling)')
        self.fileRadio.clicked.connect(self.fileSelected)
        self.fileRadio.setAutoExclusive(True)
        self.fileWidget = FileWidget('Select a file', 'Text file (*.txt *.csv)')
        self.fileWidget.textChanged.connect(self.fileRadio.click)

        self.allwordsRadio = QRadioButton('Calculate for all words in the corpus')
        self.allwordsRadio.clicked.connect(self.allwordsSelected)
        self.allwordsRadio.setAutoExclusive(True)
        self.columnEdit = QLineEdit()
        self.columnEdit.setText('Phonotactic probability')
        self.columnEdit.textChanged.connect(self.allwordsRadio.click)

        vbox.addRow(self.oneWordRadio)
        vbox.addRow(self.oneWordEdit)
        vbox.addRow(QHLine())   # add '------'
        vbox.addRow(self.oneNonwordRadio)
        vbox.addRow(self.oneNonwordLabel,self.oneNonwordButton)
        vbox.addRow(QHLine())   # add '------'
        vbox.addRow(self.fileRadio)
        vbox.addRow(self.fileWidget)
        vbox.addRow(QHLine())  # add '------'
        vbox.addRow(self.allwordsRadio)
        vbox.addRow(QLabel('Column name:'),self.columnEdit)
        note = QLabel(('(Selecting this option will add a new column containing the results to your corpus. '
                       'No results window will be displayed.)'))
        note.setWordWrap(True)
        vbox.addRow(note)

        queryFrame.setLayout(vbox)

        pplayout.addWidget(queryFrame)
        optionFrame = QGroupBox('Options')

        optionLayout = QVBoxLayout()

        self.useLogScale = QCheckBox('Use log-scaled word frequencies (token count only)')
        optionLayout.addWidget(self.useLogScale)
        self.useLogScale.setChecked(True)

        self.tierWidget = TierWidget(self.corpusModel.corpus,include_spelling=False)

        optionLayout.addWidget(self.tierWidget)

        self.typeTokenWidget = RadioSelectWidget('Type or token',
                                            OrderedDict([('Count types','type'),
                                            ('Count tokens','token')]))
        for widget in self.typeTokenWidget.widgets:
            if 'token' in widget.text():
                #we can only use log-scaling on token frequency
                widget.clicked.connect(lambda x: self.useLogScale.setEnabled(True))
            else:
                #if type frequency is selected, then disable to log-scale option
                widget.clicked.connect(lambda y: self.useLogScale.setEnabled(False))
        self.typeTokenWidget.widgets[1].click()
        #normally we do self.typeTokenWidget.initialClick()
        #but here we default to token, not type, because that's in the original algorithim by V&L

        actions = None
        self.variantsWidget = RestrictedContextWidget(self.corpusModel.corpus, actions)

        optionLayout.addWidget(self.variantsWidget)

        optionLayout.addWidget(self.typeTokenWidget)

        self.probabilityTypeWidget = RadioSelectWidget('Probability type',
                                            OrderedDict([
                                            ('Biphone','bigram'),
                                            ('Single-phone','unigram')]))

        optionLayout.addWidget(self.probabilityTypeWidget)
        
        ##----------------------
        #  minFreqFrame = QGroupBox('Minimum frequency')
        #  box = QFormLayout()
        #  self.minFreqEdit = QLineEdit()
        #  self.minFreqEdit.setValidator(QDoubleValidator(float('inf'), 0, 8))
        #  box.addRow('Minimum word frequency:',self.minFreqEdit)

        #  minFreqFrame.setLayout(box)

        #  optionLayout.addWidget(minFreqFrame)
        ##----------------------
        
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

            self.useLogScale.setToolTip(("<FONT COLOR=black>"
            'If checked, then the token frequency count will be log-scaled. This option does not apply to type'
            ' frequency.'
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
        ##------------------
        # try:
        #     frequency_cutoff = float(self.minFreqEdit.text())
        # except ValueError:
        #     frequency_cutoff = 0.0
        frequency_cutoff = 0.0
        ##-------------------
        
        kwargs = {'corpusModel':self.corpusModel,
                'algorithm': self.algorithmWidget.value(),
                'context': self.variantsWidget.value(),
                'sequence_type':self.tierWidget.value(),
                'type_token':self.typeTokenWidget.value(),
                'frequency_cutoff':frequency_cutoff,
                'probability_type':self.probabilityTypeWidget.value(),
                'log_count': self.useLogScale.isEnabled() and self.useLogScale.isChecked()}

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
            colName = column.replace(' ','_')
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
        try:
            frequency_cutoff = float(self.minFreqEdit.text())
        except (ValueError, AttributeError):
            frequency_cutoff = 0.0
        for result in results:
            w, pp = result
            self.results.append({'Corpus': self.corpusModel.corpus.name,
                                'PCT ver.': __version__,#self.corpusModel.corpus._version,
                                'Analysis name': self.name.capitalize(),
                                'Word': str(w),
                                'Algorithm': self.algorithmWidget.displayValue().replace('&&','&'),
                                'Probability type': self.probabilityTypeWidget.displayValue(),
                                'Transcription tier': self.tierWidget.displayValue(),
                                'Frequency type': self.typeTokenWidget.value().title(),
                                'Log-scaled frequency': 'Yes' if self.useLogScale.isChecked() else 'No',
                                'Pronunciation variants': self.variantsWidget.value().title(),
                                'Minimum word frequency': frequency_cutoff,
                                'Result': pp})

    def vitevitchSelected(self):
        self.probabilityTypeWidget.enable()
        self.typeTokenWidget.enable()
