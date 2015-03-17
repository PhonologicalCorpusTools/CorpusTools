
from corpustools.gui.flgui import *


app = QApplication([])

def test_flgui(specified_test_corpus):
    dialog = FLDialog(None,specified_test_corpus, True)
