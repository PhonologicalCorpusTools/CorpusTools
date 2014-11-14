
from PyQt5.QtCore import pyqtSignal as Signal,QThread
from PyQt5.QtWidgets import (QDialog, QListWidget, QGroupBox, QHBoxLayout,
                            QVBoxLayout, QPushButton, QFrame, QGridLayout,
                            QRadioButton, QLabel, QFormLayout, QLineEdit,
                            QFileDialog, QComboBox,QProgressDialog, QCheckBox,
                            QMessageBox)

from collections import OrderedDict

from .widgets import DirectoryWidget, RadioSelectWidget
import os
import corpustools.acousticsim.main as AS

class ASWorker(QThread):
    updateProgress = Signal(int)
    updateProgressText = Signal(str)

    dataReady = Signal(object)

    def __init__(self):
        QThread.__init__(self)
        self.stopped = False

    def setParams(self, kwargs):
        kwargs['stop_check'] = self.stopCheck
        kwargs['call_back'] = self.emitProgress
        self.kwargs = kwargs
        self.stopped = False
        self.total = None

    def stop(self):
        self.stopped = True

    def stopCheck(self):
        return self.stopped

    def emitProgress(self,*args):
        if isinstance(args[0],str):
            self.updateProgressText.emit(args[0])
            return
        else:
            progress = args[0]
            if len(args) > 1:
                self.total = args[1]
        self.updateProgress.emit(int((progress/self.total)*100))

    def run(self):
        kwargs = self.kwargs
        self.results = list()
        output = AS.acoustic_similarity_directories(**kwargs)
        if self.stopped:
            return
        output_list, output_val = output
        for o in output_list:
            self.results.append([os.path.split(o[0])[1],
                                            os.path.split(o[1])[1],o[2]])
        self.results.append([os.path.split(kwargs['directory_one'])[1],
                                            os.path.split(kwargs['directory_one'])[1],output_val])
        self.dataReady.emit(self.results)

class ASDialog(QDialog):

    header = ['Directory 1',
            'Directory 2',
            'Representation',
            'Match function',
            'Minimum frequency',
            'Maximum frequency',
            'Number of filters',
            'Number of coefficients',
            'Result',
            'Is similarity?']

    ABOUT = [('This function calculates the acoustic similarity of sound files in two'
                ' directories by generating either MFCCs or amplitude envelopes for each'
                ' sound file and using dynamic time warping or cross-correlation to get '
                'the average distance/similarity across all tokens.'),
                '',
                'Coded by Michael McAuliffe',
                '',
                'References',
                ('Ellis, Daniel P. W. 2005. PLP and RASTA (and MFCC, and'
                ' inversion) in Matlab (online web resource).'
                ' http://www.ee.columbia.edu/~dpwe/resources/matlab/rastamat/.'),
                ('Lewandowski, Natalie. 2012. Talent in nonnative phonetic'
                ' convergence. PhD Thesis.')]

    def __init__(self, parent, showToolTips):
        QDialog.__init__(self, parent)

        self.showToolTips = showToolTips
        layout = QVBoxLayout()

        aslayout = QHBoxLayout()

        directoryFrame = QGroupBox('Directories')
        box = QFormLayout()

        self.directoryOne = DirectoryWidget()
        self.directoryTwo = DirectoryWidget()
        box.addRow('First directory:',self.directoryOne)
        box.addRow('Second directory:',self.directoryTwo)

        directoryFrame.setLayout(box)

        aslayout.addWidget(directoryFrame)

        optionLayout = QVBoxLayout()

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
        self.maxFreqEdit = QLineEdit()

        box.addRow('Minimum frequency (Hz):',self.minFreqEdit)
        box.addRow('Maximum frequency (Hz):',self.maxFreqEdit)
        freqLimFrame.setLayout(box)

        optionLayout.addWidget(freqLimFrame)

        freqResFrame = QGroupBox('Frequency resolution')

        box = QFormLayout()

        self.filterEdit = QLineEdit()
        self.coeffEdit = QLineEdit()

        box.addRow('Number of filters:',self.filterEdit)
        box.addRow('Number of coefficients (MFCC only):',self.coeffEdit)
        freqResFrame.setLayout(box)

        optionLayout.addWidget(freqResFrame)

        self.outputSimWidget = QCheckBox('Output as similarity (0 to 1)')

        optionLayout.addWidget(self.outputSimWidget)

        self.multiprocessingWidget = QCheckBox('Use multiprocessing')

        optionLayout.addWidget(self.multiprocessingWidget)

        optionFrame = QFrame()

        optionFrame.setLayout(optionLayout)

        aslayout.addWidget(optionFrame)

        asframe = QFrame()

        asframe.setLayout(aslayout)

        layout.addWidget(asframe)

        self.newTableButton = QPushButton('Calculate acoustic similarity\n(start new results table)')
        self.oldTableButton = QPushButton('Calculate acoustic similarity\n(add to current results table)')
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
            directoryFrame.setToolTip(("<FONT COLOR=black>"
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
            self.multiprocessingWidget.setToolTip(("<FONT COLOR=black>"
            'Choose whether to use multiple processes.'
                                            ' Multiprocessing is currently not supported'
            "</FONT>"))

        self.setLayout(layout)

        self.setWindowTitle('Acoustic similarity')

        self.thread = ASWorker()

        self.progressDialog = QProgressDialog('Calculating acoustic similarity...','Cancel',0,100,self)
        self.progressDialog.setWindowTitle('Calculating acoustic similarity')
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

    def mfccSelected(self):
        self.coeffEdit.setEnabled(True)

    def envelopesSelected(self):
        self.coeffEdit.setEnabled(False)

    def calcAS(self):
        rep = self.representationWidget.value()
        alg = self.distAlgWidget.value()
        if self.filterEdit.text() in ['','0']:
            if rep == 'mfcc':
                self.filterEdit.setText('26')
            elif rep == 'envelopes':
                self.filterEdit.setText('8')
        if rep == 'mfcc' and self.coeffEdit.text() in ['','0']:
            self.coeffEdit.setText('12')
            if int(self.coeffEdit.text()) > int(self.filterEdit.text())-1:
                self.coeffEdit.setText(str(int(self.filterEdit.text())-1))
        if self.minFreqEdit.text() in ['']:
            self.minFreqEdit.setText('80')
        if self.maxFreqEdit.text() in ['']:
            self.maxFreqEdit.setText('7800')
        try:
            filters = int(self.filterEdit.text())
        except ValueError:
            return
        try:
            coeffs = int(self.coeffEdit.text())
        except ValueError:
            if rep == 'mfcc':
                return
        try:
            freq_lims = (float(self.minFreqEdit.text()),float(self.maxFreqEdit.text()))
        except ValueError:
            return
        kwargs = {
                'directory_one': self.directoryOne.value(),
                'directory_two': self.directoryTwo.value(),
                'rep':rep,
                'match_func':alg,
                'num_filters':filters,
                'num_coeffs':coeffs,
                'freq_lims':freq_lims,
                'output_sim':self.outputSimWidget.isChecked(),
                'use_multi':self.multiprocessingWidget.isChecked(),
                'return_all':True}
        self.thread.setParams(kwargs)

        self.thread.start()

        result = self.progressDialog.exec_()

        self.progressDialog.reset()
        if result:
            self.accept()


    def setResults(self,results):
        self.results = list()

        for r in results:
            self.results.append([r[0],
                            r[1],
                            self.representationWidget.name(),
                            self.distAlgWidget.name(),
                            float(self.minFreqEdit.text()),
                            float(self.maxFreqEdit.text()),
                            int(self.filterEdit.text()),
                            int(self.coeffEdit.text()),
                            r[2],
                            self.outputSimWidget.isChecked()])

    def newTable(self):
        self.update = False
        self.calcAS()

    def oldTable(self):
        self.update = True
        self.calcAS()

    def about(self):
        reply = QMessageBox.information(self,
                "About predictability of distribution", '\n'.join(self.ABOUT))
