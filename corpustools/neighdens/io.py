import csv
from corpustools.corpus.classes import Word

def load_words_neighden(path, file_sequence_type='spelling'):
    output = list()
    with open(path,'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            output.append(line)
    return output

def print_neighden_results(output_filename, neighbors, output_format):
    with open(output_filename, mode='w', encoding='utf-8-sig', newline='') as outf:
        writer = csv.writer(outf,delimiter='\t')
        for n in neighbors:
            output = str(getattr(n, output_format)).replace('.','')
            writer.writerow([output])

def print_all_neighden_results(output_filename, neighors_dict):
    with open(output_filename, mode='w', encoding='utf-8-sig') as outf:
        print('Word\tDensity\tNeighbours', file=outf)
        for word,neighbors in neighors_dict.items():
            if not neighbors:
                print('\t'.join([word, '0', '']), file=outf)
            else:
                line = '\t'.join([word,
                                  str(len(neighbors)-1),
                                  ','.join([str(n).replace('.', '') for n in neighbors[1:]])])
                #the -1 and the [1:] slice are to account for words being considered their own neighbours
                #it's easier to fix this here than to mess with the ND algorithm
                print(line, file=outf)