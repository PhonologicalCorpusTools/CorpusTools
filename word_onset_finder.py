from collections import OrderedDict




#http://stackoverflow.com/questions/843277/how-do-i-check-if-a-variable-exists
try:
    sonorant_list
except NameError:
    sonorant_list = ["a","e","i","o","u"]

#practice syllabus
corpus = ["m.e.t.e.s.a", "a.s.a.m.k.y.o", "u.h.a.l.u", "s.i", "m.e.s.e.r.a", "m.e.s.e.t.a", "e", "n.j.o.s.o",
          "l.u.N.o.b.a", "r.w.i", "m.a.s.e.s.a", "a.l.a.m.k.y.o", "a.n.a", "k.i", "m.e.r.e.s.a", "i.N.i.f.w.e", "a",
          "r.o.d.u.s.u", "t.i", "f.p.e.m.i", "l.w.a.f.w.a.s.u", "l.j.o.s.a", "h.e.N", "m.e.s.e.s.a", "l.o.s.u.d.u",
          "r.i", "o.N", "r.o.s.u.d.u", "s.u.N.o.b.a", "e.N.i.f.w.e", "h.k.a.h.j.e", "u.s.a.l.u", "s.w.i",
          "n.w.a.f.w.a.p.u", "l.w.a.f.w.a.p.u", "f.j.a.N", "a.N", "f.m.u", "s.w.a.f.w.a.p.u", "l.j.o.s.o"]

try:
    SyllableDelimiter
except NameError:
    SyllableDelimiter = "$"

#Loops through corpus and extracts all onsets


new_onsets = []


for word in corpus:
    shortest_onset_so_far = 100 #arbitrarily high onset
    for sonorant in sonorant_list: #goes through sonorant list
        if not sonorant in set(word): # if the sonorant is not in a particular word, it passes
            pass
        else:
            onset_ident = word.partition(sonorant)[0]  #all of the word to the left of a sonorant
            onset_length = len(onset_ident) #calculates length of a sonorant

            if onset_length is 0: #if the lengh of the onset is 0 and the sonorant is present, a hashtag is returned
                word_onset = "#"
                break
            else:
                if onset_length < shortest_onset_so_far:
                    shortest_onset_so_far = onset_length
                    if shortest_onset_so_far == onset_length:
                        word_onset = ''.join(onset_ident)
    new_onsets.append(word_onset)

def cluster_counter(cluster_list):
    from collections import Counter
    comb_cnt = Counter()
    for cluster in cluster_list:
        comb_cnt[cluster] += 1
    return comb_cnt

onsets = cluster_counter(new_onsets)


def cluster_length_dictionary(dictionary):
    length_dictionary = {}
    for x in dictionary:
        if x is '#':
            cluster_length = 0
        else:
            characters = len(x)
            cluster_length = characters
        length_dictionary[x] = cluster_length
    return length_dictionary

# #The length includes the separator. It is not the word length, it is generated so that syllables are segmented with the largest available onset

onset_length_dict = cluster_length_dictionary(onsets)

#
# #http://stackoverflow.com/questions/20304824/sort-dict-by-highest-value
onsets_by_length = tuple(sorted(onset_length_dict, key=onset_length_dict.get, reverse=True))

from collections import OrderedDict
onset_dict = OrderedDict()
for cluster in onsets_by_length:
    dash_cluster = cluster.replace(".","-")
    new_cluster =  SyllableDelimiter+dash_cluster
    onset_dict[cluster] = new_cluster

#http://stackoverflow.com/questions/8685809/python-writing-a-dictionary-to-a-csv-file-with-one-line-for-every-key-value
import csv

with open('onsets.csv', 'w') as csvfile:
    fieldnames=('Onset','Onset_Parser')
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for key, value in onset_dict.items():
        writer.writerow({'Onset': key, 'Onset_Parser': value})

