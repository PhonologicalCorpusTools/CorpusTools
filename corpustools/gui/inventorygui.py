from .imports import *
from .views import InventoryView, UncategorizedView
from .models import ConsonantModel, VowelModel, UncategorizedModel
from .widgets import FeatureEdit, FeatureCompleter
from collections import namedtuple


class InventoryManager(QDialog):
    def __init__(self, inventory):
        super().__init__()
        self.setWindowTitle('Manage inventory')
        self.inventory = inventory

        font = QFont('Arial', 12)
        font.setBold(True)
        layout = QVBoxLayout()

        inventoryLayout = QHBoxLayout()
        inventoryTabs = QTabWidget()
        inventoryLayout.addWidget(inventoryTabs)

        self.consModel = ConsonantModel(self.inventory)
        self.consView = InventoryView(self.consModel)
        self.consView.resizeRowsToContents()
        self.consView.resizeColumnsToContents()
        inventoryTabs.addTab(self.consView, 'Consonants')

        self.vowelModel = VowelModel(self.inventory)
        self.vowelView = InventoryView(self.vowelModel)

        self.vowelView.resizeRowsToContents()
        self.vowelView.resizeColumnsToContents()
        inventoryTabs.addTab(self.vowelView, 'Vowels')

        self.uncModel = UncategorizedModel(self.inventory)
        self.uncView = UncategorizedView(self.uncModel)
        inventoryTabs.addTab(self.uncView, 'Uncategorized segments')

        self.inventory.modelResetSignal.connect(self.uncModel.modelReset)

        layout.addLayout(inventoryLayout)

        editCategoriesLayout = QVBoxLayout()

        editConsLayout = QVBoxLayout()
        editConsLayout.addWidget(QLabel('Default consonant features (separate with commas)'))
        self.editCons = FeatureEdit(self.inventory)
        consCompleter = FeatureCompleter(self.inventory)
        self.editCons.setCompleter(consCompleter)
        try:
            self.editCons.setText(','.join(self.inventory.cons_features))
        except TypeError:
            pass
        editConsLayout.addWidget(self.editCons)
        editCategoriesLayout.addLayout(editConsLayout)

        editVowelsLayout = QVBoxLayout()
        editVowelsLayout.addWidget(QLabel('Default vowel features (separate with commas)'))
        self.editVowels = FeatureEdit(self.inventory)
        vowelCompleter = FeatureCompleter(self.inventory)
        self.editVowels.setCompleter(vowelCompleter)
        try:
            self.editVowels.setText(','.join(self.inventory.vowel_features))
        except TypeError:
            pass
        editVowelsLayout.addWidget(self.editVowels)
        editCategoriesLayout.addLayout(editVowelsLayout)

        topmessage = QLabel(text=('Tips for using the inventory manager:\n\n'
        '* Double-click on a row or column heading to edit the class of segments which appear in that row or column.\n'
        '* Right click to insert a new empty row or column.\n'
        '* Select a heading to highlight a row or column, then drag-and-drop to reorganize the table.\n'
        '* Double-click an uncategorized segment to see partial matches and a full feature specification.\n'
        '* Default features are required, and they apply automatically to every column and row in the relevant '
            'table.\n'
        '* After changing a default feature, click "Update features" to have the change come into effect.\n'
        '* A segment only gets fully categorized into the table if it matches a row, and a column, and all of the '
            'default features.\n'
        '* Auto-categorization currently only works with SPE or Hayes feature systems.\n'
        '* If you have recently made changes to your feature system, you may need to click "Update default features" '
            'to see those changes in effect.'
        ))

        #topmessage.setWordWrap(True)
        font.setBold(False)
        topmessage.setFont(font)
        layout.addWidget(topmessage)

        recatButton = QPushButton('Update default features')
        recatButton.clicked.connect(self.recategorize)
        autoRecatButton = QPushButton('Autocategorize')
        autoRecatButton.clicked.connect(self.autoCategorize)
        blankButton = QPushButton('Remove all categories')
        blankButton.clicked.connect(self.reset)
        editCategoriesLayout.addWidget(recatButton)
        editCategoriesLayout.addWidget(autoRecatButton)
        editCategoriesLayout.addWidget(blankButton)
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
        self.recategorize(exiting=True)
        QDialog.accept(self)

    def reject(self):
        QDialog.reject(self)

    def reset(self):
        alert = QMessageBox()
        alert.setWindowTitle('Warning!')
        alert.setText(('This will remove all the categories from your inventory, and put all of the segments in the '
            '\"Uncategorized\" table.'))
        alert.setInformativeText('Are you sure you want to do this?')
        alert.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        alert.setDefaultButton(QMessageBox.Yes)
        choice = alert.exec_()
        if choice == QMessageBox.Yes:
            self.inventory.resetCategories()

    def autoCategorize(self):


        if (not set(self.inventory.minimum_features['spe']).issubset(set(self.inventory.features)) and
            not set(self.inventory.minimum_features['hayes']).issubset(set(self.inventory.features))):
            alert = QMessageBox()
            alert.setWindowTitle('Action cannot be completed')
            alert.setText(('Your inventory cannot be auto-categorized. '
                           'Currently, only SPE-style and Hayes-style feature systems '
                            'are compatible with this function. Sorry about that!'))
            alert.addButton('OK', QMessageBox.AcceptRole)
            alert.exec_()
            return

        if not self.editCons.text() or not self.editVowels.text():
            alert = QMessageBox()
            alert.setWindowTitle('Missing information')
            alert.setText(('You need to include a default consonant feature and a default vowel feature.\n'
                           'Please ensure that both values are filled in.'))
            alert.addButton('OK', QMessageBox.AcceptRole)
            alert.exec_()
            return

        if not self.inventory.cons_features[0] or not self.inventory.vowel_features[0]:
            alert = QMessageBox()
            alert.setWindowTitle('Feature error')
            alert.setText(('You have entered default features, but you did not click "Update default features". '
                           'Any time that you change the default features, you must click that button in order '
                            'for the changes to have an effect.'))
            alert.addButton('OK', QMessageBox.AcceptRole)
            alert.exec_()
            return

        self.inventory.reGenerateNames()
        self.editCons.setText(','.join(self.inventory.cons_features))
        self.editVowels.setText(','.join(self.inventory.vowel_features))

    def recategorize(self, exiting=False):
        cons_features = [item.strip() for item in self.editCons.text().split(',')] if self.editCons.text() else None
        vowel_features = [item.strip() for item in self.editVowels.text().split(',')] if self.editVowels.text() else None
        if (cons_features is None or vowel_features is None) and not exiting:
            alert = QMessageBox()
            alert.setWindowTitle('Missing feature value')
            alert.setText(('You need to include a default consonant feature and a default vowel feature.\n'
                           'Please ensure that both values are filled in.'))
            alert.exec_()
            return
        round_features = None #not yet implemented
        diph_features = None #not yet implemented
        ClassFeatures = namedtuple('ClassFeatures', ['cons_features','vowel_features','round_feature', 'diph_feature'])
        class_features = ClassFeatures(cons_features, vowel_features, round_features, diph_features)
        self.inventory.set_major_class_features(class_features)
        self.inventory.modelReset()
