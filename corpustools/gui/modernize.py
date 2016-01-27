import random
from corpustools.corpus.classes.lexicon import Segment
import corpustools
VERSION = corpustools.__version__

#it would be better to import these attributes from .models.InventoryModel, but this creates a circular import problem
inventory_attributes = {'segs': dict(), 'features': dict(), 'possible_values': list(), 'stresses': list(),
                        'consColumns': set(),'consRows': set(),'vowelColumns': set(), 'vowelRows': set(),
                        'cons_column_data': dict(), 'cons_row_data': dict(),'vowel_column_data': dict(),
                        'vowel_row_data': dict(),'uncategorized': list(), '_data': dict(), 'all_rows': dict(),
                        'all_columns': dict(),'vowel_column_offset': int(), 'vowel_row_offset': int(),
                        'cons_column_header_order':dict(),'cons_row_header_order':dict(),'vowel_row_header_order':dict(),
                        'vowel_column_header_order': dict(),'consList': list(), 'vowelList': list(),
                        'vowel_features': None, 'cons_features': None, 'voice_feature': None, 'rounded_feature': None,
                        'diph_feature': None, 'isNew': True}

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

def modernize_inventory_attributes(inventory):
    for attribute,default in inventory_attributes.items():
        if not hasattr(inventory, attribute):
            setattr(inventory,attribute,default)
    return inventory

def modernize_features(inventory, specifier):
    #In some older versions of PCT, the FeatureMatrix returns Segments, instead of feature lists
    seg1 = random.choice([seg for seg in inventory.segs.values() if not seg.symbol=='#'])
    if isinstance(seg1.features, Segment):
        for seg in inventory:
            inventory[seg.symbol].features = specifier.matrix[seg.symbol]

    if not hasattr(inventory, 'cons_features'):
        inventory.cons_features = None

    if not hasattr(inventory, 'vowel_features'):
        inventory.vowel_features = inventory.vowel_feature
        del inventory.vowel_feature

    return inventory