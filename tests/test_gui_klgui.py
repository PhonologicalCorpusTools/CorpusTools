
from corpustools.gui.klgui import *

app = QApplication([])

def test_klgui(specified_test_corpus):
    dialog = KLDialog(None,specified_test_corpus, True)
