
from corpustools.gui.fagui import *

def test_fagui(qtbot, specified_test_corpus, settings):
    dialog = FADialog(None, settings,specified_test_corpus, True)
    qtbot.addWidget(dialog)
