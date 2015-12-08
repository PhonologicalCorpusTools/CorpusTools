def modernize_inventory(inventory):
    if hasattr(inventory, '_data'):
        setattr(inventory, 'segs', inventory._data)
        del inventory._data
    else:
        raise PCTError('Corpus is from an earlier version which is not supported')


    setattr(inventory, 'isNew', True)
    return inventory