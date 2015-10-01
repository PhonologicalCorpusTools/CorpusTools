from .imports import *
from .views import InventoryView
from .models import ConsonantModel, VowelModel, InventoryDelegate


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
        self.consDelegate = InventoryDelegate()
        self.consView = InventoryView(self.consModel, self.consDelegate)
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
            segButton = QPushButton(text=seg.symbol)
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
        #print(self.inventory.cons_columns)
        print([self.consModel.match(,Qt.DisplayRole, 'Velar')])
        #print([self.consView.i for j in range(self.consModel.columnCount(self.consModel))])
        # for j in range(self.consModel.columnCount()):
        #     if self.consView.horizontalHeader().data(j) == self.consModel:
        #         print('MO')
        QDialog.accept(self)