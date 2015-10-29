
from corpustools.gui.pdgui import *

def test_pdgui(qtbot, specified_test_corpus, settings):
    dialog = PDDialog(None, settings,specified_test_corpus, True)
    qtbot.addWidget(dialog)
