'''
Created on May 12, 2014

@author: Michael
'''
import string_similarity
import time
import re

def morph_relatedness_word(corpus_name, relator_type, string_type, count_what, query, threshold=None, ready_made_corpus = None, output_filename = None):
    """Given input parameters, creates a text file containing a target word and all other words in a corpus with a relatedness score

    Parameters
    ----------
    corpus_name: string
        The name of the corpus to be used, e.g. 'Iphod'
    relator_type: string
        The type of relator to be used to measure relatedness, e.g. 'string_similarity'
    string_type: string
        The type of segments to be used ('spelling' = roman letters, 'transcription' = IPA symbols)
    count_what: string
        The type of frequency, either 'type' or 'token'
    query: string
        The target word to be compared to the corpus
    threshold: double
        The lowest relatedness desired in the output file, defaults to None (i.e. output will have all words no matter how unrelated)
    ready_made_corpus: Corpus
        An already built corpus, if none if provided, one will be built

    Returns
    -------
    None - writes a text file
    """

    relator = relator_type.lower()
    if relator == 'string_similarity':
        relator = string_similarity.Relator(corpus_name, ready_made_corpus)
    elif relator == 'shared_morphemes':
        relator = shared_morphs.Relator(corpus_name, ready_made_corpus)
    elif relator == 'axb':
        relator = axb.Relator(corpus_name)
    else:
        print('Relator type not valid')
        return


    #output_filename = query + '_' + corpus_name + '_' + relator_type + '_' + string_type+'.txt'
    start_time = time.time()
    related_data = relator.relate(query, string_type, count_what)
    end_time = time.time()

    with open(output_filename, mode='w', encoding='utf-8') as outf:
        if not isinstance(query, str):
            query = ''.join([seg.symbol for seg in w])
        print('Morphological relatedness to the word using the {} algorithm: {}\r\n\r\n'.format(relator_type, query), file=outf)
        #print('This algorithm ran in: ' + str(end_time-start_time))
        for word, score in related_data:
            if threshold != None:
                if score[0] >= threshold:
                    outf.write(word + '\t' + str(score) + '\n')
                else:
                    pass
            else:
                outf.write(word + '\t' + str(score) + '\n')

def morph_relatedness_pairs(corpus_name, relator_type, string_type, count_what, input_data, output_filename=None, threshold=None, ready_made_corpus = None):
    """Given an input of pairs of words to compare to each other, returns such pairs and their relatedness scores

    Parameters
    ----------
    corpus_name: string
        The name of the corpus to be used, e.g. 'Iphod'
    relator_type: string
        The type of relator to be used to measure relatedness, e.g. 'string_similarity'
    string_type: string
        The type of segments to be used ('spelling' = roman letters, 'transcription' = IPA symbols)
    count_what: string
        The type of frequency, either 'type' or 'token'
    input_data: string - .txt filename
        The name of a .txt file which contains pairs of words separated by tabs with each pair on a new line
    output_name: string
        The name of the desired output file, if output_filename == None, no file will be created and instead the data will be returned as a list
    threshold: double
        The lowest relatedness desired in the output file, defaults to None (i.e. output will have all words no matter how unrelated)
    ready_made_corpus: Corpus
        An already built corpus, if none if provided, one will be built

    Returns
    -------
    If output_filename exists, nothing is returned, a textfile is created
    If output_filename == None, a list the pairs and their relatedness scores is returned
    """

    relator = relator_type.lower()
    with open(input_data, mode='r', encoding='utf-8') as inf:
        lines = inf.readlines()

        if relator == 'string_similarity':
            relator = string_similarity.Relator(corpus_name, ready_made_corpus)
            freq_base = relator.make_freq_base(string_type)
            related_data = list()
            start_time = time.time()
            for line in lines:
                w1, w2 = line.split('\t')
                w1, w2 = re.sub(r'\s+', '', w1), re.sub(r'\s+', '', w2)
                score = relator.string_sim(w1, w2, freq_base)
                related_data.append( (w1, w2, score) )
            end_time = time.time()

        elif relator == 'shared_morphemes':
            relator = shared_morphs.Relator(corpus_name, ready_made_corpus)
        elif relator == 'axb':
            relator = axb.Relator(corpus_name)
        else:
            print('Relator type not valid')
            return

        print('Run time for relating: ' + str(end_time-start_time))


        related_data_return = list()
        for w1, w2, score in related_data:
            if threshold != None:
                if score >= threshold:
                    related_data_return.append( (w1, w2, score) )
                else:
                    pass
            else:
                related_data_return.append( (w1, w2, score) )

        if output_filename == 'return_data':
            return related_data_return
        else:
            with open(output_filename, mode='w', encoding='utf-8') as outf:
                for w1, w2, score in related_data_return:
                    outf.write('{}\t{}\t{}\n'.format(w1, w2, score))





