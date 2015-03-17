
from corpustools.gui.pdgui import *

app = QApplication([])

def test_pdgui(specified_test_corpus):
    dialog = PDDialog(None,specified_test_corpus, True)
