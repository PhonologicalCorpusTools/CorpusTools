import os
import codecs

from .imports import *

from collections import OrderedDict

from corpustools.config import config

from corpustools.corpus.io import (load_binary, download_binary, load_corpus_csv,
                                    load_spelling_corpus, load_transcription_corpus,
                                    inspect_transcription_corpus,
                                    save_binary,export_corpus_csv, import_spontaneous_speech_corpus)

from .windows import FunctionWorker, DownloadWorker

from .widgets import (FileWidget, RadioSelectWidget, FeatureBox,
                    SaveFileWidget, DirectoryWidget, PunctuationWidget,
                    DigraphWidget)

from corpustools.gui.qt.featuregui import FeatureSystemSelect

def get_corpora_list():
    corpus_dir = os.path.join(config['storage']['directory'],'CORPUS')
    corpora = [x.split('.')[0] for x in os.listdir(corpus_dir)]
    return corpora

def corpus_name_to_path(name):
    return os.path.join(config['storage']['directory'],'CORPUS',name+'.corpus')


class CorpusSelect(QComboBox):
    def __init__(self, parent=None):
        QComboBox.__init__(self,parent)

        self.addItem('None')

        for i,s in enumerate(get_corpora_list()):
            self.addItem(s)

    def value(self):
        val = self.currentText()
        if val == 'None':
            return ''
        return val

    def path(self):
        if self.value() != '':
            return corpus_name_to_path(self.value())
        return None

class LoadWorker(FunctionWorker):
    def run(self):
        if self.stopCheck():
            return
        self.results = load_binary(self.kwargs['path'])
        if self.stopCheck():
            return
        self.dataReady.emit(self.results)

class SpontaneousLoadWorker(FunctionWorker):
    def run(self):

        corpus = import_spontaneous_speech_corpus(self.kwargs['directory'],
                                                stop_check=self.kwargs['stop_check'],
                                                call_back = self.kwargs['call_back'])
        self.dataReady.emit(corpus)

class SpellingLoadWorker(FunctionWorker):
    def run(self):

        corpus = load_spelling_corpus(**self.kwargs)
        self.dataReady.emit(corpus)

class TranscriptionLoadWorker(FunctionWorker):
    def run(self):

        corpus = load_transcription_corpus(**self.kwargs)
        self.dataReady.emit(corpus)

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

        self.corporaList.doubleClicked.connect(self.accept)

        formLayout.addWidget(listFrame)

        buttonLayout = QVBoxLayout()
        self.downloadButton = QPushButton('Download example corpora')
        self.loadFromCsvButton = QPushButton('Load corpus from pre-formatted text file')
        self.loadFromSpellingTextButton = QPushButton('Create corpus from running text (orthography)')
        self.loadFromTranscriptionTextButton = QPushButton('Create corpus from running text (transcribed)')
        self.importSpontaneousButton = QPushButton('Import spontaneous speech corpus')
        self.removeButton = QPushButton('Remove selected corpus')
        buttonLayout.addWidget(self.downloadButton)
        buttonLayout.addWidget(self.loadFromCsvButton)
        buttonLayout.addWidget(self.loadFromSpellingTextButton)
        buttonLayout.addWidget(self.loadFromTranscriptionTextButton)
        buttonLayout.addWidget(self.importSpontaneousButton)
        buttonLayout.addWidget(self.removeButton)

        self.downloadButton.clicked.connect(self.openDownloadWindow)
        self.loadFromCsvButton.clicked.connect(self.openCsvWindow)
        self.loadFromSpellingTextButton.clicked.connect(self.openSpellingTextWindow)
        self.loadFromTranscriptionTextButton.clicked.connect(self.openTranscriptionTextWindow)
        self.importSpontaneousButton.clicked.connect(self.importSpontaneousWindow)
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

        self.thread = LoadWorker()

        self.progressDialog = QProgressDialog('Loading...','Cancel',0,0,self)
        self.progressDialog.setWindowTitle('Loading corpus')
        self.progressDialog.canceled.connect(self.thread.stop)
        self.thread.dataReady.connect(self.setResults)
        self.thread.dataReady.connect(self.progressDialog.accept)

    def setResults(self, results):
        self.corpus = results

    def accept(self):
        selected = [x.text() for x in self.corporaList.selectedItems()]
        if selected:
            self.thread.setParams({'path':corpus_name_to_path(selected[0])})

            self.thread.start()

            result = self.progressDialog.exec_()

            self.progressDialog.reset()
            if result:
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

    def importSpontaneousWindow(self):
        dialog = SpontaneousSpeechDialog(self)
        if dialog.exec_():
            self.getAvailableCorpora()

    def openSpellingTextWindow(self):
        dialog = CorpusFromSpellingTextDialog(self)
        if dialog.exec_():
            self.getAvailableCorpora()

    def openTranscriptionTextWindow(self):
        dialog = CorpusFromTranscriptionTextDialog(self)
        if dialog.exec_():
            self.getAvailableCorpora()

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

        self.thread = DownloadWorker()

        self.progressDialog = QProgressDialog('Downloading...','Cancel',0,100,self)
        self.progressDialog.setWindowTitle('Download corpus')
        self.progressDialog.setAutoClose(False)
        self.progressDialog.setAutoReset(False)
        self.progressDialog.canceled.connect(self.thread.stop)
        self.thread.updateProgress.connect(self.updateProgress)
        self.thread.updateProgressText.connect(self.updateProgressText)
        self.thread.finished.connect(self.progressDialog.accept)

    def updateProgressText(self, text):
        self.progressDialog.setLabelText(text)
        self.progressDialog.reset()

    def updateProgress(self,progress):
        self.progressDialog.setValue(progress)
        self.progressDialog.repaint()

    def accept(self):
        name = self.corporaWidget.value()
        if name in get_corpora_list():
            msgBox = QMessageBox(QMessageBox.Warning, "Overwrite corpus",
                    "The corpus '{}' is already available.  Would you like to overwrite it?".format(name), QMessageBox.NoButton, self)
            msgBox.addButton("Overwrite", QMessageBox.AcceptRole)
            msgBox.addButton("Cancel", QMessageBox.RejectRole)
            if msgBox.exec_() != QMessageBox.AcceptRole:
                return
        self.thread.setParams({'name':name,'path':corpus_name_to_path(name)})

        self.thread.start()

        result = self.progressDialog.exec_()

        self.progressDialog.reset()
        if result:
            QDialog.accept(self)

class CorpusFromSpellingTextDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        layout = QVBoxLayout()

        mainlayout = QHBoxLayout()

        iolayout = QFormLayout()

        self.pathWidget = FileWidget('Open corpus text','Text files (*.txt)')
        self.pathWidget.pathEdit.textChanged.connect(self.updateName)

        iolayout.addRow(QLabel('Path to corpus'),self.pathWidget)

        self.nameEdit = QLineEdit()
        iolayout.addRow(QLabel('Name for corpus'),self.nameEdit)

        self.wordDelimiter = QLineEdit()
        iolayout.addRow(QLabel('Word delimiter'),self.wordDelimiter)

        self.punctuation = PunctuationWidget()
        iolayout.addRow(self.punctuation)

        ioframe = QGroupBox('Corpus details')
        ioframe.setLayout(iolayout)

        mainlayout.addWidget(ioframe)

        translayout = QFormLayout()

        self.supportCorpus = CorpusSelect()
        translayout.addRow(QLabel('Corpus to look up transcriptions'),self.supportCorpus)

        self.ignoreCase = QCheckBox()
        translayout.addRow(QLabel('Ignore case'),self.ignoreCase)

        transframe = QGroupBox('Transcription details')
        transframe.setLayout(translayout)

        mainlayout.addWidget(transframe)

        mainframe = QFrame()
        mainframe.setLayout(mainlayout)
        layout.addWidget(mainframe)

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

        self.setWindowTitle('Create corpus from orthographic text')

        self.thread = SpellingLoadWorker()

        self.progressDialog = QProgressDialog('Importing...','Cancel',0,100,self)
        self.progressDialog.setWindowTitle('Importing orthographic text')
        self.progressDialog.setAutoClose(False)
        self.progressDialog.setAutoReset(False)
        self.progressDialog.canceled.connect(self.thread.stop)
        self.thread.updateProgress.connect(self.updateProgress)
        self.thread.updateProgressText.connect(self.updateProgressText)
        self.thread.dataReady.connect(self.setResults)
        self.thread.dataReady.connect(self.progressDialog.accept)

    def updateProgressText(self, text):
        self.progressDialog.setLabelText(text)
        self.progressDialog.reset()

    def updateProgress(self,progress):
        self.progressDialog.setValue(progress)
        self.progressDialog.repaint()

    def setResults(self, results):
        self.corpus = results

    def generateKwargs(self):
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
        wordDelim = self.wordDelimiter.text()
        if wordDelim == '':
            wordDelim = ' '

        supportCorpus = self.supportCorpus.path()
        ignore_list = self.punctuation.value()

        kwargs = {'corpus_name':name,
                    'path':path,
                    'delimiter': wordDelim,
                    'ignore_list': ignore_list,
                    'ignore_case': self.ignoreCase.isChecked(),
                    'support_corpus_path': supportCorpus}
        return kwargs

    def accept(self):
        kwargs = self.generateKwargs()
        self.thread.setParams(kwargs)

        self.thread.start()

        result = self.progressDialog.exec_()

        self.progressDialog.reset()
        if result:
            if self.corpus is not None:
                save_binary(self.corpus,corpus_name_to_path(self.corpus.name))
            QDialog.accept(self)

    def updateName(self):
        self.nameEdit.setText(os.path.split(self.pathWidget.value())[1].split('.')[0])

class CorpusFromTranscriptionTextDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.characters = set()
        layout = QVBoxLayout()

        mainlayout = QHBoxLayout()

        iolayout = QFormLayout()

        self.pathWidget = FileWidget('Open corpus text','Text files (*.txt)')
        self.pathWidget.pathEdit.textChanged.connect(self.updateName)
        self.pathWidget.pathEdit.textChanged.connect(self.getCharacters)

        iolayout.addRow(QLabel('Path to corpus'),self.pathWidget)

        self.nameEdit = QLineEdit()
        iolayout.addRow(QLabel('Name for corpus (auto-suggested)'),self.nameEdit)

        self.wordDelimiter = QLineEdit()
        iolayout.addRow(QLabel('Word delimiter'),self.wordDelimiter)

        self.punctuation = PunctuationWidget()
        iolayout.addRow(self.punctuation)

        ioframe = QGroupBox('Corpus details')
        ioframe.setLayout(iolayout)

        mainlayout.addWidget(ioframe)

        translayout = QFormLayout()

        self.featureSystem = FeatureSystemSelect()
        translayout.addRow(self.featureSystem)

        self.transDelimiter = QLineEdit()
        translayout.addRow(QLabel('Transcription delimiter'),self.transDelimiter)

        self.digraphs = DigraphWidget(self)
        translayout.addRow(self.digraphs)

        transframe = QGroupBox('Transcription details')
        transframe.setLayout(translayout)

        mainlayout.addWidget(transframe)

        mainframe = QFrame()
        mainframe.setLayout(mainlayout)
        layout.addWidget(mainframe)

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

        self.setWindowTitle('Create corpus from transcribed text')

        self.thread = TranscriptionLoadWorker()

        self.progressDialog = QProgressDialog('Loading...','Cancel',0,100,self)
        self.progressDialog.setWindowTitle('Loading transcribed text')
        self.progressDialog.setAutoClose(False)
        self.progressDialog.setAutoReset(False)
        self.progressDialog.canceled.connect(self.thread.stop)
        self.thread.updateProgress.connect(self.updateProgress)
        self.thread.updateProgressText.connect(self.updateProgressText)
        self.thread.dataReady.connect(self.setResults)
        self.thread.dataReady.connect(self.progressDialog.accept)

    def ignoreList(self):
        return self.punctuation.value()

    def delimiters(self):
        wordDelim = self.wordDelimiter.text()
        if wordDelim == '' or wordDelim == ' ':
            wordDelim = None
        transDelim = self.transDelimiter.text()
        if transDelim == '':
            transDelim = None
        return wordDelim, transDelim


    def getCharacters(self):
        path = self.pathWidget.value()
        if path != '' and os.path.exists(path):
            self.characters = inspect_transcription_corpus(path)
        else:
            self.characters = set()

    def updateProgressText(self, text):
        self.progressDialog.setLabelText(text)
        self.progressDialog.reset()

    def updateProgress(self,progress):
        self.progressDialog.setValue(progress)
        self.progressDialog.repaint()

    def setResults(self, results):
        self.corpus = results

    def generateKwargs(self):
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
        wordDelim, transDelim = self.delimiters()
        feature_system_path = self.featureSystem.path()
        ignore_list = self.punctuation.value()

        if name in get_corpora_list():
            msgBox = QMessageBox(QMessageBox.Warning, "Duplicate name",
                    "A corpus named '{}' already exists.  Overwrite?".format(name), QMessageBox.NoButton, self)
            msgBox.addButton("Overwrite", QMessageBox.AcceptRole)
            msgBox.addButton("Abort", QMessageBox.RejectRole)
            if msgBox.exec_() != QMessageBox.AcceptRole:
                return

        kwargs = {'corpus_name':name,
                    'path':path,
                    'delimiter': wordDelim,
                    'ignore_list': ignore_list,
                    'digraph_list': self.digraphs.value(),
                    'trans_delimiter': transDelim,
                    'feature_system_path': feature_system_path}
        return kwargs

    def accept(self):
        kwargs = self.generateKwargs()
        self.thread.setParams(kwargs)

        self.thread.start()

        result = self.progressDialog.exec_()

        self.progressDialog.reset()
        if result:
            if self.corpus is not None:
                save_binary(self.corpus,corpus_name_to_path(self.corpus.name))
            QDialog.accept(self)

    def updateName(self):
        self.nameEdit.setText(os.path.split(self.pathWidget.value())[1].split('.')[0])

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
        corpus = load_corpus_csv(name, path, colDelim, transDelim,featureSystem)
        errors = corpus.check_coverage()
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

class SpontaneousSpeechDialog(QDialog):
    def __init__(self,parent):
        QDialog.__init__(self,parent)
        self.corpus = None
        layout = QVBoxLayout()

        inlayout = QFormLayout()

        self.directoryWidget = DirectoryWidget()
        inlayout.addRow('Corpus directory:',self.directoryWidget)

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

        self.setWindowTitle('Import spontaneous speech corpus')

        self.thread = SpontaneousLoadWorker()

        self.progressDialog = QProgressDialog('Importing...','Cancel',0,100,self)
        self.progressDialog.setWindowTitle('Importing spontaneous speech corpus')
        self.progressDialog.setAutoClose(False)
        self.progressDialog.setAutoReset(False)
        self.progressDialog.canceled.connect(self.thread.stop)
        self.thread.updateProgress.connect(self.updateProgress)
        self.thread.updateProgressText.connect(self.updateProgressText)
        self.thread.dataReady.connect(self.setResults)
        self.thread.dataReady.connect(self.progressDialog.accept)

    def updateProgressText(self, text):
        self.progressDialog.setLabelText(text)
        self.progressDialog.reset()

    def updateProgress(self,progress):
        self.progressDialog.setValue(progress)
        self.progressDialog.repaint()

    def setResults(self, results):
        self.corpus = results

    def accept(self):
        self.thread.setParams({'directory':self.directoryWidget.value()})

        self.thread.start()

        result = self.progressDialog.exec_()

        self.progressDialog.reset()
        if result:
            if self.corpus is not None:
                save_binary(self.corpus,corpus_name_to_path(self.corpus.name))
            QDialog.accept(self)

