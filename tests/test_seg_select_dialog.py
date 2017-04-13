import unittest
import sys
import os
import pickle
from PyQt5.QtTest import QTest
from PyQt5.QtGui import *
base = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0,base)
from corpustools.gui.widgets import *
from corpustools.gui.models import InventoryModel
app = QApplication(sys.argv)

class SingleSegmentSelectWidgetTest(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(os.getcwd(), 'lemurian.corpus'), 'rb') as f:
            self.test_corpus = pickle.load(f)
        self.settings = {'tooltips': False}  # mock settings object
        self.test_corpus.inventoryModel = InventoryModel(self.test_corpus.inventory, copy_mode=True)
        self.dialog = SegmentPairSelectWidget(self.test_corpus.inventoryModel, None, True, True)
                                             #(inventory, parent = None, features = True, single_segment = False)

    def test_add_one(self):
        QTest.mouseClick(self.addSingleButton, Qt.LeftButton)
