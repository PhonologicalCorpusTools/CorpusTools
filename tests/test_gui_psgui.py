

from corpustools.gui.psgui import *

def test_psgui(qtbot, specified_test_corpus, settings):
    dialog = PhonoSearchDialog(None, settings, specified_test_corpus, True)
    qtbot.addWidget(dialog)
