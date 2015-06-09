

from .imports import *

from .widgets import (EnvironmentSelectWidget, SegmentPairSelectWidget,
                        RadioSelectWidget, InventoryBox, FeatureBox,
                        TierWidget, SegmentSelectionWidget)

from .windows import FunctionWorker, FunctionDialog

from corpustools.corpus.classes.lexicon import EnvironmentFilter

from corpustools.exceptions import PCTError, PCTPythonError

class PSWorker(FunctionWorker):
    def run(self):
        time.sleep(0.1)
        kwargs = self.kwargs
        corpus = kwargs.pop('corpus')
        try:
            self.results = corpus.phonological_search(**kwargs)

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

class PhonoSearchDialog(FunctionDialog):
    header = ['Word',
                'Transcription',
                'Segment',
                'Environment']
    summary_header = ['Segment', ' Environment', 'Type frequency', 'Token frequency']
    _about = ['']

    name = 'phonological search'
    def __init__(self, parent, settings, corpus, showToolTips):
        FunctionDialog.__init__(self, parent, settings, PSWorker())

        self.corpus = corpus
        self.showToolTips = showToolTips

        psFrame = QFrame()
        pslayout = QHBoxLayout()

        self.targetWidget = SegmentSelectionWidget(self.corpus.inventory)

        pslayout.addWidget(self.targetWidget)

        self.envWidget = EnvironmentSelectWidget(self.corpus.inventory)
        pslayout.addWidget(self.envWidget)


        optionLayout = QVBoxLayout()

        self.tierWidget = TierWidget(corpus,include_spelling=False)

        optionLayout.addWidget(self.tierWidget)

        optionFrame = QGroupBox('Options')

        optionFrame.setLayout(optionLayout)

        pslayout.addWidget(optionFrame)

        psFrame.setLayout(pslayout)
        self.layout().insertWidget(0,psFrame)
        self.setWindowTitle('Phonological search')
        self.progressDialog.setWindowTitle('Searching')

    def generateKwargs(self):
        kwargs = {}
        targetList = self.targetWidget.value()
        if not targetList:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify at least one {}.".format(targetType[:-1].lower()))
            return
        kwargs['seg_list'] = targetList
        kwargs['corpus'] = self.corpus
        kwargs['sequence_type'] = self.tierWidget.value()
        envs = self.envWidget.value()
        if len(envs) > 0:
            kwargs['envs'] = envs
        return kwargs

    def calc(self):
        kwargs = self.generateKwargs()
        if kwargs is None:
            return
        self.thread.setParams(kwargs)
        self.thread.start()

        result = self.progressDialog.exec_()

        self.progressDialog.reset()
        if result:
            self.accept()

    def setResults(self,results):
        self.results = list()
        for w,f in results:
            segs = [x[0] for x in f]
            try:
                envs = [str(x[1]) for x in f]
            except IndexError:
                envs = []
            self.results.append([w, str(getattr(w,self.tierWidget.value())),segs,
                                envs])
