import csv


def save_minimal_pairs(output_filename, to_output, write_header = False):
    if isinstance(output_filename, str):
        outf = open(output_filename, mode='w', encoding='utf-8')
        needs_closed = True
    else:
        outf = output_filename
        needs_closed = False
    writer = csv.writer(outf, delimiter='\t')
    if write_header:
        writer.writerow(['First segment', 'Second segment', 'First word', 'Second word'])
    for o in to_output:
        pair, minimal_pairs = o
        line = [pair[0], pair[1]]
        for minpair in minimal_pairs:
            writer.writerow(line + [str(minpair[0][0]), str(minpair[1][0])])
    if needs_closed:
        outf.close()
