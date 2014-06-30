'''
Created on May 12, 2014

@author: Michael
'''
import khorsi
import edit_distance
import phono_edit_distance
import time
import re

def string_similarity_word(corpus_name, relator_type, string_type, count_what, query, min_rel=None, max_rel=None, ready_made_corpus = None, output_filename = None):
    """Given input parameters, creates a text file containing a target word and all other words in a corpus with a relatedness score

    Parameters
    ----------
    corpus_name: string
        The name of the corpus to be used, e.g. 'Iphod'
    relator_type: string
        The type of relator to be used to measure relatedness, e.g. 'khorsi'
    string_type: string
        The type of segments to be used ('spelling' = roman letters, 'transcription' = IPA symbols)
    count_what: string
        The type of frequency, either 'type' or 'token'
    query: string
        The target word to be compared to the corpus
    max_rel: double
        Filters out all words that are higher than max_rel from a relatedness measure
    min_rel: double
        Filters out all words that are lower than min_rel from a relatedness measure
    ready_made_corpus: Corpus
        An already built corpus, if none if provided, one will be built

    Returns
    -------
    None - writes a text file
    """

    relator = relator_type.lower()
    if relator == 'khorsi':
        relator = khorsi.Relator(corpus_name, ready_made_corpus)
    elif relator == 'edit_distance':
        relator = edit_distance.Relator(corpus_name, ready_made_corpus)
    elif relator == 'phono_edit_distance':
        relator = phono_edit_distance.Relator(corpus_name, ready_made_corpus)
    elif relator == 'axb':
        relator = axb.Relator(corpus_name)
    else:
        print('Relator type not valid')
        return

    related_data = relator.mass_relate(query, string_type, count_what)
    
    filtered_data = list();
    for score, word in related_data:
        if min_rel != None:
            if max_rel != None:
                if min_rel <= score[0] <= max_rel:
                    filtered_data.append( (score, word) )
            elif min_rel <= score[0]:
                filtered_data.append( (score, word) )
        elif max_rel != None and score[0] <= max_rel:
            filtered_data.append( (score, word) )
        else:
            filtered_data.append( (score, word) )
                            
    if output_filename == 'return_data':
        return filtered_data
    else:
        print_one_word_results(output_filename, query, string_type, filtered_data, min_rel, max_rel)


def print_one_word_results(output_filename, query, string_type, related_data, min_rel, max_rel):
    with open(output_filename, mode='w', encoding='utf-8') as outf:
        for score, word in related_data:
            if isinstance(word, str):
                w = word
            else:
                w = getattr(word, string_type)
                
            if not isinstance(w, str):
                w = ''.join([seg.symbol for seg in w])
            
            if isinstance(score, list):
                score = score[0]
            
            outf.write(w + '\t' + str(score) + '\n')
            
def string_similarity_single_pair(corpus_name, relator_type, string_type, w1, w2, ready_made_corpus=None):
    relator = relator_type.lower()
    if relator == 'khorsi':
        relator = khorsi.Relator(corpus_name, ready_made_corpus)
        freq_base = relator.make_freq_base(string_type)
        score = relator.khorsi(w1, w2, freq_base, string_type)
    elif relator == 'edit_distance':
        relator = edit_distance.Relator(corpus_name, ready_made_corpus)
        score = relator.edit_distance(w1, w2, string_type)
    elif relator == 'phono_edit_distance':
        relator = phono_edit_distance.Relator(corpus_name, ready_made_corpus)
        score = relator.phono_edit_distance(w1, w2, string_type)
    else:
        raise AttributeError('Relator type \'{}\' is not valid'.format(relator_type))
    
    w1, w2 = relator.get_word_string_type(w1, w2, string_type)
    return ((w1, w2, score))


def string_similarity_pairs(corpus_name, relator_type, string_type, count_what, input_data, output_filename=None, min_rel=None, max_rel=None, ready_made_corpus = None):
    """Given an input of pairs of words to compare to each other, returns such pairs and their relatedness scores

    Parameters
    ----------
    corpus_name: string
        The name of the corpus to be used, e.g. 'Iphod'
    relator_type: string
        The type of relator to be used to measure relatedness, e.g. 'khorsi'
    string_type: string
        The type of segments to be used ('spelling' = roman letters, 'transcription' = IPA symbols)
    count_what: string
        The type of frequency, either 'type' or 'token'
    input_data: string - .txt filename
        The name of a .txt file which contains pairs of words separated by tabs with each pair on a new line
    output_name: string
        The name of the desired output file, if output_filename == None, no file will be created and instead the data will be returned as a list
    max_rel: double
        Filters out all words that are higher than max_rel from a relatedness measure
    min_rel: double
        Filters out all words that are lower than min_rel from a relatedness measure
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

        if relator == 'khorsi':
            relator = khorsi.Relator(corpus_name, ready_made_corpus)
            freq_base = relator.make_freq_base(string_type)
            related_data = list()

            for line in lines:
                w1, w2 = line.split('\t')
                w1, w2 = re.sub(r'\s+', '', w1), re.sub(r'\s+', '', w2)
                score = relator.khorsi(w1, w2, freq_base, string_type)
                w1, w2 = relator.get_word_string_type(w1, w2, string_type)
                related_data.append( (w1, w2, score) )

        elif relator == 'edit_distance':
            relator = edit_distance.Relator(corpus_name, ready_made_corpus)
            related_data = list()

            for line in lines:
                w1, w2 = line.split('\t')
                w1, w2 = re.sub(r'\s+', '', w1), re.sub(r'\s+', '', w2)
                score = relator.edit_distance(w1, w2, string_type)
                w1, w2 = relator.get_word_string_type(w1, w2, string_type)
                related_data.append( (w1, w2, score) )

        elif relator == 'axb':
            relator = axb.Relator(corpus_name)
        else:
            print('Relator type not valid')
            return


        filtered_data = list()
        for w1, w2, score in related_data:
            if score == None: #A relatedness score is unavailable
                continue
            elif min_rel != None:
                if max_rel != None:
                    if min_rel <= score <= max_rel:
                        filtered_data.append( (w1, w2, score) )
                elif min_rel <= score:
                    filtered_data.append( (w1, w2, score) )
            elif max_rel != None and score <= max_rel:
                filtered_data.append( (w1, w2, score) )
            else:
                filtered_data.append( (w1, w2, score) )

        if output_filename == 'return_data':
            return filtered_data
        else:
            print_pairs_results(output_filename, filtered_data)

def print_pairs_results(output_filename, related_data_return):
    with open(output_filename, mode='w', encoding='utf-8') as outf:
        for w1, w2, score in related_data_return:
            outf.write('{}\t{}\t{}\n'.format(w1, w2, score))





