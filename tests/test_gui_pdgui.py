import unittest
import sys
import os
import pickle
from PyQt5.QtTest import QTest
from PyQt5.QtGui import *
#In order for QTest to work, you must have a QApplication object instantiated
#However, you cannot directly import QApplication from PyQt5.QtGui (although it can be done through
#PyQt4.QtGui), so instead I have to import *everything* from PyQt5.QtGui which somehow makes QApplication available
#There is an object called PyQt5.QGuiApplication, but using this is not compatible with unittest
#(importing QGuiApplication lets this program run, but there is literally no test output (it calls self.setUp()
#and nothing else)
base = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0,base)
from corpustools.gui.pdgui import *
from corpustools.gui.models import InventoryModel
app = QApplication(sys.argv)

class PredOfDistGuiTest(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(os.getcwd(), 'lemurian.corpus'), 'rb') as f:
            self.test_corpus = pickle.load(f)

        self.settings = {'tooltips': False} #mock settings
        self.test_corpus.inventoryModel = InventoryModel(self.test_corpus.inventory, copy_mode=True)
        self.dialog = PDDialog(None, self.settings, self.test_corpus, self.test_corpus.inventoryModel, True)

    def tearDown(self):
        self.dialog.reject()

    def test_kwargs(self):
        kwargs = self.dialog.generateKwargs()


    #TEST THE GUI - CHECK DEFAULTS, AND CHECK THAT THE BUTTONS DO WHAT THEY SHOULD DO

    # def test_defaults(self):
    #     self.assertTrue(self.dialog.typeTokenWidget.widgets[0].isChecked())
    #     self.assertTrue(self.dialog.enforceCheck.isChecked())
    #     self.assertEqual(self.dialog.minFreqEdit.text(), '')

    # def test_add_one_seg(self):
    #     #test that the dialog window pops-up
    #     add_button = self.dialog.segPairWidget.addSingleButton
    #     self.assertIsNotNone(add_button)
    #     QTest.mouseClick(add_button, Qt.LeftButton)
    #     self.assertIsNotNone(self.dialog.segPairWidget.dialog)

        # #test that there is an 's' in the inventory
        # self.assertTrue('s' in [btn.text() for btn in self.dialog.segPairWidget.dialog.inventoryFrame.btnGroup.buttons()])
        #
        # #test that clicking on 's' adds it to the selected segment list
        # for btn in self.dialog.segPairWidget.dialog.inventoryFrame.btnGroup.buttons():
        #     if btn.text() == 's':
        #         s = btn
        #         break
        # QTest.mouseClick(s, Qt.LeftButton)
        # self.assertEqual(self.dialog.segPairWidget.dialog.inventoryFrame.selectedSegList, ['s'])

    # def test_add_seg_pair(self):
    #     #test that the dialog window pops-up
    #     QTest.mouseClick(self.dialog.segPairWidget.addButton, Qt.LeftButton)
    #
    #     # test that both 's' and 't' are in the inventory
    #     buttons = [btn for btn in self.dialog.segPairWidget.dialog.inventoryFrame.btnGroup.buttons() if
    #                btn.text() in ['s', 't']]
    #     buttons_text = [b.text() for b in buttons]
    #     self.assertTrue('s' in buttons_text)
    #     self.assertTrue('t' in buttons_text)
    #
    #     self.assertIsInstance(self.dialog.segPairWidget.dialog, SegmentPairSelectWidget)
    #
    #
    #
    #
    #
    #     #test that clicking on 's' and 't' adds them to the selected segment list
    #     selections = [b for b in buttons if b.text() in ['s', 't']]
    #     selections.sort()
    #     s,t = selections
    #     QTest.mouseClick(s, Qt.LeftButton)
    #     QTest.mouseClick(t, Qt.LeftButton)
    #     self.assertEqual(self.dialog.segPairWidget.dialog.inventoryFrame.selectedSegList, ['s','t'])
    #
    # def test_add_environment(self):
    #     pass

    #RUN AN ANALYSIS AND TEST THE OUTPUT
    #THESE TESTS SHOULD PROBABLY START BY CHECKING THAT generateKwargs WORKS AND FINISH BY CHECKING results

    def test_with_exhaustivity(self):
        pass

    def test_without_exhaustivity(self):
        pass

    def test_min_frequency(self):
        pass



if __name__ == '__main__':
    unittest.main()



# def test_pdgui(qtbot, specified_test_corpus, settings):
#     dialog = PDDialog(None, settings, specified_test_corpus, True)
#     qtbot.addWidget(dialog)
