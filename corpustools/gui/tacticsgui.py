from .imports import *
from .windows import FunctionWorker, FunctionDialog
from .widgets import FeatureCompleter, FeatureEdit, ContextWidget, TierWidget
from corpustools.contextmanagers import (CanonicalVariantContext,
                                         MostFrequentVariantContext,
                                         SeparatedTokensVariantContext,
                                         WeightedVariantContext)

class TacticsWorker(FunctionWorker):

    def __init__(self):
        super().__init__()

class TacticsDialog(QDialog):
    header = ''

    _about = ''

    name = 'Phonotactic inference'


    def __init__(self,parent, corpus, inventory, settings, showToolTips):
        super().__init__(parent)#, settings, TacticsWorker())
        self.corpus = corpus
        self.inventory = inventory
        self.settings = settings
        self.showToolTips = showToolTips

        layout = QVBoxLayout()

        nucleusLayout = QHBoxLayout()
        nucleusLayout.addWidget(QLabel('What feature defines a syllable nucleus?'))
        self.nucleusEdit = FeatureEdit(self.inventory)
        consCompleter = FeatureCompleter(self.inventory)
        self.nucleusEdit.setCompleter(consCompleter)
        if self.inventory.vowel_features is not None:
            self.nucleusEdit.setText(self.inventory.vowel_features[0])
        nucleusLayout.addWidget(self.nucleusEdit)
        layout.addLayout(nucleusLayout)

        parseTypeLayout = QHBoxLayout()
        parseTypeLayout.addWidget(QLabel('Select a parsing strategy:'))
        self.parseTypeRadio = QRadioButton('Onset Maximization')
        parseTypeLayout.addWidget(self.parseTypeRadio)
        layout.addLayout(parseTypeLayout)

        self.variantsWidget = ContextWidget(self.corpus, None)
        layout.addWidget(self.variantsWidget)

        self.tierWidget = TierWidget(corpus, include_spelling=False)
        layout.addWidget(self.tierWidget)

        buttonLayout = QHBoxLayout()
        ok = QPushButton('OK')
        buttonLayout.addWidget(ok)
        ok.clicked.connect(self.findSyllableShapes)
        cancel = QPushButton('Cancel')
        buttonLayout.addWidget(cancel)
        cancel.clicked.connect(self.reject)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)

    def generateKwargs(self, *args):
        kwargs = dict()
        kwargs['corpus'] = self.corpus
        nucleus = self.nucleusEdit.text().strip()
        nucleus_name = nucleus[1:]
        nucleus_sign = nucleus[0]
        kwargs['nucleus'] = nucleus
        kwargs['type_token'] = 'type'
        kwargs['sequence_type'] = self.tierWidget.value()
        kwargs['context'] = self.variantsWidget.value()
        return kwargs

    def findSyllableShapes(self):
        self.parseCorpus()

        max_onset = max([len(o) for o in self.onsets])
        max_coda = max([len(c) for c in self.codas])
        onset_string = 'C'*max_onset
        coda_string = 'C'*max_coda

        self.onsets = [o if o else ['EMPTY'] for o in self.onsets ]
        self.codas = [c if c else ['EMPTY'] for c in self.codas]

        print('The biggest possible syllable has the shape {}V{}'.format(onset_string, coda_string))
        print('Onsets: ')
        print(','.join([''.join(o) for o in self.onsets]))
        print('Codas: ')
        print(','.join([''.join(c) for c in self.codas]))

    def parseCorpus(self):

        kwargs = self.generateKwargs()

        self.onsets = list()
        self.medials = list()
        self.codas = list()

        context = kwargs.pop('context')
        nucleus = kwargs['nucleus']
        nucleus_name = nucleus[1:]
        nucleus_sign = nucleus[0]
        tier = kwargs['sequence_type']

        if context == ContextWidget.canonical_value:
            cm = CanonicalVariantContext
        elif context == ContextWidget.frequent_value:
            cm = MostFrequentVariantContext
        elif context == ContextWidget.separate_value:
            cm = SeparatedTokensVariantContext
        elif context == ContextWidget.relative_value:
            cm = WeightedVariantContext

        with cm(kwargs['corpus'], kwargs['sequence_type'], kwargs['type_token']) as corpus:
            for word in corpus:
                last_pos = word.get_len(tier)
                first_pos = 0
                cur_onset = list()
                cur_coda = list()
                cur_medial = list()
                #go left to right, gather onsets
                for pos, seg in word.enumerate_symbols(tier):
                    features = self.inventory.segs[seg].features
                    if not features[nucleus_name] == nucleus_sign:
                        cur_onset.append(seg)
                    else:
                        if not cur_onset in self.onsets:
                            self.onsets.append(cur_onset)
                        first_pos = pos
                        break

                #go right to left, add remains to codas
                for pos, seg in word.enumerate_symbols(tier, reversed=True):
                    features = self.inventory.segs[seg].features
                    if not features[nucleus_name] == nucleus_sign:
                        cur_coda.append(seg)
                    else:
                        if not cur_coda in self.codas:
                            self.codas.append(cur_coda)
                        last_pos = pos
                        break

            # for pos in range(first_pos, last_pos):
            #     seg = word[pos]
            #     features = self.inventory.segs[seg].features
            #     if not seg.features[nucleus_name] == nucleus_sign:
            #         cur_medial.append(seg)
            #     else:
            #         if not cur_medial in self.medials:
            #             self.medials.append(cur_medial)
            #         cur_medial = list()

        # meds = [x for x in medials if x in onsets or x in codas]
        # for m in meds:
        # if len(m) == 1:
        #         if len(codas)==1 and codas[0]==[]: #no coda
        #             onsets.append(codas[0])#this must be an onset
        #
        #     m = reversed(m)
        #     cur_string = list()
        #     for seg in m:
        #         cur_string.append(seg)
        #         if cur_string in onsets:
        #             continue


    def accept(self):
        QDialog.accept(self)

    def reject(self):
        QDialog.reject(self)