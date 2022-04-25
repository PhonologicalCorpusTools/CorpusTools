import csv
from itertools import product

from .imports import *
from .models import VariantModel, ResultsModel, PhonoSearchResultsModel, ConsonantModel, VowelModel
from .multimedia import AudioPlayer
import corpustools.gui.widgets as PCTWidgets
from .widgets import TableWidget


class LexiconView(QWidget):
    selectTokens = Signal(object)
    wordsChanged = Signal()
    wordToBeEdited = Signal(object, object)
    columnRemoved = Signal()

    def __init__(self,parent=None):
        super(LexiconView, self).__init__(parent=parent)
        self._parent = parent
        self.setStyleSheet( """ TableWidget::item:selected:active {
                                     background: lightblue;
                                }
                                TableWidget::item:selected:!active {
                                     background: lightblue;
                                }
                                TableWidget::item:selected:disabled {
                                     background: lightblue;
                                }
                                TableWidget::item:selected:!disabled {
                                     background: lightblue;
                                }
                                """
                                )

        self.table = TableWidget(self)
        self.table.doubleClicked.connect(self.editWord)
        layout = QVBoxLayout()
        self.searchField = QLineEdit()
        self.searchField.setPlaceholderText('Search...')
        self.searchField.returnPressed.connect(self.search)
        layout.addWidget(self.searchField, alignment = Qt.AlignRight)
        layout.addWidget(self.table)

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.showMenu)

        header = self.table.horizontalHeader()
        header.setContextMenuPolicy(Qt.CustomContextMenu)
        header.customContextMenuRequested.connect( self.showHeaderMenu )

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def search(self):
        text = self.searchField.text()
        if not text:
            return
        model = self.table.model()
        curSelection = self.table.selectionModel().selectedRows()
        if curSelection:
            row = curSelection[-1].row() + 1
        else:
            row = 0
        start = model.index(row,0)
        matches = model.match(start, Qt.DisplayRole, text, 1, Qt.MatchContains)
        if matches:
            index = matches[0]
            self.table.selectionModel().select(index,
                    QItemSelectionModel.SelectCurrent|QItemSelectionModel.Rows)
            self.table.scrollTo(index,QAbstractItemView.PositionAtCenter)
        else:
            start = model.index(0,0)
            matches = model.match(start, Qt.DisplayRole, text, 1, Qt.MatchContains)
            if matches:
                index = matches[0]
                self.table.selectionModel().select(index,
                    QItemSelectionModel.SelectCurrent|QItemSelectionModel.Rows)
                self.table.scrollTo(index,QAbstractItemView.PositionAtCenter)
            else:
                self.table.selectionModel().clear()

    def highlightType(self,wordtype):
        if self.table.model() is None:
            return
        model = self.table.model()
        self.table.selectionModel().clear()
        for i,r in enumerate(model.rows):
            if model.corpus[r] == wordtype:
                index = model.index(i,0)
                break
        else:
            return
        self.table.selectionModel().select(index,
                    QItemSelectionModel.SelectCurrent|QItemSelectionModel.Rows)
        self.table.scrollTo(index,QAbstractItemView.PositionAtCenter)

    def setModel(self, model):
        self.table.setModel(model)

    def showHeaderMenu(self, pos):
        header = self.table.horizontalHeader()
        column = header.logicalIndexAt(pos.x())

        if column < 3:
            return
        attribute = self.table.model().headerData(column,
                                        Qt.Horizontal, Qt.DisplayRole)

        editAction = QAction(self)
        editAction.setText('Edit column details')
        editAction.triggered.connect(lambda: self.editColumn(column))

        removeAction = QAction(self)
        removeAction.setText('Remove column')
        removeAction.triggered.connect(lambda: self.removeColumn(column))

        menu = QMenu(self)
        #menu.addAction(editAction)
        menu.addAction(removeAction)

        menu.popup(header.mapToGlobal(pos))

    def editColumn(self, index):
        pass

    def removeColumn(self, column):
        attribute = self.table.model().headerData(column,
                                        Qt.Horizontal, Qt.DisplayRole)
        msgBox = QMessageBox(QMessageBox.Warning, "Remove columns",
                "This will permanently remove the column \'{}\'.  Are you sure?".format(str(attribute)),
                QMessageBox.NoButton, self)
        msgBox.addButton("Remove", QMessageBox.AcceptRole)
        msgBox.addButton("Cancel", QMessageBox.RejectRole)
        if msgBox.exec_() != QMessageBox.AcceptRole:
            return
        self.table.model().removeAttributes([attribute])
        self.columnRemoved.emit()

    def showMenu(self, pos):
        menu = QMenu()

        neighbourAction = QAction(self)
        neighbourAction.setText('List neighbours')
        #menu.addAction(neighbourAction)

        editWordAction = QAction(self)
        editWordAction.setText('Edit word details')
        editWordAction.triggered.connect(lambda: self.editWord(self.table.indexAt(pos)))
        menu.addAction(editWordAction)

        hideAction = QAction(self)
        nonlexhidden = self.table.model().nonLexHidden
        if nonlexhidden:
            hideAction.setText('Show non-transcribed items')
        else:
            hideAction.setText('Hide non-transcribed items')
        hideAction.triggered.connect(lambda: self.hideNonLexical(not nonlexhidden))
        menu.addAction(hideAction)

        variantsAction = QAction(self)
        variantsAction.setText('List pronunciation variants')
        variantsAction.triggered.connect(lambda: self.showVariants(self.table.indexAt(pos)))
        menu.addAction(variantsAction)

        findTokensAction = QAction(self)
        findTokensAction.setText('Find all tokens')
        findTokensAction.triggered.connect(lambda: self.findTokens(self.table.indexAt(pos)))
        menu.addAction(findTokensAction)

        menu.addSeparator()

        removeWordAction = QAction(self)
        removeWordAction.setText('Remove word')
        removeWordAction.triggered.connect(lambda: self.removeWord(self.table.indexAt(pos)))
        menu.addAction(removeWordAction)
        action = menu.exec_(self.table.viewport().mapToGlobal(pos))

    def editWord(self, index):
        word = self.table.model().wordObject(index.row())
        self.wordToBeEdited.emit(index.row(), word)

    def removeWord(self,index):
        word_key = self.table.model().rows[index.row()]

        msgBox = QMessageBox(QMessageBox.Warning, "Remove word",
                "Are you sure you want to remove '{}'?".format(str(self.table.model().corpus[word_key])),
                QMessageBox.NoButton, self)
        msgBox.addButton("Continue", QMessageBox.AcceptRole)
        msgBox.addButton("Abort", QMessageBox.RejectRole)
        if msgBox.exec_() != QMessageBox.AcceptRole:
            return
        self.table.model().removeWord(word_key)
        self.wordsChanged.emit()

    def hideNonLexical(self,b):
        self.table.model().hideNonLexical(b)

    def findTokens(self, index):
        tokens = self.table.model().wordObject(index.row()).wordtokens
        self.selectTokens.emit(tokens)

    def showVariants(self, index):
        variantDialog = VariantView(self, self.table.model().wordObject(index.row()))
        variantDialog.show()

class VariantView(QDialog):
    def __init__(self, parent, word):
        QDialog.__init__(self, parent)
        self.setWindowTitle('Pronunciation variants')
        layout = QVBoxLayout()
        self.table = TableWidget()
        layout.addWidget(self.table)
        self.table.setModel(VariantModel(word))
        closeButton = QPushButton('Close')
        closeButton.clicked.connect(self.reject)
        layout.addWidget(closeButton)
        self.setLayout(layout)

class TextView(QAbstractItemView):
    ExtraHeight = 3
    ExtraWidth = 15
    resizeCompleted = Signal()
    def __init__(self, parent=None):
        self.idealHeight = 0
        self.idealWidth = 0
        QAbstractItemView.__init__(self, parent)

        self.hashIsDirty = False
        self.rectForRow = dict()

        self.horizontalScrollBar().setRange(0,0)
        self.verticalScrollBar().setRange(0,0)
        self._resize_timer = None
        self.resizeCompleted.connect(self.handleResizeCompleted)

    def updateResizeTimer(self, interval=None):
        if self._resize_timer is not None:
            self.killTimer(self._resize_timer)
        if interval is not None:
            self._resize_timer = self.startTimer(interval)
        else:
            self._resize_timer = None

    def resizeEvent(self, event):
        self.updateResizeTimer(300)

    def timerEvent(self, event):
        if event.timerId() == self._resize_timer:
            self.updateResizeTimer()
            self.resizeCompleted.emit()

    def handleResizeCompleted(self):
        self.hashIsDirty = True
        self.calculateRectsIfNecessary()
        self.updateGeometries()

    def setModel(self,model):
        QAbstractItemView.setModel(self, model)
        self.hashIsDirty = True
        self.setItemDelegate(QStyledItemDelegate())

    def edit(self, index, trigger, event):
        if trigger == QAbstractItemView.DoubleClicked:
            return False
        return QAbstractItemView.edit(self, index, trigger, event)

    def calculateRectsIfNecessary(self):
        if not self.hashIsDirty:
            return
        if self.model() is None:
            return

        fm = QFontMetrics(self.font())
        rowHeight = fm.height() + self.ExtraHeight
        maxWidth = self.viewport().width()
        minimumWidth = 0
        x = 0
        y = 0
        for row in range(self.model().rowCount(self.rootIndex())):
            index = self.model().index(row, 0, self.rootIndex())
            text = self.model().data(index,Qt.DisplayRole)
            textWidth = fm.width(text)
            if not (x == 0 or x+textWidth+self.ExtraWidth < maxWidth):
                y += rowHeight
                x = 0
            elif x != 0:
                x += self.ExtraWidth
            self.rectForRow[row] = QRectF(x, y, textWidth + self.ExtraWidth, rowHeight)
            if textWidth > minimumWidth:
                minimumWidth = textWidth
            x += textWidth
        self.idealWidth = minimumWidth + self.ExtraWidth
        self.idealHeight = y + rowHeight
        self.hashIsDirty = False
        self.viewport().update()

    def visualRect(self,index):
        if index.isValid():
            rect = self.viewportRectForRow(index.row()).toRect()
            return rect

    def viewportRectForRow(self, row):
        self.calculateRectsIfNecessary()
        rect = self.rectForRow[row].toRect()
        if not rect.isValid():
            return rect
        return QRectF(rect.x() - self.horizontalScrollBar().value(),
                    rect.y() - self.verticalScrollBar().value(),
                    rect.width(), rect.height())

    def isIndexHidden(self, index):
        return False

    def horizontalOffset(self):
        return self.horizontalScrollBar().value()

    def verticalOffset(self):
        return self.verticalScrollBar().value()

    def scrollTo(self, index, ScrollHint):
        area = self.viewport().rect()
        rect = self.visualRect(index)

        if rect.left() < area.left():
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() + rect.left() - area.left())
        elif rect.right() > area.right():
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() + min(
                    rect.right() - area.right(), rect.left() - area.left()))

        if rect.top() < area.top():
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() + rect.top() - area.top())
        elif rect.bottom() > area.bottom():
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() + min(
                    rect.bottom() - area.bottom(), rect.top() - area.top()))
        self.viewport().update()

    def indexAt(self, point):
        prx = point.x() + self.horizontalScrollBar().value()
        pry = point.y() + self.verticalScrollBar().value()

        self.calculateRectsIfNecessary()
        for k,v in self.rectForRow.items():
            if v.contains(point):
                return self.model().index(k,0, self.rootIndex())
        return QModelIndex()

    def dataChanged(self, topLeft, bottomRight, roles):
        self.hashIsDirty = True
        QAbstractItemView.dataChanged(self, topLeft, bottomRight, roles)

    def rowsInserted(self, parent, start, end):
        self.hashIsDirty = True
        QAbstractItemView.rowsInserted(self, parent, start, end)

    def rowsAboutToBeRemoved(self, parent, start, end):
        self.hashIsDirty = True
        QAbstractItemView.rowsAboutToBeRemoved(self, parent, start, end)

    def moveCursor(self, cursorAction, modifiers):
        index = self.currentIndex()
        if ((cursorAction == QAbstractItemView.MoveLeft and index.row() > 0) or
            cursorAction == QAbstractItemView.MoveRight and index.row() + 1 < self.model().rowCount()):
            if cursorAction == QAbstractItemView.MoveLeft:
                offset = -1
            else:
                offset = 1
            index = self.model().index(index.row() + offset, index.column(), index.parent())
        elif ((cursorAction == QAbstractItemView.MoveUp and index.row() > 0) or
            cursorAction == QAbstractItemView.MoveDown and index.row() + 1 < self.model().rowCount()):
            fm = QFontMetrics(self.font())
            if cursorAction == QAbstractItemView.MoveUp:
                offset = -1
            else:
                offset = 1
            rowHeight = (fm.height() + self.ExtraHeight) * offset
            rect = self.viewportRectForRow(index.row()).toRect()
            point = QPoint(rect.center().x(), rect.center().y() + rowHeight)
            while point.x() >= 0:
                index = self.indexAt(point)
                if index.isValid():
                    break
                point.setX(point.x() - fm.width('n'))
        return index

    def scrollContentsBy(self, dx, dy):
        self.scrollDirtyRegion(dx, dy)
        self.viewport().scroll(dx, dy)

    def setSelection(self, rect, flags):
        rectangle = QRectF(rect.translated(self.horizontalScrollBar().value(),
                self.verticalScrollBar().value()).normalized())
        self.calculateRectsIfNecessary()
        firstRow = self.model().rowCount()
        lastRow = -1
        for k,v in self.rectForRow.items():
            if v.intersects(rectangle):
                if not (firstRow < k):
                    firstRow = k
                if not (lastRow > k):
                    lastRow = k
        if firstRow != self.model().rowCount() and lastRow != -1:
            selection = QItemSelection(self.model().index(firstRow,0,self.rootIndex()),
                            self.model().index(lastRow, 0, self.rootIndex()))
            self.selectionModel().select(selection, flags)
        else:
            invalid = QModelIndex()
            selection = QItemSelection(invalid, invalid)
            self.selectionModel().select(selection, flags)

        self.update()

    def visualRegionForSelection(self, selection):
        region = QRegion()

        for span in selection:
            for row in range(span.top(), span.bottom() + 1):
                for col in range(span.left(), span.right() + 1):
                    index = self.model().index(row, col, self.rootIndex())
                    region += self.visualRect(index)

        return region

    def paintEvent(self,event):
        if self.model() is None:
            return
        painter = QPainter(self.viewport())
        painter.setRenderHints(QPainter.Antialiasing|QPainter.TextAntialiasing)
        for row in range(self.model().rowCount(self.rootIndex())):
            index = self.model().index(row, 0, self.rootIndex())
            rect = self.viewportRectForRow(row)
            if not rect.isValid() or rect.bottom() < 0 or\
                    rect.y() > self.viewport().height():
                continue
            option = self.viewOptions()
            option.rect = rect.toRect()
            if self.selectionModel().isSelected(index):
                option.state |= QStyle.State_Selected
            if self.currentIndex() == index:
                option.state |= QStyle.State_HasFocus
            self.itemDelegate().paint(painter, option, index)
            self.paintOutline(painter,rect)

    def paintOutline(self, painter, rectangle):
        rect = rectangle.adjusted(0,0,-1,-1)
        painter.save()
        painter.setPen(QPen(self.palette().dark().color(), 0.5))
        painter.drawRect(rect)
        painter.setPen(QPen(Qt.black,0.5))
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())
        painter.drawLine(rect.bottomRight(), rect.topRight())
        painter.restore()

    def updateGeometries(self):
        fm = QFontMetrics(self.font())
        rowHeight = fm.height() + self.ExtraHeight
        self.horizontalScrollBar().setSingleStep(fm.width('n'))
        self.horizontalScrollBar().setPageStep(self.viewport().width())
        self.horizontalScrollBar().setRange(0, max(0, self.idealWidth - self.viewport().width()))

        self.verticalScrollBar().setSingleStep(rowHeight)
        self.verticalScrollBar().setPageStep(self.viewport().height())
        self.verticalScrollBar().setRange(0, max(0,self.idealHeight - self.viewport().height()))

    def mousePressEvent(self, event):
        QAbstractItemView.mousePressEvent(self, event)
        self.setCurrentIndex(self.indexAt(event.pos()))

class DiscourseView(QWidget):
    selectType = Signal(object)
    def __init__(self,parent=None):
        super(DiscourseView, self).__init__(parent=parent)

        self.text = TextView(self)
        self.text.setContextMenuPolicy(Qt.CustomContextMenu)
        self.text.customContextMenuRequested.connect(self.showMenu)
        self.text.hide()

        self.table = TableWidget(self)
        self.table.setSortingEnabled(False)
        try:
            self.table.horizontalHeader().setSectionsClickable(False)
        except AttributeError:
            self.table.horizontalHeader().setClickable(False)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.showMenu)

        self.setStyleSheet( """ TextView::item:selected:active {
                                     background: lightblue;
                                }
                                TextView::item:selected:!active {
                                     background: lightblue;
                                }
                                TextView::item:selected:disabled {
                                     background: lightblue;
                                }
                                TextView::item:selected:!disabled {
                                     background: lightblue;
                                }
                                TableWidget::item:selected:active {
                                     background: lightblue;
                                }
                                TableWidget::item:selected:!active {
                                     background: lightblue;
                                }
                                TableWidget::item:selected:disabled {
                                     background: lightblue;
                                }
                                TableWidget::item:selected:!disabled {
                                     background: lightblue;
                                }
                                """
                                )

        layout = QVBoxLayout()
        self.searchField = QLineEdit()
        self.searchField.setPlaceholderText('Search...')
        self.searchField.returnPressed.connect(self.search)
        layout.addWidget(self.searchField, alignment = Qt.AlignRight)
        layout.addWidget(self.text)
        layout.addWidget(self.table)

        self.player = AudioPlayer()
        self.player.hide()
        layout.addWidget(self.player, alignment=Qt.AlignHCenter)

        self.setLayout(layout)

    def model(self):
        return self.table.model()

    def setModel(self,model):
        self.text.setModel(model)
        self.table.setModel(model)
        #self.table.setSelectionModel(self.text.selectionModel())
        #self.table.selectionModel().selectionChanged.connect(self.updatePlayerTimes)

        if not hasattr(model, 'has_audio') or not model.hasAudio():
            self.player.hide()

        elif AUDIO_ENABLED and model.hasAudio():
            self.player.setAudioFile(model.audioPath())
            self.player.show()

        try:
            self.table.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        except AttributeError:
            self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

    def search(self):
        text = self.searchField.text()
        if not text:
            return
        curview = self.table
        model = curview.model()
        curSelection = curview.selectionModel().selectedRows()
        if curSelection:
            row = curSelection[-1].row() + 1
        else:
            row = 0
        start = model.index(row,0)
        matches = model.match(start, Qt.DisplayRole, text, 1, Qt.MatchContains)
        if matches:
            index = matches[0]
            curview.selectionModel().select(index,
                    QItemSelectionModel.SelectCurrent|QItemSelectionModel.Rows)
            curview.scrollTo(index,QAbstractItemView.PositionAtCenter)
        else:
            start = model.index(0,0)
            matches = model.match(start, Qt.DisplayRole, text, 1, Qt.MatchContains)
            if matches:
                index = matches[0]
                curview.selectionModel().select(index,
                    QItemSelectionModel.SelectCurrent|QItemSelectionModel.Rows)
                curview.scrollTo(index,QAbstractItemView.PositionAtCenter)
            else:
                curview.selectionModel().clear()

    def findType(self, index):
        curview = self.table
        wordtype = curview.model().wordTokenObject(index.row()).wordtype
        self.selectType.emit(wordtype)

    def changeView(self):
        if self.text.isHidden():
            self.text.show()
            self.table.hide()
        else:
            self.text.hide()
            self.table.show()

    def showMenu(self, pos):
        menu = QMenu()
        curview = self.table if self.text.isHidden() else self.text
        index = curview.indexAt(pos)
        changeViewAction = QAction(self)
        if self.text.isHidden():
           changeViewAction.setText('Show as text')
        else:
           changeViewAction.setText('Show as table')
        changeViewAction.triggered.connect(self.changeView)
        menu.addAction(changeViewAction)
        if index.isValid():
            lookupAction = QAction(self)
            lookupAction.setText('Look up word')
            lookupAction.triggered.connect(lambda: self.findType(curview.indexAt(pos)))
            menu.addAction(lookupAction)
        action = menu.exec_(curview.viewport().mapToGlobal(pos))

    def updatePlayerTimes(self):
        curview = self.table
        rows = [x.row() for x in curview.selectionModel().selectedRows()]
        if not rows:
            self.player.setLimits()
        else:
            mintime = curview.model().wordTokenObject(rows[0]).begin
            maxtime = curview.model().wordTokenObject(rows[-1]).end
            self.player.setLimits(begin = mintime, end = maxtime)

    def highlightTokens(self, tokens):
        curview = self.table
        if curview.model() is None:
            return
        curview.selectionModel().clear()
        times = [x.begin for x in tokens if x.discourse == curview.model().corpus]
        rows = curview.model().timesToRows(times)
        for r in rows:
            index = curview.model().index(r,0)
            curview.selectionModel().select(index, QItemSelectionModel.Select |QItemSelectionModel.Rows)

class SubTreeView(QTreeView):
    def __init__(self,parent=None):
        super(SubTreeView, self).__init__(parent=parent)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setExpandsOnDoubleClick(True)

class TreeWidget(SubTreeView):
    newLexicon = Signal(object)
    def __init__(self,parent=None):
        super(TreeWidget, self).__init__(parent=parent)
        # self.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.showMenu)
        self._selection_model = None
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        self._width = 40

    def sizeHint(self):
        sz = super(TreeWidget, self).sizeHint()
        sz.setWidth(self._width)
        return sz

    def setModel(self, model):
        QTreeView.setModel(self, model)
        self._selection_model = QTreeView.selectionModel(self)
        self.expandToDepth(1)
        self.resizeColumnToContents(0)
        self._width = self.sizeHintForColumn(0)+ 20
        self.collapseAll()

    def selectionModel(self):
        return self._selection_model

    def showMenu(self, pos):
        menu = QMenu()

        buildAction = QAction(self)
        buildAction.setText('Build lexicon')
        buildAction.triggered.connect(lambda: self.buildNewLexicon(self.indexAt(pos)))
        menu.addAction(buildAction)
        #combineAction = QAction(self)
        #combineAction.setText('Combine sub dialogs')
        #menu.addAction(combineAction)
        action = menu.exec_(self.viewport().mapToGlobal(pos))

    def buildNewLexicon(self, index):
        lexicon = self.model().createLexicon(index)
        self.newLexicon.emit(lexicon)

class MutualInfoVowelHarmonyWindow(QDialog):

    def __init__(self, title, dialog, parent):
        self._parent = parent
        QDialog.__init__(self)
        self.dialog = dialog
        dataModel = ResultsModel(self.dialog.header, self.dialog.results, self._parent.settings)
        layout = QVBoxLayout()
        self.table = TableWidget()
        self.table.setModel(dataModel)
        try:
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        except AttributeError:
            self.table.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
            self.table.horizontalHeader().setResizeMode(0,QHeaderView.Stretch)
        layout.addWidget(self.table)
        self.table.resizeColumnsToContents()
        self.setWindowTitle(title)
        self.table.adjustSize()
        self.setLayout(layout)

    def sizeHint(self):
        sz = QDialog.sizeHint(self)
        minWidth = self.table.calcWidth()+41
        if sz.width() < minWidth:

            sz.setWidth(minWidth)
        if sz.height() < 400:
            sz.setHeight(400)
        return sz

class ResultsWindow(QDialog):
    def __init__(self, title, dialog, parent):
        self._parent = parent
        QDialog.__init__(self)
        self.dialog = dialog
        dataModel = ResultsModel(self.dialog.header, self.dialog.results, self._parent.settings)
        layout = QVBoxLayout()
        self.table = TableWidget()
        self.table.setModel(dataModel)
        try:
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        except AttributeError:
            self.table.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.table)
        self.aclayout = QHBoxLayout()
        self.redoButton = QPushButton('Reopen function dialog')
        self.redoButton.clicked.connect(self.redo)
        self.saveButton = QPushButton('Save to file')

        self.saveButton.clicked.connect(self.save)
        self.closeButton = QPushButton('Close window')

        self.closeButton.clicked.connect(self.reject)
        self.aclayout.addWidget(self.redoButton)
        self.aclayout.addWidget(self.saveButton)
        self.aclayout.addWidget(self.closeButton)
        acframe = QFrame()
        acframe.setLayout(self.aclayout)
        layout.addWidget(acframe)
        self.setLayout(layout)

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.setWindowTitle(title)
        dialogWidth = self.table.horizontalHeader().length() + 50
        dialogHeight = self.table.verticalHeader().length() + 50
        self.resize(dialogWidth, dialogHeight)


    def sizeHint(self):
        sz = QDialog.sizeHint(self)
        minWidth = self.table.calcWidth()+41
        if sz.width() < minWidth:

            sz.setWidth(minWidth)
        if sz.height() < 400:
            sz.setHeight(400)
        return sz

    def redo(self):
        # called when 'Reopen function dialog' in analyses (except for phonological search)
        if self.dialog.exec_():
            if self.dialog.update:
                duplicated = self.duplicate_check()
                if not duplicated[0]:
                    new_result = list()
                    duplicated_result = duplicated[1]
                    for d in self.dialog.results:
                        if not list(d.values()) in [list(i) for i in duplicated_result]:
                            new_result.append(d)
                    self.table.model().addRows(new_result)
                    # simply adds all results of the new search
                    # self.table.model().addRows(self.dialog.results)
            else:
                dataModel = ResultsModel(self.dialog.header,self.dialog.results, self._parent.settings)
                self.table.setModel(dataModel)
        self.raise_()
        self.activateWindow()

    def duplicate_check(self):
        """
        When in 'repoen function dialog,' checks whether an analysis is conducted twice with the same parameters.
        If so, raise an error message and discard the new search.

        Returns
        -------
         List of
            Bool
                True if duplicate
            List
                list of duplicated individual result
        """
        try:
            analysis_name = self.dialog.results[0]['Analysis name']
            warning_type = "calculations"
            headers = self.table.model().columns
            if any([isinstance(item, list) for item in self.table.model().rows[0]]):
                existing_results_set = set()
                for r in self.table.model().rows:
                    row_list = list()
                    for h in range(len(headers)):
                        row_list.append(str(r[h])) if type(r[h]) == list else row_list.append(r[h])
                    existing_results_set.add(tuple(row_list))
            else:
                existing_results_set = set(tuple(r) for r in self.table.model().rows)

        except KeyError:
            analysis_name = "Phonological search"
            warning_type = "searches"
            headers = self.table.model().header
            existing_results_set = set()
            for r in self.table.model().allData:
                existing_results_set.add(tuple(r[h] for h in headers))

        except IndexError:
            return [False, []]

        new_results_set = set()
        for r in self.dialog.results:
            if any([isinstance(item, list) for item in r.values()]):
                row_list = list()
                for h in headers:
                    row_list.append(str(r[h])) if type(r[h]) == list else row_list.append(r[h])
                new_results_set.add(tuple(row_list))
            else:
                new_results_set.add(tuple([r[h] for h in headers]))

        if new_results_set.issubset(existing_results_set):
            msgBox = QMessageBox(QMessageBox.Critical, "Duplicate {}".format(warning_type),
                                 "It seems that you repeated one of the previous {type}.\n"
                                 "{analysis} with identical parameters does not produce new results."
                                 "Therefore, no new information will be added for these {type} this time.\n"
                                 "Click OK to go back to the previous results window.".format(type=warning_type,
                                                                                              analysis=analysis_name),
                                 QMessageBox.NoButton, self)
            msgBox.addButton("OK", QMessageBox.AcceptRole)
            msgBox.exec_()
            return [True, None]
        else:
            dup_individual_result = list(new_results_set.intersection(existing_results_set))
            return [False, dup_individual_result]

    def save(self):
        filename = QFileDialog.getSaveFileName(self,'Choose save file',
                        filter = 'Text files (*.txt *.csv)')

        if filename and filename[0]:
            with open(filename[0], mode='w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerow(self.table.model().columns)
                for row in self.table.model().rows:
                    writer.writerow(row)

class PhonoSearchResults(ResultsWindow):
    def __init__(self, title, dialog, parent):
        ResultsWindow.__init__(self, title, dialog, parent)
        dataModel = PhonoSearchResultsModel(self.dialog.header,
                        self.dialog.summary_header,
                        self.dialog.results, self._parent.settings)
        dataModel.setSummarized(True, self.dialog.segsum.isChecked())
        self.table.setModel(dataModel)

        self.summarized = True
        self.summaryButton = QPushButton('Show summary results')
        self.summaryButton.clicked.connect(self.summaryDetail)
        self.individualButton = QPushButton('Show individual results')
        self.individualButton.clicked.connect(self.summaryDetail)
        self.aclayout.insertWidget(0, self.individualButton)

    def summaryDetail(self):
        # Toggle between summaryButton and individualButton.
        # Previously QPushButton.setText() was used to update the text of the button,
        # but due to MacOS-dependent issue, QPushButton.setText() doesn't update. Instead two buttons with the identical
        # label switch.
        if self.summarized:
            # summarized result -> total result
            self.table.model().setSummarized(False, self.dialog.segsum.isChecked())  # update table contents
            self.individualButton.hide()
            self.aclayout.insertWidget(0, self.summaryButton)
            self.summaryButton.show()
        else:
            # total result -> summarized result
            self.table.model().setSummarized(True, self.dialog.segsum.isChecked())  # update table contents
            self.summaryButton.hide()
            self.aclayout.insertWidget(0, self.individualButton)
            self.individualButton.show()
        self.summarized = not self.summarized

    def redo(self):
        # called when 'Reopen function dialog' selected in phono search result window
        if self.dialog.exec_():
            if self.dialog.update:  # when 'Calculate [...] (add to current results table)' selected
                if len(self.dialog.results) > 0:
                    if not self.duplicate_check()[0]:
                        self.table.model().addRows(rows=self.dialog.results, segsum=self.dialog.segsum.isChecked())
                        self.summarized = False
                        self.table.model().setSummarized(True, self.dialog.segsum.isChecked())
            else:                   # when 'Calculate [...] (start new results table)' selected
                dataModel = PhonoSearchResultsModel(self.dialog.header,
                                                    self.dialog.summary_header,
                                                    self.dialog.results,
                                                    self._parent.settings)
                self.table.setModel(dataModel)
                self.summarized = False
                segsum = self.dialog.segsum.isChecked()
                self.table.model().setSummarized(True, segsum)
        self.raise_()
        self.activateWindow()

class UncategorizedView(QTableView):

    def __init__(self, inventory):
        super().__init__()
        self.setModel(inventory)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.doubleClicked.connect(self.showFeatures)

    def showFeatures(self, index):
        try:
            seg = self.model().data(index, role=Qt.DisplayRole)
        except IndexError:
            return

        if not seg:
            return #emtpy cells in an UncategorizedModel have empty strings

        alert = QMessageBox()
        windowTitle, text = self.model().getPartialCategorization(seg)
        alert.setWindowTitle(windowTitle)
        alert.setText(text)
        alert.addButton('Return', QMessageBox.AcceptRole)
        alert.exec_()
        return

class InventoryView(QTableView):

    dropSuccessful = Signal(str)
    columnSpecsChanged = Signal(int, list, str, bool)
    rowSpecsChanged = Signal(int, list, str, bool)

    def __init__(self, inventory):
        super().__init__()
        self.setModel(inventory)
        self.columnSpecsChanged.connect(self.model().sourceModel().changeColumnSpecs)
        self.rowSpecsChanged.connect(self.model().sourceModel().changeRowSpecs)
        self.horizontalHeader().sectionMoved.connect(self.moveColumn)
        self.verticalHeader().sectionMoved.connect(self.moveRow)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

        self.horizontalHeader().setSectionsClickable(True)
        self.horizontalHeader().sectionDoubleClicked.connect(self.editChartCol)
        self.horizontalHeader().setSectionsMovable(True)
        self.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.horizontalHeader().customContextMenuRequested.connect(self.showColumnMenu)
        #self.horizontalHeader().setStretchLastSection(True)

        self.verticalHeader().setSectionsClickable(True)
        self.verticalHeader().sectionDoubleClicked.connect(self.editChartRow)
        self.verticalHeader().setSectionsMovable(True)
        self.verticalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.verticalHeader().customContextMenuRequested.connect(self.showRowMenu)
        #self.verticalHeader().setStretchLastSection(True)

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)


    def showRowMenu(self, pos):
        menu = QMenu()
        addRowAction = menu.addAction('Insert Row')
        removeRowAction = menu.addAction('Remove Row')
        editAction = menu.addAction('Edit Row Properties')
        index = self.indexAt(pos)
        action = menu.exec_(self.mapToGlobal(pos))
        if action == addRowAction:
            self.model().insertRow(index)
        elif action == removeRowAction:
            self.model().removeRow(index)
        elif action == editAction:
            self.editChartRow(index.row())

    def showColumnMenu(self, pos):
        menu = QMenu()
        addColumnAction = menu.addAction('Insert Column')
        removeColumnAction = menu.addAction('Remove Column')
        editAction = menu.addAction('Edit Column Properties')
        index = self.indexAt(pos)
        action = menu.exec_(self.mapToGlobal(pos))
        if action == addColumnAction:
            self.model().insertColumn(index)
        elif action == removeColumnAction:
            self.model().removeColumn(index)
        elif action == editAction:
            self.editChartCol(index.column())

    def moveColumn(self):
        map = {}
        consonants = True if isinstance(self.model(), ConsonantModel) else False
        offset = 0 if consonants else self.model().sourceModel().vowel_column_offset
        for j in range(self.horizontalHeader().length()):
            visualIndex = self.horizontalHeader().visualIndex(j)
            logicalIndex = self.horizontalHeader().logicalIndex(visualIndex)
            if logicalIndex == -1:
                continue
            map[logicalIndex] = (visualIndex, self.model().sourceModel().headerData(logicalIndex+offset, Qt.Horizontal, Qt.DisplayRole))
        self.model().sourceModel().changeColumnOrder(map, consonants=consonants)

    def moveRow(self):
        map = {}
        consonants = True if isinstance(self.model(), ConsonantModel) else False
        offset = 0 if consonants else self.model().sourceModel().vowel_row_offset
        for j in range(self.verticalHeader().length()):
            visualIndex = self.verticalHeader().visualIndex(j)
            logicalIndex = self.verticalHeader().logicalIndex(visualIndex)
            if logicalIndex == -1:
                continue
            map[logicalIndex] = (visualIndex, self.model().sourceModel().headerData(logicalIndex+offset, Qt.Vertical, Qt.DisplayRole))
        self.model().sourceModel().changeRowOrder(map, consonants=consonants)

    def editChartRow(self, index):
        if isinstance(self.model(), ConsonantModel):
            consonants=True
        elif isinstance(self.model(), VowelModel):
            consonants=False
        dialog = PCTWidgets.EditInventoryWindow(self.model(), index, Qt.Horizontal, consonants=consonants)
        results = dialog.exec_()
        if results:
            self.rowSpecsChanged.emit(index, dialog.features, dialog.section_name, consonants)

    def editChartCol(self, index):
        if isinstance(self.model(), ConsonantModel):
            consonants=True
        elif isinstance(self.model(), VowelModel):
            consonants=False
        dialog = PCTWidgets.EditInventoryWindow(self.model(), index, Qt.Vertical, consonants=consonants)
        results = dialog.exec_()
        if results:
            self.columnSpecsChanged.emit(index, dialog.features, dialog.section_name, consonants)
