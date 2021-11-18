import os
from collections import OrderedDict, defaultdict

from .imports import *
from corpustools.neighdens.neighborhood_density import (neighborhood_density,
                            neighborhood_density_all_words,
                            find_mutation_minpairs_all_words,
                            find_mutation_minpairs,
                            ensure_query_is_word)
from corpustools.neighdens.io import *
from corpustools.corpus.classes import Attribute
from corpustools.exceptions import PCTError, PCTPythonError
from .windows import FunctionWorker, FunctionDialog
from .widgets import (RadioSelectWidget, FileWidget, SaveFileWidget, TierWidget, RestrictedContextWidget)
from .corpusgui import AddWordDialog
from corpustools.contextmanagers import (CanonicalVariantContext, MostFrequentVariantContext)
from corpustools import __version__

class NDWorker(FunctionWorker):
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
        output = list()

        with cm(corpus, st, tt, attribute=att, frequency_threshold = ft) as c:
            try:
                tierdict = defaultdict(list)
                # Create a dict with sequence_type keys for constant-time lookup
                for entry in c:
                    w = getattr(entry, kwargs['sequence_type'])
                    key = str(w)
                    tierdict[key].append(entry)
                if 'query' in kwargs:#this will be true when searching for a single word (in the corpus or not)
                    last_value_removed = None
                    last_key_removed = None
                    for q in kwargs['query']:
                        q = ensure_query_is_word(q, c, c.sequence_type, kwargs['tier_type'], file_type=kwargs['file_type'])
                        #the following code for adding/removing keys is to ensure that homophones are counted later in
                        #the ND algorithm (if the user wants to), but that words are not considered their own neighbours
                        #however, we only do this when comparing inside a corpus. when using a list of external words
                        #we don't want to do this, since it's possible for the external list to contain words that
                        #are in the corpus, and removing them gives the wrong ND value in this case
                        if kwargs['in_corpus']:   # if comparing inside a corpus
                            if last_value_removed:
                                tierdict[last_key_removed].append(last_value_removed)
                            w = getattr(q, kwargs['sequence_type'])
                            last_key_removed = str(w)
                            #last_value_removed = tierdict[last_key_removed].pop()
                            for i, item in enumerate(tierdict[last_key_removed]):       # loop over homophones of 'last_key_removed'
                                if str(item) == str(q) or ''.join(item.Transcription.list) == str(q):
                                    last_value_removed = tierdict[last_key_removed].pop(i)
                                    break

                        #now we call the actual ND algorithms
                        # but before doing so,
                        # if the user loaded spelled wordlist file and a word is not in the corpus...
                        non_word = False
                        try:
                            if kwargs['file_type'] != c.sequence_type:  # if spelled
                                c.corpus.find(str(q))
                        except KeyError:                                # if spelled non-word
                            non_word = True
                            res = 'N/A', ''  # then take a side way and return NA with no calculating

                        # We really 'call the actual ND algorithms', only when the query is not a non_word
                        if not non_word:
                            if kwargs['algorithm'] != 'substitution':
                                res = neighborhood_density(c, q, tierdict,
                                                    algorithm = kwargs['algorithm'],
                                                    max_distance = kwargs['max_distance'],
                                                    force_quadratic=kwargs['force_quadratic'],
                                                    collapse_homophones = kwargs['collapse_homophones'],
                                                    file_type = kwargs['file_type'],
                                                    tier_type = kwargs['tier_type'],
                                                    sequence_type = kwargs['sequence_type'],
                                                    stop_check = kwargs['stop_check'],
                                                    call_back = kwargs['call_back'])
                            else:
                                res = find_mutation_minpairs(c, q,
                                            tier_type=kwargs['tier_type'],
                                            collapse_homophones = kwargs['collapse_homophones'],
                                            stop_check = kwargs['stop_check'],
                                            call_back = kwargs['call_back'])

                        # export ND list when the calculation runs on a single word
                        if 'output_filename' in kwargs and kwargs['output_filename'] is not None:
                            print_neighden_results(kwargs['output_filename'], res[1], kwargs['output_format'])
                        if self.stopped:
                            break
                        if kwargs['file_list'] is not None:
                            output.append(','.join([str(q), str(res[0]), ','.join([str(r) for r in res[1]])]))
                        self.results.append([q, res[0]])
                else:#this will be the case if searching the entire corpus
                    end = kwargs['corpusModel'].beginAddColumn(att)
                    if kwargs['algorithm'] != 'substitution':
                        results = neighborhood_density_all_words(c, tierdict,
                                                tier_type = kwargs['tier_type'],
                                                sequence_type= kwargs['sequence_type'],
                                                algorithm = kwargs['algorithm'],
                                                output_format = kwargs['output_format'],
                                                max_distance = kwargs['max_distance'],
                                                num_cores = kwargs['num_cores'],
                                                call_back = kwargs['call_back'],
                                                stop_check = kwargs['stop_check'],
                                                settable_attr = kwargs['attribute'],
                                                collapse_homophones = kwargs['collapse_homophones']
                                                )
                    else:
                        results = find_mutation_minpairs_all_words(c, tierdict,
                                                tier_type = kwargs['tier_type'],
                                                output_format=kwargs['output_format'],
                                                collapse_homophones = kwargs['collapse_homophones'],
                                                num_cores = kwargs['num_cores'],
                                                stop_check = kwargs['stop_check'],
                                                call_back = kwargs['call_back'])
                    end = kwargs['corpusModel'].endAddColumn(end)

                    # export neighbour list when calculating on the entire corpus
                    if 'output_filename' in kwargs and kwargs['output_filename'] is not None:
                        print_all_neighden_results(kwargs['output_filename'], results)
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

        # export neighbour list when calculating ND with an external .txt wordlist file
        if output and 'output_filename' in kwargs:
            with open(kwargs['output_filename'], encoding='utf-8', mode='w') as outf:
                print('Word,Density,Neighbors', file=outf)
                for item in output:
                    print(item, file=outf)
        self.dataReady.emit(self.results)


class NDDialog(FunctionDialog):
    header = ['Corpus',
              'PCT ver.',
              'Analysis name',
              'Word',
              'Algorithm',
              'Threshold',
              'String type',
              'Frequency type',
              'Collapsed homophones',
              'Pronunciation variants',
              'Minimum word frequency',
              'Result']

    _about = [('This function calculates the neighborhood density (size)'
                    ' of a word. A neighborhood is the set of words sufficiently'
                    ' similar to the target word as defined using a distance metric.'
                    ' For information about the distance metrics, see "About this Function"'
                    ' in the string similarity analysis'),
                    '',
                    'References: ',
                    ('Luce, Paul A. & David B. Pisoni. 1998. '
                    'Recognizing spoken words: The neighborhood activation model. '
                    'Ear Hear 19.1-36.')]

    name = 'neighborhood density'

    def __init__(self, parent, settings, corpusModel, inventory, showToolTips):
        FunctionDialog.__init__(self, parent, settings, NDWorker())

        self.corpusModel = corpusModel
        self.inventory = inventory
        self.showToolTips = showToolTips


        if not self.corpusModel.corpus.has_transcription:
            self.layout().addWidget(QLabel('Corpus does not have transcription, so not all options are available.'))
        elif self.corpusModel.corpus.specifier is None:
            self.layout().addWidget(QLabel(('Corpus does not have a feature system loaded, so not all '
                                           'options are available.')))
        ndlayout = QHBoxLayout()

        algLayout = QVBoxLayout()
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


        algLayout.addWidget(self.algorithmWidget)
        ndlayout.addLayout(algLayout)


        queryFrame = QGroupBox('Query')
        vbox = QFormLayout()
        self.compType = None
        self.oneWordRadio = QRadioButton('Calculate for one word in the corpus\n(Enter spelling)')
        self.oneWordRadio.clicked.connect(self.oneWordSelected)
        self.oneWordEdit = QLineEdit()
        self.oneWordEdit.textChanged.connect(self.oneWordRadio.click)
        self.oneWordRadio.setChecked(True)

        self.oneNonwordRadio = QRadioButton('Calculate for a word/nonword not in the corpus\n(Enter transcription)')
        self.oneNonwordRadio.clicked.connect(self.oneNonwordSelected)
        self.oneNonwordLabel = QLabel('None created')
        self.oneNonword = None
        self.oneNonwordButton = QPushButton('Create word/nonword')
        self.oneNonwordButton.clicked.connect(self.createNonword)

        self.fileRadio = QRadioButton('Calculate for list of words (Load text file)')
        self.fileRadio.clicked.connect(self.fileSelected)
        self.fileWidget = FileWidget('Select a file', 'Text file (*.txt *.csv)')
        self.fileWidget.textChanged.connect(self.fileRadio.click)
        self.fileOptions = QComboBox()

        self.allwordsRadio = QRadioButton('Calculate for all words in the corpus')
        self.allwordsRadio.clicked.connect(self.allwordsSelected)
        self.columnEdit = QLineEdit()
        self.columnEdit.setText('Neighborhood density')
        self.columnEdit.textChanged.connect(self.allwordsRadio.click)

        vbox.addRow(self.oneWordRadio)
        vbox.addRow(self.oneWordEdit)
        vbox.addRow(QHLine())  # add '------'
        vbox.addRow(self.oneNonwordRadio)
        vbox.addRow(self.oneNonwordLabel,self.oneNonwordButton)
        vbox.addRow(QHLine())  # add '------'
        vbox.addRow(self.fileRadio)
        vbox.addRow(self.fileWidget)
        vbox.addRow(self.fileOptions)
        vbox.addRow(QHLine())  # add '------'
        vbox.addRow(self.allwordsRadio)
        vbox.addRow(QLabel('Column name:'),self.columnEdit)
        note = QLabel('(Selecting this option will add a new column containing the results to your corpus. '
                           'No results window will be displayed.)')
        note.setWordWrap(True)
        vbox.addRow(note)

        queryFrame.setLayout(vbox)

        ndlayout.addWidget(queryFrame)
        optionFrame = QGroupBox('Options')

        optionLayout = QVBoxLayout()
        self.useQuadratic = QCheckBox('Use alternative algorithm')
        self.useQuadratic.setChecked(False)
        optionLayout.addWidget(self.useQuadratic)

        self.collapseHomophones = QCheckBox('Collapse homophones before calculating')
        optionLayout.addWidget(self.collapseHomophones)

        self.tierWidget = TierWidget(self.corpusModel.corpus, include_spelling=False)

        optionLayout.addWidget(self.tierWidget)
        for att in reversed(self.tierWidget.attValues()):
            self.fileOptions.addItem('File contains {}'.format(att.display_name))
        self.fileOptions.addItem('File contains Spelling')

        self.typeTokenWidget = RadioSelectWidget('Type or token',
                                            OrderedDict([('Count types','type'),
                                            ('Count tokens','token')]))

        actions = None
        self.variantsWidget = RestrictedContextWidget(self.corpusModel.corpus, actions)

        optionLayout.addWidget(self.variantsWidget)

        optionLayout.addWidget(self.typeTokenWidget)

        validator = QDoubleValidator(float('inf'), 0, 8)

        threshFrame = QGroupBox('Max distance/min similarity')

        self.maxDistanceEdit = QLineEdit()
        self.maxDistanceEdit.setText('1')
        self.maxDistanceEdit.setValidator(validator)

        vbox = QFormLayout()
        vbox.addRow('Threshold:', self.maxDistanceEdit)

        threshFrame.setLayout(vbox)

        optionLayout.addWidget(threshFrame)
        
        ##----------------------
        minFreqFrame = QGroupBox('Minimum frequency')
        box = QFormLayout()
        self.minFreqEdit = QLineEdit()
        self.minFreqEdit.setValidator(validator)
        box.addRow('Minimum word frequency:', self.minFreqEdit)

        minFreqFrame.setLayout(box)

        optionLayout.addWidget(minFreqFrame)
        ##----------------------
        
        fileFrame = QGroupBox('Output list of neighbors to a file')

        self.saveFileWidget = SaveFileWidget('Select file location','Text files (*.txt)')
        self.saveFileFormat = QComboBox()
        for att in reversed(self.tierWidget.attValues()):
            self.saveFileFormat.addItem('Output neighbours as {}'.format(att.display_name))
        self.saveFileFormat.addItem('Output neighbours as spelling')

        vbox = QHBoxLayout()
        vbox.addWidget(self.saveFileWidget)
        vbox.addWidget(self.saveFileFormat)

        fileFrame.setLayout(vbox)

        optionLayout.addWidget(fileFrame)

        optionFrame.setLayout(optionLayout)

        ndlayout.addWidget(optionFrame)

        ndFrame = QFrame()
        ndFrame.setLayout(ndlayout)

        self.layout().insertWidget(0,ndFrame)

        self.algorithmWidget.initialClick()
        # for unknown reasons, the tierSelect combobox doesn't get set to Transcription inside of neighbourhood density
        # even though it does in every other algorithm. this extra line is necessary, and it has to go here
        self.tierWidget.tierSelect.setCurrentIndex(self.tierWidget.tierSelect.findText('Transcription'))


        if self.showToolTips:

            loadFromFileTip = ('<FONT COLOR=black>There must be one word per line in the file that you load. '
                               'Your file can include words that are not actually in your corpus, however all of the symbols '
                               'used in your file must be symbols from your inventory. For example, assuming an English '
                               'corpus you could supply the word "bnick" but not "spe7ec".\nIf a word in your file contains '
                               'multi-character symbols, then you should use a period as a delimiter for that word. Otherwise '
                               'no delimiter is necessary. For example, if /ts/ is an affricate in your corpus, then the word '
                               '/atsano/ should be written as "a.ts.a.n.o" in your file, but the word /blat/ can be written simply '
                               'as "blat" in your file.'
                               '</FONT>')

            self.fileWidget.setToolTip(loadFromFileTip)
            self.fileRadio.setToolTip(loadFromFileTip)

            self.useQuadratic.setToolTip(('<FONT COLOR=black>If this box is checked, PCT will use an algorithm '
            'specific to calculating neighborhood density based on a maximum edit distance of 1. '
            'This algorithm may be faster than the general-purpose algorithm, '
            'especially on very large corpora.</FONT>'))

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
        dialog = AddWordDialog(self, self.corpusModel.corpus, self.inventory)
        if dialog.exec_():
            self.oneNonword = dialog.word
            self.oneNonwordLabel.setText('{} ({})'.format(str(self.oneNonword),
                                                          str(self.oneNonword.transcription)))
            self.oneNonwordRadio.click()

    def oneWordSelected(self):
        self.compType = 'one'
        # self.saveFileWidget.setEnabled(True)

    def oneNonwordSelected(self):
        self.compType = 'nonword'
        # self.saveFileWidget.setEnabled(True)

    def fileSelected(self):
        self.compType = 'file'
        # self.saveFileWidget.setEnabled(False)

    def allwordsSelected(self):
        self.compType = 'all'
        # self.saveFileWidget.setEnabled(False)

    def generateKwargs(self):

        if self.useQuadratic.isChecked() and int(self.maxDistanceEdit.text()) != 1:
            self.useQuadratic.setChecked(False)

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

        if self.fileRadio.isChecked(): #using list of words not in corpus
            file_type = self.fileOptions.currentText().split(' ')[-1].strip()
            for tiername in [self.tierWidget.tierSelect.itemText(i) for i in range(self.tierWidget.tierSelect.count())]:
                if tiername == file_type:
                    self.tierWidget.tierSelect.setCurrentText(tiername)
                    break

        kwargs = {'corpusModel':self.corpusModel,
                'algorithm': alg,
                'context': self.variantsWidget.value(),
                'sequence_type':self.tierWidget.value(),#this is just a string
                'tier_type': self.tierWidget.attValue(),#this is an Attribute type object
                'type_token':typeToken,
                'max_distance':max_distance,
                'frequency_cutoff':frequency_cutoff,
                'num_cores':self.settings['num_cores'],
                'force_quadratic': self.useQuadratic.isChecked(),
                'file_type': self.fileOptions.currentText().split()[-1],   # "----" out of file contains "----"
                'collapse_homophones': self.collapseHomophones.isChecked(),
                'output_format': self.saveFileFormat.currentText().split(' ')[-1].lower(),\
                'in_corpus': True}

        out_file = self.saveFileWidget.value()
        if out_file == '':
            out_file = None
        else:
            kwargs['output_filename'] = out_file

        kwargs['file_list'] = None
        if self.compType is None:
            reply = QMessageBox.critical(self,
                "Missing information", 'Please select an option from the "Query" section in the middle of the window.')
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
                        "Missing information",
                        "Please recreate the word/nonword with '{}' specified.".format(self.tierWidget.displayValue()))
                return
            kwargs['query'] = [self.oneNonword]
            kwargs['in_corpus'] = True
            kwargs['output_filename'] = out_file
        elif self.compType == 'file':
            path = self.fileWidget.value()
            kwargs['file_list'] = path
            kwargs['in_corpus'] = True
            if not path:
                reply = QMessageBox.critical(self,
                        "Missing information", "Please enter a file path.")
                return
            if not os.path.exists(path):
                reply = QMessageBox.critical(self,
                        "Invalid information", "The file path entered was not found.")
                return
            kwargs['query'] = list()
            file_sequence_type = self.fileOptions.currentText().split(' ')[-1].lower()
            text = load_words_neighden(path, file_sequence_type)
            not_in_corpus = []
            for t in text:
                # before adding the line in the external file into 'query', need to check whether that word is
                # found in the corpus. If not, raise a message letting the user know about this.
                if kwargs['file_type'] == 'Spelling':            # user loaded the external file as 'spelling'
                    try:
                        kwargs['corpusModel'].corpus.find(t)
                        kwargs['query'].append(t)
                    except KeyError:
                        not_in_corpus.append(t)
                        kwargs['query'].append(t)
                else:                                           # user loaded the external file as 'transcription'
                    test = '.'.join(t) if '.' not in t else t  # 'test' to see if t is found in the corpus
                    identified = False
                    # for each word in the corpus, see if it has the same transcription as 't'
                    if test in [str(entry.transcription) for entry in kwargs['corpusModel'].corpus]:
                        identified = True
                    if not identified:
                        not_in_corpus.append(t)
                    kwargs['query'].append(t)

            if len(not_in_corpus) > 0:  # if any word not in corpus, raise error window and export file
                self.raise_noword_warning_msg(not_in_corpus, file_type=kwargs['file_type'])
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
            self.results.append({'Corpus': self.corpusModel.corpus.name,
                                'PCT ver.': __version__,#self.corpusModel.corpus._version,
                                'Analysis name': self.name.capitalize(),
                                'Word': w,
                                'Algorithm': self.algorithmWidget.displayValue(),
                                'Threshold': thresh,
                                'String type': self.tierWidget.displayValue(),
                                'Frequency type': typetoken,
                                'Collapsed homophones': 'Yes' if self.collapseHomophones.isChecked() else 'No',
                                'Pronunciation variants': self.variantsWidget.value().title(),
                                'Minimum word frequency': frequency_cutoff,
                                'Result': nd})

    def substitutionSelected(self):
        self.typeTokenWidget.disable()
        self.maxDistanceEdit.setEnabled(False)
        self.useQuadratic.setEnabled(False)
        self.fileRadio.setEnabled(True)
        self.fileWidget.setEnabled(True)
        self.fileOptions.setEnabled(True)

    def khorsiSelected(self):
        self.maxDistanceEdit.setEnabled(True)
        self.typeTokenWidget.enable()
        # self.tierWidget.setSpellingEnabled(True)   # no more nd for spelling per se. see issue #770.
        self.useQuadratic.setEnabled(False)
        self.fileRadio.setEnabled(True)
        self.fileWidget.setEnabled(True)
        self.fileOptions.setEnabled(True)

    def editDistSelected(self):
        self.maxDistanceEdit.setEnabled(True)
        self.typeTokenWidget.disable()
        # self.tierWidget.setSpellingEnabled(True)   # no more nd for spelling per se. see issue #770.
        self.useQuadratic.setEnabled(True)
        self.fileRadio.setEnabled(True)
        self.fileWidget.setEnabled(True)
        self.fileOptions.setEnabled(True)
        #self.maxDistanceEdit.setText('1')

    def phonoEditDistSelected(self):
        self.maxDistanceEdit.setEnabled(True)
        self.typeTokenWidget.disable()
        self.tierWidget.setSpellingEnabled(False)
        self.useQuadratic.setEnabled(False)

        # disable file import altogether
        self.fileRadio.setEnabled(False)
        self.fileWidget.setEnabled(False)
        self.fileOptions.setCurrentIndex(1)
        self.fileOptions.setEnabled(False)

    def raise_noword_warning_msg(self, non_word, file_type):
        """
        Raise a warning message and export a wordlist to the ERRORS folder.
        This function is called when the user loaded a text file of word pairs but one or more words
        in the file are not found in the corpus. See issue #769

        Parameters
        ----------
        non_word : list
            List of words in the external file but not in the corpus
        file_type : str
            Either 'Spelling' or 'Transcription.' The warning message should be tailored with respect to the file_type
        """
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        if len(non_word) == 1:
            msg_box.setWindowTitle("Word not in corpus")
            error_content = "The word '{}' is not in the corpus.\n".format(non_word[0])
            if file_type == 'Spelling':
                error_content += "PCT cannot calculate neighbourhood density from spelling, unless it refers to " \
                                 "a word already in the corpus. " \
                                 "Therefore, the result for '{}' will be 'N/A.'".format(non_word[0])
            else:
                error_content += "PCT can still calculate neighbourhood density for '{}' itself. " \
                                 "Note that words in the .txt file will not be added to the corpus, nor does " \
                                 "PCT include any of the words in the .txt file itself when calculating the " \
                                 "neighbourhood densities of each word.".format(non_word[0])
        else:
            error_dir = self.parent().settings.error_directory()
            corpus_name = self.corpusModel.corpus.name
            error_filename = 'neigh_density_error.txt'
            msg_box.setWindowTitle("Words not in corpus")
            error_content = "{} words are not in the corpus.\nFor details, please refer to file {} in the " \
                            "ERRORS directory or click on “Show Details” below.".format(len(non_word), error_filename)
            details = "The following words are not found in the corpus '{}.'\n".format(corpus_name)
            if file_type == 'Spelling':
                details += "PCT cannot calculate neighbourhood density from spellings, unless they refer to a word " \
                           "already in the corpus. The results for the nonwords will be listed as 'N/A.'\n\n"
            else:
                details += "PCT can still calculate neighbourhood density for a transcribed nonword itself.\n" \
                           "However, note that words in the .txt file will not be added to the corpus, " \
                           "nor does PCT include any of the words in the .txt file itself when calculating the " \
                           "neighbourhood densities of each word.\n\n"

            details += "The text file you loaded (as {}): {}\n".format(file_type, self.fileWidget.value())
            details += "Corpus: {}\n".format(corpus_name)
            details += "Words not in the corpus:"
            for nw in non_word:
                details += "\n" + nw
            with open(os.path.join(error_dir, error_filename), 'w', encoding='utf-8-sig') as f:
                print(details, file=f)

            msg_box.addButton("Open ERRORS directory", QMessageBox.AcceptRole)

            msg_box.setDetailedText(details)
        msg_box.setText(error_content)

        # Internally 'close' button (so that it comes at the right-most side) but shown as 'OK'.
        # This is done because this button should be on the right side of 'details' and should not mislead the user.
        # This button does not 'close' the function, but instead the user still proceeds to the function result window.
        msg_box.addButton(QMessageBox.Close)
        ok_button = msg_box.button(QMessageBox.Close)
        ok_button.setText('OK')

        r = msg_box.exec()

        if r == QMessageBox.AcceptRole:
            if sys.platform == 'win32':
                args = ['{}'.format(error_dir)]
                program = 'explorer'
                # subprocess.call('explorer "{0}"'.format(self.parent().settings.error_directory()),shell=True)
            elif sys.platform == 'darwin':
                program = 'open'
                args = ['{}'.format(error_dir)]
            else:
                program = 'xdg-open'
                args = ['{}'.format(error_dir)]
            # subprocess.call([program]+args,shell=True)
            proc = QProcess(self.parent())
            t = proc.startDetached(program, args)
