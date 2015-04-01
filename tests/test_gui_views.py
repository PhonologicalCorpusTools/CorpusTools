
from corpustools.gui.views import *

def test_discourse_view(qtbot):
    widget = DiscourseView()
    qtbot.addWidget(widget)

def test_lexicon_view(qtbot):
    widget = LexiconView()
    qtbot.addWidget(widget)

#def test_phono_search_results():
#   widget = PhonoSearchResults()
    #qtbot.addWidget(widget)

def test_tree_widget(qtbot):
    widget = TreeWidget()
    qtbot.addWidget(widget)

def test_table_widget(qtbot):
    widget = TableWidget()
    qtbot.addWidget(widget)

def test_text_view(qtbot):
    widget = TextView()
    qtbot.addWidget(widget)

def test_variant_view(qtbot, unspecified_test_corpus):
    w = unspecified_test_corpus['atema']
    widget = VariantView(None, w)
    qtbot.addWidget(widget)
