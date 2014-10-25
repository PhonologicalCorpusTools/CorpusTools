from PyQt5.QtGui import QFont, QKeySequence
from PyQt5.QtWidgets import (QMainWindow, QHBoxLayout, QLabel, QAction,
                            QApplication, QWidget)

from .config import Settings, PreferencesDialog
from .views import TableWidget
from .models import CorpusModel

from .corpusgui import CorpusLoadDialog

from .ssgui import SSDialog
from .asgui import ASDialog
from .flgui import FLDialog
from .fagui import FADialog
from .pdgui import PDDialog


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setMinimumSize(1000, 800)

        self.settings = Settings()

        self.resize(self.settings['size'])
        self.move(self.settings['pos'])

        self.corpusTable = TableWidget(self)
        font = QFont("Courier New", 14)
        self.corpusTable.setFont(font)
        self.wrapper = QWidget()
        layout = QHBoxLayout(self.wrapper)
        layout.addWidget(self.corpusTable)
        self.wrapper.setLayout(layout)
        self.setCentralWidget(self.wrapper)

        self.status = QLabel()
        self.status.setText("Ready")
        self.statusBar().addWidget(self.status)

        self.setWindowTitle("Phonological CorpusTools")
        self.createActions()
        self.createMenus()
        self.corpusModel = None

    def loadCorpus(self):
        dialog = CorpusLoadDialog(self)
        result = dialog.exec_()
        if result:
            self.corpusModel = CorpusModel(dialog.corpus)
            self.corpusTable.setModel(self.corpusModel)


    def loadFeatureMatrices(self):
        pass

    def saveCorpus(self):
        pass

    def exportCorpus(self):
        pass

    def exportFeatureMatrix(self):
        pass

    def showPreferences(self):
        pass

    def showFeatureSystem(self):
        pass

    def createTier(self):
        pass

    def destroyTier(self):
        pass

    def stringSim(self):
        dialog = SSDialog(self)
        result = dialog.exec_()
        if result:
            pass

    def freqOfAlt(self):
        dialog = FADialog(self)
        result = dialog.exec_()
        if result:
            pass

    def predOfDist(self):
        dialog = PDDialog(self)
        result = dialog.exec_()
        if result:
            pass

    def funcLoad(self):
        dialog = FLDialog(self)
        result = dialog.exec_()
        if result:
            pass

    def acousticSim(self):
        dialog = ASDialog(self)
        result = dialog.exec_()
        if result:
            pass

    def toggleWarnings(self):
        pass

    def toggleTooltips(self):
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

        self.toggleTooltipsAct = QAction( "Show tooltips",
                self,
                statusTip="Show tooltips", triggered=self.toggleTooltips)

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
        self.editMenu.addAction(self.toggleTooltipsAct)

        self.analysisMenu = self.menuBar().addMenu("&Analysis")
        self.analysisMenu.addAction(self.stringsimAct)
        self.analysisMenu.addAction(self.freqaltAct)
        self.analysisMenu.addAction(self.prodAct)
        self.analysisMenu.addAction(self.funcloadAct)
        self.analysisMenu.addAction(self.acousticsimAct)

        self.viewMenu = self.menuBar().addMenu("&Windows")

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.helpAct)
        self.helpMenu.addAction(self.aboutAct)
