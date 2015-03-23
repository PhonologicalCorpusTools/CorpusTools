from .imports import *
from .windows import FunctionWorker, FunctionDialog
from .widgets import RadioSelectWidget
from .luckygui import LuckyDialog
from PyQt5.QtWidgets import QInputDialog
import itertools
import random
from collections import defaultdict, OrderedDict
from corpustools.mutualinfo import mutual_information

class AutoAnalysisError(Exception):
    pass

class AutoWorker(FunctionWorker):

    def __init__(self):
        super().__init__()

class AutoDialog(QDialog):

    header = ''

    _about = ''

    name = 'Phonological pattern finding'

    def __init__(self, parent, corpusModel, showToolTips):
        QDialog.__init__(self, parent)#, AutoWorker())
        self.corpusModel = corpusModel
        self.showToolTips = showToolTips
        self.results = list()
        self.setWindowTitle('Look for phonological patterns')
        self.layout = QHBoxLayout()
        #self.layout.addWidget(QLabel('Select a phonological pattern'))

        algEnabled = {'Vowel harmony':self.corpusModel.corpus.has_transcription,
                    'Syllable shape':self.corpusModel.corpus.has_transcription,
                    'Random analysis':self.corpusModel.corpus.has_transcription}

        self.algorithmWidget = RadioSelectWidget('Which pattern do you want to look for?',
                                            OrderedDict([('Vowel harmony','vowel_harmony'),
                                            ('Syllable shape','syllables'),
                                            ('Random analysis','random')]),
                                            # {'Vowel harmony':self.vowelHarmonySelected,
                                            # 'Syllable shape':self.syllableShapeSelected,
                                            # 'Random analysis':self.randomAnalysisSelected},
                                            enabled=algEnabled)


        self.layout.addWidget(self.algorithmWidget)


        # self.vowelHarmonyLayout = QVBoxLayout()
        # self.vowelHarmonyButton = QRadioButton()
        # self.vowelHarmonyButton.toggle()
        # self.vowelHarmonyButton.setText(('Search for vowel harmony.'
        #                             ' Enter the distinctive feature for vowels. This is usually something like '
        #                             '+voc or +vocalic.\nYou can check your feature system under the Feature menu'))
        # self.vowelFeatureEntry = QLineEdit()
        #
        # self.vowelHarmonyLayout.addWidget(self.vowelHarmonyButton)
        # self.vowelHarmonyLayout.addWidget(self.vowelFeatureEntry)
        # self.layout.addLayout(self.vowelHarmonyLayout)
        #
        #
        self.buttonBox = QHBoxLayout()
        self.okButton = QPushButton('OK')
        self.okButton.clicked.connect(self.calc)
        self.buttonBox.addWidget(self.okButton)
        self.cancelButton = QPushButton('Cancel')
        self.cancelButton.clicked.connect(self.reject)
        self.buttonBox.addWidget(self.okButton)
        self.buttonBox.addWidget(self.cancelButton)
        self.layout.addLayout(self.buttonBox)
        self.setLayout(self.layout)

    def calc(self):
        if self.algorithmWidget.value() == 'vowel_harmony':
            self.doVowelHarmony()
        elif self.algorithmWidget.value() == 'syllables':
            self.doSyllableShapes()
        elif self.algorithmWidget.value() == 'random':
            self.doRandomAnalysis()

    def doSyllableShapes(self):
        nucleus = QInputDialog.getText(self, 'Syllable shapes', 'Which feature represents a syllable nucleus?')
        nucleus = nucleus[0].lstrip('[').rstrip(']')
        if not self.corpusHasFeature(nucleus):
            return

        onsets = list()
        medials = list()
        codas = list()
        sign = nucleus[0]
        name = nucleus[1:]

        for word in self.corpusModel.corpus:
            first_pos = 0
            last_pos = len(word.transcription)
            cur_onset = list()
            cur_coda = list()
            cur_medial = list()
            for pos,seg in word.enumerate_symbols('transcription'):
                seg = self.corpusModel.corpus.specifier[seg]
                if not seg.features[name] == sign:
                    cur_onset.append(seg)
                else:
                    if not cur_onset in onsets:
                        onsets.append(cur_onset)
                    first_pos = pos
                    break

            for pos in reversed(range(len(word.transcription))): #reversed(word.transcription)
                seg = self.corpusModel.corpus.specifier[word.transcription[pos]]
                if not seg.features[name] == sign:
                    cur_coda.append(seg)
                else:
                    if not cur_coda in codas:
                        codas.append(cur_coda)
                    last_pos = pos
                    break

            print(first_pos, last_pos)
            for pos in range(first_pos,last_pos):
                seg = self.corpusModel.corpus.specifier[word.transcription[pos]]
                print(seg)
                if not seg.features[name] == sign:
                    cur_medial.append(seg)
                else:
                    if not cur_medial in medials:
                        medials.append(cur_medial)
                    cur_medial = list()


        print(onsets)
        print(medials)
        print(codas)




    def doRandomAnalysis(self):
        analysis = random.choice(['string_similarity', 'functional_load', 'phonotactic_probability', 'kullback_leibler'])
        kwargs = {'corpus': self.corpusModel.corpus}

        if 'string_similarity' == analysis:
            kwargs['algorithm'] = random.choice(['khorsi', 'edit_distance'])
            kwargs['query'] = self.corpusModel.corpus.random_word()
        elif 'functional_load' == analysis:
            segpair = random.sample(self.corpusModel.corpus.inventory,2)
            kwargs['segment_pair'] = [segpair[0].symbol, segpair[1].symbol]
        elif 'phonotactic_probability' == analysis:
            kwargs['query'] = self.corpusModel.corpus.random_word()
            kwargs['sequence_type'] = 'transcription'
            kwargs['probability_type'] = random.choice(['unigram', 'bigram'])
        elif 'kullback_leibler' == analysis:
            segpair = random.sample(self.corpusModel.corpus.inventory,2)
            kwargs['seg1'] = segpair[0]
            kwargs['seg2'] = segpair[1]
            kwargs['side'] = random.choice(['lhs', 'rhs', 'both'])

        self.luckyresults = LuckyDialog(self,analysis,kwargs)
        self.luckyresults.calc()
        self.luckyresults.show()

    def corpusHasFeature(self,feature):

        has_sign = True if feature.startswith('+') or feature.startswith('-') else False
        if not has_sign:
            msg = QMessageBox()
            msg.setWindowTitle('Warning')
            msg.setText('You need to indicate +{0} or -{0}'.format(feature))
            msg.exec_()

        elif not feature[1:] in self.corpusModel.corpus.get_features():
            msg = QMessageBox()
            msg.setWindowTitle('Warning')
            msg.setText('Could not find the feature {}'.format(feature))
            msg.exec_()

        return has_sign

    def doVowelHarmony(self):

        text = QInputDialog.getText(self, 'Vowel harmony', 'Which feature is unique to vowels? In SPE this is [+voc]')
        text = text[0].lstrip('[').rstrip(']')
        if not self.corpusHasFeature(text):
            return

        self.corpusModel.corpus.add_tier('AutoGeneratedVowels',text)

        inventory = [seg for seg in self.corpusModel.corpus.inventory if seg.features[text[1:]]==text[0]]
        probs = defaultdict(list)
        for pair in itertools.product(inventory,repeat=2):
            pair = (pair[0].symbol, pair[1].symbol)
            try:
                mi = mutual_information.pointwise_mi(self.corpusModel.corpus, pair, 'AutoGeneratedVowels')
                probs[pair[0]].append( (pair[1], mi) )
            except mutual_information.MutualInformationError:
                probs[pair[0]].append( (pair[1], '*') )

        harmonic_features = ['high', 'back', 'round']
        for feature in harmonic_features:
            plus = [seg for seg in inventory if seg.features[feature]=='+']
            minus = [seg for seg in inventory if not seg in plus]
            avg_pp_mi = list()
            avg_pm_mi = list()
            avg_mm_mi = list()
            avg_mp_mi = list()
            for seg in inventory:
                for seg2,mi in probs[seg.symbol]:
                    if mi == '*':
                        continue
                    seg2 = self.corpusModel.corpus.symbol_to_segment(seg2)
                    seg2_sign = seg.features[feature]
                    if seg in plus:
                        if seg2_sign == '+':
                            avg_pp_mi.append(mi)
                        else:
                            avg_pm_mi.append(mi)
                    elif seg in minus:
                        if seg2_sign == '-':
                            avg_mm_mi.append(mi)
                        else:
                            avg_mp_mi.append(mi)
            avg_pp_mi = sum(avg_pp_mi)/len(avg_pp_mi) if len(avg_pp_mi) else 'N/A'
            avg_pm_mi = sum(avg_pm_mi)/len(avg_pm_mi) if len(avg_pm_mi) else 'N/A'
            avg_mm_mi = sum(avg_mm_mi)/len(avg_mm_mi) if len(avg_mm_mi) else 'N/A'
            avg_mp_mi = sum(avg_mp_mi)/len(avg_mp_mi) if len(avg_mp_mi) else 'N/A'
            self.results.append([avg_pp_mi, avg_pm_mi])
            self.results.append([avg_mm_mi, avg_mp_mi])
            #self.results.append(avg_pm_mi)
            #self.results.append(avg_mm_mi)
            #self.results.append(avg_mp_mi)
            print('Average [+{0}][+{0}] MI = {1}'.format(feature, avg_pp_mi))
            print('Average [+{0}][-{0}] MI = {1}'.format(feature, avg_pm_mi))
            print('Average [-{0}][-{0}] MI = {1}'.format(feature, avg_mm_mi))
            print('Average [-{0}][+{0}] MI = {1}'.format(feature, avg_mp_mi))


        self.corpusModel.corpus.remove_attribute('AutoGeneratedVowels')
        return
