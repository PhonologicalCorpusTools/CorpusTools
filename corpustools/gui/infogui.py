from collections import OrderedDict
from .windows import FunctionWorker, FunctionDialog
from .imports import *
from .widgets import SegmentPairSelectWidget, TierWidget, ContextWidget, RadioSelectWidget, SingleSegmentDialog

class InformativityDialog(FunctionDialog):

    header = []

    _about = []

    name = 'informativity'

    def __init__(self, parent, settings, corpus, inventory, showToolTips):
        FunctionDialog.__init__(self, parent, settings, InformativityWorker())
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

        self.tierSelect = TierWidget(self.corpus, include_spelling=True)
        optionsLayout.addWidget(self.tierSelect)

        self.precedingContext = RadioSelectWidget('Preceding context',
                                                  OrderedDict([('All contexts', 'all')]))
        optionsLayout.addWidget(self.precedingContext)

        self.typeTokenWidget = RadioSelectWidget('Type or token frequencies',
                                                 OrderedDict([('Type', 'type'),
                                                              ('Token', 'token')]))
        actions = None
        self.variantsWidget = ContextWidget(self.corpus, actions)

        optionsLayout.addWidget(self.variantsWidget)
        optionsLayout.addWidget(self.typeTokenWidget)
        infoLayout.addWidget(optionsFrame)

        self.layout().insertWidget(0, infoFrame)

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
        self.kwargs['segs'] = [self.segView.item(i).text() for i in range(self.segView.count())]
        self.kwargs['corpus_context'] = self.variantsWidget.value()
        self.kwargs['sequence_type'] = self.tierSelect.value()
        self.kwargs['type_token'] = self.typeTokenWidget.value()
        self.kwargs['preceding_context'] = self.precedingContext.value()

class InformativityWorker(FunctionWorker):

    def run(self):
        pass