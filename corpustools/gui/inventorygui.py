from .imports import *
from .views import InventoryView
from .models import ConsonantModel, VowelModel, UncategorizedModel
from .widgets import FeatureEdit, FeatureCompleter
from collections import namedtuple


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
                                    'class of segments which appear in that row or column.\n'))
        topmessage.setWordWrap(True)
        layout.addWidget(topmessage)


        inventoryLayout = QVBoxLayout()
        consBox = QVBoxLayout()
        cons_title = QLabel('Consonant Inventory')
        consBox.addWidget(cons_title)
        self.consModel = ConsonantModel(self.inventory)
        self.consView = InventoryView(self.consModel)
        self.consView.resizeColumnsToContents()
        self.consView.resizeRowsToContents()
        consBox.addWidget(self.consView)
        inventoryLayout.addLayout(consBox)

        vowelBox = QVBoxLayout()
        vowel_title = QLabel('Vowel Inventory')
        vowelBox.addWidget(vowel_title)
        self.vowelModel = VowelModel(self.inventory)
        self.vowelView = InventoryView(self.vowelModel)
        vowelBox.addWidget(self.vowelView)
        self.vowelView.resizeRowsToContents()
        self.vowelView.resizeColumnsToContents()
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

        editCategoriesLayout = QVBoxLayout()

        editConsLayout = QVBoxLayout()
        editConsLayout.addWidget(QLabel('Default consonant features (separate with commas)'))
        self.editCons = FeatureEdit(self.inventory)
        consCompleter = FeatureCompleter(self.inventory)
        self.editCons.setCompleter(consCompleter)
        if self.inventory.cons_features is not None:
            self.editCons.setText(','.join(self.inventory.cons_features))
        editConsLayout.addWidget(self.editCons)
        editCategoriesLayout.addLayout(editConsLayout)

        editVowelsLayout = QVBoxLayout()
        editVowelsLayout.addWidget(QLabel('Default vowel features (separate with commas)'))
        self.editVowels = FeatureEdit(self.inventory)
        vowelCompleter = FeatureCompleter(self.inventory)
        self.editVowels.setCompleter(vowelCompleter)
        if self.inventory.vowel_features is not None:
            self.editVowels.setText(','.join(self.inventory.vowel_features))
        editVowelsLayout.addWidget(self.editVowels)
        editCategoriesLayout.addLayout(editVowelsLayout)

        resetButton = QPushButton()
        editCategoriesLayout.addWidget(resetButton)
        resetButton.setText('Reset features')
        resetButton.clicked.connect(self.reset)
        layout.addLayout(editCategoriesLayout)

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
        self.reset()
        QDialog.accept(self)

    def reject(self):
        QDialog.reject(self)

    def reset(self):
        cons_features = [item.strip() for item in self.editCons.text().split(',')] if self.editCons.text() else None
        vowel_features = [item.strip() for item in self.editVowels.text().split(',')] if self.editVowels.text() else None
        if cons_features is None and vowel_features is None:
            return
        round_features = None #not yet implemented
        diph_features = None #yet implemented
        ClassFeatures = namedtuple('ClassFeatures', ['cons_features','vowel_features','round_feature', 'diph_feature'])
        class_features = ClassFeatures(cons_features, vowel_features, round_features, diph_features)
        self.inventory.set_major_class_features(class_features)
        self.inventory.modelReset()