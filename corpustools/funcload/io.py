import csv


def save_minimal_pairs(output_filename, to_output, write_header=True):
    if isinstance(output_filename, str):
        outf = open(output_filename, mode='w', encoding='utf-8-sig', newline='')
        needs_closed = True
    else:
        outf = output_filename
        needs_closed = False

    writer = csv.writer(outf, delimiter='\t')
    if write_header:
        writer.writerow(['FIRST_SEGMENT', 'SECOND_SEGMENT',
                         'FIRST_WORD', 'FIRST_WORD_TRANSCRIPTION',
                         'SECOND_WORD', 'SECOND_WORD_TRANSCRIPTION'])
    for _, _, ret_dict in to_output:
        for seg_pair, word_pair_set in ret_dict.items():
            for word_pair in word_pair_set:
                writer.writerow([seg_pair[0], seg_pair[1],
                                 word_pair[0][0], word_pair[0][1],
                                 word_pair[1][0], word_pair[1][1]])

    if needs_closed:
        outf.close()
