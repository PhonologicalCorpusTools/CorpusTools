
from PyQt5.QtWidgets import (QDialog, QListWidget, QGroupBox, QHBoxLayout,
                            QVBoxLayout, QPushButton, QFrame, QGridLayout,
                            QRadioButton, QLabel, QFormLayout, QLineEdit,
                            QFileDialog, QComboBox)

from .widgets import RadioSelectWidget

class SSDialog(QDialog):
    def __init__(self, parent, corpus):
        QDialog.__init__(self, parent)

        self.corpus = corpus
        layout = QVBoxLayout()

        sslayout = QHBoxLayout()

        self.algorithmWidget = RadioSelectWidget('String similarity algorithm',
                                            {'Khorsi':'khorsi',
                                            'Edit distance':'edit_distance',
                                            'Phonological edit distance':'phono_edit_distance'})


        sslayout.addWidget(self.algorithmWidget)

        compFrame = QGroupBox('Comparison type')

        vbox = QFormLayout()

        self.oneWordRadio = QRadioButton('Compare one word to entire corpus')
        self.oneWordEdit = QLineEdit()
        self.twoWordRadio = QRadioButton('Compare a single pair of words to each other')
        self.wordOneEdit = QLineEdit()
        self.wordTwoEdit = QLineEdit()
        self.fileRadio = QRadioButton('Compare a list of pairs of words')
        self.fileEdit = QLineEdit()
        self.fileButton = QPushButton('Choose word pairs file')

        vbox.addRow(self.oneWordRadio)
        vbox.addRow(self.oneWordEdit)
        vbox.addRow(self.twoWordRadio)
        vbox.addRow('Word 1:',self.wordOneEdit)
        vbox.addRow('Word 2:',self.wordTwoEdit)
        vbox.addRow(self.fileRadio)
        vbox.addRow(self.fileEdit)
        vbox.addRow(self.fileButton)

        compFrame.setLayout(vbox)

        sslayout.addWidget(compFrame)

        optionFrame = QGroupBox('Options')

        optionLayout = QVBoxLayout()

        self.typeTokenWidget = RadioSelectWidget('Type or token',
                                            {'Count types':'type',
                                            'Count tokens':'token'})

        optionLayout.addWidget(self.typeTokenWidget)

        self.stringTypeWidget = RadioSelectWidget('String type',
                                            {'Compare spelling':'spelling',
                                            'Compare transcription':'transcription'})

        optionLayout.addWidget(self.stringTypeWidget)

        threshFrame = QGroupBox('Return only results between...')

        self.minEdit = QLineEdit()
        self.maxEdit = QLineEdit()

        vbox = QFormLayout()
        vbox.addRow('Minimum:',self.minEdit)
        vbox.addRow('Maximum:',self.maxEdit)

        threshFrame.setLayout(vbox)

        optionLayout.addWidget(threshFrame)


        optionFrame.setLayout(optionLayout)

        sslayout.addWidget(optionFrame)

        ssFrame = QFrame()
        ssFrame.setLayout(sslayout)

        layout.addWidget(ssFrame)

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

        self.setWindowTitle('String similarity')
