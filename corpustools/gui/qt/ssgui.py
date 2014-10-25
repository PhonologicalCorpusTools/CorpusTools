
from PyQt5.QtWidgets import (QDialog, QListWidget, QGroupBox, QHBoxLayout,
                            QVBoxLayout, QPushButton, QFrame, QGridLayout,
                            QRadioButton, QLabel, QFormLayout, QLineEdit,
                            QFileDialog, QComboBox)

class SSDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)

        layout = QVBoxLayout()

        sslayout = QHBoxLayout()

        algorithmFrame = QGroupBox('String similarity algorithm')

        self.khorsiRadio = QRadioButton('Khorsi')
        self.editDistRadio = QRadioButton('Edit distance')
        self.phonEditDistRadio = QRadioButton('Phonological edit distance')
        vbox = QVBoxLayout()
        vbox.addWidget(self.khorsiRadio)
        vbox.addWidget(self.editDistRadio)
        vbox.addWidget(self.phonEditDistRadio)
        algorithmFrame.setLayout(vbox)


        sslayout.addWidget(algorithmFrame)

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

        typeTokenFrame = QGroupBox('Type or token')

        self.typeRadio = QRadioButton('Count types')
        self.tokenRadio = QRadioButton('Count tokens')

        vbox = QVBoxLayout()
        vbox.addWidget(self.typeRadio)
        vbox.addWidget(self.tokenRadio)

        typeTokenFrame.setLayout(vbox)

        optionLayout.addWidget(typeTokenFrame)

        stringTypeFrame = QGroupBox('String type')

        self.spellingRadio = QRadioButton('Compare spelling')
        self.transRadio = QRadioButton('Compare transcription')

        vbox = QVBoxLayout()
        vbox.addWidget(self.spellingRadio)
        vbox.addWidget(self.transRadio)

        stringTypeFrame.setLayout(vbox)

        optionLayout.addWidget(stringTypeFrame)

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
