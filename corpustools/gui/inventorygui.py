from .imports import *
from .views import InventoryView
from .models import ConsonantModel, VowelModel, InventoryDelegate
from .widgets import DraggableSegmentButton


class InventoryManager(QDialog):
    def __init__(self, inventory):
        super().__init__()
        self.inventory = inventory

        layout = QVBoxLayout()
        topmessage = QLabel(text=('You can edit your inventory chart from this window. Double-click on a row or column to edit the '
                      'class of segments which appear in that row or column. You can also single click on a heading to '
                      'highlight the row or column, then drag-and-drop to reorganize the table.'))
        topmessage.setWordWrap(True)
        layout.addWidget(topmessage)

        self.consModel = ConsonantModel(inventory)
        self.consView = InventoryView(self.consModel)
        self.consView.dropSuccessful.connect(self.monitorDrop)
        layout.addWidget(self.consView)

        # self.vowelModel = VowelModel(inventory)
        # self.vowelView = InventoryView(self.vowelModel)
        # layout.addWidget(self.vowelView)

        uncTitle = QLabel(text='Uncategorized elements of the inventory')
        layout.addWidget(uncTitle)

        self.uncategorizedBox = QHBoxLayout()
        self.uncategorizedBox.setAlignment(Qt.AlignLeft)
        self.uncategorizedBox.setContentsMargins(0, 0, 0, 0)
        self.uncategorizedBox.setSpacing(0)
        for seg in inventory.uncategorized:
            segButton = DraggableSegmentButton(seg.symbol)
            segButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.uncategorizedBox.addWidget(segButton)
        layout.addLayout(self.uncategorizedBox)

        buttonLayout = QHBoxLayout()
        ok_button = QPushButton('OK')
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)
        buttonLayout.addWidget(ok_button)
        buttonLayout.addWidget(cancel_button)

        layout.addLayout(buttonLayout)

        self.setLayout(layout)

    def monitorDrop(self, drop_label):
        for j in range(self.uncategorizedBox.count()):
            widget = self.uncategorizedBox.itemAt(j).widget()
            print(widget.text())
            if widget.text() == drop_label:
                del widget
                break

    def addToTable(self):
        print('adding')

    def removeFromTable(self):
        print('removing')

    def reorderTable(self):
        print('reordering')

    def getHeaderText(self):
        cons_col_headers = list()
        for index in range(1,4):#range(self.consBox.model().columnCount()):
            cons_col_headers.append(self.consView.horizontalHeader().data())
            #headerData(index,1,Qt.DisplayRole))
        print(cons_col_headers)

    def findColumnFromLabel(self, label):
        for column in range (self.consModel.columnCount()):
            if self.consModel.headerData(column, Qt.Horizontal) ==  label:
                return column

    def accept(self):
        #self.consView.commitData()
        #check if the visual and logical indices match up
        #print(self.inventory.cons_column_data)
        # print([self.consModel.match(,Qt.DisplayRole, 'Velar')])
        #print([self.consView.i for j in range(self.consModel.columnCount(self.consModel))])
        # for j in range(self.consModel.columnCount()):
        #     if self.consView.horizontalHeader().data(j) == self.consModel:
        #         print('MO')
        map = {}
        for j in range(self.consModel.columnCount()):
            visualIndex = self.consView.horizontalHeader().visualIndex(j)
            logicalIndex = self.consView.horizontalHeader().logicalIndex(visualIndex)
            map[logicalIndex] = (visualIndex, self.consModel.headerData(logicalIndex, Qt.Horizontal, Qt.DisplayRole))
        # print('j : {}, Logical Id: {}, Visual Id: {}, HeaderData: {}'.format(
        #         j, logicalIndex,visualIndex, self.consModel.headerData(j,Qt.Horizontal,Qt.DisplayRole)))
        print(map)
        self.inventory.changeColumnOrder(map, consonants=True)
        QDialog.accept(self)

    def reject(self):
        QDialog.reject(self)