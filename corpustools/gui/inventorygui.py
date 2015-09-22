import os

from .imports import *

from .views import InventoryView
#
# from .models import FeatureSystemTableModel, FeatureSystemTreeModel
#
# from .widgets import InventoryTable, InventoryBox
#
# from .helpgui import HelpDialog



class InventoryManager(QDialog):
    def __init__(self, parent, model):
        super().__init__()
        layout = QVBoxLayout()

        topmessage = QLabel(text=('You can edit your inventory chart from this window. Double-click on a row or column to edit the '
                      'class of segments which appear in that row or column. You can also single click on a heading to '
                      'highlight the row or column, then drag-and-drop to reorganize the table.'))
        topmessage.setWordWrap(True)
        layout.addWidget(topmessage)

        self.segSelectWidget = InventoryView(model)
        layout.addWidget(self.segSelectWidget)

        buttonLayout = QHBoxLayout()
        # add = QPushButton('Add row or column')
        # add.clicked.connect(self.addToTable)
        # remove = QPushButton('Remove row or column')
        # remove.clicked.connect(self.removeFromTable)
        # reorder = QPushButton('Reorder rows or columns')
        # reorder.clicked.connect(self.reorderTable)
        ok_button = QPushButton('OK')
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)

        # buttonLayout.addWidget(add)
        # buttonLayout.addWidget(remove)
        #buttonLayout.addWidget(reorder)
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

