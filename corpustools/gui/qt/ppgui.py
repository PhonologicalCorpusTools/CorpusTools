import os

from .imports import *

from collections import OrderedDict

from corpustools.phonoprob.phonotactic_probability import phonotactic_probability_vitevitch
from corpustools.neighdens.io import load_words_neighden

from .windows import FunctionWorker, FunctionDialog
from .widgets import RadioSelectWidget, FileWidget, SaveFileWidget, TierWidget


class PPWorker(FunctionWorker):
    def run(self):
        kwargs = self.kwargs
        self.results = list()
        for q in kwargs['query']:
            if kwargs['algorithm'] == 'vitevitch':
                res = phonotactic_probability_vitevitch(kwargs['corpus'], q,
                                        sequence_type = kwargs['sequence_type'],
                                        count_what = kwargs['count_what'],
                                        probability_type = kwargs['probability_type'],
                                        stop_check = kwargs['stop_check'],
                                        call_back = kwargs['call_back'])
            self.results.append([q,res])
        if self.stopped:
            return
        self.dataReady.emit(self.results)


class PPDialog(FunctionDialog):
    header = ['Word',
                'Tier',
                'Phonotactic probability',
                'Algorithm',
                'Probability type',
                'Type or token']

    _about = [('This function calculates the phonotactic probability '
                    'of a word'),
                    '',
                    'Coded by Michael McAuliffe',
                    '',
                    'References',
                    ('Vitevitch, Michael S. & Paul A. Luce. 2004.'
                    ' A Web-based interface to calculate phonotactic'
                    ' probability for words and nonwords in English.'
                    ' Behavior Research Methods, Instruments, & Computers 36 (3), 481-487')
                    ]

    name = 'phonotactic probability'

    def __init__(self, parent, corpus, showToolTips):
        FunctionDialog.__init__(self, parent, PPWorker())

        self.corpus = corpus
        self.showToolTips = showToolTips

        pplayout = QHBoxLayout()

        algEnabled = {'Vitevitch & Luce':True}
        self.algorithmWidget = RadioSelectWidget('String similarity algorithm',
                                            OrderedDict([
                                            ('Vitevitch & Luce','vitevitch'),
                                            ]),
                                            {'Vitevitch & Luce':self.vitevitchSelected,
                                            },
                                            algEnabled)


        pplayout.addWidget(self.algorithmWidget)

        queryFrame = QGroupBox('Query')

        vbox = QFormLayout()
        self.compType = None
        self.oneWordRadio = QRadioButton('Calculate for one word')
        self.oneWordRadio.clicked.connect(self.oneWordSelected)
        self.oneWordEdit = QLineEdit()
        self.oneWordEdit.textChanged.connect(self.oneWordRadio.click)
        self.fileRadio = QRadioButton('Calculate for list of words')
        self.fileRadio.clicked.connect(self.fileSelected)
        self.fileWidget = FileWidget('Select a file', 'Text file (*.txt *.csv)')
        self.fileWidget.textChanged.connect(self.fileRadio.click)

        vbox.addRow(self.oneWordRadio)
        vbox.addRow(self.oneWordEdit)
        vbox.addRow(self.fileRadio)
        vbox.addRow(self.fileWidget)

        queryFrame.setLayout(vbox)

        pplayout.addWidget(queryFrame)
        optionFrame = QGroupBox('Options')

        optionLayout = QVBoxLayout()

        self.tierWidget = TierWidget(corpus,include_spelling=False)

        optionLayout.addWidget(self.tierWidget)

        self.typeTokenWidget = RadioSelectWidget('Type or token',
                                            OrderedDict([('Count types','type'),
                                            ('Count tokens','token')]))

        optionLayout.addWidget(self.typeTokenWidget)

        self.probabilityTypeWidget = RadioSelectWidget('Probability type',
                                            OrderedDict([('Single-phone','unigram'),
                                            ('Biphone','bigram')]))

        optionLayout.addWidget(self.probabilityTypeWidget)

        optionFrame.setLayout(optionLayout)

        pplayout.addWidget(optionFrame)

        ppFrame = QFrame()
        ppFrame.setLayout(pplayout)

        self.layout().insertWidget(0,ppFrame)

        if self.showToolTips:

            self.tierWidget.setToolTip(("<FONT COLOR=black>"
            'Select whether to calculate neighborhood density'
                                ' on the spelling of a word (perhaps more useful for morphological purposes)'
                                ' or any transcription tier of a word (perhaps more useful for phonological purposes),'
                                ' in the corpus.'
            "</FONT>"))

    def oneWordSelected(self):
        self.compType = 'one'

    def fileSelected(self):
        self.compType = 'file'

    def generateKwargs(self):
        kwargs = {'corpus':self.corpus,
                'algorithm': self.algorithmWidget.value(),
                'sequence_type':self.tierWidget.value(),
                'count_what':self.typeTokenWidget.value(),
                'probability_type':self.probabilityTypeWidget.value()}

        if self.compType is None:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a comparison type.")
            return
        elif self.compType == 'one':
            text = self.oneWordEdit.text()
            if not text:
                reply = QMessageBox.critical(self,
                        "Missing information", "Please specify a word.")
                return
            kwargs['query'] = [text]
        elif self.compType == 'file':
            path = self.fileWidget.value()
            if not path:
                reply = QMessageBox.critical(self,
                        "Missing information", "Please enter a file path.")
                return
            if not os.path.exists(path):
                reply = QMessageBox.critical(self,
                        "Invalid information", "The file path entered was not found.")
                return
            kwargs['query'] = load_words_neighden(path)
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

    def setResults(self, results):
        self.results = list()
        for result in results:
            w, pp = result
            self.results.append([str(w),
                        self.tierWidget.displayValue(), pp,
                        self.algorithmWidget.displayValue(),
                        self.probabilityTypeWidget.displayValue(),
                        self.typeTokenWidget.value()])

    def vitevitchSelected(self):
        self.probabilityTypeWidget.enable()
        self.typeTokenWidget.enable()
