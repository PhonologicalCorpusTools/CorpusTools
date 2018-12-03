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

    def __init__(self, envWidget):
        self.widgetData = list()
        self.noteData = str()
        #envWidget = widget.environmentFrame.layout().itemAt(0).widget()
        #type(envWidget) == corpustools.gui.environments.EnvironmentWidget
        middle = envWidget.middleWidget
        self.middleData = middle.getData()
        #type(middle) == corpustools.gui.environments.EnvironmentSegmentWidget
        lhs = envWidget.lhsLayout
        rhs = envWidget.rhsLayout

        self.displayValue = envWidget.displayValue()  # EnvironmentWidget and EnvironmentSyllableWidget

        self.middleValue = middle.value()  # a list of segments
        self.middleDisplayValue = middle.displayValue()  # {a, +syllabic}

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
        return self.displayValue.replace('_', '_' + self.middleDisplayValue + '_')

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
        self.currentSearches = list()

        self.setupRecentsTable()
        self.setupSavedTable()
        self.setupCurrentSearchTable()

        explainLayout = QHBoxLayout()
        explanation = ('* Right-clicking a cell will reveal additional options.\n'
                       '* To search a single environment, simply left-click to select it.\n'
                       '* To search multiple environments, right-click each one and choose "Add to current search".\n'
                       '* Click "Load selected search" when you are finished.\n'
                       )
        explainLabel = QLabel()
        explainLabel.setText(explanation)
        explainLabel.setWordWrap(True)
        explainLabel.setFont(QFont("Arial", 12))
        explainLayout.addWidget(explainLabel)

        buttonLayout = QHBoxLayout()
        self.okButton = QPushButton('Load selected search')
        self.okButton.clicked.connect(self.accept)
        buttonLayout.addWidget(self.okButton)
        cancel = QPushButton('Go back')
        cancel.clicked.connect(self.reject)
        buttonLayout.addWidget(cancel)

        self.mainLayout.addLayout(self.tableLayout)
        self.mainLayout.addLayout(explainLayout)
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
        for i, search in enumerate(self.recents):
            targetItem = QTableWidgetItem(search.target())
            targetItem.setFlags(targetItem.flags() ^ Qt.ItemIsEditable)
            self.recentSearchesTable.setItem(i, 0, targetItem)

            envItem = QTableWidgetItem(search.environment())
            envItem.setFlags(envItem.flags() ^ Qt.ItemIsEditable)
            self.recentSearchesTable.setItem(i, 1, envItem)

        self.recentSearchesTable.cellClicked.connect(self.deselectSavedTable)
        self.recentSearchesTable.cellClicked.connect(self.deselectCurrentTable)


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

        self.savedSearchesTable.cellClicked.connect(self.deselectRecentTable)
        self.savedSearchesTable.cellClicked.connect(self.deselectCurrentTable)

    def setupCurrentSearchTable(self):
        currentFrame = QGroupBox('Current Search')
        currentLayout = QVBoxLayout()
        currentFrame.setLayout(currentLayout)
        self.currentSearchesTable = QTableWidget()
        self.currentSearchesTable.setSortingEnabled(False)
        self.currentSearchesTable.setColumnCount(2)
        self.currentSearchesTable.setHorizontalHeaderLabels(['Target', 'Environment'])
        self.currentSearchesTable.setRowCount(0)
        self.currentSearchesTable.setSelectionBehavior(QTableWidget.SelectRows)
        currentLayout.addWidget(self.currentSearchesTable)
        self.tableLayout.addWidget(currentFrame)

        self.currentSearchesTable.cellClicked.connect(self.deselectRecentTable)
        self.currentSearchesTable.cellClicked.connect(self.deselectSavedTable)

    def makeMenus(self):
        self.recentMenu = QMenu()
        self.deleteRecentAction = QAction('Delete search', self)
        self.moveToSavedAction = QAction('Move to "saved" searches', self)
        self.addToCurrentAction = QAction('Add to current search', self)
        self.recentMenu.addAction(self.deleteRecentAction)
        self.recentMenu.addAction(self.moveToSavedAction)
        self.recentMenu.addAction(self.addToCurrentAction)
        self.recentSearchesTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.recentSearchesTable.customContextMenuRequested.connect(self.showRecentMenu)

        self.savedMenu = QMenu()
        self.deleteSaveAction = QAction('Delete search', self)
        self.savedMenu.addAction(self.deleteSaveAction)
        self.savedMenu.addAction(self.addToCurrentAction)
        self.savedSearchesTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.savedSearchesTable.customContextMenuRequested.connect(self.showSavedMenu)

        self.currentMenu = QMenu()
        self.deleteCurrentAction = QAction('Remove from current search', self)
        self.currentMenu.addAction(self.deleteCurrentAction)
        self.currentSearchesTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.currentSearchesTable.customContextMenuRequested.connect(self.showCurrentMenu)

    def showCurrentMenu(self, pos):
        index = self.currentSearchesTable.indexAt(pos)
        action = self.currentMenu.exec_(self.currentSearchesTable.mapToGlobal(pos))
        item = self.currentSearchesTable.itemAt(index.row(), index.column())
        if not item:
            return
        if action == self.deleteCurrentAction:
            self.deleteCurrentSearch(index)

    def showSavedMenu(self, pos):
        index = self.savedSearchesTable.indexAt(pos)
        action = self.savedMenu.exec_(self.savedSearchesTable.mapToGlobal(pos))
        item = self.savedSearchesTable.itemAt(index.row(), index.column())
        if not item:
            return
        if action == self.deleteSaveAction:
            self.deleteSavedSearch(index)
        elif action == self.addToCurrentAction:
            self.addToCurrent(index, self.saved)

    def showRecentMenu(self, pos):
        index = self.recentSearchesTable.indexAt(pos)
        action = self.recentMenu.exec_(self.recentSearchesTable.mapToGlobal(pos))
        item = self.recentSearchesTable.itemAt(index.row(), index.column())
        if not item:
            return
        if action == self.deleteRecentAction:
            self.deleteRecentSearch(index)
        elif action == self.moveToSavedAction:
            self.moveToSavedTable(index)
        elif action == self.addToCurrentAction:
            self.addToCurrent(index, self.recents)

    def addToCurrent(self, index, searchlist):
        search = searchlist[index.row()]
        self.currentSearches.append(search)

        self.currentSearchesTable.setRowCount(len(self.currentSearches))

        for row, search in enumerate(self.currentSearches):
            targetItem = QTableWidgetItem(search.target())
            targetItem.setFlags(targetItem.flags() ^ Qt.ItemIsEditable)
            self.currentSearchesTable.setItem(row, 0, targetItem)

            envItem = QTableWidgetItem(search.environment())
            envItem.setFlags(envItem.flags() ^ Qt.ItemIsEditable)
            self.currentSearchesTable.setItem(row, 1, envItem)

    def moveToSavedTable(self, index):
        search = self.recents[index.row()]
        self.saved.append(search)
        self.deleteRecentSearch(index)

        # for some reason, adding a new row isn't working. a blank row is added on screen, no cell contents.
        # after closing and re-opening, the row is correctly filled (meaning self.saved is properly updated)
        # to solve this problem, update the entire table from scratch, which seems to work
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

    def deleteCurrentSearch(self, index):
        self.currentSearchesTable.removeRow(index.row())
        self.currentSearches.pop(index.row())

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

    def deselectCurrentTable(self):
        self.currentSearchesTable.clearSelection()
        self.currentSearchesTable.setCurrentCell(-1, -1)

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
    header = ['Word', 'Transcription', 'Segment', 'Environment', 'Token frequency']
    summary_header = ['Segment', 'Environment', 'Type frequency', 'Token frequency']
    _about = ['']
    name = 'phonological search'

    def __init__(self, parent, settings, recents, saved, corpus, inventory, showToolTips):
        FunctionDialog.__init__(self, parent, settings, PSWorker())
        self.setWindowTitle('Phonological search')

        self.corpus = corpus
        self.inventory = inventory
        self.showToolTips = showToolTips
        self.recentSearches = recents
        self.savedSearches = saved
        self.settings = settings

        self.psFrame = QFrame()
        self.pslayout = QHBoxLayout()

        optionFrame = QGroupBox('Options')
        optionLayout = QVBoxLayout()
        optionFrame.setLayout(optionLayout)

        modeFrame = QGroupBox('Search mode')
        modeLayout = QVBoxLayout()
        modeFrame.setLayout(modeLayout)

        self.modeGroup = QButtonGroup()
        segMode = QCheckBox('Segments')
        segMode.clicked.connect(self.changeMode)
        segMode.setChecked(True)
        self.mode = 'segMode'
        self.modeGroup.addButton(segMode)
        sylMode = QCheckBox('Syllables')
        sylMode.clicked.connect(self.changeMode)
        self.modeGroup.addButton(sylMode)
        self.modeGroup.setExclusive(True)
        self.modeGroup.setId(segMode, 0)
        self.modeGroup.setId(sylMode, 1)

        modeLayout.addWidget(segMode)
        modeLayout.addWidget(sylMode)
        optionLayout.addWidget(modeFrame)

        resultTypeFrame = QGroupBox('Result type')
        resultTypeLayout = QVBoxLayout()
        resultTypeFrame.setLayout(resultTypeLayout)

        self.resultTypeGroup = QButtonGroup()
        pos = QCheckBox('Positive')
        pos.clicked.connect(self.changeResultType)
        pos.setChecked(True)
        self.resultType = 'positive'
        self.resultTypeGroup.addButton(pos)
        neg = QCheckBox('Negative')
        neg.clicked.connect(self.changeResultType)
        self.resultTypeGroup.addButton(neg)
        self.resultTypeGroup.setExclusive(True)
        self.resultTypeGroup.setId(pos, 2)
        self.resultTypeGroup.setId(neg, -2)

        resultTypeLayout.addWidget(pos)
        resultTypeLayout.addWidget(neg)
        optionLayout.addWidget(resultTypeFrame)

        self.tierWidget = TierWidget(corpus, include_spelling=False)
        optionLayout.addWidget(self.tierWidget)

        searchFrame = QGroupBox('Searches')
        searchLayout = QVBoxLayout()
        searchFrame.setLayout(searchLayout)

        loadSearch = QPushButton('Load recent search')
        loadSearch.clicked.connect(self.loadSearch)
        searchLayout.addWidget(loadSearch)

        saveSearch = QPushButton('Save current search')
        saveSearch.clicked.connect(self.saveSearch)
        searchLayout.addWidget(saveSearch)

        optionLayout.addWidget(searchFrame)

        self.envWidget = EnvironmentSelectWidget(self.inventory, show_full_inventory=bool(settings['show_full_inventory']))

        self.pslayout.addWidget(self.envWidget)
        self.pslayout.addWidget(optionFrame)

        self.psFrame.setLayout(self.pslayout)
        self.layout().insertWidget(0, self.psFrame)

        self.progressDialog.setWindowTitle('Searching')

    def changeResultType(self):
        if self.resultTypeGroup.checkedId() == 2:  # positive
            self.resultType = 'positive'
        else:
            self.resultType = 'negative'

    def changeMode(self):
        self.pslayout.removeWidget(self.envWidget)
        self.envWidget.deleteLater()
        if self.modeGroup.checkedId() == 0:  # segMode is checked
            self.mode = 'segMode'
            self.envWidget = EnvironmentSelectWidget(self.inventory, show_full_inventory=bool(self.settings['show_full_inventory']),
                                                     mode=self.mode)
            self.pslayout.insertWidget(0, self.envWidget)

        else:
            self.mode = 'sylMode'
            self.envWidget = EnvironmentSelectWidget(self.inventory, show_full_inventory=bool(self.settings['show_full_inventory']),
                                                     mode=self.mode)
            self.pslayout.insertWidget(0, self.envWidget)

    def accept(self):
        for n in range(self.envWidget.environmentFrame.layout().count() - 2):
            # the -2 avoids catching some unncessary widgets
            widget = self.envWidget.environmentFrame.layout().itemAt(n).widget()
            search = RecentSearch(widget)
            self.recentSearches.appendleft(search)  # recentSearches is a collections.deque object, not a regular list
        super().accept()

    def loadSearch(self):
        dialog = RecentSearchDialog(self.recentSearches, self.savedSearches)
        dialog.exec_()
        self.recentSearches = dialog.recents
        self.savedSearches = dialog.saved
        if dialog.selectedSearch is None and not dialog.currentSearches:
            return

        #first remove all of the existing environments
        #it's important to loop over the count()-2 because looping over the full count deletes important
        #widgets like the "add new environment" button
        for n in reversed(range(self.envWidget.environmentFrame.layout().count()-2)):
            widget = self.envWidget.environmentFrame.layout().itemAt(n).widget()
            try:
                widget.setParent(None)
                widget.deleteLater()
                del widget
            except AttributeError: #widget is None
                pass

        if dialog.selectedSearch is not None and not dialog.currentSearches:
            searchlist = [dialog.selectedSearch]
        else:
            searchlist = dialog.currentSearches

        for n in range(len(searchlist)):
            #add a new blank environment
            self.envWidget.addNewEnvironment()

        for index, search in enumerate(searchlist):

            #Get the widgets in the new environment and update them accordingly
            widget = self.envWidget.environmentFrame.layout().itemAt(index).widget()#== environments.EnvironmentWidget

            #update the middle widget
            widget.middleWidget.loadData(search.middleData)
            widget.middleWidget.updateLabel()

            #update the left hand side
            for value in search.lhsValue:
                lhsWidget = widget.addLhs()

            for lhs_num in range(len(search.lhsValue)):
                button = widget.lhsLayout.itemAt(lhs_num).widget()
                button.loadData(search.lhsData[lhs_num])
                button.updateLabel()

            #update the right hand side
            for value in search.rhsValue:
                rhsWidget = widget.addRhs()

            for rhs_num in range(len(search.rhsValue)):
                button = widget.rhsLayout.itemAt(rhs_num).widget()
                button.loadData(search.rhsData[rhs_num])
                button.updateLabel()

    def saveSearch(self):
        layoutCount = self.envWidget.environmentFrame.layout().count()-2  # This returns # of env spec.
        # the -2 avoids catching some unncessary widgets
        for n in range(layoutCount):  # for each environment
            widget = self.envWidget.environmentFrame.layout().itemAt(n).widget()
            search = RecentSearch(widget)
            self.savedSearches.append(search)
        alert = QMessageBox()
        alert.setWindowTitle('Success')
        alert.setText('Search{} saved!'.format('es' if layoutCount > 1 else ''))
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
        kwargs['mode'] = self.mode
        kwargs['result_type'] = self.resultType
        return kwargs

    def setResults(self, results):
        self.results = list()
        if self.mode == 'segMode':
            for w, f in results:
                segs = tuple(x.middle for x in f)
                try:
                    envs = tuple(str(x) for x in f)
                except IndexError:
                    envs = tuple()
                self.results.append({'Word': w,
                                     'Transcription': str(getattr(w, self.tierWidget.value())),
                                     'Segment': segs,
                                     'Environment': envs,
                                     'Token frequency': w.frequency})
        else:
            for word, list_of_sylEnvs in results:
                middle_syllables = tuple(syl.middle[0] for syl in list_of_sylEnvs)
                try:
                    envs = tuple(str(syl) for syl in list_of_sylEnvs)
                except IndexError:
                    envs = tuple()
                self.results.append({'Word': word,
                                     'Transcription': str(getattr(word, self.tierWidget.value())),
                                     'Segment': middle_syllables,
                                     'Environment': envs,
                                     'Token frequency': word.frequency})
