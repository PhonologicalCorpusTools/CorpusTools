

from corpustools.gui.ssgui import *

from corpustools.gui.models import CorpusModel

def test_ssgui(qtbot, specified_test_corpus, settings):
    dialog = SSDialog(None, CorpusModel(specified_test_corpus, settings), True)
    qtbot.addWidget(dialog)
