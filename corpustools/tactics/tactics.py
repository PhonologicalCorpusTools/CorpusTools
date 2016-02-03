
def findSyllableShapes(corpus, inventory, nucleus, stop_check=None, call_back=None):
    onsets, medials, codas = parseCorpus(corpus, inventory, nucleus, stop_check, call_back)

    max_onset = max([len(o) for o in onsets])
    max_coda = max([len(c) for c in codas])
    onset_string = 'C' * max_onset
    coda_string = 'C' * max_coda

    onsets = [o if o else ['EMPTY'] for o in onsets]
    codas = [c if c else ['EMPTY'] for c in codas]

    print('The biggest possible syllable has the shape {}V{}'.format(onset_string, coda_string))
    print('Onsets: ')
    print(','.join([''.join(o) for o in onsets]))
    print('Codas: ')
    print(','.join([''.join(c) for c in codas]))

    return(onsets, medials, codas, onset_string, coda_string)


def parseCorpus(corpus, inventory, nucleus, stop_check, call_back):

    onsets = list()
    medials = list()
    codas = list()
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
        last_pos = word.get_len(tier)
        first_pos = 0
        cur_onset = list()
        cur_coda = list()
        cur_medial = list()
        # go left to right, gather onsets
        for pos, seg in word.enumerate_symbols(tier):
            features = inventory.segs[seg].features
            if not features[nucleus_name] == nucleus_sign:
                cur_onset.append(seg)
            else:
                if not cur_onset in onsets:
                    onsets.append(cur_onset)
                first_pos = pos
                break

        #go right to left, add remains to codas
        for pos, seg in word.enumerate_symbols(tier, reversed=True):
            features = inventory.segs[seg].features
            if not features[nucleus_name] == nucleus_sign:
                cur_coda.append(seg)
            else:
                if not cur_coda in codas:
                    codas.append(cur_coda)
                last_pos = pos
                break

                # for pos in range(first_pos, last_pos):
                #     seg = word[pos]
                #     features = self.inventory.segs[seg].features
                #     if not seg.features[nucleus_name] == nucleus_sign:
                #         cur_medial.append(seg)
                #     else:
                #         if not cur_medial in self.medials:
                #             self.medials.append(cur_medial)
                #         cur_medial = list()

                # meds = [x for x in medials if x in onsets or x in codas]
                # for m in meds:
                # if len(m) == 1:
                #         if len(codas)==1 and codas[0]==[]: #no coda
                #             onsets.append(codas[0])#this must be an onset
                #
                #     m = reversed(m)
                #     cur_string = list()
                #     for seg in m:
                #         cur_string.append(seg)
                #         if cur_string in onsets:
                #             continue
    return onsets, medials, codas