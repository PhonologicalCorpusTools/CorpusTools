import csv


def save_minimal_pairs(output_filename, to_output):
    with open(output_filename, mode='w', encoding='utf-8') as outf:
        writer = csv.writer(outf, delimiter='\t')
        writer.writerow(['First segment', 'Second segment', 'First word', 'Second word'])
        for o in to_output:
            pair, minimal_pairs = o
            line = [pair[0], pair[1]]
            for minpair in minimal_pairs:
                writer.writerow(line + [minpair[0], minpair[1]])
