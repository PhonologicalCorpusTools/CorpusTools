
import os
from collections import OrderedDict

import corpustools.acousticsim.main as AS

from .imports import *
from .widgets import DirectoryWidget, RadioSelectWidget
from .windows import FunctionWorker, FunctionDialog

class ASWorker(FunctionWorker):
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
        if self.stopped:
            return
        self.results.append([os.path.split(kwargs['directory_one'])[1],
                                            os.path.split(kwargs['directory_one'])[1],output_val])
        self.dataReady.emit(self.results)

class ASDialog(FunctionDialog):

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

    _about = [('This function calculates the acoustic similarity of sound files in two'
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

    name = 'acoustic similarity'

    def __init__(self, parent, showToolTips):
        FunctionDialog.__init__(self, parent, ASWorker())

        self.showToolTips = showToolTips
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

        self.layout().insertWidget(0,asframe)

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


    def mfccSelected(self):
        self.coeffEdit.setEnabled(True)

    def envelopesSelected(self):
        self.coeffEdit.setEnabled(False)

    def calc(self):
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

