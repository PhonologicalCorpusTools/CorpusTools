from .imports import *
import time

from .widgets import TierWidget

from .windows import FunctionWorker, FunctionDialog

from .environments import EnvironmentSelectWidget

from corpustools.phonosearch import phonological_search

from corpustools.exceptions import PCTError, PCTPythonError

class PSWorker(FunctionWorker):
    def run(self):
        time.sleep(0.1)
        kwargs = self.kwargs
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
        #type(middle) == corpustools.gui.environments.EnvironmentSegmentWidget
        lhs = envWidget.lhsLayout
        rhs = envWidget.rhsLayout

        self.middleValue = middle.value()
        self.middleDisplayValue = middle.displayValue()

        self.lhsValue = [lhs.itemAt(i).widget().value() for i in range(lhs.count())]
        self.rhsValue = [rhs.itemAt(i).widget().value() for i in range(rhs.count())]
        self.lhsDisplayValue = [lhs.itemAt(i).widget().displayValue() for i in range(lhs.count())]
        self.rhsDisplayValue = [rhs.itemAt(i).widget().displayValue() for i in range(rhs.count())]

        self.displayValue = envWidget.displayValue()

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
        mainLayout = QVBoxLayout()
        tableLayout = QHBoxLayout()
        self.saved = saved

        recentFrame = QGroupBox('Recent Searches')
        recentLayout = QVBoxLayout()
        recentFrame.setLayout(recentLayout)
        recentSearchesTable = QTableWidget()
        recentSearchesTable.setColumnCount(2)
        recentSearchesTable.setHorizontalHeaderLabels(['Target', 'Environment'])
        recentSearchesTable.setRowCount(5)
        recentSearchesTable.setSelectionBehavior(QTableWidget.SelectRows)
        recentLayout.addWidget(recentSearchesTable)
        tableLayout.addWidget(recentFrame)

        for i,search in enumerate(recents):
            recentSearchesTable.setItem(i, 0, QTableWidgetItem(search.target()))
            recentSearchesTable.setItem(i, 1, QTableWidgetItem(search.environment()))

        savedFrame = QGroupBox('Saved Searches')
        savedLayout = QVBoxLayout()
        savedFrame.setLayout(savedLayout)
        self.savedSearchesTable = QTableWidget()
        self.savedSearchesTable.setColumnCount(3)
        self.savedSearchesTable.setHorizontalHeaderLabels(['Target', 'Environment', 'Notes'])
        self.savedSearchesTable.setRowCount(len(self.saved))
        self.savedSearchesTable.setSelectionBehavior(QTableWidget.SelectRows)
        savedLayout.addWidget(self.savedSearchesTable)
        tableLayout.addWidget(savedFrame)

        for i,search in enumerate(self.saved):
            self.savedSearchesTable.setItem(i, 0, QTableWidgetItem(search.target()))
            self.savedSearchesTable.setItem(i, 1, QTableWidgetItem(search.environment()))
            noteItem = QTableWidgetItem(search.note())
            noteItem.setFlags(noteItem.flags() | Qt.ItemIsEditable)
            self.savedSearchesTable.setItem(i, 2, noteItem)

        buttonLayout = QHBoxLayout()
        ok = QPushButton('OK')
        ok.clicked.connect(self.accept)
        buttonLayout.addWidget(ok)
        cancel = QPushButton('Cancel')
        cancel.clicked.connect(self.reject)
        buttonLayout.addWidget(cancel)

        mainLayout.addLayout(tableLayout)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

    def updateNote(self):
        for row in range(self.savedSearchesTable.rowCount()):
            tableItem = self.savedSearchesTable.item(row, 2)
            note = tableItem.text()
            self.saved[row].updateNote(note)

    def accept(self):
        self.updateNote()
        super().accept()

    def reject(self):
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
    def __init__(self, parent, settings, corpus, inventory, showToolTips):
        FunctionDialog.__init__(self, parent, settings, PSWorker())

        self.corpus = corpus
        self.inventory = inventory
        self.showToolTips = showToolTips
        self.recentSearches = settings['recent_searches']
        self.savedSearches = settings['saved_searches']

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
