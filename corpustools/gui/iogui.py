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
                                    export_corpus_csv,
                                    characters_corpus_csv)
from corpustools.corpus.io.textgrid import (inspect_discourse_textgrid,
                                            load_discourse_textgrid,
                                            characters_discourse_textgrid)

from corpustools.corpus.io.text_ilg import (load_discourse_ilg,
                                        inspect_discourse_ilg,
                                        characters_discourse_ilg)

from corpustools.corpus.io.text_spelling import (load_discourse_spelling,
                                                inspect_discourse_spelling)

from corpustools.corpus.io.text_transcription import (load_discourse_transcription,
                                                        inspect_discourse_transcription,
                                                        characters_discourse_transcription)

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
        self.loadCorpusButton = QPushButton('Import corpus')
        self.removeButton = QPushButton('Remove selected corpus')
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


class LoadCorpusDialog(PCTDialog):
    supported_types = [(None, ''),('csv', 'Column delimited text file'),
                        ('transcription', 'Transcribed text'),
                        ('spelling', 'Orthography text'),
                        ('ilg', 'Interlinear text'),
                        ('textgrid', 'TextGrid'),
                        ('buckeye', 'Buckeye format'),
                        ('timit', 'Timit format')]
    def __init__(self, parent, settings):
        PCTDialog.__init__(self, parent)
        self.settings = settings

        self.createWidgets()

        layout = QVBoxLayout()

        mainlayout = QHBoxLayout()

        iolayout = QFormLayout()

        self.characters = set()
        self.pathWidget = FileWidget('Open corpus text','Text files (*.txt *.csv *.TextGrid *.words *.wrds)')
        self.pathWidget.pathEdit.textChanged.connect(self.updateName)


        self.textType = None

        iolayout.addRow(QLabel('Path to corpus'),self.pathWidget)

        self.nameEdit = QLineEdit()
        iolayout.addRow(QLabel('Name for corpus'),self.nameEdit)

        #self.punctuation = PunctuationWidget(string.punctuation, 'Punctuation to ignore')
        #iolayout.addRow(self.punctuation)


        ioframe = QGroupBox('Corpus details')
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
        self.tabWidget.addTab(csvFrame,'Column delimited text file')

        transFrame = QFrame()
        translayout = QFormLayout()

        translayout.addRow(self.transFeatureSystem)
        transFrame.setLayout(translayout)
        self.tabWidget.addTab(transFrame,'Transcribed text')

        orthFrame = QFrame()
        orthlayout = QFormLayout()
        orthlayout.addRow(self.orthLookupWidget)
        orthFrame.setLayout(orthlayout)
        self.tabWidget.addTab(orthFrame,'Orthographic text')

        ilgFrame = QFrame()
        ilglayout = QFormLayout()
        ilglayout.addRow(QLabel('Number of lines per gloss (auto-detected)'),self.lineNumberEdit)
        ilglayout.addRow(self.ilgForceInspectButton)
        ilglayout.addRow(self.ilgFeatureSystem)
        ilglayout.addRow(self.ilgLookupWidget)
        ilgFrame.setLayout(ilglayout)
        self.tabWidget.addTab(ilgFrame,'Interlinear text')

        tgFrame = QFrame()
        tglayout = QFormLayout()
        tglayout.addRow(self.tgFeatureSystem)
        tglayout.addRow(self.tgLookupWidget)
        tgFrame.setLayout(tglayout)
        self.tabWidget.addTab(tgFrame,'TextGrid')

        buckeyeFrame = QFrame()
        buckeyelayout = QFormLayout()
        buckeyelayout.addRow(self.buckeyeFeatureSystem)
        buckeyeFrame.setLayout(buckeyelayout)
        self.tabWidget.addTab(buckeyeFrame,'Buckeye format')

        timitFrame = QFrame()
        timitlayout = QFormLayout()
        timitlayout.addRow(self.timitFeatureSystem)
        timitFrame.setLayout(timitlayout)
        self.tabWidget.addTab(timitFrame,'TIMIT format')

        self.tabWidget.currentChanged.connect(self.typeChanged)

        mainframe = QFrame()
        mainframe.setLayout(mainlayout)
        layout.addWidget(mainframe)

        layout.addWidget(self.tabWidget)

        scroll = QScrollArea()
        self.columnFrame = QWidget()
        self.columns = list()
        lay = QBoxLayout(QBoxLayout.TopToBottom)
        lay.addStretch()
        self.columnFrame.setLayout(lay)
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.columnFrame)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setMinimumHeight(140)
        policy = scroll.sizePolicy()
        policy.setVerticalStretch(1)
        scroll.setSizePolicy(policy)
        #self.columnFrame.
        layout.addWidget(scroll)

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
        self.transFeatureSystem = FeatureSystemSelect(self.settings)
        self.ilgFeatureSystem = FeatureSystemSelect(self.settings)
        self.tgFeatureSystem = FeatureSystemSelect(self.settings)
        self.buckeyeFeatureSystem = FeatureSystemSelect(self.settings)
        self.timitFeatureSystem = FeatureSystemSelect(self.settings)

        self.csvForceInspectButton = QPushButton('Reinspect')
        self.csvForceInspectButton.clicked.connect(self.forceInspect)

        self.ilgForceInspectButton = QPushButton('Reinspect')
        self.ilgForceInspectButton.clicked.connect(self.forceInspect)


        self.orthLookupWidget = SupportCorpusWidget(self.settings)
        self.ilgLookupWidget = SupportCorpusWidget(self.settings)
        self.tgLookupWidget = SupportCorpusWidget(self.settings)

    def updateType(self, type):
        for i in range(self.tabWidget.count()):
            self.tabWidget.setTabEnabled(i, False)
            if type == 'text':
                if self.supported_types[i + 1][0] in ['csv', 'transcription','spelling','ilg']:
                    self.tabWidget.setTabEnabled(i, True)
                if i == 0:
                    self.tabWidget.setCurrentIndex(i)
            elif type == self.supported_types[i + 1][0]:
                self.tabWidget.setTabEnabled(i, True)
                self.tabWidget.setCurrentIndex(i)

    def typeChanged(self):
        self.textType = self.supported_types[self.tabWidget.currentIndex() + 1][0]
        self.inspect()

    def help(self):
        self.helpDialog = HelpDialog(self,name = 'loading corpora',
                                    section = 'creating-a-corpus-from-running-text')
        self.helpDialog.exec_()

    def setResults(self, results):
        self.corpus = results

    def ignoreList(self):
        return []
        return self.punctuation.value()

    def delimiters(self):
        wordDelim = None
        colDelim = codecs.getdecoder("unicode_escape")(self.columnDelimiterEdit.text())[0]
        return wordDelim, colDelim

    def getCharacters(self):
        return
        path = self.pathWidget.value()
        characters = set()

        if path != '' and os.path.exists(path):
            if self.textType == 'transcription':
                characters = characters_discourse_transcription(path)
            elif self.textType == 'csv':
                pass
            elif self.textType == 'textgrid':
                pass
            elif self.textType == 'ilg':
                pass

        minus = set(self.ignoreList())
        wd, cd = self.delimiters()
        delims = []
        if wd is None:
            delims.extend([' ','\t','\n'])
        elif isinstance(wd,list):
            delims.extend(wd)
        else:
            delims.append(wd)
        for c in self.columns:
            if c.value().delimiter is not None:
                delims.append(cd)
        if cd is not None:
            if isinstance(cd,list):
                delims.extend(cd)
            else:
                delims.append(cd)
        minus.update(delims)
        characters = characters - minus
        self.digraphs.setCharacters(characters)

    @check_for_errors
    def inspect(self):
        if self.textType is not None and os.path.exists(self.pathWidget.value()):
            if self.textType == 'csv':
                try:
                    atts, coldelim = inspect_csv(self.pathWidget.value())
                except:
                    return
                self.columnDelimiterEdit.setText(coldelim.encode('unicode_escape').decode('utf-8'))
                self.updateColumnFrame(atts, column = True)
            else:
                if self.textType == 'textgrid':
                    anno_types = inspect_discourse_textgrid(self.pathWidget.value())
                elif self.textType == 'ilg':
                    anno_types = inspect_discourse_ilg(self.pathWidget.value())
                    self.lineNumberEdit.setText(str(len(anno_types)))
                elif self.textType == 'transcription':
                    anno_types = inspect_discourse_transcription(self.pathWidget.value())
                elif self.textType == 'spelling':
                    anno_types = inspect_discourse_spelling(self.pathWidget.value(), self.orthLookupWidget.path())
                elif self.textType in ['buckeye','timit']:

                    anno_types = inspect_discourse_multiple_files(self.pathWidget.value(), self.textType)
                self.updateColumnFrame(anno_types)

        else:
            self.updateColumnFrame([])
        if self.textType is not None:
            self.getCharacters()

    @check_for_errors
    def forceInspect(self, b):
        if os.path.exists(self.pathWidget.value()):
            if self.textType == 'csv':
                colDelim = codecs.getdecoder("unicode_escape")(self.columnDelimiterEdit.text())[0]
                if not colDelim:
                    colDelim = None
                atts, coldelim = inspect_csv(self.pathWidget.value(),
                        coldelim = colDelim)
                self.updateColumnFrame(atts, column = True)
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

    def updateColumnFrame(self, atts, column = False):
        if column:
            self.columnFrame.layout().setDirection(QBoxLayout.LeftToRight)
        else:
            self.columnFrame.layout().setDirection(QBoxLayout.TopToBottom)
        for i in reversed(range(self.columnFrame.layout().count()-1)):
            w = self.columnFrame.layout().itemAt(i).widget()
            if w is None:
                del w
                continue
            w.setParent(None)
            w.deleteLater()
        self.columns = list()
        for a in reversed(atts):
            title = None
            if self.textType == 'textgrid':
                title = 'Tier details'
            elif self.textType in ['ilg','spelling']:
                title = 'Line details'
            elif self.textType == 'transcription':
                if a.name == 'transcription':
                    title = 'Line details'
                else:
                    title = 'Spellings inferred from text'

            c = AnnotationTypeWidget(a, title = title, column = column)
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
        if self.textType == None:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a type of file to load.")
            return
        wordDelim, colDelim = self.delimiters()
        ignore_list = self.punctuation.value()
        feature_system_path = self.featureSystem.path()
        supportCorpus = self.supportCorpus.path()
        kwargs = {'corpus_name': name,
                    'path': path,
                    'text_type': self.textType,
                    'ignore_list':ignore_list}
        kwargs['delimiter'] = wordDelim
        kwargs['annotation_types'] = [x.value() for x in self.columns]
        kwargs['digraph_list'] = self.digraphs.value()
        kwargs['feature_system_path'] = feature_system_path
        if self.textType == 'csv':
            del kwargs['ignore_list']
            kwargs['attributes'] = kwargs.pop('annotation_types')
            kwargs['delimiter'] = colDelim
        elif self.textType == 'textgrid':
            pass
        elif self.textType == 'spelling':
            kwargs['ignore_case'] = self.ignoreCase.isChecked()
            kwargs['support_corpus_path'] = supportCorpus
            del kwargs['feature_system_path']
            del kwargs['digraph_list']
        elif self.textType == 'transcription':
            pass
        elif self.textType == 'ilg':
            pass
        elif self.textType in ['buckeye', 'timit']:
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
            del kwargs['ignore_list']
            del kwargs['digraph_list']
            del kwargs['feature_system_path']
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
        elif ext.lower() == '.words':
            self.updateType('buckeye')
        elif ext.lower() == '.wrds':
            self.updateType('timit')
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
