import os
import codecs
import string

from .imports import *

from collections import OrderedDict

from corpustools.config import config

from corpustools.corpus.classes import Attribute, Word

from corpustools.corpus.io import (load_binary, download_binary, load_corpus_csv,
                                    load_spelling_corpus, load_transcription_corpus,
                                    inspect_transcription_corpus,
                                    save_binary,export_corpus_csv, import_spontaneous_speech_corpus)

from .windows import FunctionWorker, DownloadWorker

from .widgets import (FileWidget, RadioSelectWidget, FeatureBox,
                    SaveFileWidget, DirectoryWidget, PunctuationWidget,
                    DigraphWidget, InventoryBox, AttributeFilterWidget,
                    TranscriptionWidget, SegFeatSelect, TierWidget)

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
                                                dialect = self.kwargs['dialect'],
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

class SubsetCorpusDialog(QDialog):
    def __init__(self, parent, corpus):
        QDialog.__init__(self, parent)

        self.corpus = corpus

        layout = QVBoxLayout()

        mainlayout = QFormLayout()

        self.nameEdit = QLineEdit()
        self.nameEdit.setText(corpus.name + '_subset')

        mainlayout.addRow(QLabel('Name for new corpus'),self.nameEdit)

        self.filterWidget = AttributeFilterWidget(corpus)

        mainlayout.addRow(self.filterWidget)

        layout.addLayout(mainlayout)

        self.acceptButton = QPushButton('Create subset corpus')
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
        filters = self.filterWidget.value()
        name = self.nameEdit.text()
        if name == '':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a name for the new corpus.")
            return None
        if len(filters) == 0:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify at least one filter.")
            return None

        if name in get_corpora_list():
            msgBox = QMessageBox(QMessageBox.Warning, "Duplicate name",
                    "A corpus named '{}' already exists.  Overwrite?".format(name), QMessageBox.NoButton, self)
            msgBox.addButton("Overwrite", QMessageBox.AcceptRole)
            msgBox.addButton("Abort", QMessageBox.RejectRole)
            if msgBox.exec_() != QMessageBox.AcceptRole:
                return
        new_corpus = self.corpus.subset(filters)
        new_corpus.name = name
        new_corpus.set_feature_matrix(self.corpus.specifier)
        save_binary(new_corpus,corpus_name_to_path(new_corpus.name))
        QDialog.accept(self)

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

        #self.wordDelimiter = QLineEdit()
        iolayout.addRow(QLabel('Word delimiter'),QLabel('All whitespace'))#self.wordDelimiter)

        self.punctuation = PunctuationWidget(string.punctuation, 'Punctuation to ignore')
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
                return None
        wordDelim = None#self.wordDelimiter.text()
        #if wordDelim == '':
        #    wordDelim = ' '

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
        if kwargs is None:
            return
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

        #self.wordDelimiter = PunctuationWidget(['space','tab'],'Word delimiters')
        iolayout.addRow(QLabel('Word delimiters'), QLabel('All whitespace'))

        self.punctuation = PunctuationWidget(string.punctuation,'Punctuation to ignore')

        iolayout.addRow(self.punctuation)

        ioframe = QGroupBox('Corpus details')
        ioframe.setLayout(iolayout)

        mainlayout.addWidget(ioframe)

        translayout = QFormLayout()

        self.featureSystem = FeatureSystemSelect()
        translayout.addRow(self.featureSystem)

        self.transDelimiter = PunctuationWidget(['.','-','='],'Transcription delimiters')
        self.transDelimiter.check()
        translayout.addRow(self.transDelimiter)

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
        #wordDelim = self.wordDelimiter.text()
        #if wordDelim == '' or wordDelim == ' ':
        wordDelim = None
        transDelim = self.transDelimiter.value()
        if transDelim == []:
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
        if kwargs is None:
            return
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

class InventorySummary(QWidget):
    def __init__(self, corpus, parent=None):
        QWidget.__init__(self,parent)

        self.corpus = corpus

        layout = QHBoxLayout()

        layout.setAlignment(Qt.AlignTop)

        self.segments = InventoryBox('Segments',self.corpus.inventory)
        self.segments.setExclusive(True)
        for b in self.segments.btnGroup.buttons():
            b.clicked.connect(self.summarizeSegment)

        layout.addWidget(self.segments)

        self.detailFrame = QFrame()

        layout.addWidget(self.detailFrame)

        self.setLayout(layout)

    def summarizeSegment(self):
        self.detailFrame.deleteLater()
        seg = self.sender().text()

        self.detailFrame = QGroupBox('Segment details')

        layout = QFormLayout()
        layout.setAlignment(Qt.AlignTop)

        freq_base = self.corpus.get_frequency_base('transcription', 'type', gramsize = 1,
                        probability = False)

        probs = self.corpus.get_frequency_base('transcription', 'type', gramsize = 1,
                        probability = True)

        layout.addRow(QLabel('Type frequency:'),
                            QLabel('{:,.1f} ({:.2%})'.format(
                                                freq_base[seg], probs[seg]
                                                )
                            ))

        freq_base = self.corpus.get_frequency_base('transcription', 'token', gramsize = 1,
                        probability = False)

        probs = self.corpus.get_frequency_base('transcription', 'token', gramsize = 1,
                        probability = True)

        layout.addRow(QLabel('Token frequency:'),
                            QLabel('{:,.1f} ({:.2%})'.format(
                                                    freq_base[seg], probs[seg]
                                                    )
                            ))

        self.detailFrame.setLayout(layout)

        self.layout().addWidget(self.detailFrame, alignment = Qt.AlignTop)


class AttributeSummary(QWidget):
    def __init__(self, corpus, parent=None):
        QWidget.__init__(self,parent)

        self.corpus = corpus

        layout = QFormLayout()

        self.columnSelect = QComboBox()
        for a in self.corpus.attributes:
            self.columnSelect.addItem(str(a))
        self.columnSelect.currentIndexChanged.connect(self.summarizeColumn)

        layout.addRow(QLabel('Column'),self.columnSelect)

        self.detailFrame = QFrame()

        layout.addRow(self.detailFrame)

        self.setLayout(layout)

        self.summarizeColumn()

    def summarizeColumn(self):
        for a in self.corpus.attributes:
            if str(a) == self.columnSelect.currentText():
                self.detailFrame.deleteLater()
                self.detailFrame = QFrame()
                layout = QFormLayout()
                layout.addRow(QLabel('Type:'), QLabel(a.att_type.title()))
                if a.att_type == 'numeric':
                    l = QLabel('{0[0]:,}-{0[1]:,}'.format(a.range))
                    layout.addRow(QLabel('Range:'), l)

                elif a.att_type == 'factor':
                    if len(a.range) > 300:
                        l = QLabel('Too many levels to display')
                    else:
                        l = QLabel(', '.join(sorted(a.range)))
                    l.setWordWrap(True)
                    layout.addRow(QLabel('Factor levels:'), l)

                elif a.att_type == 'tier':
                    if a.name == 'transcription':
                        layout.addRow(QLabel('Included segments:'), QLabel('All'))
                    else:
                        l = QLabel(', '.join(a.range))
                        l.setWordWrap(True)
                        layout.addRow(QLabel('Included segments:'), l)
                self.detailFrame.setLayout(layout)
                self.layout().addRow(self.detailFrame)


class CorpusSummary(QDialog):
    def __init__(self, parent, corpus):
        QDialog.__init__(self,parent)


        if hasattr(corpus,'lexicon'):
            c = corpus.lexicon

            if hasattr(corpus,'discourses'):
                speech_corpus = True
            else:
                speech_corpus = False
        else:
            c = corpus

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSizeConstraint(QLayout.SetFixedSize)

        main = QFormLayout()

        main.addRow(QLabel('Corpus:'),QLabel(corpus.name))

        if c.specifier is not None:
            main.addRow(QLabel('Feature system:'),QLabel(c.specifier.name))
        else:
            main.addRow(QLabel('Feature system:'),QLabel('None'))

        main.addRow(QLabel('Number of words types:'),QLabel(str(len(c))))

        detailTabs = QTabWidget()

        self.inventorySummary = InventorySummary(c)

        detailTabs.addTab(self.inventorySummary,'Inventory')

        self.attributeSummary = AttributeSummary(c)

        detailTabs.addTab(self.attributeSummary,'Columns')
        detailTabs.currentChanged.connect(self.hideWidgets)

        main.addRow(detailTabs)

        mainFrame = QFrame()
        mainFrame.setLayout(main)

        layout.addWidget(mainFrame, alignment = Qt.AlignCenter)

        self.doneButton = QPushButton('Done')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.doneButton)
        self.doneButton.clicked.connect(self.accept)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)
        self.setWindowTitle('Corpus summary')

    def hideWidgets(self,index):
        return
        if index == 0:
            self.inventorySummary.hide()
            self.attributeSummary.hide()
        elif index == 1:
            self.inventorySummary.hide()
            self.attributeSummary.show()
        self.adjustSize()



class AddWordDialog(QDialog):
    def __init__(self, parent, corpus, word = None):
        QDialog.__init__(self,parent)
        self.corpus = corpus

        layout = QVBoxLayout()
        layout.setSizeConstraint(QLayout.SetFixedSize)

        main = QFormLayout()

        self.edits = {}

        for a in self.corpus.attributes:
            if a.att_type == 'tier' and a.name == 'transcription':
                self.edits[a.name] = TranscriptionWidget('Transcription',self.corpus.inventory)
                self.edits[a.name].transcriptionChanged.connect(self.updateTiers)
                main.addRow(self.edits[a.name])
            elif a.att_type == 'tier':
                self.edits[a.name] = QLabel('Empty')
                main.addRow(QLabel(str(a)),self.edits[a.name])
            elif a.att_type == 'spelling':
                self.edits[a.name] = QLineEdit()
                main.addRow(QLabel(str(a)),self.edits[a.name])
            elif a.att_type == 'numeric':
                self.edits[a.name] = QLineEdit()
                self.edits[a.name].setText('0')
                main.addRow(QLabel(str(a)),self.edits[a.name])
            elif a.att_type == 'factor':
                self.edits[a.name] = QLineEdit()
                main.addRow(QLabel(str(a)),self.edits[a.name])
            else:
                print(a.name)
                print(str(a))
            if word is not None:
                self.edits[a.name].setText(str(getattr(word,a.name)))

        mainFrame = QFrame()
        mainFrame.setLayout(main)

        layout.addWidget(mainFrame)
        if word is None:
            self.createButton = QPushButton('Create word')
            self.setWindowTitle('Create word')
        else:
            self.createButton = QPushButton('Save word changes')
            self.setWindowTitle('Edit word')
        self.createButton.setAutoDefault(True)
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.createButton)
        acLayout.addWidget(self.cancelButton)
        self.createButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

    def updateTiers(self, new_transcription):
        transcription = new_transcription.split('.')
        for a in self.corpus.attributes:
            if a.att_type != 'tier':
                continue
            if a.name == 'transcription':
                continue
            if a.name not in self.edits:
                continue
            text = '.'.join([x for x in transcription if x in a.range])
            if text == '':
                text = 'Empty'
            self.edits[a.name].setText(text)

    def accept(self):

        kwargs = {}

        for a in self.corpus.attributes:
            if a.att_type == 'tier':
                text = self.edits[a.name].text()
                if text == 'Empty':
                    text = ''
                kwargs[a.name] = [x for x in text.split('.') if x != '']
                #if not kwargs[a.name]:
                #    reply = QMessageBox.critical(self,
                #            "Missing information", "Words must have a Transcription.".format(str(a)))
                #    return

                for i in kwargs[a.name]:
                    if i not in self.corpus.inventory:
                        reply = QMessageBox.critical(self,
                            "Invalid information", "The column '{}' must contain only symbols in the corpus' inventory.".format(str(a)))
                        return
            elif a.att_type == 'spelling':
                kwargs[a.name] = self.edits[a.name].text()
                if kwargs[a.name] == '' and a.name == 'spelling':
                    kwargs[a.name] = None
                #if not kwargs[a.name] and a.name == 'spelling':
                #    reply = QMessageBox.critical(self,
                #            "Missing information", "Words must have a spelling.".format(str(a)))
                #    return
            elif a.att_type == 'numeric':
                try:
                    kwargs[a.name] = float(self.edits[a.name].text())
                except ValueError:
                    reply = QMessageBox.critical(self,
                            "Invalid information", "The column '{}' must be a number.".format(str(a)))
                    return

            elif a.att_type == 'factor':
                kwargs[a.name] = self.edits[a.name].text()
        self.word = Word(**kwargs)
        QDialog.accept(self)

class AddCountColumnDialog(QDialog):
    def __init__(self, parent, corpus):
        QDialog.__init__(self,parent)
        self.corpus = corpus

        layout = QVBoxLayout()

        main = QFormLayout()

        self.nameWidget = QLineEdit()

        main.addRow('Name of column',self.nameWidget)

        self.tierWidget = TierWidget(self.corpus)

        main.addRow('Tier to count on',self.tierWidget)

        self.segmentSelect = SegFeatSelect(self.corpus,'Segment selection')

        main.addRow(self.segmentSelect)


        mainFrame = QFrame()
        mainFrame.setLayout(main)

        layout.addWidget(mainFrame)

        self.createButton = QPushButton('Add count column')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.createButton)
        acLayout.addWidget(self.cancelButton)
        self.createButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Add count column')

    def accept(self):
        name = self.nameWidget.text()
        self.attribute = Attribute(name.lower().replace(' ',''),'numeric',name)
        if name == '':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please enter a name for the tier.")
            return
        elif self.attribute.name in self.corpus.basic_attributes:
            reply = QMessageBox.critical(self,
                    "Invalid information", "The name '{}' overlaps with a protected column.".format(name))
            return
        elif self.attribute in self.corpus.attributes:

            msgBox = QMessageBox(QMessageBox.Warning, "Duplicate tiers",
                    "'{}' is already the name of a tier.  Overwrite?".format(name), QMessageBox.NoButton, self)
            msgBox.addButton("Overwrite", QMessageBox.AcceptRole)
            msgBox.addButton("Cancel", QMessageBox.RejectRole)
            if msgBox.exec_() != QMessageBox.AcceptRole:
                return

        self.sequenceType = self.tierWidget.value()

        self.segList = self.segmentSelect.segments()

        QDialog.accept(self)


class AddColumnDialog(QDialog):
    def __init__(self, parent, corpus, attribute = None):
        QDialog.__init__(self,parent)
        self.corpus = corpus

        layout = QVBoxLayout()

        main = QFormLayout()

        self.nameWidget = QLineEdit()

        main.addRow('Name of column',self.nameWidget)

        self.typeWidget = QComboBox()
        for at in Attribute.ATT_TYPES:
            if at == 'tier':
                continue
            self.typeWidget.addItem(at.title())
        self.typeWidget.currentIndexChanged.connect(self.updateDefault)

        main.addRow('Type of column',self.typeWidget)

        self.defaultWidget = QLineEdit()

        main.addRow('Default value',self.defaultWidget)


        mainFrame = QFrame()
        mainFrame.setLayout(main)

        layout.addWidget(mainFrame)

        self.createButton = QPushButton('Add column')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.createButton)
        acLayout.addWidget(self.cancelButton)
        self.createButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Add column')

    def updateDefault(self):
        if self.typeWidget.currentText().lower() == 'numeric':
            self.defaultWidget.setText('0')
        else:
            self.defaultWidget.setText('')

    def accept(self):
        name = self.nameWidget.text()
        at = self.typeWidget.currentText().lower()
        dv = self.defaultWidget.text()
        self.attribute = Attribute(name.lower().replace(' ',''),at,name)
        if name == '':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please enter a name for the tier.")
            return
        elif self.attribute.name in self.corpus.basic_attributes:
            reply = QMessageBox.critical(self,
                    "Invalid information", "The name '{}' overlaps with a protected column.".format(name))
            return
        elif self.attribute in self.corpus.attributes:

            msgBox = QMessageBox(QMessageBox.Warning, "Duplicate tiers",
                    "'{}' is already the name of a tier.  Overwrite?".format(name), QMessageBox.NoButton, self)
            msgBox.addButton("Overwrite", QMessageBox.AcceptRole)
            msgBox.addButton("Cancel", QMessageBox.RejectRole)
            if msgBox.exec_() != QMessageBox.AcceptRole:
                return
        if at == 'numeric':
            try:
                dv = float(dv)
            except ValueError:
                reply = QMessageBox.critical(self,
                        "Invalid information", "The default value for numeric columns must be a number")
                return
        self.attribute.default_value = dv
        QDialog.accept(self)


class AddAbstractTierDialog(QDialog):
    def __init__(self, parent, corpus):
        QDialog.__init__(self,parent)
        self.corpus = corpus

        layout = QVBoxLayout()

        main = QFormLayout()

        self.cvradio = QRadioButton('CV skeleton')
        self.cvradio.click()
        main.addWidget(self.cvradio)

        mainFrame = QFrame()
        mainFrame.setLayout(main)

        layout.addWidget(mainFrame)

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

        self.setWindowTitle('Create abstract tier')

    def preview(self):
        if self.cvradio.isChecked():
            segList = {'C' : [x.symbol for x in self.corpus.inventory
                                    if x.category is not None
                                    and x.category[0] == 'Consonant'],
                        'V' : [x.symbol for x in self.corpus.inventory
                                    if x.category is not None
                                    and x.category[0] != 'Consonant'],
                                    }
        preview = "The following abstract symbols correspond to the following segments:\n"
        for k,v in segList.items():
            preview += '{}: {}\n'.format(k,', '.join(v))
        reply = QMessageBox.information(self,
                "Tier preview", preview)


    def accept(self):
        if self.cvradio.isChecked():
            tierName = 'CV skeleton'
            self.attribute = Attribute('cvskeleton','factor','CV skeleton')
            self.segList = {'C' : [x.symbol for x in self.corpus.inventory
                                    if x.category is not None
                                    and x.category[0] == 'Consonant'],
                        'V' : [x.symbol for x in self.corpus.inventory
                                    if x.category is not None
                                    and x.category[0] != 'Consonant'],
                                    }

        if tierName == '':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please enter a name for the tier.")
            return
        if self.attribute.name in self.corpus.basic_attributes:
            reply = QMessageBox.critical(self,
                    "Invalid information", "The name '{}' overlaps with a protected column.".format(tierName))
            return
        elif self.attribute in self.corpus.attributes:

            msgBox = QMessageBox(QMessageBox.Warning, "Duplicate tiers",
                    "'{}' is already the name of a tier.  Overwrite?".format(tierName), QMessageBox.NoButton, self)
            msgBox.addButton("Overwrite", QMessageBox.AcceptRole)
            msgBox.addButton("Cancel", QMessageBox.RejectRole)
            if msgBox.exec_() != QMessageBox.AcceptRole:
                return

        QDialog.accept(self)

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

        self.createType = QComboBox()
        self.createType.addItem('Segments')
        if self.corpus.specifier is not None:
            self.createType.addItem('Features')
        else:
            layout.addWidget(QLabel('Features for tier creation are not available without a feature system.'))

        self.createType.currentIndexChanged.connect(self.generateFrames)

        layout.addWidget(QLabel('Basis for creating tier:'))
        layout.addWidget(self.createType, alignment = Qt.AlignLeft)
        self.createFrame = QFrame()
        createLayout = QVBoxLayout()
        self.createWidget = InventoryBox('Segments to define the tier',self.corpus.inventory)

        createLayout.addWidget(self.createWidget)

        self.createFrame.setLayout(createLayout)

        layout.addWidget(self.createFrame)

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

    def createFeatureFrame(self):
        self.createWidget.deleteLater()

        self.createWidget = FeatureBox('Features to define the tier',self.corpus.inventory)
        self.createFrame.layout().addWidget(self.createWidget)

    def createSegmentFrame(self):
        self.createWidget.deleteLater()

        self.createWidget = InventoryBox('Segments to define the tier',self.corpus.inventory)
        self.createFrame.layout().addWidget(self.createWidget)

    def generateFrames(self,ind=0):
        if self.createType.currentText() == 'Segments':
            self.createSegmentFrame()
        elif self.createType.currentText() == 'Features':
            self.createFeatureFrame()

    def preview(self):
        createType = self.createType.currentText()
        createList = self.createWidget.value()
        if not createList:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify at least one {}.".format(createType[:-1].lower()))
            return
        if createType == 'Features':
            createList = createList[1:-1]
            segList = self.corpus.features_to_segments(createList)
        else:
            segList = createList
        notInSegList = [x.symbol for x in self.corpus.inventory if x.symbol not in segList]

        reply = QMessageBox.information(self,
                "Tier preview", "Segments included: {}\nSegments excluded: {}".format(', '.join(segList),', '.join(notInSegList)))


    def accept(self):
        tierName = self.nameEdit.text()
        self.attribute = Attribute(tierName.lower().replace(' ',''),'tier',tierName)
        if tierName == '':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please enter a name for the tier.")
            return
        elif self.attribute.name in self.corpus.basic_attributes:
            reply = QMessageBox.critical(self,
                    "Invalid information", "The name '{}' overlaps with a protected column.".format(tierName))
            return
        elif self.attribute in self.corpus.attributes:

            msgBox = QMessageBox(QMessageBox.Warning, "Duplicate tiers",
                    "'{}' is already the name of a tier.  Overwrite?".format(tierName), QMessageBox.NoButton, self)
            msgBox.addButton("Overwrite", QMessageBox.AcceptRole)
            msgBox.addButton("Cancel", QMessageBox.RejectRole)
            if msgBox.exec_() != QMessageBox.AcceptRole:
                return
        createType = self.createType.currentText()
        createList = self.createWidget.value()
        if not createList:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify at least one {}.".format(createType[:-1].lower()))
            return
        if createType == 'Features':
            createList = createList[1:-1]
            self.segList = self.corpus.features_to_segments(createList)
        else:
            self.segList = createList
        QDialog.accept(self)

class RemoveAttributeDialog(QDialog):
    def __init__(self, parent, corpus):
        QDialog.__init__(self, parent)
        layout = QVBoxLayout()

        self.tierSelect = QListWidget()
        self.tierSelect.setSelectionMode(QAbstractItemView.ExtendedSelection)
        for t in corpus.attributes:
            if t in corpus.basic_attributes:
                continue
            self.tierSelect.addItem(t.display_name)

        layout.addWidget(self.tierSelect)

        self.removeSelectedButton = QPushButton('Remove selected columns')
        self.removeAllButton = QPushButton('Remove all non-essential columns')
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
                    "Missing information", "Please specify a column to remove.")
            return
        self.tiers = [x.text() for x in selected]
        msgBox = QMessageBox(QMessageBox.Warning, "Remove columns",
                "This will permanently remove the columns: {}.  Are you sure?".format(', '.join(self.tiers)), QMessageBox.NoButton, self)
        msgBox.addButton("Remove", QMessageBox.AcceptRole)
        msgBox.addButton("Cancel", QMessageBox.RejectRole)
        if msgBox.exec_() != QMessageBox.AcceptRole:
            return

        QDialog.accept(self)

    def removeAll(self):
        if self.tierSelect.count() == 0:
            reply = QMessageBox.critical(self,
                    "Missing information", "There are no columns to remove.")
            return
        self.tiers = [self.tierSelect.item(i).text() for i in range(self.tierSelect.count())]
        msgBox = QMessageBox(QMessageBox.Warning, "Remove columns",
                "This will permanently remove the columns: {}.  Are you sure?".format(', '.join(self.tiers)), QMessageBox.NoButton, self)
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
        self.columnDelimiterEdit.setText('\t')
        formLayout.addRow(QLabel('Column delimiter'),self.columnDelimiterEdit)

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
        corpus = load_corpus_csv(name, path, colDelim, transDelim, featureSystem)
        errors = corpus.check_coverage()
        if errors:
            msgBox = QMessageBox(QMessageBox.Warning, "Missing symbols",
                    "{} were all missing from the feature system.  Would you like to initialize them as unspecified?".format(', '.join(errors)), QMessageBox.NoButton, self)
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
        self.dialectWidget = QComboBox()
        self.dialectWidget.addItem('TextGrid')
        self.dialectWidget.addItem('TIMIT')
        self.dialectWidget.addItem('Buckeye')
        inlayout.addRow('Corpus file set up:',self.dialectWidget)

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
        self.thread.setParams({'directory':self.directoryWidget.value(),
                            'dialect':self.dialectWidget.currentText().lower()})

        self.thread.start()

        result = self.progressDialog.exec_()

        self.progressDialog.reset()
        if result:
            if self.corpus is not None:
                save_binary(self.corpus,corpus_name_to_path(self.corpus.name))
            QDialog.accept(self)

