import random
from corpustools.corpus.classes.lexicon import Corpus, Inventory, Segment, FeatureMatrix, Word
from corpustools import __version__ as currentPCTversion

def force_update2(corpus):
    corpus = Corpus(None, update=corpus)
    for word in [x for x in corpus]:
        word2 = Word(update=word)
        corpus.remove_word(word)
        corpus.add_word(word2)
    corpus.inventory = modernize_inventory_attributes(corpus.inventory)
    corpus.inventory, corpus.specifier = modernize_features(corpus.inventory, corpus.specifier)
    return corpus


def set_defaults(corpus):
    corpus = Corpus(corpus.name, update=corpus)

    corpus.inventory = Inventory(update=corpus.inventory)

    word_list = list()
    for word in corpus:
        word2 = Word(update=word)
        word_list.append(word2)
    corpus.update_wordlist(word_list)

    return corpus

def force_update(corpus):
    #This runs through known incompatibilities with previous version of PCT and tries to patch them all up. This gets
    #called from the LoadCorpusDialog.forceUpdate() in iogui.py
    corpus = set_defaults(corpus)

    if not hasattr(corpus.inventory, 'segs'):
        #setattr(corpus.inventory, 'segs', {'#': Segment('#')})
        setattr(corpus.inventory,
                'segs',
                {symbol: Segment(symbol) for symbol in Inventory.inventory_attributes['non_segment_symbols']})
    has_segs = [seg for seg in corpus.inventory.segs if not seg in Inventory.inventory_attributes['non_segment_symbols']]


    segs = set()
    #some old copora have a different spelling/transcription attribute set-up
    for word in corpus:
        if not hasattr(word, '_transcription'):
            setattr(word, 'Transcription', getattr(word, 'transcription'))
            word._transcription = word.Transcription
            del word.transcription
        if not hasattr(word, '_spelling'):
            word._spelling = word.spelling
        word._corpus = corpus
        for seg in word.transcription:
            segs.add(seg)
        corpus.remove_word()
        word = Word(update=word)

    if not has_segs:
        for seg in segs:
            corpus.inventory.segs[seg] = Segment(seg,corpus.specifier.specify(seg))

    corpus.inventory = modernize_inventory_attributes(corpus.inventory)
    corpus.inventory, corpus.specifier = modernize_features(corpus.inventory, corpus.specifier)
    corpus.inventory.isNew = False
    if not corpus.specifier.possible_values or len(corpus.specifier.possible_values) < 2:
        f_values = set()
        for seg in corpus.inventory:
            if seg == '#':
                continue
            features = corpus.specifier.specify(seg)
            f_values.update(features.values())
        f_values.add('n')
        corpus.specifier.possible_values = f_values
    return corpus

def need_update(corpus):
    if hasattr(corpus, '_version') and corpus._version == currentPCTversion:
        return False
    else:
        setattr(corpus, '_version', currentPCTversion)
        return True

def modernize_inventory_attributes(inventory):
    for attribute,default in Inventory.inventory_attributes.items():
        if not hasattr(inventory, attribute):
            setattr(inventory, attribute, default)

    has_segs = [s for s in inventory.segs if not s in Inventory.inventory_attributes['non_segment_symbols']]
    if not has_segs and inventory._data:
        #in an older version, inventory._data was a list of segs, but with the model/view set up,
        #this is changed
        inventory.segs = inventory._data.copy()
        inventory._data = list()

    if hasattr(inventory, 'vowel_feature'):
        #multiple vowel features are allowed, but earlier version only allowed a single one
        inventory.vowel_features = [inventory.vowel_feature]
        del inventory.vowel_feature
    return inventory

def modernize_specifier(specifier):
    #In older versions of PCT, the FeatureMatrix returns Segments, instead of feature dicts
    for seg in specifier.matrix.keys():
        if seg == '#':
            continue
        if isinstance(specifier.matrix[seg], Segment):
            specifier.matrix[seg] = specifier.matrix[seg].features

    #In some SPE matrices, uppercase [EXTRA] and [LONG] appear in specifier.features, but lower case [extra] and [long]
    #are used in the actual feature specifications. This next step forces the .features list to match the specifications
    features = sorted(list(specifier.matrix[seg].keys()))
    setattr(specifier, '_features', features)

    return FeatureMatrix(specifier.name, specifier)  # this adds new class methods too

def modernize_features(inventory, specifier):

    specifier = modernize_specifier(specifier)

    for seg in inventory:
        if seg == '#':
            continue
        if isinstance(seg.features, Segment):
            inventory[seg.symbol].features = specifier.matrix[seg.symbol]

    return inventory, specifier