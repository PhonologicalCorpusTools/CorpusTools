from collections import OrderedDict
import corpustools.informativity.informativity as informativity
from corpustools.exceptions import PCTError, PCTPythonError
from .windows import FunctionWorker, FunctionDialog
from .imports import *
from .widgets import TierWidget, ContextWidget, RadioSelectWidget, SingleSegmentDialog
from corpustools.contextmanagers import (CanonicalVariantContext,
                                        MostFrequentVariantContext,
                                        SeparatedTokensVariantContext,
                                        WeightedVariantContext)

class InformativityDialog(FunctionDialog):

    header = ['Corpus', 'Segment', 'Informativity', 'Context', 'Type or token', 'Transcription tier', 'Pronunciation variants']

    _about = []

    name = 'informativity'

    def __init__(self, parent, settings, corpus, inventory, showToolTips):
        FunctionDialog.__init__(self, parent, settings, InformativityWorker())#, infinite_progress=True)
        self.corpus = corpus
        self.inventory = inventory
        self.showToolTips = showToolTips

        infoFrame = QFrame()

        infoLayout = QHBoxLayout()
        infoFrame.setLayout(infoLayout)

        segSelectFrame = QFrame()
        segSelectLayout = QVBoxLayout()
        segSelectFrame.setLayout(segSelectLayout)
        self.singleSegButton = QPushButton('Select one or more segments from the inventory')
        self.singleSegButton.clicked.connect(self.addOne)
        self.allSegsButton = QPushButton('Select all segments in the inventory')
        self.allSegsButton.clicked.connect(self.addAll)
        self.removeSegButton = QPushButton('Remove selected segment')
        self.removeSegButton.clicked.connect(self.removeOne)
        self.removeAllSegsButton = QPushButton('Remove all segments')
        self.removeAllSegsButton.clicked.connect(self.removeAll)
        segSelectLayout.addWidget(self.singleSegButton)
        segSelectLayout.addWidget(self.allSegsButton)
        segSelectLayout.addWidget(self.removeSegButton)
        segSelectLayout.addWidget(self.removeAllSegsButton)
        self.segView = QListWidget()
        segSelectLayout.addWidget(self.segView)
        infoLayout.addWidget(segSelectFrame)

        optionsFrame = QFrame()
        optionsLayout = QVBoxLayout()
        optionsFrame.setLayout(optionsLayout)

        self.tierSelect = TierWidget(self.corpus, include_spelling=False)
        optionsLayout.addWidget(self.tierSelect)

        self.precedingContext = RadioSelectWidget('Preceding context',
                                                  OrderedDict([('All preceding segments', 'all')]))
        optionsLayout.addWidget(self.precedingContext)

        self.typeTokenWidget = RadioSelectWidget('Type or token frequencies',
                                                 OrderedDict([('Token', 'token'),
                                                              ('Type', 'type')]))

        actions = None
        self.variantsWidget = ContextWidget(self.corpus, actions)

        optionsLayout.addWidget(self.variantsWidget)
        optionsLayout.addWidget(self.typeTokenWidget)
        infoLayout.addWidget(optionsFrame)

        self.layout().insertWidget(0, infoFrame)

        if showToolTips:
            self.typeTokenWidget.setToolTip('<FONT COLOR=black>'
                'To replicate the original informativity algorithm by Cohen Priva, choose token frequency.'
                '</FONT>')


    def addOne(self):
        self.dialog = SingleSegmentDialog(self.inventory)
        self.dialog.rowToAdd.connect(self.addToList)
        addOneMore = True
        while addOneMore:
            self.dialog.reset()
            result = self.dialog.exec_()
            addOneMore = self.dialog.addOneMore
        self.dialog = None

    def addAll(self):
        self.segView.clear()
        for seg in self.inventory:
            if seg in self.inventory.non_segment_symbols:
                continue
            self.segView.addItem(seg.symbol)
        self.segView.sortItems()

    def removeOne(self):
        current = self.segView.currentRow()
        self.segView.takeItem(current)

    def removeAll(self):
        self.segView.clear()

    def addToList(self, seglist):
        items = [self.segView.item(i).text() for i in range(self.segView.count())]
        for seg in seglist:
            seg = seg[0]
            if seg in items:
                continue
            else:
                self.segView.addItem(seg[0])
        self.segView.sortItems()

    def generateKwargs(self):
        self.kwargs = dict()
        self.kwargs['corpus'] = self.corpus
        self.kwargs['segs'] = [self.segView.item(i).text() for i in range(self.segView.count())]
        self.kwargs['context'] = self.variantsWidget.value()
        self.kwargs['sequence_type'] = self.tierSelect.value()
        self.kwargs['type_token'] = self.typeTokenWidget.value()
        self.kwargs['preceding_context'] = self.precedingContext.value()
        self.kwargs['rounding'] = self.settings['sigfigs']
        self.kwargs['type_or_token'] = self.typeTokenWidget.value()
        return self.kwargs

class InformativityWorker(FunctionWorker):

    def run(self):
        kwargs = self.kwargs
        self.results = []
        context = kwargs.pop('context')
        if context == ContextWidget.canonical_value:
            cm = CanonicalVariantContext
        elif context == ContextWidget.frequent_value:
            cm = MostFrequentVariantContext
        elif context == ContextWidget.separate_value:
            cm = SeparatedTokensVariantContext
        elif context == ContextWidget.relative_value:
            cm = WeightedVariantContext
        corpus = kwargs.pop('corpus')
        sequence_type = kwargs.pop('sequence_type')
        type_token = kwargs.pop('type_token')
        rounding = kwargs.pop('rounding')
        with cm(corpus, sequence_type, type_token) as c:
            try:
                # if len(kwargs['segs']) == 1:
                #     seg = kwargs['segs'][0]
                #     seg = c.inventory[seg]
                #     result = informativity.get_informativity(c, seg, sequence_type,
                #             rounding=rounding,stop_check= kwargs['stop_check'], call_back=kwargs['call_back'])
                #     try:
                #         result.pop('Rounding')
                #         self.results.append(result)
                #     except AttributeError:
                #         self.stopped = True #result is None if user cancelled
                # else:
                results = informativity.get_multiple_informativity(c, kwargs['segs'], sequence_type, type_or_token=kwargs['type_or_token'],
                            rounding=rounding, stop_check= kwargs['stop_check'], call_back=kwargs['call_back'])
                try:
                    for result in results:
                        result.pop('Rounding')
                        self.results.append(result)
                except (TypeError, AttributeError):
                    self.stopped = True #result is None if user cancelled

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
