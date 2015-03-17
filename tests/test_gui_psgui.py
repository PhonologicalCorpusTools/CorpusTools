

from corpustools.gui.psgui import *

app = QApplication([])

def test_psgui(specified_test_corpus):
    dialog = PhonoSearchDialog(None, specified_test_corpus, True)
