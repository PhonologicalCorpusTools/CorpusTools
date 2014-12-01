
from .imports import *

from collections import OrderedDict

from corpustools.neighdens.neighborhood_density import neighborhood_density

from .windows import FunctionWorker, FunctionDialog
from .widgets import RadioSelectWidget, FileWidget


class NDWorker(FunctionWorker):
    def run(self):
        kwargs = self.kwargs
        self.results = list()
        for q in kwargs['query']:
            self.results.append([q,neighborhood_density(kwargs['corpus'], q,
                                        algorithm = kwargs['algorithm'],
                                        string_type = kwargs['string_type'],
                                        #tier_name = kwargs['tier_name'],
                                        count_what = kwargs['count_what'],
                                        max_distance = kwargs['max_distance'],
                                        stop_check = kwargs['stop_check'],
                                        call_back = kwargs['call_back'])[0]])
        if self.stopped:
            return
        self.dataReady.emit(self.results)


class NDDialog(FunctionDialog):
    header = ['Word',
                'Neighborhood density',
                'String type',
                'Type or token',
                'Algorithm type']

    _about = [('This function calculates the neighborhood density '
                    'of a word'),
                    '',
                    'Coded by Blake Allen and Michael Fry',
                    #'',
                    #'References',
                    #('Surendran, Dinoj & Partha Niyogi. 2003. Measuring'
                    #' the functional load of phonological contrasts.'
                    #' In Tech. Rep. No. TR-2003-12.'),
                    #('Wedel, Andrew, Abby Kaplan & Scott Jackson. 2013.'
                    #' High functional load inhibits phonological contrast'
                    #' loss: A corpus study. Cognition 128.179-86')
                    ]

    name = 'neighborhood density'

    def __init__(self, parent, corpus, showToolTips):
        FunctionDialog.__init__(self, parent, NDWorker())

        self.corpus = corpus
        self.showToolTips = showToolTips

        if not self.corpus.has_transcription:
            layout.addWidget(QLabel('Corpus does not have transcription, so not all options are available.'))

        ndlayout = QHBoxLayout()

        algEnabled = {'Khorsi':True,
                    'Edit distance':True,
                    'Phonological edit distance':self.corpus.has_transcription}
        self.algorithmWidget = RadioSelectWidget('String similarity algorithm',
                                            OrderedDict([
                                            ('Edit distance','edit_distance'),
                                            ('Phonological edit distance','phono_edit_distance'),
                                            ('Khorsi','khorsi'),]),
                                            {'Khorsi':self.khorsiSelected,
                                            'Edit distance':self.editDistSelected,
                                            'Phonological edit distance':self.phonoEditDistSelected},
                                            algEnabled)


        ndlayout.addWidget(self.algorithmWidget)

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

        ndlayout.addWidget(queryFrame)
        optionFrame = QGroupBox('Options')

        optionLayout = QVBoxLayout()

        self.typeTokenWidget = RadioSelectWidget('Type or token',
                                            {'Count types':'type',
                                            'Count tokens':'token'})

        optionLayout.addWidget(self.typeTokenWidget)

        stringEnabled = {'Compare spelling':True,
                        'Compare transcription': self.corpus.has_transcription}
        self.stringTypeWidget = RadioSelectWidget('String type',
                                    OrderedDict([('Compare spelling', 'spelling'),
                                    ('Compare transcription','transcription')]),
                                    enabled = stringEnabled)

        optionLayout.addWidget(self.stringTypeWidget)

        threshFrame = QGroupBox('Max distance/min similarity')

        self.maxDistanceEdit = QLineEdit()
        self.maxDistanceEdit.setText('1')

        vbox = QFormLayout()
        vbox.addRow('Threshold:',self.maxDistanceEdit)

        threshFrame.setLayout(vbox)

        optionLayout.addWidget(threshFrame)

        optionFrame.setLayout(optionLayout)

        ndlayout.addWidget(optionFrame)

        ndFrame = QFrame()
        ndFrame.setLayout(ndlayout)

        self.layout().insertWidget(0,ndFrame)

    def oneWordSelected(self):
        self.compType = 'one'

    def fileSelected(self):
        self.compType = 'file'

    def generateKwargs(self):
        if self.maxDistanceEdit.text() == '':
            max_distance = None
        else:
            max_distance = float(self.maxDistanceEdit.text())

        alg = self.algorithmWidget.value()
        typeToken = self.typeTokenWidget.value()
        strType = self.stringTypeWidget.value()

        kwargs = {'corpus':self.corpus,
                'algorithm': alg,
                'string_type':strType,
                'count_what':typeToken,
                'max_distance':max_distance}

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
            #Not implemented yet
            return
            pairs_path = self.fileWidget.value()
            if not pairs_path:
                reply = QMessageBox.critical(self,
                        "Missing information", "Please enter a file path.")
                return
            if not os.path.exists(pairs_path):
                reply = QMessageBox.critical(self,
                        "Invalid information", "The file path entered was not found.")
                return
            kwargs['query'] = read_pairs_file(pairs_path)
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
            w, nd = result
            if not isinstance(w,str):
                w = w.spelling
            if self.algorithmWidget.value() != 'khorsi':
                typetoken = 'N/A'
            else:
                typetoken = self.typeTokenWidget.value()
            self.results.append([w, nd,
                        self.stringTypeWidget.value(), typetoken,
                        self.algorithmWidget.value()])

    def khorsiSelected(self):
        self.stringTypeWidget.enable()
        self.typeTokenWidget.enable()

    def editDistSelected(self):
        self.stringTypeWidget.enable()
        self.typeTokenWidget.disable()
        self.maxDistanceEdit.setText('1')

    def phonoEditDistSelected(self):
        self.stringTypeWidget.disable()
        self.typeTokenWidget.disable()
