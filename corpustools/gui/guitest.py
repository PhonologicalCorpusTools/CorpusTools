import sys
import unittest
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from corpustools.gui.flgui import FLDialog, FLWorker
from corpustools.corpus.io import load_binary
from corpustools.gui.models import InventoryModel

class FLTester(unittest.TestCase):

    def test_DialogLoad(self):
        corpus = load_binary(r'C:\Users\Scott\Documents\GitHub\CorpusTools\corpustools\lemurian.corpus')
        inventory = InventoryModel(corpus.inventory, copy_mode=True)
        self.dialog = FLDialog(parent=None, corpus=corpus, inventory=inventory, settings=None, showToolTips=False)

    def test_MinFreqEdit(self):

        self.dialog.minFreqEdit.clear()
        QTest.keyClicks('2', self.dialog.minFreqEdit)
        self.assertEqual(self.dialog.minFreqEdit.value(), '2')

    def test_FuncLoadAlgorithmChoice(self):

        print(self.dialog.algorithmWidget.value())
        QTest.MouseClick(self.dialog.algorithmWidget.widgets[1], Qt.LeftButton)
        print(self.dialog.algorithmWidget.value())
        self.assertEqual(self.dialog.value(), 'entropy')

    def test_Kwargs(self):
        self.assertEqual(self.dialog.kwargs['frequency_cutoff'], '2')
        self.assertEqual(self.dialog.kwargs[''])


if __name__ == '__main__':
    unittest.main()



