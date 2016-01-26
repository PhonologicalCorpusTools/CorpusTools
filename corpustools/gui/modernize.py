import random
from corpustools.corpus.classes.lexicon import Segment


def isNotSupported(corpus):
    if corpus.name.lower() == 'iphod':
        return True
    else:
        return False

def need_update(corpus):
    #This should be checking for the version number instead
    if hasattr(corpus, 'isNew'):
        return False
    else:
        return True

def modernize_features(inventory, specifier):
    #In some older versions of PCT, the FeatureMatrix returns Segments, instead of feature lists
    seg1 = random.choice(list(inventory.segs.values()))
    if isinstance(seg1.features, Segment):
        for seg in inventory:
            inventory[seg.symbol].features = specifier.matrix[seg.symbol].features

    if not hasattr(inventory, 'cons_features'):
        inventory.cons_features = None

    if not hasattr(inventory, 'vowel_features'):
        inventory.vowel_features = inventory.vowel_feature
        del inventory.vowel_feature

    return inventory