from corpustools.corpus.io import binary
import os

path = os.path.join(os.getcwd(), 'lemurian.corpus')
corpus = binary.load_binary(path)
#get the path to your corpus
#they are saved automactically by PCT in /documents/PCT/CORPUS


#you can easily iterate over all the Word objects in a corpus
from collections import defaultdict
bigrams = defaultdict(int)
for word in corpus:
    print(word)
    sequence = zip(*[word.transcription[i:] for i in range(2)])
    for s in sequence:
        bigrams[s] += 1
for key,value in bigrams.items():
    print(key, value)

# #if you want just a single word, for testing purposes, do this:
# word = corpus.random_word()
#
# #you can iterate over the corpus inventory, which gets you Segment objects
# #these have two useful attributes: .symbol and .features
# for segment in corpus.inventory:
#     print(segment.symbol, segment.features)
#
# #words have a transcription attribute you can iterate over
# #this will gets you all the Segment objects in the transcription
# for seg in word.transcription:
#     print(seg)
#
# #if you iterate over spelling, however, you get strings, not Segements
# for letter in word.spelling:
#     print(letter)
