
from PyQt5.QtWidgets import (QDialog, QListWidget, QGroupBox, QHBoxLayout,
                            QVBoxLayout, QPushButton, QFrame, QGridLayout,
                            QRadioButton, QLabel, QFormLayout, QLineEdit,
                            QFileDialog, QComboBox)

from .widgets import SegmentPairSelectWidget, RadioSelectWidget

class FLDialog(QDialog):
    def __init__(self, parent, corpus):
        QDialog.__init__(self, parent)

        self.corpus = corpus
        layout = QVBoxLayout()

        flFrame = QFrame()
        fllayout = QHBoxLayout()

        self.segPairWidget = SegmentPairSelectWidget(corpus.inventory)

        fllayout.addWidget(self.segPairWidget)

        layout.addWidget(flFrame)

        self.algorithmWidget = RadioSelectWidget('Functional load algorithm',
                                            {'Minimal pairs':'min_pairs',
                                            'Change in entropy':'h'})

        fllayout.addWidget(self.algorithmWidget)

        optionLayout = QVBoxLayout()

        self.segPairOptionsWidget = RadioSelectWidget('Multiple segment pair behaviour',
                                                {'All segment pairs together':'together',
                                                'Each segment pair individually':'individual'})

        optionLayout.addWidget(self.segPairOptionsWidget)

        minFreqFrame = QGroupBox('Minimum frequency')
        box = QFormLayout()
        self.minFreqEdit = QLineEdit()
        box.addRow('Only consider words with frequency of at least:',self.minFreqEdit)

        minFreqFrame.setLayout(box)

        optionLayout.addWidget(minFreqFrame)

        minPairOptionFrame = QGroupBox('Minimal pair options')

        box = QVBoxLayout()

        self.relativeCountWidget = RadioSelectWidget('Relative count',
                                                    {'Use counts relative to number of possible pairs':'relative',
                                                    'Use raw counts':'raw'})

        self.homophoneWidget = RadioSelectWidget('Homophones',
                                                {'Include homophones':'include',
                                                'Ignore homophones':'ignore'})

        box.addWidget(self.relativeCountWidget)
        box.addWidget(self.homophoneWidget)

        minPairOptionFrame.setLayout(box)

        optionLayout.addWidget(minPairOptionFrame)

        entropyOptionFrame = QGroupBox('Change in entropy options')

        box = QVBoxLayout()

        self.typeTokenWidget = RadioSelectWidget('Type or token frequencies',
                                                    {'Type':'type',
                                                    'Token':'token'})

        box.addWidget(self.typeTokenWidget)
        entropyOptionFrame.setLayout(box)
        optionLayout.addWidget(entropyOptionFrame)

        optionFrame = QGroupBox('Options')
        optionFrame.setLayout(optionLayout)

        fllayout.addWidget(optionFrame)
        flFrame.setLayout(fllayout)


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

        self.setWindowTitle('Functional load')
