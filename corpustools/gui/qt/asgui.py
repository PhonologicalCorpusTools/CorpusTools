
from PyQt5.QtWidgets import (QDialog, QListWidget, QGroupBox, QHBoxLayout,
                            QVBoxLayout, QPushButton, QFrame, QGridLayout,
                            QRadioButton, QLabel, QFormLayout, QLineEdit,
                            QFileDialog, QComboBox)

from .widgets import DirectoryWidget, RadioSelectWidget

class ASDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)

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
                                                        {'MFCC':'mfcc',
                                                        'Amplitude envelopes':'envelopes'})

        optionLayout.addWidget(self.representationWidget)

        self.distAlgWidget = RadioSelectWidget('Distance algorithm',
                                                        {'Dynamic time warping':'dtw',
                                                        'Cross-correlation':'xcorr'})

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

        self.outputSimWidget = RadioSelectWidget('Output',
                                                        {'Output as similarity (0 to 1)':True,
                                                        'Output as distance':False})

        optionLayout.addWidget(self.outputSimWidget)

        self.multiprocessingWidget = RadioSelectWidget('Multiprocessing',
                                                        {'Use multiprocessing':True,
                                                        'Use single core':False})

        optionLayout.addWidget(self.multiprocessingWidget)

        optionFrame = QFrame()

        optionFrame.setLayout(optionLayout)

        aslayout.addWidget(optionFrame)

        asframe = QFrame()

        asframe.setLayout(aslayout)

        layout.addWidget(asframe)

        self.acceptButton = QPushButton('Ok')
        self.cancelButton = QPushButton('Cancel')
        self.aboutButton = QPushButton('About this function...')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.cancelButton)
        acLayout.addWidget(self.aboutButton)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Acoustic similarity')
