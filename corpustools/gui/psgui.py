from .imports import *
import time

from .widgets import TierWidget

from .windows import FunctionWorker, FunctionDialog

from .environments import EnvironmentSelectWidget

from corpustools.phonosearch import phonological_search

from corpustools.exceptions import PCTError, PCTPythonError

class PSWorker(FunctionWorker):
    def run(self):
        time.sleep(0.1)
        kwargs = self.kwargs
        try:
            self.results = phonological_search(**kwargs)
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
                'Environment',
                'Token frequency']
    summary_header = ['Segment', 'Environment', 'Type frequency', 'Token frequency']
    _about = ['']

    name = 'phonological search'
    def __init__(self, parent, settings, corpus, inventory, showToolTips):
        FunctionDialog.__init__(self, parent, settings, PSWorker())

        self.corpus = corpus
        self.inventory = inventory
        self.showToolTips = showToolTips

        psFrame = QFrame()
        pslayout = QHBoxLayout()
        self.envWidget = EnvironmentSelectWidget(self.inventory,
                                                 show_full_inventory=bool(settings['show_full_inventory']))
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
        envs = self.envWidget.value()
        if len(envs) > 0:
            for i, e in enumerate(envs):
                if len(e.middle) == 0:
                    reply = QMessageBox.critical(self, "Missing information",
                            "Please specify at least segment to search for in environment {}.".format(i+1))
                    return
            kwargs['envs'] = envs

        kwargs['corpus'] = self.corpus
        kwargs['sequence_type'] = self.tierWidget.value()
        return kwargs

    def setResults(self,results):
        self.results = []
        for w,f in results:
            segs = tuple(x.middle for x in f)
            try:
                envs = tuple(str(x) for x in f)
            except IndexError:
                envs = tuple()
            self.results.append({'Word': w, 
                                'Transcription': str(getattr(w,self.tierWidget.value())),
                                'Segment': segs,
                                'Environment': envs,
                                'Token frequency':w.frequency})
