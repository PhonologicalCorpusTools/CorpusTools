
from corpustools.gui.main import *

def test_main_window(qtbot):
    window = MainWindow(qtbot._app)
    qtbot.addWidget(window)
