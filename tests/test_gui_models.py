
from corpustools.gui.models import *

def test_base_corpus_model(qtbot, specified_test_corpus):
    model = BaseCorpusTableModel()
    qtbot.addWidget(model)

def test_base_table_model(qtbot):
    model = BaseTableModel()
    qtbot.addWidget(model)

def test_corpus_model(qtbot, specified_test_corpus, settings):
    model = CorpusModel(specified_test_corpus, settings)
    qtbot.addWidget(model)

#def test_discourse_model(qtbot):
    #model = DiscourseModel()
    #qtbot.addWidget(model)

def test_environment_model(qtbot):
    model = EnvironmentModel()
    qtbot.addWidget(model)

def test_feature_system_table_model(qtbot, spe_specifier):
    model = FeatureSystemTableModel(spe_specifier)
    qtbot.addWidget(model)

def test_feature_system_tree_model(qtbot, spe_specifier):
    model = FeatureSystemTreeModel(spe_specifier)
    qtbot.addWidget(model)

def test_filter_model(qtbot):
    model = FilterModel()
    qtbot.addWidget(model)

def test_segment_pair_model(qtbot):
    model = SegmentPairModel()
    qtbot.addWidget(model)

def test_variant_model(qtbot, unspecified_test_corpus):
    w = unspecified_test_corpus['atema']
    model = VariantModel(w)
    qtbot.addWidget(model)

#def test_spontaneous_speech_model(qtbot):
    #model = SpontaneousSpeechCorpusModel()
    #qtbot.addWidget(model)


