#!/usr/bin/env python

import os
import random
import collections
from codecs import open


class Segment(object):
    """
    """

    def __init__(self, symbol, pos=None, master=None, feature_dict=None):
        #None defaults are for word-boundary symbols
        self.symbol = symbol
        if feature_dict is None:
            self.features = {'#':'#'}
        else:
            self.features = {feature:sign for feature,sign in feature_dict.items()}
        self.pos = pos
        self.master = master

    def get_env(self):
        """Returns the left and right hand sides of a Segment instance

        """
        if self.master is None or self.pos is None:
            return 0
        else:
            return self.master.get_env(self.pos)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.symbol

    def __eq__(self, other):
        """Two segments are considered equal if their symbol attributes match

        """
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

class FeatureMatrix(object):
    def __init__(self, name, feature_entries):
        '''
feature_entries : list of dictionaries
loaded from matrix in text file
'''
        self.name = name
        self.features = None
        self.possible_values = set()
        self.matrix = {}
        for s in feature_entries:
            if self.features is None:
                self.features = [k for k in s.keys() if k != 'symbol']
                self.features.sort()
            self.matrix[s['symbol']] = {k:v[:1] for k,v in s.items() if k != 'symbol'}
            self.possible_values.update({v for v in self.matrix[s['symbol']].values()})
    
    def validate(self):
        for v in self.possible_values:
            if v not in ['+','-']:
                default_value = v
                break
        for k,v in self.matrix.items():
            for f in self.features:
                if f not in v:
                    self.matrix[k][f] = default_value
    
    def get_name(self):
        return self.name
    
    def get_feature_list(self):
        return self.features
    
    def add_segment(self,seg,feat_spec):
        self.matrix[seg] = feat_spec
        
    def add_feature(self,feature):
        self.features.append(feature)
        self.validate()
    
    def get_segments(self):
        return list(self.matrix.keys())
        
    def get_possible_values(self):
        return self.possible_values
    
    def size(self):
        return (len(self),len(features))

    def __getitem__(self,item):
        return self.matrix[item]

    def __delitem__(self,item):
        del self.matrix[item]

    def __contains__(self,item):
        return item in self.matrix

    def __setitem__(self,key,value):
        self.matrix[key] = value

    def __len__(self):
        return len(self.matrix)
        
    def __iter__(self):
        for seg in self.matrix.keys():
            yield seg

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
            if 'spe' in filename:
                sep =','
            elif 'hayes' in filename:
                sep = '\t'
            else:
                sep = ','
            self.feature_system = encoding
##        else:
##            raise ValueError('{} is not a recognized feature system'.format(encoding))

        self.matrix = dict()
        path = os.path.join(data_directory, 'TRANS', filename)
        with open(path, encoding='utf-8', mode='r') as f:
            header = f.readline()
            header = header.split(sep)
            for line in f:
                line = line.lstrip('\ufeff')
                line = line.strip()
                if not line: #the line was blank, or just a newline character
                    continue
                symbol, features = line.split(sep, 1)

                if 'hayes' in encoding:
                    self.matrix[symbol] = [Feature(sign+header[j]) for j,sign in enumerate(features.split(sep))]

                else:# 'spe' in encoding:
                    #assume everything is formatted like the spe file, this could be changed
                    self.matrix[symbol] = [Feature(name) for name in features.split(sep)]

            self.matrix['#'] = [Feature('#')]
            self.matrix[''] = [Feature('*')]

    def get_features(self):
        """Get the list of feature names used by a feature system

        Returns
        -------
        features: list of str
            List of names of features
        """
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
    """An object representing a word in a corpus

    A Corpus object creates Words from information in a user-supplied text file.
    The names of the attributes of a Word are therefore unpredictable.

    Attributes
    ----------
    spelling : str
        A representation of a word that lacks phonological information.

    transcription : list of Segments
        A representation of a word that includes phonological information.

    tiers : list
        A list of tiers, which are created with the self.add_tier method. This
        is an empty list if not tiers have been created.

    descriptors : list of str
        A list of the names of the attributes of a Word instance. This is
        automatically generated based on the contents of the original corpus


    """

    def __init__(self, **kwargs):

        self.tiers = list()
        self.transcription = None
        kwargs = {key.lower():value for key,value in list(kwargs.items())}
        #THINGS THAT ARE STRINGS
        string_descriptors = ['spelling', 'error_msg']
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
             # setattr(self, descriptor, float(kwargs.get(descriptor)))
        if hasattr(self, 'frequency'):
            self.abs_freq = self.frequency
        elif hasattr(self, 'abs_freq'):
            self.frequency = self.abs_freq

        self.descriptors = ['spelling']
        #List and other descriptors
        custom_descriptors = [kw.lower() for kw in kwargs if (kw not in string_descriptors) and (kw not in float_descriptors)]
        for descriptor in custom_descriptors:
            if 'tier' in descriptor:
                self.tiers.append(descriptor)
                tier = kwargs.get(descriptor)
                tier = [Segment(seg,pos,self) for pos,seg in enumerate(tier)]
                setattr(self, descriptor, tier)
            elif descriptor == 'transcription':
                self.descriptors.append('transcription')
                trans = kwargs.get(descriptor)
                self.transcription = [Segment(seg,pos,self) for pos,seg in enumerate(trans)]
            else:
                setattr(self, descriptor, kwargs.get(descriptor))

        self.descriptors.extend([kw for kw in sorted(kwargs) if not kw in self.descriptors])

    def get_frequency(self):
        for f in ['frequency','abs_freq', 'freq_per_mil', 
        'lowercase_freq', 'log10_freq']:
            if f in self.descriptors:
                return f
        return 0.0

    def add_tier(self, tier_name, tier_features):
        """Adds a new tier attribute to a Word instance

        Parameters
        ----------
        tier_name : str
            User-supplied name for the new tier

        tier_features: list of str
            User-supplied list of phonological features values that define
            which segments are included in the tier

        """

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
        """Deletes a tier attribute from a Word

        Parameters
        ----------
        tier_name : str
            Name of tier attribute to be deleted.

        Notes
        ----------
        If tier_name is not a valid attribute, this function does nothing. It
        does not raise an error.

        """
        try:
            self.descriptors.remove(tier_name)
            self.tiers.remove(tier_name)
            delattr(self, tier_name)
        except ValueError:
            pass #tier_name does not exist



    def startswith(self, query):
        """Returns the first segment in the Word's string

        """
        tier = getattr(self,tier_name)
        return query == self.tier[0]

    def endswith(self, query, tier_name):
        """Returns the last segment in the Word's string

        """
        tier = getattr(self,tier_name)
        return query == tier[-1]

    def match_env(self, query, tier_name):
        """Searches for occurences of a particular environment in the word

        Parameters
        ----------
        query : Environment
            The environment to search for in the word


        Returns
        ----------
        matches : list of Envrionments
            This list is empty if no matches are found
        """

        matches = list()
        tier = getattr(self,tier_name)
        for pos,seg in enumerate(tier):
            env = self.get_env(pos, tier_name)
            if env == query:
                matches.append(env)

        return matches


    def _specify_features(self, feature_matrix):
        """
        Adds a transcription attribute to a Word, consisting of Segment objects

        Parameters
        ----------
        feature_matrix : FeatureMatrix
            Matrix of features and their values

        Notes
        ----------
        Generally, don't call this method. Consider it a "behind the scenes"
        method for making a corpus.
        """
        if self.transcription == '#':
            self.transcription = [Segment('#', None)]
        elif self.transcription is not None:
            check = self.transcription[0]
            if isinstance(check, str):
                self.transcription = [Segment(seg,
                                        pos, self,
                                        feature_matrix[seg])
                                        for pos,seg in enumerate(self.get_transcription())]
            elif isinstance(check, Segment):
                self.transcription = [Segment(seg.symbol,
                                        pos, self,
                                        feature_matrix[seg.symbol])
                                        for pos,seg in enumerate(self.get_transcription())]

    def details(self):
        """Formatted printout of a Word's attributes and their values.

        Notes
        ----------
        This is intended for debugging and interactive mode.
        """
        print('-'*25)
        for description in self.descriptors:
            print('{}: {}'.format(description, getattr(self,description)))
        print('-'*25+'\n')

    def get_env(self,pos, tier_name):
        """Get details of a particular environment in a Word

        Parameters
        ----------
        pos : int
            A position in the word, so 0<=pos<=len(self)
            
        tier_name : string
            Attribute for which tier to use in getting the environment

        Returns
        ----------
        e : Environment
            Environment of the segment at the given position in the word

        """
        tier = getattr(self,tier_name)
        if len(tier) == 1:
            lhs = Segment('#')
            rhs = Segment('#')
        elif pos == 0:
            lhs = Segment('#')
            rhs = tier[pos+1]
        elif pos == len(tier)-1:
            lhs = tier[pos-1]
            rhs = Segment('#')
        else:
            lhs = tier[pos-1]
            rhs = tier[pos+1]

        e = Environment(lhs, rhs)

        return e


    def get_spelling(self):
        return self.spelling
        
    def get_transcription(self):
        return self.transcription
        
    def get_transcription_string(self):
        return '.'.join(map(str,self.transcription))
        

    def __repr__(self):
        if self.transcription is not None:
            return "<Word object: %s /%s/>" % (self.spelling,'.'.join(map(str,self.transcription)))
        return "<Word object: %s>" % (self.spelling,)

    def __str__(self):
        return self.spelling


    def __eq__(self, other):
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

    def __len__(self):
        return len(self.spelling)



class Environment(object):

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return '_'.join([self.lhs.symbol, self.rhs.symbol])

    def __repr__(self):
        return self.__str__()

    def __eq__(self,other):
        """Two Environments are equal if they share a left AND right hand side

        """

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
        """Match left-hand environment only

        """

        l_match = False

        if not self.lhs or not other.lhs:
            #no left hand side specified, automatic match
            l_match = True
        elif self.lhs == other.lhs:
            l_match = True

        return l_match

    def __gt__(self,other):
        """Match right-hand environment only

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
    """


    def __init__(self):

        self.text2cmu = dict()
        path = os.path.join(data_directory, 'TRANS', 'cmudict.txt')
        with open(path, encoding='utf-8', mode='r') as cmu:
            for line in cmu:
                line = line.lstrip('\ufeff')
                line = line.strip()
                word, transcription = line.split(' ',1)
                transcription = transcription.strip()
                self.text2cmu[word] = [symbol for symbol in transcription.split(' ')]

        self.cmu2ipa = dict()
        path = os.path.join(data_directory, 'TRANS', 'cmu2ipa.txt')
        with open(path, encoding='utf-8', mode='r') as ipa:
            for line in ipa:
                line = line.lstrip('\ufeff')
                line = line.strip()
                cmu_symbol, ipa_symbol = line.split(',')
                self.cmu2ipa[cmu_symbol] = ipa_symbol


    def translate(self, lookup, input_type):
        """Translates from plaintext to CMU and from CMU to IPA.
        If input_type == 'text', a CMU string is returned.
        If input_type == 'cmu', a Segment object is returned.

        Parameters
        ----------

        lookup : str
            string to be translated

        input_type : str
            encoding of lookup string

        Returns
        ----------

        translation : str or Segment
            Result of translation
        """

        if input_type == 'text':
            lookup = lookup.upper()
            try:#temporary fix for while SUBTLEX still has words not in CMU
                lookup = self.text2cmu[lookup]
            except KeyError:
                return None
            translation =  self.translate(lookup, 'cmu')


        elif input_type == 'cmu':
            ipaword = [self.cmu2ipa[symbol] for symbol in lookup]
            ipaword = ''.join(ipaword)
            translation = ipaword

        return translation


class Corpus(object):
    """
    Attributes
    ----------

    name : str
        Name of the corpus, used only for easy of reference

    wordlist : dict
        Dictionary where every key is a unique string representing a word in a
        corpus, and each entry is a Word object

    specifier : FeatureSpecifier
        See the FeatureSpecifier object

    inventory : list
        list of all Segments that appear at least once in self.wordlist.values()

    orthography : list
        list of one-character strings that appear in self.wordlist.keys()

    custom : bool
        True if this is a user-supplied corpus, False if it is a built-in corpus

    feature_system : str
        Name of the feature system used for the corpus
    """

    __slots__ = ['name', 'wordlist', 'feature_matrix',
                'inventory', 'orthography', 'custom', 'feature_system',
                'has_frequency_value','has_spelling_value','has_transcription_value']

    def __init__(self, name):
        self.name = name
        self.wordlist = dict()
        self.feature_matrix = None
        self.inventory = {'#' : Segment('#')} #set of Segments, if transcription exists
        self.orthography = {'#'} #set of orthographic characters
        self.custom = False
        self.has_frequency_value = None
        self.has_spelling_value = None
        self.has_transcription_value = None
        #specifier is not passed as an argument because of how it's created
        #it's directly assigned in CorpusFactory.make_corpus()

    def iter_sort(self):
        """Sorts the keys in the corpus dictionary, then yields the values in that order

        """
        sorted_list = sorted(self.wordlist.keys())
        for word in sorted_list:
            yield self.wordlist[word]

    def get_name(self):
        return self.name
        
    def is_custom(self):
        return self.custom

    def get_feature_matrix(self):
        return self.feature_matrix
        
    def set_feature_matrix(self,matrix):
        self.feature_matrix = matrix
        
    def has_feature_matrix(self):
        return self.feature_matrix is not None

    def has_frequency(self):
        """Return True if words in the corpus have the 'frequency' label.
        """
        return self.has_frequency_value

    def has_spelling(self):
        """Return True if words in the corpus have the 'spelling' label.
        """
        return self.has_spelling_value

    def has_transcription(self):
        """Return True if words in the corpus have the 'transcription' label.
        """
        return self.has_transcription_value

    def get_inventory(self):
        inventory = list(self.inventory.values())
        inventory.sort()
        return inventory

    def get_random_subset(self, size, new_corpus_name='randomly_generated'):
        """Get a new corpus consisting a random selection from the current corpus

        Parameters
        ----------
        size : int
            Size of new corpus

        new_corpus_name : str

        Returns
        ----------
        new_corpus : Corpus
            New corpus object with len(new_corpus) == size
        """
        new_corpus = Corpus(new_corpus_name)
        while len(new_corpus) < size:
            word = self.random_word()
            new_corpus.add_word(word, allow_duplicates=False)
        new_corpus.specifier = self.specifier
        return new_corpus

    def add_word(self, word, allow_duplicates=True):
        """Add a word to the Corpus.
        If allow_duplicates is True, then words with identical spelling can
        be added. They are kept sepearate by adding a "silent" number to them
        which is never displayed to the user. If allow_duplicates is False,
        then duplicates are simply ignored.

        Parameters
        ----------
        word : Word
            Word object to be added

        allow_duplicates : bool

        """

        #If the word doesn't exist, add it
        try:
            check = self.find(word.spelling, keyerror=True)
        except KeyError:
            self.wordlist[word.spelling] = word
            if word.spelling is not None:
                self.orthography.update(word.spelling)
                if self.has_spelling_value is None:
                    self.has_spelling_value = True
            elif self.has_spelling_value is None:
                self.has_spelling_value = False
            if word.transcription is not None:
                self.inventory.update({ seg.symbol : seg for seg in word.transcription})
                if self.has_transcription_value is None:
                    self.has_transcription_value = True
            elif self.has_transcription_value is None:
                self.has_transcription_value = False
            if self.has_frequency_value is None:
                if 'frequency' in word.descriptors:
                    self.has_frequency_value = True
                else:
                    self.has_frequency_value = False
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
        """Return a randomly selected Word

        """
        word = random.choice(list(self.wordlist.keys()))
        return self.wordlist[word]

    def change_feature_system(self, feature_system):
        """Changes the feature system that is used to describe Segments

        Parameters
        ----------
        feature_system : str
            Name of a feature file that can be used to create a FeatureSpecifier

        Returns
        ----------
        errors : list
            List of segments that could not be found in the feature_system file

        Notes
        ----------
        This method is intended to be called by the GUI, and the errors list is
        printed to file for the user to inspect.

        """
        if feature_system == self.specifier.feature_system:
            #no point in doing any work in this case
            return None

        old_specifier = self.specifier
        self.specifier = FeatureSpecifier(encoding=feature_system)
        missing = [seg.symbol for seg in self.get_inventory() if not seg.symbol in list(self.specifier.matrix.keys())]

        if not missing:#all(seg.symbol in self.specifier.matrix for seg in self.inventory):
        #check first if all the transcription symbol in the corpus actually
        #appear in the Specifier. If they do, then re-specify all words
            for word in self.wordlist.keys():
                self.wordlist[word]._specify_features(self)
            errors = False

        else:
        #if there are symbols in the corpus not in the specifier, then
        #do some error logging and don't actually change the feature system
            self.specifier = old_specifier
            #missing = [seg.symbol for seg in self.inventory if not seg.symbol in self.specifier.matrix]
            #errors = collections.defaultdict(list)
            errors = {seg:list() for seg in missing}
            for key in self.wordlist.keys():
                word = [seg.symbol for seg in self.wordlist[key].transcription]
                for missing_seg in missing:
                    if missing_seg in word:
                        errors[missing_seg].append(''.join(word))

        return errors

    def get_features(self):
        """Get a list of the features used to describe Segments

        Returns
        ----------
        list of str

        """
        return self.feature_matrix.get_feature_list()

    def find(self, word, keyerror=False):
        """Search for a Word in the corpus
        If keyerror == True, then raise a KeyError if the word is not found
        If keyerror == False, then return an EmptyWord if the word is not found

        Parameters
        ----------
        word : str
            String representing the spelling of the word (not transcription)

        keyerror : bool
            Set whether a KeyError should be raised if a word is not found

        Returns
        ----------
        result : Word or EmptyWord


        Raises
        ----------
        KeyError if keyerror == True and word is not found

        """
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
    """

    def __init__(self, spelling, error_msg):
        self.error_msg = error_msg
        super().__init__(spelling=spelling, error_msg=self.error_msg)
        self._string = [letter for letter in self.spelling]

    def __len__(self):
        return 0

class CorpusFactory(object):
    """ Factory object for producing Corpus objects

    Attributes
    ----------
    basepath : User app data directory
        Used for finding the location of corpus files

    """

    essential_descriptors = ['spelling', 'transcription', 'freq']

    def __init__(self):
        self.basepath = data_directory

    def change_path(self, path):
        self.basepath = path

    def make_corpus_from_gui(self,corpus_name, features, size=100, q=None, corpusq=None):
        """ Called from GUI. Instead of returning a corpus object, it puts it
        into a Queue. This Queue is also used to update the GUI as to how
        many words have been read into the corpus.

        Parameters
        ----------
        corpus_name : str
            User-supplied name for corpus

        features : str
            Name of feature system to use (e.g. 'spe' or 'hayes')

        size : int
            Size of corpus to create.

        q : None or Queue
            queue for updating a progress bar in the GUI

        corpusq : None or Queue
            queue for putting in the final corpus


        See Also
        ----------
        The load_corpus method in corpus_gui.py
        """
        self.specifier = FeatureSpecifier(encoding=features)

        corpus_name = corpus_name.upper()
        if corpus_name == 'IPHOD':
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
        """Make a new corpus

        Parameters
        ----------
        corpus_name : str
            User-supplied name for the corpus

        features : str
            Name of feature system to use (e.g. 'spe' or 'hayes')

        size : int
            Size of the corpus


        Returns
        ----------
        corpus : Corpus
        """
        self.specifier = FeatureSpecifier(encoding=features)
        corpus = self.get_corpus_info(corpus_name, size)
        corpus.specifier = FeatureSpecifier(encoding=features)
        #new_matrix = dict()
        #for seg in self.specifier.matrix:
        #    new_matrix[seg] = {feature.name:feature.sign for feature in self.specifier.matrix[seg]}
        #corpus.specifier = new_matrix
        return corpus

    def get_corpus_info(self,corpus_name, size):
        """ Find the file for a built-in corpus, call the approprite reader method
        and then return a Corpus object.

        Parameters
        ----------
        corpus_name : str
            Name of a built-int corpus

        size : int
            Size of corpus to create

        Returns
        ----------
        corpus : Corpus

        Raises
        ----------
        ValueError if corpus_name is not a recognized built-in corpus

        Notes
        ----------
        This method is only necessary when building a corpus the first time.
        After that, it is faster to pickle the corpus and load from the pickle.
        """
        corpus_name = corpus_name.upper()

        if corpus_name == 'IPHOD':
            filename = 'IPhOD2_Words.txt'
            func = self.read_iphod

        else:
            raise ValueError('{} is not a recognizable corpus name'.format(corpus_name))

        corpus_path = os.path.join(self.basepath, corpus_name, filename)
        corpus = func(corpus_path, size)

        return corpus

    def read_iphod(self, corpus_path, max_size, q=None):
        """Create IPHOD corpus from file

        Parameters
        ----------
        corpus_path : str
            path to original IPHOD file

        max_size : int
            size of corpus

        q : None or Queue
            queue object if calling from GUI


        Returns
        ----------
        corpus : Corpus
        """
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


if __name__ == '__main__':
    factory = CorpusFactory()
    iphod = factory.make_corpus('iphod', 'spe', size=500)
    print(iphod.random_word().details())
