import os

from .imports import *

from collections import OrderedDict

from corpustools.neighdens.neighborhood_density import (neighborhood_density,
                            neighborhood_density_all_words,
                            find_mutation_minpairs_all_words,
                            find_mutation_minpairs)
from corpustools.neighdens.io import load_words_neighden, print_neighden_results
from corpustools.corpus.classes import Attribute

from corpustools.exceptions import PCTError, PCTPythonError

from .windows import FunctionWorker, FunctionDialog
from .widgets import (RadioSelectWidget, FileWidget, SaveFileWidget, TierWidget,
                        RestrictedContextWidget)
from .corpusgui import AddWordDialog

from corpustools.contextmanagers import (CanonicalVariantContext,
                                        MostFrequentVariantContext,
                                        SeparatedTokensVariantContext,
                                        WeightedVariantContext)

class NDWorker(FunctionWorker):
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
        ft = kwargs['frequency_cutoff']
        with cm(corpus, st, tt, frequency_threshold = ft) as c:
            try:
                if 'query' in kwargs:
                    for q in kwargs['query']:
                        if kwargs['algorithm'] != 'substitution':
                            res = neighborhood_density(c, q,
                                                algorithm = kwargs['algorithm'],
                                                max_distance = kwargs['max_distance'],
                                                stop_check = kwargs['stop_check'],
                                                call_back = kwargs['call_back'])
                        else:
                            res = find_mutation_minpairs(c, q,
                                        stop_check = kwargs['stop_check'],
                                        call_back = kwargs['call_back'])
                        if 'output_filename' in kwargs and kwargs['output_filename'] is not None:
                            print_neighden_results(kwargs['output_filename'],res[1])
                        if self.stopped:
                            break
                        self.results.append([q,res[0]])
                else:
                    end = kwargs['corpusModel'].beginAddColumn(att)
                    if kwargs['algorithm'] != 'substitution':
                        neighborhood_density_all_words(c,
                                                algorithm = kwargs['algorithm'],
                                                max_distance = kwargs['max_distance'],
                                                num_cores = kwargs['num_cores'],
                                                call_back = kwargs['call_back'],
                                                stop_check = kwargs['stop_check']
                                                )
                    else:
                        find_mutation_minpairs_all_words(c,
                                                num_cores = kwargs['num_cores'],
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


class NDDialog(FunctionDialog):
    header = ['Corpus',
                'Word',
                'Algorithm',
                'Threshold',
                'String type',
                'Frequency type',
                'Pronunciation variants',
                'Minimum word frequency',
                'Neighborhood density']

    _about = [('This function calculates the neighborhood density (size)'
                    ' of a word. A neighborhood is the set of words sufficiently'
                    ' similar to the target word as defined using a distance metric.'
                    ' For information about the distance metrics, see "About this Function"'
                    ' in the string similarity analysis'),
                    '',
                    'Coded by Blake Allen and Michael Fry',
                    '',
                    'References',
                    ('Luce, Paul A. & David B. Pisoni. 1998. '
                    'Recognizing spoken words: The neighborhood activation model. '
                    'Ear Hear 19.1-36.')]

    name = 'neighborhood density'

    def __init__(self, parent, settings, corpusModel, showToolTips):
        FunctionDialog.__init__(self, parent, settings, NDWorker())

        self.corpusModel = corpusModel
        self.showToolTips = showToolTips

        if not self.corpusModel.corpus.has_transcription:
            self.layout().addWidget(QLabel('Corpus does not have transcription, so not all options are available.'))
        elif self.corpusModel.corpus.specifier is None:
            self.layout().addWidget(QLabel('Corpus does not have a feature system loaded, so not all options are available.'))
        ndlayout = QHBoxLayout()

        algEnabled = {'Khorsi':True,
                    'Edit distance':True,
                    'Substitution neighbors only':True,
                    'Phonological edit distance':
                        (self.corpusModel.corpus.has_transcription and
                            self.corpusModel.corpus.specifier is not None)}
        self.algorithmWidget = RadioSelectWidget('String similarity algorithm',
                                            OrderedDict([
                                            ('Edit distance','edit_distance'),
                                            ('Phonological edit distance','phono_edit_distance'),
                                            ('Khorsi','khorsi'),
                                            ('Substitution neighbors only','substitution'),]),
                                            {'Khorsi':self.khorsiSelected,
                                            'Edit distance':self.editDistSelected,
                                            'Substitution neighbors only':self.substitutionSelected,
                                            'Phonological edit distance':self.phonoEditDistSelected},
                                            algEnabled)


        ndlayout.addWidget(self.algorithmWidget)

        queryFrame = QGroupBox('Query')

        vbox = QFormLayout()
        self.compType = None
        self.oneWordRadio = QRadioButton('Calculate for one word in the corpus')
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
        self.columnEdit.setText('Neighborhood density')
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

        ndlayout.addWidget(queryFrame)
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

        threshFrame = QGroupBox('Max distance/min similarity')

        self.maxDistanceEdit = QLineEdit()
        self.maxDistanceEdit.setText('1')

        vbox = QFormLayout()
        vbox.addRow('Threshold:',self.maxDistanceEdit)

        threshFrame.setLayout(vbox)

        optionLayout.addWidget(threshFrame)
        
        ##----------------------
        minFreqFrame = QGroupBox('Minimum frequency')
        box = QFormLayout()
        self.minFreqEdit = QLineEdit()
        box.addRow('Minimum word frequency:',self.minFreqEdit)

        minFreqFrame.setLayout(box)

        optionLayout.addWidget(minFreqFrame)
        ##----------------------
        
        fileFrame = QGroupBox('Output list of neighbors to a file')

        self.saveFileWidget = SaveFileWidget('Select file location','Text files (*.txt)')

        vbox = QHBoxLayout()
        vbox.addWidget(self.saveFileWidget)

        fileFrame.setLayout(vbox)

        optionLayout.addWidget(fileFrame)

        optionFrame.setLayout(optionLayout)

        ndlayout.addWidget(optionFrame)

        ndFrame = QFrame()
        ndFrame.setLayout(ndlayout)

        self.layout().insertWidget(0,ndFrame)

        self.algorithmWidget.initialClick()
        if self.showToolTips:
            self.algorithmWidget.setToolTip(("<FONT COLOR=black>"
            'Select which algorithm'
                                        ' to use for calculating similarity. For Khorsi,'
                                        ' a larger number means strings are more similar.'
                                        ' For edit distance, a smaller number means strings'
                                        ' are more similar (with 0 being identical). For more'
                                        ' information, click on \'About this function\'.'
                                        ' \'Substitution neighbors\' will consider similar '
                                        ' only forms distinguished from the query by segment '
                                        ' substitution (not addition/deletion).'
            "</FONT>"))

            self.tierWidget.setToolTip(("<FONT COLOR=black>"
            'Select whether to calculate neighborhood density'
                                ' on the spelling of a word (perhaps more useful for morphological purposes)'
                                ' or any transcription tier of a word (perhaps more useful for phonological purposes),'
                                ' in the corpus.'
            "</FONT>"))

            threshFrame.setToolTip(("<FONT COLOR=black>"
            'These values set the minimum similarity'
                            ' or maximum distance needed in order for two words to be'
                            ' considered a neighbor.'
            "</FONT>"))

            self.typeTokenWidget.setToolTip(("<FONT COLOR=black>"
            'Select which type of frequency to use'
                                    ' for calculating distance (only relevant for Khorsi). Type'
                                    ' frequency means each letter is counted once per word. Token '
                                    'frequency means each letter is counted as many times as its '
                                    'words frequency in the corpus.'
            "</FONT>"))

            self.tierWidget.setToolTip(("<FONT COLOR=black>"
            'Select whether to calculate neighborhood density'
                                ' on the spelling of a word (perhaps more useful for morphological purposes)'
                                ' or any transcription tier of a word (perhaps more useful for phonological purposes),'
                                ' in the corpus.'
            "</FONT>"))

    def createNonword(self):
        dialog = AddWordDialog(self, self.corpusModel.corpus)
        if dialog.exec_():
            self.oneNonword = dialog.word
            self.oneNonwordLabel.setText('{} ({})'.format(str(self.oneNonword),
                                                          str(self.oneNonword.transcription)))
            self.oneNonwordRadio.click()

    def oneWordSelected(self):
        self.compType = 'one'
        self.saveFileWidget.setEnabled(True)

    def oneNonwordSelected(self):
        self.compType = 'nonword'
        self.saveFileWidget.setEnabled(True)

    def fileSelected(self):
        self.compType = 'file'
        self.saveFileWidget.setEnabled(False)

    def allwordsSelected(self):
        self.compType = 'all'
        self.saveFileWidget.setEnabled(False)

    def generateKwargs(self):
        if self.maxDistanceEdit.text() == '':
            max_distance = None
        else:
            max_distance = float(self.maxDistanceEdit.text())
        ##------------------
        try:
            frequency_cutoff = float(self.minFreqEdit.text())
        except ValueError:
            frequency_cutoff = 0.0
        ##-------------------
        alg = self.algorithmWidget.value()
        typeToken = self.typeTokenWidget.value()

        kwargs = {'corpusModel':self.corpusModel,
                'algorithm': alg,
                'context': self.variantsWidget.value(),
                'sequence_type':self.tierWidget.value(),
                'type_token':typeToken,
                'max_distance':max_distance,
                'frequency_cutoff':frequency_cutoff,
                'num_cores':self.settings['num_cores'],}
        out_file = self.saveFileWidget.value()
        if out_file == '':
            out_file = None

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
            kwargs['output_filename'] = out_file
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
            kwargs['output_filename'] = out_file
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
                else:
                    w = t
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

    header = ['Corpus',
                'Word',
                'Algorithm',
                'Threshold',
                'String type',
                'Frequency type',
                'Pronunciation variants',
                'Minimum word frequency',
                'Neighborhood density']
    def setResults(self, results):
        self.results = []
        try:
            frequency_cutoff = float(self.minFreqEdit.text())
        except ValueError:
            frequency_cutoff = 0.0
        for result in results:
            w, nd = result
            if not isinstance(w,str):
                w = w.spelling
            if self.algorithmWidget.value() != 'khorsi':
                typetoken = 'N/A'
            else:
                typetoken = self.typeTokenWidget.value().title()
            if self.algorithmWidget.value() == 'substitution':
                thresh = 'N/A'
            else:
                thresh = float(self.maxDistanceEdit.text())
            self.results.append([self.corpusModel.corpus.name, w,
                        self.algorithmWidget.displayValue(), thresh,
                        self.tierWidget.displayValue(), typetoken,
                        self.variantsWidget.value().title(), frequency_cutoff,
                        nd])

    def substitutionSelected(self):
        self.typeTokenWidget.disable()
        self.maxDistanceEdit.setEnabled(False)

    def khorsiSelected(self):
        self.maxDistanceEdit.setEnabled(True)
        self.typeTokenWidget.enable()
        self.tierWidget.setSpellingEnabled(True)

    def editDistSelected(self):
        self.maxDistanceEdit.setEnabled(True)
        self.typeTokenWidget.disable()
        self.maxDistanceEdit.setText('1')
        self.tierWidget.setSpellingEnabled(True)

    def phonoEditDistSelected(self):
        self.maxDistanceEdit.setEnabled(True)
        self.typeTokenWidget.disable()
        self.tierWidget.setSpellingEnabled(False)
