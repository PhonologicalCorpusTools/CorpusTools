#!/usr/bin/env python

import os
import random
import collections

class CorpusIntegrityError(Exception):
    pass

class Segment(object):
    """
    """

    def __init__(self, symbol):
        #None defaults are for word-boundary symbols
        self.symbol = symbol
        self.features = dict()

    def specify(self,feature_dict):
        self.features = feature_dict

    def feature_match(self,specification):
        for f in specification:
            try:
                if self.features[f[1:]]!=f[0]:
                    return False
            except KeyError:
                return False
        return True

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

class Transcription(object):
    def __init__(self,seg_list):
        self._list = seg_list

    def __getitem__(self, key):
        if isinstance(key,int):
            return self._list[key]
        raise(KeyError)

    def __str__(self):
        return '.'.join(self._list)

    def __iter__(self):
        for s in self._list:
            yield s

    def __eq__(self, other):
        if not isinstance(other, Transcription) and not isinstance(other,list):
            return False

        if len(other) != len(self):
            return False
        for i,s  in enumerate(self):
            if s != other[i]:
                return False
        return True

    def generate_tier(self, tier_segments):
        new_tier = list()
        for s in self:
            if s in tier_segments:
                new_tier.append(s)
        return new_tier

    def get_env(self,pos):

        if len(self) == 1:
            lhs = '#'
            rhs = '#'
        elif pos == 0:
            lhs = '#'
            rhs = self[pos+1]
        elif pos == len(self)-1:
            lhs = self[pos-1]
            rhs = '#'
        else:
            lhs = self[pos-1]
            rhs = self[pos+1]
        return lhs,rhs

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return len(self._list)

class FeatureMatrix(object):
    """
    An object that stores feature values for segments


    Attributes
    ----------
    name : str
        An informative identifier for the feature matrix

    feature_entries : list of Dictionary
        Dictionaries in the list should contain feature names as keys
        and feature values as values, as well as a special key-value pair
        for the symbol

    """

    def __init__(self, name,feature_entries):

        self.name = name
        self.features = None
        self.possible_values = set()
        self.matrix = {}
        self._default_value = 'n'
        for s in feature_entries:
            if self.features is None:
                self.features = {k for k in s.keys() if k != 'symbol'}
            #wheee, let's turn dictionaries of strings in lists of features so we can then generate dictionaries of strings!
            #compatability, yay!
            #self.matrix[s['symbol']] = [Feature(sign+name) for name,sign in s.items() if name != 'symbol']
            self.matrix[s['symbol']] = {k:v for k,v in s.items() if k != 'symbol'}
            #So much easier with a dictionary
            self.possible_values.update({v for k,v in s.items() if k != 'symbol'})

        #What are these?
        self.matrix['#'] = {'#':''}
        self.matrix[''] = {'*':''}

    def __eq__(self, other):
        if not isinstance(other,FeatureMatrix):
            return False
        if self.matrix == other.matrix:
            return True
        return False

    def __setstate__(self,state):
        self.__dict__.update(state)

        #Backwards compatability
        if '_default_value' not in state:
            self._default_value = 'n'

    def get_features(self):
        """Get the list of feature names used by a feature system

        Returns
        -------
        features: list of str
            List of names of features
        """
        features = list(self.features)
        features.sort()
        return features

    def validate(self):
        """
        Make sure that all segments in the matrix have all the features.
        If not, add an unspecified value for that feature to them.
        """
        for v in self.possible_values:
            if v not in ['+','-','.']:
                default_value = v
                break
        #dictionary
        for k,v in self.matrix.items():
            for f in self.features:
                if f not in v:
                    self.matrix[k][f] = self._default_value

        #Feature
        #for f in self.features:
        #    for s,v in self.matrix.items():
        #        for f2 in v:
        #            if f == f2.name:
        #                break
        #        else:
        #            self.matrix[s].append(Feature(default_value+f))

    def get_name(self):
        """
        Return an informative identifier for this feature system

        Returns
        -------
        str
            Name of FeatureMatrix
        """
        return self.name

    def get_feature_list(self):
        """
        Get a list of features that are used in this feature system

        Returns
        -------
        list
            List of the names of all features in the matrix
        """
        features = list(self.features)
        features.sort()
        return features

    def add_segment(self,seg,feat_spec):
        """
        Add a segment with a feature specification to the feature system

        Attributes
        ----------
        seg : str
            Segment symbol to add to the feature system

        feat_spec : dictionary
            Dictionary with features as keys and feature values as values

        """

        #Validation
        for f in feat_spec.keys():
            if f not in self.features:
                raise(AttributeError('The segment \'%s\' has a feature \'%s\' that is not defined for this feature matrix' %(seg,f)))

        self.matrix[seg] = feat_spec

    def add_feature(self,feature):
        """
        Add a feature to the feature system

        Attributes
        ----------
        feature : str
            Name of the feature to add to the feature system

        """

        self.features.update({feature})
        self.validate()

    def get_segments(self):
        """
        Return a list of segment symbols that are specified in the feature
        system

        Returns
        -------
        list
            List of all the segments with feature specifications
        """
        return list(self.matrix.keys())

    def get_possible_values(self):
        """
        Get the set of feature values used in the feature system

        Returns
        -------
        set
            Set of feature values
        """
        return self.possible_values

    def seg_to_feat_line(self,symbol):
        """
        Get a list of feature values for a given segment in the order
        that features are return in get_feature_list

        Use for display purposes

        Attributes
        ----------
        symbol : str
            Segment symbol to look up

        Returns
        -------
        list
            List of feature values for the symbol, as well as the symbol itself
        """
        #Feature
        #feats = self.matrix[symbol]
        #featline = [symbol]
        #for feat in self.get_feature_list():
        #    for f in feats:
        #        if f.name == feat:
        #            featline.append(f.sign)
        #            break
        #dictionary
        featline = [symbol] + [ self.matrix[symbol][feat]
                            for feat in self.get_feature_list()]
        return featline

    def __getitem__(self,item):
        if isinstance(item,str):
            return self.matrix[item]
        elif isinstance(item,tuple):
            return self.matrix[item[0]][item[1]]

    def __delitem__(self,item):
        del self.matrix[item]

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

    _corpus = None

    def __init__(self, **kwargs):

        self.tiers = list()
        self.transcription = None
        self.spelling = None
        self.descriptors = ['spelling','transcription']
        kwargs = {key.lower():value for key,value in list(kwargs.items())}

        for key, value in kwargs.items():
            key = key.lower()
            if isinstance(value,list):
                #transcription type stuff
                if key != 'transcription':
                    self.tiers.append(key)
                value = Transcription(value)
            elif key != 'spelling':
                try:
                    value = float(value)
                except ValueError:
                    pass
            setattr(self,key, value)
            if key not in self.descriptors:
                self.descriptors.append(key)
        if self.spelling is None and self.transcription is None:
            raise(ValueError('Words must be specified with at least a spelling or a transcription.'))
        if self.spelling is None:
            self.spelling = ''.join(map(str,self.transcription))

    def __getstate__(self):
        state = self.__dict__.copy()
        #for k,v in state.items():
        #    if (k == 'transcription' or k in self.tiers) and v is not None:
        #        state[k] = [x.symbol for x in v] #Only store string symbols
        return state

    def get_frequency(self):
        for f in ['frequency','abs_freq', 'freq_per_mil',
        'lowercase_freq', 'log10_freq']:
            try:
                return getattr(self,f)
            except AttributeError:
                pass
        return 0.0

    def add_tier(self, tier_name, tier_segments):
        """Adds a new tier attribute to a Word instance

        Parameters
        ----------
        tier_name : str
            User-supplied name for the new tier

        tier_features: list of str
            User-supplied list of phonological features values that define
            which segments are included in the tier

        """
        new_tier = self.transcription.generate_tier(tier_segments)
        setattr(self,tier_name,new_tier)
        if tier_name not in self.tiers:
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
            self.tiers.remove(tier_name)
            delattr(self, tier_name)
        except ValueError:
            pass #tier_name does not exist



    def startswith(self, query):
        """Returns the first segment in the Word's string

        """
        return query == self._string[0]

    def endswith(self, query):
        """Returns the last segment in the Word's string

        """
        return query == self._string[-1]

    def match_env(self, query, tier_name):
        """Searches for occurences of a particular environment in the word

        Parameters
        ----------
        query : Environment
            The environment to search for in the word


        Returns
        ----------
        list of Envrionments
            This list is empty if no matches are found
        """

        matches = list()
        tier = getattr(self,tier_name)
        for pos,seg in enumerate(tier):
            env = self.get_env(pos, tier_name)
            if env == query:
                matches.append(env)

        return matches

    def get_spelling(self):
        """
        Get the orthography of the word

        Returns
        -------
        str
            Orthographic spelling
        """
        return self.spelling

    def get_transcription(self):
        """
        Return the transcription of the word in the form of a list of
        Segment objects

        Returns
        -------
        list of Segments
            List containing the transcription for the word
        """
        return self.transcription

    def get_transcription_string(self):
        """
        Returns the transcription of the word as a string delimited by
        '.'

        Returns
        -------
        str
            String representation of the transcription
        """
        if self.transcription is None:
            return None
        return '.'.join(map(str,self.transcription))

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

    def get_env(self,pos,tier_name):
        """Get details of a particular environment in a Word

        Parameters
        ----------
        pos : int
            A position in the word, so 0<=pos<=len(self)

        Returns
        ----------
        e : Environment
            Environment of the segment at the given position in the word

        """
        tier = getattr(self,tier_name)
        lhs, rhs = tier.get_env(pos)
        e = Environment(self._corpus.specifier[lhs], self._corpus.specifier[rhs])

        return e

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        #returning self._string is problematic, because sometimes it's a list
        #and print functions don't like that, and raise a TypeError
        return '<Word: \'%s\'>' % self.spelling


    def __eq__(self, other):
        if not isinstance(other,Word):
            return False
        if self.spelling != other.spelling:
            return False
        if self.transcription != other.transcription:
            return False
        if self.frequency != other.frequency:
            return False
        return True

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

    #__slots__ = ['name', 'wordlist', 'specifier',
    #            'inventory', 'orthography', 'custom', 'feature_system',
    #            'has_frequency_value','has_spelling_value','has_transcription_value']

    def __init__(self, name):
        self.name = name
        self.wordlist = dict()
        self.specifier = None
        self.inventory = {'#' : Segment('#')} #set of Segments, if transcription exists
        self.orthography = {'#'} #set of orthographic characters
        self.custom = False
        self.has_frequency_value = None
        self.has_spelling_value = None
        self.has_transcription_value = None
        self._tiers = []

    def __eq__(self, other):
        if not isinstance(other,Corpus):
            return False
        if self.wordlist != other.wordlist:
            return False
        return True

    @property
    def tiers(self):
        return self._tiers

    def features_to_segments(self, feature_description):
        segments = list()
        for k,v in self.inventory.items():
            if v.feature_match(feature_description):
                segments.append(k)
        return segments

    def add_tier(self, tier_name, tier_features):
        if tier_name not in self._tiers:
            self._tiers.append(tier_name)
        tier_segs = self.features_to_segments(tier_features)
        for word in self:
            word.add_tier(tier_name,tier_segs)

    def remove_tier(self, tier_name):
        for word in self:
            word.remove_tier(tier_name)

    def __setstate__(self,state):
        try:
            self.__dict__.update(state)
            self._specify_features()

            #Backwards compatability
            word = self.random_word()
            if '_tiers' not in state:
                self._tiers = word.tiers
            if not isinstance(word.transcription, Transcription):
                for w in self:
                    w.transcription = Transcription(w.transcription)
                    for t in w.tiers:
                        setattr(w,t,Transcription(getattr(w,t)))
        except Exception as e:
            raise(CorpusIntegrityError("An error occurred while loading the corpus: {}.\nPlease redownload or recreate the corpus.".format(str(e))))


    def _specify_features(self):
        if self.has_feature_matrix():
            for k in self.inventory.keys():
                try:
                    self.inventory[k].specify(self.specifier[k])
                except KeyError:
                    pass

    def check_coverage(self):
        if not self.has_feature_matrix():
            return []
        return [x for x in self.inventory.keys() if x not in self.specifier]

    def iter_sort(self):
        """Sorts the keys in the corpus dictionary, then yields the values in that order

        """
        sorted_list = sorted(self.wordlist.keys())
        for word in sorted_list:
            yield self.wordlist[word]

    def get_name(self):
        """
        Get an informative identifier for the corpus

        Returns
        -------
        str
            Corpus's name
        """
        return self.name

    def is_custom(self):
        """
        Returns True if the corpus is user made versus supplied by PCT

        Returns
        -------
        bool
            True if corpus is user-created, otherwise False
        """
        return self.custom

    def get_feature_matrix(self):
        """
        Return the feature system used in the corpus

        Returns
        -------
        FeatureMatrix
            Currently used feature system
        """
        return self.specifier

    def set_feature_matrix(self,matrix):
        """
        Set the feature system to be used by the corpus and make sure
        every word is using it too.

        Attributes
        ----------
        matrix : FeatureMatrix
            New feature system to use in the corpus
        """
        self.specifier = matrix
        self._specify_features()

    def has_feature_matrix(self):
        """
        Check whether the corpus has a feature system

        Returns
        -------
        bool
            True if corpus has a feature system, otherwise False
        """
        return self.specifier is not None

    def has_frequency(self):
        """
        Return True if words in the corpus have the 'frequency' label

        Returns
        -------
        bool
            True if corpus has a frequency value, otherwise False
        """
        return self.has_frequency_value

    def has_spelling(self):
        """
        Return True if words in the corpus have the 'spelling' label

        Returns
        -------
        bool
            True if corpus has spellings, otherwise False
        """
        return self.has_spelling_value

    def has_transcription(self):
        """
        Return True if words in the corpus have the 'transcription' label

        Returns
        -------
        bool
            True if corpus has transcriptions, otherwise False
        """
        return self.has_transcription_value

    def get_inventory(self):
        """
        Returns a sorted list of segments used in transcriptions

        Returns
        -------
        list
            List of segment symbols used in transcriptions in the corpus
        """
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
        word._corpus = self
        #If the word doesn't exist, add it
        try:
            check = self.find(word.spelling, keyerror=True)
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
        except KeyError:
            self.wordlist[word.spelling] = word
            if word.spelling is not None:
                self.orthography.update(word.spelling)
                if self.has_spelling_value is None:
                    self.has_spelling_value = True
            elif self.has_spelling_value is None:
                self.has_spelling_value = False
            if self.has_frequency_value is None:
                if word.get_frequency():
                    self.has_frequency_value = True
                else:
                    self.has_frequency_value = False

        if word.transcription is not None:
            for s in word.transcription:
                if s not in self.inventory:
                    self.inventory[s] = Segment(s)
            if self.has_transcription_value is None:
                self.has_transcription_value = True
        elif self.has_transcription_value is None:
            self.has_transcription_value = False


    def random_word(self):
        """Return a randomly selected Word

        """
        word = random.choice(list(self.wordlist.keys()))
        return self.wordlist[word]

    def get_features(self):
        """Get a list of the features used to describe Segments

        Returns
        ----------
        list of str

        """
        return self.specifier.get_features()

    def find(self, word, keyerror=True):
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
                result = [self.wordlist[key]]
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
