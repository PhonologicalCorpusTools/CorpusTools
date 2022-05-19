from .imports import *
import time
import collections
import regex as re

from .widgets import TierWidget, RadioSelectWidget

from .windows import FunctionWorker, FunctionDialog

from .environments import EnvironmentSelectWidget, EnvironmentWidget, EnvironmentSyllableWidget

from corpustools.phonosearch import phonological_search

from corpustools.exceptions import PCTError, PCTPythonError
from corpustools import __version__

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

    def __init__(self, envWidget, note = str()):
        self.widgetData = list()
        self.noteData = note
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


class PSSaveDialog(QDialog):
    def __init__(self, search):
        super(PSSaveDialog, self).__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        main = QFormLayout()

        self.nameWidget = QLineEdit()

        main.addRow('Name of search', self.nameWidget) # put 'name of search' input box here
        main.addRow(QLabel('Target:'), QLabel(search.target()))
        main.addRow(QLabel('Environment:'), QLabel(search.environment()))

        mainFrame = QFrame()
        mainFrame.setLayout(main)

        layout.addWidget(mainFrame)

        self.setWindowTitle('Name this search')
        self.createButton = QPushButton('Save')
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

    def accept(self):
        self.assignName()
        QDialog.accept(self)

    def assignName(self):
        self.name = self.nameWidget.text()
        return self.name


class RecentSearchDialog(QDialog):

    def __init__(self, recents, saved, currentEnv):
        super().__init__()
        self.setWindowTitle('Searches')
        self.mainLayout = QVBoxLayout()
        self.tableLayout = QHBoxLayout()
        self.saved = saved
        self.recents = recents
        self.currentSearches = currentEnv

        self.setupRecentsTable()
        self.setupSavedTable()
        self.setupCurrentSearchTable()

        explainLayout = QHBoxLayout()
        explanation = ('* To add an environment to current search, right-click and choose "Add to current search"\n'
                       '* To remove an environment, right-click and choose "Delete search".\n'
                       '* You can also save recent searches by selecting "Save search" from the right-click menu.\n'
                       '* Click "Update environments" when you are finished.\n'
                       )
        explainLabel = QLabel()
        explainLabel.setText(explanation)
        explainLabel.setWordWrap(True)
        explainLabel.setFont(QFont("Arial", 12))
        explainLayout.addWidget(explainLabel)

        buttonLayout = QHBoxLayout()
        self.okButton = QPushButton('Update environments')
        self.okButton.clicked.connect(self.accept)
        buttonLayout.addWidget(self.okButton)
        cancel = QPushButton('Cancel')
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
        self.savedSearchesTable.setHorizontalHeaderLabels(['Name', 'Target', 'Environment'])
        self.savedSearchesTable.setRowCount(len(self.saved))
        self.savedSearchesTable.setSelectionBehavior(QTableWidget.SelectRows)
        savedLayout.addWidget(self.savedSearchesTable)
        self.tableLayout.addWidget(savedFrame)
        for i, search in enumerate(self.saved):
            noteItem = QTableWidgetItem(search.note())
            noteItem.setFlags(noteItem.flags() | Qt.ItemIsEditable)
            self.savedSearchesTable.setItem(i, 0, noteItem)

            targetItem = QTableWidgetItem(search.target())
            targetItem.setFlags(targetItem.flags() ^ Qt.ItemIsEditable)
            self.savedSearchesTable.setItem(i, 1, targetItem)

            envItem = QTableWidgetItem(search.environment())
            envItem.setFlags(envItem.flags() ^ Qt.ItemIsEditable)
            self.savedSearchesTable.setItem(i, 2, envItem)

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
        self.currentSearchesTable.setRowCount(len(self.currentSearches))
        self.currentSearchesTable.setSelectionBehavior(QTableWidget.SelectRows)
        currentLayout.addWidget(self.currentSearchesTable)
        self.tableLayout.addWidget(currentFrame)
        for i, search in enumerate(self.currentSearches):
            targetItem = QTableWidgetItem(search.target())
            targetItem.setFlags(targetItem.flags() ^ Qt.ItemIsEditable)
            self.currentSearchesTable.setItem(i, 0, targetItem)

            envItem = QTableWidgetItem(search.environment())
            envItem.setFlags(envItem.flags() ^ Qt.ItemIsEditable)
            self.currentSearchesTable.setItem(i, 1, envItem)

        self.currentSearchesTable.cellClicked.connect(self.deselectRecentTable)
        self.currentSearchesTable.cellClicked.connect(self.deselectSavedTable)

    def makeMenus(self):
        # Dropdown menu for recent searches
        self.recentMenu = QMenu(parent=self)
        self.deleteRecentAction = QAction('Delete search', self)
        self.recentToSavedAction = QAction('Save search', self)
        self.addToCurrentAction = QAction('Add to current search', self)
        self.recentMenu.addAction(self.deleteRecentAction)
        self.recentMenu.addAction(self.recentToSavedAction)
        self.recentMenu.addAction(self.addToCurrentAction)
        self.recentSearchesTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.recentSearchesTable.customContextMenuRequested.connect(self.showRecentMenu)

        # Dropdown menu for saved searches
        self.savedMenu = QMenu(parent=self)
        self.deleteSaveAction = QAction('Delete search', self)
        self.changeSavedAction = QAction('Change name', self)
        self.savedMenu.addAction(self.deleteSaveAction)
        self.savedMenu.addAction(self.changeSavedAction)
        self.savedMenu.addAction(self.addToCurrentAction)
        self.savedSearchesTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.savedSearchesTable.customContextMenuRequested.connect(self.showSavedMenu)

        # Dropdown menu for current searches
        self.currentMenu = QMenu(parent=self)
        self.deleteCurrentAction = QAction('Delete search', self)
        self.currentToSavedAction = QAction('Save search', self)
        self.currentMenu.addAction(self.deleteCurrentAction)
        self.currentMenu.addAction(self.currentToSavedAction)
        self.currentSearchesTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.currentSearchesTable.customContextMenuRequested.connect(self.showCurrentMenu)

    def showCurrentMenu(self, pos):
        index = self.currentSearchesTable.indexAt(pos)
        selected = self.currentSearchesTable.selectionModel().selectedRows()  # multiple search selection as a list
        action = self.currentMenu.exec_(self.currentSearchesTable.mapToGlobal(pos))
        item = self.currentSearchesTable.itemAt(index.row(), index.column())
        if not item or action is None:
            return
        if action == self.deleteCurrentAction:
            for index in reversed(selected):  # and loop over the list to get each search
                self.deleteCurrentSearch(index)
            return
        elif action == self.currentToSavedAction:
            for index in selected:  # and loop over the list to get each search
                self.currentToSavedTable(index)

    def showSavedMenu(self, pos):
        index = self.savedSearchesTable.indexAt(pos)
        selected = self.savedSearchesTable.selectionModel().selectedRows()  # multiple search selection as a list
        action = self.savedMenu.exec_(self.savedSearchesTable.mapToGlobal(pos))
        item = self.savedSearchesTable.itemAt(index.row(), index.column())
        if not item or action is None:
            return
        if action == self.deleteSaveAction:
            for index in reversed(selected):  # and loop over the list to get each search
                self.deleteSavedSearch(index)
            return
        if action == self.changeSavedAction:
            self.changeSavedSearch(index)
            return
        elif action == self.addToCurrentAction:
            for index in selected:
                self.addToCurrent(index, self.saved)

    def showRecentMenu(self, pos):
        index = self.recentSearchesTable.indexAt(pos)
        selected = self.recentSearchesTable.selectionModel().selectedRows()
        action = self.recentMenu.exec_(self.recentSearchesTable.mapToGlobal(pos))
        try:
            if action == self.deleteRecentAction:
                for index in reversed(selected):
                    self.deleteRecentSearch(index)
                return
            elif action == self.recentToSavedAction:
                for index in selected:
                    self.recentToSavedTable(index)
            elif action == self.addToCurrentAction:
                for index in selected:
                    self.addToCurrent(index, self.recents)
        except IndexError: # Right-clicking on an empty slot raises IndexError
            return

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

    def recentToSavedTable(self, index):
        search = self.recents[index.row()]
        dialog = PSSaveDialog(search)
        if dialog.exec_():
            search.noteData = dialog.name
        self.saved.append(search)
        self.deleteRecentSearch(index)

        # for some reason, adding a new row isn't working. a blank row is added on screen, no cell contents.
        # after closing and re-opening, the row is correctly filled (meaning self.saved is properly updated)
        # to solve this problem, update the entire table from scratch, which seems to work
        self.refreshSavedTable()

    def currentToSavedTable(self, index):
        search = self.currentSearches[index.row()]
        dialog = PSSaveDialog(search)
        if dialog.exec_():
            search.noteData = dialog.name
        self.saved.append(search)
        self.refreshSavedTable()  # update the saved table after adding a new row

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

    def changeSavedSearch(self, index):
        search = self.saved[index.row()]
        dialog = PSSaveDialog(search)
        if dialog.exec_():
            self.saved[index.row()].noteData = dialog.name
        self.refreshSavedTable()  # update the saved table after adding a new row

    def refreshSavedTable(self):
        self.savedSearchesTable.setRowCount(len(self.saved))
        for row in range(len(self.saved)):
            search = self.saved[row]

            noteItem = QTableWidgetItem(search.note())
            noteItem.setFlags(noteItem.flags() ^ Qt.ItemIsEditable)
            self.savedSearchesTable.setItem(row, 0, noteItem)

            targetItem = QTableWidgetItem(search.target())
            targetItem.setFlags(targetItem.flags() ^ Qt.ItemIsEditable)
            self.savedSearchesTable.setItem(row, 1, targetItem)

            envItem = QTableWidgetItem(search.environment())
            envItem.setFlags(envItem.flags() ^ Qt.ItemIsEditable)
            self.savedSearchesTable.setItem(row, 2, envItem)

    def updateNote(self):
        for row in range(self.savedSearchesTable.rowCount()):
            tableItem = self.savedSearchesTable.item(row, 2)
            if tableItem is None:
                note = str()
            else:
                if self.saved[row].noteData != '-':
                    note = self.saved[row].noteData
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


class PSEnvironmentSelectWidget(EnvironmentSelectWidget):
    env_num_changed = Signal(str)

    def __init__(self, inventory, rt, show_full_inventory, mode='segMode'):
        super().__init__(inventory, show_full_inventory=show_full_inventory, mode=mode)
        self.resultTypeGroup = rt
        self.env_num_changed.connect(self.rt_control)

    def addNewEnvironment(self):
        if self.mode == 'segMode':
            envWidget = PSEnvironmentWidget(inventory=self.inventory, middle=self.middle, parent=self,
                                            show_full_inventory=self.show_full_inventory)
        else:
            envWidget = PSEnvironmentSyllableWidget(inventory=self.inventory, middle=self.middle, parent=self,
                                                    show_full_inventory=self.show_full_inventory)
        pos = self.environmentFrame.layout().count() - 2
        self.environmentFrame.layout().insertWidget(pos, envWidget)
        self.env_num_changed.emit('add')

    def addCopiedEnvironment(self, args):
        copy_data = args[0] if args else None
        if self.mode == 'segMode':
            envWidget = PSEnvironmentWidget(self.inventory, middle=copy_data.middle, parent=self, copy_data=copy_data)
        else:
            envWidget = PSEnvironmentSyllableWidget(self.inventory, middle=copy_data.middle, parent=self,
                                                    copy_data=copy_data)
        pos = self.environmentFrame.layout().count() - 2
        self.environmentFrame.layout().insertWidget(pos, envWidget)
        self.env_num_changed.emit('add')

    @Slot(str)
    def rt_control(self, text):
        # This function checks the number of environments (pos) and enable or disable 'negative search'.
        # 'text' is either 'add' or 'remove'. It indicates where the signal has started.
        pos = self.environmentFrame.layout().count() - 2
        if text == 'remove':
            pos -= 1
        if pos > 1:  # if there are more than one environments, we disable 'negative search' in result type
            if self.resultTypeGroup.widgets[1].isChecked():  # if 'negative search' has been previously selected.
                alert = QMessageBox(QMessageBox.Warning,
                                    'Negative search with multiple environments',
                                    'Negative search is not compatible with multiple environments.\n\n'
                                    'Click "OK" to continue with multiple environments and a positive search type\n'
                                    'Click "Cancel" to go back to a negative search type and a single environment.\n\n'
                                    'You can run successive negative searches with different single environments '
                                    'if you need to get multiple negative-search results.',
                                    QMessageBox.NoButton, self)
                alert.addButton('OK', QMessageBox.AcceptRole)
                alert.addButton('Cancel', QMessageBox.RejectRole)
                alert.exec_()
                if alert.buttonRole(alert.clickedButton()) == QMessageBox.RejectRole:
                    if text == 'add':
                        self.environmentFrame.children()[-1].deleteLater()
                        pass
                    return
                self.resultTypeGroup.widgets[1].setChecked(False)  # then uncheck 'negative search'
                self.resultTypeGroup.widgets[0].setChecked(True)  # and check 'positive search'
            self.resultTypeGroup.widgets[1].setEnabled(False)  # disable 'negative search' in result type
        else:
            self.resultTypeGroup.widgets[1].setEnabled(True)  # enable 'negative search' in result type


class PSEnvironmentWidget(EnvironmentWidget):
    def __init__(self, inventory, parent=None, middle=True, show_full_inventory=False, copy_data=None):
        super().__init__(inventory=inventory, parent=parent, middle=middle, copy_data=copy_data, show_full_inventory=show_full_inventory)
        self.removeButton.clicked.connect(self.deleteEnvironment)

    def deleteEnvironment(self):
        self.deleteLater()
        self.parent.env_num_changed.emit('remove')


class PSEnvironmentSyllableWidget(EnvironmentSyllableWidget):
    def __init__(self, inventory, parent=None, middle=True, show_full_inventory=False, copy_data=None):
        super().__init__(inventory=inventory, parent=parent, middle=middle, copy_data=copy_data, show_full_inventory=show_full_inventory)
        self.removeButton.clicked.connect(self.deleteEnvironment)

    def deleteEnvironment(self):
        self.deleteLater()
        self.parent.env_num_changed.emit('remove')


class PhonoSearchDialog(FunctionDialog):
    header = ['Corpus', 'PCT ver.', 'Word', 'Transcription', 'Token frequency', 'Target', 'Environment',
              'Transcription tier', 'Result type', 'Min Word Freq', 'Max Word Freq', 'Min Phoneme Number',
              'Max Phoneme Number', 'Min Syllable Number', 'Max Syllable Number']
    summary_header = ['Corpus', 'PCT ver.', 'Target', 'Environment', 'Type frequency', 'Token frequency',
                      'Transcription tier', 'Result type', 'Min Word Freq', 'Max Word Freq', 'Min Phoneme Number',
                      'Max Phoneme Number', 'Min Syllable Number', 'Max Syllable Number']
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

        self.modeGroup = RadioSelectWidget('Search mode',
                                           collections.OrderedDict([('Segments', 'segs'),
                                                                    ('Syllables', 'syls')])
                                           )
        self.mode = 'segMode'  # default search mode is 'segment mode' -- when the user doesn't touch any radio button

        if len(inventory.syllables) == 0:  # if there's no syllable in the corpus,
            self.modeGroup.widgets[1].setEnabled(False)  # then grey out the syllable search option.

        for searchmode_btn in self.modeGroup.widgets:
            searchmode_btn.toggled.connect(lambda: self.changeMode(searchmode_btn))

        optionLayout.addWidget(self.modeGroup)

        resultTypeFrame = QGroupBox('Result type')
        resultTypeLayout = QVBoxLayout()
        resultTypeFrame.setLayout(resultTypeLayout)

        self.resultTypeGroup = RadioSelectWidget('Result type',
                                                 collections.OrderedDict([('Positive', 'pos'),
                                                                          ('Negative', 'neg')]))
        self.resultType = 'positive'  # default result type is 'positive' -- when the users don't touch any radio button

        for n, resulttype_btn in enumerate(self.resultTypeGroup.widgets):
            resulttype_btn.toggled.connect(lambda: self.changeResultType(resulttype_btn))
        optionLayout.addWidget(self.resultTypeGroup)

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
        self.segsum = QCheckBox('List target segments and environments\nseparately in summary results')
        optionLayout.addWidget(self.segsum)
        # for additional filters (word/phoneme/syllable frequency filters)
        validator = QDoubleValidator(float('inf'), 0, 8)  # values should be 0-inf with max 8 sub-decimal digits
        filterFrame = QGroupBox('Additional filters')
        filterLayout = QVBoxLayout()
        filterFrame.setLayout(filterLayout)
        filterFrame.setFixedWidth(200)

        wordFreqFrame = QGroupBox('Word frequency filters')
        wFbox = QFormLayout()
        self.minWordFreqFrame = QLineEdit()
        self.minWordFreqFrame.setValidator(validator)
        wFbox.addRow('Minimum:', self.minWordFreqFrame)
        self.maxWordFreqFrame = QLineEdit()
        self.maxWordFreqFrame.setValidator(validator)
        wFbox.addRow('Maximum:', self.maxWordFreqFrame)
        wordFreqFrame.setLayout(wFbox)
        filterLayout.addWidget(wordFreqFrame)

        phonFreqFrame = QGroupBox('Phoneme number filters')
        pFbox = QFormLayout()
        self.minPhonFreqFrame = QLineEdit()
        self.minPhonFreqFrame.setValidator(validator)
        pFbox.addRow('Minimum:', self.minPhonFreqFrame)
        self.maxPhonFreqFrame = QLineEdit()
        self.maxPhonFreqFrame.setValidator(validator)
        pFbox.addRow('Maximum:', self.maxPhonFreqFrame)
        phonFreqFrame.setLayout(pFbox)
        filterLayout.addWidget(phonFreqFrame)

        syllFreqFrame = QGroupBox('Syllable number filters')
        sFbox = QFormLayout()
        self.minSyllFreqFrame = QLineEdit()
        self.minSyllFreqFrame.setValidator(validator)
        sFbox.addRow('Minimum:', self.minSyllFreqFrame)
        self.maxSyllFreqFrame = QLineEdit()
        self.maxSyllFreqFrame.setValidator(validator)
        sFbox.addRow('Maximum:', self.maxSyllFreqFrame)
        if len(inventory.syllables) == 0:
            # grey out the box if there are no syllable delimiters
            self.maxSyllFreqFrame.setStyleSheet("""QLineEdit { background-color: rgb(236, 236, 236);}""")
            self.maxSyllFreqFrame.setEnabled(False)
            self.minSyllFreqFrame.setStyleSheet("""QLineEdit { background-color: rgb(236, 236, 236);}""")
            self.minSyllFreqFrame.setEnabled(False)
        syllFreqFrame.setLayout(sFbox)
        filterLayout.addWidget(syllFreqFrame)

        self.envWidget = PSEnvironmentSelectWidget(inventory=self.inventory, rt=self.resultTypeGroup,
                                                   show_full_inventory=bool(settings['show_full_inventory']))
        # self.envWidget = EnvironmentSelectWidget(inventory=self.inventory, show_full_inventory=bool(settings['show_full_inventory']))

        self.pslayout.addWidget(self.envWidget)
        self.pslayout.addWidget(optionFrame)
        self.pslayout.addWidget(filterFrame)

        self.psFrame.setLayout(self.pslayout)

        self.layout().insertWidget(0, self.psFrame)

        self.progressDialog.setWindowTitle('Searching')

    def changeResultType(self, btn):
        if btn.text() == 'Negative':
            if btn.isChecked():     # 'negative' is checked
                self.resultType = 'negative'

                self.segsum.setChecked(False)  # unselect the list-summary-result-by-seg option
                self.segsum.setEnabled(False)  # and grey it out
            else:                   # 'negative' is deselected
                self.resultType = 'positive'
                self.segsum.setEnabled(True)  # list-sum-res-by-seg option enabled

    def changeMode(self, btn):
        self.pslayout.removeWidget(self.envWidget)
        self.envWidget.deleteLater()

        if btn.text() == 'Syllables':
            if btn.isChecked():     # sylMode is checked
                self.mode = 'sylMode'
            else:                   # sylMode is deselected
                self.mode = 'segMode'
        self.envWidget = PSEnvironmentSelectWidget(self.inventory,
                                                   show_full_inventory=bool(self.settings['show_full_inventory']),
                                                   mode=self.mode,
                                                   rt=self.resultTypeGroup)
        self.pslayout.insertWidget(0, self.envWidget)

    def accept(self):
        for n in range(self.envWidget.environmentFrame.layout().count() - 2):
            # the -2 avoids catching some unncessary widgets
            widget = self.envWidget.environmentFrame.layout().itemAt(n).widget()
            search = RecentSearch(widget)
            self.recentSearches.appendleft(search)  # recentSearches is a collections.deque object, not a regular list
        super().accept()

    def loadSearch(self):
        currentlyLoaded = list()
        for n in range(self.envWidget.environmentFrame.layout().count() - 2):
            widget = self.envWidget.environmentFrame.layout().itemAt(n).widget()
            widget = RecentSearch(widget)
            currentlyLoaded.append(widget)

        dialog = RecentSearchDialog(self.recentSearches, self.savedSearches, currentlyLoaded)
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
        if layoutCount == 0:   # save search should not work when no environment is specified
            return
        # size of layoutCount
        cancelCount = 0 # should deduct the number of 'cancels' the user selects on the save window
        for n in range(layoutCount):  # for each environment
            widget = self.envWidget.environmentFrame.layout().itemAt(n).widget()
            search = RecentSearch(widget)
            dialog = PSSaveDialog(search)
            if dialog.exec_():
                name = dialog.name
            else:
                cancelCount += 1
                continue
            search = RecentSearch(widget, name)
            self.savedSearches.append(search)

        layoutCount = layoutCount - cancelCount
        # the number of cancels is deducted so that the 'success' window shows the exact number of searches saved
        if layoutCount > 0:
            alert = QMessageBox()
            alert.setWindowTitle('Success')
            alert.setText('%d Search%s saved!' % (layoutCount, 'es' if layoutCount > 1 else ''))
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

        # The following chunk is messy. Need to be streamlined.
        try:
            min_word_freq = float(self.minWordFreqFrame.text())
        except ValueError:
            min_word_freq = 0.0
        try:
            min_phon_num = float(self.minPhonFreqFrame.text())
        except ValueError:
            min_phon_num = 0.0
        try:
            min_syl_num = float(self.minSyllFreqFrame.text())
        except ValueError:
            min_syl_num = 0.0

        try:
            max_word_freq = float(self.maxWordFreqFrame.text())
        except ValueError:
            max_word_freq = float('inf')
        try:
            max_phon_num = float(self.maxPhonFreqFrame.text())
        except ValueError:
            max_phon_num = float('inf')
        try:
            max_syl_num = float(self.maxSyllFreqFrame.text())
        except ValueError:
            max_syl_num = float('inf')

        kwargs['min_word_freq'] = min_word_freq
        kwargs['min_phon_num'] = min_phon_num
        kwargs['min_syl_num'] = min_syl_num
        kwargs['max_word_freq'] = max_word_freq
        kwargs['max_phon_num'] = max_phon_num
        kwargs['max_syl_num'] = max_syl_num

        kwargs['corpus'] = self.corpus
        kwargs['sequence_type'] = self.tierWidget.value()
        kwargs['mode'] = self.mode
        kwargs['result_type'] = self.resultType
        kwargs['seg_summary'] = self.segsum

        return kwargs

    def setResults(self, results):
        self.results = list()

        # 'additional' filters
        freq_filters = {
            "min_word": self.minWordFreqFrame.text(),
            "max_word": self.maxWordFreqFrame.text(),
            "min_phoneme": self.minPhonFreqFrame.text(),
            "max_phoneme": self.maxPhonFreqFrame.text(),
            "min_syl": self.minSyllFreqFrame.text(),
            "max_syl": self.maxSyllFreqFrame.text()
        }
        for key in freq_filters:
            if len(freq_filters[key]) == 0:
                freq_filters[key] = 'N/A'           # if user didn't input a freq filter, 'N/A' in the result window.

        for word, found in results:
            if self.mode == 'segMode':
                userinput_target = tuple(', '.join(list(y.original_middle)) for y in self.envWidget.value())
                userinput_env = tuple(str(y) for y in self.envWidget.value())
                fo = [f[1] for f in found]  # fo drops all env# info. i.e., contains environment objects only.

                if str(word) == 'N/A' and word.transcription is None:  # if there was no hit from the search, side way
                    res_transcription = target = envs = word.frequency = 'N/A'

                else:                                                   # regular cases with one or more words searched
                    f = list(filter(None, fo))
                    target = tuple(x.middle for x in f)
                    res_transcription = str(getattr(word, self.tierWidget.value()))
                    if len(target) == 0 and self.resultType == 'negative':
                        target = userinput_target
                    try:
                        envs = tuple(str(x) for x in f)
                        if len(envs) == 0 and self.resultType == 'negative':
                            envs = userinput_env
                    except IndexError:
                        envs = tuple()

            else:  # syllable search mode
                userinput_target, userinput_env = self.cleanse_syl_userinput()
                fo = [f[1] for f in found]  # fo drops all env# info. i.e., contains environment objects only.

                if str(word) == 'N/A' and word.transcription is None:  # if there was no hit from the search, side way
                    res_transcription = target = envs = word.frequency = 'N/A'

                else:                                                   # regular cases with one or more words searched
                    list_of_sylEnvs = list(filter(None, fo))
                    target = tuple(
                        syl.print_syl_structure(env=False) for syl in list_of_sylEnvs)  # 'target' column in res. window

                    if len(target) == 0 and self.resultType == 'negative':
                        target = userinput_target
                    try:
                        envs = tuple(syl.print_syl_structure(env=True) for syl in
                                     list_of_sylEnvs)  # 'environment' col in res. win
                        if len(envs) == 0 and self.resultType == 'negative':
                            envs = userinput_env
                    except IndexError:
                        envs = tuple()
                    res_transcription = str(getattr(word, self.tierWidget.value()))

            self.results.append({'Corpus': self.corpus.name,
                                 'PCT ver.': __version__,  # self.corpus._version,
                                 'Word': word,
                                 'Transcription': res_transcription,
                                 'Target': target,
                                 'Environment': envs,
                                 'Transcription tier': self.tierWidget.displayValue(),
                                 'Result type': self.resultType,
                                 'Token frequency': word.frequency,
                                 'Min Word Freq': freq_filters['min_word'],
                                 'Max Word Freq': freq_filters['max_word'],
                                 'Min Phoneme Number': freq_filters['min_phoneme'],
                                 'Max Phoneme Number': freq_filters['max_phoneme'],
                                 'Min Syllable Number': freq_filters['min_syl'],
                                 'Max Syllable Number': freq_filters['max_syl'],
                                 'userinput_target': userinput_target,  # target from the user setting (for summary)
                                 'userinput_env': userinput_env,  # env from user setting (used in summary view)
                                 'raw_env': found})

    def cleanse_syl_userinput(self):
        """Convert sylprint() results into more readable strings.

        Parametres
        ----------

        Returns
        -------
        tuple(str, ...), tuple(str, ...)
            Two tuples 'userinput_evn' and 'userinput_target' that feed into the PhonoSearch result window. They
            can have more than one str. Each str represents each env or target that the user inputs.
        """
        # this function changes sylprint results into more readable string.
        # returns userinput_env and unierinput_target
        envs = tuple([y.lhs, y.rhs] for y in self.envWidget.value())
        targets = tuple(y.middle for y in self.envWidget.value())

        userinput_env = list()
        for env in envs:
            lhs, rhs = "", ""
            if len(env[0]) > 0:
                lhs = [self.sylprint(e) for e in env[0]]
                lhs = ", ".join(lhs)
                lhs += " " if len(lhs) > 0 else lhs
            if len(env[1]) > 0:
                rhs = [self.sylprint(e) for e in env[1]]
                rhs = ", ".join(rhs)
                rhs += " " if len(rhs) > 0 else rhs
            userinput_env.append(lhs + "_" + rhs)

        userinput_target = list()
        for target in targets:
            userinput_target.append(self.sylprint(target[0]))
        # userinput_env = lhs + "_" + rhs
        # userinput_target = "".join([self.sylprint(target[0]) for target in targets])

        return tuple(userinput_target), tuple(userinput_env)

    def sylprint(self, syll_dict):
        if list(syll_dict['nonsegs']):
            chunks = list(syll_dict['nonsegs'])
            chunks = "{" + ",".join(chunks) + "}" if len(chunks) > 1 else chunks[0]

            return chunks

        chunks = []

        for d in syll_dict.keys():
            if len(syll_dict[d]) == 0 or list(syll_dict[d])[0] == 'None':
                pass
            elif len(syll_dict[d]['contents']) == 0:
                pass
            else:
                header = d[0].capitalize() if d in ['onset', 'nucleus', 'coda'] else d.capitalize()
                contents = str()
                for c in syll_dict[d]['contents'][0]:
                    contents += c
                chunks.append(header + ":{[" + ", ".join(contents) + "], option: " + syll_dict[d]['search_type'] + "}")

        return "S:{" + ", ".join(chunks) + "}"
