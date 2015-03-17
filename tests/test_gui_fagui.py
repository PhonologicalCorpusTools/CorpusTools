
from corpustools.gui.fagui import *


app = QApplication([])

def test_fagui(specified_test_corpus):
    dialog = FADialog(None,specified_test_corpus, True)
