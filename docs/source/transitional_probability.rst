.. _transitional_probability:

************************
Transitional Probability
************************

.. _about_tp:

About the function
------------------
Transitional probability is a measure of how likely a symbol will appear, given a
preceding or succeeding symbol. For a bigram `AB`, its forward transitional
probability is the likelihood of `B` given `A`, and its backward transitional
probability is the likelihood of `A` given `B` [Pelucci2009]_. The measurement can be used to predict
word or morpheme boundaries in speech (see [Saffran1996a]_, [Saffran1996b]_ and
[Daland2011]_). Two symbols with a low transitional probability are unlikely to
co-occur, which would predict that that a word or morpheme boundary is likely to
exist between them. Conversely, two symbols with a high transitional probability
are likely to co-occur, and are predicted to exist within one word or morpheme. For
example, the symbols [n] and [d] may have a high forward transitional probability in a corpus of English,
because they appear within words like [saʊnd] 'sound' or [ʌndɚ] 'under'. In the same corpus, the symbols
[d] and [f] may have a low forward transitional probability, because the sequence [df] only
occurs across word boundaries, such as in [ænd#fɹʌm] 'and from'.

Note that because corpora in PCT are treated as lists of words in isolation, even if they
were created from running transcriptions, transitional probability calculations are always actually
*within words* in PCT.

.. _tp_method:

Method of calculation
---------------------
In PCT, transitional probability is calculated on the segment level, and it is
possible to calculate both forward and backward TP. Given two segments :math:`a` and
:math:`b`, occuring in the order :math:`ab`,

Forward transitional probability:

:math:`P(b|a) = \frac{P(ab)}{P(a)}`

Backward transitional probability:

:math:`P(a|b) = \frac{P(ab)}{P(b)}`

where :math:`P(ab)` is the probability of the bigram :math:`ab`, and :math:`P(a)`
and :math:`P(b)` are the probabilities of the segments :math:`a` and
:math:`b`.

A toy example
`````````````
Consider the following corpus:

+----------+---------------+-----------+
| Spelling | Transcription | Frequency |
+==========+===============+===========+
| mata     | m.ɑ.t.ɑ       | 2         |
+----------+---------------+-----------+
| nama     | n.ɑ.m.ɑ       | 4         |
+----------+---------------+-----------+
| ʃi       | ʃ.i           | 6         |
+----------+---------------+-----------+

Using type frequencies, the probability of the bigram `ɑm` is:

:math:`P(am) = \frac{n_{am}}{n_{bigrams}} = \frac{1}{7}`

i.e., the frequency of the bigram `am` divided by the total number of bigrams in
the corpus (assuming only segments count toward bigrams; see more in the section 
on word boundaries below). 

Using token frequencies, the probability is:

:math:`P(am) = \frac{n_{am}}{n_{bigrams}} = \frac{4}{24}`

The probability of the individual segments are found by finding the number of bigrams
that start with the first segment, when looking for the first,
or end with the second segment, when looking for the second. For [m] and [ɑ]:

:math:`P(a) = \frac{n_{a\_}}{n_{bigrams}} = \frac{2}{7}` with type frequencies, or
:math:`\frac{6}{24}` with token frequencies.

:math:`P(m) = \frac{n_{\_m}}{n_{bigrams}} = \frac{1}{7}` with type frequencies, or
:math:`\frac{4}{24}` with token frequencies.

Given the bigram `am`, the forward TP is:

:math:`P(m|a) = \frac{P(am)}{P(a)} = \frac{1/7}{2/7} = \frac{1}{2}` with type frequencies, or
:math:`\frac{4/24}{6/24} = \frac{2}{3}` with token frequencies.

The backward TP is:

:math:`P(a|m) = \frac{P(am)}{P(m)} = \frac{1/7}{1/7} = 1` with type
frequencies, or :math:`\frac{4/24}{4/24} = 1` with token frequencies.

In this corpus, the segment `m` will occur after the segment `ɑ` 50% of the time given type frequencies or 67% of the time given token frequencies. Meanwhile, `ɑ` is certain to appear before the segment `m` (if `m` has any segment before it, i.e., is not word-initial).

For more on this method, see [Anghelescu2016]_.

Word Boundaries
```````````````
In PCT, word boundaries can be set to occur once at the end of every word, to occur
on both sides of a word, or to be ignored (as they were in the above examples). The first option is the default setting.

Assuming a single boundary at the end of every word:

+----------+---------------+-----------+
| Spelling | Transcription | Frequency |
+==========+===============+===========+
| mata     | m.ɑ.t.ɑ.#     | 2         |
+----------+---------------+-----------+
| nama     | n.ɑ.m.ɑ.#     | 4         |
+----------+---------------+-----------+
| ʃi       | ʃ.i.#         | 6         |
+----------+---------------+-----------+

The probability of the bigram `am` is:

:math:`P(am) = \frac{n_{am}}{n_{bigrams}} = \frac{1}{10}` with type frequencies,
and :math:`\frac{4}{36}` with token frequencies.

The probabilities of the individual symbols are:

:math:`P(a) = \frac{n_{a\_}}{n_{bigrams}} = \frac{4}{10}` with type frequencies, and
:math:`\frac{12}{36}` with token frequencies.

:math:`P(m) = \frac{n_{\_m}}{n_{bigrams}} = \frac{1}{10}` with type frequencies, and
:math:`\frac{4}{36}` with token frequencies.

Given single word boundaries, the forward TP of the bigram `am` is:

:math:`P(m|a) = \frac{P(am)}{P(a)} = \frac{1/10}{4/10} = \frac{1}{4}` with type frequencies, or
:math:`\frac{4/36}{12/36} = \frac{1}{3}` with token frequencies.

The backward TP is:

:math:`P(a|m) = \frac{P(am)}{P(m)} = \frac{1/10}{1/10} = 1` with type
frequencies, or :math:`\frac{4/36}{4/36} = 1` with token frequencies.

Assuming boundaries on each side of a word:

+----------+---------------+-----------+
| Spelling | Transcription | Frequency |
+==========+===============+===========+
| mata     | #.m.ɑ.t.ɑ.#   | 2         |
+----------+---------------+-----------+
| nama     | #.n.ɑ.m.ɑ.#   | 4         |
+----------+---------------+-----------+
| ʃi       | #.ʃ.i.#       | 6         |
+----------+---------------+-----------+

The probability of the bigram `am` is:

:math:`P(am) = \frac{n_{am}}{n_{bigrams}} = \frac{1}{13}` with type frequencies,
and :math:`\frac{4}{48}` with token frequencies.

The probabilities of the individual symbols are:

:math:`P(a) = \frac{n_{a\_}}{n_{bigrams}} = \frac{4}{13}` with type frequencies, and
:math:`\frac{12}{48}` with token frequencies.

:math:`P(m) = \frac{n_{\_m}}{n_{bigrams}} = \frac{2}{13}` with type frequencies, and
:math:`\frac{6}{48}` with token frequencies.

Given single word boundaries, the forward TP of the bigram `am` is:

:math:`P(m|a) = \frac{P(am)}{P(a)} = \frac{1/13}{4/13} = \frac{1}{4}` with type frequencies, or
:math:`\frac{4/48}{12/48} = \frac{1}{3}` with token frequencies.

The backward TP is:

:math:`P(a|m) = \frac{P(am)}{P(m)} = \frac{1/13}{2/13} = \frac{1}{2}` with type
frequencies, or :math:`\frac{4/48}{6/48} = \frac{2}{3}` with token frequencies.

The first example in this section was calculated ignoring word boundaries.

.. _tp_gui:

Calculating transitional probability in the GUI
-----------------------------------------------
As with most analysis functions, a corpus must first be loaded (see
:ref:`loading_corpora`). Once a corpus is loaded:

1. **Getting started**: Choose "Analysis" / "Calculate transitional
probability..." from the top menu bar.

2. **Bigram selection**: To select segment pairs, click on the "Add
bigram" button to open the :ref:`bigram_selector` dialogue box. Note that the order
of the bigram matters for calculating transitional probability.

3. **Direction**: Transitional probability can be calculated based on the
presence of either the first or second segment. The labels "P(B|A)" and
"P(A|B)" correspond to the column labels "A" and "B" on the Bigrams table.

4. **Word boundary**: Select an option for word boundary. The default is to
assume that there is only one boundary per word, and that it is in final
position (as is assumed in [Goldsmith2012]_ with respect to Mutual Information calculations). 
This is based on the assumption
that in running text, the final boundary of word 1 will be the initial boundary
of word 2, so that there is no need to have two boundaries per word. Select
“Keep both word boundaries” to have boundaries on both sides, or “Ignore all
word boundaries” to ignore all word boundaries in the calculation.

5. **Pronunciation variants**: If the corpus contains multiple
pronunciation variants for lexical items, select which strategy should be
used. For details, see :ref:`pronunciation_variants`.

6. **Tier**: Select which tier transitional probability will be
calculated from. The default is transcription, but other tiers can be
created in order to isolate or group together various phonemes. See
:ref:`create_tiers` for details on creating and using tiers.

7. **Type or token frequency**: Transitional probability can be calculated
using either type or token frequencies, provided that the loaded corpus
includes both frequency measures (see :ref:`corpus_format`).

8. **Minimum frequency**: It is possible to set a minimum token frequency
for including words in the calculation. This allows easy exclusion of
rare words. To include all words in the corpus, regardless of their token
frequency, set the minimum frequency to 0, or leave the field blank. Note
that if a minimum frequency is set, all words below that frequency will be
ignored entirely for the purposes of calculation.

.. _tp_classes_and_functions:

Classes and functions
---------------------
For further details about the relevant classes and functions in PCT's
source code, please refer to :ref:`trans_prob_api`.
