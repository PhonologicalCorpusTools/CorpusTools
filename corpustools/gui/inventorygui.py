import os
import copy

from .imports import *

from .views import TableWidget, SubTreeView

from .models import FeatureSystemTableModel, FeatureSystemTreeModel

from .widgets import FileWidget, RadioSelectWidget,SaveFileWidget, InventoryBox, CreateClassWidget

from .helpgui import HelpDialog


class InventoryManager(QDialog):
    def __init__(self, parent, corpus):
        super().__init__()
        self.corpus = corpus
        self.segFrame = QGroupBox()
        self.segSelectWidget = InventoryBox('Segments',self.corpus.inventory)
        segLayout = QVBoxLayout()
        segLayout.addWidget(self.segSelectWidget)
        self.segFrame.setLayout(segLayout)
