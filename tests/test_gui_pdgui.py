
from corpustools.gui.pdgui import *

def test_pdgui(qtbot, specified_test_corpus):
    dialog = PDDialog(None,specified_test_corpus, True)
    qtbot.addWidget(dialog)
