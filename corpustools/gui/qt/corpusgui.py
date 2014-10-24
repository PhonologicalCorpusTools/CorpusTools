import os

from PyQt5.QtWidgets import (QDialog, QListWidget, QGroupBox, QHBoxLayout,
                            QVBoxLayout, QPushButton, QFrame, QGridLayout)

from corpustools.config import config

from corpustools.corpus.io import load_binary

def get_corpora_list():
    corpus_dir = os.path.join(config['storage']['directory'],'CORPUS')
    corpora = [x.split('.')[0] for x in os.listdir(corpus_dir)]
    return corpora

def get_systems_list():
    system_dir = os.path.join(config['storage']['directory'],'FEATURE')
    systems = [x.split('.')[0] for x in os.listdir(system_dir)]
    return systems

def corpus_name_to_path(name):
    return os.path.join(config['storage']['directory'],'CORPUS',name+'.corpus')

def system_name_to_path(name):
    return os.path.join(config['storage']['directory'],'FEATURE',name+'.feature')

class CorpusLoadDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.corpus = None

        layout = QHBoxLayout()
        listFrame = QGroupBox('Available corpora')
        listLayout = QGridLayout()


        self.corporaList = QListWidget(self)
        listLayout.addWidget(self.corporaList)
        listFrame.setLayout(listLayout)
        self.getAvailableCorpora()

        layout.addWidget(listFrame)

        buttonLayout = QVBoxLayout()
        self.loadButton = QPushButton('Load selected corpus')
        self.downloadButton = QPushButton('Download example corpora')
        self.loadFromCsvButton = QPushButton('Load corpus from pre-formatted text file')
        self.loadFromTextButton = QPushButton('Create corpus from running text')
        self.removeButton = QPushButton('Remove selected corpus')
        self.cancelButton = QPushButton('Cancel')
        buttonLayout.addWidget(self.loadButton)
        buttonLayout.addWidget(self.downloadButton)
        buttonLayout.addWidget(self.loadFromCsvButton)
        buttonLayout.addWidget(self.loadFromTextButton)
        buttonLayout.addWidget(self.removeButton)
        buttonLayout.addWidget(self.cancelButton)

        self.loadButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        buttonFrame = QFrame()
        buttonFrame.setLayout(buttonLayout)

        layout.addWidget(buttonFrame)

        self.setLayout(layout)

    def accept(self):
        selected = [x.text() for x in self.corporaList.selectedItems()]
        if selected:
            self.corpus = load_binary(corpus_name_to_path(selected[0]))
            QDialog.accept(self)



    def getAvailableCorpora(self):
        self.corporaList.clear()
        corpora = get_corpora_list()
        for c in corpora:
            self.corporaList.addItem(c)


class DownloadCorpusDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)

class CorpusFromTextDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)

class AddFeatureDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)

class AddTierDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)

class RemoveTierDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)

class CorpusFromCsvDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)

class DownloadFeatureMatrixDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)

class EditFeatureMatrixDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)

class EditSegmentDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)



