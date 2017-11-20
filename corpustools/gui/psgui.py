from .imports import *
import time
import collections

from .widgets import TierWidget

from .windows import FunctionWorker, FunctionDialog

from .environments import EnvironmentSelectWidget

from corpustools.phonosearch import phonological_search

from corpustools.exceptions import PCTError, PCTPythonError

class PSWorker(FunctionWorker):
    def run(self):
        time.sleep(0.1)
        kwargs = self.kwargs
        if 'envs' not in kwargs or not kwargs['envs']:
            return #user clicked "search" without actually entering a single environment
        try:
            self.results = phonological_search(**kwargs)
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
        self.dataReady.emit(self.results)

class RecentSearch:

    def __init__(self, widget):
        self.widgetData = list()
        self.noteData = str()
        envWidget = widget.environmentFrame.layout().itemAt(0).widget()
        #type(envWidget) == corpustools.gui.environments.EnvironmentWidget
        middle = envWidget.middleWidget
        self.middleData = middle.getData()
        #type(middle) == corpustools.gui.environments.EnvironmentSegmentWidget
        lhs = envWidget.lhsLayout
        rhs = envWidget.rhsLayout

        self.displayValue = envWidget.displayValue()

        self.middleValue = middle.value()
        self.middleDisplayValue = middle.displayValue()

        lhsWidgets = [lhs.itemAt(i).widget() for i in range(lhs.count())]
        self.lhsValue, self.lhsDisplayValue, self.lhsData = list(), list(), list()
        for w in lhsWidgets:
            self.lhsValue.append(w.value())
            self.lhsDisplayValue.append(w.displayValue())
            self.lhsData.append(w.getData())

        rhsWidgets = [rhs.itemAt(i).widget() for i in range(rhs.count())]
        self.rhsValue, self.rhsDisplayValue, self.rhsData = list(), list(), list()
        for w in rhsWidgets:
            self.rhsValue.append(w.value())
            self.rhsDisplayValue.append(w.displayValue())
            self.rhsData.append(w.getData())


    def __str__(self):
        return self.displayValue

    def target(self):
        return self.middleDisplayValue

    def environment(self):
        return self.displayValue

    def note(self):
        return self.noteData

    def updateNote(self, noteData):
        self.noteData = noteData


class RecentSearchDialog(QDialog):

    def __init__(self, recents, saved):
        super().__init__()
        self.setWindowTitle('Searches')
        self.mainLayout = QVBoxLayout()
        self.tableLayout = QHBoxLayout()
        self.saved = saved
        self.recents = recents

        self.setupRecentsTable()
        self.setupSavedTable()

        buttonLayout = QHBoxLayout()
        ok = QPushButton('Load selected search')
        ok.clicked.connect(self.accept)
        buttonLayout.addWidget(ok)
        cancel = QPushButton('Go back')
        cancel.clicked.connect(self.reject)
        buttonLayout.addWidget(cancel)

        self.mainLayout.addLayout(self.tableLayout)
        self.mainLayout.addLayout(buttonLayout)
        self.setLayout(self.mainLayout)
        self.makeMenus()

    def setupRecentsTable(self):
        recentFrame = QGroupBox('Recent Searches')
        recentLayout = QVBoxLayout()
        recentFrame.setLayout(recentLayout)
        self.recentSearchesTable = QTableWidget()
        self.recentSearchesTable.setSortingEnabled(False)
        self.recentSearchesTable.setColumnCount(2)
        self.recentSearchesTable.setHorizontalHeaderLabels(['Target', 'Environment'])
        self.recentSearchesTable.setRowCount(5)
        self.recentSearchesTable.setSelectionBehavior(QTableWidget.SelectRows)
        recentLayout.addWidget(self.recentSearchesTable)
        self.tableLayout.addWidget(recentFrame)
        print('setting up RecentTable')
        for i, search in enumerate(self.recents):
            targetItem = QTableWidgetItem(search.target())
            targetItem.setFlags(targetItem.flags() ^ Qt.ItemIsEditable)
            self.recentSearchesTable.setItem(i, 0, targetItem)

            envItem = QTableWidgetItem(search.environment())
            envItem.setFlags(envItem.flags() ^ Qt.ItemIsEditable)
            self.recentSearchesTable.setItem(i, 1, envItem)
            print(targetItem.row(), targetItem.column(), targetItem.text())
            print(envItem.row(), envItem.column(), envItem.text())

        self.recentSearchesTable.cellClicked.connect(self.deselectSavedTable)


    def setupSavedTable(self):
        savedFrame = QGroupBox('Saved Searches')
        savedLayout = QVBoxLayout()
        savedFrame.setLayout(savedLayout)
        self.savedSearchesTable = QTableWidget()
        self.savedSearchesTable.setSortingEnabled(False)
        self.savedSearchesTable.setColumnCount(3)
        self.savedSearchesTable.setHorizontalHeaderLabels(['Target', 'Environment', 'Notes'])
        self.savedSearchesTable.setRowCount(len(self.saved))
        self.savedSearchesTable.setSelectionBehavior(QTableWidget.SelectRows)
        savedLayout.addWidget(self.savedSearchesTable)
        print('setting up SavedTable')
        self.tableLayout.addWidget(savedFrame)
        for i, search in enumerate(self.saved):
            targetItem = QTableWidgetItem(search.target())
            targetItem.setFlags(targetItem.flags() ^ Qt.ItemIsEditable)
            self.savedSearchesTable.setItem(i, 0, targetItem)

            envItem = QTableWidgetItem(search.environment())
            envItem.setFlags(envItem.flags() ^ Qt.ItemIsEditable)
            self.savedSearchesTable.setItem(i, 1, envItem)

            noteItem = QTableWidgetItem(search.note())
            noteItem.setFlags(noteItem.flags() | Qt.ItemIsEditable)
            self.savedSearchesTable.setItem(i, 2, noteItem)
            print(targetItem.row(), targetItem.column(), targetItem.text())
            print(envItem.row(), envItem.column(), envItem.text())
            print(noteItem.row(), noteItem.column(), noteItem.text())
        self.savedSearchesTable.cellClicked.connect(self.deselectRecentTable)

    def makeMenus(self):
        self.recentMenu = QMenu()
        self.deleteRecentAction = QAction('Delete search')
        self.moveToSavedAction = QAction('Move to "saved" searches')
        self.recentMenu.addAction(self.deleteRecentAction)
        self.recentMenu.addAction(self.moveToSavedAction)
        self.recentSearchesTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.recentSearchesTable.customContextMenuRequested.connect(self.showRecentMenu)

        self.savedMenu = QMenu()
        self.deleteSaveAction = QAction('Delete search')
        self.savedMenu.addAction(self.deleteSaveAction)
        self.savedSearchesTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.savedSearchesTable.customContextMenuRequested.connect(self.showSavedMenu)

    def showSavedMenu(self, pos):
        index = self.savedSearchesTable.indexAt(pos)
        action = self.savedMenu.exec_(self.savedSearchesTable.mapToGlobal(pos))
        item = self.savedSearchesTable.itemAt(index.row(), index.column())
        if not item:
            return
        if action == self.deleteSaveAction:
            self.deleteSavedSearch(index)

    def showRecentMenu(self, pos):
        index = self.recentSearchesTable.indexAt(pos)
        action = self.recentMenu.exec_(self.recentSearchesTable.mapToGlobal(pos))
        item = self.recentSearchesTable.itemAt(index.row(), index.column())
        if not item:
            return
        if action == self.deleteRecentAction:
            self.deleteRecentSearch(index)
        elif action == self.moveToSavedAction:
            self.addToSavedTable(index)

    def addToSavedTable(self, index):
        search = self.recents[index.row()]
        self.saved.append(search)
        self.deleteRecentSearch(index)

        self.savedSearchesTable.setRowCount(len(self.saved))

        for row in range(len(self.saved)):
            search = self.saved[row]

            targetItem = QTableWidgetItem(search.target())
            targetItem.setFlags(targetItem.flags() ^ Qt.ItemIsEditable)
            self.savedSearchesTable.setItem(row, 0, targetItem)

            envItem = QTableWidgetItem(search.environment())
            envItem.setFlags(envItem.flags() ^ Qt.ItemIsEditable)
            self.savedSearchesTable.setItem(row, 1, envItem)

            noteItem = QTableWidgetItem(search.note())
            noteItem.setFlags(noteItem.flags() ^ Qt.ItemIsEditable)
            self.savedSearchesTable.setItem(row, 2, noteItem)

    def deleteSavedSearch(self, index):
        self.savedSearchesTable.removeRow(index.row())
        self.saved.pop(index.row())

    def deleteRecentSearch(self, index):
        self.recentSearchesTable.removeRow(index.row())
        self.recentSearchesTable.insertRow(self.recentSearchesTable.rowCount())
        self.recents = collections.deque([x for (i,x) in enumerate(self.recents) if not i == index.row()], maxlen=5)

    def deselectRecentTable(self):
        self.recentSearchesTable.clearSelection()
        self.recentSearchesTable.setCurrentCell(-1, -1)

    def deselectSavedTable(self):
        self.savedSearchesTable.clearSelection()
        self.savedSearchesTable.setCurrentCell(-1, -1)

    def updateNote(self):
        for row in range(self.savedSearchesTable.rowCount()):
            tableItem = self.savedSearchesTable.item(row, 2)
            if tableItem is None:
                note = str()
            else:
                note = tableItem.text()
            self.saved[row].updateNote(note)

    def accept(self):
        self.updateNote()

        if self.recentSearchesTable.currentItem() is not None:
            self.selectedSearch = self.recentSearchesTable.currentItem()
            row = self.recentSearchesTable.currentRow()
            item = self.recents[row]
            if not item:
                self.selectedSearch = None
            else:
                self.selectedSearch = item
        elif self.savedSearchesTable.currentItem() is not None:
            self.selectedSearch = self.savedSearchesTable.currentItem()
            row = self.savedSearchesTable.currentRow()
            item = self.saved[row]
            self.selectedSearch = item
        else:
            self.selectedSearch = None

        super().accept()

    def reject(self):
        self.selectedSearch = None
        self.updateNote()
        super().reject()


class PhonoSearchDialog(FunctionDialog):
    header = ['Word',
                'Transcription',
                'Segment',
                'Environment',
                'Token frequency']
    summary_header = ['Segment', 'Environment', 'Type frequency', 'Token frequency']
    _about = ['']

    name = 'phonological search'
    def __init__(self, parent, settings, recents, saved, corpus, inventory, showToolTips):
        FunctionDialog.__init__(self, parent, settings, PSWorker())

        self.corpus = corpus
        self.inventory = inventory
        self.showToolTips = showToolTips
        self.recentSearches = recents
        self.savedSearches = saved

        psFrame = QFrame()
        pslayout = QHBoxLayout()
        self.envWidget = EnvironmentSelectWidget(self.inventory,
                                                 show_full_inventory=bool(settings['show_full_inventory']))
        pslayout.addWidget(self.envWidget)

        optionFrame = QGroupBox('Options')
        optionLayout = QVBoxLayout()
        optionFrame.setLayout(optionLayout)

        self.tierWidget = TierWidget(corpus,include_spelling=False)
        optionLayout.addWidget(self.tierWidget)

        searchFrame = QGroupBox('Searches')
        searchLayout = QVBoxLayout()
        searchFrame.setLayout(searchLayout)
        loadSearch = QPushButton('Load recent search')
        loadSearch.clicked.connect(self.loadSearch)
        saveSearch = QPushButton('Save current search')
        saveSearch.clicked.connect(self.saveSearch)
        searchLayout.addWidget(loadSearch)
        searchLayout.addWidget(saveSearch)
        optionLayout.addWidget(searchFrame)

        pslayout.addWidget(optionFrame)

        psFrame.setLayout(pslayout)
        self.layout().insertWidget(0,psFrame)
        self.setWindowTitle('Phonological search')
        self.progressDialog.setWindowTitle('Searching')

    def accept(self):
        search = RecentSearch(self.envWidget)
        self.recentSearches.appendleft(search) #recentSearches is a collections.deque object, not a regular list
        super().accept()

    def loadSearch(self):
        dialog = RecentSearchDialog(self.recentSearches, self.savedSearches)
        dialog.exec_()
        self.recentSearches = dialog.recents
        self.savedSearches = dialog.saved
        if dialog.selectedSearch is None:
            return

        #first remove all of the existing environments
        #it's important to loop over the count()-2 because looping over the full count deletes important
        #widgets like the "add new environment" button
        for n in reversed(range(self.envWidget.environmentFrame.layout().count()-2)):
            widget = self.envWidget.environmentFrame.layout().itemAt(n).widget()
            try:
                widget.deleteLater()
            except AttributeError: #widget is None
                pass

        #add a new blank environment
        self.envWidget.addNewEnvironment()

        #Get the widgets in the new environment and update them accordingly
        widget = self.envWidget.environmentFrame.layout().itemAt(0).widget() #== environments.EnvironmentWidget
        search = dialog.selectedSearch#== RecentSearch which is located in this module

        #update the middle widget
        widget.middleWidget.loadData(search.middleData)
        widget.middleWidget.updateLabel()

        #update the left hand side
        for value in search.lhsValue:
            lhsWidget = widget.addLhs()

        for n in range(len(search.lhsValue)):
            button = widget.lhsLayout.itemAt(n).widget()
            button.loadData(search.lhsData[n])
            button.updateLabel()

        #update the right hand side
        for value in search.rhsValue:
            rhsWidget = widget.addRhs()

        for n in range(len(search.rhsValue)):
            button = widget.rhsLayout.itemAt(n).widget()
            button.loadData(search.rhsData[n])
            button.updateLabel()

    def saveSearch(self):
        search = RecentSearch(self.envWidget)
        self.savedSearches.append(search)
        alert = QMessageBox()
        alert.setWindowTitle('Success')
        alert.setText('Search saved!')
        alert.exec_()

    def generateKwargs(self):
        kwargs = {}
        envs = self.envWidget.value()
        if not envs:
            return
        if len(envs) > 0:
            for i, e in enumerate(envs):
                if len(e.middle) == 0:
                    reply = QMessageBox.critical(self, "Missing information",
                            "Please specify at least segment to search for in environment {}.".format(i+1))
                    return
            kwargs['envs'] = envs

        kwargs['corpus'] = self.corpus
        kwargs['sequence_type'] = self.tierWidget.value()
        return kwargs

    def setResults(self,results):
        self.results = []
        for w,f in results:
            segs = tuple(x.middle for x in f)
            try:
                envs = tuple(str(x) for x in f)
            except IndexError:
                envs = tuple()
            self.results.append({'Word': w, 
                                'Transcription': str(getattr(w,self.tierWidget.value())),
                                'Segment': segs,
                                'Environment': envs,
                                'Token frequency':w.frequency})
