
from corpustools.gui.ppgui import *

from corpustools.gui.models import CorpusModel

def test_ppgui(qtbot, specified_test_corpus, settings):
    dialog = PPDialog(None,CorpusModel(specified_test_corpus, settings), True)
    qtbot.addWidget(dialog)
