import csv

def load_words_neighden(path):
    output = set()
    with open(path,'r') as f:
        for line in f:
            fields = line.strip().split(None)
            output.update(fields)
    return list(output)

def print_neighden_results(output_filename, neighbors):
    with open(output_filename, mode='w', encoding='utf-8') as outf:
        writer = csv.writer(outf,delimiter='\t')
        for n in neighbors:
            writer.writerow([n])
