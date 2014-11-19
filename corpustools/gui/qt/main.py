from PyQt5.QtGui import QFont, QKeySequence
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QHBoxLayout, QLabel, QAction,
                            QApplication, QWidget, QMessageBox,QSplitter)

from .config import Settings, PreferencesDialog
from .views import TableWidget, TreeWidget, TextView, ResultsWindow, LexiconView
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


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setMinimumSize(400, 400)

        self.settings = Settings()

        self.showWarnings = True
        self.showToolTips = True

        self.resize(self.settings['size'])
        self.move(self.settings['pos'])

        self.corpusTable = LexiconView(self)
        self.discourseTree = TreeWidget(self)
        self.discourseTree.newLexicon.connect(lambda x: self.corpusTable.setModel(CorpusModel(x)))
        self.discourseTree.hide()
        self.textWidget = TextView(self)
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
                        "Missing transcription", "This corpus has no transcriptions, so the requested cannot be performed.")
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
                self.discourseTree.show()
                self.discourseTree.setModel(SpontaneousSpeechCorpusModel(self.corpus))
                self.discourseTree.selectionModel().selectionChanged.connect(self.changeText)
                #self.discourseTree.selectionModel().select(self.discourseTree.model().createIndex(0,0))
                #self.discourseTree.resizeColumnToContents(0)
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

    def showFeatureSystem(self):
        dialog = EditFeatureMatrixDialog(self,self.corpusModel.corpus)
        if dialog.exec_():
            self.corpusModel.corpus.set_feature_matrix(dialog.specifier)

    def createTier(self):
        dialog = AddTierDialog(self, self.corpusModel.corpus)
        if dialog.exec_():
            self.corpusModel.addTier(dialog.tierName, dialog.featureList)
            self.corpusTable.horizontalHeader().resizeSections()

    def destroyTier(self):
        dialog = RemoveTierDialog(self, self.corpusModel.corpus)
        if dialog.exec_():
            self.corpusModel.removeTiers(dialog.tiers)
            self.corpusTable.horizontalHeader().resizeSections()

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

        self.stringsimAct = QAction( "Calculate string similarity...",
                self,
                statusTip="Calculate string similarity", triggered=self.stringSim)

        self.freqaltAct = QAction( "Calculate frequency of alternation...",
                self,
                statusTip="Calculate frequency of alternation", triggered=self.freqOfAlt)

        self.prodAct = QAction( "Calculate predictability of distribution...",
                self,
                statusTip="Calculate predictability of distribution", triggered=self.predOfDist)

        self.funcloadAct = QAction( "Calculate functional load...",
                self,
                statusTip="Calculate functional load", triggered=self.funcLoad)

        self.acousticsimAct = QAction( "Calculate acoustic similarity...",
                self,
                statusTip="Calculate acoustic similarity", triggered=self.acousticSim)

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

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&Corpus")
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
        self.editMenu.addAction(self.viewFeatureSystemAct)
        self.editMenu.addAction(self.addTierAct)
        self.editMenu.addAction(self.removeTierAct)
        self.editMenu.addAction(self.toggleWarningsAct)
        self.editMenu.addAction(self.toggleToolTipsAct)

        self.analysisMenu = self.menuBar().addMenu("&Analysis")
        self.analysisMenu.addAction(self.stringsimAct)
        self.analysisMenu.addAction(self.freqaltAct)
        self.analysisMenu.addAction(self.prodAct)
        self.analysisMenu.addAction(self.funcloadAct)
        self.analysisMenu.addAction(self.acousticsimAct)

        self.viewMenu = self.menuBar().addMenu("&Windows")
        self.viewMenu.addAction(self.showInventoryAct)
        self.viewMenu.addAction(self.showTextAct)
        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.helpAct)
        self.helpMenu.addAction(self.aboutAct)
