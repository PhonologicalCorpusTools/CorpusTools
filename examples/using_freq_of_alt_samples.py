#!/usr/bin/env python

import freq_of_alt
import corpustools
import time

def freq_of_alt_samples(corpus_name, s1, s2, relator_type, string_type, count_what, output_filename, threshold, phono_align, min_pairs_okay, num_of_samples, sample_size):
    print('Building Corpus')
    start_time = time.time()
    factory = corpustools.CorpusFactory()
    corpus = factory.make_corpus(corpus_name, features='hayes', size='all')
    end_time = time.time()
    print('Corpus Complete')
    print('Corpus creation time: ' + str(end_time-start_time))

    freq_of_alt_total = 0
    for i in range(num_of_samples):
        sub_corpus = corpus.get_random_subset(sample_size)
        freq = freq_of_alt.Freqor('iphod', None, sub_corpus)
        output_filename = output_filename.replace('.txt.', '')
        curr_freq_of_alt = freq.calc_freq_of_alt(s1, s2, relator_type, string_type, count_what, output_filename + '_' + str(i) + '.txt', threshold, phono_align, min_pairs_okay)
        freq_of_alt_total += curr_freq_of_alt
    
    print('Average frequency of alternation: ' + str(freq_of_alt_total/num_of_samples))
    
    

freq = freq_of_alt.Freqor('iphod', 4000)
freq.calc_freq_of_alt('s', 'ʃ', 'string_similarity', 'transcription', 'type', 'ess_esh_alt_with_min_pairs.txt', 0, 1, 1)

#freq_of_alt_samples('iphod', 's', 'ʃ', 'string_similarity', 'transcription', 'ess_esh_alt_with_min_pairs.txt', 0, 1, 1, 2, 2000)


