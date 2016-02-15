import collections

def findSyllableShapes(corpus, inventory, nucleus, stop_check=None, call_back=None):

    onsets, codas = parseCorpus(corpus, inventory, nucleus, stop_check, call_back)

    onset_strings = collections.defaultdict(int)
    for onset,freq in onsets.items():
        string = 'C'*len(onset)
        onset_strings[string] += freq
    coda_strings = collections.defaultdict(int)
    for coda,freq in codas.items():
        string = 'C'*len(coda)
        coda_strings[string] += freq

    syll_shapes = [[k,str(v),'',''] if k
                   else ['EMPTY', str(v),'','']
                   for (k,v) in onset_strings.items()]
    syll_shapes.extend([['','',k,str(v)]
                        if k else
                        ['','','EMPTY',str(v)]
                        for (k,v) in coda_strings.items()])
    return syll_shapes


def parseCorpus(corpus, inventory, nucleus, stop_check, call_back):

    tier = corpus.sequence_type
    nucleus_name = nucleus[1:]
    nucleus_sign = nucleus[0]
    onsets, codas = lookAtWordEdges(corpus, inventory, nucleus_name, nucleus_sign, tier, stop_check, call_back)

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

        # go left to right, gather onsets
        for pos, seg in word.enumerate_symbols(tier):
            features = inventory.segs[seg].features
            if not features[nucleus_name] == nucleus_sign:
                cur_onset.append(seg)
            else:
                cur_onset = ''.join(cur_onset)
                for n in reversed(range(len(cur_onset))):
                    #check if this onset contains a known coda from the search above
                    if cur_onset[:n+1] in codas:
                        codas[cur_onset[:n+1]] += 1
                        onsets[cur_onset[n+1:]] += 1
                        cur_onset = list()
                        break
                else:
                    onsets[cur_onset] += 1
                    cur_onset = list()

    return onsets, codas


def lookAtWordEdges(corpus, inventory, nucleus_name, nucleus_sign, tier, stop_check, call_back):

    onsets = collections.defaultdict(int)
    codas = collections.defaultdict(int)
    if call_back is not None:
        call_back('Looking for onsets and codas...')
        call_back(0, len(corpus))
        cur = 0

    #Look for things at the beginnings of words which are necessarily onsets
    for word in corpus:
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 1000 == 0:
                call_back(cur)
        cur_onset = list()
        cur_coda = list()
        for pos,seg in word.enumerate_symbols(tier):
            features = inventory.segs[seg].features
            if not features[nucleus_name] == nucleus_sign:
                cur_onset.append(seg)
            else:
                cur_onset = ''.join(cur_onset)
                onsets[cur_onset] += 1
                break

        for pos,seg in word.enumerate_symbols(tier, reversed=True):
            features = inventory.segs[seg].features
            if not features[nucleus_name] == nucleus_sign:
                cur_coda.append(seg)
            else:
                if cur_coda:
                    cur_coda.reverse()
                    cur_coda = ''.join(cur_coda)
                    codas[cur_coda] += 1
                break
    return onsets, codas
