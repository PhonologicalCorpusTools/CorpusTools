import itertools
import random
from collections import defaultdict, OrderedDict

from PyQt5.QtWidgets import QInputDialog

from .imports import *
from .windows import FunctionWorker
from .widgets import RadioSelectWidget
from .luckygui import LuckyDialog
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
        self.layout = QVBoxLayout()

        algEnabled = {'Vowel harmony':self.corpusModel.corpus.has_transcription,
                    'Syllable shape':self.corpusModel.corpus.has_transcription,
                    'Random analysis':self.corpusModel.corpus.has_transcription}

        self.algorithmWidget = RadioSelectWidget('Which pattern do you want to look for?',
                                            OrderedDict([('Vowel harmony','vowel_harmony'),
                                            ('Syllable shape','syllables'),
                                            ('Random analysis','random')]),
                                            enabled=algEnabled)


        self.layout.addWidget(self.algorithmWidget)


        self.buttonBox = QHBoxLayout()
        self.okButton = QPushButton('OK')
        self.okButton.clicked.connect(self.calc)
        self.buttonBox.addWidget(self.okButton)
        self.cancelButton = QPushButton('Cancel')
        self.cancelButton.clicked.connect(self.reject)
        self.buttonBox.addWidget(self.okButton)
        self.buttonBox.addWidget(self.cancelButton)
        self.layout.addLayout(self.buttonBox)

        self.resultsLayout = QVBoxLayout()
        self.layout.addLayout(self.resultsLayout)

        self.setLayout(self.layout)

    def clearResultsLayout(self):
       while self.resultsLayout.count() > 0:
           item = self.resultsLayout.takeAt(0)
           if not item:
               continue

           w = item.widget()
           if w:
               w.deleteLater()

    def calc(self):

        self.clearResultsLayout()

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
        self.sign = nucleus[0]
        self.name = nucleus[1:]

        for word in self.corpusModel.corpus:
            first_pos = 0
            last_pos = len(word.transcription)
            cur_onset = list()
            cur_coda = list()
            cur_medial = list()
            for pos,seg in word.enumerate_symbols('transcription'):
                seg = self.corpusModel.corpus.specifier[seg]
                if not seg.features[self.name] == self.sign:
                    cur_onset.append(seg)
                else:
                    if not cur_onset in onsets:
                        onsets.append(cur_onset)
                    first_pos = pos
                    break

            for pos in reversed(range(len(word.transcription))):
                seg = self.corpusModel.corpus.specifier[word.transcription[pos]]
                if not seg.features[self.name] == self.sign:
                    cur_coda.append(seg)
                else:
                    if not cur_coda in codas:
                        codas.append(cur_coda)
                    last_pos = pos
                    break

            for pos in range(first_pos,last_pos):
                seg = self.corpusModel.corpus.specifier[word.transcription[pos]]
                if not seg.features[self.name] == self.sign:
                    cur_medial.append(seg)
                else:
                    if not cur_medial in medials:
                        medials.append(cur_medial)
                    cur_medial = list()

        # meds = [x for x in medials if x in onsets or x in codas]
        # for m in meds:
        #     if len(m) == 1:
        #         if len(codas)==1 and codas[0]==[]: #no coda
        #             onsets.append(codas[0])#this must be an onset
        #
        #     m = reversed(m)
        #     cur_string = list()
        #     for seg in m:
        #         cur_string.append(seg)
        #         if cur_string in onsets:
        #             continue

        self.outputSyllableResults(onsets, medials, codas)


    def outputSyllableResults(self,onsets,medials,codas):
        onset_patterns = self.lookForPatterns(onsets)
        onset_patterns = '\n'.join(onset_patterns)
        onsets = [''.join(o.symbol for o in ons) if ons else '\u2205' for ons in onsets]
        onsets.sort()
        onsets_label = QLabel('These are possible onsets in your corpus:')
        onsets_list = ','.join(onsets)
        onsets_label2 = QLabel(onsets_list)
        commentary = 'Comments:\n{}'.format(onset_patterns)
        onset_commentary = QLabel(commentary)

        coda_patterns = self.lookForPatterns(codas)
        coda_patterns = ','.join(coda_patterns)
        codas = [''.join(c.symbol for c in coda) if coda else '\u2205' for coda in codas]
        codas.sort()
        codas_label = QLabel('\n************\nThese are possible codas in your corpus:')
        codas_list = ','.join(codas)
        codas_label2 = QLabel(codas_list)
        commentary = 'Comments:\n{}'.format(coda_patterns)
        coda_commentary = QLabel(commentary)


        self.resultsLayout.addWidget(onsets_label)
        self.resultsLayout.addWidget(onsets_label2)
        self.resultsLayout.addWidget(onset_commentary)
        self.resultsLayout.addWidget(codas_label)
        self.resultsLayout.addWidget(codas_label2)
        self.resultsLayout.addWidget(coda_commentary)

    def lookForPatterns(self, seg_list):

        #look for a few common patterns
        #this assumes certain features, but it won't necessarily work across all feature systems
        text = list()

        ########empty list?
        if len(seg_list)==1 and seg_list[0] == []:
            text.append('No segments are allowed in this position')
            return text


        ##########check for obstruents
        for segs in seg_list:
            if not all(seg.feature_match('-son') for seg in segs):
                obstruents = False
        else:
                obstruents = True
        if not obstruents:
            text.append('no obstruents occur here')

        #######check for nasals
        for segs in seg_list:
            if not all(seg.feature_match('-nasal') for seg in segs):
                nasals = False
        else:
            nasals = True

        if not nasals:
            text.append('no nasals occur here')

        ########check for exhaustivity
        inventory = self.corpusModel.corpus.inventory
        sign = '-' if self.sign == '+' else '+' #won't work for all feature systems
        inventory = [seg for seg in inventory if seg.feature_match(sign+self.name)]
        for segs in seg_list:
            if not all([seg in inventory for seg in segs]):
                break
        else:
            text.append('The entire inventory appears in this position')

        ########look for things all the segs have in common

        segs = self.flattenSegList(seg_list)
        feature_list = self.corpusModel.corpus.get_features()
        matches = list()
        for name in feature_list:
            sign = '+'
            feature = sign+name
            if all(seg.feature_match(feature) for seg in segs):
                matches.append(feature)
            else:
                sign = '-'
                feature = sign+name
                if all(seg.feature_match(feature) for seg in segs):
                    matches.append(feature)

        if matches:
            text.append('They have these features in common:\n{}'.format(','.join([m for m in matches])))

        ########nothing found
        if not text:
            text.append('No patterns could be found')

        text = list(set(text))

        return text

    def flattenSegList(self, seg_list):
        master_list = list()
        for segs in seg_list:
            for seg in segs:
                if seg not in master_list:
                    master_list.append(seg)
        return master_list

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
        self.harmony_feature = text
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
        commentary = list()
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
            self.resultsLayout.addWidget(QLabel('Average [+{0}][+{0}] MI = {1}'.format(feature, avg_pp_mi)))
            self.resultsLayout.addWidget(QLabel('Average [+{0}][-{0}] MI = {1}'.format(feature, avg_pm_mi)))
            self.resultsLayout.addWidget(QLabel('Average [-{0}][-{0}] MI = {1}'.format(feature, avg_mm_mi)))
            self.resultsLayout.addWidget(QLabel('Average [-{0}][+{0}] MI = {1}'.format(feature, avg_mp_mi)))
            if avg_pp_mi > avg_pm_mi and avg_mm_mi > avg_mp_mi:
                commentary.append('There might be harmony based on {}'.format(feature))

        commentary = '\n'.join([c for c in commentary])
        self.outputHarmonyResults(avg_pp_mi,avg_pm_mi,avg_mm_mi,avg_mp_mi,commentary)
        self.corpusModel.corpus.remove_attribute('AutoGeneratedVowels')
        return

    def outputHarmonyResults(self,avg_pp_mi,avg_pm_mi,avg_mm_mi,avg_mp_mi,commentary):

        # commentary = list()
        # if avg_pp_mi > avg_pm_mi:
        #     commentary.append('There might be +{} harmony'.format(self.harmony_feature[1:]))
        # if avg_mm_mi > avg_mp_mi:
        #     commentary.append('There might be -{} harmony'.format(self.harmony_feature[1:]))

        avg_pp_mi = sum(avg_pp_mi)/len(avg_pp_mi) if len(avg_pp_mi) else 'N/A'
        avg_pm_mi = sum(avg_pm_mi)/len(avg_pm_mi) if len(avg_pm_mi) else 'N/A'
        avg_mm_mi = sum(avg_mm_mi)/len(avg_mm_mi) if len(avg_mm_mi) else 'N/A'
        avg_mp_mi = sum(avg_mp_mi)/len(avg_mp_mi) if len(avg_mp_mi) else 'N/A'
        # self.results.append([avg_pp_mi, avg_pm_mi])
        # self.results.append([avg_mm_mi, avg_mp_mi])
        l1 = QLabel('Average [+{0}][+{0}] MI = {1}'.format(self.harmony_feature[1:], avg_pp_mi))
        l2 = QLabel('Average [+{0}][-{0}] MI = {1}'.format(self.harmony_feature[1:], avg_pm_mi))
        l3 = QLabel('Average [-{0}][-{0}] MI = {1}'.format(self.harmony_feature[1:], avg_mm_mi))
        l4 = QLabel('Average [-{0}][+{0}] MI = {1}'.format(self.harmony_feature[1:], avg_mp_mi))
        self.resultsLayout.addWidget(l1)
        self.resultsLayout.addWidget(l2)
        self.resultsLayout.addWidget(l3)
        self.resultsLayout.addWidget(l4)
        self.resultsLayout.addWidget(QLabel(commentary))




