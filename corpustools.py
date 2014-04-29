#!/usr/bin/env python

import os
import random
import collections
from codecs import open


class Segment(object):

    def __init__(self, symbol, feature_list=None, pos=None, master=None):
        #None defaults are for word-boundary symbols
        self.symbol = symbol
        if feature_list is None:
            self.features = {'#':'#'}
        else:
            self.features = {feature.name:feature.sign for feature in feature_list}
        self.pos = pos
        self.master = master

    def get_env(self):
        if self.master is None or self.pos is None:
            return 0
        else:
            return self.master.get_env(self.pos)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.symbol

    def __eq__(self, other):
        if isinstance(other, Segment):
            return self.symbol == other.symbol
        else:
            return self.symbol == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self,other):
        if isinstance(other, Segment):
            return self.symbol < other.symbol
        else:
            return self.symbol < other

    def __le__(self,other):
        return (self.symbol == other.symbol or self.symbol < other.symbol)

    def __ge__(self,other):
        return (self.symbol == other.symbol or self.symbol > other.symbol)

    def __gt__(self,other):
        if isinstance(other, Segment):
            return self.symbol > other.symbol
        else:
            return self.symbol > other

    def __len__(self):
        return len(self.symbol)

class Feature(object):

    def __init__(self, string):
        self.sign = string[0]
        self.name = string[1:]

    def __str__(self):
        return self.sign+self.name

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.__str__() == other.__str__()

    def __ne__(self, other):
        return not self.__eq__(other)

class FeatureSpecifier(object):

    def __init__(self, encoding):

        if encoding == 'spe':
            filename = 'ipa2spe.txt'
            sep = ','
            self.feature_system = 'spe'
        elif encoding == 'hayes':
            filename = 'ipa2hayes.txt'
            sep = '\t'
            self.feature_system = 'hayes'
        else:
            filename = encoding+'.txt'
            sep=','
            self.feature_system = encoding
##        else:
##            raise ValueError('{} is not a recognized feature system'.format(encoding))

        self.matrix = dict()
        path = os.path.join(os.getcwd(), 'TRANS', filename)
        with open(path, encoding='utf-8', mode='r') as f:
            header = f.readline()
            header = header.split(sep)
            for line in f:
                line = line.lstrip('\ufeff')
                line = line.strip()
                if not line: #the line was blank, or just a newline character
                    continue
                symbol, features = line.split(sep, 1)

                if encoding == 'hayes':
                    self.matrix[symbol] = [Feature(sign+header[j]) for j,sign in enumerate(features.split(sep))]
                #if encoding == 'spe':
                else:
                    #assume everything is formatted like the spe file, this could be changed
                    self.matrix[symbol] = [Feature(name) for name in features.split(sep)]

            self.matrix['#'] = [Feature('#')]
            self.matrix[''] = [Feature('*')]

    def get_features(self):
        symbol = random.choice(list(self.matrix.keys()))
        features = [feature.name for feature in self.matrix[symbol]]
        features.sort()
        return features

    def __getitem__(self,item):
        return self.matrix[item]

    def __contains__(self,item):
        return item in list(self.matrix.keys())

    def __setitem__(self,key,value):
        self.matrix[key] = value

    def __len__(self):
        return len(self.matrix)

class Word(object):

    def __init__(self, **kwargs):

        self.tiers = list()

        #THINGS THAT ARE STRINGS
        string_descriptors = ['spelling', 'transcription', 'error_msg']
        for descriptor in string_descriptors:
            setattr(self, descriptor, kwargs.get(descriptor))

        #THINGS THAT ARE NUMBERS
        float_descriptors = ['abs_freq', 'syl_length', 'freq_per_mil', 'phone_length',
        'lowercase_freq', 'log10_freq', 'frequency']
        for descriptor in float_descriptors:
            try:
                setattr(self, descriptor, float(kwargs.get(descriptor)))
            except TypeError:
                pass
            #if getattr(self, descriptor) is not None:
             #   setattr(self, descriptor, float(kwargs.get(descriptor)))
        if hasattr(self, 'frequency'):
            self.abs_freq = self.frequency
        elif hasattr(self, 'abs_freq'):
            self.frequency = self.abs_freq

        #CUSTOM DESCRIPTORS. STRINGS BY NECESSITY
        custom_descriptors = [kw for kw in kwargs if (kw not in string_descriptors) and (kw not in float_descriptors)]
        for descriptor in custom_descriptors:
            if 'tier' in descriptor:
                #descriptor = descriptor.split('(')[0].strip()
                self.tiers.append(descriptor)
                tier = kwargs.get(descriptor)
                #print(descriptor, tier, type(tier))
                tier.strip('[]')
                tier = tier.split('.')
                setattr(self, descriptor, tier)
            else:
                setattr(self, descriptor, kwargs.get(descriptor))


        self.descriptors = ['spelling']
        if self.transcription is not None:
            self.descriptors.append('transcription')

        self.descriptors.extend([kw for kw in sorted(kwargs) if not kw in self.descriptors])

        if self.transcription is not None:
            self._string = self.transcription
        else:
            self._string = self.spelling

    def add_tier(self, tier_name, tier_features):

        new_tier = list()
        #tier_features = {feature[1:]:feature[0] for feature in tier_features}
        for seg in self.transcription:
            if all(seg.features[feature[1:]]==feature[0] for feature in tier_features):
                new_tier.append(seg)
        if new_tier:
            for pos,seg in enumerate(new_tier):
                seg.pos = pos
                seg.master = self
            #self.tiers[name] = new_tier
            setattr(self,tier_name,new_tier)
        else:
            #self.tiers[name] = list()
            setattr(self,tier_name,new_tier)

        self.descriptors.append(tier_name)
        self.tiers.append(tier_name)

    def remove_tier(self, tier_name):
        try:
            self.descriptors.remove(tier_name)
            self.tiers.remove(tier_name)
            delattr(self, tier_name)
        except ValueError:
            pass #tier_name does not exist



    def startswith(self, query):
        return query == self._string[0]

    def endswith(self, query):
        return query == self._string[-1]

    def match_env(self, query):

        matches = list()

        for pos,seg in enumerate(self.string):
            env = self.get_env(pos)
            if env == query:
                matches.append(env)

        return matches


    def _specify_features(self, caller):
        """
        This is called by a CorpusFactory and is for creating a transcription
        consisting of Segment objects that have more detailed phonological
        information.
        The caller argument must be an object that has an attribute called
        'specifier' which is a FeatureSpecifier object
        Generally, don't call this method. Consider it a "behind the scenes"
        method for making a corpus
        """
        if self.transcription is None:
            #handles cases where no transcription is found in the CMU dictionary
            self._string = [letter for letter in self.spelling]
        elif self.transcription == '#':
            self.transcription = [Segment('#', None)]
        else:
            check = self.transcription[0]
            if isinstance(check, str):
                self.transcription = [Segment(seg,
                                        caller.specifier[seg],
                                        pos, self)
                                        for pos,seg in enumerate(self.transcription)]
            elif isinstance(check, Segment):
                self.transcription = [Segment(seg.symbol,
                                        caller.specifier[seg.symbol],
                                        pos, self)
                                        for pos,seg in enumerate(self.transcription)]

        #self._string = self.transcription

    def details(self):
        print('-'*25)
        for description in self.descriptors:
            print('{}: {}'.format(description, getattr(self,description)))
        print('-'*25+'\n')

    def transcribe(self):

        if self.transcription:
            return ''.join([seg for seg in self.transcription])
        else:
            return self.spelling

    def get_env(self,pos):
        if len(self) == 1:
            lhs = Segment('#')
            rhs = Segment('#')
        elif pos == 0:
            lhs = Segment('#')
            rhs = self[pos+1]
        elif pos == len(self)-1:
            lhs = self[pos-1]
            rhs = Segment('#')
        else:
            lhs = self[pos-1]
            rhs = self[pos+1]

        return Environment(lhs, rhs)


    def set_string(self, attr):
        new_string = getattr(self, attr, None)
        if new_string is None:
            msg = 'cannot assign {} to string, no value was found'.format(attr)
            raise ValueError(msg)
        else:
            self._string = new_string

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        #returning self._string is problematic, because sometimes it's a list
        #and print functions don't like that, and raise a TypeError
        if not type(self._string) == str:
            return ''.join([str(x) for x in self._string])
        return self._string


    def __eq__(self, other):
        #return self._string == other._string
        return self.spelling == other.spelling

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.spelling < other.spelling

    def __gt__(self, other):
        return self.spelling > other.spelling

    def __le__(self, other):
        return self.spelling <= other.spelling

    def __ge__(self, other):
        return self.spelling >= other.spelling

    def __contains__(self,item):
        return item in [seg for seg in self._string]
        #return item in [letter for letter in self.spelling]

    def __len__(self):
        return len(self._string)

    def __getitem__(self,key):
        if not isinstance(key,int):
            raise TypeError('index must be an integer')
        else:
            return self._string[key]

    def __setitem__(self,key,value):
        if not isinstance(key,int):
            raise TypeError('index must be an integer')
        self._string[key] = value

    def __iter__(self):
        for seg in self._string:
            yield seg


class Environment(object):

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return '_'.join([self.lhs.symbol, self.rhs.symbol])

    def __repr__(self):
        return self.__str__()

    def __eq__(self,other):

        l_match = False
        r_match = False

        if not self.lhs or not other.lhs:
            #no left hand side specified, automatic match
            l_match = True
        elif self.lhs == other.lhs:
            l_match = True

        if not self.rhs or not other.rhs:
            #no right hand side specified, automatic match
            r_match = True
        elif self.rhs == other.rhs:
            r_match = True

        return l_match and r_match

    def __lt__(self,other):
        """
        Match left-hand environment only
        """

        l_match = False

        if not self.lhs or not other.lhs:
            #no left hand side specified, automatic match
            l_match = True
        elif self.lhs == other.lhs:
            l_match = True

        return l_match

    def __gt__(self,other):
        """
        Match right-hand environment only
        """

        r_match = False

        if not self.rhs or not other.rhs:
            #no left hand side specified, automatic match
            r_match = True
        elif self.rhs == other.rhs:
            r_match = True

        return r_match


    def __ne__(self,other):
        return not self.__eq__(other)



class Translator(object):
    """
    Translates from plaintext to CMU and from CMU to IPA
    """


    def __init__(self):

        self.text2cmu = dict()
        path = os.path.join(os.getcwd(), 'TRANS', 'cmudict.txt')
        with open(path, encoding='utf-8', mode='r') as cmu:
            for line in cmu:
                line = line.lstrip('\ufeff')
                line = line.strip()
                word, transcription = line.split(' ',1)
                transcription = transcription.strip()
                self.text2cmu[word] = [symbol for symbol in transcription.split(' ')]

        self.cmu2ipa = dict()
        path = os.path.join(os.getcwd(), 'TRANS', 'cmu2ipa.txt')
        with open(path, encoding='utf-8', mode='r') as ipa:
            for line in ipa:
                line = line.lstrip('\ufeff')
                line = line.strip()
                cmu_symbol, ipa_symbol = line.split(',')
                self.cmu2ipa[cmu_symbol] = ipa_symbol


    def translate(self, lookup, input_type):


        if input_type == 'text':
            lookup = lookup.upper()
            try:#temporary fix for while SUBTLEX still has words not in CMU
                lookup = self.text2cmu[lookup]
            except KeyError:
                return None
            return self.translate(lookup, 'cmu')


        elif input_type == 'cmu':
            ipaword = [self.cmu2ipa[symbol] for symbol in lookup]
            ipaword = ''.join(ipaword)
            return ipaword


class Corpus(object):

    __slots__ = ['name', 'wordlist', 'specifier',
                'inventory', 'orthography', 'custom', 'feature_system']

    def __init__(self, name):
        self.name = name
        self.wordlist = dict()
        self.specifier = None
        self.inventory = list() #list of Segments, if transcription exists
        self.orthography = list() #lists of orthographic characters
        self.custom = False
        #specifier is not passed as an argument because of how it's created
        #it's directly assigned in CorpusFactory.make_corpus()

    def iter_sort(self):
        """
        Sorts the keys in the corpus dictionary, then yields the values in that
        order
        """
        sorted_list = sorted(self.wordlist.keys())
        for word in sorted_list:
            yield self.wordlist[word]

    def get_random_subset(self, size):
        new_corpus = Corpus('new_corpus')
        while len(new_corpus) < size:
            word = self.random_word()
            new_corpus.add_word(word, allow_duplicates=False)
        return new_corpus

    def add_word(self, word, allow_duplicates=True):

        #If the word doesn't exist, add it
        try:
            check = self.find(word.spelling, keyerror=True)
        except KeyError:
        #if isinstance(check, EmptyWord):
            #self.wordlist[word.spelling.lower()] = word
            self.wordlist[word.spelling] = word
            return

        if allow_duplicates:
            #Some words have more than one entry in a corpus, e.g. "live" and "live"
            #so they need to be assigned unique keys

            n = 0
            while True:
                n += 1
                #key = '{} ({})'.format(word.spelling.lower(),n)
                key = '{} ({})'.format(word.spelling,n)
                try:
                    check = self.find(key, keyerror=True)
                except KeyError:
                #if isinstance(check, EmptyWord):
                    self.wordlist[key] = word
                    break

    def random_word(self):
        word = random.choice(list(self.wordlist.keys()))
        return self.wordlist[word]

    def change_feature_system(self, feature_system):
        self.specifier = FeatureSpecifier(encoding=feature_system)
        errors = collections.defaultdict(list)

        if all(seg.symbol in self.specifier.matrix for seg in self.inventory):
        #check first if all the transcription symbol in the corpus actually
        #appear in the Specifier. If they do, then re-specify all words
            for word in self.wordlist.keys():
                self.wordlist[word]._specify_features(self)


        else:
        #if there are symbols in the corpus not in the specifier, then
        #do some error logging and don't actually change the feature system
            for word in self.wordlist.keys():
                try:
                    #self.wordlist[key]._specify_features(self)
                    test = [self.specifier[w.symbol] for w in self.wordlist[word]]
                except KeyError as e:
                    errors[str(e)].append(''.join(seg.symbol for seg in self.wordlist[word].transcription))


        return errors

    def get_features(self):
        return self.specifier.get_features()

    def find(self, word, keyerror=False):
        #word = word.lower()
        try:
            result = self.wordlist[word]
        except KeyError:
            try:
                key = '{} (1)'.format(word)
                result = self.wordlist[key]
            except KeyError:
                if keyerror:
                    raise KeyError('The word \"{}\" is not in the corpus'.format(word))
                else:
                    result = EmptyWord(word, 'Word could not be found in the corpus')

        return result

    def __contains__(self,item):
        return self.wordlist.__contains__(item)

    def __len__(self):
        return len(self.wordlist)

    def __setitem__(self,item,value):
        self.wordlist[item] = value

    def __getitem__(self,item):
        return self.wordlist[item]

    def __iter__(self):
        return iter(self.wordlist.values())


class EmptyWord(Word):
    """
    Returned when nothing can be found in the corpus
    """

    def __init__(self, spelling, error_msg):
        self.error_msg = error_msg
        super().__init__(spelling=spelling, error_msg=self.error_msg)
        self._string = [letter for letter in self.spelling]

    def __len__(self):
        return 0

class CorpusFactory(object):
    """
    Reads a file and returns a corpus object
    """

    essential_descriptors = ['spelling', 'transcription', 'freq']

    def __init__(self):
        self.basepath = os.getcwd()

    def change_path(self, path):
        self.basepath = path

    def make_corpus_from_gui(self, corpus_name, features, size=100, q=None, corpusq=None):
        """
        Called from GUI. Instead of returning a corpus object, it puts it
        into a Queue. This Queue is also used to update the GUI as to how
        many words have been read into the corpus
        """
        self.specifier = FeatureSpecifier(encoding=features)

        corpus_name = corpus_name.upper()
        if corpus_name == 'SUBTLEX':
            filename = 'SUBTLEXus_74286_words.txt'
            func = self.read_subtlex
        elif corpus_name == 'IPHOD':
            filename = 'IPhOD2_Words.txt'
            func = self.read_iphod
        else:
            raise ValueError('{} is not a recognizable corpus name'.format(corpus_name))

        corpus_path = os.path.join(self.basepath, corpus_name, filename)
        corpus = func(corpus_path, size, q)
        q.put('done')

        corpus.specifier = FeatureSpecifier(encoding=features)

        corpusq.put(corpus)
        return

    def make_corpus(self,corpus_name, features, size=100):
        self.specifier = FeatureSpecifier(encoding=features)
        corpus = self.get_corpus_info(corpus_name, size)
        corpus.specifier = FeatureSpecifier(encoding=features)
        #new_matrix = dict()
        #for seg in self.specifier.matrix:
        #    new_matrix[seg] = {feature.name:feature.sign for feature in self.specifier.matrix[seg]}
        #corpus.specifier = new_matrix
        return corpus

    def get_corpus_info(self,corpus_name, size):
        """
        Find the appropriate corpus file, call the approprite reader method
        and then return a Corpus object.
        """
        corpus_name = corpus_name.upper()

        if corpus_name == 'SUBTLEX':
            filename = 'SUBTLEXus_74286_words.txt'
            func = self.read_subtlex

        elif corpus_name == 'IPHOD':
            filename = 'IPhOD2_Words.txt'
            func = self.read_iphod

        else:
            raise ValueError('{} is not a recognizable corpus name'.format(corpus_name))

        corpus_path = os.path.join(self.basepath, corpus_name, filename)
        corpus = func(corpus_path, size)

        return corpus

    def read_subtlex(self, corpus_path, max_size, q=None):
        corpus = Corpus('subtlex')
        translator = Translator()
        with open(corpus_path, encoding='utf-8') as f:
            headers = f.readline()
            headers = headers.split()
            counter = 0
            for line in f:
                d = {attribute:value for attribute,value in zip(headers,line.split())}
                transcription = translator.translate(d['Word'], 'text')
                word = Word(spelling=d['Word'], abs_freq=d['FREQcount'], freq_per_mil=d['SUBTLWF'],
                lowercase_freq=d['Cdlow'], log10_freq=d['Lg10WF'], transcription=transcription)
                word._specify_features(self)
                for letter in word.spelling:
                    if letter not in corpus.orthography:
                        corpus.orthography.append(letter)
                if transcription is not None:
                    for seg in word.transcription:
                        if seg not in corpus.inventory:
                            corpus.inventory.append(seg)
                    corpus.add_word(word)
                counter += 1
                if q is not None:
                    q.put(counter)
                if counter == max_size:
                    break

        corpus.orthography.append('#')
        corpus.inventory.append(Segment('#'))
        return corpus

    def read_iphod(self, corpus_path, max_size, q=None):
        corpus = Corpus('iphod')
        translator = Translator()
        with open(corpus_path, encoding='utf-8') as f:
            headers = f.readline()
            headers = headers.split()
            counter = 0
            for line in f:
                d = {attribute:value for attribute,value in zip(headers,line.split())}
                transcription = translator.translate(d['UnTrn'].split('.'), 'cmu')
                word = Word(spelling=d['Word'], transcription=transcription, freq_per_mil=d['SFreq'],
                syl_length=d['NSyll'], phone_length=d['NPhon'])
                word._specify_features(self)
                corpus.add_word(word)
                for letter in word.spelling:
                    if letter not in corpus.orthography:
                        corpus.orthography.append(letter)
                for seg in word.transcription:
                    if seg not in corpus.inventory:
                        corpus.inventory.append(seg)
                counter += 1
                if q is not None:
                    q.put(counter)
                if counter == max_size:
                    break

        corpus.orthography.append('#')
        corpus.inventory.append(Segment('#'))
        return corpus

    def read_swahili(self, corpus_path):
        corpus = Corpus('swahili')
        translator = Translator()
        with open(corpus_path, encoding='utf-8') as f:
            headers = f.readline()
            headers = headers.split()
            counter = 0
            for line in f:
                d = {attribute:value for attribute,value in zip(headers,line.split())}
                #transcription = translator.translate(d['UnTrn'].split('.'), 'cmu')
                word = Word(spelling=d['Spelling'], transcription=d['Transcription'], freq_per_mil=d['SFreq'],
                syl_length=d['NSyll'], phone_length=d['NPhon'])
                word._specify_features(self)
                corpus.add_word(word)
                for letter in word.spelling:
                    if letter not in corpus.orthography:
                        corpus.orthography.append(letter)
                for seg in word.transcription:
                    if seg not in corpus.inventory:
                        corpus.inventory.append(seg)
                counter += 1
                if q is not None:
                    q.put(counter)
                if counter == max_size:
                    break

        corpus.orthography.append('#')
        corpus.inventory.append(Segment('#'))
        return corpus

if __name__ == '__main__':
    pass
