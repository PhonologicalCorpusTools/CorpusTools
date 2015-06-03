import os
import sys
import codecs
import string

from .imports import *

from collections import OrderedDict

from corpustools.exceptions import PCTError, PCTPythonError
from corpustools.decorators import check_for_errors

from corpustools.corpus.io import (load_binary, download_binary,
                                    save_binary,
                                    import_spontaneous_speech_corpus
                                    )
from corpustools.corpus.io.csv import (inspect_csv, load_corpus_csv,
                                    export_corpus_csv)

from corpustools.corpus.io.textgrid import (inspect_discourse_textgrid,
                                            load_discourse_textgrid)

from corpustools.corpus.io.text_ilg import (load_discourse_ilg,
                                        inspect_discourse_ilg)

from corpustools.corpus.io.text_spelling import (load_discourse_spelling,
                                                inspect_discourse_spelling)

from corpustools.corpus.io.text_transcription import (load_discourse_transcription,
                                                        inspect_discourse_transcription)

from corpustools.corpus.io.multiple_files import (load_discourse_multiple_files,
                                                    inspect_discourse_multiple_files)

from corpustools.corpus.io.helper import get_corpora_list, corpus_name_to_path

from .windows import FunctionWorker, DownloadWorker, PCTDialog

from .widgets import (FileWidget, RadioSelectWidget, FeatureBox,
                    SaveFileWidget, DirectoryWidget, PunctuationWidget,
                    DigraphWidget, InventoryBox, AttributeFilterWidget,
                    TranscriptionWidget, SegFeatSelect, TierWidget,
                    AttributeWidget, AnnotationTypeWidget,
                    CorpusSelect)

from .featuregui import FeatureSystemSelect
from .helpgui import HelpDialog


class LoadWorker(FunctionWorker):
    def run(self):
        time.sleep(0.1)
        if self.stopCheck():
            return
        try:
            self.results = load_binary(self.kwargs['path'])
        except PCTError as e:
            self.errorEncountered.emit(e)
            return
        except Exception as e:
            e = PCTPythonError(e)
            self.errorEncountered.emit(e)
            return
        if self.stopCheck():
            return
        self.dataReady.emit(self.results)

class LoadCorpusWorker(FunctionWorker):
    def run(self):
        time.sleep(0.1)
        textType = self.kwargs.pop('text_type')
        try:
            if textType == 'spelling':
                    corpus = load_discourse_spelling(**self.kwargs)
            elif textType == 'transcription':
                corpus = load_discourse_transcription(**self.kwargs)
            elif textType == 'ilg':
                corpus = load_discourse_ilg(**self.kwargs)
            elif textType == 'textgrid':
                corpus = load_discourse_textgrid(**self.kwargs)
            elif textType == 'csv':
                corpus = load_corpus_csv(**self.kwargs)
            elif textType in ['buckeye', 'timit']:
                self.kwargs['dialect'] = textType
                corpus = load_discourse_multiple_files(**self.kwargs)
        except PCTError as e:
            self.errorEncountered.emit(e)
            return
        except Exception as e:
            e = PCTPythonError(e)
            self.errorEncountered.emit(e)
            return
        self.dataReady.emit(corpus)


class CorpusLoadDialog(QDialog):
    def __init__(self, parent,settings):
        QDialog.__init__(self, parent)
        self.corpus = None
        self.settings = settings
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
        self.downloadButton.setAutoDefault(False)
        self.loadCorpusButton = QPushButton('Import corpus')
        self.loadCorpusButton.setAutoDefault(False)
        self.removeButton = QPushButton('Remove selected corpus')
        self.removeButton.setAutoDefault(False)
        buttonLayout.addWidget(self.downloadButton)
        buttonLayout.addWidget(self.loadCorpusButton)
        buttonLayout.addWidget(self.removeButton)

        self.downloadButton.clicked.connect(self.openDownloadWindow)
        self.loadCorpusButton.clicked.connect(self.openLoadWindow)
        self.removeButton.clicked.connect(self.removeCorpus)

        buttonFrame = QFrame()
        buttonFrame.setLayout(buttonLayout)

        formLayout.addWidget(buttonFrame)

        formFrame = QFrame()
        formFrame.setLayout(formLayout)
        layout.addWidget(formFrame)

        self.acceptButton = QPushButton('Load selected corpus')
        self.acceptButton.setDefault(True)
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
        self.progressDialog.setMinimumDuration(0)
        self.progressDialog.canceled.connect(self.thread.stop)
        self.thread.dataReady.connect(self.setResults)
        self.thread.dataReady.connect(self.progressDialog.accept)

    def setResults(self, results):
        self.corpus = results

    def accept(self):
        selected = [x.text() for x in self.corporaList.selectedItems()]
        if selected:
            self.thread.setParams({
                'path':corpus_name_to_path(
                            self.settings['storage'],selected[0])})

            self.thread.start()

            result = self.progressDialog.exec_()

            self.progressDialog.reset()
            if result:
                QDialog.accept(self)

    def openLoadWindow(self):
        dialog = LoadCorpusDialog(self, self.settings)
        result = dialog.exec_()
        if result:
            self.getAvailableCorpora()

    def openDownloadWindow(self):
        dialog = DownloadCorpusDialog(self, self.settings)
        result = dialog.exec_()
        if result:
            self.getAvailableCorpora()

    def removeCorpus(self):
        corpus = self.corporaList.currentItem().text()
        msgBox = QMessageBox(QMessageBox.Warning, "Remove corpus",
                "This will permanently remove '{}'.  Are you sure?".format(corpus), QMessageBox.NoButton, self)
        msgBox.addButton("Remove", QMessageBox.AcceptRole)
        msgBox.addButton("Cancel", QMessageBox.RejectRole)
        if msgBox.exec_() != QMessageBox.AcceptRole:
            return
        os.remove(corpus_name_to_path(self.settings['storage'],corpus))
        self.getAvailableCorpora()

    def getAvailableCorpora(self):
        self.corporaList.clear()
        corpora = get_corpora_list(self.settings['storage'])
        for c in corpora:
            self.corporaList.addItem(c)


class DownloadCorpusDialog(QDialog):
    def __init__(self, parent, settings):
        QDialog.__init__(self, parent)
        self.settings = settings
        layout = QVBoxLayout()
        self.corporaWidget = RadioSelectWidget('Select a corpus',
                                        OrderedDict([('Example toy corpus','example'),
                                        ('IPHOD','iphod')]))

        layout.addWidget(self.corporaWidget)

        self.acceptButton = QPushButton('Ok')
        self.cancelButton = QPushButton('Cancel')
        self.helpButton = QPushButton('Help')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.cancelButton)
        acLayout.addWidget(self.helpButton)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.helpButton.clicked.connect(self.help)

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

    def help(self):
        self.helpDialog = HelpDialog(self,name = 'loading corpora',
                                    section = 'using-a-built-in-corpus')
        self.helpDialog.exec_()

    def updateProgressText(self, text):
        self.progressDialog.setLabelText(text)
        self.progressDialog.reset()

    def updateProgress(self,progress):
        self.progressDialog.setValue(progress)
        self.progressDialog.repaint()

    def accept(self):
        name = self.corporaWidget.value()
        if name in get_corpora_list(self.settings['storage']):
            msgBox = QMessageBox(QMessageBox.Warning, "Overwrite corpus",
                    "The corpus '{}' is already available.  Would you like to overwrite it?".format(name), QMessageBox.NoButton, self)
            msgBox.addButton("Overwrite", QMessageBox.AcceptRole)
            msgBox.addButton("Cancel", QMessageBox.RejectRole)
            if msgBox.exec_() != QMessageBox.AcceptRole:
                return
        self.thread.setParams({'name':name,
                'path':corpus_name_to_path(self.settings['storage'],name)})

        self.thread.start()

        result = self.progressDialog.exec_()

        self.progressDialog.reset()
        if result:
            QDialog.accept(self)

class SupportCorpusWidget(QGroupBox):
    def __init__(self, settings, parent = None):
        QGroupBox.__init__(self, 'Support corpus', parent)
        self.supportCorpus = CorpusSelect(self, settings)

        layout = QFormLayout()
        layout.addRow(QLabel('Corpus to look up transcriptions'),self.supportCorpus)

        self.ignoreCase = QCheckBox()
        layout.addRow(QLabel('Ignore case for look up'),self.ignoreCase)

        self.setLayout(layout)

    def path(self):
        return self.supportCorpus.path()

    def value(self):
        return self.path(), self.ignoreCase.isChecked()


class LoadCorpusDialog(PCTDialog):
    supported_types = [(None, ''),('csv', 'Column-delimited file'),
                        ('running', 'Running text'),
                        ('ilg', 'Interlinear text'),
                        ('textgrid', 'TextGrid'),
                        ('multiple', 'Other standards'),]
    def __init__(self, parent, settings):
        PCTDialog.__init__(self, parent)
        self.settings = settings
        self.textType = None

        self.createWidgets()

        layout = QVBoxLayout()

        mainlayout = QHBoxLayout()

        iolayout = QFormLayout()

        pathlayout = QHBoxLayout()

        self.characters = set()
        self.pathWidget = FileWidget('Select file','Text files (*.txt *.csv *.TextGrid *.words *.wrds)')
        self.pathWidget.pathEdit.textChanged.connect(self.updateName)

        pathlayout.addWidget(QLabel('Source path'))
        pathlayout.addWidget(self.pathWidget)

        self.nameEdit = QLineEdit()
        pathlayout.addWidget(QLabel('Corpus name'))
        pathlayout.addWidget(self.nameEdit)

        pathframe = QFrame()
        pathframe.setLayout(pathlayout)

        iolayout.addRow(pathframe)

        #self.punctuation = PunctuationWidget(string.punctuation, 'Punctuation to ignore')
        #iolayout.addRow(self.punctuation)


        ioframe = QFrame()
        ioframe.setLayout(iolayout)

        mainlayout.addWidget(ioframe)

        self.tabWidget = QTabWidget()

        optionlayout = QFormLayout()

        csvFrame = QFrame()

        csvlayout = QFormLayout()
        csvlayout.addRow(QLabel('Column delimiter (auto-detected)'),self.columnDelimiterEdit)
        csvlayout.addRow(self.csvForceInspectButton)

        csvlayout.addRow(self.csvFeatureSystem)

        csvFrame.setLayout(csvlayout)
        self.tabWidget.addTab(csvFrame,'Column-delimited file')

        runningFrame = QFrame()
        runninglayout = QFormLayout()
        runninglayout.addRow('Text type', self.runningSelect)

        runninglayout.addRow(self.runningFeatureSystem)
        runninglayout.addRow(self.runningLookupWidget)
        runningFrame.setLayout(runninglayout)
        self.tabWidget.addTab(runningFrame,'Running text')

        ilgFrame = QFrame()
        ilglayout = QFormLayout()
        ilglayout.addRow(QLabel('Number of lines per gloss (auto-detected)'),self.lineNumberEdit)
        ilglayout.addRow(self.ilgForceInspectButton)
        ilglayout.addRow(self.ilgFeatureSystem)
        #ilglayout.addRow(self.ilgLookupWidget)
        ilgFrame.setLayout(ilglayout)
        self.tabWidget.addTab(ilgFrame,'Interlinear text')

        tgFrame = QFrame()
        tglayout = QFormLayout()
        tglayout.addRow(self.tgFeatureSystem)
        tglayout.addRow(self.tgLookupWidget)
        tgFrame.setLayout(tglayout)
        self.tabWidget.addTab(tgFrame,'TextGrid')

        multFrame = QFrame()
        multlayout = QFormLayout()
        multlayout.addRow('File format', self.multSelect)
        multlayout.addRow(self.multFeatureSystem)
        multFrame.setLayout(multlayout)
        self.tabWidget.addTab(multFrame,'Other standards')

        self.tabWidget.currentChanged.connect(self.typeChanged)

        mainframe = QFrame()
        mainframe.setLayout(mainlayout)
        layout.addWidget(mainframe)

        iolayout.addWidget(self.tabWidget)
        previewlayout = QVBoxLayout()
        previewlayout.addWidget(QLabel('Parsing preview'))
        scroll = QScrollArea()
        self.columnFrame = QWidget()
        self.columns = list()
        lay = QBoxLayout(QBoxLayout.TopToBottom)
        lay.addStretch()
        self.columnFrame.setLayout(lay)
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.columnFrame)
        scroll.setMinimumHeight(140)
        policy = scroll.sizePolicy()
        policy.setVerticalStretch(1)
        scroll.setSizePolicy(policy)
        previewlayout.addWidget(scroll)
        mainlayout.addLayout(previewlayout)

        self.acceptButton = QPushButton('Ok')
        self.csvForceInspectButton.setAutoDefault(False)
        self.ilgForceInspectButton.setAutoDefault(False)
        self.acceptButton.setDefault(True)
        self.cancelButton = QPushButton('Cancel')
        self.helpButton = QPushButton('Help')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.cancelButton)
        acLayout.addWidget(self.helpButton)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.helpButton.clicked.connect(self.help)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Import corpus')

        self.thread = LoadCorpusWorker()
        self.thread.errorEncountered.connect(self.handleError)

        self.progressDialog.setWindowTitle('Importing corpus...')
        self.progressDialog.beginCancel.connect(self.thread.stop)
        self.thread.updateProgress.connect(self.progressDialog.updateProgress)
        self.thread.updateProgressText.connect(self.progressDialog.updateText)
        self.thread.dataReady.connect(self.setResults)
        self.thread.dataReady.connect(self.progressDialog.accept)
        self.thread.finishedCancelling.connect(self.progressDialog.reject)

        self.typeChanged()

    def createWidgets(self):
        self.columnDelimiterEdit = QLineEdit()

        self.lineNumberEdit = QLineEdit()
        self.csvFeatureSystem = FeatureSystemSelect(self.settings)
        self.runningFeatureSystem = FeatureSystemSelect(self.settings)
        self.ilgFeatureSystem = FeatureSystemSelect(self.settings)
        self.tgFeatureSystem = FeatureSystemSelect(self.settings)
        self.multFeatureSystem = FeatureSystemSelect(self.settings)

        self.csvForceInspectButton = QPushButton('Reinspect')
        self.csvForceInspectButton.clicked.connect(self.forceInspect)

        self.ilgForceInspectButton = QPushButton('Reinspect')
        self.ilgForceInspectButton.clicked.connect(self.forceInspect)
        self.runningLookupWidget = SupportCorpusWidget(self.settings)
        self.ilgLookupWidget = SupportCorpusWidget(self.settings)
        self.tgLookupWidget = SupportCorpusWidget(self.settings)

        self.multSelect = QComboBox()
        self.multSelect.addItem('Buckeye')
        self.multSelect.addItem('Timit')
        self.multSelect.currentIndexChanged.connect(self.typeChanged)

        self.runningSelect = QComboBox()
        self.runningSelect.addItem('Orthography')
        self.runningSelect.addItem('Transcribed')
        self.runningSelect.currentIndexChanged.connect(self.typeChanged)


    def updateType(self, type):
        curIndex = self.tabWidget.currentIndex()
        if type == 'text':
            if curIndex > 2:
                self.tabWidget.setTabEnabled(0,True)
                self.tabWidget.setCurrentIndex(0)
            else:
                self.inspect()
        elif type == 'textgrid':
            if curIndex != 3:
                self.tabWidget.setTabEnabled(3,True)
                self.tabWidget.setCurrentIndex(3)
            else:
                self.inspect()
        elif type == 'multiple':
            if curIndex != 4:
                self.tabWidget.setTabEnabled(4,True)
                self.tabWidget.setCurrentIndex(4)
            else:
                self.inspect()
        elif type == 'csv':
            if curIndex != 0:
                self.tabWidget.setTabEnabled(0,True)
                self.tabWidget.setCurrentIndex(0)
            else:
                self.inspect()
        for i in range(self.tabWidget.count()):
            if type == 'text':
                if self.supported_types[i + 1][0] in ['csv', 'running','ilg']:
                    self.tabWidget.setTabEnabled(i, True)
                else:
                    self.tabWidget.setTabEnabled(i, False)
            elif type == self.supported_types[i + 1][0]:
                self.tabWidget.setTabEnabled(i, True)
            else:
                self.tabWidget.setTabEnabled(i, False)

    def typeChanged(self):
        type = self.supported_types[self.tabWidget.currentIndex() + 1][0]
        if type == 'running':
            if self.runningSelect.currentText() == 'Orthography':
                type = 'spelling'
            else:
                type = 'transcription'
        elif type == 'multiple':
            if self.multSelect.currentText() == 'Buckeye':
                type = 'buckeye'
            else:
                type = 'timit'
        self.textType = type
        self.inspect()

    def help(self):
        self.helpDialog = HelpDialog(self,name = 'loading corpora',
                                    section = 'creating-a-corpus-from-running-text')
        self.helpDialog.exec_()

    def setResults(self, results):
        self.corpus = results

    def delimiters(self):
        wordDelim = None
        colDelim = codecs.getdecoder("unicode_escape")(self.columnDelimiterEdit.text())[0]
        return wordDelim, colDelim

    @check_for_errors
    def inspect(self):
        if self.textType is not None and os.path.exists(self.pathWidget.value()):
            if self.textType == 'csv':
                try:
                    atts, coldelim = inspect_csv(self.pathWidget.value())
                except PCTError:
                    self.updateColumnFrame([])
                    return
                self.columnDelimiterEdit.setText(coldelim.encode('unicode_escape').decode('utf-8'))
                self.updateColumnFrame(atts)
            else:
                if self.textType == 'textgrid':
                    anno_types = inspect_discourse_textgrid(self.pathWidget.value())
                elif self.textType == 'ilg':
                    anno_types = inspect_discourse_ilg(self.pathWidget.value())
                    self.lineNumberEdit.setText(str(len(anno_types)))
                elif self.textType == 'transcription':
                    anno_types = inspect_discourse_transcription(self.pathWidget.value())
                elif self.textType == 'spelling':
                    anno_types = inspect_discourse_spelling(self.pathWidget.value())
                elif self.textType in ['buckeye','timit']:

                    anno_types = inspect_discourse_multiple_files(self.pathWidget.value(), self.textType)
                self.updateColumnFrame(anno_types)

        else:
            self.updateColumnFrame([])

    @check_for_errors
    def forceInspect(self, b):
        if os.path.exists(self.pathWidget.value()):
            if self.textType == 'csv':
                colDelim = codecs.getdecoder("unicode_escape")(self.columnDelimiterEdit.text())[0]
                if not colDelim:
                    colDelim = None
                atts, coldelim = inspect_csv(self.pathWidget.value(),
                        coldelim = colDelim)
                self.updateColumnFrame(atts)
            elif self.textType == 'ilg':
                number = self.lineNumberEdit.text()
                if number == '':
                    number = None
                else:
                    try:
                        number = int(number)
                    except:
                        number = None
                annotation_types = inspect_discourse_ilg(self.pathWidget.value(), number = number)
                self.updateColumnFrame(annotation_types)

    def updateColumnFrame(self, atts):
        for i in reversed(range(self.columnFrame.layout().count()-1)):
            w = self.columnFrame.layout().itemAt(i).widget()
            if w is None:
                del w
                continue
            w.setParent(None)
            w.deleteLater()
        self.columns = list()
        for a in reversed(atts):
            show_attribute = self.textType not in ['spelling','transcription']
            c = AnnotationTypeWidget(a, show_attribute = show_attribute)
            self.columns.append(c)
            self.columnFrame.layout().insertWidget(0, c)

    def generateKwargs(self):
        path = self.pathWidget.value()
        if path == '':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a file or directory.")
            return
        if not os.path.exists(path):
            reply = QMessageBox.critical(self,
                    "Invalid information", "The specified path does not exist.")
            return
        name = self.nameEdit.text()
        if name == '':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a name for the corpus.")
            return
        kwargs = {'corpus_name': name,
                    'path': path,
                    'text_type': self.textType}
        kwargs['annotation_types'] = [x.value() for x in reversed(self.columns)]
        if self.textType == 'csv':
            kwargs['delimiter'] = codecs.getdecoder("unicode_escape")(
                                        self.columnDelimiterEdit.text()
                                        )[0]
            kwargs['feature_system_path'] = self.csvFeatureSystem.path()
        elif self.textType == 'textgrid':
            kwargs['feature_system_path'] = self.tgFeatureSystem.path()
        elif self.textType == 'spelling':
            (kwargs['support_corpus_path'],
                kwargs['ignore_case']) = self.runningLookupWidget.value()
        elif self.textType == 'transcription':
            kwargs['feature_system_path'] = self.runningFeatureSystem.path()
        elif self.textType == 'ilg':
            kwargs['feature_system_path'] = self.ilgFeatureSystem.path()
            #(kwargs['support_corpus_path'],
            #    kwargs['ignore_case']) = self.ilgLookupWidget.value()
        elif self.textType in ['buckeye', 'timit']:
            kwargs['feature_system_path'] = self.multFeatureSystem.path()
            base, ext = os.path.splitext(path)
            if ext == '.words':
                phone_path = base +'.phones'
            elif ext == '.wrd':
                phone_path = base + '.phn'
            if not os.path.exists(phone_path):
                reply = QMessageBox.critical(self,
                        "Invalid information", "The phone file for the specifie words file does not exist.")
                return
            kwargs['word_path'] = kwargs.pop('path')
            kwargs['phone_path'] = phone_path
        if name in get_corpora_list(self.settings['storage']):
            msgBox = QMessageBox(QMessageBox.Warning, "Duplicate name",
                    "A corpus named '{}' already exists.  Overwrite?".format(name), QMessageBox.NoButton, self)
            msgBox.addButton("Overwrite", QMessageBox.AcceptRole)
            msgBox.addButton("Abort", QMessageBox.RejectRole)
            if msgBox.exec_() != QMessageBox.AcceptRole:
                return None

        return kwargs

    @check_for_errors
    def accept(self, b):
        kwargs = self.generateKwargs()
        if kwargs is None:
            return
        self.thread.setParams(kwargs)

        self.thread.start()

        result = self.progressDialog.exec_()

        self.progressDialog.reset()
        if result:
            if self.corpus is not None:
                save_binary(self.corpus,
                    corpus_name_to_path(self.settings['storage'],self.corpus.name))
            QDialog.accept(self)

    def updateName(self):
        path = self.pathWidget.value()
        filename = os.path.split(path)[1]
        name, ext = os.path.splitext(filename)
        self.nameEdit.setText(name)
        if ext.lower() == '.textgrid':
            self.updateType('textgrid')
        elif ext.lower() == '.csv':
            self.updateType('csv')
        elif ext.lower() in ['.words','.wrds']:
            self.updateType('multiple')
        elif ext.lower() == '.txt':
            self.updateType('text')


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
        self.helpButton = QPushButton('Help')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.cancelButton)
        acLayout.addWidget(self.helpButton)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.helpButton.clicked.connect(self.help)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Subset corporus')

    def help(self):
        self.helpDialog = HelpDialog(self,name = 'loading corpora',
                                    section = 'subsetting-a-corpus')
        self.helpDialog.exec_()

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

        if name in get_corpora_list(self.parent().settings['storage']):
            msgBox = QMessageBox(QMessageBox.Warning, "Duplicate name",
                    "A corpus named '{}' already exists.  Overwrite?".format(name), QMessageBox.NoButton, self)
            msgBox.addButton("Overwrite", QMessageBox.AcceptRole)
            msgBox.addButton("Abort", QMessageBox.RejectRole)
            if msgBox.exec_() != QMessageBox.AcceptRole:
                return
        new_corpus = self.corpus.subset(filters)
        new_corpus.name = name
        new_corpus.set_feature_matrix(self.corpus.specifier)
        save_binary(new_corpus,
            corpus_name_to_path(self.parent().settings['storage'],new_corpus.name))
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

        self.variantCheck = QCheckBox()

        inlayout.addRow('Include pronunciation variants', self.variantCheck)

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

        export_corpus_csv(self.corpus,filename,colDelim,transDelim, self.variantCheck.isChecked())

        QDialog.accept(self)
