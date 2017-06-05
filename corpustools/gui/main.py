# import faulthandler
# faulthandler.enable()
import os
import sys
import logging
import corpustools.gui.modernize as modernize
from PyQt5 import QtGui

from .imports import *

from .widgets import FileNameDialog

from .config import Settings, PreferencesDialog

from .views import (TreeWidget, DiscourseView, ResultsWindow,
                    LexiconView,PhonoSearchResults)

from .models import (CorpusModel, SpontaneousSpeechCorpusModel,
                    DiscourseModel, InventoryModel)

from .iogui import (CorpusLoadDialog, SubsetCorpusDialog, ExportCorpusDialog, save_binary)

from .corpusgui import (AddTierDialog, AddAbstractTierDialog,
                        RemoveAttributeDialog,AddColumnDialog,
                        AddCountColumnDialog,
                        AddWordDialog, CorpusSummary)

from .featuregui import (FeatureMatrixManager, EditFeatureMatrixDialog,
                        ExportFeatureSystemDialog)

from .inventorygui import InventoryManager

from corpustools.corpus.classes.lexicon import Corpus, Inventory, Word

from corpustools.corpus.classes.spontaneous import Discourse, SpontaneousSpeechCorpus

from corpustools.corpus.io.helper import get_corpora_list

from corpustools import __version__ as currentPCTversion


from .ssgui import SSDialog
from .asgui import ASDialog
from .flgui import FLDialog
from .fagui import FADialog
from .pdgui import PDDialog
from .ndgui import NDDialog
from .ppgui import PPDialog
from .psgui import PhonoSearchDialog
from .migui import MIDialog
from .klgui import KLDialog
from .infogui import InformativityDialog
from .autogui import AutoDialog
from .helpgui import AboutDialog, HelpDialog


class QApplicationMessaging(QApplication):
    messageFromOtherInstance = Signal(bytes)

    def __init__(self, argv):
        QApplication.__init__(self, argv)
        self._key = 'PCT'
        self._timeout = 1000
        self._locked = False
        socket = QLocalSocket(self)
        socket.connectToServer(self._key, QIODevice.WriteOnly)
        if not socket.waitForConnected(self._timeout):
            self._server = QLocalServer(self)
            # noinspection PyUnresolvedReferences
            self._server.newConnection.connect(self.handleMessage)
            self._server.listen(self._key)
        else:
            self._locked = True
        socket.disconnectFromServer()

    def __del__(self):
        if not self._locked:
            self._server.close()

    def event(self, e):
        if e.type() == QEvent.FileOpen:
            self.messageFromOtherInstance.emit(bytes(e.file(), 'UTF-8'))
            return True
        else:
            return QApplication.event(self, e)

    def isRunning(self):
        return self._locked

    def handleMessage(self):
        socket = self._server.nextPendingConnection()
        if socket.waitForReadyRead(self._timeout):
            self.messageFromOtherInstance.emit(socket.readAll().data())

    def sendMessage(self, message):
        socket = QLocalSocket(self)
        socket.connectToServer(self._key, QIODevice.WriteOnly)
        socket.waitForConnected(self._timeout)
        socket.write(bytes(message, 'UTF-8'))
        socket.waitForBytesWritten(self._timeout)
        socket.disconnectFromServer()

class MainWindow(QMainWindow):

    def __init__(self,app):
        app.messageFromOtherInstance.connect(self.handleMessage)
        super(MainWindow, self).__init__()

        self.unsavedChanges = False

        self.settings = Settings()
        logging.basicConfig(handlers = [logging.FileHandler(os.path.join(
                                self.settings.log_directory(), 'pct_gui.log'),
                            encoding = 'utf-8-sig',
                            mode = 'w')],
                            level = logging.INFO)

        self.showWarnings = True
        self.showToolTips = True

        self.resize(self.settings['size'])
        self.move(self.settings['pos'])

        self.corpusTable = LexiconView(self)
        self.corpusTable.wordsChanged.connect(self.enableSave)
        self.corpusTable.wordToBeEdited.connect(self.editWord)
        self.corpusTable.columnRemoved.connect(self.enableSave)
        self.discourseTree = TreeWidget(self)
        self.discourseTree.hide()
        self.textWidget = DiscourseView(self)
        self.textWidget.hide()
        #font = QFont("Courier New", 14)
        #self.corpusTable.setFont(font)
        splitter = QSplitter()
        splitter.addWidget(self.discourseTree)
        splitter.addWidget(self.corpusTable)
        splitter.addWidget(self.textWidget)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 1)
        self.wrapper = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(splitter)
        self.wrapper.setLayout(layout)
        self.setCentralWidget(self.wrapper)

        self.status = QLabel()
        self.status.setText("Ready")
        self.statusBar().addWidget(self.status, stretch=1)
        self.corpusStatus = QLabel()
        self.corpusStatus.setText("No corpus selected")
        self.statusBar().addWidget(self.corpusStatus)
        self.featureSystemStatus = QLabel()
        self.featureSystemStatus.setText("No feature system selected")
        self.statusBar().addWidget(self.featureSystemStatus)
        self.setWindowTitle("Phonological CorpusTools")
        iconPath = os.path.join(os.path.dirname(sys.modules[__name__].__file__), '../../resources/favicon.png')
        self.setWindowIcon(QtGui.QIcon(iconPath))
        self.createActions()
        self.createMenus()
        self.corpus = None
        self.corpusModel = None
        self.inventoryModel = None
        self.resultsCodes = ['FL', 'PD', 'FA', 'SS', 'AS', 'ND', 'PP', 'MI', 'KL', 'PhonoSearch', 'Auto', 'Informativity']
        for abbrv in self.resultsCodes:
            window_name = abbrv+'Window'
            setattr(self, window_name, None)
        self.setMinimumWidth(self.menuBar().sizeHint().width())

    def sizeHint(self):
        sz = QMainWindow.sizeHint(self)
        minWidth = self.menuBar().sizeHint().width()
        if sz.width() < minWidth:
            sz.setWidth(minWidth)
        if sz.height() < 400:
            sz.setHeight(400)
        return sz

    def handleMessage(self):
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        #self.raise_()
        #self.show()
        self.activateWindow()

    def check_for_unsaved_changes(function):
        def do_check(self):
            if self.corpusModel is None:
                pass
            elif self.unsavedChanges:
                if self.settings['ask_overwrite_corpus']:
                    name_hint = self.generate_corpus_name_hint()
                    reply = FileNameDialog(self.corpusModel.corpus.name, 'corpus', self.settings, hint=name_hint)
                    reply.exec_()

                    if reply.choice == 'saveas':
                        self.corpusModel.corpus.name = reply.getFilename()
                        self.saveCorpus()

                    elif reply.choice == 'overwrite':
                        self.saveCorpus()

                    self.settings['ask_overwrite_corpus'] = 0 if reply.stopShowing.isChecked() else 1
                else:
                    self.saveCorpus()
            function(self)
        return do_check

    def generate_corpus_name_hint(self):
        name_list = get_corpora_list(self.settings['storage'])
        name_hint = self.corpusModel.corpus.name.split('-')

        if len(name_hint) == 1 or not name_hint[-1].isdigit():
            name_hint = self.corpusModel.corpus.name + '-2'
        else:
            n = 2
            name = name_hint[0]
            while True:
                name_hint = '-'.join([name,str(n)])
                if name_hint not in name_list:
                    break
                n += 1
        return name_hint

    def check_for_empty_corpus(function):
        def do_check(self):
            if self.corpusModel is None or self.corpusModel.corpus is None:
                reply = QMessageBox.critical(self,
                        "Missing corpus", "There is no corpus loaded.")
                return
            else:
                function(self)
        return do_check

    def check_for_transcription(function):
        def do_check(self):
            if not self.corpusModel.corpus.has_transcription:
                reply = QMessageBox.critical(self,
                        "Missing transcription", "This corpus has no transcriptions, so the requested action cannot be performed.")
                return
            if self.inventoryModel is None:
                reply = QMessageBox.critical(self,
                        'Missing information', 'This menu option is not available without a feature system. Please go to '
                        'Features>View/Change feature system...')
                return
            else:
                function(self)
        return do_check

    def check_for_feature_system(func):
        def do_check(self):
            if self.corpusModel.corpus.specifier is None:
                reply = QMessageBox.critical(self, 'Missing information', 'This corpus has no feature file associated, '
                'so it is not possible to use this menu option.\nPlease associate a feature system with this corpus by '
                'going to Features > View/change feature system...')
                return
            else:
                func(self)
        return do_check

    def enableSave(self):
        self.unsavedChanges = True
        self.saveCorpusAct.setEnabled(True)

    def editWord(self, row, word):
        dialog = AddWordDialog(self, self.corpusModel.corpus, self.inventoryModel, word)
        if dialog.exec_():
            self.corpusModel.replaceWord(row, dialog.word)
            self.enableSave()

    def changeTextAndLexicon(self):
        index = self.discourseTree.selectionModel().currentIndex()
        name = self.discourseTree.model().data(index, Qt.DisplayRole)
        if name == 'All speakers':
            self.corpusTable.setModel(CorpusModel(self.corpusModel.corpus, self.settings))
            self.inventoryModel = None if self.corpusModel.corpus.specifier is None else self.generateInventoryModel()
            self.textWidget.hide()
        else:
            self.textWidget.show()
            self.changeText(name)
            self.changeLexicon(name)

    def changeText(self,name):
        discourse = self.corpusModel.corpus.discourses[name]
        self.textWidget.setModel(DiscourseModel(discourse, self.settings))

    def changeLexicon(self,name):
        corpus = self.corpusModel.corpus.discourses[name]
        self.corpusTable.setModel(CorpusModel(corpus.lexicon, self.settings))
        self.inventoryModel = None if self.corpusModel.corpus.specifier is None else self.generateInventoryModel()
        self.corpusStatus.setText('Corpus: {}'.format(corpus.name))
        name = corpus.lexicon.specifier.name if corpus.lexicon.specifier is not None else 'No feature system selected'

        self.featureSystemStatus.setText('Feature system: {}'.format(name))

    @check_for_unsaved_changes
    def loadCorpus(self):
        try:
            name = self.corpusModel.corpus.name
        except AttributeError:
            name = None

        dialog = CorpusLoadDialog(self, name, self.settings)
        result = dialog.exec_()
        if result:
            self.corpus = dialog.corpus
            self.inventoryModel = None
            if hasattr(self.corpus, 'lexicon'):
                # the lexicon attribute is a Corpus object
                self.corpus.lexicon = self.compatibility_check(self.corpus.lexicon)

                if hasattr(self.corpus,'discourses'):
                    self.discourseTree.show()
                    self.discourseTree.setModel(SpontaneousSpeechCorpusModel(self.corpus))
                    self.discourseTree.selectionModel().selectionChanged.connect(self.changeTextAndLexicon)
                    self.showDiscoursesAct.setEnabled(True)
                    self.showDiscoursesAct.setChecked(True)
                    if self.textWidget.model() is not None:
                        self.textWidget.model().deleteLater()
                else:
                    self.textWidget.setModel(DiscourseModel(self.corpus, self.settings))
                    #self.textWidget is a DiscourseView object
                    self.discourseTree.hide()
                    self.showDiscoursesAct.setEnabled(False)
                    self.showDiscoursesAct.setChecked(False)

                self.corpusTable.selectTokens.connect(self.textWidget.highlightTokens)
                self.textWidget.selectType.connect(self.corpusTable.highlightType)
                self.textWidget.show()
                self.showTextAct.setEnabled(True)
                self.showTextAct.setChecked(True)

            else:#nothing special, just a corpus
                self.corpus = self.compatibility_check(self.corpus)
                self.textWidget.hide()
                self.discourseTree.hide()
                self.showTextAct.setEnabled(False)
                self.showTextAct.setChecked(False)
                self.showDiscoursesAct.setEnabled(False)
                self.showDiscoursesAct.setChecked(False)
                if self.textWidget.model() is not None:
                    self.textWidget.model().deleteLater()

            if not hasattr(self.corpus, 'lexicon'):
                specifier_check = self.corpus.specifier
            else:
                specifier_check = self.corpus.lexicon.specifier

            if specifier_check is not None:
                self.featureSystemStatus.setText('Feature system: {}'.format(specifier_check.name))
            else:
                self.featureSystemStatus.setText('No feature system selected')
                alert = QMessageBox()
                alert.setWindowTitle('Missing corpus information')
                alert.setText('Your corpus was loaded without a transcription or feature system. '
                              'The majority of PCT\'s analysis functions require this information to work correctly. '
                              'Go to Features > View/Change feature system... to select one.\n '
                              'If you do not have any feature files available at all, you can '
                              'download one by going to File > Manage feature systems...\n'
                              'If your corpus only contains spelling, and not transcription, then you can ignore this '
                              'warning, although you will still have limited access to PCT analysis functions.')
                alert.addButton('OK', QMessageBox.AcceptRole)
                alert.exec_()
            self.corpusModel = CorpusModel(self.corpus, self.settings)
            self.corpusTable.setModel(self.corpusModel)
            self.corpusStatus.setText('Corpus: {}'.format(self.corpus.name))
            self.inventoryModel = None if specifier_check is None else self.generateInventoryModel()
            self.corpusModel.corpus.inventory.isNew = False
            self.saveCorpus()
            self.unsavedChanges = False
            self.saveCorpusAct.setEnabled(False)
            self.createSubsetAct.setEnabled(True)
            self.exportCorpusAct.setEnabled(True)
            self.exportFeatureSystemAct.setEnabled(True)

    def generateInventoryModel(self):
        if not hasattr(self.corpusModel.corpus.inventory, 'segs'):
            return None

        if self.corpusModel.corpus.inventory.isNew:
            # just loaded from a text file
            inventoryModel = InventoryModel(self.corpusModel.corpus.inventory, copy_mode=False)
            inventoryModel.updateFeatures(self.corpusModel.corpus.specifier)

        else:
            # just loaded a .corpus file, not from text
            inventoryModel = InventoryModel(self.corpusModel.corpus.inventory, copy_mode=True)

        return inventoryModel


    # def forceUpdate(self, corpus):
    #     corpus = Corpus(corpus.name, update=corpus)
    #
    #     if not hasattr(corpus.inventory, 'segs'):
    #         corpus.inventory = modernize.modernize_inventory_attributes(corpus.inventory)
    #     corpus.inventory = Inventory(update=corpus.inventory)
    #
    #     word_list = list()
    #     for word in corpus:
    #         word2 = Word(update=word)
    #         word_list.append(word2)
    #     corpus.update_wordlist(word_list)
    #
    #     print('updated!')
    #     return corpus

    def compatibility_check(self, corpus):
        update_corpus, update_inventory, update_words = False, False, False
        for attribute in Corpus.corpus_attributes:
            if not hasattr(corpus, attribute):
                update_corpus = True
                break
        for attribute in Inventory.inventory_attributes:
            if not hasattr(corpus.inventory, attribute):
                update_inventory = True
                break
        word = corpus.random_word()

        for attribute in Word.word_attributes:
            if not hasattr(word, attribute):
                update_words = True
                break
            if not hasattr(word, 'Frequency'):
                update_words = True
                break
        if update_corpus:
            corpus = Corpus(corpus.name, update=corpus)
        if update_inventory:
            if not hasattr(corpus.inventory, 'segs'):
                corpus.inventory = modernize.modernize_inventory_attributes(corpus.inventory)
            corpus.inventory = Inventory(update=corpus.inventory)
        if update_words:
            word_list = list()
            for word in corpus:
                word2 = Word(update=word)
                word_list.append(word2)
            corpus.update_wordlist(word_list)
        return corpus

    def loadFeatureMatrices(self):
        try:
            current_system = self.corpusModel.corpus.specifier.name
        except AttributeError:
            current_system = None
        dialog = FeatureMatrixManager(self, self.settings, current_system)
        result = dialog.exec_()
        if result:
            pass

    @check_for_empty_corpus
    @check_for_feature_system
    def manageInventoryChart(self):
        copy_model = InventoryModel(self.inventoryModel, copy_mode=True)
        if not self.inventoryModel._data:
            alert = QMessageBox()
            alert.setWindowTitle('Warning!')
            alert.setText('There was a problem loading your inventory. You can normally fix this problem by going '
            'to Features > View/Edit feature system... and then simply clicking "Save changes" (you do not actually '
            'need to make any changes). Sorry about that!')
            alert.addButton('OK', QMessageBox.AcceptRole)
            alert.exec_()
            return
        dialog = InventoryManager(copy_model)
        result = dialog.exec_()
        if result:
            self.inventoryModel.updateFromCopy(dialog.inventory)
            #self.corpusModel.corpus.inventory.__dict__.update(self.inventoryModel.__dict__)
            # shouldn't need to save, since this doesn't affect the corpus, only the FeatureMatrix, and there's
            # already a check for that in the InventoryManager dialog
            if self.settings['ask_overwrite_corpus']:
                self.enableSave()
            else:
                self.saveCorpus()
                self.saveCorpusAct.setEnabled(False)


    def subsetCorpus(self):
        dialog = SubsetCorpusDialog(self,self.corpusModel.corpus)
        result = dialog.exec_()
        if result:
            pass

    def saveCorpus(self):

        self.corpusModel.corpus.inventory.save(self.inventoryModel)
        save_binary(self.corpus, os.path.join(self.settings['storage'], 'CORPUS', self.corpus.name+'.corpus') )

        if self.corpusModel.corpus.specifier is not None:
            save_binary(self.corpusModel.corpus.specifier,
                    os.path.join(self.settings['storage'], 'FEATURE', self.corpusModel.corpus.specifier.name+'.feature'))
        self.saveCorpusAct.setEnabled(False)
        self.unsavedChanges = False

    def exportCorpus(self):
        dialog = ExportCorpusDialog(self,self.corpusModel.corpus)
        result = dialog.exec_()
        if result:
            pass

    def exportFeatureMatrix(self):
        dialog = ExportFeatureSystemDialog(self,self.corpusModel.corpus)
        result = dialog.exec_()
        if result:
            pass

    @check_for_empty_corpus
    def showPreferences(self):
        dialog = PreferencesDialog(self, self.settings)
        if dialog.exec_():
            self.settings = dialog.settings

    @check_for_empty_corpus
    def showFeatureSystem(self):
        try:
            oldSystem = self.corpusModel.corpus.specifier.name
        except AttributeError:
            oldSystem = None
        dialog = EditFeatureMatrixDialog(self, self.corpusModel.corpus, self.settings)
        results = dialog.exec_()
        if results:
            #if going from None to a feature system
            if self.corpusModel.corpus.specifier is None and dialog.specifier is not None:
                self.corpusModel.corpus.set_feature_matrix(dialog.specifier)
                self.corpusModel.corpus.update_features()
                self.inventoryModel = InventoryModel(self.corpusModel.corpus.inventory)
                self.featureSystemStatus.setText(dialog.specifier.name)
                self.saveCorpus()
                return

            #if going from a feature system to None
            if dialog.specifier is None:
                self.corpusModel.corpus.specifier = None
                self.inventoryModel = None
                self.saveCorpus()
                return

            #if changing feature systems
            if dialog.specifier is not None:
                self.corpusModel.corpus.set_feature_matrix(dialog.specifier)
                if dialog.transcription_changed:
                    #This block is currently unreachable, due to the RestrictedFeatureSelectSystem
                    #The code should be left alone in case we later choose to move back to the nonRestricted type
                    #RestrictedFeatureSystems are those where the transcription and features are necessarily linked
                    #In a nonRestricted system the transcription and features can be independantly selected and
                    #the corpus will get automatically retranscribed
                    self.corpusModel.corpus.retranscribe(dialog.segmap)#this also updates the corpus inventory
                    self.inventoryModel.updateInventory(list(self.corpusModel.corpus.inventory.segs.keys()))

                self.corpusModel.corpus.update_features()
                preserveFeatures = True if dialog.specifier.name == oldSystem else False
                self.inventoryModel.updateFeatures(dialog.specifier, preserve_features = preserveFeatures)

            if dialog.feature_system_changed:
                self.inventoryModel.reGenerateNames()

            if self.corpusModel.corpus.specifier is not None:
                self.featureSystemStatus.setText('Feature system: {}'.format(self.corpusModel.corpus.specifier.name))
            else:
                self.featureSystemStatus.setText('No feature system selected')
            self.saveCorpus()

    @check_for_empty_corpus
    @check_for_transcription
    def createTier(self):
        dialog = AddTierDialog(self, self.corpusModel.corpus, self.inventoryModel)
        if dialog.exec_():
            self.corpusModel.addTier(dialog.attribute, dialog.segList)
            if self.settings['ask_overwrite_corpus']:
                self.enableSave()
            else:
                self.saveCorpus()
                self.saveCorpusAct.setEnabled(False)
            self.adjustSize()

    @check_for_empty_corpus
    @check_for_transcription
    def createAbstractTier(self):
        dialog = AddAbstractTierDialog(self, self.corpusModel.corpus, self.inventoryModel)
        if dialog.exec_():
            self.corpusModel.addAbstractTier(dialog.attribute, dialog.segList)
            if self.settings['ask_overwrite_corpus']:
                self.enableSave()
            else:
                self.saveCorpus()
                self.saveCorpusAct.setEnabled(False)
            self.adjustSize()

    @check_for_empty_corpus
    def createColumn(self):
        dialog = AddColumnDialog(self, self.corpusModel.corpus)
        if dialog.exec_():
            self.corpusModel.addColumn(dialog.attribute)
            if self.settings['ask_overwrite_corpus']:
                self.enableSave()
            else:
                self.saveCorpus()
                self.saveCorpusAct.setEnabled(False)

    @check_for_empty_corpus
    def createCountColumn(self):
        dialog = AddCountColumnDialog(self, self.corpusModel.corpus, self.inventoryModel)
        if dialog.exec_():
            self.corpusModel.addCountColumn(dialog.attribute, dialog.sequenceType, dialog.segList)
            if self.settings['ask_overwrite_corpus']:
                self.enableSave()
            else:
                self.saveCorpus()
                self.saveCorpusAct.setEnabled(False)


    @check_for_empty_corpus
    @check_for_transcription
    def removeAttribute(self):
        dialog = RemoveAttributeDialog(self, self.corpusModel.corpus)
        if dialog.exec_():
            self.corpusModel.removeAttributes(dialog.tiers)
            self.adjustSize()

            if self.settings['ask_overwrite_corpus']:
                self.enableSave()
            else:
                self.saveCorpus()
                self.saveCorpusAct.setEnabled(False)


    @check_for_empty_corpus
    def stringSim(self):
        dialog = SSDialog(self, self.settings, self.corpusModel, self.inventoryModel, self.showToolTips)
        result = dialog.exec_()
        if result:
            if self.SSWindow is not None and dialog.update and self.SSWindow.isVisible():
                self.SSWindow.table.model().addData(dialog.results)
            else:
                self.SSWindow = ResultsWindow('String similarity results',dialog,self)
                self.SSWindow.show()
                self.showSSResults.triggered.connect(self.SSWindow.raise_)
                self.showSSResults.triggered.connect(self.SSWindow.activateWindow)
                self.SSWindow.rejected.connect(lambda: self.showSSResults.setVisible(False))
                self.showSSResults.setVisible(True)

    @check_for_empty_corpus
    @check_for_transcription
    def freqOfAlt(self):
        dialog = FADialog(self, self.settings, self.corpusModel.corpus, self.inventoryModel, self.showToolTips)
        result = dialog.exec_()
        if result:
            if self.FAWindow is not None and dialog.update and self.FAWindow.isVisible():
                self.FAWindow.table.model().addRows(dialog.results)
            else:
                self.FAWindow = ResultsWindow('Frequency of alternation results',dialog,self)
                self.FAWindow.show()
                self.showFAResults.triggered.connect(self.FAWindow.raise_)
                self.showFAResults.triggered.connect(self.FAWindow.activateWindow)
                self.FAWindow.rejected.connect(lambda: self.showFAResults.setVisible(False))
                self.showFAResults.setVisible(True)

    @check_for_empty_corpus
    @check_for_transcription
    def predOfDist(self):
        dialog = PDDialog(self, self.settings, self.corpusModel.corpus, self.inventoryModel, self.showToolTips)
        result = dialog.exec_()
        if result:
            if self.PDWindow is not None and self.PDWindow.isVisible():
                self.PDWindow.table.model().addRows(dialog.results)
            else:
                self.PDWindow = ResultsWindow('Predictability of distribution results',dialog,self)
                self.PDWindow.show()
                self.showPDResults.triggered.connect(self.PDWindow.raise_)
                self.showPDResults.triggered.connect(self.PDWindow.activateWindow)
                self.PDWindow.rejected.connect(lambda: self.showPDResults.setVisible(False))
                self.showPDResults.setVisible(True)

    @check_for_empty_corpus
    @check_for_transcription
    def funcLoad(self):
        dialog = FLDialog(self, self.settings, self.corpusModel.corpus, self.inventoryModel, self.showToolTips)
        result = dialog.exec_()
        if result:
            if self.FLWindow is not None and dialog.update and self.FLWindow.isVisible():
                self.FLWindow.table.model().addRows(dialog.results)
            else:
                self.FLWindow = ResultsWindow('Functional load results',dialog,self)
                self.FLWindow.show()
                self.showFLResults.triggered.connect(self.FLWindow.raise_)
                self.showFLResults.triggered.connect(self.FLWindow.activateWindow)
                self.FLWindow.rejected.connect(lambda: self.showFLResults.setVisible(False))
                self.showFLResults.setVisible(True)

    @check_for_empty_corpus
    @check_for_transcription
    def kullbackLeibler(self):
        dialog = KLDialog(self, self.settings, self.corpusModel.corpus, self.inventoryModel, self.showToolTips)
        result = dialog.exec_()
        if result:
            if self.KLWindow is not None and dialog.update and self.KLWindow.isVisible():
                self.KLWindow.table.model().addRows(dialog.results)
            else:
                self.KLWindow = ResultsWindow('Kullback Leibler results', dialog, self)
                self.KLWindow.show()
                self.showKLResults.triggered.connect(self.KLWindow.raise_)
                self.showKLResults.triggered.connect(self.KLWindow.activateWindow)
                self.KLWindow.rejected.connect(lambda: self.showKLResults.setVisible(False))
                self.showKLResults.setVisible(True)

    @check_for_empty_corpus
    @check_for_transcription
    def autoAnalysis(self):
        dialog = AutoDialog(self, self.corpusModel.corpus, self.inventoryModel, self.settings, self.showToolTips)
        dialog.exec_()


    @check_for_empty_corpus
    def informativity(self):
        dialog = InformativityDialog(self, self.settings, self.corpusModel.corpus, self.inventoryModel, self.showToolTips)
        result = dialog.exec_()
        if result:
            if self.InformativityWindow is not None and dialog.update and self.InformativityIWindow.isVisible():
                self.InformativityWindow.table.model().addRows(dialog.results)
            else:
                self.InformativityWindow = ResultsWindow('Mutual information results',dialog,self)
                self.InformativityWindow.show()
                self.showInformativityResults.triggered.connect(self.InformativityWindow.raise_)
                self.showInformativityResults.triggered.connect(self.InformativityWindow.activateWindow)
                self.InformativityWindow.rejected.connect(lambda: self.showInformativityResults.setVisible(False))
                self.showInformativityResults.setVisible(True)

    @check_for_empty_corpus
    @check_for_transcription
    def mutualInfo(self):
        dialog = MIDialog(self, self.settings, self.corpusModel.corpus, self.inventoryModel, self.showToolTips)
        result = dialog.exec_()
        if result:
            if self.MIWindow is not None and dialog.update and self.MIWindow.isVisible():
                self.MIWindow.table.model().addRows(dialog.results)
            else:
                self.MIWindow = ResultsWindow('Mutual information results',dialog,self)
                self.MIWindow.show()
                self.showMIResults.triggered.connect(self.MIWindow.raise_)
                self.showMIResults.triggered.connect(self.MIWindow.activateWindow)
                self.MIWindow.rejected.connect(lambda: self.showMIResults.setVisible(False))
                self.showMIResults.setVisible(True)

    def acousticSim(self):
        dialog = ASDialog(self, self.settings, self.showToolTips)
        result = dialog.exec_()
        if result:
            if self.ASWindow is not None and dialog.update and self.ASWindow.isVisible():
                self.ASWindow.table.model().addRows(dialog.results)
            else:
                self.ASWindow = ResultsWindow('Acoustic similarity results',dialog,self)
                self.ASWindow.show()
                self.showASResults.triggered.connect(self.ASWindow.raise_)
                self.showASResults.triggered.connect(self.ASWindow.activateWindow)
                self.ASWindow.rejected.connect(lambda: self.showASResults.setVisible(False))
                self.showASResults.setVisible(True)

    @check_for_empty_corpus
    def neighDen(self):
        dialog = NDDialog(self, self.settings, self.corpusModel, self.inventoryModel, self.showToolTips)
        result = dialog.exec_()
        if result and dialog.results:
            if self.NDWindow is not None and dialog.update and self.NDWindow.isVisible():
                self.NDWindow.table.model().addRows(dialog.results)
            else:
                self.NDWindow = ResultsWindow('Neighborhood density results',dialog,self)
                self.NDWindow.show()
                self.showNDResults.triggered.connect(self.NDWindow.raise_)
                self.showNDResults.triggered.connect(self.NDWindow.activateWindow)
                self.NDWindow.rejected.connect(lambda: self.showNDResults.setVisible(False))
                self.showNDResults.setVisible(True)
        elif result:
            if self.settings['ask_overwrite_corpus']:
                self.enableSave()
            else:
                self.saveCorpus()
                self.saveCorpusAct.setEnabled(False)

    @check_for_empty_corpus
    @check_for_transcription
    def phonoProb(self):
        dialog = PPDialog(self, self.settings, self.corpusModel, self.inventoryModel, self.showToolTips)
        result = dialog.exec_()
        if result and dialog.results:
            if self.PPWindow is not None and dialog.update and self.PPWindow.isVisible():
                self.PPWindow.table.model().addRows(dialog.results)
            else:
                self.PPWindow = ResultsWindow('Phonotactic probability results', dialog,self)
                self.PPWindow.show()
                self.showPPResults.triggered.connect(self.PPWindow.raise_)
                self.showPPResults.triggered.connect(self.PPWindow.activateWindow)
                self.PPWindow.rejected.connect(lambda: self.showPPResults.setVisible(False))
                self.showPPResults.setVisible(True)
        elif result:
            if self.settings['ask_overwrite_corpus']:
                self.enableSave()
            else:
                self.saveCorpus()
                self.saveCorpusAct.setEnabled(False)


    @check_for_empty_corpus
    @check_for_transcription
    def phonoSearch(self):
        dialog = PhonoSearchDialog(self, self.settings, self.corpusModel.corpus, self.inventoryModel, self.showToolTips)
        result = dialog.exec_()
        if result:
            if self.PhonoSearchWindow is not None and dialog.update and self.PhonoSearchWindow.isVisible():
                self.PhonoSearchWindow.table.model().addRows(dialog.results)
            else:
                self.PhonoSearchWindow = PhonoSearchResults(
                                'Phonological search results',dialog,self)
                self.PhonoSearchWindow.show()
                self.showSearchResults.triggered.connect(self.PhonoSearchWindow.raise_)
                self.showSearchResults.triggered.connect(self.PhonoSearchWindow.activateWindow)
                self.PhonoSearchWindow.rejected.connect(lambda: self.showSearchResults.setVisible(False))
                self.showSearchResults.setVisible(True)

    def createWord(self):
        dialog = AddWordDialog(self, self.corpusModel.corpus, self.inventoryModel)
        if dialog.exec_():
            self.corpusModel.addWord(dialog.word)
            self.enableSave()

    def toggleWarnings(self):
        self.showWarnings = not self.showWarnings

    def toggleToolTips(self):
        self.showToolTips = not self.showToolTips

    def toggleInventory(self):
        pass

    def toggleText(self):
        if self.showTextAct.isChecked():
            self.textWidget.show()
        else:
            self.textWidget.hide()

    def toggleDiscourses(self):
        if self.showDiscoursesAct.isChecked():
            self.discourseTree.show()
        else:
            self.discourseTree.hide()

    def about(self):
        dialog = AboutDialog(self)
        dialog.exec_()
        #dialog.show()

    def help(self):
        dialog = HelpDialog(self)
        dialog.exec_()

    def checkForUpdates(self):
        if getattr(sys, "frozen", False):
            release_url = "https://github.com/PhonologicalCorpusTools/CorpusTools/releases"
            from .versioning import VERSION, parse_version, find_versions
            best_version = VERSION
            best_version_p = parse_version(VERSION)
            for version in find_versions(release_url):
                version_p = parse_version(version)
                if version_p > best_version_p:
                    best_version_p = version_p
                    best_version = version
            msgBox = QMessageBox(self)
            msgBox.setTextFormat(Qt.RichText)

            if best_version == VERSION:
                title = "Up to date"
                message = "The current version ({}) is the latest released.".format(VERSION)
            else:
                if sys.platform == 'darwin':
                    installer = 'Phonological.CorpusTools-{}.dmg'.format(best_version)
                else:
                    installer = 'PhonologicalCorpusTools_win64_{}.exe'.format(best_version)
                title = "Update available"
                message = ("A new release (v{}) is available (current is v{}). "
                        "Please download the {} file from our <a href= '{}'>releases "
                        "page</a> if you would like to upgrade.").format(best_version,
                                                                    VERSION,
                                                                    installer,
                                                                    release_url)
            msgBox.setText(message)
            msgBox.setWindowTitle(title)
            msgBox.setStandardButtons(QMessageBox.Ok)
            result = msgBox.exec_()


    @check_for_empty_corpus
    def corpusSummary(self):
        dialog = CorpusSummary(self,self.corpusModel.corpus, self.inventoryModel, self.corpusModel.columns)
        result = dialog.exec_()

    def createActions(self):

        self.loadCorpusAct = QAction( "L&oad corpus...",
                self, shortcut=QKeySequence.Open,
                statusTip="Load a corpus", triggered=self.loadCorpus)

        self.manageFeatureSystemsAct = QAction( "Manage feature systems...",
                self,
                statusTip="Manage feature systems", triggered=self.loadFeatureMatrices)

        self.manageInventoryAct = QAction ( "Manage inventory chart...",
                self,
                statusTip="Manage inventory chart", triggered=self.manageInventoryChart)

        self.createSubsetAct = QAction( "Generate a corpus subset",
                self,
                statusTip="Create and save a subset of the current corpus", triggered=self.subsetCorpus)
        self.createSubsetAct.setEnabled(False)

        self.saveCorpusAct = QAction( "Save corpus",
                self,
                statusTip="Save corpus", triggered=self.saveCorpus)
        self.saveCorpusAct.setEnabled(False)

        self.exportCorpusAct = QAction( "Export corpus as text file (use with spreadsheets etc.)...",
                self,
                statusTip="Export corpus", triggered=self.exportCorpus)
        self.exportCorpusAct.setEnabled(False)

        self.exportFeatureSystemAct = QAction( "Export feature system as text file...",
                self,
                statusTip="Export feature system", triggered=self.exportFeatureMatrix)
        self.exportFeatureSystemAct.setEnabled(False)

        self.editPreferencesAct = QAction( "Preferences...",
                self,
                statusTip="Edit preferences", triggered=self.showPreferences)

        self.viewFeatureSystemAct = QAction( "View/change feature system...",
                self,
                statusTip="View feature system", triggered=self.showFeatureSystem)

        self.summaryAct = QAction( "Summary",
                self,
                statusTip="Summary of corpus", triggered=self.corpusSummary)

        self.addWordAct = QAction( "Add new word...",
                self,
                statusTip="Add new word", triggered=self.createWord)

        self.addTierAct = QAction( "Add tier...",
                self,
                statusTip="Add tier", triggered=self.createTier)

        self.addAbstractTierAct = QAction( "Add abstract tier...",
                self,
                statusTip="Add abstract tier", triggered=self.createAbstractTier)

        self.addCountColumnAct = QAction( "Add count column...",
                self,
                statusTip="Add count column", triggered=self.createCountColumn)

        self.addColumnAct = QAction( "Add column...",
                self,
                statusTip="Add column", triggered=self.createColumn)

        self.removeAttributeAct = QAction( "Remove tier or column...",
                self,
                statusTip="Remove tier or column", triggered=self.removeAttribute)

        self.phonoSearchAct = QAction( "Phonological search...",
                self,
                statusTip="Search transcriptions", triggered=self.phonoSearch)

        self.neighDenAct = QAction( "Calculate neighborhood density...",
                self,
                statusTip="Calculate neighborhood density", triggered=self.neighDen)

        self.phonoProbAct = QAction( "Calculate phonotactic probability...",
                self,
                statusTip="Calculate phonotactic probability", triggered=self.phonoProb)

        self.stringSimFileAct = QAction( "Calculate string similarity...",
                self,
                statusTip="Calculate string similarity for a file of string pairs")#, triggered=self.stringSim)

        self.stringSimAct = QAction( "Calculate string similarity...",
                self,
                statusTip="Calculate string similarity for corpus", triggered=self.stringSim)

        self.informativityAct = QAction("Calculate informativity...",
                self,
                statusTip="Calculate informativity for segments in the inventory", triggered=self.informativity)

        self.freqaltAct = QAction( "Calculate frequency of alternation...",
                self,
                statusTip="Calculate frequency of alternation", triggered=self.freqOfAlt)

        self.prodAct = QAction( "Calculate predictability of distribution...",
                self,
                statusTip="Calculate predictability of distribution", triggered=self.predOfDist)

        self.funcloadAct = QAction( "Calculate functional load...",
                self,
                statusTip="Calculate functional load", triggered=self.funcLoad)

        self.klAct = QAction( "Calculate Kullback-Leibler...",
                self,
                statusTip="Compare distributions", triggered=self.kullbackLeibler)

        self.mutualInfoAct = QAction( "Calculate mutual information...",
                self,
                statusTip="Calculate mutual information", triggered=self.mutualInfo)

        self.acousticSimFileAct = QAction( "Calculate acoustic similarity (for files)...",
                self,
                statusTip="Calculate acoustic similarity for files", triggered=self.acousticSim)

        self.acousticSimAct = QAction( "Calculate acoustic similarity (from corpus)...",
                self,
                statusTip="Calculate acoustic similarity for corpus")#, triggered=self.acousticSim)

        self.autoAnalysisAct = QAction( "Look for phonological patterns...",
                self,
                statusTip = "Look for phonological patterns", triggered = self.autoAnalysis)

        self.toggleWarningsAct = QAction( "Show warnings",
                self,
                statusTip="Show warnings", triggered=self.toggleWarnings)
        self.toggleWarningsAct.setCheckable(True)
        if self.showWarnings:
            self.toggleWarningsAct.setChecked(True)

        self.toggleToolTipsAct = QAction( "Show tooltips",
                self,
                statusTip="Show tooltips", triggered=self.toggleToolTips)
        self.toggleToolTipsAct.setCheckable(True)
        if self.showToolTips:
            self.toggleToolTipsAct.setChecked(True)

        self.showInventoryAct = QAction( "Show inventory",
                self,
                statusTip="Show inventory", triggered=self.toggleInventory)
        self.showInventoryAct.setCheckable(True)

        self.showTextAct = QAction( "Show corpus text",
                self,
                statusTip="Show text", triggered=self.toggleText)
        self.showTextAct.setCheckable(True)
        self.showTextAct.setEnabled(False)

        self.showDiscoursesAct = QAction( "Show corpus discourses",
                self,
                statusTip="Show discourses", triggered=self.toggleDiscourses)
        self.showDiscoursesAct.setCheckable(True)
        self.showDiscoursesAct.setEnabled(False)

        self.quitAct = QAction("&Quit", self, shortcut="Ctrl+Q",
                statusTip="Quit the application", triggered=self.close)

        self.aboutAct = QAction("&About", self,
                statusTip="Show the application's About box",
                triggered=self.about)

        self.helpAct = QAction("&Help", self,
                statusTip="Help information",
                triggered=self.help)

        self.updateAct = QAction("Check for updates...", self,
                statusTip="Check for updates",
                triggered=self.checkForUpdates)

        self.showSearchResults = QAction("Phonological search results", self)
        self.showSearchResults.setVisible(False)

        self.showSSResults = QAction("String similarity results", self)
        self.showSSResults.setVisible(False)

        self.showMIResults = QAction("Mutual information results", self)
        self.showMIResults.setVisible(False)

        self.showASResults = QAction("Acoustic similarity results", self)
        self.showASResults.setVisible(False)

        self.showFLResults = QAction("Functional load results", self)
        self.showFLResults.setVisible(False)

        self.showKLResults = QAction("Kullback-Leibler results", self)
        self.showKLResults.setVisible(False)

        self.showFAResults = QAction("Frequency of alternation results", self)
        self.showFAResults.setVisible(False)

        self.showPDResults = QAction("Predictability of distribution results", self)
        self.showPDResults.setVisible(False)

        self.showNDResults = QAction("Neighborhood density results", self)
        self.showNDResults.setVisible(False)

        self.showPPResults = QAction("Phonotactic probability results", self)
        self.showPPResults.setVisible(False)

        self.showAutoResults = QAction("Automatic phonological analysis results", self)
        self.showAutoResults.setVisible(False)

        self.showInformativityResults = QAction("Informativity results", self)
        self.showInformativityResults.setVisible(False)

        self.closeResultsWindowsAct = QAction("Close all open results windows", self,
                                           triggered=self.closeResultsWindows)

        self.goToMainWindowAct = QAction("Bring the main window to the front", self,
                                         triggered=self.raise_)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.loadCorpusAct)
        self.fileMenu.addAction(self.manageFeatureSystemsAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.createSubsetAct)
        self.fileMenu.addAction(self.saveCorpusAct)
        self.fileMenu.addAction(self.exportCorpusAct)
        self.fileMenu.addAction(self.exportFeatureSystemAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAct)

        self.editMenu = self.menuBar().addMenu("&Options")
        self.editMenu.addAction(self.editPreferencesAct)
        #self.editMenu.addAction(self.toggleWarningsAct)
        self.editMenu.addAction(self.toggleToolTipsAct)

        self.corpusMenu = self.menuBar().addMenu("&Corpus")
        self.corpusMenu.addAction(self.summaryAct)
        self.corpusMenu.addSeparator()
        self.corpusMenu.addAction(self.addWordAct)
        self.corpusMenu.addSeparator()
        self.corpusMenu.addAction(self.addTierAct)
        self.corpusMenu.addAction(self.addAbstractTierAct)
        self.corpusMenu.addAction(self.addCountColumnAct)
        self.corpusMenu.addAction(self.addColumnAct)
        self.corpusMenu.addSeparator()
        self.corpusMenu.addAction(self.removeAttributeAct)
        self.corpusMenu.addSeparator()
        self.corpusMenu.addAction(self.phonoSearchAct)

        self.featureMenu = self.menuBar().addMenu("F&eatures")
        self.featureMenu.addAction(self.viewFeatureSystemAct)
        self.featureMenu.addAction(self.manageInventoryAct)

        self.analysisMenu = self.menuBar().addMenu("&Analysis")
        self.analysisMenu.addAction(self.phonoProbAct)
        self.analysisMenu.addAction(self.funcloadAct)
        self.analysisMenu.addAction(self.prodAct)
        self.analysisMenu.addAction(self.informativityAct)
        self.analysisMenu.addAction(self.klAct)
        self.analysisMenu.addAction(self.stringSimAct)
        self.analysisMenu.addAction(self.neighDenAct)
        self.analysisMenu.addAction(self.freqaltAct)
        self.analysisMenu.addAction(self.mutualInfoAct)
        self.analysisMenu.addAction(self.acousticSimFileAct)
        #self.analysisMenu.addAction(self.autoAnalysisAct)

        self.viewMenu = self.menuBar().addMenu("&Windows")
        self.viewMenu.addAction(self.goToMainWindowAct)
        self.viewMenu.addAction(self.closeResultsWindowsAct)
        self.viewMenu.addAction(self.showDiscoursesAct)
        self.viewMenu.addAction(self.showTextAct)

        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.showPPResults)
        self.viewMenu.addAction(self.showFLResults)
        self.viewMenu.addAction(self.showPDResults)
        self.viewMenu.addAction(self.showKLResults)
        self.viewMenu.addAction(self.showSSResults)
        self.viewMenu.addAction(self.showNDResults)
        self.viewMenu.addAction(self.showFAResults)
        self.viewMenu.addAction(self.showMIResults)
        self.viewMenu.addAction(self.showASResults)
        self.viewMenu.addAction(self.showSearchResults)

        self.helpMenu = self.menuBar().addMenu("&Help")
        if getattr(sys, "frozen", False):
            self.helpMenu.addAction(self.updateAct)
            self.helpMenu.addSeparator()
        self.helpMenu.addAction(self.helpAct)
        self.helpMenu.addAction(self.aboutAct)

    def closeResultsWindows(self):
        for abbrv in self.resultsCodes:
            window = getattr(self, abbrv+'Window')
            if window is not None and window.isVisible():
                window.close()

    def closeEvent(self, event):
        if self.unsavedChanges:
            if self.settings['ask_overwrite_corpus']:
                name_hint = self.generate_corpus_name_hint()
                reply = FileNameDialog(self.corpusModel.corpus.name, 'corpus', self.settings, hint=name_hint)
                reply.exec_()
                if reply.choice == 'saveas':
                    self.corpus.name = reply.getFilename()
                    self.corpusModel.corpus.name = reply.getFilename()
                    self.saveCorpus()
                elif reply.choice == 'overwrite':
                    self.saveCorpus()
                elif reply.choice == 'cancel':
                    return
            else:
                self.saveCorpus()

        self.corpusModel = None
        if self.FLWindow is not None:
            self.FLWindow.reject()
            #self.FLWindow.deleteLater()
        if self.PDWindow is not None:
            self.PDWindow.reject()
            #self.PDWindow.deleteLater()
        if self.FAWindow is not None:
            self.FAWindow.reject()
            #self.FAWindow.deleteLater()
        if self.SSWindow is not None:
            self.SSWindow.reject()
            #self.SSWindow.deleteLater()
        if self.ASWindow is not None:
            self.ASWindow.reject()
            #self.ASWindow.deleteLater()
        if self.NDWindow is not None:
            self.NDWindow.reject()
            #self.NDWindow.deleteLater()
        if self.PPWindow is not None:
            self.PPWindow.reject()
            #self.PPWindow.deleteLater()
        if self.MIWindow is not None:
            self.MIWindow.reject()
            #self.MIWindow.deleteLater()
        if self.KLWindow is not None:
            self.KLWindow.reject()
            #self.KLWindow.deleteLater()
        if self.PhonoSearchWindow is not None:
            self.PhonoSearchWindow.reject()
            #self.PhonoSearchWindow.deleteLater()
        self.settings['size'] = self.size()
        self.settings['pos'] = self.pos()
        #tmpfiles = os.listdir(TMP_DIR)
        #for f in tmpfiles:
        #    os.remove(os.path.join(TMP_DIR,f))
        super(MainWindow, self).closeEvent(event)

    def cleanUp(self):
        # Clean up everything
        for i in self.__dict__:
            item = self.__dict__[i]
            clean(item)

def clean(item):
    """Clean up the memory by closing and deleting the item if possible."""
    if isinstance(item, list) or isinstance(item, dict):
        for _ in range(len(item)):
            clean(item.pop())
    else:
        try:
            item.close()
        except (RuntimeError, AttributeError): # deleted or no close method
            pass
        try:
            item.deleteLater()
        except (RuntimeError, AttributeError): # deleted or no deleteLater method
            pass
# end cleanUp
