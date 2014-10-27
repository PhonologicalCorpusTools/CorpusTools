
from PyQt5.QtWidgets import (QDialog, QListWidget, QGroupBox, QHBoxLayout,
                            QVBoxLayout, QPushButton, QFrame, QGridLayout,
                            QRadioButton, QLabel, QFormLayout, QLineEdit,
                            QFileDialog, QComboBox, QCheckBox)

from .widgets import EnvironmentSelectWidget, SegmentPairSelectWidget, RadioSelectWidget

class PDDialog(QDialog):
    def __init__(self, parent, corpus):
        QDialog.__init__(self, parent)

        layout = QVBoxLayout()



        pdFrame = QFrame()
        pdlayout = QHBoxLayout()

        self.segPairWidget = SegmentPairSelectWidget(corpus.inventory)

        pdlayout.addWidget(self.segPairWidget)

        self.envWidget = EnvironmentSelectWidget(corpus.inventory)
        pdlayout.addWidget(self.envWidget)


        optionLayout = QVBoxLayout()
        self.tierWidget = QComboBox()
        self.tierWidget.addItem('transcription')
        for t in corpus.tiers:
            self.tierWidget.addItem(t)

        tierFrame = QGroupBox('Tier')

        box = QVBoxLayout()
        box.addWidget(self.tierWidget)
        tierFrame.setLayout(box)

        optionLayout.addWidget(tierFrame)

        self.typeTokenWidget = RadioSelectWidget('Type or token',
                                                {'Count types': 'type',
                                                'Count tokens': 'token'})

        optionLayout.addWidget(self.typeTokenWidget)


        checkFrame = QGroupBox('Exhaustivity and uniqueness')

        checkLayout = QVBoxLayout()

        self.enforceCheck = QCheckBox('Enforce enviroment exhaustivity and uniqueness')

        checkLayout.addWidget(self.enforceCheck)

        checkFrame.setLayout(checkLayout)

        optionLayout.addWidget(checkFrame)

        optionFrame = QGroupBox('Options')

        optionFrame.setLayout(optionLayout)

        pdlayout.addWidget(optionFrame)

        pdFrame.setLayout(pdlayout)

        layout.addWidget(pdFrame)



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

        self.setWindowTitle('Predictability of distribution')
