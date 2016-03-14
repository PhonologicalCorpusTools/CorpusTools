import argparse
import os
import sys
import codecs
import ntpath
import csv
import re

# default to importing from CorpusTools repo
base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(0,base)

from corpustools.visualize import visualize


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def main():

    #### Parse command-line arguments
    parser = argparse.ArgumentParser(description = \
             'Phonological CorpusTools: visualization of segment inventory')
    parser.add_argument('distance_file_name', help='Name of input distance file')
    parser.add_argument('-m', '--visualization_method', default='pca', help="Method of visualization: any of principal components analysis ('pca'), hierarchical clustering ('hc'), or a heatmap ('hm')")
    parser.add_argument('-v', '--value_column', default='result', type=str, help='header for column containing distance values')
    parser.add_argument('-s', '--segment_column', default='segment(s)', type=str, help='header for column containing segment pairs')
    parser.add_argument('-d', '--column_delimiter', default='\t', type=str, help='header for column containing segment pairs')

    args = parser.parse_args()

    ####

    delimiter = codecs.getdecoder("unicode_escape")(args.column_delimiter)[0]

    try: # Full path specified
        with open(args.distance_file_name) as infile:
            reader = csv.DictReader(infile, delimiter=delimiter)
            visualize(reader, args.visualization_method, args.value_column, args.segment_column)
    except FileNotFoundError:
        try: # Unix filepaths
            filename, extension = os.path.splitext(os.path.dirname(os.path.realpath(__file__))+'/'+args.csv_file_name)
            reader = csv.DictReader(os.path.dirname(os.path.realpath(__file__))+'/'+args.csv_file_name)
            visualize(reader, args.visualization_method, args.value_column, args.segment_column)
        except FileNotFoundError: # Windows filepaths
            filename, extension = os.path.splitext(os.path.dirname(os.path.realpath(__file__))+'\\'+args.csv_file_name)
            reader = csv.DictReader(os.path.dirname(os.path.realpath(__file__))+'\\'+args.csv_file_name)
            visualize(reader, args.visualization_method, args.value_column, args.segment_column)




if __name__ == '__main__':
    main()