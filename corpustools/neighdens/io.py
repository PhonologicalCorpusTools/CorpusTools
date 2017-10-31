import csv
from corpustools.corpus.classes import Word

def load_words_neighden(path):
    output = list()
    with open(path,'r', encoding='utf-8-sig') as f:
        for line in f:
            fields = [x for x in line.strip().split(None) if x != '']
            if len(fields) > 1:
                fields[1] = fields[1].split('.')
                fields = Word(spelling=fields[0], transcription = fields[1])
            elif len(fields) == 1:
                fields = fields[0]
            else:
                continue
            output.append(fields)
    return output

def print_neighden_results(output_filename, neighbors):
    with open(output_filename, mode='w', encoding='utf-8-sig') as outf:
        writer = csv.writer(outf,delimiter='\t')
        for n in neighbors:
            writer.writerow([n])

def print_all_neighden_results(output_filename, neighors_dict):
    with open(output_filename, mode='w', encoding='utf-8-sig') as outf:
        for word,neighbors in neighors_dict.items():
            if not neighbors:
                print(word, file=outf)
            else:
                line = '\t'.join([word, '\t'.join([n for n in neighbors])])
                print(line, file=outf)