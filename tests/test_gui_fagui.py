
from corpustools.gui.fagui import *

def test_fagui(qtbot, specified_test_corpus):
    dialog = FADialog(None,specified_test_corpus, True)
    qtbot.addWidget(dialog)
