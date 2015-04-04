
from corpustools.gui.config import *

def test_preferences(qtbot, settings):
    dialog = PreferencesDialog(None, settings)
    qtbot.addWidget(dialog)

    dialog.accept()
