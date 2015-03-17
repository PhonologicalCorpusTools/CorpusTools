
from corpustools.gui.asgui import *

from PyQt5.QtTest import QTest

app = QApplication([])

def test_asgui():
    dialog = ASDialog(None, True)
