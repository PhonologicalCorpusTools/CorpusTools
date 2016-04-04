import random
from corpustools.corpus.classes.lexicon import Segment, FeatureMatrix
from corpustools import __version__ as currentPCTversion

#it would be better to import these attributes from .models.InventoryModel, but this creates a circular import problem
inventory_attributes = {'_data':list(), 'segs':dict(), 'features':list(), 'possible_values':list(), 'stresses':list(),
                        'consColumns': set(['Column 1']), 'vowelColumns': set(['Column 1']),
                        'vowelRows': set(['Row 1']), 'consRows':set(['Row 1']),
                        'cons_column_data': {'Column 1': [0,{},None]}, 'cons_row_data': {'Row 1': [0,{},None]},
                        'vowel_column_data': {'Column 1': [0,{},None]}, 'vowel_row_data': {'Row 1': [0,{},None]},
                        'uncategorized': list(), 'all_rows': dict(),
                        'all_columns': dict(),'vowel_column_offset': int(), 'vowel_row_offset': int(),
                        'cons_column_header_order':dict(),'cons_row_header_order':dict(),
                        'vowel_row_header_order':dict(),'vowel_column_header_order': dict(),
                        'consList': list(), 'vowelList': list(), 'non_segment_symbols': ['#'],
                        'vowel_features': [None], 'cons_features': [None], 'voice_feature': None, 'rounded_feature': None,
                        'diph_feature': None, 'isNew': True, 'filterNames': False}

def force_update(corpus):
    #This runs through known incompatibilities with previous version of PCT and tries to patch them all up. This gets
    #called from the LoadCorpusDialog.forceUpdate() in iogui.py
    corpus.inventory = modernize_inventory_attributes(corpus.inventory)
    corpus.inventory,corpus.specifier = modernize_features(corpus.inventory, corpus.specifier)
    corpus.inventory.isNew = False
    if corpus.has_transcription:
        if not [seg for seg in corpus.inventory if not seg=='#']:
            #for some reason, the segment inventory is an empty list in the old IPHOD corpus, and potentially other
            #old PCT files too
            segs = set()
            for word in corpus:
                for seg in word.transcription:
                    segs.add(seg)
            for seg in segs:
                corpus.inventory.segs[seg] = Segment(seg,corpus.specifier.specify(seg))

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
    for attribute,default in inventory_attributes.items():
        if not hasattr(inventory, attribute):
            setattr(inventory, attribute, default)
        elif not getattr(inventory, attribute) and default:
            setattr(inventory, attribute, default)
    if not inventory.segs and inventory._data:
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
            specifier.matrix[seg.symbol] = specifier.matrix[seg.symbol].features

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