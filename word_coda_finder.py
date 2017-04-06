from collections import OrderedDict

#Defines the syllable delimiter
try:
    SyllableDelimiter
except NameError:
    SyllableDelimiter = "$"


#http://stackoverflow.com/questions/843277/how-do-i-check-if-a-variable-exists
try:
    sonorant_list
except NameError:
    sonorant_list = ["a","a","e","i","o","u"]

#practice syllabus
corpus = ["m.e.t.e.s.a", "a.s.a.m.k.y.o", "u.h.a.l.u", "s.i", "m.e.s.e.r.a", "m.e.s.e.t.a", "e", "n.j.o.s.o",
          "l.u.N.o.b.a", "r.w.i", "m.a.s.e.s.a", "a.l.a.m.k.y.o", "a.n.a", "k.i", "m.e.r.e.s.a", "i.N.i.f.w.e", "a",
          "r.o.d.u.s.u", "t.i", "f.p.e.m.i", "l.w.a.f.w.a.s.u", "l.j.o.s.a", "h.e.N", "m.e.s.e.s.a", "l.o.s.u.d.u",
          "r.i", "o.N", "r.o.s.u.d.u", "s.u.N.o.b.a", "e.N.i.f.w.e", "h.k.a.h.j.e", "u.s.a.l.u", "s.w.i",
          "n.w.a.f.w.a.p.u", "l.w.a.f.w.a.p.u", "f.j.a.N", "a.N", "f.m.u", "s.w.a.f.w.a.p.u", "l.j.o.s.o"]

#Loops through corpus and extracts all codas


new_codas = []


for word in corpus:
    shortest_coda_so_far = 100 #arbitrarily long coda to start with
    for sonorant in sonorant_list: # goes through sonorant list
        if not sonorant in set(word): # if the sonorant is not in a particular word, it passes
            pass
        else:
            reverse_word = word[::-1]
            coda_ident = reverse_word.partition(sonorant)[0] #change to -1 relative to onsets so that it goes from right to left and not l-to-r
            coda_length =len(coda_ident)
            if coda_length is 0:
                word_coda = "#"
                break
            else:
                if coda_length < shortest_coda_so_far:
                    shortest_coda_so_far = coda_length
                    if shortest_coda_so_far == coda_length:
                        word_coda = coda_ident
    new_codas.append(word_coda[::-1])

#count occurrences of onsets/coda:
def cluster_counter(cluster_list):
    from collections import Counter
    comb_cnt = Counter()
    for cluster in cluster_list:
        comb_cnt[cluster] += 1
    return comb_cnt


codas = cluster_counter(new_codas)

#Make list of onsets/codas by length
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
#The length includes the separator. It is not the true length, it is generated so that syllables are segmented with the largest possible coda


coda_length_dict = cluster_length_dictionary(codas)

#http://stackoverflow.com/questions/20304824/sort-dict-by-highest-value
codas_by_length = tuple(sorted(coda_length_dict, key=coda_length_dict.get, reverse=True))

from collections import OrderedDict
coda_dict = OrderedDict()
for cluster in codas_by_length:
    dash_cluster = cluster.replace(".","-")
    new_cluster =  SyllableDelimiter+dash_cluster
    coda_dict[cluster] = new_cluster

import csv

#writes a csv file with all word codas
with open('codas.csv', 'w') as csvfile:
    fieldnames=('Coda','Coda_Parser')
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for key, value in coda_dict.items():
        writer.writerow({'Coda': key, 'Coda_Parser': value})