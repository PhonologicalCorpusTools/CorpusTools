import random
import os
import itertools

#general phonotactics
#max syllable is C1C2VC3
#Anything can go in C1
#C2 is always optional
#C2 can be a glide, a stop, or a nasal.
#Glides can occur after anything, stops and nasals only occur after an initial fricative
#C3 is always optional, and if present must be a nasal
#V is any vowel.
#There is front/back harmony, and vowels in a word must only contain vowels from one of those sets (see below)
#The vowel /a/ is "neutral" and appears in both sets

#There are two phonological processes:
#[-cont][+voice] -> [-voice] / [+cont] (positional neutralization)
#This devoices stops after fricatives, which can only occur in onset. Voiceless stops are already in the inventory.
#s->z / V_V (intervocalic voicing)
#This voices /s/ between vowels. /z/ otherwise is not in the inventory.

#more minimal pairs are generated using coronals than other sounds, which should mean a higher functional load

#There are some spelling rules to make orthography different from transcription
#the glides in /wu/ and /ji/ are always omitted in the writing, and only the vowel appears
#/x/ is written as /h/
#the nasal codas are not distinguished in the writing system, and both are written as N

cons = ['p','t','k','b','d','g','m','n','r','l','s','f','x']
glides = ['j','w']
fricatives = ['s','f','x']
coronals = ['t','d','r','s','n','l']
stops = ['p','t','k','b','d','g']
nasals = ['m','n']
vowels = ['i','e','o','u','a']
front = ['i','e','a']
back = ['o','u','a']
vowel_type = ['front', 'back']

def pick_a_cons():
    return random.choice(cons)

def pick_a_fricative():
    return random.choice(fricatives)

def pick_a_stop():
    return random.choice(stops)

def pick_a_nasal():
    return random.choice(nasals)

def pick_a_glide():
    return random.choice(glides)

def pick_a_vowel():
    return random.choice(vowels)

def pick_a_vowel_type():
    return ''

def pick_a_coda():
    return pick_a_nasal().upper()

def pick_a_front_vowel():
    return random.choice(front)

def pick_a_back_vowel():
    return random.choice(back)

def stop():
    pass

spelling_rules = {'x':'h', 'wu':'u', 'ji':'i', 'N': 'N', 'M':'N', 'z':'s'}

transitions = {#pick an onset
               'q1': (pick_a_cons,['q5','q6']), #C2 will be either a glide or nothing
               'q2': (pick_a_fricative,['q3','q4','q5','q6']), #always C1(+C2)
               'q3': (pick_a_stop, ['q6']),#always C2
               'q4': (pick_a_nasal, ['q6']),#always C2
               'q5': (pick_a_glide, ['q6']),#always C2
               #pick a nucleus
               'q6': (pick_a_vowel_type,['q7','q8']),
               'q7': (pick_a_front_vowel,['q9','q11','q99']),
               'q8': (pick_a_back_vowel, ['q12','q14','q99']),
               #do a syllable n>=2,front vowel harmony
               'q9': (pick_a_cons,['q10','q7']),
               'q10': (pick_a_glide,['q7']),
               'q11': (pick_a_coda,['q7','q99']),
               #do a syllable n>=2, back vowel harmony
               'q12': (pick_a_cons,['q13','q8']),
               'q13': (pick_a_glide,['q8']),
               'q14': (pick_a_coda,['q8','q99']),
               #terminate
               'q99': (stop, ['end'])}

start_states = ['q1','q2','q6']

def allophones(lexicon):
    #s->z / V_V
    #[-cont,+voice] -> [-voice] / [+cont]_
    new_lexicon = list()
    replacements = {}
    for i in itertools.product(vowels,vowels):
        key = i[0]+'s'+i[1]
        value = i[0]+'z'+i[1]
        replacements[key] = value

    for word in lexicon:
        for r in replacements:
            word = word.replace(r, replacements[r])
        if any(word.startswith(f) for f in fricatives):
            if word[1] == 'b':
                word = word.replace('b','p',1)
            elif word[1] == 'd':
                word = word.replace('d','t',1)
            elif word[1] == 'g':
                word = word.replace('g','k',1)
        new_lexicon.append(word)
    return new_lexicon


def make_minimal_pairs(lexicon, subset_size):
    #high functional load for coronals

    coronal_pairs = int(round(subset_size*.75))
    other_pairs = int(round(subset_size*.25))
    words_with_coronals = [word for word in lexicon if any(letter in coronals for letter in word if not letter in nasals)]
    #nasals are avoided because it's hard to find which are codas at this point
    minimal_pairs = list()

    for j in range(coronal_pairs):
        word = random.choice(words_with_coronals)
        pos = [(i,x) for (i,x) in enumerate(word) if x in coronals]

        pos,seg1 = random.choice(pos)
        nextseg = word[pos+1]

        if nextseg in vowels or nextseg in glides:#any consonant can go here
            seg2 = random.choice([s for s in coronals if not s == seg1])
        elif nextseg in stops or nextseg in nasals: #it's a complex onset, must be a fricative
            seg2 = random.choice(['f','x'])
        else:
            seg2 = seg1 #no change


        possible_word = word[:]
        possible_word[pos] = seg2
        minimal_pairs.append(possible_word)

    for j in range(other_pairs):
        word = random.choice(lexicon)
        pos = random.choice(range(len(word)))
        seg1 = word[pos]
        if seg1 in front:
            seg2 = random.choice([f for f in front if not f == seg1])
        elif seg1 in back:
            seg2 = random.choice([b for b in back if not b == seg1])
        elif seg1 in glides:
            pass#glides have really restricted distributions, leave them alone
        else:
            if seg1 in stops:
                seg2 = random.choice([s for s in stops if not s == seg1])
            elif seg1 in nasals:
                seg2 = random.choice([n for n in nasals if not n == seg1])
            elif seg1 in fricatives:
                seg2 = random.choice([f for f in fricatives if not f == seg1])
        possible_word = word[:]
        possible_word[pos] = seg2
        minimal_pairs.append(possible_word)

    return minimal_pairs

def generate_lexicon(lexicon_size, max_syllable_length, minimal_pair_num):
    lexicon = list()
    lexicon.extend(['usalu', 'mesesa', 'rosudu', 'ljoso', 'asamkyo'])
    #for n in range(lexicon_size):
    syl_count = 0
    word = list()
    initial_state = random.choice(start_states)
    letter,state = transitions[initial_state]
    next_state = random.choice(state)
    word.append(letter())
    while len(lexicon)<lexicon_size:
        letter,state = transitions[next_state]
        word.append(letter())
        next_state = random.choice(state)
        if syl_count >= max_syllable_length:
            lexicon.append(word)
            word = list()
            syl_count = 0
            next_state = random.choice(start_states)
        if next_state == 'q99':
            lexicon.append(word)
            word = list()
            syl_count = 0
            next_state = random.choice(start_states)
        elif next_state == 'q7' or next_state=='q8':#vowel states
            syl_count += 1
    lexicon = [[w for w in word if w] for word in lexicon]
    lexicon.extend(make_minimal_pairs(lexicon, minimal_pair_num))
    return [''.join(word) for word in lexicon]

def make_corpus(lexicon):
    corpus = list()
    frequency = 1
    for word in lexicon:
        transcription = '.'.join([w.lower() for w in word])
        for sr in spelling_rules:
            word = word.replace(sr, spelling_rules[sr])
        frequency = (frequency*2)/random.randint(2,6) + (random.randint(1,100)) - (frequency/random.randint(2,8))
        if frequency <=0 :
            frequency = 5
        text = ','.join([transcription,word,str(int(round(frequency)))])
        corpus.append(text)
    return corpus


if __name__ == '__main__':
    lexicon = generate_lexicon(60, 3, 40)#base lexicon size, max syllable length, number of minimal pairs to add to base lexicon
    lexicon = allophones(lexicon)
    corpus = make_corpus(lexicon)
    with open(os.path.join(os.getcwd(),'lemurian.txt'), mode='w', encoding='utf-8-sig') as f:
        f.write('Transcription,Spelling,Frequency\n')
        for word in corpus:
            print(word, file=f)