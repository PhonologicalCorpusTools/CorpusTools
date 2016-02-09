import collections

def findSyllableShapes(corpus, inventory, nucleus, stop_check=None, call_back=None):
    onsets, codas = parseCorpus(corpus, inventory, nucleus, stop_check, call_back)

    max_onset = max([len(o) for o in list(onsets.keys())])
    max_coda = max([len(c) for c in list(codas.keys())])

    onset_strings = collections.defaultdict(int)
    for onset,freq in onsets.items():
        string = 'C'*len(onset)
        onset_strings[string] += freq

    coda_strings = collections.defaultdict(int)
    for coda,freq in codas.items():
        string = 'C'*len(coda)
        coda_strings[string] += freq

    syll_shapes = [[k,str(v),'',''] if k else ['EMPTY', str(v),'',''] for (k,v) in onset_strings.items()]
    syll_shapes.extend([['','',k,str(v)] if k else ['','','EMPTY',str(v)] for (k,v) in coda_strings.items()])

    # print('The biggest possible syllable has the shape {}V{}'.format(onset_string, coda_string))
    # print('Onsets: ')
    # print(','.join([''.join(o) for o in onsets]))
    # print('Codas: ')
    # print(','.join([''.join(c) for c in codas]))

    return syll_shapes


def parseCorpus(corpus, inventory, nucleus, stop_check, call_back):

    onsets = collections.defaultdict(int)
    codas = collections.defaultdict(int)
    tier = corpus.sequence_type
    nucleus_name = nucleus[1:]
    nucleus_sign = nucleus[0]
    if call_back is not None:
        call_back('Looking for phonotactic patterns...')
        call_back(0, len(corpus))
        cur = 0
    for word in corpus:
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 1000 == 0:
                call_back(cur)
        cur_onset = list()
        cur_coda = list()
        # go left to right, gather onsets
        for pos, seg in word.enumerate_symbols(tier):
            features = inventory.segs[seg].features
            if not features[nucleus_name] == nucleus_sign:
                cur_onset.append(seg)
            else:
                cur_onset = ''.join(cur_onset)
                onsets[cur_onset] += 1
                break

        #go right to left, add remains to codas
        for pos, seg in word.enumerate_symbols(tier, reversed=True):
            features = inventory.segs[seg].features
            if not features[nucleus_name] == nucleus_sign:
                cur_coda.append(seg)
            else:
                cur_coda = ''.join(cur_coda)
                codas[cur_coda] += 1
                break

    return onsets, codas