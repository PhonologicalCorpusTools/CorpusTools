import os
import copy

from .imports import *

from .views import TableWidget, SubTreeView

from .models import FeatureSystemTableModel, FeatureSystemTreeModel

from .widgets import InventoryTable, InventoryBox

from .helpgui import HelpDialog

class InventoryManager(QDialog):
    def __init__(self, parent, corpus):
        super().__init__()
        self.corpus = corpus
        self.segSelectWidget = InventoryBox(self, self.corpus, editable=True)
        segLayout = QVBoxLayout()
        segLayout.addWidget(self.segSelectWidget)
        self.setLayout(segLayout)
        #STILL NEED 'OK', 'CANCEL', 'ADD ROW', 'REMOVE ROW', 'ADD COLUMN', 'REMOVE COLUMN'
