from .imports import *
from .views import InventoryView
from .models import ConsonantModel, VowelModel, UncategorizedModel


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

        consBox = QVBoxLayout()
        cons_title = QLabel('Consonant Inventory')
        consBox.addWidget(cons_title)
        self.consModel = ConsonantModel(inventory)
        self.consView = InventoryView(self.consModel)
        consBox.addWidget(self.consView)
        layout.addLayout(consBox)

        vowelBox = QVBoxLayout()
        vowel_title = QLabel('Vowel Inventory')
        vowelBox.addWidget(vowel_title)
        self.vowelModel = VowelModel(inventory)
        self.vowelView = InventoryView(self.vowelModel)
        vowelBox.addWidget(self.vowelView)
        layout.addLayout(vowelBox)

        uncBox = QVBoxLayout()
        unc_title = QLabel('Uncategorized Segments')
        uncBox.addWidget(unc_title)
        self.uncModel = UncategorizedModel(inventory)
        self.uncView = InventoryView(self.uncModel)
        self.uncView.horizontalHeader().hide()
        self.uncView.verticalHeader().hide()
        uncBox.addWidget(self.uncView)
        layout.addLayout(uncBox)

        # self.uncategorizedBox = QHBoxLayout()
        # self.uncategorizedBox.setAlignment(Qt.AlignLeft)
        # self.uncategorizedBox.setContentsMargins(0, 0, 0, 0)
        # self.uncategorizedBox.setSpacing(0)
        # for seg in inventory.uncategorized:
        #     segButton = DraggableSegmentButton(seg.symbol)
        #     segButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        #     self.uncategorizedBox.addWidget(segButton)
        # layout.addLayout(self.uncategorizedBox)

        buttonLayout = QHBoxLayout()
        ok_button = QPushButton('OK')
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)
        buttonLayout.addWidget(ok_button)
        buttonLayout.addWidget(cancel_button)

        layout.addLayout(buttonLayout)

        self.setLayout(layout)

    def checkForColumnRowChanges(self):
        map = {} #update any changes to Consonant Columns
        for j in range(self.consModel.columnCount()):
            visualIndex = self.consView.horizontalHeader().visualIndex(j)
            logicalIndex = self.consView.horizontalHeader().logicalIndex(visualIndex)
            map[logicalIndex] = (visualIndex, self.consModel.headerData(logicalIndex, Qt.Horizontal, Qt.DisplayRole))
        self.inventory.changeColumnOrder(map, consonants=True)

        map = {} #update any changes to Consonant Rows
        for j in range(self.consModel.rowCount()):
            visualIndex = self.consView.verticalHeader().visualIndex(j)
            logicalIndex = self.consView.verticalHeader().logicalIndex(visualIndex)
            map[logicalIndex] = (visualIndex, self.consModel.headerData(logicalIndex, Qt.Vertical, Qt.DisplayRole))
        self.inventory.changeRowOrder(map, consonants=True)

        map = {} #update any changes to Vowel Columns
        for j in range(self.vowelModel.columnCount()):
            visualIndex = self.vowelView.horizontalHeader().visualIndex(j)
            logicalIndex = self.vowelView.horizontalHeader().logicalIndex(visualIndex)
            map[logicalIndex] = (visualIndex, self.vowelModel.headerData(logicalIndex, Qt.Horizontal, Qt.DisplayRole))
        self.inventory.changeColumnOrder(map, consonants=False)

        map = {} #update any changes to Vowel Rows
        for j in range(self.vowelModel.rowCount()):
            visualIndex = self.vowelView.verticalHeader().visualIndex(j)
            logicalIndex = self.vowelView.verticalHeader().logicalIndex(visualIndex)
            map[logicalIndex] = (visualIndex, self.vowelModel.headerData(logicalIndex, Qt.Vertical, Qt.DisplayRole))
        self.inventory.changeRowOrder(map, consonants=False)

    def accept(self):

        self.checkForColumnRowChanges()
        self.inventory.sortData()
        QDialog.accept(self)

    def reject(self):
        QDialog.reject(self)