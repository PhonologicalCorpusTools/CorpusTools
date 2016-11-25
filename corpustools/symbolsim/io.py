

def print_pairs_results(output_filename, related_data_return):
    with open(output_filename, mode='w', encoding='utf-8-sig') as outf:
        for w1, w2, score in related_data_return:
            outf.write('{}\t{}\t{}\n'.format(w1, w2, score))

def print_one_word_results(output_filename, query, string_type, related_data, min_rel, max_rel):
    with open(output_filename, mode='w', encoding='utf-8-sig') as outf:
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

def read_pairs_file(path):
    output = []
    with open(path,'r') as f:
        for line in f:
            fields = line.strip().split('\t')
            output.append(fields)
    return output
