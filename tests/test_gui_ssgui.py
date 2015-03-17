

from corpustools.gui.ssgui import *

from corpustools.gui.models import CorpusModel

app = QApplication([])

def test_ssgui(specified_test_corpus, settings):
    dialog = SSDialog(None, CorpusModel(specified_test_corpus, settings), True)
