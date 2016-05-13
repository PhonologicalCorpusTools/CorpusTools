import sys
import unittest
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
from corpustools.gui.flgui import FLDialog, FLWorker
from corpustools.corpus.io import load_binary
from corpustools.gui.models import InventoryModel
from corpustools.gui.main import MainWindow, QApplicationMessaging

app = QApplicationMessaging(sys.argv)
main = MainWindow(app)

class FLTester(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        corpus = load_binary(r'C:\Users\Scott\Documents\GitHub\CorpusTools\corpustools\lemurian.corpus')
        inventory = InventoryModel(corpus.inventory, copy_mode=True)
        cls.dialog = FLDialog(main, None, corpus, inventory, False)

    def test_FuncLoadAlgorithmChoice(self):
        print(self.dialog.algorithmWidget.value())
        self.dialog.algorithmWidget.widgets[1].click()
        #why doesn't this work with QTest.mouseClick(...,Qt.LeftButton, Qt.NoModifier) ???
        print(self.dialog.algorithmWidget.value())
        self.assertEqual(self.dialog.algorithmWidget.value(), 'entropy')

    def test_MinFreqEdit(self):
        self.dialog.minFreqEdit.clear()
        QTest.keyClicks(self.dialog.minFreqEdit, '2')
        self.assertEqual(self.dialog.minFreqEdit.text(), '2')

    @unittest.expectedFailure()
    def test_Kwargs(self):
         QTest.mouseClick(self.dialog.newTableButton, Qt.LeftButton)
         self.assertEqual(self.dialog.kwargs['frequency_cutoff'], '2')

if __name__ == '__main__':
    unittest.main()



