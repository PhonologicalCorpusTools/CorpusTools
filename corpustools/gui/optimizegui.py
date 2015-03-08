

from collections import OrderedDict

from corpustools.symbolsim.string_similarity import optimize_string_similarity, string_sim_key
from corpustools.exceptions import PCTError, PCTPythonError

from .imports import *

from .windows import FunctionWorker, FunctionDialog
from .widgets import RadioSelectWidget, TierWidget

class OptimizeSSWorker(FunctionWorker):
    def run(self):
        time.sleep(0.1)
        kwargs = self.kwargs
        try:
            optimize_string_similarity(kwargs['corpus'],
                                        kwargs['algorithm'],
                                        kwargs['sequence_type'], kwargs['count_what'],
                                        max_distance = kwargs['max_distance'],
                                        num_cores = kwargs['num_cores'],
                                        stop_check = kwargs['stop_check'],
                                        call_back = kwargs['call_back'])
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
        self.dataReady.emit('success')

class OptimizeStringSimDialog(FunctionDialog):
    def __init__(self, parent, corpus):
        FunctionDialog.__init__(self, parent, OptimizeSSWorker())
        self.corpus = corpus
        if not self.corpus.has_transcription:
            self.layout().addWidget(QLabel('Corpus does not have transcription, so not all options are available.'))

        sslayout = QHBoxLayout()

        algEnabled = {'Khorsi':True,
                    'Edit distance':True,
                    'Phonological edit distance':self.corpus.has_transcription}
        self.algorithmWidget = RadioSelectWidget('String similarity algorithm',
                                            OrderedDict([('Edit distance','edit_distance'),
                                            ('Phonological edit distance','phono_edit_distance'),
                                            ('Khorsi','khorsi')]),
                                            {'Khorsi':self.khorsiSelected,
                                            'Edit distance':self.editDistSelected,
                                            'Phonological edit distance':self.phonoEditDistSelected},
                                            algEnabled)


        sslayout.addWidget(self.algorithmWidget)

        optionFrame = QGroupBox('Options')

        optionLayout = QVBoxLayout()

        self.tierWidget = TierWidget(self.corpus,include_spelling=True)

        optionLayout.addWidget(self.tierWidget)

        self.typeTokenWidget = RadioSelectWidget('Type or token',
                                            OrderedDict([('Count types','type'),
                                            ('Count tokens','token')]))

        optionLayout.addWidget(self.typeTokenWidget)

        threshFrame = QGroupBox('Max distance/min similarity to cache')

        self.maxDistanceEdit = QLineEdit()
        self.maxDistanceEdit.setText('10')

        vbox = QFormLayout()
        vbox.addRow('Threshold:',self.maxDistanceEdit)

        threshFrame.setLayout(vbox)

        optionLayout.addWidget(threshFrame)

        optionFrame.setLayout(optionLayout)

        sslayout.addWidget(optionFrame)

        ssFrame = QFrame()
        ssFrame.setLayout(sslayout)

        self.layout().insertWidget(0,ssFrame)

    def generateKwargs(self):
        if self.maxDistanceEdit.text() == '':
            max_distance = None
        else:
            max_distance = float(self.maxDistanceEdit.text())
        kwargs = {'corpus':self.corpus,
                'algorithm': self.algorithmWidget.value(),
                'sequence_type':self.tierWidget.value(),
                'count_what': self.typeTokenWidget.value(),
                'max_distance': max_distance,
                'num_cores':self.parent().settings['num_cores']}
        key = string_sim_key(kwargs['algorithm'], kwargs['sequence_type'], kwargs['count_what'])
        if key in self.corpus._graph.graph['symbolsim']:
            msgBox = QMessageBox(QMessageBox.Warning, "Cache exists",
                    "An optimization for these parameters already exists.  Overwrite?", QMessageBox.NoButton, self)
            msgBox.addButton("Overwrite", QMessageBox.AcceptRole)
            msgBox.addButton("Abort", QMessageBox.RejectRole)
            if msgBox.exec_() != QMessageBox.AcceptRole:
                return

        return kwargs



    def calc(self):
        kwargs = self.generateKwargs()
        if kwargs is None:
            return
        self.thread.setParams(kwargs)
        self.thread.start()

        result = self.progressDialog.exec_()

        if result:
            self.accept()

    def khorsiSelected(self):
        self.typeTokenWidget.enable()
        self.tierWidget.setSpellingEnabled(True)

    def editDistSelected(self):
        self.typeTokenWidget.disable()
        self.tierWidget.setSpellingEnabled(True)

    def phonoEditDistSelected(self):
        self.typeTokenWidget.disable()
        self.tierWidget.setSpellingEnabled(False)

