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
        self.consModel = ConsonantModel(self.inventory)
        self.consView = InventoryView(self.consModel)
        consBox.addWidget(self.consView)
        layout.addLayout(consBox)

        vowelBox = QVBoxLayout()
        vowel_title = QLabel('Vowel Inventory')
        vowelBox.addWidget(vowel_title)
        self.vowelModel = VowelModel(self.inventory)
        self.vowelView = InventoryView(self.vowelModel)
        vowelBox.addWidget(self.vowelView)
        layout.addLayout(vowelBox)

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