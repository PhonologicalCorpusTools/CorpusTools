
from corpustools.gui.models import *

app = QApplication([])

def test_base_corpus_model(specified_test_corpus):
    model = BaseCorpusTableModel()

def test_base_table_model():
    model = BaseTableModel()

def test_corpus_model(specified_test_corpus, settings):
    model = CorpusModel(specified_test_corpus, settings)

#def test_discourse_model():
    #model = DiscourseModel()

def test_environment_model():
    model = EnvironmentModel()

def test_feature_system_table_model(spe_specifier):
    model = FeatureSystemTableModel(spe_specifier)

def test_feature_system_tree_model(spe_specifier):
    model = FeatureSystemTreeModel(spe_specifier)

def test_filter_model():
    model = FilterModel()

def test_segment_pair_model():
    model = SegmentPairModel()

def test_variant_model():
    model = VariantModel([])

#def test_spontaneous_speech_model():
    #model = SpontaneousSpeechCorpusModel()


