
from corpustools.gui.views import *

app = QApplication([])

def test_discourse_view():
    widget = DiscourseView()

def test_lexicon_view():
    widget = LexiconView()

#def test_phono_search_results():
#   widget = PhonoSearchResults()

def test_tree_widget():
    widget = TreeWidget()

def test_table_widget():
    widget = TableWidget()

def test_text_view():
    widget = TextView()

def test_variant_view():
    widget = VariantView(None, {})
