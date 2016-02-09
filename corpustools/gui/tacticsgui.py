from .imports import *
from .windows import FunctionWorker, FunctionDialog
from .widgets import FeatureCompleter, FeatureEdit, ContextWidget, TierWidget
from corpustools.contextmanagers import (CanonicalVariantContext,
                                         MostFrequentVariantContext,
                                         SeparatedTokensVariantContext,
                                         WeightedVariantContext)
from corpustools.tactics import tactics
from corpustools.exceptions import PCTError, PCTPythonError
import time

class TacticsWorker(FunctionWorker):

    def __init__(self):
        super().__init__()

    def run(self):
        time.sleep(0.1)
        kwargs = self.kwargs
        self.results = list()
        context = kwargs.pop('context')
        nucleus = kwargs['nucleus']
        tier = kwargs['sequence_type']
        inventory = kwargs['inventory']
        if context == ContextWidget.canonical_value:
            cm = CanonicalVariantContext
        elif context == ContextWidget.frequent_value:
            cm = MostFrequentVariantContext
        elif context == ContextWidget.separate_value:
            cm = SeparatedTokensVariantContext
        elif context == ContextWidget.relative_value:
            cm = WeightedVariantContext
        with cm(kwargs['corpus'], kwargs['sequence_type'], kwargs['type_token']) as corpus:
            try:
                res = tactics.findSyllableShapes(corpus, inventory, nucleus, kwargs['stop_check'], kwargs['call_back'])
                if not self.stopped:
                    self.results = res
            except PCTError as e:
                self.errorEncountered.emit(e)
                return
            except Exception as e:
                e = PCTPythonError(e)
                self.errorEncountered.emit(e)
                return
        if self.stopped:
            self.finishedCancelling.emit()
            return
        self.dataReady.emit(self.results)

class TacticsDialog(FunctionDialog):
    header = ['Onset type', 'Frequency', 'Coda Type', 'Frequency']

    _about = ''

    name = 'Phonotactic inference'


    def __init__(self,parent, corpus, inventory, settings, showToolTips):
        super().__init__(parent, settings, TacticsWorker())
        self.corpus = corpus
        self.inventory = inventory
        self.showToolTips = showToolTips

        nucleusFrame = QFrame()
        nucleusLayout = QHBoxLayout()
        nucleusLayout.addWidget(QLabel('What feature defines a syllable nucleus?'))
        self.nucleusEdit = FeatureEdit(self.inventory)
        consCompleter = FeatureCompleter(self.inventory)
        self.nucleusEdit.setCompleter(consCompleter)
        if self.inventory.vowel_features is not None:
            self.nucleusEdit.setText(self.inventory.vowel_features[0])
        nucleusLayout.addWidget(self.nucleusEdit)
        nucleusFrame.setLayout(nucleusLayout)


        parseFrame = QFrame()
        parseTypeLayout = QHBoxLayout()
        parseTypeLayout.addWidget(QLabel('Select a parsing strategy:'))
        self.parseTypeRadio = QRadioButton('Onset Maximization')
        parseTypeLayout.addWidget(self.parseTypeRadio)
        parseFrame.setLayout(parseTypeLayout)


        optionFrame = QFrame()
        optionFrame.setWindowTitle('Options')
        optionBox = QVBoxLayout()
        self.variantsWidget = ContextWidget(self.corpus, None)
        optionBox.addWidget(self.variantsWidget)
        self.tierWidget = TierWidget(corpus, include_spelling=False)
        optionBox.addWidget(self.tierWidget)


        self.layout().insertWidget(0, nucleusFrame)
        self.layout().insertWidget(1,parseFrame)
        self.layout().insertWidget(2,optionFrame)


    def generateKwargs(self, *args):
        kwargs = dict()
        kwargs['corpus'] = self.corpus
        nucleus = self.nucleusEdit.text().strip()
        kwargs['nucleus'] = nucleus
        kwargs['type_token'] = 'type'
        kwargs['sequence_type'] = self.tierWidget.value()
        kwargs['context'] = self.variantsWidget.value()
        kwargs['inventory'] = self.inventory
        return kwargs


    def accept(self):
        QDialog.accept(self)

    def reject(self):
        QDialog.reject(self)