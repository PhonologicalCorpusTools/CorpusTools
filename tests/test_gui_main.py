
from corpustools.gui.main import *

def test_main_window(qtbot):
    window = MainWindow(app)
    qtbot.addWidget(window)
