import re
import numpy as np
import pdb

from scipy.cluster.hierarchy import linkage, dendrogram

from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
import seaborn as sns

from sklearn.decomposition import PCA


def organize_data(reader, visualization_method, value_column, segment_column):
    raw_data = {tuple([x[1:-1] for x in re.findall("'.+?'", r[segment_column])]): float(r[value_column]) for r in reader}
    all_segments = list(set([segment for pair in raw_data for segment in pair]))

    # ## TEMP: REMOVE VOWELS
    # VOWELS = ['IY', 'UW', 'IH', 'EH', 'ER', 'AW', 'AY', 'EY', 'OW', 'OY', 'AA', 'AE', 'AH', 'AO', 'UH']
    # all_segments = [s for s in all_segments if s not in VOWELS]
    # ##

    if visualization_method in ['pca', 'hm']:
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
        m /= np.amax(m)
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
    # original_data = {row['result']: row['segment(s)'] for row in reader}
    labels, data = organize_data(reader, visualization_method, value_column, segment_column)
    data_dict = {label: datum for label, datum in zip(labels, data)}

    if visualization_method == 'hc':
        link = linkage(data)
        dendrogram(link, leaf_label_func=lambda i: labels[i])
        ax = plt.axes()
        ax.set_title('Segment pair functional load: hierarchical clustering')
        plt.gcf()
        plt.show()

    if visualization_method == 'hm':
        ax = sns.heatmap(data)
        ax.set_title('Segment pair functional load: heatmap')
        plt.xticks([p+0.5 for p in range(len(labels))], labels)
        plt.yticks([p+0.5 for p in range(len(labels))], reversed(labels))
        plt.show()

    if visualization_method == 'pca':
        n = len(labels)
        data -= data.mean()
        clf = PCA(n_components=2)
        transformed = clf.fit_transform(data)

        # def get_sim(s1, s2):
        #     i1 = labels.index(s1)
        #     i2 = labels.index(s2)
        #     print(similarities[i1][i2])

        fig = plt.figure(1)
        ax = plt.axes([0., 0., 1., 1.])
        ax.set_title('Segment pair functional load: first two principal components')

        plt.scatter(transformed[:, 0], transformed[:, 1], marker=',', c='b', s=0)

        for label, x, y in zip(labels, transformed[:, 0], transformed[:, 1]):
            plt.annotate(
                label, 
                xy = (x, y), xytext = (0, 0),
                textcoords = 'offset points')

        plt.show()

