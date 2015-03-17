

from corpustools.gui.migui import *

app = QApplication([])

def test_migui(specified_test_corpus):
    dialog = MIDialog(None,specified_test_corpus, True)
