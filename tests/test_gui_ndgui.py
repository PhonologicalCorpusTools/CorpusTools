
from corpustools.gui.ndgui import *

from corpustools.gui.models import CorpusModel

app = QApplication([])

def test_ndgui(specified_test_corpus, settings):
    dialog = NDDialog(None,CorpusModel(specified_test_corpus, settings), True)
