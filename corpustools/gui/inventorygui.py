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

        font = QFont('Arial', 10)
        font.setBold(True)
        layout = QVBoxLayout()

        inventoryLayout = QHBoxLayout()
        consBox = QVBoxLayout()
        cons_title = QLabel('Consonant Inventory')
        cons_title.setFont(font)
        consBox.addWidget(cons_title)
        self.consModel = ConsonantModel(self.inventory)
        self.consView = InventoryView(self.consModel)
        self.consView.resizeRowsToContents()
        self.consView.resizeColumnsToContents()
        consBox.addWidget(self.consView)
        inventoryLayout.addLayout(consBox)

        vowelBox = QVBoxLayout()
        vowel_title = QLabel('Vowel Inventory')
        vowel_title.setFont(font)
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
        unc_title.setFont(font)
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
        if self.inventory.cons_features is None or self.inventory.cons_features[0] is not None:
            self.editCons.setText(','.join(self.inventory.cons_features))
        editConsLayout.addWidget(self.editCons)
        editCategoriesLayout.addLayout(editConsLayout)

        editVowelsLayout = QVBoxLayout()
        editVowelsLayout.addWidget(QLabel('Default vowel features (separate with commas)'))
        self.editVowels = FeatureEdit(self.inventory)
        vowelCompleter = FeatureCompleter(self.inventory)
        self.editVowels.setCompleter(vowelCompleter)
        if self.inventory.vowel_features is None or self.inventory.vowel_features[0] is not None:
            self.editVowels.setText(','.join(self.inventory.vowel_features))
        editVowelsLayout.addWidget(self.editVowels)
        editCategoriesLayout.addLayout(editVowelsLayout)

        topmessage = QLabel(text=(  'Double-click on a row or column to edit the '
                                    'class of segments which appear in that row or column.\n'
                                    'Right click to insert a new empty row or column.\n'
                                    'Select a heading and drag-and-drop to reorganize the table.\n'
        ))

        topmessage.setWordWrap(True)
        font.setBold(False)
        topmessage.setFont(font)
        layout.addWidget(topmessage)

        resetButton = QPushButton()
        editCategoriesLayout.addWidget(resetButton)
        resetButton.setText('Reset features')
        resetButton.clicked.connect(self.reset)
        inventoryLayout.addLayout(editCategoriesLayout)

        layout.addSpacing(15)

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
        self.reset(exiting=True)
        QDialog.accept(self)

    def reject(self):
        QDialog.reject(self)

    def reset(self, exiting=False):
        cons_features = [item.strip() for item in self.editCons.text().split(',')] if self.editCons.text() else None
        vowel_features = [item.strip() for item in self.editVowels.text().split(',')] if self.editVowels.text() else None
        if (cons_features is None or vowel_features is None) and not exiting:
            alert = QMessageBox()
            alert.setText('One of the categories is missing a default feature. Please fill in both.')
            alert.setWindowTitle('Missing feature value')
            alert.exec_()
            return
        round_features = None #not yet implemented
        diph_features = None #yet implemented
        ClassFeatures = namedtuple('ClassFeatures', ['cons_features','vowel_features','round_feature', 'diph_feature'])
        class_features = ClassFeatures(cons_features, vowel_features, round_features, diph_features)
        self.inventory.set_major_class_features(class_features)
        self.inventory.modelReset()