
from corpustools.gui.multimedia import *

def test_audio_player(qtbot):
    widget = AudioPlayer()
    qtbot.addWidget(widget)
