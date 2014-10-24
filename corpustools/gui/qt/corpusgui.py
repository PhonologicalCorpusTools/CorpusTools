import os

from PyQt5.QtWidgets import (QDialog, QListWidget, QGroupBox, QHBoxLayout,
                            QVBoxLayout, QPushButton, QFrame, QGridLayout,
                            QRadioButton, QLabel, QFormLayout, QLineEdit,
                            QFileDialog, QComboBox)

from corpustools.config import config

from corpustools.corpus.io import load_binary, download_binary, load_corpus_csv, save_binary

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

        layout = QVBoxLayout()
        formLayout = QHBoxLayout()
        listFrame = QGroupBox('Available corpora')
        listLayout = QGridLayout()


        self.corporaList = QListWidget(self)
        listLayout.addWidget(self.corporaList)
        listFrame.setLayout(listLayout)
        self.getAvailableCorpora()

        formLayout.addWidget(listFrame)

        buttonLayout = QVBoxLayout()
        self.downloadButton = QPushButton('Download example corpora')
        self.loadFromCsvButton = QPushButton('Load corpus from pre-formatted text file')
        self.loadFromTextButton = QPushButton('Create corpus from running text')
        self.removeButton = QPushButton('Remove selected corpus')
        buttonLayout.addWidget(self.downloadButton)
        buttonLayout.addWidget(self.loadFromCsvButton)
        buttonLayout.addWidget(self.loadFromTextButton)
        buttonLayout.addWidget(self.removeButton)

        self.downloadButton.clicked.connect(self.openDownloadWindow)
        self.loadFromCsvButton.clicked.connect(self.openCsvWindow)

        buttonFrame = QFrame()
        buttonFrame.setLayout(buttonLayout)

        formLayout.addWidget(buttonFrame)


        formFrame = QFrame()
        formFrame.setLayout(formLayout)
        layout.addWidget(formFrame)

        self.acceptButton = QPushButton('Load selected corpus')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.cancelButton)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

    def accept(self):
        selected = [x.text() for x in self.corporaList.selectedItems()]
        if selected:
            self.corpus = load_binary(corpus_name_to_path(selected[0]))
            QDialog.accept(self)

    def openDownloadWindow(self):
        dialog = DownloadCorpusDialog(self)
        result = dialog.exec_()
        if result:
            self.getAvailableCorpora()

    def openCsvWindow(self):
        dialog = CorpusFromCsvDialog(self)
        result = dialog.exec_()
        if result:
            self.getAvailableCorpora()

    def getAvailableCorpora(self):
        self.corporaList.clear()
        corpora = get_corpora_list()
        for c in corpora:
            self.corporaList.addItem(c)


class DownloadCorpusDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)

        layout = QVBoxLayout()
        corporaFrame = QGroupBox('Select a corpus')

        self.exampleRadio = QRadioButton('Example toy corpus')
        self.iphodRadio = QRadioButton('IPHOD')
        hbox = QHBoxLayout()
        hbox.addWidget(self.exampleRadio)
        hbox.addWidget(self.iphodRadio)
        corporaFrame.setLayout(hbox)


        layout.addWidget(corporaFrame)

        self.acceptButton = QPushButton('Ok')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.cancelButton)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        layout.addWidget(QLabel("Please be patient. It can take up to 30 seconds to download a corpus.\nThis window will close when finished."))

        self.setLayout(layout)

    def accept(self):
        if self.exampleRadio.isChecked():
            name = 'example'
        elif self.iphodRadio.isChecked():
            name = 'iphod'
        download_binary(name,corpus_name_to_path(name))
        QDialog.accept(self)

class CorpusFromTextDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        layout = QVBoxLayout()

        self.acceptButton = QPushButton('Ok')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.cancelButton)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

class AddFeatureDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        layout = QVBoxLayout()

        self.acceptButton = QPushButton('Ok')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.cancelButton)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

class AddTierDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        layout = QVBoxLayout()

        self.acceptButton = QPushButton('Ok')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.cancelButton)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

class RemoveTierDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        layout = QVBoxLayout()

        self.acceptButton = QPushButton('Ok')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.cancelButton)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

class CorpusFromCsvDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        layout = QVBoxLayout()

        formLayout = QFormLayout()

        pathLayout = QHBoxLayout()
        self.pathEdit = QLineEdit()
        pathButton = QPushButton('Choose file...')
        pathButton.clicked.connect(self.pathSet)
        pathLayout.addWidget(self.pathEdit)
        pathLayout.addWidget(pathButton)
        pathFrame = QFrame()
        pathFrame.setLayout(pathLayout)

        formLayout.addRow(QLabel('Path to corpus'),pathFrame)

        self.nameEdit = QLineEdit()
        formLayout.addRow(QLabel('Name for corpus (auto-suggested)'),self.nameEdit)

        self.columnDelimiterEdit = QLineEdit()
        self.columnDelimiterEdit.setText(',')
        formLayout.addRow(QLabel('Column delimiter (enter \'t\' for tab)'),self.columnDelimiterEdit)

        self.transDelimiterEdit = QLineEdit()
        self.transDelimiterEdit.setText('.')
        formLayout.addRow(QLabel('Transcription delimiter'),self.transDelimiterEdit)

        self.featureSystemEdit = QComboBox()
        self.featureSystemEdit.addItem('')
        for fs in get_systems_list():
            self.featureSystemEdit.addItem(fs)

        formLayout.addRow(QLabel('Feature system (if applicable)'),self.featureSystemEdit)

        formFrame = QFrame()
        formFrame.setLayout(formLayout)
        layout.addWidget(formFrame)

        self.acceptButton = QPushButton('Ok')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.cancelButton)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

    def pathSet(self):
        filename = QFileDialog.getOpenFileName(self,'Open corpus csv', filter='Text files (*.txt *.csv)')
        if filename:
            self.pathEdit.setText(filename[0])
            self.nameEdit.setText(os.path.split(filename[0])[1].split('.')[0])

    def accept(self):
        path = self.pathEdit.text()
        name = self.nameEdit.text()
        colDelim = self.columnDelimiterEdit.text()
        transDelim = self.transDelimiterEdit.text()
        featureSystem = self.featureSystemEdit.currentText()
        if featureSystem:
            featureSystem = system_name_to_path(featureSystem)
        corpus,errors = load_corpus_csv(name, path, colDelim, transDelim,featureSystem)

        if errors:
            not_found = sorted(list(errors.keys()))
            msg1 = 'Not every symbol in your corpus can be interpreted with this feature system.'
            msg2 = 'The symbols that were missing were {}.\n'.format(', '.join(not_found))
            msg3 = 'Would you like to create all of them as unspecified? You can edit them later by going to Options-> View/change feature system...\nYou can also manually create the segments in there.'
            msg = '\n'.join([msg1, msg2, msg3])
            carry_on = MessageBox.askyesno(message=msg)
            if not carry_on:
                return
            for s in not_found:
                corpus.specifier.add_segment(s.strip('\''),{})
            corpus.specifier.validate()
        save_binary(corpus,corpus_name_to_path(name))

        QDialog.accept(self)



class DownloadFeatureMatrixDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        layout = QVBoxLayout()

        self.acceptButton = QPushButton('Ok')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.cancelButton)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

class EditFeatureMatrixDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        layout = QVBoxLayout()

        self.acceptButton = QPushButton('Ok')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.cancelButton)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

class EditSegmentDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        layout = QVBoxLayout()

        self.acceptButton = QPushButton('Ok')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.cancelButton)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)



