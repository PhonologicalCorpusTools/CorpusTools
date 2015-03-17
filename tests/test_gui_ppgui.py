
from corpustools.gui.ppgui import *

from corpustools.gui.models import CorpusModel

app = QApplication([])

def test_ppgui(specified_test_corpus, settings):
    dialog = PPDialog(None,CorpusModel(specified_test_corpus, settings), True)
