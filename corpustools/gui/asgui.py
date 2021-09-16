import os
from collections import OrderedDict

from corpustools.acousticsim.io import load_path_mapping
from corpustools.exceptions import PCTPythonError

try:
    real_acousticsim = True
    from acousticsim.main import(acoustic_similarity_mapping,
                            acoustic_similarity_directories,
                            analyze_directory, AcousticSimError)
except (ImportError, ModuleNotFoundError) as e:
    real_acousticsim = False
    from corpustools.acousticsim.main import(acoustic_similarity_mapping,
                            acoustic_similarity_directories,
                            analyze_directory, AcousticSimError)

from .imports import *
from .widgets import DirectoryWidget, RadioSelectWidget, FileWidget
from .windows import FunctionWorker, FunctionDialog
from corpustools import __version__

class ASWorker(FunctionWorker):
    def run(self):
        kwargs = self.kwargs
        self.results = list()
        if kwargs['type'] == 'one':
            try:
                asim = analyze_directory(kwargs['query'], **kwargs)
            except AcousticSimError as e:
                self.errorEncountered.emit(e)
                return
            except Exception as e:
                e = PCTPythonError(e)
                self.errorEncountered.emit(e)
                return
        elif kwargs['type'] == 'two':
            try:
                asim, output_val = acoustic_similarity_directories(*kwargs['query'],**kwargs)
            except AcousticSimError as e:
                self.errorEncountered.emit(e)
                return
            except Exception as e:
                e = PCTPythonError(e)
                self.errorEncountered.emit(e)
                return

            #asim[(kwargs['query'][0],kwargs['query'][1])] = output_val
        elif kwargs['type'] == 'file':
            try:
                asim = acoustic_similarity_mapping(kwargs['query'], **kwargs)
            except AcousticSimError as e:
                self.errorEncountered.emit(e)
                return
            except Exception as e:
                e = PCTPythonError(e)
                self.errorEncountered.emit(e)
                return
        if self.stopped:
            return
        for k,v in asim.items():
            if self.stopped:
                return
            self.results.append(list(k) + [v])

        if kwargs['type'] == 'two':
            self.results.append([os.path.basename(kwargs['query'][0]),os.path.basename(kwargs['query'][1]), output_val])
        else:
            self.results.append(['AVG', 'AVG',sum(asim.values())/len(asim)])
        if self.stopped:
            self.finishedCancelling.emit()
            return
        self.dataReady.emit(self.results)

class ASDialog(FunctionDialog):

    header = ['PCT ver.',
            'Analysis name',
            'File 1',
            'File 2',
            'Representation',
            'Match function',
            'Minimum frequency',
            'Maximum frequency',
            'Number of filters',
            'Number of coefficients',
            'Is similarity',
            'Result']

    _about = [('This function calculates the acoustic similarity of sound files in two'
                ' directories by generating either MFCCs or amplitude envelopes for each'
                ' sound file and using dynamic time warping or cross-correlation to get '
                'the average distance/similarity across all tokens.'),
                '',
                'References: ',
                ('Ellis, Daniel P. W. 2005. PLP and RASTA (and MFCC, and'
                ' inversion) in Matlab (online web resource).'
                ' http://www.ee.columbia.edu/~dpwe/resources/matlab/rastamat/.'),
                ('Lewandowski, Natalie. 2012. Talent in nonnative phonetic'
                ' convergence. PhD Thesis.')]

    name = 'acoustic similarity'

    def __init__(self, parent, settings, showToolTips):
        FunctionDialog.__init__(self, parent, settings, ASWorker())

        self.showToolTips = showToolTips
        aslayout = QHBoxLayout()

        compFrame = QGroupBox('Comparison type')

        vbox = QFormLayout()
        self.compType = None
        self.oneDirectoryRadio = QRadioButton('Analyze single directory')
        self.oneDirectoryRadio.clicked.connect(self.oneDirectorySelected)
        self.oneDirectoryWidget = DirectoryWidget()
        self.oneDirectoryWidget.textChanged.connect(self.oneDirectoryRadio.click)
        self.twoDirectoryRadio = QRadioButton('Compare two directories')
        self.twoDirectoryRadio.clicked.connect(self.twoDirectoriesSelected)
        self.directoryOneWidget = DirectoryWidget()
        self.directoryOneWidget.textChanged.connect(self.twoDirectoryRadio.click)
        self.directoryTwoWidget = DirectoryWidget()
        self.directoryTwoWidget.textChanged.connect(self.twoDirectoryRadio.click)
        self.fileRadio = QRadioButton('Use list of full path comparisons')
        self.fileRadio.clicked.connect(self.fileSelected)
        self.fileWidget = FileWidget('Select a word pairs file', 'Text file (*.txt *.csv)')
        self.fileWidget.textChanged.connect(self.fileRadio.click)

        vbox.addRow(self.oneDirectoryRadio)
        vbox.addRow(QLabel('Directory:'))
        vbox.addRow(self.oneDirectoryWidget)
        vbox.addRow(self.twoDirectoryRadio)
        vbox.addRow(QLabel('First directory:'))
        vbox.addRow(self.directoryOneWidget)
        vbox.addRow(QLabel('Second directory:'))
        vbox.addRow(self.directoryTwoWidget)
        vbox.addRow(self.fileRadio)
        vbox.addRow(self.fileWidget)

        compFrame.setLayout(vbox)

        aslayout.addWidget(compFrame)

        optionLayout = QVBoxLayout()

        validator = QDoubleValidator(float('inf'), 0, 8)

        self.representationWidget = RadioSelectWidget('Represenation',
                                                        OrderedDict([('MFCC','mfcc'),
                                                        ('Amplitude envelopes','envelopes')]),
                                                        {'MFCC':self.mfccSelected,
                                                        'Amplitude envelopes':self.envelopesSelected})

        optionLayout.addWidget(self.representationWidget)

        self.distAlgWidget = RadioSelectWidget('Distance algorithm',
                                                        OrderedDict([('Dynamic time warping','dtw'),
                                                        ('Cross-correlation','xcorr')]))

        optionLayout.addWidget(self.distAlgWidget)

        freqLimFrame = QGroupBox('Frequency limits')

        box = QFormLayout()

        self.minFreqEdit = QLineEdit()
        self.minFreqEdit.setValidator(validator)
        self.minFreqEdit.setText('80')

        self.maxFreqEdit = QLineEdit()
        self.maxFreqEdit.setValidator(validator)
        self.maxFreqEdit.setText('7800')

        box.addRow('Minimum frequency (Hz):',self.minFreqEdit)
        box.addRow('Maximum frequency (Hz):',self.maxFreqEdit)
        freqLimFrame.setLayout(box)

        optionLayout.addWidget(freqLimFrame)

        freqResFrame = QGroupBox('Frequency resolution')

        box = QFormLayout()

        self.filterEdit = QLineEdit()
        self.filterEdit.setValidator(validator)
        self.coeffEdit = QLineEdit()
        self.coeffEdit.setValidator(validator)

        box.addRow('Number of filters:',self.filterEdit)
        box.addRow('Number of coefficients (MFCC only):',self.coeffEdit)
        freqResFrame.setLayout(box)

        optionLayout.addWidget(freqResFrame)

        self.outputSimWidget = QCheckBox('Output as similarity (0 to 1)')

        optionLayout.addWidget(self.outputSimWidget)

        #self.multiprocessingWidget = QCheckBox('Use multiprocessing')

        #optionLayout.addWidget(self.multiprocessingWidget)
        if real_acousticsim:
            optionLayout.addWidget(QLabel('Acoustic similarity benefits from multiprocessing.'))
            optionLayout.addWidget(QLabel('Multiprocessing can be enabled in Preferences.'))
        else:
            optionLayout.addWidget(QLabel('The acoustic similarity module loaded\ndoes not support multiprocessing.'))
            optionLayout.addWidget(QLabel('Install python-acoustic-similarity\nto access multiprocessing and additional _features.'))

        optionFrame = QFrame()

        optionFrame.setLayout(optionLayout)

        aslayout.addWidget(optionFrame)

        asframe = QFrame()

        asframe.setLayout(aslayout)

        self.layout().insertWidget(0,asframe)
        self.representationWidget.initialClick()
        if self.showToolTips:
            compFrame.setToolTip(("<FONT COLOR=black>"
            'Choose two directories to compare sound files between.'
            "</FONT>"))
            self.representationWidget.setToolTip(("<FONT COLOR=black>"
            'Choose how to represent acoustic waveforms.'
            "</FONT>"))
            self.distAlgWidget.setToolTip(("<FONT COLOR=black>"
            'Choose how to compare representations.'
            "</FONT>"))
            freqLimFrame.setToolTip(("<FONT COLOR=black>"
            'Choose frequency range.'
            "</FONT>"))
            freqResFrame.setToolTip(("<FONT COLOR=black>"
            'Choose how many filters to divide the frequency range'
                                            ' and how many coefficients to use for MFCC generation.'
                                            ' Leave blank for reasonable defaults based on the'
                                            ' representation.'
            "</FONT>"))
            self.outputSimWidget.setToolTip(("<FONT COLOR=black>"
            'Choose whether the result should be similarity'
                                            ' or distance. Similarity is inverse distance,'
                                            ' and distance is inverse similarity'
            "</FONT>"))
            #self.multiprocessingWidget.setToolTip(("<FONT COLOR=black>"
            #'Choose whether to use multiple processes.'
            #                                ' Multiprocessing is currently not supported'
            #"</FONT>"))

    def oneDirectorySelected(self):
        self.compType = 'one'

    def twoDirectoriesSelected(self):
        self.compType = 'two'

    def fileSelected(self):
        self.compType = 'file'

    def mfccSelected(self):
        self.coeffEdit.setEnabled(True)
        self.filterEdit.setText('26')
        self.coeffEdit.setText('12')


    def envelopesSelected(self):
        self.coeffEdit.setText('N/A')
        self.coeffEdit.setEnabled(False)
        self.filterEdit.setText('8')

    def generateKwargs(self):
        rep = self.representationWidget.value()
        alg = self.distAlgWidget.value()

        try:
            filters = int(self.filterEdit.text())
            if filters < 0:
                raise(ValueError)
        except ValueError:
            reply = QMessageBox.critical(self,
                    "Invalid information", "The number of filters must be a number greater than 0.")
            return
        try:
            coeffs = int(self.coeffEdit.text())
            if coeffs <= 0:
                raise(ValueError)
            if int(self.coeffEdit.text()) > int(self.filterEdit.text())-1:
                raise(ValueError)

        except ValueError:
            if rep == 'mfcc':
                reply = QMessageBox.critical(self,
                        "Invalid information", "The number of coefficients must be a number greater than 0 and less than the number of filters.")
                return
        try:
            freq_lims = (float(self.minFreqEdit.text()),float(self.maxFreqEdit.text()))
            if freq_lims[0] < 0 or freq_lims[1] < 0:
                raise(ValueError("The minimum and maximum frequenies must be greater than 0."))
            if freq_lims[0] >= freq_lims[1]:
                raise(ValueError("The maximum frequeny must be greater than the minimum frequency."))
        except ValueError as e:
                reply = QMessageBox.critical(self,
                        "Invalid information", str(e))
                return
        kwargs = {
                'type': self.compType,
                'rep':rep,
                'match_func':alg,
                'num_filters':filters,
                'freq_lims':freq_lims,
                'output_sim':self.outputSimWidget.isChecked(),
                'use_multi':self.settings['use_multi'],
                'num_cores':self.settings['num_cores'],
                'return_all':True}
        if rep == 'mfcc':
            kwargs['num_coeffs'] = coeffs
        if self.compType is None:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a comparison type.")
            return
        elif self.compType == 'one':
            kwargs['query'] = self.oneDirectoryWidget.value()
        elif self.compType == 'two':
            dirOne = self.directoryOneWidget.value()
            if dirOne == '':
                reply = QMessageBox.critical(self,
                        "Missing information", "Please specify the first directory.")
                return
            if not os.path.exists(dirOne):
                reply = QMessageBox.critical(self,
                        "Invalid information", "The first directory does not exist.")
                return
            dirTwo = self.directoryTwoWidget.value()
            if dirTwo == '':
                reply = QMessageBox.critical(self,
                        "Missing information", "Please specify the second directory.")
                return
            if not os.path.exists(dirTwo):
                reply = QMessageBox.critical(self,
                        "Invalid information", "The second directory does not exist.")
                return

            kwargs['query'] = [dirOne, dirTwo]
        elif self.compType == 'file':
            path = self.fileWidget.value()
            if path == '':
                reply = QMessageBox.critical(self,
                        "Missing information", "Please specify a path mapping file.")
                return
            if not os.path.exists(path):
                reply = QMessageBox.critical(self,
                        "Invalid information", "The specified path mapping file does not exist.")
                return
            try:
                kwargs['query'] = load_path_mapping(path)
            except OSError as e:
                reply = QMessageBox.critical(self,
                        "Invalid information", str(e))
                return
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


    def setResults(self,results):
        self.results = list()

        for r in results:            
            self.results.append({'PCT ver.': __version__,#self.corpusModel.corpus._version,
                                'Analysis name': self.name.capitalize(),
                                'File 1': r[0],
                                'File 2': r[1],
                                'Representation': self.representationWidget.displayValue(),
                                'Match function': self.distAlgWidget.displayValue(),
                                'Minimum frequency': float(self.minFreqEdit.text()),
                                'Maximum frequency': float(self.maxFreqEdit.text()),
                                'Number of filters': int(self.filterEdit.text()),
                                'Number of coefficients': self.coeffEdit.text(),
                                'Is similarity': self.outputSimWidget.isChecked(),
                                'Result': r[2]})

