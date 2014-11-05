import os
import codecs

from PyQt5.QtWidgets import (QDialog, QListWidget, QGroupBox, QHBoxLayout,
                            QVBoxLayout, QPushButton, QFrame, QGridLayout,
                            QRadioButton, QLabel, QFormLayout, QLineEdit,
                            QFileDialog, QComboBox, QMessageBox)

from collections import OrderedDict

from corpustools.config import config

from corpustools.corpus.io import (load_binary, download_binary, load_corpus_csv,
                                    save_binary,export_corpus_csv)

from .widgets import FileWidget, RadioSelectWidget, FeatureBox, SaveFileWidget

from .featuregui import FeatureSystemSelect

def get_corpora_list():
    corpus_dir = os.path.join(config['storage']['directory'],'CORPUS')
    corpora = [x.split('.')[0] for x in os.listdir(corpus_dir)]
    return corpora

def corpus_name_to_path(name):
    return os.path.join(config['storage']['directory'],'CORPUS',name+'.corpus')

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
        self.loadFromTextButton.clicked.connect(self.openTextWindow)
        self.removeButton.clicked.connect(self.removeCorpus)

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

        self.setWindowTitle('Load corpora')

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

    def openTextWindow(self):
        pass

    def removeCorpus(self):
        corpus = self.corporaList.currentItem().text()
        msgBox = QMessageBox(QMessageBox.Warning, "Remove corpus",
                "This will permanently remove '{}'.  Are you sure?".format(corpus), QMessageBox.NoButton, self)
        msgBox.addButton("Remove", QMessageBox.AcceptRole)
        msgBox.addButton("Cancel", QMessageBox.RejectRole)
        if msgBox.exec_() != QMessageBox.AcceptRole:
            return
        os.remove(corpus_name_to_path(corpus))
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
        self.corporaWidget = RadioSelectWidget('Select a corpus',
                                        OrderedDict([('Example toy corpus','example'),
                                        ('IPHOD','iphod')]))

        layout.addWidget(self.corporaWidget)

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

        self.setWindowTitle('Download corpora')

    def accept(self):
        name = self.corporaWidget.value()
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

        self.setLayout(layout)

        self.setWindowTitle('Create corpus from text')

class AddTierDialog(QDialog):
    def __init__(self, parent, corpus):
        QDialog.__init__(self, parent)

        self.corpus = corpus

        layout = QVBoxLayout()

        nameFrame = QGroupBox('Name of tier')
        self.nameEdit = QLineEdit()

        box = QFormLayout()
        box.addRow(self.nameEdit)

        nameFrame.setLayout(box)

        layout.addWidget(nameFrame)

        self.featureWidget = FeatureBox('Select features to define the tier',corpus.specifier.features)

        layout.addWidget(self.featureWidget)

        self.createButton = QPushButton('Create tier')
        self.previewButton = QPushButton('Preview tier')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.createButton)
        acLayout.addWidget(self.previewButton)
        acLayout.addWidget(self.cancelButton)
        self.createButton.clicked.connect(self.accept)
        self.previewButton.clicked.connect(self.preview)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Create tier')

    def preview(self):
        featureList = self.featureWidget.value()
        if not featureList:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify at least one feature.")
            return
        segList = self.corpus.features_to_segments(featureList)
        notInSegList = [x.symbol for x in self.corpus.inventory if x.symbol not in segList]

        reply = QMessageBox.information(self,
                "Tier preview", "Segments included: {}\nSegments excluded: {}".format(', '.join(segList),', '.join(notInSegList)))


    def accept(self):
        self.tierName = self.nameEdit.text()
        if self.tierName == '':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please enter a name for the tier.")
            return
        if self.tierName in self.corpus.tiers:

            msgBox = QMessageBox(QMessageBox.Warning, "Duplicate tiers",
                    "{} is already the name of a tier.  Overwrite?", QMessageBox.NoButton, self)
            msgBox.addButton("Overwrite", QMessageBox.AcceptRole)
            msgBox.addButton("Cancel", QMessageBox.RejectRole)
            if msgBox.exec_() != QMessageBox.AcceptRole:
                return

        self.featureList = self.featureWidget.value()
        if not self.featureList:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify at least one feature.")
            return
        QDialog.accept(self)

class RemoveTierDialog(QDialog):
    def __init__(self, parent, corpus):
        QDialog.__init__(self, parent)
        layout = QVBoxLayout()

        self.tierSelect = QListWidget()
        for t in corpus.tiers:
            self.tierSelect.addItem(t)

        layout.addWidget(self.tierSelect)

        self.removeSelectedButton = QPushButton('Remove selected tiers')
        self.removeAllButton = QPushButton('Remove all tiers')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.removeSelectedButton)
        acLayout.addWidget(self.removeAllButton)
        acLayout.addWidget(self.cancelButton)
        self.removeSelectedButton.clicked.connect(self.removeSelected)
        self.removeAllButton.clicked.connect(self.removeAll)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Remove tier')

    def removeSelected(self):
        selected = self.tierSelect.selectedItems()
        if not selected:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a tier to remove.")
            return
        self.tiers = [x.text() for x in selected]
        msgBox = QMessageBox(QMessageBox.Warning, "Remove tiers",
                "This will permanently remove the tiers: {}.  Are you sure?".format(', '.join(self.tiers)), QMessageBox.NoButton, self)
        msgBox.addButton("Remove", QMessageBox.AcceptRole)
        msgBox.addButton("Cancel", QMessageBox.RejectRole)
        if msgBox.exec_() != QMessageBox.AcceptRole:
            return

        QDialog.accept(self)

    def removeAll(self):
        if self.tierSelect.count() == 0:
            reply = QMessageBox.critical(self,
                    "Missing information", "There are no tiers to remove.")
            return
        self.tiers = [self.tierSelect.item(i).text() for i in range(self.tierSelect.count())]
        msgBox = QMessageBox(QMessageBox.Warning, "Remove tiers",
                "This will permanently remove the tiers: {}.  Are you sure?".format(', '.join(self.tiers)), QMessageBox.NoButton, self)
        msgBox.addButton("Remove", QMessageBox.AcceptRole)
        msgBox.addButton("Cancel", QMessageBox.RejectRole)
        if msgBox.exec_() != QMessageBox.AcceptRole:
            return

        QDialog.accept(self)

class CorpusFromCsvDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        layout = QVBoxLayout()

        formLayout = QFormLayout()


        self.pathWidget = FileWidget('Open corpus csv','Text files (*.txt *.csv)')
        self.pathWidget.pathEdit.textChanged.connect(self.updateName)

        formLayout.addRow(QLabel('Path to corpus'),self.pathWidget)

        self.nameEdit = QLineEdit()
        formLayout.addRow(QLabel('Name for corpus (auto-suggested)'),self.nameEdit)

        self.columnDelimiterEdit = QLineEdit()
        self.columnDelimiterEdit.setText(',')
        formLayout.addRow(QLabel('Column delimiter (enter \'t\' for tab)'),self.columnDelimiterEdit)

        self.transDelimiterEdit = QLineEdit()
        self.transDelimiterEdit.setText('.')
        formLayout.addRow(QLabel('Transcription delimiter'),self.transDelimiterEdit)

        self.featureSystemSelect = FeatureSystemSelect()

        formLayout.addRow(QLabel('Feature system (if applicable)'),self.featureSystemSelect)

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

        self.setWindowTitle('Create corpus from csv')

    def updateName(self):
        self.nameEdit.setText(os.path.split(self.pathWidget.value())[1].split('.')[0])

    def accept(self):
        path = self.pathWidget.value()
        if path == '':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a path to the csv file.")
            return
        if not os.path.exists(path):
            reply = QMessageBox.critical(self,
                    "Invalid information", "The specified file does not exist.")
            return

        name = self.nameEdit.text()
        if name == '':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a name to the csv file.")
            return
        if name in get_corpora_list():
            msgBox = QMessageBox(QMessageBox.Warning, "Duplicate name",
                    "A corpus named '{}' already exists.  Overwrite?".format(name), QMessageBox.NoButton, self)
            msgBox.addButton("Overwrite", QMessageBox.AcceptRole)
            msgBox.addButton("Abort", QMessageBox.RejectRole)
            if msgBox.exec_() != QMessageBox.AcceptRole:
                return
        colDelim = codecs.getdecoder("unicode_escape")(self.columnDelimiterEdit.text())[0]
        if len(colDelim) != 1:
            reply = QMessageBox.critical(self,
                    "Invalid information", "The column delimiter must be a single character.")
            return
        transDelim = self.transDelimiterEdit.text()

        featureSystem = self.featureSystemSelect.path()
        corpus,errors = load_corpus_csv(name, path, colDelim, transDelim,featureSystem)

        if errors:
            msgBox = QMessageBox(QMessageBox.Warning, "Missing symbols",
                    "{} were all missing from the feature system.  Would you like to initialize them as unspecified?".format(', '.join(errors.keys())), QMessageBox.NoButton, self)
            msgBox.addButton("Yes", QMessageBox.AcceptRole)
            msgBox.addButton("No", QMessageBox.RejectRole)
            if msgBox.exec_() == QMessageBox.AcceptRole:
                for s in errors:
                    corpus.specifier.add_segment(s.strip('\''),{})
                corpus.specifier.validate()
        save_binary(corpus,corpus_name_to_path(name))

        QDialog.accept(self)

class ExportCorpusDialog(QDialog):
    def __init__(self, parent, corpus):
        QDialog.__init__(self, parent)

        self.corpus = corpus

        layout = QVBoxLayout()

        inlayout = QFormLayout()

        self.pathWidget = SaveFileWidget('Select file location','Text files (*.txt *.csv)')

        inlayout.addRow('File name:',self.pathWidget)

        self.columnDelimiterEdit = QLineEdit()
        self.columnDelimiterEdit.setText(',')

        inlayout.addRow('Column delimiter:',self.columnDelimiterEdit)

        self.transDelimiterEdit = QLineEdit()
        self.transDelimiterEdit.setText('.')

        inlayout.addRow('Transcription delimiter:',self.transDelimiterEdit)

        inframe = QFrame()
        inframe.setLayout(inlayout)

        layout.addWidget(inframe)

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

        self.setWindowTitle('Export corpus')

    def accept(self):
        filename = self.pathWidget.value()

        if filename == '':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a path to save the corpus.")
            return

        colDelim = codecs.getdecoder("unicode_escape")(self.columnDelimiterEdit.text())[0]
        if len(colDelim) != 1:
            reply = QMessageBox.critical(self,
                    "Invalid information", "The column delimiter must be a single character.")
            return
        transDelim = self.transDelimiterEdit.text()

        export_corpus_csv(self.corpus,filename,colDelim,transDelim)

        QDialog.accept(self)
