'''
Created on May 12, 2014

@author: Michael
'''
import string_similarity
import time
import re

def morph_relatedness_word(corpus_name, relator_type, string_type, query, threshold=None, ready_made_corpus = None):
    relator = relator_type.lower()
    if relator == 'string_similarity':
        relator = string_similarity.Relator(corpus_name, ready_made_corpus)
    elif relator == 'shared_morphemes':
        relator = shared_morphs.Relator(corpus_name, ready_made_corpus)
    elif relator == 'axb':
        relator = axb.Relator(corpus_name)
    else:
        relator = None
    
    output_filename = query + '_' + corpus_name + '_' + relator_type + '_' + string_type+'.txt'
    start_time = time.time()
    related_data = relator.relate(query, string_type)
    end_time = time.time() 
    
    with open(output_filename, mode='w', encoding='utf-8') as outf:
        if not isinstance(query, str):
            query = ''.join([seg.symbol for seg in w])
        print('Morphological relatedness to the word using the {} algorithm: {}\r\n\r\n'.format(relator_type, query), file=outf)
        print('This algorithm ran in: ' + str(end_time-start_time))
        for word, score in related_data:
            if threshold != None:
                if score[0] >= threshold:
                    outf.write(word + '\t' + str(score) + '\n')
                else:
                    pass
            else:
                outf.write(word + '\t' + str(score) + '\n')

def morph_relatedness_pairs(corpus_name, relator_type, string_type, input_data, output_filename, threshold=None, ready_made_corpus = None):
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
            relator = None
        
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
                    outf.write('{}\t{}: {}\n'.format(w1, w2, score))

            


        
