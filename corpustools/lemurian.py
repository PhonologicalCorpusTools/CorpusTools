import random

cons = ['p','t','k','b','d','g','m','n','r','l','s','z','f','v','x']
glides = ['j','w']
fricatives = ['s','z','f','v','x']
stops = ['p','t','k','b','d','g']
nasals = ['m','n']
vowels = ['i','e','o','u','a']
front = ['i','e','a']
back = ['o','u']
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
    return pick_a_nasal()

def pick_a_front_vowel():
    return random.choice(front)

def pick_a_back_vowel():
    return random.choice(back)

def stop():
    pass

def main(lexicon_size, max_syllable_length):
    lexicon = list()
    for n in range(lexicon_size):
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

    return [''.join(word) for word in lexicon]

transitions = {#pick an onset
               'q1': (pick_a_cons,['q5','q6']), #no C2 in this case
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
               'q99': (stop, ['end'])}#no coda

start_states = ['q1','q2','q6']

if __name__ == '__main__':
    lexicon = main(100, 5)
    corpus = list()
    spelling_rules = {'x':'h', 'wu':'u', 'ji':'i'}
    frequency = 1
    output = list()
    for word in lexicon:
        transcription = '.'.join(word)
        for sr in spelling_rules:
            word = word.replace(sr, spelling_rules[sr])

        frequency = (frequency*2)/random.randint(2,6) + (random.randint(1,100)) - (frequency/random.randint(2,8))
        text = ','.join([transcription,word,str(int(round(frequency)))])
        output.append(text)
    with open('c:\\lemurian.txt', mode='w', encoding='utf-8') as f:
        f.write('Transcription,Spelling,Frequency\n')
        for word in output:
            print(word, file=f)