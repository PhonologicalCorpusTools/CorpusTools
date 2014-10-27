
from PyQt5.QtWidgets import (QDialog, QListWidget, QGroupBox, QHBoxLayout,
                            QVBoxLayout, QPushButton, QFrame, QGridLayout,
                            QRadioButton, QLabel, QFormLayout, QLineEdit,
                            QFileDialog, QComboBox, QCheckBox)

from .widgets import SegmentPairSelectWidget, RadioSelectWidget, FileWidget

class FADialog(QDialog):
    def __init__(self, parent, corpus):
        QDialog.__init__(self, parent)

        self.corpus = corpus
        layout = QVBoxLayout()

        falayout = QHBoxLayout()

        self.segPairsWidget = SegmentPairSelectWidget(corpus.inventory)

        falayout.addWidget(self.segPairsWidget)


        self.algorithmWidget = RadioSelectWidget('String similarity algorithm',
                                            {'Khorsi':'khorsi',
                                            'Edit distance':'edit_distance',
                                            'Phonological edit distance':'phono_edit_distance'})


        falayout.addWidget(self.algorithmWidget)

        optionFrame = QGroupBox('Options')

        optionLayout = QVBoxLayout()

        self.typeTokenWidget = RadioSelectWidget('Type or token',
                                            {'Count types':'type',
                                            'Count tokens':'token'})

        optionLayout.addWidget(self.typeTokenWidget)

        self.minPairsWidget = RadioSelectWidget('Minimal pairs',
                                            {'Ignore minimal pairs':'ignore',
                                            'Include minimal pairs':'include'})

        optionLayout.addWidget(self.minPairsWidget)

        threshFrame = QGroupBox('Threshold values')

        self.minEdit = QLineEdit()
        self.maxEdit = QLineEdit()

        vbox = QFormLayout()
        vbox.addRow('Minimum similarity (Khorsi):',self.minEdit)
        vbox.addRow('Maximum distance (edit distance):',self.maxEdit)

        threshFrame.setLayout(vbox)

        optionLayout.addWidget(threshFrame)

        alignFrame = QGroupBox('Alignment')

        self.alignCheck = QCheckBox('Do phonological alignment')

        vbox = QVBoxLayout()
        vbox.addWidget(self.alignCheck)

        alignFrame.setLayout(vbox)

        optionLayout.addWidget(alignFrame)

        corpusSizeFrame = QGroupBox('Corpus size')

        self.corpusSizeEdit = QLineEdit()

        vbox = QFormLayout()
        vbox.addRow('Subset corpus:',self.corpusSizeEdit)

        corpusSizeFrame.setLayout(vbox)

        optionLayout.addWidget(corpusSizeFrame)

        fileFrame = QGroupBox('Output file')

        self.fileWidget = FileWidget('Select file location','Text files (*.txt)')

        vbox = QHBoxLayout()
        vbox.addWidget(self.fileWidget)

        fileFrame.setLayout(vbox)

        optionLayout.addWidget(fileFrame)


        optionFrame.setLayout(optionLayout)

        falayout.addWidget(optionFrame)

        faframe = QFrame()
        faframe.setLayout(falayout)



        layout.addWidget(faframe)

        self.newTableButton = QPushButton('Calculate frequency of alternation\n(new table)')
        self.oldTableButton = QPushButton('Calculate frequency of alternation\n(add to current table)')
        self.cancelButton = QPushButton('Cancel')
        self.aboutButton = QPushButton('About this function...')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.newTableButton)
        acLayout.addWidget(self.oldTableButton)
        acLayout.addWidget(self.cancelButton)
        acLayout.addWidget(self.aboutButton)
        self.newTableButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Frequency of alternation')
