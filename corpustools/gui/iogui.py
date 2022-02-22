import os
import codecs
import logging
from collections import OrderedDict, defaultdict
import webbrowser

from .imports import *
from corpustools.exceptions import PCTError, PCTPythonError, MissingFeatureError, PCTEncodingError
from corpustools.decorators import check_for_errors
from corpustools.corpus.io.binary import load_binary, save_binary, PCTUnpickler
from corpustools.corpus.io.csv import (inspect_csv, load_corpus_csv,
                                       export_corpus_csv)
from corpustools.corpus.io.pct_textgrid import (inspect_discourse_textgrid,
                                                load_discourse_textgrid,
                                                load_directory_textgrid)
from corpustools.corpus.io.text_ilg import (load_discourse_ilg,
                                            inspect_discourse_ilg,
                                            load_directory_ilg)
from corpustools.corpus.io.text_spelling import (load_discourse_spelling,
                                                 inspect_discourse_spelling,
                                                 load_directory_spelling)
from corpustools.corpus.io.text_transcription import (load_discourse_transcription,
                                                      inspect_discourse_transcription,
                                                      load_directory_transcription)
from corpustools.corpus.io.multiple_files import (load_discourse_multiple_files,
                                                  inspect_discourse_multiple_files,
                                                  load_directory_multiple_files)
from corpustools.corpus.io.helper import (get_corpora_list,
                                          corpus_name_to_path,
                                          inspect_directory,
                                          log_annotation_types,
                                          punctuation_names)
from corpustools.gui.featuregui import system_name_to_path
import corpustools.gui.modernize as modernize
from .windows import FunctionWorker, DownloadWorker, PCTDialog

from .widgets import (RadioSelectWidget, SaveFileWidget, AttributeFilterWidget, AnnotationTypeWidget, CorpusSelect)
from .featuregui import FeatureSystemSelect, RestrictedFeatureSystemSelect
from .helpgui import HelpDialog, get_url
from urllib.request import urlretrieve


class LoadBinaryWorker(FunctionWorker):
    def run(self):
        if self.stopCheck():
            return
        try:
            unpickler = PCTUnpickler(self.kwargs['path'], self.kwargs['call_back'], self.kwargs['stop_check'])
            results = unpickler.load()
        except PCTError as e:
            self.errorEncountered.emit(e)
            return
        except Exception as e:
            e = PCTPythonError(e)
            self.errorEncountered.emit(e)
            return
        if self.stopped:
            self.finishedCancelling.emit()
            return
        self.dataReady.emit(results)


class LoadCorpusWorker(FunctionWorker):

    def run(self):
        textType = self.kwargs.pop('text_type')
        isDirectory = self.kwargs.pop('isDirectory')
        logging.info('Importing {} corpus named {}'.format(textType, self.kwargs['corpus_name']))
        try:
            logging.info('Path: '.format(self.kwargs['path']))
        except KeyError:  # Buckeye Corpus
            logging.info('Path: '.format(self.kwargs['word_path']))
        log_annotation_types(self.kwargs['annotation_types'])
        try:
            if textType == 'spelling':
                if isDirectory:
                    corpus = load_directory_spelling(**self.kwargs)
                else:
                    corpus = load_discourse_spelling(**self.kwargs)

            elif textType == 'transcription':
                if isDirectory:
                    corpus = load_directory_transcription(**self.kwargs)
                else:
                    corpus = load_discourse_transcription(**self.kwargs)

            elif textType == 'ilg':
                if isDirectory:
                    corpus = load_directory_ilg(**self.kwargs)
                else:
                    corpus = load_discourse_ilg(**self.kwargs)

            elif textType == 'textgrid':
                if isDirectory:
                    corpus = load_directory_textgrid(**self.kwargs)
                else:
                    corpus = load_discourse_textgrid(**self.kwargs)

            elif textType == 'csv':
                corpus = load_corpus_csv(**self.kwargs)

            elif textType == 'buckeye':
                self.kwargs['dialect'] = textType
                if isDirectory:
                    corpus = load_directory_multiple_files(**self.kwargs)
                else:
                    corpus = load_discourse_multiple_files(**self.kwargs)

        except MissingFeatureError as e:
            self.errorEncountered.emit(e)
            return

        except PCTError as e:
            self.errorEncountered.emit(e)
            return
        except Exception as e:
            e = PCTPythonError(e)
            self.errorEncountered.emit(e)
            return
        if self.stopped:
            self.finishedCancelling.emit()
            return
        if corpus is None:
            return

        # If a Discourse object was just loaded, it needs to have its features specified
        # A Corpus has its features specified already at this point
        if hasattr(corpus, 'lexicon'):
            for seg in corpus.lexicon.inventory:
                try:
                    corpus.lexicon.inventory[seg].features = corpus.lexicon.specifier.specify(seg)
                except KeyError:
                    # Occurs if a user selected a feature/transcription system that doesn't match the corpus
                    corpus.lexicon.specifier[seg] = {feature: 'n' for feature in corpus.lexicon.specifier.features}
                    corpus.lexicon.inventory[seg].features = corpus.lexicon.specifier.specify(seg)
                except AttributeError:
                    pass  # This only has spelling, no transcription

        self.dataReady.emit(corpus)


class CorpusLoadDialog(PCTDialog):
    def __init__(self, parent, current_corpus, settings):
        PCTDialog.__init__(self, parent, infinite_progress=True)
        self.current_corpus = None if current_corpus is None else parent.corpus.name
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
        self.loadCorpusButton = QPushButton('Create corpus from file')
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
        # self.forceUpdateButton = QPushButton('Load corpus with forced update')
        # self.forceUpdateButton.setAutoDefault(False)
        self.cancelButton = QPushButton('Cancel')
        self.helpButton = QPushButton('Help')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        # acLayout.addWidget(self.forceUpdateButton)
        acLayout.addWidget(self.cancelButton)
        acLayout.addWidget(self.helpButton)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.helpButton.clicked.connect(self.help)
        # self.forceUpdateButton.clicked.connect(self.forceUpdate)
        # self.forceUpdateButton.setToolTip(
        #     ('<span>This loads a corpus file, and reformats it to ensure it has all of the '
        #      'required attributes for the current version PCT. Try this option if you are having trouble getting a '
        #      'corpus to load properly.</span>'))
        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Load corpora')

        self.thread = LoadBinaryWorker()
        self.thread.errorEncountered.connect(self.handleError)

        self.progressDialog.setWindowTitle('Loading...')
        self.progressDialog.beginCancel.connect(self.thread.stop)
        self.thread.updateProgress.connect(self.progressDialog.updateProgress)
        self.thread.updateProgressText.connect(self.progressDialog.updateText)
        self.thread.dataReady.connect(self.setResults)
        self.thread.dataReady.connect(self.progressDialog.accept)
        self.thread.finishedCancelling.connect(self.progressDialog.reject)

    def help(self):
        url = get_url('loading corpora')
        webbrowser.open(url)
        # self.helpDialog = HelpDialog(self, name = 'loading corpora')
        # self.helpDialog.exec_()

    def setResults(self, results):
        if results is None:
            return
        self.corpus = results

    def forceUpdate(self):
        result = self.loadCorpus()
        if result:
            if hasattr(self.corpus, 'lexicon'):
                self.corpus.lexicon = modernize.force_update(self.corpus.lexicon)
            else:
                self.corpus = modernize.force_update(self.corpus)
            QDialog.accept(self)

    def loadCorpus(self):
        selected = [x.text() for x in self.corporaList.selectedItems()]
        if selected:
            self.thread.setParams({
                'path': corpus_name_to_path(
                    self.settings['storage'], selected[0])})
            self.progressDialog.setWindowTitle('Loading {}...'.format(selected[0]))
            self.thread.start()
            result = self.progressDialog.exec_()
            self.progressDialog.reset()
            return result

    def accept(self):
        result = self.loadCorpus()
        # self.loadCorpus() returns whether user clicked cancel, or whether the progress bar completed
        # it does not return anything about the corpus itself
        # the corpus is saved in the Dialog.corpus attribute
        if result:
            QDialog.accept(self)

        else:
            self.progressDialog.cancelButton.setEnabled(True)
            self.progressDialog.cancelButton.setText('Cancel')
            self.progressDialog.setLabelText('')

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
        if self.current_corpus == corpus:
            alert = QMessageBox()
            alert.setWindowTitle('Warning!')
            alert.setText('You are trying to delete the corpus that is currently open in PCT. '
                          'Please close the corpus before deleting. You can do this '
                          'by opening up another corpus first, or else by closing PCT and re-opening with a blank window.')
            alert.addButton('OK', QMessageBox.AcceptRole)
            alert.exec_()
            return
        msgBox = QMessageBox(QMessageBox.Warning, "Remove corpus",
                             "This will permanently remove '{}'.  Are you sure?".format(corpus), QMessageBox.NoButton,
                             self)
        msgBox.addButton("Remove", QMessageBox.AcceptRole)
        msgBox.addButton("Cancel", QMessageBox.RejectRole)
        if msgBox.exec_() != QMessageBox.AcceptRole:
            return
        os.remove(corpus_name_to_path(self.settings['storage'], corpus))
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
                                               OrderedDict([('Example toy corpus', 'example'),
                                                            ('Example toy corpus (syllabified)','example_syllabified'),
                                                            ('Lemurian (Toy language)', 'lemurian'),
                                                            ('IPHOD with homographs', 'iphod_with_homographs'),
                                                            ('IPHOD without homographs (default before 2019)',
                                                             'iphod_without_homographs')]))

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

        layout.addWidget(QLabel("Please be patient. It can take up to 30 seconds to download a corpus.\n"
                                "This window will close when finished."))

        self.setLayout(layout)

        self.setWindowTitle('Download corpora')

        self.thread = DownloadWorker()

        self.progressDialog = QProgressDialog('Downloading...', 'Cancel', 0, 100, self)
        self.progressDialog.setWindowTitle('Download corpus')
        self.progressDialog.setAutoClose(False)
        self.progressDialog.setAutoReset(False)
        self.progressDialog.canceled.connect(self.thread.stop)
        self.thread.updateProgress.connect(self.updateProgress)
        self.thread.updateProgressText.connect(self.updateProgressText)
        self.thread.finished.connect(self.progressDialog.accept)

    def help(self):
        url = get_url('loading corpora', section='using-a-built-in-corpus')
        webbrowser.open(url)
        # self.helpDialog = HelpDialog(self, name='loading corpora',
        #                              section='using-a-built-in-corpus')
        # self.helpDialog.exec_()

    def updateProgressText(self, text):
        self.progressDialog.setLabelText(text)
        self.progressDialog.reset()

    def updateProgress(self, progress):
        self.progressDialog.setValue(progress)
        self.progressDialog.repaint()

    def accept(self):
        name = self.corporaWidget.value()
        if name in get_corpora_list(self.settings['storage']):
            msgBox = QMessageBox(QMessageBox.Warning, "Overwrite corpus",
                                 "The corpus '{}' is already available.  Would you like to overwrite it?".format(name),
                                 QMessageBox.NoButton, self)
            msgBox.addButton("Overwrite", QMessageBox.AcceptRole)
            msgBox.addButton("Cancel", QMessageBox.RejectRole)
            if msgBox.exec_() != QMessageBox.AcceptRole:
                return
        try:
            # try downloading a tiny bit from the PCT file storage on Dropbox.
            # If fails for whatever reason, including no internet or SSL-certi issue on MacOS, prompt an error message.
            # When making any changes to here, check the equivalent part on featuregui.py as well.
            urlretrieve('https://www.dropbox.com/s/ytcl72nxydiqkyg/do_not_remove.txt?dl=1')
        except:
            QMessageBox.critical(self, 'Cannot access online repository',
                                 'PCT could not make a secured connection to PCT repository hosted at Dropbox.\n\n'
                                 'Please make sure you are connected to the internet. \nIf you are using MacOS, '
                                 'Go to "Applications -> Python x.y (your version)" on Finder and run '
                                 '"Certificates.command".')
            return

        self.thread.setParams({'name': name,
                               'path': corpus_name_to_path(self.settings['storage'], name)})

        self.thread.start()

        result = self.progressDialog.exec_()

        self.progressDialog.reset()
        if result:
            QDialog.accept(self)


class SupportCorpusWidget(QGroupBox):
    def __init__(self, settings, parent=None):
        QGroupBox.__init__(self, 'Support corpus', parent)
        self.supportCorpus = CorpusSelect(self, settings)

        layout = QFormLayout()
        layout.addRow(QLabel('Corpus to look up transcriptions'), self.supportCorpus)

        self.ignoreCase = QCheckBox()
        layout.addRow(QLabel('Ignore case for look up'), self.ignoreCase)

        self.setLayout(layout)

    def path(self):
        return self.supportCorpus.path()

    def value(self):
        return self.path(), self.ignoreCase.isChecked()


class CorpusSourceWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.filefilter = 'Text files (*.txt *.csv *.TextGrid *.words)'
        self.relevent_files = None
        self.suggested_type = None

        layout = QHBoxLayout()
        pathLayout = QVBoxLayout()
        buttonLayout = QVBoxLayout()

        self.pathEdit = QLineEdit()
        pathLayout.addWidget(self.pathEdit)

        self.pathButton = QPushButton('Choose file...')
        self.pathButton.setAutoDefault(False)
        self.pathButton.setDefault(False)
        self.pathButton.clicked.connect(self.pickFile)
        buttonLayout.addWidget(self.pathButton)

        self.directoryButton = QPushButton('Choose directory...')
        self.directoryButton.setAutoDefault(False)
        self.directoryButton.setDefault(False)
        self.directoryButton.clicked.connect(self.pickDirectory)
        buttonLayout.addWidget(self.directoryButton)

        self.mouseover = QLabel('Mouseover for included files')
        self.mouseover.setFrameShape(QFrame.Box)
        self.mouseover.setToolTip('No included files')
        pathLayout.addWidget(self.mouseover)

        layout.addLayout(pathLayout)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

        self.textChanged = self.pathEdit.textChanged

    def pickDirectory(self):
        filename = QFileDialog.getExistingDirectory(self, "Choose a directory")
        if filename:

            self.suggested_type, self.relevent_files = inspect_directory(filename)
            self.updateType(self.suggested_type)
            self.pathEdit.setText(filename)
        else:
            self.relevent_files = None
            self.suggested_type = None

    def updateType(self, type):
        if self.relevent_files is None or type is None:
            self.mouseover.setToolTip('No included files')
        else:
            self.mouseover.setToolTip('\n'.join(self.relevent_files[type]))

    def pickFile(self):
        filename = QFileDialog.getOpenFileName(self, 'Select file',
                                               filter=self.filefilter)
        if filename:
            self.pathEdit.setText(filename[0])

    def value(self):
        return self.pathEdit.text()


class LoadCorpusDialog(PCTDialog):
    supported_types = [(None, ''), ('csv', 'Column-delimited file'),
                       ('running', 'Running text'),
                       ('ilg', 'Interlinear text'),
                       ('textgrid', 'TextGrid'),
                       ('multiple', 'Other standards'), ]

    def __init__(self, parent, settings):
        PCTDialog.__init__(self, parent, infinite_progress=True)
        self.settings = settings
        self.textType = None
        self.isDirectory = False
        self.corpus = None
        self.createWidgets()

        layout = QVBoxLayout()
        mainlayout = QHBoxLayout()
        iolayout = QFormLayout()
        pathlayout = QHBoxLayout()

        self.pathWidget = CorpusSourceWidget()
        self.pathWidget.pathEdit.textChanged.connect(self.updateName)

        pathlayout.addWidget(QLabel('Corpus source'))
        pathlayout.addWidget(self.pathWidget)

        self.nameEdit = QLineEdit()
        pathlayout.addWidget(QLabel('Corpus name'))
        pathlayout.addWidget(self.nameEdit)

        pathframe = QWidget()
        pathframe.setLayout(pathlayout)
        iolayout.addRow(pathframe)

        ioframe = QWidget()
        ioframe.setLayout(iolayout)

        mainlayout.addWidget(ioframe)

        self.tabWidget = QTabWidget()

        optionlayout = QFormLayout()

        csvFrame = QWidget()
        csvlayout = QFormLayout()
        csvlayout.addRow(QLabel('Column delimiter (auto-detected)'), self.columnDelimiterEdit)
        csvlayout.addRow(self.csvForceInspectButton)

        csvlayout.addRow(self.csvFeatureSystem)

        csvFrame.setLayout(csvlayout)
        self.tabWidget.addTab(csvFrame, 'Column-delimited file')

        runningFrame = QWidget()
        runninglayout = QFormLayout()
        runninglayout.addRow('Text type', self.runningSelect)

        runninglayout.addRow(self.runningFeatureSystem)
        runninglayout.addRow(self.runningLookupWidget)
        runningFrame.setLayout(runninglayout)
        self.tabWidget.addTab(runningFrame, 'Running text')

        ilgFrame = QWidget()
        ilglayout = QFormLayout()
        ilglayout.addRow(QLabel('Number of lines per gloss (auto-detected)'), self.lineNumberEdit)
        ilglayout.addRow(self.ilgForceInspectButton)
        ilglayout.addRow(self.ilgFeatureSystem)
        # ilglayout.addRow(self.ilgLookupWidget)
        ilgFrame.setLayout(ilglayout)
        self.tabWidget.addTab(ilgFrame, 'Interlinear text')

        tgFrame = QWidget()
        tglayout = QFormLayout()
        tglayout.addRow(self.tgFeatureSystem)
        tglayout.addRow(self.tgLookupWidget)
        tgFrame.setLayout(tglayout)
        self.tabWidget.addTab(tgFrame, 'TextGrid')

        multFrame = QFrame()
        multlayout = QFormLayout()
        multlayout.addRow('File format', self.multSelect)
        multlayout.addRow(self.multFeatureSystem)
        multFrame.setLayout(multlayout)
        self.tabWidget.addTab(multFrame, 'Other standards')

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
        scroll.setMinimumWidth(500)
        policy = scroll.sizePolicy()
        policy.setVerticalStretch(1)
        scroll.setSizePolicy(policy)
        previewlayout.addWidget(scroll)
        mainlayout.addLayout(previewlayout)

        self.acceptButton = QPushButton('Ok')
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

        acFrame = QWidget()
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
        self.csvFeatureSystem = RestrictedFeatureSystemSelect(self.settings, None)
        self.runningFeatureSystem = RestrictedFeatureSystemSelect(self.settings, None)
        self.ilgFeatureSystem = RestrictedFeatureSystemSelect(self.settings, None)
        self.tgFeatureSystem = RestrictedFeatureSystemSelect(self.settings, None)
        self.multFeatureSystem = RestrictedFeatureSystemSelect(self.settings, None)

        self.csvForceInspectButton = QPushButton('Reinspect')
        self.csvForceInspectButton.clicked.connect(self.forceInspect)

        self.ilgForceInspectButton = QPushButton('Reinspect')
        self.ilgForceInspectButton.clicked.connect(self.forceInspect)

        self.csvForceInspectButton.setAutoDefault(False)
        self.ilgForceInspectButton.setAutoDefault(False)

        self.runningLookupWidget = SupportCorpusWidget(self.settings)
        self.ilgLookupWidget = SupportCorpusWidget(self.settings)
        self.tgLookupWidget = SupportCorpusWidget(self.settings)

        self.multSelect = QComboBox()
        self.multSelect.addItem('Buckeye')
        # self.multSelect.addItem('Timit')
        self.multSelect.currentIndexChanged.connect(self.typeChanged)

        self.runningSelect = QComboBox()
        self.runningSelect.addItem('Orthography')
        self.runningSelect.addItem('Transcribed')
        self.runningSelect.currentIndexChanged.connect(self.typeChanged)

    def updateType(self, type):
        curIndex = self.tabWidget.currentIndex()
        if type == 'text':
            if not self.isDirectory and curIndex > 2:
                self.tabWidget.setTabEnabled(0, True)
                self.tabWidget.setCurrentIndex(0)
            elif self.isDirectory:
                self.tabWidget.setTabEnabled(1, True)
                self.tabWidget.setCurrentIndex(1)
                self.tabWidget.setTabEnabled(0, False)
            else:
                self.inspect()
        elif type == 'textgrid':
            if curIndex != 3:
                self.tabWidget.setTabEnabled(3, True)
                self.tabWidget.setCurrentIndex(3)
            else:
                self.inspect()
        elif type == 'multiple':
            if curIndex != 4:
                self.tabWidget.setTabEnabled(4, True)
                self.tabWidget.setCurrentIndex(4)
            else:
                self.inspect()
        elif type == 'csv':
            if curIndex != 0:
                self.tabWidget.setTabEnabled(0, True)
                self.tabWidget.setCurrentIndex(0)
            else:
                self.inspect()
        for i in range(self.tabWidget.count()):
            if type == 'text':
                if self.supported_types[i + 1][0] in ['csv', 'running', 'ilg']:
                    if self.isDirectory and self.supported_types[i + 1][0] == 'csv':
                        continue
                    self.tabWidget.setTabEnabled(i, True)
                else:
                    self.tabWidget.setTabEnabled(i, False)
            elif type == self.supported_types[i + 1][0]:
                self.tabWidget.setTabEnabled(i, True)
            else:
                self.tabWidget.setTabEnabled(i, False)

    def typeChanged(self):
        type_ = self.supported_types[self.tabWidget.currentIndex() + 1][0]
        if type_ == 'running':
            if self.runningSelect.currentText() == 'Orthography':
                type_ = 'spelling'
            else:
                type_ = 'transcription'
        elif type_ == 'multiple':
            if self.multSelect.currentText() == 'Buckeye':
                type_ = 'buckeye'
            # Now Buckeye is the only multiple type but others can be added later
            # else:
            #    type_ = 'timit'
        self.textType = type_
        if self.isDirectory:
            t = 'text'
            if type_ == 'textgrid':
                t = type_
            elif type_ == 'buckeye':
                t = 'multiple'
            self.pathWidget.updateType(t)

        self.inspect()

    def help(self):
        url = get_url(name='loading corpora',
                      section='creating-a-corpus')
        webbrowser.open(url)
        # self.helpDialog = HelpDialog(self,name = 'loading corpora',
        #                            section = 'using-a-custom-corpus')
        # self.helpDialog.exec_()

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
                except PCTEncodingError as error:
                    # when user tries to load a file with an unknown encoding
                    reply = QMessageBox.critical(self, "Error encountered", str(error))
                    self.updateColumnFrame([])
                    return
                except PCTError:
                    self.updateColumnFrame([])
                    return
                self.columnDelimiterEdit.setText(coldelim.encode('unicode_escape').decode('utf-8-sig'))
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
                elif self.textType == 'buckeye':
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
                atts, coldelim = inspect_csv(self.pathWidget.value(), coldelim=colDelim)
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
                annotation_types = inspect_discourse_ilg(self.pathWidget.value(), number=number)
                self.updateColumnFrame(annotation_types)

    def updateColumnFrame(self, atts):
        for i in reversed(range(self.columnFrame.layout().count() - 1)):
            w = self.columnFrame.layout().itemAt(i).widget()
            if w is None:
                del w
                continue
            w.setParent(None)
            w.deleteLater()
        self.columns = list()
        for a in reversed(atts):
            ignorable = self.textType not in ['spelling', 'transcription']
            c = AnnotationTypeWidget(a, ignorable=ignorable)
            if not ignorable:  # self.textType in ['spelling', 'transcription']:
                c.nameWidget.setEnabled(False)
            self.columns.append(c)
            self.columnFrame.layout().insertWidget(0, c)

        set_default_trans = False
        set_default_spell = False
        for c in reversed(self.columns):
            if not set_default_trans and c.typeWidget.currentText() == 'Transcription (alternative)':
                c.typeWidget.setCurrentIndex(c.typeWidget.findText('Transcription (default)'))
                set_default_trans = True
            if not set_default_spell and c.typeWidget.currentText() == 'Orthography (alternative)':
                c.typeWidget.setCurrentIndex(c.typeWidget.findText('Orthography (default)'))
                set_default_spell = True
            if set_default_spell and set_default_trans:
                break

    def generateKwargs(self):
        path = self.pathWidget.value()
        if path == '':
            reply = QMessageBox.critical(self,
                                         "Missing information",
                                         "Please specify a file or directory.")
            return

        if not os.path.exists(path):
            reply = QMessageBox.critical(self,
                                         "Invalid information",
                                         "The specified path to the corpus file does not exist.")
            return

        name = self.nameEdit.text()
        if name == '':
            reply = QMessageBox.critical(self,
                                         "Missing information",
                                         "Please specify a name for the corpus.")
            return

        if self.csvFeatureSystem.path() is not None and not os.path.exists(self.csvFeatureSystem.path()):
            featurename = os.path.split(self.csvFeatureSystem.path())[-1].split('.')[0]
            reply = QMessageBox.critical(self,
                                         'Missing information',
                                         'No feature file called {} could be found'.format(featurename))
            return

        kwargs = {'corpus_name': name, 'path': path, 'isDirectory': self.isDirectory, 'text_type': self.textType,
                  'annotation_types': [x.value() for x in reversed(self.columns)]}

        for x in kwargs['annotation_types']:
            if 'default' in x.name:
                if 'transcription' in x.name.lower() or 'orthography' in x.name.lower():
                    x.is_default = True
                    x.attribute.is_default = True
            else:
                x.is_default = False
                x.attribute.is_default = False

        # Prompting messages when users try to create a corpus from a file but requirements are not satisfied
        type_ = self.supported_types[self.tabWidget.currentIndex() + 1][0]
        if type_ == 'running':
            if self.runningSelect.currentText() == 'Transcribed':
                if not any([x.base for x in kwargs['annotation_types']]):
                    QMessageBox.critical(self,
                                         'Incompatible Information',
                                         'You have selected running text of type "Transcription" in the left window, '
                                         'but in the Parsing Preview window you did not select a transcription')
                    return

            elif self.runningSelect.currentText() == 'Orthography':
                if not any([x.anchor for x in kwargs['annotation_types']]):
                    QMessageBox.critical(self, 'Incompatible Information',
                                         'You have selected running text of type "Orthography" in the left window, '
                                         'but in the Parsing Preview window you did not select an orthography.')
                    return

        if type_ != 'ilg' and type_ != 'multiple' and type_ != 'textgrid':
            variant_tokens = [x.is_token_base for x in kwargs['annotation_types']]
            if any(variant_tokens):
                QMessageBox.critical(self,
                                     'Pronunciation variants not supported',
                                     ('You selected a transcription column to vary within words. However, your selected '
                                      'format cannot be used for creating a corpus with pronunciation variants.\n\n'
                                      'Currently, PCT supports pronunciation variants for an interlinear gloss file, '
                                      'praat TextGrid file or a specially formatted corpus, such as the Buckeye corpus. '
                                      'If you are dealing with one of these formats, please first change the left-hand '
                                      'side tab accordingly'))
                return

        if (not any([x.base for x in kwargs['annotation_types']])
                and not any([x.anchor for x in kwargs['annotation_types']])):
            QMessageBox.critical(self,
                                 'Missing information',
                                 ('No spelling or transcription was selected for the corpus. Please check the '
                                  '"Parsing Preview" section and ensure that you have a "default" Transcription '
                                  'or Orthography.'))
            return

        names = [x.name for x in kwargs['annotation_types']]
        if 'Transcription (alternative)' in names and 'Transcription (default)' not in names:
            QMessageBox.critical(self, 'Missing information',
                                 'You have selected an alternative transcription without selecting a default. Please '
                                 'go to the "Parsing Preview" section, and select one default transcription.')
            return

        if 'Orthography (alternative)' in names and 'Orthography (default)' not in names:
            QMessageBox.critical(self, 'Missing information',
                                 'You have selected an alternative orthography without selecting a default. Please '
                                 'go to the "Parsing Preview" section, and select one default orthography. If your '
                                 'corpus has no spelling system, then use "Other (character)" or "Notes".')
            return

        if any('Transcription' in x.name for x in kwargs['annotation_types']) and \
                all(x.attribute.name not in x.name for x in kwargs['annotation_types'] if
                    x.name in {'Transcription (default)', 'Transcription (alternative)'}):
            col_name_warning = QMessageBox.warning(self, 'Column name error',
                                                   'The column you selected as transcription is not named "Transcription". '
                                                   'Please rename the column and import the file again.',
                                                   QMessageBox.Ok)
            if col_name_warning == QMessageBox.Ok:
                return


        duplicates = False
        if names.count('Transcription (default)') > 1:
            duplicates = 'Transcription (default)'
        elif names.count('Orthography (default)') > 1:
            duplicates = 'Orthography (default)'
        elif names.count('Frequency') > 1:
            duplicates = 'Frequency'
        if type(duplicates) is str:
            if 'default' in duplicates:
                QMessageBox.critical(self, 'Duplicate information',
                                     (
                                         'You have more than one column with an Annotation Type set to {}. Please go to the "Parsing Preview" '
                                         'section to change this.\n\n'
                                         'A corpus can only have one "default" Transcription and Orthography. If your corpus contains '
                                         'more than one transcription or spelling systems, choose one default and set the others '
                                         'to "alternative".'.format(duplicates)))
            elif 'Frequency' in duplicates:
                QMessageBox.critical(self, 'Duplicate information',
                                     (
                                         'You have more than one column with an Annotation Type set to {}. Please go to the "Parsing Preview" '
                                         'section to change this.\n\n'
                                         'A corpus can only have one "Frequency" column. If your corpus contains '
                                         'more than one frequency systems, choose one as "Frequency" and set the others '
                                         'to "Numeric".'.format(duplicates)))
            return

        atts = [x.attribute.display_name for x in kwargs['annotation_types']]
        duplicates = list(set([x for x in atts if atts.count(x) > 1]))
        if duplicates:
            duplicates = ' and '.join(duplicates)
            QMessageBox.critical(self, 'Duplicate information',
                                 'You have more than one column named {} in your corpus. Please go to the '
                                 '"Parsing Preview" section and ensure that all columns have unique names.'.format(
                                     duplicates))
            return

        if self.textType == 'csv':
            kwargs['delimiter'] = codecs.getdecoder("unicode_escape")(
                self.columnDelimiterEdit.text()
            )[0]
            kwargs['feature_system_path'] = self.csvFeatureSystem.path()
        elif self.textType == 'textgrid':
            kwargs['feature_system_path'] = self.tgFeatureSystem.path()
        elif self.textType == 'spelling':
            (kwargs['support_corpus_path'], kwargs['ignore_case']) = self.runningLookupWidget.value()
        elif self.textType == 'transcription':
            kwargs['feature_system_path'] = self.runningFeatureSystem.path()
        elif self.textType == 'ilg':
            kwargs['feature_system_path'] = self.ilgFeatureSystem.path()
            # (kwargs['support_corpus_path'],
            #    kwargs['ignore_case']) = self.ilgLookupWidget.value()
        elif self.textType == 'buckeye':
            kwargs['feature_system_path'] = self.multFeatureSystem.path()
            if not self.isDirectory:
                base, ext = os.path.splitext(path)
                if ext == '.words':
                    phone_path = base + '.phones'
                if not os.path.exists(phone_path):
                    reply = QMessageBox.critical(self,
                                                 "Invalid information",
                                                 "The phone file for the specified words file does not exist.")
                    return
                kwargs['word_path'] = kwargs.pop('path')
                kwargs['phone_path'] = phone_path

        if (not self.textType == 'spelling' and
                not any(['Transcription' in x.name for x in kwargs['annotation_types']])):
            alert = QMessageBox(QMessageBox.Warning,
                                'No transcription selected',
                                'You did not select any transcription column for your corpus. '
                                'Without transcriptions, you will not be able to use some of PCT\'s analysis '
                                'functions. \nClick "OK" if you want to continue without transcriptions. \nClick '
                                '"Cancel" to go back.',
                                QMessageBox.NoButton, self)
            alert.addButton('OK', QMessageBox.AcceptRole)
            alert.addButton('Cancel', QMessageBox.RejectRole)
            alert.exec_()
            if alert.buttonRole(alert.clickedButton()) == QMessageBox.RejectRole:
                return
            else:
                kwargs['feature_system_path'] = None

        elif 'feature_system_path' in kwargs and kwargs['feature_system_path'] is None:
            alert = QMessageBox(QMessageBox.Warning,
                                'No feature file selected',
                                'You didn’t select any “Transcription and feature” file for your corpus. '
                                'You have two options:\n\n1. Select a pre-existing feature file from the list, even if it '
                                'doesn’t perfectly match your corpus’ system. PCT will warn you of the symbols that aren’t '
                                'recognized and assign default features to them; these can then be changed later.\n\n'
                                '2. Exit out of the “Import corpus” dialogue box, and download or create an appropriate '
                                'feature system by going to “File” > “Manage feature systems…”; once a system is available, '
                                'return to the “Import corpus” dialogue box and select that feature system.',
                                QMessageBox.NoButton, self)
            alert.addButton('OK', QMessageBox.AcceptRole)
            alert.exec_()
            if alert.buttonRole(alert.clickedButton()) == QMessageBox.AcceptRole:
                return

        if not any(['Frequency' in x.name for x in kwargs['annotation_types']]) and type_ == 'csv':
            # a column for freq is expected if creating corpus from csv:
            alert = QMessageBox(QMessageBox.Warning,
                                'No frequency selected',
                                'You didn’t select any frequency column for your corpus. \n'
                                'Click "OK" if you want to proceed, and PCT will create a new column for frequency. \n'
                                'Click "Cancel" to go back.',
                                QMessageBox.NoButton, self)
            alert.addButton('OK', QMessageBox.AcceptRole)
            alert.addButton('Cancel', QMessageBox.RejectRole)
            alert.exec_()
            if alert.buttonRole(alert.clickedButton()) == QMessageBox.RejectRole:
                return

        if name in get_corpora_list(self.settings['storage']):
            msgBox = QMessageBox(QMessageBox.Warning, "Duplicate name",
                                 "A corpus named '{}' already exists.  Overwrite?".format(name), QMessageBox.NoButton,
                                 self)
            msgBox.addButton("Overwrite", QMessageBox.AcceptRole)
            msgBox.addButton("Cancel", QMessageBox.RejectRole)
            if msgBox.exec_() != QMessageBox.AcceptRole:
                return None

        # if kwargs['feature_system_path'] = None

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

        if not result:
            self.progressDialog.cancelButton.setEnabled(True)
            self.progressDialog.cancelButton.setText('Cancel')
            return

        if result:
            if self.corpus is not None:
                # self.corpus is set in self.setResults(),
                # which is a slot connected to the LoadCorpusWorker dataReady signal
                if not hasattr(self.corpus, 'lexicon'):
                    # it's a Corpus object
                    c = self.corpus
                else:
                    # It's a Discourse object
                    c = self.corpus.lexicon
                    c.inventory.update_features(c.specifier)
                unmatched = list()
                for seg in c.inventory:
                    if seg.symbol in c.inventory.non_segment_symbols:
                        continue
                    if all(f == 'n' for f in seg.features.values()):
                        if seg.symbol in punctuation_names:
                            unmatched.append('{} ({})'.format(seg.symbol, punctuation_names[seg.symbol]))
                        else:
                            unmatched.append(seg.symbol)

                if unmatched and c.specifier is not None:
                    unmatched = ','.join(unmatched)
                    alert = QMessageBox()
                    alert.setWindowTitle('Warning')
                    alert.setText(('The following symbols in your corpus do not match up with any symbols in your '
                                   'selected {} feature system:\n{}\n\nThese symbols have been given default values of \'n\' for every '
                                   'feature. You can change these feature values in PCT by going to Features>View/Change feature '
                                   'system...'
                                   '\n\nIf this list contains your transcription delimiter, or if it contains symbols that should be '
                                   'part of a digraph, then it means that your parsing settings are incorrect. You can change these '
                                   'settings in the "Parsing Preview" section on the right-hand side.'
                                   '\n\nIf you see a very large number of symbols in the list, it is possible that you have selected '
                                   'the wrong feature system for your corpus.'.format(c.specifier.name, unmatched)))
                    alert.addButton('OK (load corpus with default features)', QMessageBox.AcceptRole)
                    alert.addButton('Cancel (return to previous window)', QMessageBox.RejectRole)
                    choice = alert.exec_()
                    if choice == QMessageBox.AcceptRole:
                        if hasattr(self.corpus, 'lexicon'):
                            self.corpus.lexicon.specifier.name = '_'.join([
                                self.corpus.lexicon.specifier.name, self.corpus.name])
                        else:
                            self.corpus.specifier.name = '_'.join([self.corpus.specifier.name, self.corpus.name])

                    else:
                        c = None
                        self.corpus = None
                        return

                save_binary(self.corpus, corpus_name_to_path(self.settings['storage'], self.corpus.name))
                if c.specifier is not None:
                    save_binary(c.specifier, system_name_to_path(self.settings['storage'], c.specifier.name))

                QDialog.accept(self)

    def updateName(self):
        """
        When creating a corpus from an external file/directory,
        this function   (i) updates the '(recommended) corpus name' and
                        (ii) passes the file extension info to updateType()
        """
        path = self.pathWidget.value()
        filename = os.path.split(path)[1]
        if os.path.isdir(path):
            self.isDirectory = True
            self.nameEdit.setText(filename)
            self.updateType(self.pathWidget.suggested_type)
            return
        name, ext = os.path.splitext(filename)
        ext = ext.lower()
        self.nameEdit.setText(name)
        self.isDirectory = False
        if ext == '.textgrid':
            self.updateType('textgrid')
        elif ext == '.csv':
            self.updateType('csv')
        elif ext == '.words':
            self.updateType('multiple')
        elif ext == '.txt':
            self.updateType('text')


class SubsetCorpusDialog(QDialog):
    def __init__(self, parent, corpus):
        QDialog.__init__(self, parent)

        self.corpus = corpus

        layout = QVBoxLayout()
        mainlayout = QFormLayout()

        self.nameEdit = QLineEdit()
        self.nameEdit.setText(corpus.name + '_subset')

        mainlayout.addRow(QLabel('Name for new corpus'), self.nameEdit)

        modeFrame = QGroupBox('Filter logic')
        modeLayout = QHBoxLayout()
        modeFrame.setLayout(modeLayout)

        self.logicGroup = QButtonGroup()
        andMode = QCheckBox('AND')
        andMode.clicked.connect(self.changeMode)
        andMode.setChecked(True)
        self.mode = 'andMode'
        self.logicGroup.addButton(andMode)
        orMode = QCheckBox('OR')
        orMode.clicked.connect(self.changeMode)
        self.logicGroup.addButton(orMode)
        self.logicGroup.setExclusive(True)
        self.logicGroup.setId(orMode, 0)
        self.logicGroup.setId(andMode, 1)

        modeLayout.addWidget(andMode)
        modeLayout.addWidget(orMode)
        mainlayout.addRow(modeFrame)

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
        self.setWindowTitle('Subset corpus')

    def changeMode(self):
        if self.logicGroup.checkedId() == 0:
            self.mode = 'orMode'
        else:
            self.mode = 'andMode'

    def help(self):
        url = get_url('loading corpora', section='subsetting-a-corpus')
        webbrowser.open(url)
        # self.helpDialog = HelpDialog(self, name='loading corpora', section='subsetting-a-corpus')
        # self.helpDialog.exec_()

    def accept(self):
        filters = self.filterWidget.value()
        name = self.nameEdit.text()
        if name == '':
            reply = QMessageBox.critical(self,
                                         'Missing information',
                                         'Please specify a name for the new corpus.')
            return None
        if len(filters) == 0:
            reply = QMessageBox.critical(self,
                                         'Missing information',
                                         'Please specify at least one filter.')
            return None

        new_corpus = self.corpus.subset(filters, self.mode)

        if len(new_corpus) == 0:
            reply = QMessageBox.critical(self,
                                         'Subcorpus empty',
                                         'Subcorpus generated is empty. '
                                         'Please change the filter specifications')
            return None

        if name in get_corpora_list(self.parent().settings['storage']):
            msgBox = QMessageBox(QMessageBox.Warning, 'Duplicate name',
                                 'A corpus named "{}" already exists.  Overwrite?'.format(name),
                                 QMessageBox.NoButton, self)
            msgBox.addButton('Overwrite', QMessageBox.AcceptRole)
            msgBox.addButton('Abort', QMessageBox.RejectRole)
            if msgBox.exec_() != QMessageBox.AcceptRole:
                return

        new_corpus.name = name
        new_corpus.set_feature_matrix(self.corpus.specifier)
        save_binary(new_corpus,
                    corpus_name_to_path(self.parent().settings['storage'], new_corpus.name))
        QMessageBox.information(self, 'Corpus subset created',
                                'Successfully generated a corpus subset. \nTo open it, go to "File > Load '
                                'corpus..." and select "{}".'.format(new_corpus.name),
                                QMessageBox.Ok, QMessageBox.Ok)
        QDialog.accept(self)


class ExportCorpusDialog(QDialog):
    variantOptions = [('Do not include', None),
                      ('Include in each word\'s line', 'column'),
                      ('Have a line for each variant', 'token')]

    def __init__(self, parent, corpus):
        QDialog.__init__(self, parent)

        self.corpus = corpus

        layout = QVBoxLayout()

        inlayout = QFormLayout()

        self.pathWidget = SaveFileWidget('Select file location', 'Text files (*.txt *.csv)')

        inlayout.addRow('File name:', self.pathWidget)

        self.columnDelimiterEdit = QLineEdit()
        self.columnDelimiterEdit.setText(',')

        inlayout.addRow('Column delimiter:', self.columnDelimiterEdit)

        self.transDelimiterEdit = QLineEdit()
        self.transDelimiterEdit.setText('.')

        inlayout.addRow('Transcription delimiter:', self.transDelimiterEdit)

        self.syllDelimiterEdit = QLineEdit()
        self.syllDelimiterEdit.setText('-')
        if len(self.corpus.inventory.syllables) == 0:  # if there's no syllable in the corpus,
            self.syllDelimiterEdit.setEnabled(False)   # then grey out the syllable delimiter option.
            self.syllDelimiterEdit.setText('')

        inlayout.addRow('Syllable delimiter:', self.syllDelimiterEdit)

        self.variantWidget = QComboBox()
        for o in self.variantOptions:
            self.variantWidget.addItem(o[0])

        if not self.corpus.has_wordtokens:
            self.variantWidget.setEnabled(False)

        inlayout.addRow('Exporting pronunciation variants', self.variantWidget)

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
        syllDelim = self.syllDelimiterEdit.text() if self.syllDelimiterEdit.text() != '' else None
        if colDelim == transDelim or colDelim == syllDelim or transDelim == syllDelim:
            reply = QMessageBox(QMessageBox.Warning,
                                "Invalid information", 'You used the same delimiter for column, transcription, or'
                                                       ' syllable.\nClick "OK" if you want to proceed, but you may lose'
                                                       ' information. \nClick "Cancel" to go back.',
                                QMessageBox.NoButton, self)
            reply.addButton('OK', QMessageBox.AcceptRole)
            reply.addButton('Cancel', QMessageBox.RejectRole)
            reply.exec_()
            if reply.buttonRole(reply.clickedButton()) == QMessageBox.RejectRole:
                return

        variant_behavior = self.variantOptions[self.variantWidget.currentIndex()][1]
        export_corpus_csv(self.corpus, filename, colDelim, transDelim, syllDelim, variant_behavior)

        # Success message
        QMessageBox.information(self, "Corpus exported",
                               f"You successfully exported the \'{self.corpus.name}\' corpus.\n"
                               f"It is saved as \'{filename}.\'",
                                QMessageBox.Ok, QMessageBox.Ok)
        QDialog.accept(self)
