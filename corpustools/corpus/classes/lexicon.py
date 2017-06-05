from corpustools import __version__ as currentPCTversion
import re
import random
import collections
import operator
import locale
import copy

from corpustools.exceptions import CorpusIntegrityError

class Segment(object):
    """
    Class for segment symbols

    Parameters
    ----------
    symbol : str
        Segment symbol

    Attributes
    ----------
    _features : dict
        Feature specification for the segment
    """

    def __init__(self, symbol, features=None):
        #None defaults are for word-boundary symbols
        self.symbol = symbol
        if features is None:
            self.features = {}
        else:
            self.features = features

    def specify(self, feature_dict):
        """
        Specify a segment with a new feature specification

        Parameters
        ----------
        feature_dict : dict
            Feature specification
        """
        self.features = {k.lower(): v for k,v in feature_dict.items()}

    def minimal_difference(self, other, features):
        """
        Check if this segment is a minimal feature difference with another
        segment (ignoring some _features)

        Parameters
        ----------
        other : Segment
            Segment to compare with
        _features : list
            Features that are allowed to vary between the two segments

        Returns
        -------
        bool
            True if all _features other than the specified ones match,
            False otherwise
        """

        for k, v in self.features.items():
            if k in features:
                continue
            if v != other[k]:
                return False
        return True

    def feature_match(self, specification):
        """
        Return true if segment matches specification, false otherwise.

        Parameters
        ----------
        specification : object
            Specification can be a single feature value '+feature', a list of
            feature values ['+feature1','-feature2'], or a dictionary of
            features and values {'feature1': '+', 'feature2': '-'}

        Returns
        -------
        bool
            True if this segment contains the feature values in the specification
        """
        if isinstance(specification,str):
            try:
                if self[specification[1:]]!=specification[0]:
                    return False
            except KeyError:
                return False
        elif isinstance(specification,list) or isinstance(specification, set):
            for f in specification:
                try:
                    if self[f[1:]]!=f[0]:
                        return False
                except KeyError:
                    return False
        elif isinstance(specification, dict):
            for f,v in specification.items():
                try:
                    if self[f] != v:
                        return False
                except KeyError:
                    return False,
        return True

    def __contains__(self, item):
        return item.lower() in self.features

    def __getitem__(self, key):
        #return self.features[key.lower()]
        return self.features[key]

    def __setitem__(self, key, value):
        #self.features[key.lower()] = value
        self.features[key] = value

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
    """
    Transcription object, sequence of symbols

    Parameters
    ----------
    seg_list : list
        List of segments that form the transcription.
        Elements in the list, can be Segments, strings, or BaseAnnotations

    Attributes
    ----------
    _list : list
        List of strings representing segment symbols
    stress_pattern: dict
        Dictionary with keys of segment indices and values of the stress
        for that segment
    boundaries : dict
        Possible keys of 'morpheme' or 'tone' that keeps track of where
        morpheme or tone boundaries are inserted
    """
    def __init__(self,seg_list):
        self._list = []
        #self._times = []
        self.stress_pattern = {}
        self.boundaries = {}
        cur_group = 0
        cur_tone = None
        if seg_list is not None:
            for i,s in enumerate(seg_list):
                try:
                    self._list.append(s.label)
                    #if s.begin is not None and s.end is not None:
                    #    self._times.append((s.begin,s.end))
                    if s.stress is not None:
                        self.stress_pattern[i] = s.stress
                    if s.tone is not None:
                        if 'tone' not in self.boundaries:
                            self.boundaries['tone'] = {}
                        if s.tone != cur_tone:
                            self.boundaries['tone'][i] = s.tone
                            cur_tone = s.tone
                    if s.group is not None:
                        if 'morpheme' not in self.boundaries:
                            self.boundaries['morpheme'] = []
                        if s.group != cur_group:
                            self.boundaries['morpheme'].append(i)
                            cur_group = s.group
                except AttributeError:
                    if isinstance(s,str):
                        self._list.append(s)
                    elif isinstance(s,dict):
                        try:
                            symbol = s['label']
                        except KeyError:
                            symbol = s['symbol']
                        self._list.append(symbol)
                        #if 'begin' in s and 'end' in s:
                        #    self._times.append((s['begin'],s['end']))
                    elif isinstance(s,list):
                        if len(s) == 3:
                            self._list.append(s[0])
                            #self._times.append((s[1],s[2]))
                        else:
                            raise(NotImplementedError('That format for seg_list is not supported.'))
                    else:
                        raise(NotImplementedError('That format for seg_list is not supported.'))

    def with_word_boundaries(self):
        """
        Return the string of segments with word boundaries surrounding them

        Returns
        -------
        list
            Transcription with word boundaries
        """
        return ['#'] + self._list + ['#']

    def find(self, environment):
        """
        Find instances of an EnvironmentFilter in the Transcription

        Parameters
        ----------
        environment : EnvironmentFilter
            EnvironmentFilter to search for

        Returns
        -------
        list
            List of Environments that fit the EnvironmentFilter
        """
        if not isinstance(environment, EnvironmentFilter):
            return None
        if all(m not in self for m in environment._middle):
            return None
        num_segs = len(environment)

        possibles = zip(*[self.with_word_boundaries()[i:] for i in range(num_segs)])

        lhs_num = environment.lhs_count()
        middle_num = lhs_num
        rhs_num = middle_num + 1
        envs = []

        for i, p in enumerate(possibles):
            if p in environment:
                lhs = p[:lhs_num]
                middle = p[middle_num]
                rhs = p[rhs_num:]
                envs.append(Environment(middle, i + middle_num, lhs, rhs))

        lhsZeroes, rhsZeroes = environment.zeroPositions
        if lhsZeroes:
            word = [seg for pos,seg in enumerate(self.with_word_boundaries()) if pos not in lhsZeroes]
            possibles = zip(*[word[i:] for i in range(num_segs)])
            for i, p in enumerate(possibles):
                if environment.without_zeroes_contains(p):
                    lhs = p[:lhs_num]
                    middle = p[middle_num]
                    rhs = p[rhs_num:]
                    envs.append(Environment(middle, i + middle_num, lhs, rhs))

        if rhsZeroes:
            rhsZeroes = [rz+middle_num+1 for rz in rhsZeroes]
            word = [seg for pos, seg in enumerate(self.with_word_boundaries()) if pos not in rhsZeroes]
            possibles = zip(*[word[i:] for i in range(num_segs)])
            for i, p in enumerate(possibles):
                if environment.without_zeroes_contains(p):
                    lhs = p[:lhs_num]
                    middle = p[middle_num]
                    rhs = p[rhs_num:]
                    envs.append(Environment(middle, i + middle_num, lhs, rhs))

        if not envs:
            return None
        return envs

    def find_nonmatch(self, environment, is_sets=False):
        """
        Find all instances of an EnvironmentFilter in the Transcription
        that match in the middle segments, but don't match on the sides

        Parameters
        ----------
        environment : EnvironmentFilter
            EnvironmentFilter to search for

        Returns
        -------
        list
            List of Environments that fit the EnvironmentFilter's middle
            but not the sides
        """
        if not isinstance(environment, EnvironmentFilter):
            return None
        if is_sets:
            #I'm sure this entire block can be reduced to a list comprehension plus any() or all(), but I just
            #can't figure it out right now. Something like:
            #if not any([[m in self for m in mid] for mid in environment.middle]): return None
            found = False
            for mid in environment.middle:
                for m in mid:
                    if m in self:
                        found = True
                        break
            if not found:
                return None
        else:
            if all(m not in self for m in environment.middle):
                return None
        num_segs = len(environment)

        possibles = zip(*[self.with_word_boundaries()[i:]
                                for i in range(num_segs)])
        envs = []
        lhs_num = environment.lhs_count()
        middle_num = lhs_num
        rhs_num = middle_num + 1
        for i, p in enumerate(possibles):
            has_segs = False
            if is_sets:
                for mid in environment.middle:
                    if p[middle_num] in mid:
                        has_segs = True
            else:
                has_segs = p[middle_num] in environment.middle
            if p not in environment and has_segs:
                lhs = p[:lhs_num]
                middle = p[middle_num]
                rhs = p[rhs_num:]
                envs.append(Environment(middle, i + middle_num, lhs, rhs))
        if not envs:
            return None
        return envs


    def __contains__(self, other):
        if isinstance(other, Segment):
            if other.symbol in self._list:
                return True
        elif isinstance(other, str):
            if other in self._list:
                return True
        return False

    def __setstate__(self, state):
        if 'stress_pattern' not in state:
            state['stress_pattern'] = {}
        if 'boundaries' not in state:
            state['boundaries'] = {}
        self.__dict__.update(state)

    def __hash__(self):
        return hash(str(self))

    def __getitem__(self, key):
        if isinstance(key,int) or isinstance(key,slice):
            return self._list[key]
        raise(KeyError)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        temp_list = []
        for i,s in enumerate(self._list):
            if self.stress_pattern and i in self.stress_pattern:
                s += self.stress_pattern[i]
            if 'tone' in self.boundaries and i in self.boundaries['tone']:
                s += self.boundaries['tone'][i]
            temp_list.append(s)
        if 'morpheme' in self.boundaries:
            beg = 0
            bound_list = []
            for i in self.boundaries['morpheme']:
                bound_list.append('.'.join(temp_list[beg:i]))
            bound_list.append('.'.join(temp_list[i:]))
            return '-'.join(bound_list)
        else:
            return '.'.join(temp_list)

    def __iter__(self):
        for s in self._list:
            yield s

    def __add__(self, other):
        """
        Allow for Transcriptions to be added to get all the segments in each
        """
        if not isinstance(other,Transcription):
            raise(TypeError)
        return self._list + other._list

    def __eq__(self, other):
        if isinstance(other,list):
            if len(other) != len(self):
                return False
            for i,s  in enumerate(self):
                if s != other[i]:
                    return False
            return True
        if not isinstance(other, Transcription):
            return False
        if self._list != other._list:
            return False
        if self.stress_pattern != other.stress_pattern:
            return False
        if self.boundaries != other.boundaries:
            return False
        return True

    def __lt__(self,other):
        if isinstance(other, Transcription):
            return self._list < other._list
        else:
            return self._list < other

    def __le__(self,other):
        if isinstance(other, Transcription):
            return (self._list == other._list or self._list < other._list)
        else:
            return self._list <= other

    def __ge__(self,other):
        if isinstance(other, Transcription):
            return (self._list == other._list or self._list > other._list)
        else:
            return self._list >= other

    def __gt__(self,other):
        if isinstance(other, Transcription):
            return self._list > other._list
        else:
            return self._list > other

    def match_segments(self, segments):
        """
        Returns a matching segments from a list of segments

        Parameters
        ----------
        segments : list
            List of Segments or strings to filter the Transcription

        Returns
        -------
        list
            List of segments (in their original order) that match the
            segment parameter
        """
        match = []
        for s in self:
            if s in segments:
                match.append(s)
        return match

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return len(self._list)


class FeatureMatrix(object):
    """
    An object that stores feature values for segments

    Parameters
    ----------
    name : str
        Name to give the FeatureMatrix
    feature_entries : list
        List of dict with one dictionary per segment, requires the key
        of symbol which identifies the segment

    Attributes
    ----------
    name : str
        An informative identifier for the feature matrix
    features : list
        Sorted list of feature names
    possible_values : set
        Set of values used in the FeatureMatrix
    default_value : str
        Default feature value, usually corresponding to unspecified _features
    stresses : dict
        Mapping of stress values to segments that bear that stress
    places : dict
        Mapping from place of articulation labels to a feature specification
    manners : dict
        Mapping from manner of articulation labels to a feature specification
    height : dict
        Mapping from vowel height labels to a feature specification
    backness : dict
        Mapping from vowel backness labels to a feature specification
    vowel_features : str
        Feature value (i.e., '+voc') that separates vowels from consonants
    voice_feature : str
        Feature value (i.e., '+voice') that codes voiced obstruents
    diph_feature : str
        Feature value (i.e., '+diphthong' or '.high') that separates
        diphthongs from monophthongs
    rounded_feature : str
        Feature value (i.e., '+round') that codes rounded vowels


    """
    attributes = ['name', '_features', 'vowel_features', 'cons_features', 'voice_features', 'rounded_feature',
                  'diph_feature', 'possible_values', 'matrix', '_default_value']

    def __init__(self, name, feature_entries):
        self.name = name
        self._features = None
        self.vowel_feature = None
        self.cons_features = None
        self.voice_features = None
        self.rounded_feature = None
        self.diph_feature = None
        self.possible_values = set()
        self.matrix = {}
        self._default_value = 'n'
        if isinstance(feature_entries, FeatureMatrix):
            for attr in self.attributes:
                if hasattr(feature_entries, attr):
                    setattr(self, attr, getattr(feature_entries, attr))
        else:
            for s in feature_entries:
                self.matrix[s['symbol']] = {k:v for k,v in s.items() if k != 'symbol'}
                self.possible_values.update({v for k,v in s.items() if k != 'symbol'})
            #This if-block never seems to be called, and this whole class' code
            #appears to treat ._features as a list, so why it should default to
            #dictionary here is unclear. However, changing to a list causes the
            #"make feature system from text file" option to break, so better to
            #leave this alone
            if self._features is None:
                self._features = {k for k in s.keys() if k != 'symbol'}


    def __eq__(self, other):
        if not isinstance(other, FeatureMatrix):
            return False
        if self.matrix == other.matrix:
            return True
        return False

    def default_fill(self, seg_list):
        for seg in seg_list:
            self.matrix[seg] = {feature: self.default_value for feature in self._features}

    @property
    def trans_name(self):
        return self.name.split('2')[0]

    @property
    def feature_name(self):
        return self.name.split('2')[-1]

    def features_to_segments(self, feature_description):
        """
        Given a feature description, return the segments in the inventory
        that match that feature description

        Feature descriptions should be either lists, such as
        ['+feature1', '-feature2'] or strings that can be separated into
        lists by ',', such as '+feature1,-feature2'.

        Parameters
        ----------
        feature_description : str, list, or dict
            Feature values that specify the segments, see above for format

        Returns
        -------
        list of Segments
            Segments that match the feature description

        """
        segments = list()
        if isinstance(feature_description, str):
            feature_description = feature_description.split(',')
        #otherwise it's probably a list, leave it be
        for k,v in self.matrix.items():
            if self.feature_match(feature_description, v):
                segments.append(k)
        return segments

    def feature_match(self, features_to_match, segment_description):
        """
        :param features_to_match:  a list of strings representing features, e.g. ['+voice','-nasal']
        :param segment_description:  a dictionary of {feature_name:feature_value}
        :return: True if features match up with the segment description, e.g. if {'voice':'+', 'nasal':'-'} is in the
                segment dictionary. Otherwise returns False.
        """
        for feature in features_to_match:
            if segment_description[feature[1:]] == feature[0]:
                continue
            else:
                return False
        else:
            return True


    def __setstate__(self,state):
        if 'features' not in state:
            state['features'] = state['_features']
        self.__dict__.update(state)

        #Backwards compatability
        if '_default_value' not in state:
            self._default_value = 'n'
        if 'places' not in state:
            self.places = collections.OrderedDict()
            self.manners = collections.OrderedDict()
            self.backness = collections.OrderedDict()
            self.height = collections.OrderedDict()
            #self.generate_generic_names()

        if 'cons_column_data' not in state:
            self.cons_columns = {}
            self.cons_rows = {}
            self.vow_columns = {}
            self.vow_rows = {}
            self.vowel_feature = None
            self.voice_feature = None
            self.rounded_feature = None

    def __iter__(self):
        for k in sorted(self.matrix.keys()):
            yield self.matrix[k]

    def validate(self):
        """
        Make sure that all segments in the matrix have all the features.
        If not, add an unspecified value for that feature to them.
        """
        for k,v in self.matrix.items():
            for f in self._features:
                if f not in v:
                    self.matrix[k][f] = self._default_value

    def set_major_class_features(self, source):
        self.vowel_feature = source.vowel_feature
        self.voice_feature = source.voice_feature
        self.rounded_feature = source.rounded_feature
        self.diphthong_feature = source.diph_feature


    @property
    def default_value(self):
        return self._default_value

    @property
    def features(self):
        """
        Get a list of _features that are used in this feature system

        Returns
        -------
        list
            Sorted list of the names of all _features in the matrix
        """
        return sorted(list(self._features))

    def add_segment(self,seg,feat_spec):
        """
        Add a segment with a feature specification to the feature system

        Attributes
        ----------
        seg : str
            Segment symbol to add to the feature system
        feat_spec : dictionary
            Dictionary with _features as keys and feature values as values
        """

        #Validation
        for f in feat_spec.keys():
            if f not in self._features:
                raise(AttributeError('The segment \'%s\' has a feature \'%s\' that is not defined for this feature matrix' %(seg,f)))
        # s = Segment(seg)
        # s.set_features(feat_spec)
        # self.matrix[seg] = s._features
        self.matrix[seg] = feat_spec

    def add_feature(self,feature, default = None):
        """
        Add a feature to the feature system

        Attributes
        ----------
        feature : str
            Name of the feature to add to the feature system
        default : str, optional
            If specified, set the value for all segments to this value,
            otherwise use the FeatureMatrix's ``default_value``
        """

        #self._features.update({feature})
        #see note about dictionary vs. list in the __init__() method
        self._features.append(feature)
        self._features.sort()
        if default is None:
            self.validate()
        else:
            for seg,features in self.matrix.items():
                for f in self._features:
                    if f not in features:
                        self.matrix[seg][f] = default


    def valid_feature_strings(self):
        """
        Get all combinations of ``possible_values`` and ``_features``

        Returns
        -------
        list
            List of valid feature strings
        """
        strings = []
        for v in self.possible_values:
            for f in self._features:
                strings.append(v+f)
        return strings

    def categorize(self, seg):
        """
        Categorize a segment into consonant/vowel, place of articulation,
        manner of articulation, voicing, vowel height, vowel backness, and vowel
        rounding.

        For consonants, the category is of the format:

        ('Consonant', PLACE, MANNER, VOICING)

        For vowels, the category is of the format:

        ('Vowel', HEIGHT, BACKNESS, ROUNDED)

        Diphthongs are categorized differently:

        ('Diphthong', 'Vowel')

        Parameters
        ----------
        seg : Segment
            Segment to categorize

        Returns
        -------
        tuple or None
            Returns categories according to the formats above, if any are
            unable to be calculated, returns None in those places.
            Returns None if a category cannot be found.
        """
        if seg == '#':
            return None
        seg_features = seg.features
        if seg.feature_match(self.vowel_feature):
            category = ['Vowel']

            if seg.feature_match(self.diph_feature):
                category.insert(0,'Diphthong')
                return category

            for k,v in self.height.items():
                if seg.feature_match(v):
                    category.append(k)
                    break
            else:
                category.append(None)
            for k,v in self.backness.items():
                if seg.feature_match(v):
                    category.append(k)
                    break
            else:
                category.append(None)

            if seg.feature_match(self.rounded_feature):
                category.append('Rounded')
            else:
                category.append('Unrounded')
        else:
            category = ['Consonant']

            for k,v in self.places.items():
                if seg.feature_match(v):
                    category.append(k)
                    break
            else:
                category.append(None)

            for k,v in self.manners.items():
                if seg.feature_match(v):
                    category.append(k)
                    break
            else:
                category.append(None)

            if seg.feature_match(self.voice_feature):
                category.append('Voiced')
            else:
                category.append('Voiceless')
        return category

    @property
    def segments(self):
        """
        Return a list of segment symbols that are specified in the feature
        system

        Returns
        -------
        list
            List of all the segments with feature specifications
        """
        return list(self.matrix.keys())

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
        featline = [symbol] + [ self.matrix[symbol][feat]
                            for feat in self._features]
        return featline

    def specify(self, seg, assign_defaults = False):

        if isinstance(seg, Segment):
            symbol = seg.symbol
        else:
            symbol = seg

        try:
            features = self.matrix[symbol]
        except KeyError:
            if assign_defaults:
                self.matrix[symbol] = {feature:'n' for feature in self.features}
                features = self.matrix[symbol]
            else:
                raise KeyError(symbol)
        return features

    def __getitem__(self,item):
        if isinstance(item,str):
            #get full feature list for a given segment
            return self.matrix[item]
        if isinstance(item, Segment):
            return self.matrix[item.symbol]
        if isinstance(item,tuple):
            #tuple should be (symbol,feature_name) to get only that feature's value
            return self.matrix[item[0]][item[1]]

    def __delitem__(self,item):
        del self.matrix[item]

    def __contains__(self,item):
        return item in list(self.matrix.keys())

    def __setitem__(self,key,value):
        if isinstance(key, str):
            self.matrix[key] = value
        if isinstance(key, Segment):
            self.matrix[key.symbol] = value

    def __len__(self):
        return len(self.matrix)

class Word(object):
    """An object representing a word in a corpus

    Information about the attributes are contained in the Corpus' ``attributes``.

    Attributes
    ----------
    spelling : str
        A representation of a word that lacks phonological information.

    transcription : Transcription
        A representation of a word that includes phonological information.

    frequency : float
        Token frequency in a corpus
    """

    word_attributes = {'_corpus':None, '_transcription':None, '_spelling':None,
                       '_transcription_name':None, '_spelling_name': None,
                       'alt_transcriptions': list(), 'alt_spellings': list(),
                       '_frequency':0, 'wordtokens':list(),
                       'descriptors':list()}
    _freq_names = ['abs_freq', 'freq_per_mil','sfreq', 'lowercase_freq', 'log10_freq', 'freq', 'frequency']

    def __init__(self, update=False, **kwargs):

        if update:
            self.update(update)
            return

        self.initDefaults()

        for key, value in kwargs.items():
            if not all([letter.isupper() for letter in key]):
                key = key.capitalize()
            if isinstance(value, tuple):
                #this block of code is used when loading a corpus for the first time
                att, value = value
                if att.att_type == 'numeric':
                    try:
                        value = locale.atof(value)
                    except (ValueError, TypeError):
                        value = float('nan')
                    if key == 'Frequency':
                        setattr(self, key, value)
                        setattr(self, '_frequency', value)

                elif att.att_type == 'tier':
                    value = Transcription(value)
                else:# att.att_type == 'spelling' or att.att_type == 'factor':
                    pass

                setattr(self, key, value)

                if att.is_default:
                    if att.att_type == 'tier':
                        setattr(self, '_transcription', value)
                        self._transcription_name = key
                    elif att.att_type == 'spelling':
                        setattr(self, '_spelling', value)
                        self._spelling_name = key
                else:
                    if att.att_type == 'tier':
                        self.alt_transcriptions.append(key)
                    elif att.att_type == 'spelling':
                        self.alt_spellings.append(key)

            #the following code is reached when adding a word, not when loading a corpus
            elif isinstance(value, list):
                #probably a transcription
                value = Transcription(value)
                setattr(self, key, value)
                setattr(self, '_transcription', value)
                setattr(self, '_transcription_name', key)

            elif isinstance(value, str):
                try:
                    value = float(value)
                    if key == 'Frequency':
                        setattr(self, 'Frequency', value)
                        setattr(self, '_frequency', self.Frequency)
                except ValueError:
                    #it's spelling, leave value as-is
                    setattr(self, '_spelling', value)
                    setattr(self, '_spelling_name', key)
                setattr(self, key, value)

            elif isinstance(value, (float, int)):
                if key == 'Frequency':
                    setattr(self, 'Frequency', value)
                    setattr(self, '_frequency', self.Frequency)
                setattr(self, key, value)


            if key not in self.descriptors:
                self.descriptors.append(key)

        if self.spelling is None and self.transcription is None:
            raise(ValueError('Words must be specified with at least a spelling or a transcription.'))
        if self.spelling is None:
            self.Spelling = ''.join(map(str,self._transcription))
            self._spelling = self.Spelling
            self._spelling_name = 'Spelling'
            if not 'Spelling' in self.descriptors:
                self.descriptors.append('Spelling')
        if not 'Frequency' in self.descriptors:
            self.descriptors.append('Frequency')
            self._frequency = 0
            self.Frequency = 0

        if self._transcription_name is None:
            for d in self.descriptors:
                if isinstance(getattr(self,d,None), Transcription):
                    self._transcription_name = d
                    break
            else:
                self._transcription = None

    def initDefaults(self):
        for attribute, default_value in Word.word_attributes.items():
            if isinstance(default_value, list):
                setattr(self, attribute, [x for x in default_value])
            elif isinstance(default_value, dict):
                setattr(self, attribute, default_value.copy())
            else:
                setattr(self, attribute, default_value)

    @property
    def frequency(self):
        return max([self.Frequency, self._frequency])

    @frequency.setter
    def frequency(self, value):
        self.Frequency = value

    @frequency.deleter
    def frequency(self):
        del self.Frequency

    @property
    def transcription(self):
        try:
            value = getattr(self, self._transcription_name, self._transcription)
        except (TypeError, AttributeError):
            value = None #transcription doesn't exist
        return value

    @transcription.setter
    def transcription(self, value):
        if self._transcription_name is not None:
            setattr(self, self._transcription_name, value)
        self._transcription = value

    @transcription.deleter
    def transcription(self):
        del self._transcription

    @property
    def spelling(self):
        try:
            value = getattr(self, self._spelling_name, self._spelling)
        except (TypeError, AttributeError):
            value = None #spelling doesn't exist
        return value

    @spelling.setter
    def spelling(self, value):
        if self._spelling_name is not None:
            setattr(self, self._spelling_name, value)
        self._spelling = value

    @spelling.deleter
    def spelling(self):
        del self._spelling

    def __copy__(self):
        return Word(update=self)

    def update(self, old_word):

        for attribute, value in old_word.__dict__.items():
            if not hasattr(self, attribute):
                setattr(self, attribute, value)

        for attribute, default_value in Word.word_attributes.items():
            if hasattr(old_word, attribute):
                setattr(self, attribute, getattr(old_word, attribute))
            else:
                setattr(self, attribute, default_value)

        if hasattr(old_word, 'wordtokens'):
            self.wordtokens = list()
            for wt in old_word.wordtokens:
                self.wordtokens.append(copy.copy(wt))

        self.descriptors.extend([att for att in Word.word_attributes if not att.startswith('_')])
        self.descriptors = list(set(self.descriptors))

        if not self._transcription:
            try:
                self._transcription = old_word.__dict__['transcription']
            except KeyError:
                try:
                    self._transcription = old_word.__dict__['_transcription']
                except KeyError:
                    self._transcription = None

            self.Transcription = self._transcription
            self._transcription_name = 'Transcription'
            self.descriptors.append('Transcription')

        if not self._spelling:
            try:
                self._spelling = old_word.__dict__['spelling']
            except KeyError:
                try:
                    self._spelling = old_word.__dict__['_spelling']
                except KeyError:
                    self._spelling = None

            self.Spelling = self._spelling
            self._spelling_name = 'Spelling'
            self.descriptors.append('Spelling')

        try:
            self.Frequency = old_word.__dict__['frequency']
        except KeyError:
            self.Frequency = old_word.__dict__['Frequency']
        try:
            self.descriptors.remove('_frequency')
        except ValueError:
            pass
        try:
            self.descriptors.remove('frequency')
        except ValueError:
            pass
        self.descriptors.append('Frequency')


    def get_len(self, tier_name):
        return len(getattr(self, tier_name))

    def enumerate_symbols(self, tier_name, reversed=False):
        if reversed:
            word = [k for k in range(self.get_len(tier_name))]
            word.reverse()
            for j in word:
                yield (j, getattr(self, tier_name)[j])

        else:
            for j in range(self.get_len(tier_name)):
                yield (j, getattr(self, tier_name)[j])

    def __hash__(self):
        return hash((self._spelling,str(self._transcription)))

    def __getstate__(self):
        state = self.__dict__.copy()
        # state['wordtokens'] = []
        # state['_corpus'] = None
        # for k,v in state.items():
        #    if (k == 'transcription' or k in self.tiers) and v is not None:
        #        state[k] = [x.symbol for x in v] #Only store string symbols
        return state

    def __setstate__(self, state):
        self._transcription = []
        self._spelling = ''
        self._frequency = 0
        if 'wordtokens' not in state:
            state['wordtokens'] = []
        if 'descriptors' not in state:
            state['descriptors'] = ['_spelling','_transcription', '_frequency']
        if '_frequency' not in state['descriptors']:
            state['descriptors'].append('_frequency')
        try:
            tiers = state.pop('tiers')
            for t in tiers:
                state['descriptors'].append(t)
        except KeyError:
            pass
        self.__dict__.update(state)

    def add_abstract_tier(self, tier_name, tier_segments):
        """
        Add an abstract tier to the Word

        Parameters
        ----------
        tier_name : str
            Attribute name
        tier_segments: dict
            Dictionary with keys of the abstract segments (i.e., 'C' or 'V')
            and values that are sets of segments
        """
        tier = []
        for s in self.transcription:
            for k,v in tier_segments.items():
                if s in v:
                    tier.append(k)
                    break
        setattr(self,tier_name,''.join(tier))

    def add_attribute(self, tier_name, value):
        """
        Add an arbitrary attribute to the Word

        Parameters
        ----------
        tier_name : str
            Attribute name
        value: object
            Attribute value
        """
        setattr(self, tier_name, value)

    def add_tier(self, tier_name, tier_segments):
        """Adds a new tier attribute to the Word

        Parameters
        ----------
        tier_name : str
            Name for the new tier

        tier_segments: list of segments
            Segments that count for inclusion in the tier
        """
        matching_segs = self.transcription.match_segments(tier_segments)
        new_tier = Transcription(matching_segs)
        setattr(self,tier_name,new_tier)
        for wt in self.wordtokens:
            matching_segs = wt.transcription.match_segments(tier_segments)
            new_tier = Transcription(matching_segs)
            setattr(wt,tier_name,new_tier)


    def remove_attribute(self, attribute_name):
        """Deletes a tier attribute from a Word

        Parameters
        ----------
        attribute_name : str
            Name of tier attribute to be deleted.

        Notes
        -----
        If attribute_name is not a valid attribute, this function does nothing. It
        does not raise an error.

        """
        if attribute_name.startswith('_'):
            return
        try:
            delattr(self, attribute_name)
        except ValueError:
            pass #attribute_name does not exist

    def variants(self, sequence_type = 'transcription'):
        """
        Get variants and frequencies for a Word

        Parameters
        ----------
        sequence_type : str, optional
            Tier name to get variants

        Returns
        -------
        dict
            Dictionary with keys of Transcriptions and values of their frequencies
        """
        return collections.Counter(getattr(x,sequence_type) for x in self.wordtokens)

    def __repr__(self):
        return '<Word: \'%s\'>' % self.spelling

    def __str__(self):
        return self.spelling

    def __eq__(self, other):
        if not isinstance(other,Word):
            return False
        if self.spelling != other.spelling:
            return False
        if self.transcription != other.transcription:
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
    """
    Specific sequence of segments that was a match for an EnvironmentFilter

    Parameters
    ----------
    middle : str
        Middle segment
    position : int
        Position of the middle segment in the word (to differentiate between
        repetitions of an environment in the same word
    lhs : list, optional
        Segments to the left of the middle segment
    rhs : list, optional
        Segments to the right of the middle segment
    """
    def __init__(self, middle, position, lhs = None, rhs = None):
        self.middle = middle
        self.position = position
        self.lhs = lhs
        self.rhs = rhs
        self.lhs_string = None
        self.rhs_string = None
        self.middle_string = None

    def __getitem__(self, key):
        if self.lhs is not None:
            if key < len(self.lhs):
                return self.lhs[key]
            elif key == len(self.lhs):
                return self.middle
            elif self.rhs is not None:
                return self.rhs[key - len(self.lhs) - 1]
            else:
                raise(KeyError('Index out of bounds'))
        else:
            if key == 0:
                return self.middle
            elif self.rhs is not None:
                return self.rhs[key - 1]
            else:
                raise(KeyError('Index out of bounds'))

    def __str__(self):
        elements = []
        if self.lhs_string is not None:
            elements.append(self.lhs_string)
        elif self.lhs is not None:
            elements.append(''.join(self.lhs))
        else:
             elements.append('')
        if self.rhs_string is not None:
            elements.append(self.rhs_string)
        elif self.rhs is not None:
            elements.append(''.join(self.rhs))
        else:
             elements.append('')
        return '_'.join(elements)

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash((self.lhs, self.position, self.middle, self.rhs))

    def __eq__(self,other):
        """
        Two Environments are equal if they share a left AND right hand side
        An empty lhs or rhs is an automatic match
        """
        if not isinstance(other,Environment):
            return False

        if other.lhs and other.lhs != self.lhs:
            return False
        if other.rhs and other.rhs != self.rhs:
            return False
        if other.position != self.position:
            return False
        return True

    def __ne__(self,other):
        return not self.__eq__(other)

class EnvironmentFilter(object):
    """
    Filter to use for searching words to generate Environments that match

    Parameters
    ----------
    middle_segments : set
        Set of segments to center environments
    lhs : list, optional
        List of set of segments on the left of the middle
    rhs : list, optional
        List of set of segments on the right of the middle

    """
    def __init__(self, middle_segments, lhs = None, rhs = None, zeroPositions = None):
        self.original_middle = middle_segments
        self.special_match_symbol = '*'
        if lhs is not None:
            lhs = tuple(lhs)
        self.lhs = lhs
        if rhs is not None:
            rhs = tuple(rhs)
        self.rhs = rhs

        self.lhs_string = None
        self.rhs_string = None
        self._sanitize()

        if zeroPositions is None:
            self.zeroPositions = (None, None)
        else:
            self.zeroPositions = zeroPositions

    @property
    def middle(self):
        return self.original_middle

    @middle.setter
    def middle(self, middle_segments):
        self.original_middle = middle_segments
        self._sanitize()

    def _sanitize(self):
        if self.lhs is not None:
            new_lhs = []
            for seg_set in self.lhs:
                if not isinstance(seg_set,frozenset):
                    new_lhs.append(frozenset(seg_set))
                else:
                    new_lhs.append(seg_set)
            self.lhs = tuple(new_lhs)
        if self.rhs is not None:
            new_rhs = []
            for seg_set in self.rhs:
                if not isinstance(seg_set,frozenset):
                    new_rhs.append(frozenset(seg_set))
                else:
                    new_rhs.append(seg_set)
            self.rhs = tuple(new_rhs)
        if not isinstance(self.middle, frozenset):
            self.middle = frozenset(self.middle)
        self._middle = set()
        for m in self.middle:
            if isinstance(m, str):
                self._middle.add(m)
            elif isinstance(m, (list, tuple, set)):
                self._middle.update(m)

    def is_applicable(self, sequence):
        """
        Check whether the Environment filter is applicable to the sequence
        (i.e., the sequence must be greater or equal in length to the
        EnvironmentFilter)

        Parameters
        ----------
        sequence : list
            Sequence to check applicability

        Returns
        -------
        bool
            True if the sequence is equal length or longer than the
            EnvironmentFilter
        """
        if len(sequence) < len(self):
            return False
        return True

    def compile_re_pattern(self):
        pass

    def lhs_count(self):
        """
        Get the number of elements on the left hand side

        Returns
        -------
        int
            Length of the left hand side
        """
        if self.lhs is None:
            return 0
        return len(self.lhs)

    def rhs_count(self):
        """
        Get the number of elements on the right hand side

        Returns
        -------
        int
            Length of the right hand side
        """
        if self.rhs is None:
            return 0
        return len(self.rhs)

    def set_lhs(self, lhs):
        self.lhs = lhs
        self.compile_re_pattern()

    def set_rhs(self, rhs):
        self.rhs = rhs
        self.compile_re_pattern()

    def __iter__(self):
        if self.lhs is not None:
            for s in self.lhs:
                yield s
        yield self._middle
        if self.rhs is not None:
            for s in self.rhs:
                yield s

    def __len__(self):
        length = 1
        if self.lhs is not None:
            length += len(self.lhs)
        if self.rhs is not None:
            length += len(self.rhs)
        return length

    def __str__(self):
        elements = []
        if self.lhs_string is not None:
            elements.append(self.lhs_string)
        elif self.lhs is not None:
            elements.append(''.join('{' + ','.join(x) + '}' for x in self.lhs))
        else:
             elements.append('')
        if self.rhs_string is not None:
            elements.append(self.rhs_string)
        elif self.rhs is not None:
            elements.append(''.join('{' + ','.join(x) + '}' for x in self.rhs))
        else:
             elements.append('')
        return '_'.join(elements)

    def __eq__(self, other):
        if not hasattr(other,'lhs'):
            return False
        if not hasattr(other,'rhs'):
            return False
        if self.lhs != other.lhs:
            return False
        if self.rhs != other.rhs:
            return False
        return True

    def __hash__(self):
        return hash((self.rhs, self.lhs))

    def __contains__(self, sequence):
        for i, s in enumerate(self):
            if self.special_match_symbol in s:
                continue
            if sequence[i] not in s:
                return False
        return True

    def without_zeroes_contains(self, sequence):
        for i, s in enumerate(self.without_zero_positions()):
            if self.special_match_symbol in s:
                continue
            if sequence[i] not in s:
                return False
        return True

    def without_zero_positions(self):
        e = list()
        if self.lhs is not None:
            for i,s in enumerate(self.lhs):
                if i in self.zeroPositions[0]:
                    continue
                else:
                    e.append(s)

        e.append(self._middle)

        if self.rhs is not None:
            for i,s in enumerate(self.rhs):
                if i in self.zeroPositions[1]:
                    continue
                else:
                    e.append(s)
        return e

class Attribute(object):
    """
    Attributes are for collecting summary information about attributes of
    Words or WordTokens, with different types of attributes allowing for
    different behaviour

    Parameters
    ----------
    name : str
        Python-safe name for using `getattr` and `setattr` on Words and
        WordTokens

    att_type : str
        Either 'spelling', 'tier', 'numeric' or 'factor'

    display_name : str
        Human-readable name of the Attribute, defaults to None

    default_value : object
        Default value for initializing the attribute

    Attributes
    ----------
    name : string
        Python-readable name for the Attribute on Word and WordToken objects

    display_name : string
        Human-readable name for the Attribute

    default_value : object
        Default value for the Attribute.  The type of `default_value` is
        dependent on the attribute type.  Numeric Attributes have a float
        default value.  Factor and Spelling Attributes have a string
        default value.  Tier Attributes have a Transcription default value.

    range : object
        Range of the Attribute, type depends on the attribute type.  Numeric
        Attributes have a tuple of floats for the range for the minimum
        and maximum.  The range for Factor Attributes is a set of all
        factor levels.  The range for Tier Attributes is the set of segments
        in that tier across the corpus.  The range for Spelling Attributes
        is None.
    """
    ATT_TYPES = ['spelling', 'tier', 'numeric', 'factor']
    def __init__(self, name, att_type, display_name = None, default_value = None, is_default = False):
        self.name = name
        self.att_type = att_type
        self._display_name = display_name
        self.is_default = is_default

        if self.att_type == 'numeric':
            self._range = [0,0]
            if default_value is not None and isinstance(default_value,(int,float)):
                self._default_value = default_value
            else:
                self._default_value = 0
        elif self.att_type == 'factor':
            if default_value is not None and isinstance(default_value,str):
                self._default_value = default_value
            else:
                self._default_value = ''
            if default_value:
                self._range = set([default_value])
            else:
                self._range = set()
        elif self.att_type == 'spelling':
            self._range = None
            if default_value is not None and isinstance(default_value,str):
                self._default_value = default_value
            else:
                self._default_value = ''
        elif self.att_type == 'tier':
            self._range = set()
            self._delim = None
            if default_value is not None and isinstance(default_value,Transcription):
                self._default_value = default_value
            else:
                self._default_value = Transcription(None)

    def __gt__(self, other):
        return self.display_name < other.display_name

    def __lt__(self, other):
        return not self.__gt__(other)

    @property
    def delimiter(self):
        if self.att_type != 'tier':
            return None
        else:
            return self._delim

    @delimiter.setter
    def delimiter(self, value):
        self._delim = value

    @staticmethod
    def guess_type(values, trans_delimiters = None):
        """
        Guess the attribute type for a sequence of values

        Parameters
        ----------
        values : list
            List of strings to evaluate for the attribute type
        trans_delimiters : list, optional
            List of delimiters to look for in transcriptions, defaults
            to ``.``, ``;``, and ``,``

        Returns
        -------
        str
            Attribute type that had the most success in parsing the
            values specified
        """
        if trans_delimiters is None:
            trans_delimiters = ['.',' ', ';', ',']
        probable_values = {x: 0 for x in Attribute.ATT_TYPES}
        for i,v in enumerate(values):
            try:
                t = float(v)
                probable_values['numeric'] += 1
                continue
            except ValueError:
                for d in trans_delimiters:
                    if d in v:
                        probable_values['tier'] += 1
                        break
                else:
                    if v in [v2 for j,v2 in enumerate(values) if i != j]:
                        probable_values['factor'] += 1
                    else:
                        probable_values['spelling'] += 1
        return max(probable_values.items(), key=operator.itemgetter(1))[0]

    @staticmethod
    def sanitize_name(name):
        """
        Sanitize a display name into a Python-readable attribute name

        Parameters
        ----------
        name : string
            Display name to sanitize

        Returns
        -------
        str
            Sanitized name
        """
        name = re.sub('\W','',name)#.lower())
        name = name if all([s.isupper() for s in name]) else name.capitalize()
        return name

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return '<Attribute of type {} with name \'{}\'>'.format(self.att_type,self.name)

    def __str__(self):
        return self.display_name

    def __eq__(self,other):
        if isinstance(other,Attribute):
            if self.name == other.name:
                return True
        if isinstance(other,str):
            if self.name == other:
                return True
        return False

    @property
    def display_name(self):
        if self._display_name is not None:
            return self._display_name#.lower()
        return self.name

    @property
    def default_value(self):
        return self._default_value

    @default_value.setter
    def default_value(self, value):
        self._default_value = value
        self._range = set([value])

    @property
    def range(self):
        return self._range

    def update_range(self,value):
        """
        Update the range of the Attribute with the value specified.
        If the attribute is a Factor, the value is added to the set of levels.
        If the attribute is Numeric, the value expands the minimum and
        maximum values, if applicable.  If the attribute is a Tier, the
        value (a segment) is added to the set of segments allowed. If
        the attribute is Spelling, nothing is done.

        Parameters
        ----------
        value : object
            Value to update range with, the type depends on the attribute
            type
        """
        if value is None:
            return
        if self.att_type == 'numeric':
            if isinstance(value, str):
                try:
                    value = float(value)
                except ValueError:
                    self.att_type = 'spelling'
                    self._range = None
                    return
            if value < self._range[0]:
                self._range[0] = value
            elif value > self._range[1]:
                self._range[1] = value
        elif self.att_type == 'factor':
            self._range.add(value)
            #if len(self._range) > 1000:
            #    self.att_type = 'spelling'
            #    self._range = None
        elif self.att_type == 'tier':
            if isinstance(self._range, list):
                self._range = set(self._range)
            self._range.update([x for x in value])

class Inventory(object):
    """

    Inventories contain information about a Corpus' segmental inventory. This class exists mainly for the purposes
    of saving and loading user data. When a user loads a corpus into PCT, the Inventory is passed to the constructor of
    an InventoryModel (corpustools\gui\models). The InventoryModel is what the user will interact with, and it has
    several useful functions for analyzing, modifying and sorting the contents of an inventory. The InventoryModel is
    also connected with an InventoryView (corpustools\gui\views) for the purposes of displaying inventory charts in PCT.

    User data is saved using Python's built-in pickle module. However, Qt objects (like the InventoryModel) cannot be
    pickled. Instead, the data from the model is copied to this Inventory class, which is a native Python object and
    can be properly pickled.


    Parameters
    ----------

    data : dict, optional
        Mapping from segment symbol to Segment objects

    Attributes
    ----------
    _features : list
        List of all _features used as specifications for segments
    possible_values : set
        Set of values that segments use for _features
    stresses : dict
        Mapping of stress values to segments that bear that stress
    places : dict
        Mapping from place of articulation labels to sets of segments
    manners : dict
        Mapping from manner of articulation labels to sets of segments
    height : dict
        Mapping from vowel height labels to sets of segments
    backness : dict
        Mapping from vowel backness labels to sets of segments
    vowel_features : str
        Feature value (i.e., '+voc') that separates vowels from consonants
    voice_feature : str
        Feature value (i.e., '+voice') that codes voiced obstruents
    diph_feature : str
        Feature value (i.e., '+diphthong' or '.high') that separates
        diphthongs from monophthongs
    rounded_feature : str
        Feature value (i.e., '+round') that codes rounded vowels


    """
    inventory_attributes = {'_data': list(), 'segs': {'#': Segment('#')},
                            'features': list(), 'possible_values': list(),
                            'stresses': list(),
                            'consColumns': set(), 'vowelColumns': set(),
                            'vowelRows': set(), 'consRows': set(),
                            'cons_column_data': {}, 'cons_row_data': {},
                            'vowel_column_data': {}, 'vowel_row_data': {},
                            'uncategorized': list(), 'all_rows': dict(),
                            'all_columns': dict(), 'vowel_column_offset': int(), 'vowel_row_offset': int(),
                            'cons_column_header_order': dict(), 'cons_row_header_order': dict(),
                            'vowel_row_header_order': dict(), 'vowel_column_header_order': dict(),
                            'consList': list(), 'vowelList': list(), 'non_segment_symbols': ['#', '-', '='],
                            'vowel_features': [None], 'cons_features': [None], 'voice_feature': None,
                            'rounded_feature': None,
                            'diph_feature': None, 'isNew': True, 'filterNames': False,
                            'minimum_features': {'hayes' : ['consonantal', 'labial', 'coronal', 'labiodental',
                                                              'anterior', 'dorsal',
                                                              'back', 'sonorant', 'delayed_release', 'nasal',
                                                              'continuant', 'trill', 'tap',
                                                              'lateral', 'front', 'back', 'high', 'low'],
                                                 'spe' : ['voc', 'ant', 'cor', 'high', 'low', 'back', 'son',
                                                          'lat', 'nasal']}
                            }

    def __init__(self, update=False):
        if update:
            self.update(update)
            self.isNew = False
            return

        self.initDefaults()

    def initDefaults(self):
        for attribute, default_value in Inventory.inventory_attributes.items():
            if isinstance(default_value, list):
                setattr(self, attribute, [x for x in default_value])
            elif isinstance(default_value, dict):
                setattr(self, attribute, default_value.copy())
            else:
                setattr(self, attribute, default_value)

    def update(self, source):
        for attribute, default_value in Inventory.inventory_attributes.items():
            if hasattr(source, attribute):
                setattr(self, attribute, getattr(source, attribute))
            else:
                if isinstance(default_value, list):
                    setattr(self, attribute, [x for x in default_value])
                elif isinstance(default_value, dict):
                    setattr(self, attribute, default_value.copy())
                else:
                    setattr(self, attribute, default_value)

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        if 'stresses' not in state:
            state['stresses'] = collections.OrderedDict()
        if 'places' not in state:
            state['places'] = collections.OrderedDict()
        if 'manners' not in state:
            state['manners'] = collections.OrderedDict()
        if 'height' not in state:
            state['height'] = collections.OrderedDict()
        if 'backness' not in state:
            state['backness'] = collections.OrderedDict()
        if 'vowel_features' not in state:
            state['vowel_features'] = None
        if 'voice_feature' not in state:
            state['voice_feature'] = None
        if 'diph_feature' not in state:
            state['diph_feature'] = None
        if 'rounded_feature' not in state:
            state['rounded_feature'] = None
        self.__dict__.update(state)

    def save(self, model):
        """
        Takes an InventoryModel as input, and updates attributes. This is called in main.py in saveCorpus().
        """
        for attribute in Inventory.inventory_attributes:
            if hasattr(model, attribute):
                setattr(self, attribute, getattr(model, attribute))
            # else:
            #     pass

    def __len__(self):
        return len(self.segs.keys())

    def keys(self):
        return self.segs.keys()

    def values(self):
        return self.segs.values()

    def items(self):
        return self.segs.items()

    def __getitem__(self, key):
        if isinstance(key, slice):
            return sorted(self.segs.keys())[key]
        if isinstance(key, str):
            return self.segs[key]
        if isinstance(key, Segment):
            return self.segs[key.symbol]

    def __setitem__(self, key, value):
        self.segs[key] = value

    def __iter__(self):
        for k in sorted(self.segs.keys()):
            if k in self.non_segment_symbols:
                continue
            yield self.segs[k]

    def __contains__(self, item):
        if isinstance(item, str):
            return item in self.segs.keys()
        elif isinstance(item, Segment):
            return item.symbol in self.segs.keys()
        return False

    def valid_feature_strings(self):
        """
        Get all combinations of ``possible_values`` and ``_features``

        Returns
        -------
        list
            List of valid feature strings
        """
        strings = []
        for v in self.possible_values:
            for f in self.features:
                strings.append(v+f)
        return strings

    def features_to_segments(self, feature_description):
        """
        Given a feature description, return the segments in the inventory
        that match that feature description

        Feature descriptions should be either lists, such as
        ['+feature1', '-feature2'] or strings that can be separated into
        lists by ',', such as '+feature1,-feature2'.

        Parameters
        ----------
        feature_description : string or list
            Feature values that specify the segments, see above for format

        Returns
        -------
        list of Segments
            Segments that match the feature description

        """
        segments = []
        if isinstance(feature_description, str):
            feature_description = feature_description.split(',')
        for k,v in self.segs.items():
            if v.feature_match(feature_description):
                segments.append(k)
        return segments

    def update_features(self, specifier):
        for seg in self.segs:
            if seg in self.non_segment_symbols:
                continue
            self.segs[seg].features = specifier.specify(seg, assign_defaults=True)
        self.cons_features = specifier.cons_features if hasattr(specifier, 'cons_features') else [None]
        self.vowel_features = specifier.vowel_features if hasattr(specifier, 'vowel_features') else [None]
        self.voice_feature = specifier.voice_feature if hasattr(specifier, 'voice_feature') else None
        self.rounded_feature = specifier.rounded_feature if hasattr(specifier, 'rounded_feature') else None
        self.diphthong_feature = specifier.diph_feature if hasattr(specifier, 'diph_feature') else None
        self.features = specifier.features
        self.possible_values = specifier.possible_values

class Corpus(object):
    """
    Lexicon to store information about Words, such as transcriptions,
    spellings and frequencies

    Parameters
    ----------
    name : string
        Name to identify Corpus

    Attributes
    ----------

    name : str
        Name of the corpus, used only for easy of reference

    attributes : list of Attributes
        List of Attributes that Words in the Corpus have

    wordlist : dict
        Dictionary where every key is a unique string representing a word in a
        corpus, and each entry is a Word object

    words : list of strings
        All the keys for the wordlist of the Corpus

    specifier : FeatureSpecifier
        See the FeatureSpecifier object

    inventory : Inventory
        Inventory that contains information about segments in the Corpus
    """

    corpus_attributes = {'name':'corpus', 'wordlist': dict(), '_discourse': None,
                  'specifier': None, 'inventory': None, 'inventoryModel': None, 'has_frequency': True,
                  'has_spelling':False, 'has_wordtokens':False, 'has_audio': False, 'wav_path': None,
                  '_attributes': list(),
                  '_version': currentPCTversion
                    }
    basic_attributes = ['spelling','transcription','frequency']

    def __init__(self, name, update=False):
        if update:
            self.update(update)
            return

        self.initDefaults()
        self.name = name

    def initDefaults(self):
        for attribute, default_value in Corpus.corpus_attributes.items():
            if attribute == 'inventory':
                setattr(self, attribute, Inventory())
            # elif attribute == '_attributes':
            #     setattr(self, attribute, [Attribute('spelling', 'spelling'),
            #                               Attribute('transcription', 'tier'),
            #                               Attribute('frequency', 'numeric')])
            elif isinstance(default_value, list):
                setattr(self, attribute, [x for x in default_value])
            elif isinstance(default_value, dict):
                setattr(self, attribute, default_value.copy())
            else:
                setattr(self, attribute, default_value)
        self._version = currentPCTversion

    def update(self, old_corpus):
        for attribute,default_value in Corpus.corpus_attributes.items():
            if hasattr(old_corpus, attribute):
                setattr(self, attribute, getattr(old_corpus, attribute))
            else:
                setattr(self, attribute, default_value)
        self._version = currentPCTversion

    def update_wordlist(self, new_wordlist):
        self.wordlist = dict()
        for word in new_wordlist:
            self.add_word(word)

    @property
    def has_transcription(self):
        for a in self.attributes:
            if a.att_type == 'tier' and len(a.range) > 0:
                return True
        return False

    def __eq__(self, other):
        if not isinstance(other,Corpus):
            return False
        if self.wordlist != other.wordlist:
            return False
        return True

    def __iadd__(self, other):
        for a in other.attributes:
            if a not in self.attributes:
                self.add_attribute(a)
        for w in other:
            try:
                sw = self.find(w.spelling)
                sw.frequency += w.frequency
                for a in self.attributes:
                    if getattr(sw, a.name) == a.default_value and getattr(w, a.name) != a.default_value:
                        setattr(sw, a.name, copy.copy(getattr(w, a.name)))
                for wt in w.wordtokens:
                    sw.wordtokens.append(copy.copy(wt))
            except KeyError:
                self.add_word(copy.copy(w))
        if self.specifier is None and other.specifier is not None:
            self.set_feature_matrix(other.specifier)

        self.inventory.segs.update(other.inventory.segs)
        return self

    def key(self, word):
        key = word.spelling
        if self[key] == word:
            return key
        count = 0
        while True:
            count += 1
            key = '{} ({})'.format(word.spelling,count)
            try:
                if self[key] == word:
                    return key
            except KeyError:
                break


    def keys(self):
        for k in sorted(self.wordlist.keys()):
            yield k

    def set_default_representations(self):
        for att in self.attributes:
            if att.att_type == 'tier':
                if att.is_default:
                    self.default_transcription = att
                else:
                    self.alternative_transcriptions.append(att)
            elif att.att_type == 'spelling':
                if att.is_default:
                    self.default_spelling = att
                else:
                    self.alternative_spellings.append(att)

    def generate_alternative_inventories(self):

        for att in self.alternative_transcriptions:
            altinv = set()
            for word in self:
                transcription = getattr(word, att.name)
                for x in transcription:
                    altinv.add(x)
            self.alternative_inventories[att.name] = Inventory()
            for seg in altinv:
                #for some reason, this loop alters the contents of self.inventory, which it shouldn't
                self.alternative_inventories[att.name].segs[seg] = Segment(seg,
                                                                   self.specifier.specify(seg, assign_defaults=True))
    @property
    def all_inventories(self):
        inventories = dict()
        if hasattr(self, 'lexicon'):
            inventories[self.default_transcription.display_name] = self.lexicon.inventory
        else:
            inventories[self.default_transcription.display_name] = self.inventory

        for name,inv in self.alternative_inventories.items():
            inventories[name] = inv
        return inventories.items()


    def retranscribe(self, segmap):

        self.inventory = Inventory()
        for word in self.wordlist:
            T = Transcription([segmap[seg] for seg in self.wordlist[word].transcription])
            self.wordlist[word].transcription = T
            #self.update_inventory(self.wordlist[word].transcription)
            for seg in T:
                if seg not in self.inventory:
                    self.inventory.segs[seg] = Segment(seg)
                    self.inventory.segs[seg].features = self.specifier[seg]


    def subset(self, filters):
        """
        Generate a subset of the corpus based on filters.

        Filters for Numeric Attributes should be tuples of an Attribute
        (of the Corpus), a comparison callable (``__eq__``, ``__neq__``,
        ``__gt__``, ``__gte__``, ``__lt__``, or ``__lte__``) and a value
        to compare all such attributes in the Corpus to.

        Filters for Factor Attributes should be tuples of an Attribute,
        and a set of levels for inclusion in the subset.

        Other attribute types cannot currently be the basis for filters.

        Parameters
        ----------
        filters : list of tuples
            See above for format

        Returns
        -------
        Corpus
            Subset of the corpus that matches the filter conditions
        """

        new_corpus = Corpus('')
        new_corpus._attributes = [Attribute(x.name, x.att_type, x.display_name)
                    for x in self.attributes]

        for word in self:
            for f in filters:
                if f[0].att_type == 'numeric':
                    op = f[1]
                    if not op(getattr(word,f[0].name), f[2]):
                        break
                elif f[0].att_type == 'factor':
                    if getattr(word,f[0].name) not in f[1]:
                        break
            else:
                new_corpus.add_word(word)
        return new_corpus

    @property
    def attributes(self):
        #'transcription', 'spelling' and 'frequency' are special attributes which are acually
        # methods decorated with @property
        #these methods return the value of word._transcription, word._spelling, or word._frequency
        #we don't want to put them into the GUI column headers because that will lead to duplication
        return sorted([a for a in self._attributes if not a.name in ('spelling', 'transcription', 'frequency')])

    @property
    def words(self):
        return sorted(list(self.wordlist.keys()))

    def symbol_to_segment(self, symbol):
        for seg in self.inventory:
            if seg.symbol == symbol:
                return seg
        else:
            raise CorpusIntegrityError('Could not find {} in the inventory'.format(symbol))


    def features_to_segments(self, feature_description):
        """
        Given a feature description, return the segments in the inventory
        that match that feature description

        Feature descriptions should be either lists, such as
        ['+feature1', '-feature2'] or strings that can be separated into
        lists by ',', such as '+feature1,-feature2'.

        Parameters
        ----------
        feature_description : string or list
            Feature values that specify the segments, see above for format

        Returns
        -------
        list of Segments
            Segments that match the feature description

        """
        segments = list()
        if isinstance(feature_description,str):
            feature_description = feature_description.split(',')
        for k,v in self.inventory.items():
            if v.feature_match(feature_description):
                segments.append(k)
        return segments

    def segment_to_features(self, seg):
        """
        Given a segment, return the _features for that segment.

        Parameters
        ----------
        seg : string or Segment
            Segment or Segment symbol to look up

        Returns
        -------
        dict
            Dictionary with keys as _features and values as featue values
        """
        try:
            features = self.specifier.matrix[seg]
        except TypeError:
            features = self.specifier.matrix[seg.symbol]
        return features

    def add_abstract_tier(self, attribute, spec):
        """
        Add a abstract tier (currently primarily for generating CV skeletons
        from tiers).

        Specifiers for abstract tiers should be dictionaries with keys that
        are the abstract symbol (such as 'C' or 'V') and the values are
        iterables of segments that should count as that abstract symbols
        (such as all consonants or all vowels).

        Currently only operates on the ``transcription`` of words.

        Parameters
        ----------
        attribute : Attribute
            Attribute to add/replace

        spec : dict
            Mapping for creating abstract tier
        """
        for i,a in enumerate(self._attributes):
            if attribute.name == a.name:
                self._attributes[i] = attribute
                break
        else:
            self._attributes.append(attribute)
        for word in self:
            word.add_abstract_tier(attribute.name,spec)
            attribute.update_range(getattr(word,attribute.name))

    def add_attribute(self, attribute, initialize_defaults = False):
        """
        Add an Attribute of any type to the Corpus or replace an existing Attribute.

        Parameters
        ----------
        attribute : Attribute
            Attribute to add or replace

        initialize_defaults : boolean
            If True, words will have this attribute set to the ``default_value``
            of the attribute, defaults to False
        """
        for i,a in enumerate(self._attributes):
            if attribute.display_name == a.display_name:
                self._attributes[i] = attribute
                break
        else:
            self._attributes.append(attribute)
        if initialize_defaults:
            for word in self:
                word.add_attribute(attribute.name,attribute.default_value)

    def add_count_attribute(self, attribute, sequence_type, spec):
        """
        Add an Numeric Attribute that is a count of a segments in a tier that
        match a given specification.

        The specification should be either a list of segments or a string of
        the format '+feature1,-feature2' that specifies the set of segments.

        Parameters
        ----------
        attribute : Attribute
            Attribute to add or replace

        sequence_type : string
            Specifies whether to use 'spelling', 'transcription' or the name of a
            transcription tier to use for comparisons

        spec : list or str
            Specification of what segments should be counted
        """
        if isinstance(attribute,str):
            attribute = Attribute(attribute,'numeric')
        for i,a in enumerate(self._attributes):
            if attribute.name == a.name:
                self._attributes[i] = attribute
                break
        else:
            self._attributes.append(attribute)
        if isinstance(spec, str):
            tier_segs = self.features_to_segments(spec)
        else:
            tier_segs = spec
        for word in self:
            v = sum([1 for x in getattr(word, sequence_type) if x in tier_segs])
            setattr(word, attribute.name, v)
            attribute.update_range(v)

    def add_tier(self, attribute, spec):
        """
        Add a Tier Attribute based on the transcription of words as a new Attribute
        that includes all segments that match the specification.

        The specification should be either a list of segments or a string of
        the format '+feature1,-feature2' that specifies the set of segments.

        Parameters
        ----------
        attribute : Attribute
            Attribute to add or replace

        spec : list or str
            Specification of what segments should be counted
        """
        if isinstance(attribute,str):
            attribute = Attribute(attribute, 'tier')
        for i,a in enumerate(self._attributes):
            if attribute.name == a.name:
                self._attributes[i] = attribute
                break
        else:
            self._attributes.append(attribute)
        if isinstance(spec, str):
            tier_segs = self.features_to_segments(spec)
        else:
            tier_segs = spec
        attribute._range = tier_segs
        for word in self:
            word.add_tier(attribute.name,tier_segs)

    def remove_word(self, word_key):
        """
        Remove a Word from the Corpus using its identifier in the Corpus.

        If the identifier is not found, nothing happens.

        Parameters
        ----------
        word_key : string
            Identifier to use to remove the Word
        """
        try:
            del self.wordlist[word_key]
        except KeyError:
            pass

    def remove_attribute(self, attribute):
        """
        Remove an Attribute from the Corpus and from all its Word objects.

        Parameters
        ----------
        attribute : Attribute
            Attribute to remove
        """
        if isinstance(attribute,str):
            name = attribute
        else:
            name = attribute.name
        if name in self.basic_attributes:
            return
        for i in range(len(self._attributes)):
            if self._attributes[i].name == name:
                del self._attributes[i]
                break
        else:
            return
        for word in self:
            word.remove_attribute(name)

    def __getstate__(self):
        state = self.__dict__
        return state

    def __setstate__(self, state):
        try:
            if 'inventory' not in state:
                state['inventory'] = state['_inventory'] #backcompat
            if not isinstance(state['inventory'], Inventory):
                state['inventory'] = Inventory()
            if 'has_spelling' not in state:
                state['has_spelling'] = state['has_spelling_value']
            if 'has_transcription' in state:
                del state['has_transcription']
            if 'has_wordtokens' not in state:
                state['has_wordtokens'] = False
            if '_freq_base' in state:
                del state['_freq_base']
            if '_attributes' not in state:
                state['_attributes'] = [Attribute('spelling','spelling'),
                                        Attribute('transcription','tier'),
                                        Attribute('frequency','numeric')]
                try:
                    tiers = state.pop('_tiers')
                    for t in tiers:
                        state['_attributes'].append(Attribute(t,'tier'))
                except KeyError:
                    pass
            self.__dict__.update(state)
            #Backwards compatability
            for k,w in self.wordlist.items():
                w._corpus = self
                # for a in self.attributes:
                #     if a.att_type == 'tier':
                #         if not isinstance(getattr(w,a.name), Transcription):
                #             setattr(w,a.name,Transcription(getattr(w,a.name)))
                #     else:
                #         try:
                #             a.update_range(getattr(w,a.name))
                #         except AttributeError as e:
                #             print(k)
                #             print(w.__dict__)
                #             raise(e)

        except Exception as e:
            raise(e)
            raise(CorpusIntegrityError("An error occurred while loading the corpus: {}."
                                       "\nPlease redownload or recreate the corpus.".format(str(e))))

    def _specify_features(self):
        self.inventory.specify(self.specifier)

    def check_coverage(self):
        """
        Checks the coverage of the specifier (FeatureMatrix) of the Corpus over the
        inventory of the Corpus

        Returns
        -------
        list
            List of segments in the inventory that are not in the specifier
        """
        if not self.specifier is not None:
            return []
        return [x for x in self.inventory.keys() if x not in self.specifier]

    def iter_words(self):
        """
        Sorts the keys in the corpus dictionary,
        then yields the values in that order

        Returns
        -------
        generator
            Sorted Words in the corpus
        """
        sorted_list = sorted(self.wordlist.keys())
        for word in sorted_list:
            yield self.wordlist[word]

    def iter_sort(self):
        """
        Sorts the keys in the corpus dictionary, then yields the
        values in that order

        Returns
        -------
        generator
            Sorted Words in the corpus

        """
        sorted_list = sorted(self.wordlist.keys())
        for word in sorted_list:
            yield self.wordlist[word]

    def set_feature_matrix(self,matrix):
        """
        Set the feature system to be used by the corpus and make sure
        every word is using it too.

        Parameters
        ----------
        matrix : FeatureMatrix
            New feature system to use in the corpus
        """
        self.specifier = matrix


    def get_random_subset(self, size, new_corpus_name='randomly_generated'):
        """Get a new corpus consisting a random selection from the current corpus

        Parameters
        ----------
        size : int
            Size of new corpus

        new_corpus_name : str

        Returns
        -------
        new_corpus : Corpus
            New corpus object with len(new_corpus) == size
        """
        new_corpus = Corpus(new_corpus_name)
        while len(new_corpus) < size:
            word = self.random_word()
            new_corpus.add_word(word, allow_duplicates=False)
        new_corpus.specifier = self.specifier
        return new_corpus

    def add_word(self, word, allow_duplicates=False):
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
            If False, duplicate Words with the same spelling as an existing
            word in the corpus will not be added

        """
        word._corpus = self
        tokens = word.wordtokens[:]
        #If the word doesn't exist, add it
        try:
            check = self.find(word.spelling)
            if allow_duplicates:
                #Some words have more than one entry in a corpus, e.g. "live" and "live"
                #so they need to be assigned unique keys

                n = 0
                while True:
                    n += 1
                    key = '{} ({})'.format(word.spelling,n)
                    try:
                        check = self.find(key)
                    except KeyError:
                        self.wordlist[key] = word
                        break
            else:
                check.frequency += 1
                check.wordtokens.extend(tokens)
                return
        except KeyError:
            if word.frequency == 0:
                word.frequency += 1

            self.wordlist[word.spelling] = word#copy.copy(word)
            if word.spelling is not None:
                if not self.has_spelling:
                    self.has_spelling = True
        added_default = False
        if word.transcription is not None:
            added_default = self.update_inventory(word.transcription)
            #added_default == True if the word contains symbols not found in the feature file
            #in this case, the symbol has been given a default value of 'n' for every feature
            word.transcription._list = [self.inventory[x].symbol for x in word.transcription._list]

        for d in word.descriptors:
            if d not in self._attributes:
                if isinstance(getattr(word,d),str):
                    self._attributes.append(Attribute(d,'spelling'))#'factor'))
                elif isinstance(getattr(word,d),Transcription):
                    self._attributes.append(Attribute(d,'tier'))
                elif isinstance(getattr(word,d),(int, float)):
                    self._attributes.append(Attribute(d,'numeric'))

        for a in self._attributes:
            if not hasattr(word,a.name):
                word.add_attribute(a.name, a.default_value)
            a.update_range(getattr(word,a.name))

        return added_default

    def update_features(self):
        for seg in self.inventory:
            if seg.symbol == '#':
                continue
            self.inventory[seg.symbol].features = self.specifier.specify(seg)

    def update_inventory(self, transcription):
        """
        Update the inventory of the Corpus to ensure it contains all
        the segments in the given transcription

        Parameters
        ----------
        transcription : list
            Segment symbols to add to the inventory if needed
        """
        added_default = False
        for s in transcription:
            if isinstance(s, Segment):
                s = s.symbol
            if s not in self.inventory:
                self.inventory.segs[s] = Segment(s)
                if self.specifier is not None:
                    if not s in self.specifier:
                        self.specifier[s] = {feature.lower(): 'n' for feature in self.specifier.features}
                        added_default = True
                    self.inventory.segs[s].features = self.specifier[s]

        if transcription.stress_pattern:
            for k,v in transcription.stress_pattern.items():
                self.inventory.stresses[v].add(transcription[k])

        return added_default

    def get_or_create_word(self, **kwargs):
        """
        Get a Word object that has the spelling and transcription
        specified or create that Word, add it to the Corpus and return it.

        Parameters
        ----------
        spelling : string
            Spelling to search for

        transcription : list
            Transcription to search for

        Returns
        -------
        Word
            Existing or newly created Word with the spelling and transcription
            specified
        """
        try:
            spelling = kwargs['spelling']
        except KeyError:
            for key,value in kwargs.items():
                att_type = value[0].att_type
                default = value[0].is_default
                if att_type == 'spelling' and default:
                    spelling = value[1]
                    break
            else:
                return None

        words = self.find_all(spelling)
        for w in words:
            for k,v in kwargs.items():
                if isinstance(v,tuple):
                    v = v[1]
                if isinstance(v,list):
                    v = Transcription(v)
                if getattr(w,k) != v:
                    break
            else:
                return w
        else:
            word = Word(**kwargs)
            self.add_word(word)
        return word

    def random_word(self):
        """Return a randomly selected Word

        Returns
        -------
        Word
            Random Word
        """
        word = random.choice(list(self.wordlist.keys()))
        return self.wordlist[word]

    def get_features(self):
        """
        Get a list of the _features used to describe Segments

        Returns
        ----------
        list of str

        """
        return self.specifier.features

    def find(self, word, ignore_case = False):
        """Search for a Word in the corpus

        Parameters
        ----------
        word : str
            String representing the spelling of the word (not transcription)

        Returns
        -------
        Word
            Word that matches the spelling specified

        Raises
        ------
        KeyError
            If word is not found
        """
        patterns = [word]
        if ignore_case:
            patterns.append(word.lower())
            patterns.append(word.title())
        for w in patterns:
            key = w
            try:
                result = self.wordlist[w]
                return result
            except KeyError:
                try:
                    key = '{} (1)'.format(w)
                    result = self.wordlist[key]
                    return result
                except KeyError:
                    pass

        raise KeyError('The word \"{}\" is not in the corpus'.format(word))

    def find_all(self, spelling):
        """
        Find all Word objects with the specified spelling

        Parameters
        ----------
        spelling : string
            Spelling to look up

        Returns
        -------
        list of Words
            Words that have the specified spelling
        """
        words = list()
        try:
            words.append(self.wordlist[spelling])
            count = 0
            while True:
                count += 1
                try:
                    words.append(self.wordlist['{} ({})'.format(spelling,count)])
                except KeyError:
                    break
        except KeyError:
            pass
        return words

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



