
from corpustools.gui.views import *
from corpustools.gui.models import CorpusModel

def test_discourse_view(qtbot):
    widget = DiscourseView()
    qtbot.addWidget(widget)

def test_lexicon_view(qtbot, unspecified_test_corpus, settings):
    widget = LexiconView()
    model = CorpusModel(unspecified_test_corpus, settings)
    qtbot.addWidget(widget)
    qtbot.addWidget(model)

    widget.setModel(model)
    widget.search()
    assert(len(widget.table.selectionModel().selectedRows()) == 0)
    widget.searchField.setText('ma')
    widget.search()
    assert(len(widget.table.selectionModel().selectedRows()) == 1)
    assert(widget.table.selectionModel().selectedRows()[0].row() == 0)
    widget.search()
    assert(len(widget.table.selectionModel().selectedRows()) == 1)
    assert(widget.table.selectionModel().selectedRows()[0].row() == 2)
    widget.searchField.setText('matemma')
    widget.search()
    assert(len(widget.table.selectionModel().selectedRows()) == 0)

    w = model.wordObject(0)
    widget.highlightType(w)
    assert(len(widget.table.selectionModel().selectedRows()) == 1)
    assert(widget.table.selectionModel().selectedRows()[0].row() == 0)




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
