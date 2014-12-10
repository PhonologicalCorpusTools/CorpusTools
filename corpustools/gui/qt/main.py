import os

from .imports import *

from corpustools.config import TMP_DIR

from .config import Settings, PreferencesDialog
from .views import TableWidget, TreeWidget, DiscourseView, ResultsWindow, LexiconView
from .models import CorpusModel, ResultsModel, SpontaneousSpeechCorpusModel,DiscourseModel

from .corpusgui import (CorpusLoadDialog, AddTierDialog, RemoveTierDialog,
                        ExportCorpusDialog)

from .featuregui import (FeatureMatrixManager, EditFeatureMatrixDialog,
                        ExportFeatureSystemDialog)

from .ssgui import SSDialog
from .asgui import ASDialog
from .flgui import FLDialog
from .fagui import FADialog
from .pdgui import PDDialog
from .ndgui import NDDialog


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.settings = Settings()

        self.showWarnings = True
        self.showToolTips = True

        self.resize(self.settings['size'])
        self.move(self.settings['pos'])

        self.corpusTable = LexiconView(self)
        self.discourseTree = TreeWidget(self)
        self.discourseTree.newLexicon.connect(lambda x: self.corpusTable.setModel(CorpusModel(x)))
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
        self.statusBar().addWidget(self.status)

        self.setWindowTitle("Phonological CorpusTools")
        self.createActions()
        self.createMenus()
        self.corpusModel = None


        self.FLWindow = None
        self.PDWindow = None
        self.FAWindow = None
        self.SSWindow = None
        self.ASWindow = None
        self.NDWindow = None
        self.setMinimumSize(self.menuBar().sizeHint().width(), 400)

        if not os.path.exists(TMP_DIR):
            os.mkdir(TMP_DIR)

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
            else:
                function(self)
        return do_check

    def changeText(self):
        name = self.discourseTree.model().itemFromIndex(self.discourseTree.selectedIndexes()[0]).text()
        if hasattr(self.corpus, 'lexicon'):
            self.textWidget.setModel(DiscourseModel(self.corpus.discourses[name]))

    def loadCorpus(self):
        dialog = CorpusLoadDialog(self)
        result = dialog.exec_()
        if result:
            self.corpus = dialog.corpus
            if hasattr(self.corpus,'lexicon'):
                self.setMinimumSize(800, 400)
                c = self.corpus.lexicon
                if hasattr(self.corpus,'discourses'):
                    self.discourseTree.show()
                    self.discourseTree.setModel(SpontaneousSpeechCorpusModel(self.corpus))
                    self.discourseTree.selectionModel().selectionChanged.connect(self.changeText)
                else:
                    self.textWidget.setModel(DiscourseModel(self.corpus))
                #self.discourseTree.selectionModel().select(self.discourseTree.model().createIndex(0,0))
                #self.discourseTree.resizeColumnToContents(0)
                self.corpusTable.selectTokens.connect(self.textWidget.highlightTokens)
                self.textWidget.show()
            else:
                c = self.corpus
            self.corpusModel = CorpusModel(c)
            self.corpusTable.setModel(self.corpusModel)

    def loadFeatureMatrices(self):
        dialog = FeatureMatrixManager(self)
        result = dialog.exec_()

    def saveCorpus(self):
        pass

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

    def showPreferences(self):
        pass

    @check_for_empty_corpus
    @check_for_transcription
    def showFeatureSystem(self):
        dialog = EditFeatureMatrixDialog(self,self.corpusModel.corpus)
        if dialog.exec_():
            self.corpusModel.corpus.set_feature_matrix(dialog.specifier)

    @check_for_empty_corpus
    @check_for_transcription
    def createTier(self):
        dialog = AddTierDialog(self, self.corpusModel.corpus)
        if dialog.exec_():
            self.corpusModel.addTier(dialog.tierName, dialog.segList)
            self.corpusTable.table.horizontalHeader().resizeSections()

    @check_for_empty_corpus
    @check_for_transcription
    def destroyTier(self):
        dialog = RemoveTierDialog(self, self.corpusModel.corpus)
        if dialog.exec_():
            self.corpusModel.removeTiers(dialog.tiers)
            self.corpusTable.table.horizontalHeader().resizeSections()

    @check_for_empty_corpus
    def stringSim(self):
        dialog = SSDialog(self, self.corpusModel.corpus,self.showToolTips)
        result = dialog.exec_()
        if result:
            if self.SSWindow is not None and dialog.update and self.SSWindow.isVisible():
                self.SSWindow.table.model().addData(dialog.results)
            else:
                dataModel = ResultsModel(dialog.header,dialog.results)
                self.SSWindow = ResultsWindow('String similarity results',dataModel,self)
                self.SSWindow.show()

    @check_for_empty_corpus
    @check_for_transcription
    def freqOfAlt(self):
        dialog = FADialog(self, self.corpusModel.corpus,self.showToolTips)
        result = dialog.exec_()
        if result:
            if self.FAWindow is not None and dialog.update and self.FAWindow.isVisible():
                self.FAWindow.table.model().addData(dialog.results)
            else:
                dataModel = ResultsModel(dialog.header,dialog.results)
                self.FAWindow = ResultsWindow('Frequency of alternation results',dataModel,self)
                self.FAWindow.show()

    @check_for_empty_corpus
    @check_for_transcription
    def predOfDist(self):
        dialog = PDDialog(self, self.corpusModel.corpus,self.showToolTips)
        result = dialog.exec_()
        if result:
            if self.PDWindow is not None and self.PDWindow.isVisible():
                self.PDWindow.table.model().addData(dialog.results)
            else:
                dataModel = ResultsModel(dialog.header,dialog.results)
                self.PDWindow = ResultsWindow('Predictability of distribution results',dataModel,self)
                self.PDWindow.show()

    @check_for_empty_corpus
    @check_for_transcription
    def funcLoad(self):
        dialog = FLDialog(self, self.corpusModel.corpus,self.showToolTips)
        result = dialog.exec_()
        if result:
            if self.FLWindow is not None and dialog.update and self.FLWindow.isVisible():
                self.FLWindow.table.model().addData(dialog.results)
            else:
                dataModel = ResultsModel(dialog.header,dialog.results)
                self.FLWindow = ResultsWindow('Functional load results',dataModel,self)
                self.FLWindow.show()

    def acousticSim(self):
        dialog = ASDialog(self,self.showToolTips)
        result = dialog.exec_()
        if result:
            if self.ASWindow is not None and dialog.update and self.ASWindow.isVisible():
                self.ASWindow.table.model().addData(dialog.results)
            else:
                dataModel = ResultsModel(dialog.header,dialog.results)
                self.ASWindow = ResultsWindow('Acoustic similarity results',dataModel,self)
                self.ASWindow.show()

    @check_for_empty_corpus
    def neighDen(self):
        dialog = NDDialog(self, self.corpusModel.corpus,self.showToolTips)
        result = dialog.exec_()
        if result:
            if self.NDWindow is not None and dialog.update and self.NDWindow.isVisible():
                self.NDWindow.table.model().addData(dialog.results)
            else:
                dataModel = ResultsModel(dialog.header,dialog.results)
                self.NDWindow = ResultsWindow('Neighborhood density results',dataModel,self)
                self.NDWindow.show()


    def toggleWarnings(self):
        self.showWarnings = not self.showWarnings

    def toggleToolTips(self):
        self.showToolTips = not self.showToolTips

    def toggleInventory(self):
        pass

    def toggleText(self):
        pass

    def about(self):
        pass

    def createActions(self):

        self.loadCorpusAct = QAction( "L&oad corpus...",
                self, shortcut=QKeySequence.Open,
                statusTip="Load a corpus", triggered=self.loadCorpus)

        self.manageFeatureSystemsAct = QAction( "Manage feature systems...",
                self,
                statusTip="Manage feature systems", triggered=self.loadFeatureMatrices)

        self.saveCorpusAct = QAction( "Save corpus",
                self,
                statusTip="Save corpus", triggered=self.saveCorpus)

        self.exportCorpusAct = QAction( "Export corpus as text file (use with spreadsheets etc.)...",
                self,
                statusTip="Export corpus", triggered=self.exportCorpus)

        self.exportFeatureSystemAct = QAction( "Export feature system as text file...",
                self,
                statusTip="Export feature system", triggered=self.exportFeatureMatrix)

        self.editPreferencesAct = QAction( "Preferences...",
                self,
                statusTip="Edit preferences", triggered=self.showPreferences)

        self.viewFeatureSystemAct = QAction( "View/change feature system...",
                self,
                statusTip="View feature system", triggered=self.showFeatureSystem)

        self.addTierAct = QAction( "Add tier...",
                self,
                statusTip="Add tier", triggered=self.createTier)

        self.removeTierAct = QAction( "Remove tier...",
                self,
                statusTip="Remove tier", triggered=self.destroyTier)

        self.neighDenAct = QAction( "Calculate neighborhood density...",
                self,
                statusTip="Calculate neighborhood density", triggered=self.neighDen)

        self.stringSimFileAct = QAction( "Calculate string similarity...",
                self,
                statusTip="Calculate string similarity for a file of string pairs")#, triggered=self.stringSim)

        self.stringSimAct = QAction( "Calculate string similarity...",
                self,
                statusTip="Calculate string similarity for corpus", triggered=self.stringSim)

        self.freqaltAct = QAction( "Calculate frequency of alternation...",
                self,
                statusTip="Calculate frequency of alternation", triggered=self.freqOfAlt)

        self.prodAct = QAction( "Calculate predictability of distribution...",
                self,
                statusTip="Calculate predictability of distribution", triggered=self.predOfDist)

        self.funcloadAct = QAction( "Calculate functional load...",
                self,
                statusTip="Calculate functional load", triggered=self.funcLoad)

        self.acousticSimFileAct = QAction( "Calculate acoustic similarity (for files)...",
                self,
                statusTip="Calculate acoustic similarity for files", triggered=self.acousticSim)

        self.acousticSimAct = QAction( "Calculate acoustic similarity (from corpus)...",
                self,
                statusTip="Calculate acoustic similarity for corpus")#, triggered=self.acousticSim)

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

        self.quitAct = QAction("&Quit", self, shortcut="Ctrl+Q",
                statusTip="Quit the application", triggered=self.close)

        self.aboutAct = QAction("&About", self,
                statusTip="Show the application's About box",
                triggered=self.about)

        self.helpAct = QAction("&Help", self,
                statusTip="Help information",
                triggered=self.about)

        self.batchNeighDenAct = QAction("Add neighborhood density...", self,
                statusTip="Calculate all words' neighborhood density and add as a column",
                triggered=self.about)

        self.batchPhonProbAct = QAction("Add phonotactic probability...", self,
                statusTip="Calculate all words' phonotactic probability and add as a column",
                triggered=self.about)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.loadCorpusAct)
        self.fileMenu.addAction(self.manageFeatureSystemsAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.saveCorpusAct)
        self.fileMenu.addAction(self.exportCorpusAct)
        self.fileMenu.addAction(self.exportFeatureSystemAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAct)

        self.editMenu = self.menuBar().addMenu("&Options")
        self.editMenu.addAction(self.editPreferencesAct)
        self.editMenu.addAction(self.toggleWarningsAct)
        self.editMenu.addAction(self.toggleToolTipsAct)

        self.enhanceMenu = self.menuBar().addMenu("&Corpus")
        self.enhanceMenu.addAction(self.addTierAct)
        self.enhanceMenu.addAction(self.removeTierAct)
        self.enhanceMenu.addAction(self.batchNeighDenAct)
        self.enhanceMenu.addAction(self.batchPhonProbAct)

        self.featureMenu = self.menuBar().addMenu("&Features")
        self.featureMenu.addAction(self.viewFeatureSystemAct)

        self.analysisMenu = self.menuBar().addMenu("&Analysis")
        self.analysisMenu.addAction(self.stringSimAct)
        #self.analysisMenu.addAction(self.stringSimFileAct)
        self.analysisMenu.addAction(self.freqaltAct)
        self.analysisMenu.addAction(self.prodAct)
        self.analysisMenu.addAction(self.funcloadAct)
        self.analysisMenu.addAction(self.neighDenAct)
        self.analysisMenu.addAction(self.acousticSimAct)
        self.analysisMenu.addAction(self.acousticSimFileAct)

        #self.otherMenu = self.menuBar().addMenu("Other a&nalysis")

        #self.viewMenu = self.menuBar().addMenu("&Windows")
        #self.viewMenu.addAction(self.showInventoryAct)
        #self.viewMenu.addAction(self.showTextAct)
        #self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.helpAct)
        self.helpMenu.addAction(self.aboutAct)

    def closeEvent(self, event):
        tmpfiles = os.listdir(TMP_DIR)
        for f in tmpfiles:
            os.remove(os.path.join(TMP_DIR,f))
        super(MainWindow, self).closeEvent(event)
