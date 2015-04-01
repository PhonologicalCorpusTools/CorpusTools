import argparse
import os
import codecs
import ntpath
import csv
import re

import numpy as np

from scipy.cluster.hierarchy import linkage, dendrogram

from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection

from sklearn import manifold
from sklearn.metrics import euclidean_distances
from sklearn.decomposition import PCA


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def organize_data(reader, visualization_method, value_column, segment_column):
    raw_data = {tuple([x[1:-1] for x in re.findall("'.+?'", r[segment_column])]): float(r[value_column]) for r in reader}
    all_segments = list(set([segment for pair in raw_data for segment in pair]))

    if visualization_method == 'mds':
        m = np.zeros(shape=(len(all_segments),len(all_segments)), dtype=float)
        for i, s1 in enumerate(all_segments):
            for j, s2 in enumerate(all_segments):
                if j > i:
                    try:
                        value = raw_data[(s1, s2)]
                    except KeyError:
                        value = raw_data[(s2, s1)]
                    m[i][j] = value
                    m[j][i] = value
        return (all_segments, m)

    elif visualization_method == 'hc':
        a = np.array([], dtype=float)
        for i, s1 in enumerate(all_segments):
            for j, s2 in enumerate(all_segments):
                if j > i:
                    try:
                        value = raw_data[(s1, s2)]
                    except KeyError:
                        value = raw_data[(s2, s1)]
                    a = np.append(a, value)
        a = (max(a) * 2) - a
        return (all_segments, a)


def visualize(reader, visualization_method, value_column, segment_column):
    labels, data = organize_data(reader, visualization_method, value_column, segment_column)

    if visualization_method == 'hc':
        link = linkage(data)
        dendrogram(link, leaf_label_func=lambda i: labels[i])
        plt.gcf()
        plt.show()

    if visualization_method == 'mds':
        n = len(labels)
        data -= data.mean()
        clf = PCA(n_components=2)
        data = clf.fit_transform(data)

        similarities = euclidean_distances(data)

        # Add noise to the similarities
        noise = np.random.rand(n, n)
        noise = noise + noise.T
        noise[np.arange(noise.shape[0]), np.arange(noise.shape[0])] = 0
        similarities += noise


        fig = plt.figure(1)
        ax = plt.axes([0., 0., 1., 1.])

        similarities = similarities.max() / similarities * 100
        similarities[np.isinf(similarities)] = 0

        plt.scatter(data[:, 0], data[:, 1], c='r', s=20)
        plt.legend('Position', loc='best')
        start_idx, end_idx = np.where(data)
        segments = [[data[i, :], data[j, :]]
                    for i in range(len(data)) for j in range(len(data))]
        values = np.abs(similarities)
        lc = LineCollection(segments,
                            zorder=0, cmap=plt.cm.hot_r,
                            norm=plt.Normalize(0, values.max()))
        lc.set_array(similarities.flatten())
        lc.set_linewidths(0.5 * np.ones(len(segments)))
        ax.add_collection(lc)

        for label, x, y in zip(labels, data[:, 0], data[:, 1]):
            plt.annotate(
                label, 
                xy = (x, y), xytext = (-20, 20),
                textcoords = 'offset points', ha = 'right', va = 'bottom',
                bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
                arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))



        plt.show()



def main():

    #### Parse command-line arguments
    parser = argparse.ArgumentParser(description = \
             'Phonological CorpusTools: visualization of segment inventory')
    parser.add_argument('distance_file_name', help='Name of input distance file')
    parser.add_argument('-m', '--visualization_method', default='hc', help="Method of visualization: either hierarchical clustering ('hc') or multi-dimensional scaling ('mds')")
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