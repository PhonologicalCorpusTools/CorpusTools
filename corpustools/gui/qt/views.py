
import csv

from PyQt5.QtWidgets import (QTableView, QAbstractItemView, QWidget,
                            QHeaderView, QDockWidget, QPushButton,
                            QVBoxLayout, QFileDialog, QFrame, QTreeView,
                            QAbstractItemView, QStyle, QMenu, QAction, QDialog)

from PyQt5.QtCore import QRectF, Qt, QModelIndex, QItemSelection
from PyQt5.QtGui import QPainter, QFontMetrics, QPen, QRegion

from .models import VariantModel

class TableWidget(QTableView):
    def __init__(self,parent=None):
        super(TableWidget, self).__init__(parent=parent)

        self.verticalHeader().hide()

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        #self.setContextMenuPolicy(Qt.CustomContextMenu)
        #self.customContextMenuRequested.connect(self.popup)
        #header = self.horizontalHeader()
        #header.setContextMenuPolicy(Qt.CustomContextMenu)
        #header.customContextMenuRequested.connect( self.showHeaderMenu )
        #self.horizontalHeader().setMinimumSectionSize(100)
        #self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setSortingEnabled(True)

    def setModel(self,model):
        super(TableWidget, self).setModel(model)
        #self.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    #def minimumSizeHint(self):
        #header = self.horizontalHeader()
        #fm = QFontMetrics(self.font())
        #width = 0
        #for x in x:

            #width += fm.width(text)
            #width += 10
        #width = header.length()
        #sh = header.sizeHint()
        #sh.setWidth(width-100)
        #return sh

class LexiconView(TableWidget):
    def __init__(self,parent=None):
        super(LexiconView, self).__init__(parent=parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)

    def showMenu(self, pos):
        menu = QMenu()

        variantsAction = QAction(self)
        variantsAction.setText('Show neighbours')
        menu.addAction(variantsAction)
        variantsAction = QAction(self)
        variantsAction.setText('Show pronunciation variants')
        variantsAction.triggered.connect(lambda: self.showVariants(self.indexAt(pos)))
        menu.addAction(variantsAction)
        action = menu.exec_(self.viewport().mapToGlobal(pos))

    def showVariants(self, index):
        variantDialog = QDialog()
        layout = QVBoxLayout()
        table = TableWidget()
        layout.addWidget(table)
        table.setModel(VariantModel(self.model().wordObject(index.row()).wordtokens))
        variantDialog.setLayout(layout)
        variantDialog.exec_()


class TextView(QAbstractItemView):
    ExtraHeight = 3
    ExtraWidth = 10
    def __init__(self, parent=None):
        QAbstractItemView.__init__(self, parent)

        self.hashIsDirty = False
        self.hasAudio = False
        self.rectForRow = dict()

        self.horizontalScrollBar().setRange(0,0)
        self.verticalScrollBar().setRange(0,0)
        self.idealHeight = 0
        self.idealWidth = 0
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)

    def showMenu(self, pos):
        menu = QMenu()
        index = self.indexAt(pos)
        if not index.isValid():
            return
        lookupAction = QAction(self)
        lookupAction.setText('Look up word')
        menu.addAction(lookupAction)
        if self.hasAudio:
            playAudioAction = QAction(self)
            playAudioAction.setText('Play audio')
            menu.addAction(playAudioAction)
        action = menu.exec_(self.viewport().mapToGlobal(pos))


    def setModel(self,model):
        QAbstractItemView.setModel(self, model)
        self.hashIsDirty = True

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
            text = self.model().data(index)
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
            index = model().index(index.row() + offset, index.column(), index.parent())
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

    def resizeEvent(self, event):
        self.hashIsDirty = True
        self.calculateRectsIfNecessary()
        self.updateGeometries()

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

class TreeWidget(QTreeView):
    def __init__(self,parent=None):
        super(TreeWidget, self).__init__(parent=parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)
        self.setColumnWidth(0,40)

    def edit(self, index, trigger, event):
        if trigger == QAbstractItemView.DoubleClicked:
            return False
        return QTreeView.edit(self, index, trigger, event)

    def showMenu(self, pos):
        menu = QMenu()

        buildAction = QAction(self)
        buildAction.setText('Build lexicon')
        menu.addAction(buildAction)
        combineAction = QAction(self)
        combineAction.setText('Combine sub dialogs')
        #saveRepAction.triggered.connect(lambda: self.saveRep(self.indexAt(pos)))
        menu.addAction(combineAction)
        action = menu.exec_(self.viewport().mapToGlobal(pos))

class ResultsWindow(QWidget):
    def __init__(self, title, dataModel, parent=None):
        QWidget.__init__(self)#, parent)

        layout = QVBoxLayout()
        self.table = TableWidget()
        self.table.setModel(dataModel)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.table)

        self.saveButton = QPushButton('Save to file')
        self.saveButton.clicked.connect(self.save)
        layout.addWidget(self.saveButton)
        #frame = QFrame()
        self.setLayout(layout)
        #self.setWidget(frame)
        self.table.resizeColumnsToContents()
        #self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setWindowTitle(title)
        self.table.adjustSize()
        self.resize(self.sizeHint())

    def sizeHint(self):
        sh = self.table.sizeHint()
        return sh

    def save(self):
        filename = QFileDialog.getSaveFileName(self,'Choose save file',
                        filter = 'Text files (*.txt *.csv)')
        if filename:

            with open(filename[0], mode='w', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerow(self.table.model().columns)
                for row in self.table.model().data:
                    writer.writerow(row)
