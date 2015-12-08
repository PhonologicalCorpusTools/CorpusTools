from .imports import *
from .views import InventoryView
from .models import ConsonantModel, VowelModel, UncategorizedModel


class InventoryManager(QDialog):
    def __init__(self, inventory):
        super().__init__()
        self.setWindowTitle('Manage inventory')
        self.inventory = inventory

        layout = QVBoxLayout()
        topmessage = QLabel(text=('You can edit your inventory chart from this window.\n'
                                  'Click on a heading to highlight the row or column, then drag-and-drop to reorganize '
                                    'the table.\n'
                                    'Right click to insert a new empty row or column.\n'
                                    'Double-click on a row or column to edit the '
                                    'class of segments which appear in that row or column.\n'
                                  'To change what counts as a consonant or vowel, go the menu option Features > '
                                  'Edit/View Feature System... and then click on \"Edit Inventory Categories\".'

        ))
        topmessage.setWordWrap(True)
        layout.addWidget(topmessage)

        inventoryLayout = QHBoxLayout()

        consBox = QVBoxLayout()
        cons_title = QLabel('Consonant Inventory')
        consBox.addWidget(cons_title)
        self.consModel = ConsonantModel(self.inventory)
        self.consView = InventoryView(self.consModel)
        consBox.addWidget(self.consView)
        inventoryLayout.addLayout(consBox)

        vowelBox = QVBoxLayout()
        vowel_title = QLabel('Vowel Inventory')
        vowelBox.addWidget(vowel_title)
        self.vowelModel = VowelModel(self.inventory)
        self.vowelView = InventoryView(self.vowelModel)
        vowelBox.addWidget(self.vowelView)
        inventoryLayout.addLayout(vowelBox)

        layout.addLayout(inventoryLayout)

        uncBox = QVBoxLayout()
        unc_title = QLabel('Uncategorized Segments')
        uncBox.addWidget(unc_title)
        self.uncModel = UncategorizedModel(self.inventory)
        self.uncView = InventoryView(self.uncModel)
        self.uncView.horizontalHeader().hide()
        self.uncView.verticalHeader().hide()
        uncBox.addWidget(self.uncView)
        layout.addLayout(uncBox)

        buttonLayout = QHBoxLayout()
        ok_button = QPushButton('OK')
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)
        buttonLayout.addWidget(ok_button)
        buttonLayout.addWidget(cancel_button)

        layout.addLayout(buttonLayout)

        self.setLayout(layout)

    def accept(self):
        QDialog.accept(self)

    def reject(self):
        QDialog.reject(self)