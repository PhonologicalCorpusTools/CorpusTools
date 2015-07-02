
from corpustools.gui.klgui import *

def test_klgui(qtbot, specified_test_corpus, settings):
    dialog = KLDialog(None, settings,specified_test_corpus, True)
    qtbot.addWidget(dialog)
