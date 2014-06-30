#!/usr/bin/env python

import freq_of_alt
import corpustools
import time

def freq_of_alt_samples(corpus_name, s1, s2, relator_type, string_type, count_what, output_filename, min_rel, max_rel, phono_align, min_pairs_okay, num_of_samples, sample_size, features = 'hayes', ready_made_corpus = None):
    if ready_made_corpus is not None:
        corpus = ready_made_corpus
    else:
        print('Building Corpus')
        start_time = time.time()
        factory = corpustools.CorpusFactory()
        corpus = factory.make_corpus(corpus_name, features='spe', size='all')
        end_time = time.time()
        print('Corpus Complete')
        print('Corpus creation time: ' + str(end_time-start_time))

    freq_of_alt_total = 0
    for i in range(num_of_samples):
        sub_corpus = corpus.get_random_subset(sample_size)
        freq = freq_of_alt.Freqor('iphod', ready_made_corpus = sub_corpus)
        output_filename = output_filename.replace('.txt.', '')
        curr_freq_of_alt = freq.calc_freq_of_alt(s1, s2, relator_type, string_type, count_what, output_filename + '_' + str(i) + '.txt', min_rel, max_rel, phono_align, min_pairs_okay)
        freq_of_alt_total += curr_freq_of_alt
    
    print('Average frequency of alternation: ' + str(freq_of_alt_total/num_of_samples))
    
    

freq = freq_of_alt.Freqor('iphod', 1000)
freq.calc_freq_of_alt('s', 'ʃ', 'phono_edit_distance', 'transcription', 'type', 'ess_esh_alt_with_min_pairs2000.txt', 0,20, 1, 1)

#freq_of_alt_samples('iphod', 's', 'ʃ', 'phono_edit_distance', 'transcription', 'type', 'ess_esh_alt_with_min_pairs', 0, 30, 1, 1, 2, 2000)


