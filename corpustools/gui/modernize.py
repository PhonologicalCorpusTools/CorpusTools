import random
from corpustools.corpus.classes.lexicon import Segment


def isNotSupported(corpus):
    if corpus.name.lower() == 'iphod':
        return True
    else:
        return False

def need_update(corpus):
    if hasattr(corpus, 'isNew'):
        return False
    else:
        return True

# def modernize_inventory(inventory):
#     if hasattr(inventory, '_data'):
#         #turn the old ._data attribute into a .segs attribute
#         #._data is now used for something else, so clear the old one
#         inventory.segs = inventory._data.copy()
#         inventory._data = dict()
#     else:
#         raise PCTError('Corpus is from an earlier version which is no longer supported')
#
#     setattr(inventory, 'isNew', True)
#     return inventory

def modernize_features(inventory, specifier):
    #In some older versions of PCT, the FeatureMatrix returns Segments, instead of feature lists
    seg1 = random.choice(list(inventory.segs.values()))
    if isinstance(seg1.features, Segment):
        for seg in inventory:
            inventory[seg.symbol].features = specifier.matrix[seg.symbol].features
    return inventory