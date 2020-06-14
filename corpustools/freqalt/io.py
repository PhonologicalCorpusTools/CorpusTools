import csv


def print_freqalt_results(output_filename, related_list):
    with open(output_filename, mode='w', encoding='utf-8-sig', newline='') as outf2:
        writer = csv.writer(outf2,delimiter= '\t')
        writer.writerow(['FirstWord', 'SecondWord', 'RelatednessScore'])
        for line in related_list:
            writer.writerow(line)
