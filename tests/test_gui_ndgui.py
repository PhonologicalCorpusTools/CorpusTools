
from corpustools.gui.ndgui import *

from corpustools.gui.models import CorpusModel

def test_ndgui(qtbot, specified_test_corpus, settings):
    dialog = NDDialog(None,CorpusModel(specified_test_corpus, settings), True)
    qtbot.addWidget(dialog)
