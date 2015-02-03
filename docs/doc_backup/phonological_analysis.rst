.. _phonological_analysis:

********************
Phonlogical analysis
********************

We preface all of the tools used here for phonological analysis with the
caveat that they are simply that: *tools*. That is, they are computational
implementations of calculations that have been claimed in the literature
to reflect phonologically useful information. In order to be useful,
they must be used by researchers who have an understanding of these
claims and can apply the tools appropriately. There are no magic bullets
here; just mathematical operations. It is up to an informed researcher
to ensure that the numbers going in to the calculations make sense, and
to interpret the results of said calculations coherently. We provide
references throughout to facilitate the ability of researchers to
understand how and why these particular functions would be helpful.
Similarly, we do not provide arguments here for *why* these particular
functions have been chosen in the literature; they are included in PCT
because they have been argued to be helpful elsewhere. Again, the references
provided are excellent sources of these original arguments. **Relatedly:
when using these algorithms, it should be remembered that in most cases,
PCT is an implementation of someone else’s original work, and those original
authors should be cited**. For example, if one were calculating the acoustic
similarity of segments in a corpus, one might say “Acoustic similarity of
the voiced vs. voiceless fricatives was calculated with the sound files
represented in terms of multiple band amplitude envelopes (Lewandowski, 2012),
using dynamic time warping (Sakoe & Chiba, 1971). Calculations were done
using the software *Phonological CorpusTools* (Hall et al. 2015).”

Some of the analysis functions can be calculated on either word types or
word tokens. If token frequency is not available in a given corpus, then
those options will be greyed out in PCT, and the function will be required
to be run on types. See the references associated with each measure for
explanations of the advantages of one kind of measure vs. the other.

.. _phonotactic_probability:

Phonotactic Probability
=======================

.. _about_phonotactic_probability:

About the function
------------------

Phonotactic probability refers to the likelihood of a given set of segments
occurring in a given order for a given corpus of transcriptions.  For instance,
*blick* is a phonotactically probable nonword in English, but *bnick* is
phonotactically improbable.  Words as well as nonwords can be assessed for
their phonotactic probability, and this measure has been used in behavioural
research ([Vitevitch1999]_ and others). In particular, the phonotactic
probability of words has been correlated with their ability to be segmented,
acquired, processed, and produced; see especially the discussion in [Vitevitch2004]_
for extensive references.

.. _method_phonotactic_probability:

Method of calculation
---------------------

One method for computing the phonotactic probability uses average unigram
or bigram positional probabilities across a word ([Vitevitch2004]_;
their online calculator for this function is available `here
<http://www.people.ku.edu/~mvitevit/PhonoProbHome.html>`_).
For a word like *blick* in English, the unigram average would include the
probability of /b/ occurring in the first position of a word, the
probability of /l/ in the second position, the probability of /ɪ/
occuring in the third position, and the probability of /k/ occurring
in the fourth position of a word.  Each positional probability is
calculated by summing the log token frequency of words containing that
segment in that position divided by the sum of the log token frequency
of all words that have that position in their transcription.  The bigram
average is calculated in an equivalent way, except that sequences of two
segments and their positions are used instead of single segments.  So for
*blick* that would be /bl/, /lɪ/, /ɪk/ as the included poisitional probabilities.
As with all n-gram based approaches, bigrams are preferable to unigrams.
In the example of *blick* versus *bnick*, unigrams wouldn't likely capture
the intuitive difference in phonotactic probability, since the probability
of /n/ and /l/ in the second position isn't necessarily radically different.
Using bigrams, however, would capture that the probability of /bl/ versus /bn/
in the first position is radically different.

There are other ways of calculating phonotactic probability that don't
have the strict left-to-right positional assumptions that the Vitevitch
& Luce algorithm has, such as the constraint-based method in BLICK by
Bruce Hayes (Windows executable available `here
<http://www.linguistics.ucla.edu/people/hayes/BLICK/>`_, Python package
available `here <https://pypi.python.org/pypi/python-BLICK/0.2.12>`_
with source code available at <https://github.com/mmcauliffe/python-BLICK/>_).
However, such algorithms require training on a specific language, and
the constraints are not computed from transcribed corpora in as
straightforward a manner as the probabilities used in the Vitevitch &
Luce algorithm. Therefore, PCT currently supports only the Vitevitch &
Luce style algorithm.

.. _phonotactic_probability_gui:

Implementing the phonotactic probability function in the GUI
------------------------------------------------------------

To start the analysis, click on “Analysis” / “Calculate phonotactic probability...”
in the main menu, and then follow these steps:

1. **Phonotactic probability algorithm**: Currently the only offered algorithm
   is the Vitevitch & Luce algorithm, described above.
2. **Query type**: Phonotactic probability can be calculated for one of three
   types of inputs:

   a. **One word**: The phonotactic probability of a single word can be calculated
      by entering that word’s orthographic representation in the query box.
   b. **One word/nonword not in the corpus**: The phonotactic probability can
      be calculated on a word that is not itself in the corpus, but using
      the probabilities derived from the corpus. These words are distinct
      from the corpus and won't be added to it, nor will their creation
      affect any future calculations. See §4.6.4 for information on how
      to more permanently add a new word to the corpus. Words can be
      created through the dialogue opened by pressing the button:

      i. **Spelling**: Enter the spelling for your new word / nonword using
         the regular input keyboard on your computer. The spelling is
         how the word will be referenced in the results table, but won’t
         affect the calculation of phonotactic probability.
      ii. **Transcription**: To add in the phonetic transcription of the new
          word, it is best to use the provided inventory. While it is
          possible to type directly in to the transcription box, using
          the provided inventory will ensure that all characters are
          understood by PCT to correspond to existing characters in the
          corpus (with their concomitant featural interpretation). Click
          on “Show inventory” and then choose to show “Consonants,” “Vowels,”
          and/or other. (If there is no featural interpretation of your
          inventory, you will simply see a list of all the available
          segments, but they will not be classifed by major category.)
          Clicking on the individual segments will add them to the
          transcription. The selections will remain even when the
          sub-inventories are hidden; we allow for showing / hiding
          the inventories to ensure that all relevant buttons on the
          dialogue box are available, even on small computer screens.
          Note that you do NOT need to include word boundaries at the
          beginning and end of the word, even when the boundary symbol
          is included as a member of the inventory; these will be assumed
          automatically by PCT.
      iii. **Frequency**: This can be left at the default. Note that entering
           a value will NOT affect the calculation; there is no particular
           need to enter anything here (it is an artifact of using the same
           dialogue box here as in the “Add Word” function described in §4.6.4).
      iv. **Create word**: To finish and return to the “Phonotactic probability”
          dialogue box, click on “Create word.”

   c. **List of words**: If there is a specific list of words for which
      phonotactic probability is to be calculated (e.g., the stimuli list
      for an experiment), that list can be saved as a .txt file with one
      word per line and uploaded into PCT for analysis.  If words in the
      list are not in the corpus, you can still calculate their phonotactic
      probability by entering in the spelling of the word and the transcription
      of the word in a single line delimited by a tab. The transcription
      should be delimited by periods.
   d. **Whole corpus**: Alternatively, the phonotactic probability for every
      current word in the corpus can be calculated. The phonotactic
      probability of each word will be added to the corpus itself, as
      a separate column; in the “query” box, simply enter the name of
      that column (the default is “Phonotactic probability”).

3. **Tier**: Phonotactic probability can be calculated from transcription
   tiers in a corpus (e.g., transcription or tiers that represent subsets
   of entries, such as a vowel or consonant tier).
4. **Type vs. token frequency**: Specify whether phonotactic probabilities
   should be based on word type frequency or token frequency.  The
   original Vitevitch & Luce algorithm uses token frequency. Token frequency
   will use the log frequency when calculating probabilities.
5. **Probability type**: Specify whether to use biphone positional
   probabilities or single segment positional probabilities.  Defaults to biphone.
6. **Results**: Once all options have been selected, click “Calculate
   phonotactic probability.” If this is not the first calculation, and
   you want to add the results to a pre-existing results table, select
   the choice that says “add to current results table.” Otherwise, select
   “start new results table.” A dialogue box will open, showing a table of
   the results, including the word, its phonotactic probability, the
   transcription tier from which phonotactic probability was calculated,
   whether type or token frequency was used, whether the algorithm used
   unigram or bigram probabilities, and the phonotactic probability algorithm
   that was used. If the phonotactic probability for all words in the corpus
   is being calculated, simply click on the “start new results table” option,
   and you will be returned to your corpus, where a new column has been added
   automatically.
7. **Saving results**: The results tables can each be saved to tab-delimited .txt
   files by selecting “Save to file” at the bottom of the window. If all
   phonotactic probabilities are calculated for a corpus, the corpus
   itself can be saved by going to “File” / “Export corpus as text file,”
   from where it can be reloaded into PCT for use in future sessions with
   the phonotactic probabilities included.

An example of the “Phonotactic Probability” dialogue box for calculating
the probability of the non-word “pidger” [pɪdʒɚ] using unigram position
probabilities (using the IPHOD corpus):

.. image:: _static/phonoprobdialog.png
   :width: 90%
   :align: center

.. image:: _static/phonoprobresults.png
   :width: 90%
   :align: center

To return to the function dialogue box with your most recently used
selections, click on “Reopen function dialog.” Otherwise, the results
table can be closed and you will be returned to your corpus view.

.. _functional_load:

Functional Load
===============

.. _about_functional_load:

About the function
------------------

Functional load is a measure of the “work” that any particular contrast
does in a language, as compared to other contrasts (e.g., [Hockett1955]_,
[Hockett1966]_; [Kucera1963]_; [King1967]_; [Surendran2003]_). Two contrasts
in a language, such as [d] / [t] vs. [ð] / [θ] in English, may have very
different functional loads. The difference between [d] and [t] is used to
distinguish between many different lexical items, so it has a high
functional load; there are, on the other hand, very few lexical items
that hinge on the distinction between [ð] and [θ], so its functional
load is much lower. One of the primary claims about functional load is
that it is related to sounds’ propensity to merge over time, with pairs
of sounds that have higher functional loads being less likely to merge
than pairs of sounds with lower functional loads (e.g., [Wedel2013]_, [Todd2012]_).
The average functional load of a particular sound has also been claimed to
affect its likelihood of being used as an epenthetic vowel [Hume2013]_.
Functional load has also been illustrated to affect the perceived
similarity of sounds [Hall2014a]_.

.. _method_functional_load:

Method of calculation
---------------------

There are two primary ways of calculating functional load that are
provided as part of the PCT package. One is based on the change of
entropy in a system upon merger of a segment pair or set of segment
pairs (cf. [Surendran2003]_); the other is based on simply
counting up the number of minimal pairs (differing in only the target
segment pair or pairs) that occur in the corpus.

.. _method_change_entropy:

Change in entropy
`````````````````

The calculation based on change in entropy is described in detail in
[Surendran2003]_. Entropy is an Information-Theoretic measure of the
amount of uncertainty in a system [Shannon1949]_, and is
calculated using the formula in (1); it will also be used for the
calculation of predictability of distribution (see §6.2). For every
symbol *i* in some inventory (e.g., every phoneme in the phoneme inventory,
or every word in the lexicon), one multiplies the probability of *i* by
the :math:`log_{2}` of the probability of *i*; the entropy is the sum of the products
for all symbols in the inventory.

Entropy:

:math:`H = -\sum_{i \in N} p_{i} * log_{2}(p_{i})`

The functional load of any pair of sounds in the system, then, can be
calculated by first calculating the entropy of the system at some level
of structure (e.g., words, syllables) with all sounds included, then
merging the pair of sounds in question and re-calculating the entropy
of the new system. That is, the functional load is the amount of
uncertainty (entropy) that is lost by the merger. If the pair has a
functional load of 0, then nothing has changed when the two are merged,
and :math:`H_{1}` will equal :math:`H_{2}`. If the pair has a non-zero functional load, then
the total inventory has become smaller through the conflating of pairs
of symbols that were distinguished only through the given pair of sounds.

Functional load as change in entropy:

:math:`\Delta H = H_{1} - H_{2}`

Consider a toy example, in which the following corpus is assumed (note
that, generally speaking, there is no “type frequency” column in a PCT
corpus, as it is assumed that each row in the corpus represents 1 type;
it is included here for clarity):

Consider a toy example, in which the following corpus is assumed
(note that, generally speaking, there is no “type frequency” column
in a PCT corpus, as it is assumed that each row in the corpus represents
1 type; it is included here for clarity):

+--------+-----------------------+-----------------------+-----------------------+
|        |        Original       | Under [h] / [ŋ] merger| Under [t] / [d] merger|
|        +--------+------+-------+--------+------+-------+--------+------+-------+
|  Word  | Trans. | Type | Token | Trans. | Type | Token | Trans. | Type | Token |
|        |        | Freq.| Freq. |        | Freq.| Freq. |        | Freq.| Freq. |
+========+========+======+=======+========+======+=======+========+======+=======+
|  hot   |  [hɑt] |    1 |     2 |  [Xɑt] |    1 |     2 |  [hɑX] |    1 |     2 |
+--------+--------+------+-------+--------+------+-------+--------+------+-------+
|  song  |  [sɑŋ] |    1 |     4 |  [sɑX] |    1 |     4 |  [sɑŋ] |    1 |     4 |
+--------+--------+------+-------+--------+------+-------+--------+------+-------+
|  hat   |  [hæt] |    1 |     1 |  [Xæt] |    1 |     1 |  [hæX] |    1 |     1 |
+--------+--------+------+-------+--------+------+-------+--------+------+-------+
|  sing  |  [sɪŋ] |    1 |     6 |  [sɪX] |    1 |     6 |  [sɪŋ] |    1 |     6 |
+--------+--------+------+-------+--------+------+-------+--------+------+-------+
|  tot   |  [tɑt] |    1 |     3 |  [tɑt] |    1 |     3 |  [XɑX] |      |       |
+--------+--------+------+-------+--------+------+-------+--------+    1 |     8 |
|  dot   |  [dɑt] |    1 |     5 |  [dɑt] |    1 |     5 |  [XɑX] |      |       |
+--------+--------+------+-------+--------+------+-------+--------+------+-------+
|  hip   |  [hɪp] |    1 |     2 |  [Xɪp] |    1 |     2 |  [hɪp] |    1 |     2 |
+--------+--------+------+-------+--------+------+-------+--------+------+-------+
|  hid   |  [hɪd] |    1 |     7 |  [Xɪd] |    1 |     7 |  [hɪX] |    1 |     7 |
+--------+--------+------+-------+--------+------+-------+--------+------+-------+
|  team  |  [tim] |    1 |     5 |  [tim] |    1 |     5 |  [Xim] |      |       |
+--------+--------+------+-------+--------+------+-------+--------+    1 |    10 |
|  deem  |  [dim] |    1 |     5 |  [dim] |    1 |     5 |  [Xim] |      |       |
+--------+--------+------+-------+--------+------+-------+--------+------+-------+
|  toot  |  [tut] |    1 |     9 |  [tut] |    1 |     9 |  [XuX] |      |       |
+--------+--------+------+-------+--------+------+-------+--------+    1 |    11 |
|  dude  |  [dud] |    1 |     2 |  [dud] |    1 |     2 |  [XuX] |      |       |
+--------+--------+------+-------+--------+------+-------+--------+------+-------+
|  hiss  |  [hɪs] |    1 |     3 |  [Xɪs] |    1 |     3 |  [hɪs] |    1 |     3 |
+--------+--------+------+-------+--------+------+-------+--------+------+-------+
|  his   |  [hɪz] |    1 |     5 |  [Xɪz] |    1 |     5 |  [hɪz] |    1 |     5 |
+--------+--------+------+-------+--------+------+-------+--------+------+-------+
| sizzle | [sɪzəl]|    1 |     4 | [sɪzəl]|    1 |     4 | [sɪzəl]|    1 |     4 |
+--------+--------+------+-------+--------+------+-------+--------+------+-------+
| dizzy  |  [dɪzi]|    1 |     3 |  [dɪzi]|    1 |     3 |  [Xɪzi]|      |       |
+--------+--------+------+-------+--------+------+-------+--------+    1 |     7 |
| tizzy  |  [tɪzi]|    1 |     4 |  [tɪzi]|    1 |     4 |  [Xɪzi]|      |       |
+--------+--------+------+-------+--------+------+-------+--------+------+-------+
|      Total      |   17 |    70 |        |   17 |    70 |        |   13 |    70 |
+--------+--------+------+-------+--------+------+-------+--------+------+-------+

The starting entropy, assuming word types as the relative unit of
structure and counting, is:

:math:`H_{1 - types} = -[(\frac{1}{17} log_{2}(\frac{1}{17}))
+ (\frac{1}{17} log_{2}(\frac{1}{17})) + (\frac{1}{17} log_{2}(\frac{1}{17}))
+ (\frac{1}{17} log_{2}(\frac{1}{17})) + (\frac{1}{17} log_{2}(\frac{1}{17}))\\
+ (\frac{1}{17} log_{2}(\frac{1}{17})) + (\frac{1}{17} log_{2}(\frac{1}{17}))
+ (\frac{1}{17} log_{2}(\frac{1}{17})) + (\frac{1}{17} log_{2}(\frac{1}{17}))
+ (\frac{1}{17} log_{2}(\frac{1}{17})) + (\frac{1}{17} log_{2}(\frac{1}{17}))\\
+ (\frac{1}{17} log_{2}(\frac{1}{17})) + (\frac{1}{17} log_{2}(\frac{1}{17}))
+ (\frac{1}{17} log_{2}(\frac{1}{17})) + (\frac{1}{17} log_{2}(\frac{1}{17}))
+ (\frac{1}{17} log_{2}(\frac{1}{17})) + (\frac{1}{17} log_{2}(\frac{1}{17}))]
=4.087`

The starting entropy, assuming word tokens, is:

:math:`H_{1 - tokens} = -[(\frac{2}{70} log_{2}(\frac{2}{70}))
+ (\frac{4}{70} log_{2}(\frac{4}{70})) + (\frac{1}{70} log_{2}(\frac{1}{70}))
+ (\frac{6}{70} log_{2}(\frac{6}{70})) + (\frac{3}{70} log_{2}(\frac{3}{70}))\\
+ (\frac{5}{70} log_{2}(\frac{5}{70})) + (\frac{2}{70} log_{2}(\frac{2}{70}))
+ (\frac{7}{70} log_{2}(\frac{7}{70})) + (\frac{5}{70} log_{2}(\frac{5}{70}))
+ (\frac{5}{70} log_{2}(\frac{5}{70})) + (\frac{9}{70} log_{2}(\frac{9}{70}))\\
+ (\frac{2}{70} log_{2}(\frac{2}{70})) + (\frac{3}{70} log_{2}(\frac{3}{70}))
+ (\frac{5}{70} log_{2}(\frac{5}{70})) + (\frac{4}{70} log_{2}(\frac{4}{70}))
+ (\frac{3}{70} log_{2}(\frac{3}{70})) + (\frac{4}{70} log_{2}(\frac{4}{70}))]
= 3.924`

Upon merger of [h] and [ŋ], there is no change in the number of unique words;
there are still 17 unique words with all their same token frequencies.
Thus, the entropy after an [h] / [ŋ] merger will be the same as it was
before the merger. The functional load, then would be 0, as the pre-merger
and post-merger entropies are identical.

Upon merger of [t] and [d], on the other hand, four pairs of words have
been collapsed. E.g., the difference between *team* and *deem* no longer
exists; there is now just one word, [Xim], where [X] represents the
result of the merger. Thus, there are only 13 unique words, and while
the total token frequency count remains the same, at 70, those 70 occurrences
are divided among only 13 unique words instead of 17.

Thus, the entropy after a [t] / [d] merger, assuming word types, is:

:math:`H_{1 - types} = -[(\frac{1}{13} log_{2}(\frac{1}{13}))
+ (\frac{1}{13} log_{2}(\frac{1}{13})) + (\frac{1}{13} log_{2}(\frac{1}{13}))
+ (\frac{1}{13} log_{2}(\frac{1}{13})) + (\frac{1}{13} log_{2}(\frac{1}{13}))\\
+ (\frac{1}{13} log_{2}(\frac{1}{13})) + (\frac{1}{13} log_{2}(\frac{1}{13}))
+ (\frac{1}{13} log_{2}(\frac{1}{13})) + (\frac{1}{13} log_{2}(\frac{1}{13}))
+ (\frac{1}{13} log_{2}(\frac{1}{13})) + (\frac{1}{13} log_{2}(\frac{1}{13}))\\
+ (\frac{1}{13} log_{2}(\frac{1}{13})) + (\frac{1}{13} log_{2}(\frac{1}{13}))]
= 3.700`

And the entropy after a [t] / [d] merger, assuming word tokens, is:

:math:`H_{1 - tokens} = -[(\frac{2}{70} log_{2}(\frac{2}{70}))
+ (\frac{4}{70} log_{2}(\frac{4}{70})) + (\frac{1}{70} log_{2}(\frac{1}{70}))
+ (\frac{6}{70} log_{2}(\frac{6}{70})) + (\frac{8}{70} log_{2}(\frac{8}{70}))\\
+ (\frac{2}{70} log_{2}(\frac{2}{70})) + (\frac{7}{70} log_{2}(\frac{7}{70}))
+ (\frac{10}{70} log_{2}(\frac{10}{70})) + (\frac{11}{70} log_{2}(\frac{11}{70}))
+ (\frac{3}{70} log_{2}(\frac{3}{70})) + (\frac{5}{70} log_{2}(\frac{5}{70}))\\
+ (\frac{4}{70} log_{2}(\frac{4}{70})) + (\frac{7}{70} log_{2}(\frac{7}{70}))]
= 3.466`


:math:`\Delta H = H_{1-types} - H_{2-types} = 4.087– 3.700 = 0.387`

And the functional load of [t] / [d] based on word tokens is:

:math:`\Delta H = H_{1-tokens} - H_{2-tokens} = 3.924– 3.466 = 0.458`

.. _method_change_minimal_pairs:

(Relative) Minimal Pair Counts
``````````````````````````````

The second means of calculating functional load that is included in PCT
is a straight count of minimal pairs, which can be relativized to the
number of words in the corpus that are potential minimal pairs—i.e. the
number of words in the corpus with at least one of the target segments.

In the above example, the number of minimal pairs that hinge on [h] vs.
[ŋ] is of course 0, so the functional load of [h] / [ŋ] is 0. The number
of minimal pairs that hinge on [t] / [d] is 3, and the number of words
with either [t] or [d] is 11; the functional load as a relativized minimal
pair count would therefore be 3/11 = 0.273. Note that here, a relatively
loose definition of minimal pair is used; specifically, two words are
considered to be a minimal pair hinging on sounds A and B if, upon merger
of A and B into a single symbol X, the words are identical. Thus, *toot* and
*dude* are considered a minimal pair on this definition, because they both
become [XuX] upon merger of [t] and [d].

The resulting calculations of functional load are thus quite similar
between the two measures, but the units are entirely different.
Functional load based on change in entropy is measured in *bits*,
while functional load based on relativized minimal pair counts is
simply a percentage. Also note that functional load based on minimal
pairs is only based on type frequency; the frequency of the usage of
the words is not used as a weighting factor, the way it can be under
the calculation of functional load as change in entropy.

.. _functional_load_gui:

Implementing the functional load function in the GUI
----------------------------------------------------

As with most analysis functions, a corpus must first be loaded (see §3). Once a corpus is loaded, use the following steps.

1. **Getting started**: Choose “Analysis” / “Calculate functional load...”
   from the top menu bar.
2. **Sound selection**: First, select which two sounds you want the functional
   load to be calculated for. Do this by clicking on “Add pair of sounds”;
   the “Select segment pair” dialogue box will open. The segment choices that
   are available will automatically correspond to all of the unique
   transcribed characters in your corpus. The order of the sounds is
   irrelevant; picking [i] first and [u] second will yield the same
   results as picking [u] first and [i] second. Once a pair of sounds
   has been selected, click “Add.” They will appear in the “Functional
   load” dialogue box. Multiple pairs of sounds can be selected and
   added to the list for calculation simultaneously. To do this without
   going back to the “Functional Load” dialogue box first, click “Add
   and create another.” When multiple pairs are selected, they can be
   treated in two different ways, listed under “Options” on the right-hand
   side of the “Functional Load” dialogue box under “Multiple segment
   pair behaviour”:

   a. **All segment pairs together**: This option allows for the calculation
      of the functional load of featural contrasts. E.g., if the pairs [e]/[i]
      and [o]/[u] are chosen, PCT will  calculate the functional load from
      both pairs at the same time. This option is useful for investigating
      the functional load of featural contrasts: e.g., if the above pairs
      are the ONLY pairs of sounds in the corpus that differ by exactly the
      single feature [high], then this option will allow you to calculate
      the functional load of the [high] contrast. Note that the results
      table will list “[e], [o]” as “sound 1” and “[i], [u]” as “sound 2”
      in this scenario, to remind you that you are getting a single functional
      load value. Note too that this does not collapse all four sounds to a
      single sound (which would erroneously also neutralize [e]/[o], [e]/[u],
      [i]/[o], [i]/[u]), but rather collapses each pair of segments and only
      then checks for any minimal pairs or drop in entropy.
   b. **Each segment pair individually**: This option cycles through the list
      of pairs and gives the functional load of each pair individually
      from the corpus. E.g., if the pairs [e]/[i] and [o]/[u] are chosen,
      you will get results showing first the functional load of [e]/[i]
      in the corpus and then the functional load of [o]/[u] in the corpus,
      independently.

3. **Functional load algorithm**: Select which of the two methods of calculation
   you want to use—i.e., minimal pairs or change in entropy.
   (See discussion above for details of each.)
4. **Tier**: Select which tier the functional load should be calculated from.
   The default is the “transcription” tier, i.e., looking at the entire
   word transcriptions. If another tier has been created (see §4.5),
   functional load can be calculated on the basis of that tier. For example,
   if a vowel tier has been created, then “minimal pairs” will be entries
   that are identical except for one entry in the vowels only, entirely
   independently of consonants. Thus, the words [mapotik] and [ʃɹaɡefli]
   would be treated as a minimal pair, given that their vowel-tier
   representations are [aoi] and [aei].
5. **Minimum frequency**: It is possible to set a minimum token frequency
   for words in the corpus in order to be included in the calculation.
   This allows easy exclusion of rare words; for example, if one were
   calculating the functional load of [s] vs. [ʃ] in English and didn’t
   set a minimum frequency, words such as *santy* (vs. *shanty*) might be
   included, which might not be a particularly accurate reflection of
   the phonological knowledge of speakers. To include all words in the
   corpus, regardless of their token frequency, set the the minimum frequency to 0.
6. **Additional parameters for minimal pairs**: If minimal pairs serve as the
   means of calculation, there are two additional parameters can be set.

   a. **Raw vs. relative count**: First, PCT can report only the raw count of
      minimal pairs that hinge on the contrast in the corpus, if you just
      want to know the scope of the contrast. On the other hand, the
      default is to relativize the raw count to the corpus size, by
      dividing the raw number by the number of lexical entries that
      include at least one instance of any of the target segments.
   b. **Include vs. ignore homophones**: Second, PCT can either include
      homophones or ignore them. For example, if the corpus includes
      separate entries for the words *sock* (n.), *sock* (v.), *shock* (n.),
      and *shock* (v.), this would count as four minimal pairs if homophones
      are included, but only one if homophones are ignored. The default is
      to ignore homophones.

7. **Additional parameters for change in entropy**: If you are calculating
   functional load using change in entropy, one additional parameter can be set.

   a. **Type or token frequency**: As described in §5.1.2.1, entropy can be
      calculated using either type or token frequencies. This option
      determines which to use.

Here is an example of selecting [m] and [n], with functional load to be
calculated on the basis of minimal pairs, only including words with a
token frequency of at least 1, from the built-in example corpus:

.. image:: _static/funtionalloaddialog.png
   :width: 90%
   :align: center

8. Results table: Once all parameters have been set, click one of the two
   “Calculate functional load” buttons. If this is the first calculation,
   the option to “start new results table” should be selected. For subsequent
   calculations, the calculation can be added to the already started table,
   for direct comparison, or a new table can be started. [Note that if a
   table is closed, new calculations will not be added to the previously
   open table; a new table must be started.] Either way, the results table
   will have the following columns, with one row per calculation: segment 1,
   segment 2, which tier was used, which measurement method was selected,
   the resulting functional load, what the minimum frequency was, and for
   calculations using minimal pairs, whether the count is absolute or
   relative and whether homophones were ignored or not. (For calculations
   using change in entropy, “N/A” values are entered into the latter two columns.)
9. Saving results: Once a results table has been generated for at least
   one pair, the table can be saved by clicking on “Save to file” at the
   bottom of the table to open a system dialogue box and save the results
   at a user-designated location.

.. image:: _static/funtionalloadresults.png
   :width: 90%
   :align: center

(Note that in the above screen shot, not all columns are visible;
they are visible only by scrolling over to the right, due to constraints
on the window size. All columns would be saved to the results file.)

To return to the function dialogue box with your most recently used
selections, click on “Reopen function dialog.” Otherwise, the results
table can be closed and you will be returned to your corpus view.

.. _functional_load_cli:

Implementing the functional load function on the command line
-------------------------------------------------------------

In order to perform this analysis on the command line, you must enter
a command in the following format into your Terminal::

   pct_funcload CORPUSFILE ARG2

...where CORPUSFILE is the name of your *.corpus file and ARG2 is either
the transcription character(s) of a single segment (if calculating relative
functional load) or the name of your segment pair(s) file (if calculating a
single functional load value). The segment pairs file must list the pairs
of segments whose functional load you wish to calculate, with each pair
separated by a tab (\t) and one pair on each line. You may also use
command line options to change various parameters of your functional
load calculations. Descriptions of these arguments can be viewed by
running ``pct_funcload –h`` or ``pct_funcload --help``. The help text from
this command is copied below, augmented with specifications of default values:

Positional arguments:

.. cmdoption:: corpus_file_name

   Name of corpus file

.. cmdoption:: pairs_file_name_or_segment

   Name of file with segment pairs (or target segment if relative fl is True)

Optional arguments:

.. cmdoption:: -h
               --help

   Show help message and exit

.. cmdoption:: -a ALGORITHM
               --algorithm ALGORITHM

   Algorithm to use for calculating functional load:
   "minpair" for minimal pair count or "deltah" for change in entropy.
   Defaults to minpair.

.. cmdoption:: -f FREQUENCY_CUTOFF
               --frequency_cutoff FREQUENCY_CUTOFF

   Minimum frequency of words to consider as possible minimal pairs or
   contributing to lexicon entropy.

.. cmdoption:: -d DISTINGUISH_HOMOPHONES
               --distinguish_homophones DISTINGUISH_HOMOPHONES

   For minimal pair FL: if False, then you'll count sock~shock
   (sock=clothing) and sock~shock (sock=punch) as just one minimal
   pair; but if True, you'll overcount alternative spellings of the
   same word, e.g. axel~actual and axle~actual. False is the value
   used by Wedel et al.

.. cmdoption:: -t TYPE_OR_TOKEN
               --type_or_token TYPE_OR_TOKEN

   For change in entropy FL: specifies whether entropy is based on type
   or token frequency.

.. cmdoption:: -e RELATIVE_FL
               --relative_fl RELATIVE_FL

   If True, calculate the relative FL of a single segment by averaging
   across the functional loads of it and all other segments.

.. cmdoption:: -s SEQUENCE_TYPE
               --sequence_type SEQUENCE_TYPE

   The attribute of Words to calculate FL over. Normally this will be
   the transcription, but it can also be the spelling or a user-specified tier.

.. cmdoption:: -o OUTFILE
               --outfile OUTFILE

   Name of output file

EXAMPLE 1: If your corpus file is example.corpus and you want to
calculate the minimal pair functional load of the segments [m] and [n]
using defaults for all optional arguments, you first need to create a
text file that contains the text “m\tn” (where \t is a tab; no quotes
in the file). Let us call this file pairs.txt. You would then run the
following command in your terminal window::

   pct_funcload example.corpus pairs.txt

EXAMPLE 2: Suppose you want to calculate the relative (average) functional
load of the segment [m]. Your corpus file is again example.corpus. You
want to use the change in entropy measure of functional load rather than
the minimal pairs measure, and you also want to use type frequency
instead of (the default value of) token frequency. In addition, you want
the script to produce an output file called output.txt.  You would need
to run the following command::

   pct_funcload example.corpus m -a deltah -t type -o output.txt

.. _pred_dist:

Predictability of Distribution
==============================

.. _about_pred_dist:

About the function
------------------

Predictability of distribution is one of the common methods of determining
whether or not two sounds in a language are contrastive or allophonic.
The traditional assumption is that two sounds that are predictably
distributed (i.e., in complementary distribution) are allophonic, and
that any deviation from complete predictability of distribution means
that the two sounds are contrastive. [Hall2009]_, [Hall2012]_ proposes a way of
quantifying predictability of distribution in a gradient fashion, using
the information-theoretic quantity of *entropy* (uncertainty), which is
also used for calculating functional load (see §5.2), which can be used
to document the *degree* to which sounds are contrastive in a language.
This has been shown to be useful in, e.g., documenting sound changes
[Hall2013b]_, understanding the choice of epenthetic vowel in a languages
[Hume2013]_, modeling intra-speaker variability (Thakur 2011),
gaining insight into synchronic phonological patterns (Hall & Hall 2013),
and understanding the influence of phonological relations on perception
([Hall2009]_, [Hall2014a]_). See also the related measure of
Kullback-Leibler divergence (§5.4), which is used in [Peperkamp2006]_
and applied to acquisition; it is also a measure of the degree to which
environments overlap, but the method of calculation differs (especially
in terms of environment selection).

It should be noted that predictability of distribution and functional
load are not the same thing, despite the fact that both give a measure
of phonological contrast using entropy. Two sounds could be entirely
unpredictably distributed (perfectly contrastive), and still have either
a low or high functional load, depending on how often that contrast is
actually used in distinguishing lexical items. Indeed, for any degree of
predictability of distribution, the functional load may be either high or
low, with the exception of the case where both are 0. That is, if two
sounds are entirely predictably distributed, and so have an entropy of
0 in terms of distribution, then by definition they cannot be used to
distinguish between any words in the language, and so their functional
load, measured in terms of change in entropy upon merger, would also be 0.

.. _method_pred_dist:

Method of calculation
---------------------

As mentioned above, predictability of distribution is calculated using
the same entropy formula as above, repeated here below, but with different
inputs.

Entropy:

:math:`H = -\sum_{i \in N} p_{i} * log_{2}(p_{i})`

Because predictability of distribution is determined between exactly two
sounds, *i* will have only two values, that is, each of the two sounds.
Because of this limitation to two sounds, entropy will range in these
situations between 0 and 1. An entropy of 0 means that there is 0
uncertainty about which of the two sounds will occur; i.e., they are
perfectly predictably distributed (commonly associated with being
allophonic). This will happen when one of the two sounds has a probability
of 1 and the other has a probability of 0. On the other hand, an entropy
of 1 means that there is complete uncertainty about which of the two
sounds will occur; i.e., they are in perfectly overlapping distribution
(what might be termed “perfect” contrast). This will happen when each
of the two sounds has a probability of 0.5.

Predictability of distribution can be calculated both within an individual
environment and across all environments in the language; these two
calculations are discussed in turn.

.. _method_pred_dist_environment:

Predictability of Distribution in a Single Environment
``````````````````````````````````````````````````````

For any particular environment (e.g., word-initially; between vowels;
before a [+ATR] vowel with any number of intervening consonants; etc.),
one can calculate the probability that each of two sounds can occur.
This probability can be calculated using either types or tokens, just
as was the case with functional load. Consider the following toy data,
which is again repeated from the examples of functional load, though
just the original distribution of sounds.


+--------+-----------------------+
|        |        Original       |
|        +--------+------+-------+
|  Word  | Trans. | Type | Token |
|        |        | Freq.| Freq. |
+========+========+======+=======+
|  hot   |  [hɑt] |    1 |     2 |
+--------+--------+------+-------+
|  song  |  [sɑŋ] |    1 |     4 |
+--------+--------+------+-------+
|  hat   |  [hæt] |    1 |     1 |
+--------+--------+------+-------+
|  sing  |  [sɪŋ] |    1 |     6 |
+--------+--------+------+-------+
|  tot   |  [tɑt] |    1 |     3 |
+--------+--------+------+-------+
|  dot   |  [dɑt] |    1 |     5 |
+--------+--------+------+-------+
|  hip   |  [hɪp] |    1 |     2 |
+--------+--------+------+-------+
|  hid   |  [hɪd] |    1 |     7 |
+--------+--------+------+-------+
|  team  |  [tim] |    1 |     5 |
+--------+--------+------+-------+
|  deem  |  [dim] |    1 |     5 |
+--------+--------+------+-------+
|  toot  |  [tut] |    1 |     9 |
+--------+--------+------+-------+
|  dude  |  [dud] |    1 |     2 |
+--------+--------+------+-------+
|  hiss  |  [hɪs] |    1 |     3 |
+--------+--------+------+-------+
|  his   |  [hɪz] |    1 |     5 |
+--------+--------+------+-------+
| sizzle | [sɪzəl]|    1 |     4 |
+--------+--------+------+-------+
| dizzy  |  [dɪzi]|    1 |     3 |
+--------+--------+------+-------+
| tizzy  |  [tɪzi]|    1 |     4 |
+--------+--------+------+-------+
|      Total      |   17 |    70 |
+--------+--------+------+-------+


Consider the distribution of [h] and [ŋ], word-initially. In this
environment, [h] occurs in 6 separate words, with a total token frequency
of 20. [ŋ] occurs in 0 words, with, of course, a token frequency of 0.
The probability of [h] occurring in this position as compared to [ŋ],
then, is 6/6 based on types, or 20/20 based on tokens. The entropy of
this pair of sounds in this context, then, is:

:math:`H_{types/tokens} = -[1 log_{2}(1) + 0 log_{2} (0)] = 0`

Similar results would obtain for [h] and [ŋ] in word-final position,
except of course that it’s [ŋ] and not [h] that can appear in this environment.

For [t] and [d] word-initially, [t] occurs 4 words in this environment,
with a total token frequency of 21, and [d] also occurs in 4 words,
with a total token frequency of 15. Thus, the probability of [t] in
this environment is 4/8, counting types, or 21/36, counting tokens, and
the probability of [d] in this environment is 4/8, counting types, or
15/36, counting tokens. The entropy of this pair of sounds is therefore:

:math:`H_{types} = -[(\frac{4}{8} log_{2}(\frac{4}{8}))
+ (\frac{4}{8} log_{2}(\frac{4}{8}))] = 1`

:math:`H_{types} = -[(\frac{21}{36} log_{2}(\frac{21}{36}))
+ (\frac{15}{36} log_{2}(\frac{15}{36}))] = 0.98`

In terms of what environment(s) are interesting to examine, that is of
course up to individual researchers. As mentioned in the preface to §6,
these functions are just tools. It would be just as possible to calculate
the entropy of [t] and [d] in word-initial environments before [ɑ],
separately from word-initial environments before [u]. Or one could
calculate the entropy of [t] and [d] that occur anywhere in a word
before a bilabial nasal...etc., etc. The choice of environment should
be phonologically informed, using all of the resources that have
traditionally been used to identify conditioning environments of interest.
See also the caveats in the following section that apply when one is
calculating systemic entropy across multiple environments.

.. _pred_dist_envs:

Predictability of Distribution across All Environments (Systemic Entropy)
`````````````````````````````````````````````````````````````````````````

While there are times in which knowing the predictability of distribution
within a particular environment is helpful, it is generally the case that
phonologists are more interested in the relationship between the two
sounds as a whole, across all environments. This is achieved by
calculating the weighted average entropy across all environments in which
at least one of the two sounds occurs.

As with single environments, of course, the selection of environments
for the systemic measure need to be phonologically informed. There are
two further caveats that need to be made about environment selection when
multiple environments are to be considered, however: (1) **exhaustivity** and
(2) **uniqueness**.

With regard to **exhausitivity**: In order to calculate the total
predictability of distribution of a pair of sounds in a language, one
must be careful to include all possible environments in which at least
one of the sounds occurs. That is, the total list of environments needs
to encompass all words in the corpus that contain either of the two
sounds; otherwise, the measure will obviously be incomplete. For example,
one would not want to consider just word-initial and word-medial positions
for [h] and [ŋ]; although the answer would in fact be correct (they have 0
entropy across these environments), it would be for the wrong reason—i.e.,
it ignores what happens in word-final position, where they *could* have had
some other distribution.

With regard to **uniqueness**: In order to get an *accurate* calculation of the
total predictability of distribution of a pair of sounds, it is important
to ensure that the set of environments chosen do not overlap with each other,
to ensure that individual tokens of the sounds are not being counted multiple
times. For example, one would not want to have both [#__] and [__i] in the
environment list for [t]/[d] while calculating systemic entropy, because
the words *team* and *deem* would appear in both environments, and the sounds
would (in this case) appear to be “more contrastive” (less predictably
distributed) than they might otherwise be, because the contrasting nature
of these words would be counted twice.

To be sure, one can calculate the entropy in a set of individual
environments that are non-exhaustive and/or overlapping, for comparison
of the differences in possible generalizations. But, in order to get an
accurate measure of the total predictability of distribution, the set of
environments must be both exhaustive and non-overlapping. As will be
described below, PCT will by default check whether any set of environments
you provide does in fact meet these characteristics, and will throw a
warning message if it does not.

It is also possible that there are multiple possible ways of developing
a set of exhaustive, non-overlapping environments. For example,
“word-initial” vs. “non-word-initial” would suffice, but so would
“word-initial” vs. “word-medial” vs. “word-final.” Again, it is up to
individual researchers to determine which set of environments makes the
most sense for the particular pheonmenon they are interested in.
See [Hall2012]_ for a comparison of two different sets of possible
environments in the description of Canadian Raising.

Once a set of exhaustive and non-overlapping environments has been
determined, the entropy in each individual environment is calculated,
as described in §6.2.2.1. The frequency of each environment itself is
then calculated by examining how many instances of the two sounds
occurred in each environment, as compared to all other environments, and
the entropy of each environment is weighted by its frequency. These
frequency-weighted entropies are then summed to give the total average
entropy of the sounds across the environments. Again, this value will
range between 0 (complete predictability; no uncertainty) and 1 (complete
unpredictability; maximal uncertainty). This formula is given below; e
represents each individual environment in the exhaustive set of
non-overlapping environments.

Formula for systemic entropy:

:math:`H_{total} = -\sum_{e \in E} H(e) * p(e)`

As an example, consider [t]/[d]. One possible set of exhaustive,
non-overlapping environments for this pair of sounds is (1) word-initial
and (2) word-final. The relevant words for each environment are shown in
the table below, along with the calculation of systemic entropy from
these environments.

The calculations for the entropy of word-initial environments were given
above, in §5.2.2.1; the calculations for word-final environments are analogous.

To calculate the probability of the environments, we simply count up the
number of total words (either types or tokens) that occur in each
environment, and divide by the total number of words (types or tokens)
that occur in all environments.

Calculation of systemic entropy of [t] and [d]:

+------+-------+-------+---------------------------------+----------------------------------+
| *e*  | [t]-  | [d]-  |             Types               |             Types                |
|      |       |       +-------+-------+-----------------+-------+--------+-----------------+
|      | words | words | H(*e*)| p(*e*)| p(*e*) * H(*e*) | H(*e*)| p(*e*) | p(*e*) * H(*e*) |
+======+=======+=======+=======+=======+=================+=======+========+=================+
| [#__]| tot,  | dot,  |     1 |(4+4)/ |          0.533  |   0.98|(21+15)/|          0.543  |
|      | team, | dude, |       |(8+7)  |                 |       |(36+29) |                 |
|      | toot, | deem, |       |=8/15  |                 |       |=36/65  |                 |
|      | tizzy | dizzy |       |       |                 |       |        |                 |
+------+-------+-------+-------+-------+-----------------+-------+--------+-----------------+
| [__#]| hot,  | hid,  | 0.863 |7/15   |          0.403  |  0.894| 29/65  |          0.399  |
|      | hat,  | dude  |       |       |                 |       |        |                 |
|      | tot,  |       |       |       |                 |       |        |                 |
|      | dot,  |       |       |       |                 |       |        |                 |
|      | toot  |       |       |       |                 |       |        |                 |
+------+-------+-------+-------+-------+-----------------+-------+--------+-----------------+
|                                      |0.533+0.403=0.936|                |0.543+0.399=0.942|
+--------------------------------------+-----------------+----------------+-----------------+

In this case, [t]/[d] are relatively highly unpredictably distributed
(contrastive) in both environments, and both environments contributed
approximately equally to the overall measure. Compare this to the example
of [s]/[z], shown below.

Calculation of systemic entropy of [s] and [z]:

+------+-------+-------+---------------------------------+----------------------------------+
| *e*  | [s]-  | [z]-  |             Types               |             Types                |
|      |       |       +-------+-------+-----------------+-------+--------+-----------------+
|      | words | words | H(*e*)| p(*e*)| p(*e*) * H(*e*) | H(*e*)| p(*e*) | p(*e*) * H(*e*) |
+======+=======+=======+=======+=======+=================+=======+========+=================+
| [#__]| song, |       |     0 | 3/8   |          0      |   0   |14/33   |          0      |
|      | sing, |       |       |       |                 |       |        |                 |
|      | sizzle|       |       |       |                 |       |        |                 |
+------+-------+-------+-------+-------+-----------------+-------+--------+-----------------+
| [__#]| hiss  | his   | 1     |2/8    |          0.25   |  0.954| 8/33   |          0.231  |
+------+-------+-------+-------+-------+-----------------+-------+--------+-----------------+
| [V_V]|       |sizzle,| 0     |3/8    |          0      |  0    | 11/33  |          0      |
|      |       |dizzy, |       |       |                 |       |        |                 |
|      |       |tizzy  |       |       |                 |       |        |                 |
+------+-------+-------+-------+-------+-----------------+-------+--------+-----------------+
|                                      |       0.25      |                |     0.231       |
+--------------------------------------+-----------------+----------------+-----------------+

In this case, there is what would traditionally be called a contrast word
finally, with the minimal pair *hiss* vs. *his*; this contrast is neutralized
(made predictable) in both word-initial position, where [s] occurs but
[z] does not, and intervocalic position, where [z] occurs but [s] does
not. The three environments are roughly equally probable, though the
environment of contrast is somewhat less frequent than the environments
of neutralization. The overall entropy of the pair of sounds is on
around 0.25, clearly much closer to perfect predictability (0 entropy)
than [t]/[d].

Note, of course, that this is an entirely fictitious example—that is,
although these are real English words, one would **not** want to infer
anything about the actual relationship between either [t]/[d] or [s]/[z]
on the basis of such a small corpus. These examples are simplified for
the sake of illustrating the mathematical formulas!

.. _pred_dist_all:

“Predictability of Distribution” Across All Environments (i.e., Frequency-Only Entropy)
```````````````````````````````````````````````````````````````````````````````````````

Given that the calculation of predictability of distribution is based on
probabilities of occurrence across different environments, it is also
possible to calculate the overall entropy of two segments using their
raw probabilities and ignoring specific environments. Note that this
doesn’t really reveal anything about predictability of distribution per
se; it simply gives the uncertainty of occurrence of two segments that
is related to their relative frequencies. This is calculated by simply
taking the number of occurrences of each of sound 1 (N1) and sound 2
(N2) in the corpus as a whole, and then applying the following formula:

Formula for frequency-only entropy:

:math:`H = (-1) * [(\frac{N1}{N1+N2}) log_{2} (\frac{N1}{N1+N2})
+(\frac{N2}{N1+N2}) log_{2} (\frac{N2}{N1+N2})]`

The entropy will be 0 if one or both of the sounds never occur(s) in the
corpus. The entropy will be 1 if the two sounds occur with exactly the
same frequency. It will be a number between 0 and 1 if both sounds occur,
but not with the same frequency.

Note that an entropy of 1 in this case, which was analogous to
perfect contrast in the environment-specific implementation of this
function, does *not* align with contrast here. For example, [h] and [ŋ]
in English, which are in complementary distribution, could theoretically
have an entropy of 1 if environments are ignored and they happened to
occur with exactly the same frequency in some corpus. Similarly, two
sounds that do in fact occur in the same environments might have a low
entropy, close to 0, if one of the sounds is vastly more frequent than
the other. That is, this calculation is based ONLY on the frequency of
occurrence, and not actually on the distribution of the sounds in the
corpus. This function is thus useful only for getting a sense of the
frequency balance / imbalance between two sounds. Note that one can
also get total frequency counts for any segment in the corpus through
the “Summary” information feature (§3.6).

.. _pred_dist_gui:

Implementing the predictability of distribution function in the GUI
-------------------------------------------------------------------

Assuming a corpus has been opened or created, predictability of
distribution is calculated using the following steps.

1. **Getting started**: Choose “Analysis” / “Calculate predictability of
   distribution...” from the top menu bar.
2. **Sound selection**: On the left-hand side of the “Predictability of
   distribution” dialogue box, select the two sounds of interest by
   clicking “Add pair of sounds. The order of the sounds is
   irrelevant; picking [i] first and [u] second will yield the
   same results as [u] first and [i] second. Currently, PCT only
   allows entire segments to be selected; the next release will allow
   a “sound” to be defined as a collection of feature values. The
   segment choices that are available will automatically correspond
   to all of the unique transcribed characters in your corpus. You can
   select more than one pair of sounds to examine in the same environments;
   each pair of sounds will be treated individually.
3. **Environments**: Click on “Add environment” to add an environment in
   which to calculate predictability of distribution. The left side of
   the “Create environment” dialogue box allows left-hand environments
   to be specified (e.g., [+back]___), while the right side allows
   right-hand environments to be specified (e.g., __#). Both can be used
   simultaneously to specify environments on both sides (e.g., [+back]__#).

   a. **Basis for building environments (segments vs. features)**: Environments
      can be selected either as entire segments (including #) or as bundles
      of features. Select from the drop-down menu which you prefer. Each
      side of an environment can be specified using either type.
   b. **Segment selection**: To specify an environment using segments, simply
      click on the segment desired.
   c. **Feature selection**: To specify an environment using features, select
      the first feature from the list (e.g., [voice]), and then specify
      whether you want it to be [+voice] or [-voice] by selecting “Add
      [+feature]” or “Add [-feature]” as relevant. To add another feature
      to this same environment, select another feature and again add
      either the + or – value.
   d. **No environments**: Note that if NO environments are added, PCT will
      calculate the overall predictability of distribution of the two
      sounds based only on their frequency of occurrence. This will simply
      count the frequency of each sound in the pair and calculate the
      entropy based on those frequencies (either type or token). See
      below for an example of calculating environment-free entropy for
      four different pairs in the sample corpus:

.. image:: _static/prodfreq.png
   :width: 90%
   :align: center

4. **Environment list**: Once all features / segments for a given environment
   have been selected, for both the left- and right-hand sides, click on
   “Add”; it will appear back in the “Predictability of Distribution”
   dialogue box in the environment list. To automatically return to the
   environment selection window to select another environment, click on
   “Add and select another” instead. Individual environments from the
   list can be selected and removed if it is determined that an environment
   needs to be changed. It is this list that PCT will verify as being
   both exhaustive and unique; i.e., the default is that the environments
   on this list will exhaustively cover all instances in your corpus of
   the selected sounds, but will do so in such a way that each instance
   is counted exactly once.
5. **Analysis tier**: Under “Options,” first pick the tier on which you want
   predictability of distribution to be calculated. The default is for
   the entire transcription to be used, such that environments are defined
   on any surrounding segments. If a separate tier has been created as part
   of the corpus (see §4.5), however, predictability of distribution can
   be calculated on this tier. For example, one could extract a separate
   tier that contains only vowels, and then calculate predictability of
   distribution based on this tier. This makes it much easier to define
   non-adjacent contexts. For instance, if one wanted to investigate the
   extent to which [i] and [u] are predictably distributed before front
   vs. back vowels, it will be much easier to to specify that the relevant
   environments are __[+back] and __[-back] on the vowel tier than to try
   to account for possible intervening segments on the entire transcription
   tier.
6. **Type vs. Token Frequency**: Next, pick whether you want the calculation
   to be done on types or tokens, assuming that token frequencies are
   available in your corpus. If they are not, this option will not be
   available. (Note: if you think your corpus does include token frequencies,
   but this option seems to be unavailable, see §3.2.1 on the required
   format for a corpus.)
7. **Exhaustivity & Uniqueness**: The default is for PCT to check for both
   exhaustivity and uniqueness of environments, as described above in
   §5.3.2.2. Un-checking this box will turn off this mechanism. For
   example, if you wanted to compare a series of different possible
   environments, to see how the entropy calculations differ under
   different generalizations, uniqueness might not be a concern. Keep
   in mind that if uniqueness and exhaustivity are not met, however,
   the calculation of systemic entropy will be inaccurate.

   a. If you ask PCT to check for exhaustivity, and it is not met, an error
      message will appear that warns you that the environments you have
      selected do not exhaustively cover all instances of the symbols in
      the corpus, as in the following; the “Show details...” option has
      been clicked to reveal the specific words that occur in the corpus
      that are not currently covered by your list of environments.
      Furthermore, a .txt file is automatically created that lists all
      of the words, so that the environments can be easily adjusted. This
      file is stored in the ERRORS folder within the working directory
      that contains the PCT software, and can be accessed directly by
      clicking “Open errors directory.” If exhaustivity is not important,
      and only the entropy in individual environments matters, then it is
      safe to not enforce exhaustivity; it should be noted that the
      weighted average entropy across environments will NOT be accurate
      in this scenario, because not all words have been included.

.. image:: _static/proderror.png
   :width: 90%
   :align: center


   b. If you ask PCT to check for uniqueness, and it is not met, an error
      message will appear that indicates that the environments
      are not unique, as shown below. Furthermore, a .txt file explaining
      the error and listing all the words that are described by multiple
      environments in your list is created automatically and stored in
      the ERRORS folder within the working directory that contains the
      PCT software. Clicking “Show details” in the error box also reveals
      this information.

.. image:: _static/proderror2.png
   :width: 90%
   :align: center

Here’s an example of correctly exhaustive and unique selections for
calculating the predictability of distribution based on token frequency
for [s] and [ʃ] in the sample corpus:


.. image:: _static/proddialog.png
   :width: 90%
   :align: center

8. **Entropy calculation / results**: Once all environments have been specified,
   click “Calculate predictability of distribution.” If you want to start
   a new results table, click that button; if you’ve already done at least
   one calculation and want to add new calculations to the same table,
   select the button with “add to current results table.” Results will
   appear in a pop-up window on screen.  The last row for each pair gives
   the weighted average entropy across all selected environments, with
   the environments being weighted by their own frequency of occurrence.
   See the following example:

.. image:: _static/prodresults.png
   :width: 90%
   :align: center

9. **Output file / Saving results**: If you want to save the table of results,
   click on “Save to file” at the bottom of the table. This opens up a
   system dialogue box where the directory and name can be selected.

To return to the function dialogue box with your most recently used
selections, click on “Reopen function dialog.” Otherwise, the results
table can be closed and you will be returned to your corpus view.

.. _kl:

Kullback-Leibler Divergence
===========================

.. _about_kl:

About the function
------------------

Another way of measuring the distribution of environments as a proxy for
phonological relationships is the Kullback-Leibler (KL) measure of the
dissimilarity between probability distributions [Kullback1951]_.
Sounds that are distinct phonemes appear in the same environments, that is,
there are minimal or near-minimal, pairs. Allophones, on the other hand,
have complementary distribution, and never appear in the same environment.
Distributions that are identical have a KL score of 0, and the more
dissimilar two distributions, the higher the KL score. Applied to
phonology, the idea is to calculate the probability of two sounds across
all environments in a corpus, and use KL to measure their dissimilarity.
Scores close to 0 suggest that the two sounds are distinct phonemes,
since they occur in many of the same environments (or else there is
extensive free variation). Higher scores represent higher probabilities
that the two sounds are actually allophones. Since KL scores have no
upper bound, it is up to the user to decide what counts as “high enough”
for two sounds to be allophones (this is unlike the predictability of
distribution measure described in §5.3). See [Peperkamp2006]_
for a discussion of how to use Z-Scores to make this discrimination.

As with the predictability of distribution measure in §5.3, spurious
allophony is also possible, since many sounds happen to have non-overlapping
distributions. As a simple example, vowels and consonants generally have
high KL scores, because they occur in such different environments.
Individual languages might have cases of accidental complementary
distribution too. For example, in English /h/ occurs only initially and
[ŋ] only occurs finally. However, it is not usual to analyze them as
being in allophones of a single underlying phonemes. Instead, there is
a sense that allophones need to be phonetically similar to some degree,
and /h/ and /ŋ/ are simply too dissimilar.

To deal with this problem, [Peperkamp2006]_ suggest two
“linguistic filters” that can be applied, which can help identify
cases of spurious allophones, such as /h/ and /ŋ/. Their filters do
not straightforwardly apply to CorpusTools, since they use 5-dimensional
vectors to represent sounds, while in CorpusTools most sounds have only
binary features. An alternative filter is used instead, and it is
described below.

It is important to note that this function's usefulness depends on the
level of analysis in your transcriptions. In many cases, corpora are
transcribed at a phonemic level of detail, and KL will not be very
informative. For instance, the IPHOD corpus does not distinguish between
aspirated and unaspirated voiceless stops, so you cannot measure their
KL score.

.. _method_kl:

Method of calculation
---------------------

All calculations were adopted from [Peperkamp2006]_. The variables
involves are as follows: s is a segment, *c* is a context, and *C* is the
set of all contexts. The Kullback-Leibler measure of dissimilarity between
the distributions of two segments is the sum for all contexts of the
entropy of the contexts given the segments:

KL Divergence:

:math:`m_{KL} (s_1,s_2) = \sum_{c \in C} P(c|s_1) log (\frac{P(c|s_1)}{P(c|s_2)})
+ P(c|s_2) log (\frac{P(c|s_2)}{P(c|s_1)}) `

The notation :math:`P(c|s)` means the probability of context c given segment s,
and it is calculated as follows:

:math:`P(c|s) = \frac{n(c,s) + 1}{n(s) + N}`

...where *n(c,s)* is the number of occurrences of segments *s* in context *c*.
[Peperkamp2006]_ note that this equal to the number of occurrences
of the sequence *sc*, which suggests that they are only looking at the right
hand environment. This is probably because in their test corpora, they were
looking at allophones conditioned by the following segment. PCT provides
the option to look only at the left-hand environment, only at the right-hand
environment, or at both.

[Peperkamp2006]_ then compare the average entropy values of each segment,
in the pair. The segment with the higher entropy is considered to be a
surface representation (SR), i.e. an allophone, while the other is the
underlying representation (UR). In a results window in PCT, this is given
as “Possible UR.” More formally:

:math:`SR = \max_{SR,UR}[\sum_{c} P(c|s) log \frac{P(c|s)}{P(c)}]`

[Peperkamp2006]_ give two linguistic filters for getting rid of spurious
allophones, which rely on sounds be coded as 5-dimensional vectors. In
PCT, this concept as been adopted to deal with binary features. The aim
of the filter is the same, however. In a results window the column labeled
“spurious allophones” gives the result of applying this filter.

The features of the supposed UR and SR are compared. If they differ by
only one feature, they are considered plausibly close enough to be
allophones, assuming the KL score is high enough for this to be
reasonable (which will depend on the corpus and the user's expectations).
In this case, the “spurious allophones?” results will say ‘No.’

If they differ by more than 1 feature, PCT checks to see if there any
other sounds in the corpus that are closer to the SR than the UR is.
For instance, if /p/ and /s/ are compared in the IPHOD corpus, /p/ is
considered the UR and /s/ is the SR. The two sounds differ by two
features, namely [continuant] and [coronal]. There also exists another
sound, /t/, which differs from /s/ by [continuant], but not by [coronal]
(or any other feature). In other words, /t/ is more similar to /s/ than
/p/ is to /s/. If such an “in-between” sound can be found, then in the
“spurious allophones?” column, the results will say ‘Yes.’

If the two sounds differ by more than 1 feature, but no in-between sound
can be found, then the “spurious allophones?” results will say ‘Maybe.’

Note too that a more direct comparison of the acoustic similarity of
sounds can also be conducted using the functions in §5.8.

.. kl_gui:

Implementing the Kullback-Leibler Divergence function in the GUI
----------------------------------------------------------------

To implement the KL function in the GUI, select “Analysis” / “Calculate
Kullback-Leibler...” and then follow these steps:

1. Pair of sounds: Click on “Add pair of sounds” to open the “Select
   segment pair” dialogue box. The segment choices that are available
   will automatically correspond to all of the unique transcribed
   characters in your corpus; click on “Consonants” and/or “Vowels”
   to see the options. You can select more than one pair of sounds to
   examine in the same environments; each pair of sounds will be treated
   individually. Selecting more than two sounds at a time will run the
   analysis on all possible pairs of those sounds (e.g., selecting [t],
   [s], and [d] will calculate the KL score for [t]~[s], [s]~[d], and
   [t]~[d]).
2. Contexts: Using KL requires a notion of “context,” and there are three
   options: left, right, or both. Consider the example word [atema]. If
   using the “both” option, then this word consists of these environments:
   [#\_t], [a\_e], [t\_m], [e\_a], and [m\_#]. If the left-side option is chosen,
   then only the left-hand side is used, i.e., the word consists of the
   environments [#\_], [a\_], [t\_], [e\_], and [m\_]. If the right-side option
   is chosen, then the environments in the word are [\_t], [\_e], [\_m], [\_a],
   and [\_#]. Note that the word boundaries don’t count as elements of words,
   but can count as parts of environments.
3. Results: Once all selections have been made, click “Calculate
   Kullback-Leibler.” If you want to start a new results table, click
   that button; if you’ve already done at least one calculation and
   want to add new calculations to the same table, select the button
   with “add to current results table.” Results will appear in a pop-up
   window on screen. Each member of the pair is listed, along with which
   context was selected, the entropy of each segment, the KL score, which
   of the two members of the pair is more likely to be the UR (as described
   above), and PCT’s judgment as to whether this is a possible case of
   spurious allophones based on the featural distance.
4. Output file / Saving results: If you want to save the table of results,
   click on “Save to file” at the bottom of the table. This opens up a
   system dialogue box where the directory and name can be selected.

To return to the function dialogue box with your most recently used
selections, click on “Reopen function dialog.” Otherwise, the results
table can be closed and you will be returned to your corpus view.

An example of calculating the KL scores in the Example corpus, with the
sounds [s], [ʃ], [t], [n], [m], [e], [u] selected (and therefore all
pairwise comparisons thereof calculated), examining only right-hand side
contexts:

The “Select segment pair” dialogue box, within the “Kullback-Leibler”
dialogue box:

.. image:: _static/segmentpair.png
   :width: 90%
   :align: center

The “Kullback-Leibler” dialogue box, with pairs of sounds and contexts
selected:

.. image:: _static/kldialog.png
   :width: 90%
   :align: center

The resulting table of results:

.. image:: _static/klresults.png
   :width: 90%
   :align: center

.. _string_similarity:

String similarity and neighbourhood density
===========================================

.. _about_string_similarity:

About the functions
-------------------

String similarity is any measure of how similar any two sequences of
characters are. These character strings can be strings of letters or
phonemes; both of the methods of calculation included in PCT allow for
calculations using either type of character. It is, therefore, a basic
measure of overall form-based similarity.

String similarity finds more widespread use in areas of linguistics other
than phonology; it is, for example, used in Natural Language Processing
applications to determine, for example, possible alternative spellings
when a word has been mistyped. It is, however, also useful for determining
how phonologically close any two words might be.

String similarity could be part of a calculation of morphological
relatedness, if used in conjunction with a measure of semantic similarity
(see, e.g., [Hall2014b]_). In particular, it can be used in conjunction
with the Frequency of Alternation function of PCT (see §5.6) as a means
of calculating the frequency with which two sounds alternate with each
other in a language.

Some measure of string similarity is also used to calculate neighbourhood
density (e.g. [Greenberg1964]_; [Luce1998]_; [Yao2011]_),
which has been shown to affect phonological processing. A phonological
“neighbour” of some word X is a word that is similar in some close way
to X. For example, it might differ by maximally one phone (through deletion,
addition, or subsitution) from X. X’s neighbourhood density, then, is the
number of words that fit the criterion for being a neighbour.

.. _method_string_similarity:

Method of calculation: String similarity
----------------------------------------

.. _edit_distance:

Levenshtein Edit Distance
`````````````````````````

Edit distance is defined as the minimum number of one-symbol deletions,
additions, and substitutions necessary to turn one string into another.
For example, *turn* and *burn* would have an edit distance of 1, as the only
change necessary is to turn the <t> into a <b>, while the edit distance
between *turn* and *surfs* would be 3, with <t> becoming <s>, <n> becoming
<f>, and ∅ becoming <s> at the end of the word. All such one-symbol
changes are treated as equal in Levenshtein edit distance, unlike
phonological edit distance, described in the following section. Generally
speaking, the neighbourhood density of a particular lexical item is
measured by summing the number of lexical items that have an edit distance
of 1 from that item [Luce1998]_.

.. _phono_edit_distance:

Phonological Edit Distance
``````````````````````````

Phonological edit distance is quite similar to Levenshtein edit distance,
in that it calculates the number of one-symbol changes between strings,
but it differs in that changes are weighted based on featural similarity.
For example, depending on the feature system used, changing <t> to <s>
might involve a single feature change (from [-cont] to [+cont]), while
changing <t> to <b> might involve two (from [-voice, +cor] to [+voice,
-cor]). By default, the formula for calculating the phonological distance
between two segments—or between a segment and “silence”, i.e. insertion
or deletion—is the one used in the Sublexical Learner [Allen2014]_.
When comparing two segments, the distance between them is equal to the
sum of the distances between each of their feature values: the distance
between two feature values that are identical is 0, while the distance
between two opposing values (+/- or -/+) is 1, and the distance between
two feature values in the case that just one of them is 0 (unspecified)
is set to by default to 0.25. When comparing a segment to “silence”
(insertion/deletion), the silence is given feature values of 0 for
all features and then compared to the segment as normal.

.. _khorsi:

Khorsi (2012) Similarity Metric
```````````````````````````````

Khorsi (2012) proposes a particular measure of string similarity based
on orthography, which he suggests can be used as a direct measure of
morphological relatedness. PCT allows one to calculate this measure,
which could be used, as Khorsi describes, on its own, or could be used
in conjunction with other measures (e.g., semantic similarity) to create
a more nuanced view.

This measure starts with the sum of the log of the inverse of the
frequency of occurrence of each of the letters in the longest common
shared sequence between two words, and then subtracts the sum of the
log of the inverse of the frequency of the letters that are not shared,
as shown below.

Formula for string similarity from [Khorsi2012]_:

:math:`\sum_{i=1}^{\lVert LCS(w_1,w_2) \rVert} log (\frac{1}{freq(LCS(w_1,w_2)[i])})
- \sum_{i=1}^{\lVert \overline{LCS(w_1,w_2)} \rVert} log (\frac{1}{freq(\overline{LCS(w_1,w_2)}[i])})`

Note:
* *w1, w2* are two words whose string similarity is to be measured
* *LCS(w1, w2)* represents the Longest Common Shared Sequence of symbols
  between the two words

As with other functions, the frequency measure used for each character
will be taken from the current corpus. This means that the score will
be different for a given pair of words (e.g., *pressed* vs. *pressure*)
depending on the frequency of the individual characters in the loaded corpus.

.. _method_neighborhood_density:

Method of calculation: Neighbourhood density
--------------------------------------------

A word's neighborhood density is equal to the number of other words in the
corpus similar to that word (or, if using token frequencies, the sum of
those words' counts). The threshold that defines whether two words are
considered similar to each other can be calculated using any of the three
distance metrics described in §5.5.2: Levenshtein edit distance,
phonological edit distance, or Khorsi (2012) similarity. As implemented
in PCT, for a query word, each other word in the corpus is checked for
its similarity to the query word and then added to a list of neighbors
if sufficiently similar.

For further detail about the available distance/similarity metrics,
refer to §5.5.2.

.. _string_similarity_gui:

Implementing the string similarity function in the GUI
------------------------------------------------------

To start the analysis, click on “Analysis” / “Calculate string similarity...”
in the main menu, and then follow these steps:

1. **String similarity algorithm**: The first step is to choose which of the
   three methods described above is to be used to calculate string similarity.
   The options are phonological edit distance, standard (Levenshtein) edit
   distance, and the algorithm described above and in [Khorsi2012]_.
2. **Comparison type**: Next, choose what kind of comparison is to be done.
   One can either take a single word and get its string similarity score
   to every other word in the corpus (useful, for example, when trying
   to figure out which words are most / least similar to a given word,
   as one might for stimuli creation), or can compare individual pairs
   of words (useful if a limited set of pre-determined words is of
   interest). For each of these, you can use words that already exist
   in the corpus or calculate the similarity for words (or non-words)
   that are not in the corpus. Note that these words will NOT be added
   to the corpus itself; if you want to globally add the word (and
   therefore have its own properties affect calculations), please use
   the instructions in §4.6.4.

   a. **One word in the corpus**: To compare the similarity of one word that
      already exists in the corpus to every other word in the corpus,
      simply select “Compare one word to entire corpus” and enter the
      single word into the dialogue box, using its standard orthographic
      representation. Note that you can choose later which tier string
      similarity will be calculated on (spelling, transcription, etc.);
      this simply identifies the word for PCT.
   b. **One word not in the corpus**: Click on “Calculate for a word/nonword
      not in the corpus” and then select “Create word/nonword” to enter
      the new word.

      i. **Spelling**: Enter the spelling for your new word / nonword using
         the regular input keyboard on your computer.
      ii. **Transcription**: To add in the phonetic transcription of the new
          word, it is best to use the provided inventory. While it is
          possible to type directly in to the transcription box, using
          the provided inventory will ensure that all characters are
          understood by PCT to correspond to existing characters in the
          corpus (with their concomitant featural interpretation). Click
          on “Show inventory” and then choose to show “Consonants,”
          “Vowels,” and/or other. (If there is no featural interpretation
          of your inventory, you will simply see a list of all the
          available segments, but they will not be classified by major
          category.) Clicking on the individual segments will add them to
          the transcription. The selections will remain even when the
          sub-inventories are hidden; we allow for showing / hiding the
          inventories to ensure that all relevant buttons on the dialogue
          box are available, even on small computer screens. Note that
          you do NOT need to include word boundaries at the beginning
          and end of the word, even when the boundary symbol is included
          as a member of the inventory; these will be assumed
          automatically by PCT.
      iii. **Frequency and other columns**: These can be left at the default.
           Note that entering values will NOT affect the calculation;
           there is no particular need to enter anything here (it is an
           artifact of using the same dialogue box here as in the “Add Word”
           function described in §4.6.4).
      iv. **Create word**: To finish and return to the “String similarity”
          dialogue box, click on “Create word.”

   c. **Single word pair (in or not in) the corpus**: If the similarity of an
      individual word pair is to be calculated, one can enter the pair
      directly into the dialogue box. For each word that **is** in the corpus,
      simply enter its standard orthographic form. For each word that is
      **not** in the corpus, you can add it by selecting “Create word/nonword”
      and following the steps described immediately above in (2b).
   d. **List of word pairs (in the corpus)**: If there is a long list of pairs
      of words, one can simply create a tab-delimited plain .txt file
      with one *word pair* per line. In this case, click on “Choose word
      pairs file” and select the .txt file in the resulting system
      dialogue box. Note that this option is currently available only
      for words that already exist in the corpus, and that these pairs
      should be listed using their standard orthographic representations.

2. **Tier**: The tier from which string similarity is to be calculated can
   be selected. Generally, one is likely to care most about either
   spelling or transcription, but other tiers (e.g., a vowel tier)
   can also be selected; in this case, all information removed from
   the tier is ignored. Words should always be entered orthographically
   (e.g., when telling PCT what word pairs to compare). If similarity is
   to be calculated on the basis of spelling, words that are *entered* are
   broken into their letter components. If similarity is to be calculated
   on the basis of transcription, the transcriptions are looked up in the
   corpus. If a word does not occur in the corpus, its similarity to other
   words can still be calculated on the basis of spelling, but not
   transcription (as PCT has no way of inferring the transcription from
   the spelling).
3. **Frequency type**: If Khorsi similarity is to be calculated, the frequencies
   of the symbols is relevant, and so will be looked up in the currently
   loaded corpus. Either type frequency or token frequency can be used for
   the calculation. This option will not be available for either edit
   distance algorithm, because frequency isn’t taken into account in
   either one.
4. **Minimum / Maximum similarity**: If one is calculating the similarity of
   one word to all others in the corpus, an arbitrary minimum and maximum
   can be set to filter out words that are particularly close or distant.
   For example, one could require that only words with an edit distance
   of both at least and at most 1 are returned, to get the members of
   the standard neighbourhood of a particular lexical item. (Recall
   that the Khorsi calculation is a measure of similarity, while edit
   distance and phonological edit distance are measures of difference.
   Thus, a minimum similarity value is analogous to a maximum distance
   value. PCT will automatically interpret “minimum” and “maximum”
   relative to the string-similarity algorithm chosen.

Here’s an example for calculating the Khorsi similarity of the pair
*mata* (which occurs in the corpus) and *mitoo* [mitu] (which does not),
in the sample corpus, using token frequencies and comparing transcriptions:

.. image:: _static/stringsimilaritydialog.png
   :width: 90%
   :align: center

5. Results: Once all options have been selected, click “Calculate string
   similarity.” If this is not the first calculation, and you want to
   add the results to a pre-existing results table, select the choice
   that says “add to current results table.” Otherwise, select “start
   new results table.” A dialogue box will open, showing a table of the
   results, including word 1, word 2, the result (i.e., the similarity
   score for Khorsi or distance score for either of the edit algorithms),
   whether type or token frequency was used (if the Khorsi method is
   selected; otherwise, N/A), and which algorithm was used. Note that
   the entries in the table will be written in spelling regardless of
   whether spelling or transcriptions were used. This file can be saved
   to a desired location by selecting “Save to file” at the bottom of
   the table.

Here’s an example result file for the above selection:

.. image:: _static/stringsimilarityresults.png
   :width: 90%
   :align: center

To return to the function dialogue box with your most recently used
selections, click on “Reopen function dialog.” Otherwise, the results
table can be closed and you will be returned to your corpus view.

.. _neighborhood_density_gui:

Implementing the neighbourhood density function in the GUI
----------------------------------------------------------

To start the analysis, click on “Analysis” / “Calculate neighbourhood
density...” in the main menu, and then follow these steps:

1. **String similarity algorithm**: The first step is to choose which of the
   three methods of string similarity is to be used to calculate
   neighbourhood density. Note that the standard way of calculating
   density is using standard Levenstein edit distance. We include the
   other two algorithms here as options primarily for the purpose of
   allowing users to explore whether they might be useful measures; we
   make no claims that either phonological edit distance or the Khorsi
   algorithm might be better than edit distance for any reason.

   a. **Minimal pair counts / Substitution neighbours**: It is also possible to
      calculate neighbourhood density by using a variation of edit distance
      that allows for “substitutions only” (not deletions or insertions).
      This is particularly useful if, for example, you wish to know the
      number of or identity of all minimal pairs for a given word in the
      corpus, as minimal pairs are generally assumed to be substitution
      neighbours with an edit distance of 1. (Note that the substitution
      neighbours algorithm automatically assumes a threshold of 1; multiple
      substitutions are not allowed.)

2. **Query type**: Neighbourhood density can be calculated for one of four
   types of inputs:

   a. **One word in the corpus**: The neighbourhood density of a single word
      can be calculated by entering that word’s orthographic representation
      in the query box.
   b. **One word not in the corpus**: (Note that this will NOT add the word
      itself to the corpus, and will not affect any subsequent calculations.
      To globally add a word to the corpus itself, please see the
      instructions in §4.6.4.) Select “Calculate for a word/nonword
      in the corpus,” then choose “Create word/nonword” to enter the
      new word and do the following:

      i. **Spelling**: Enter the spelling for your new word / nonword using
         the regular input keyboard on your computer.
      ii. **Transcription**: To add in the phonetic transcription of the new
          word, it is best to use the provided inventory. While it is
          possible to type directly in to the transcription box, using
          the provided inventory will ensure that all characters are
          understood by PCT to correspond to existing characters in the
          corpus (with their concomitant featural interpretation). Click
          on “Show inventory” and then choose to show “Consonants,”
          “Vowels,” and/or other. (If there is no featural interpretation
          of your inventory, you will simply see a list of all the
          available segments, but they will not be classifed by major
          category.) Clicking on the individual segments will add them
          to the transcription. The selections will remain even when the
          sub-inventories are hidden; we allow for showing / hiding the
          inventories to ensure that all relevant buttons on the dialogue
          box are available, even on small computer screens. Note that you
          do NOT need to include word boundaries at the beginning and end
          of the word, even when the boundary symbol is included as a member
          of the inventory; these will be assumed automatically by PCT.
      iii. **Frequency and other columns**: These can be left at the default.
           Note that entering values will NOT affect the calculation; there
           is no particular need to enter anything here (it is an artifact
           of using the same dialogue box here as in the “Add Word” function
           described in §4.6.4).
      iv. **Create word**: To finish and return to the “String similarity”
          dialogue box, click on “Create word.”

   c. **List of words**: If there is a specific list of words for which density
      is to be calculated (e.g., the stimuli list for an experiment), that
      list can be saved as a .txt file with one word per line and uploaded
      into PCT for analysis. Note that in this case, if the words **are** in
      the corpus, either transcription- or spelling-based neighbourhood
      density can be calculated; either way, the words on the list should be
      written in standard orthography (their transcriptions will be looked
      up in the corpus if needed). If the words are **not** in the corpus, then
      only spelling-based neighbourhood density can currently be calculated;
      again, the words should be written in orthographically.
   d. **Whole corpus**: Alternatively, the neighbourhood density for every word
      in the corpus can be calculated. This is useful, for example, if one
      wishes to find words that match a particular neighbourhood density.
      The density of each word will be added to the corpus itself, as a
      separate column; in the “query” box, simply enter the name of that
      column (the default is “Neighborhood Density”).
3. **Tier**: Neighbourhood density can be calculated from most of the available
   tiers in a corpus (e.g., spelling, transcription, or tiers that
   represent subsets of entries, such as a vowel or consonant tier).
   (If neighbourhood density is being calculated with phonological edit
   distance as the similarity metric, spelling cannot be used.) Standard
   neighbourhood density is calculated using edit distance on transcriptions.
4. **Type vs. token frequency**: If the Khorsi algorithm is selected as the
   string similarity metric, similarity can be calculated using either
   type or token frequency, as described in §5.5.2.3.
5. **Distance / Similarity Threshold**: A specific threshold must be set to
   determine what counts as a “neighbour.” If either of the edit distance
   metrics is selected, this should be the maximal distance that is
   allowed – in standard calculations of neighbourhood density, this
   would be 1, signifying a maximum 1-phone change from the starting
   word. If the Khorsi algorithm is selected, this should be the
   minimum similarity score that is required. Because this is not the
   standard way of calculating neighbourhood density, we have no
   recommendations for what value(s) might be good defaults here;
   instead, we recommend experimenting with the string similarity
   algorithm to determine what kinds of values are common for words
   that seem to count as neighbours, and working backward from that.
6. **Output file**: If this option is left blank, PCT will simply return
   the actual neighbourhood density for each word that is calculated
   (i.e., the number of neighbours of each word). If a file is chosen,
   then the number will still be returned, but additionally, a file
   will be created that lists all of the actual neighbours for each word.
7. **Results**: Once all options have been selected, click “Calculate
   neighborhood density.” If this is not the first calculation, and
   you want to add the results to a pre-existing results table, select
   the choice that says “add to current results table.” Otherwise,
   select “start new results table.” A dialogue box will open, showing
   a table of the results, including the word, its neighbourhood density,
   the string type from which neighbourhood density was calculated,
   whether type or token frequency was used (if applicable), the string
   similarity algorithm that was used, and the threshold value. If the
   neighbourhood density for all words in the corpus is being calculated,
   simply click on the “start new results table” option, and you will be
   returned to your corpus, where a new column has been added automatically.
8. **Saving results**: The results tables can each be saved to tab-delimited
   .txt files by selecting “Save to file” at the bottom of the window.
   Any output files containing actual lists of neighbours are already
   saved as .txt files in the location specified (see step 6). If all
   neighbourhood densities are calculated for a corpus, the corpus itself
   can be saved by going to “File” / “Export corpus as text file,” from
   where it can be reloaded into PCT for use in future sessions with the
   neighbourhood densities included.

Here’s an example of neighbourhood density being calculated on
transcriptions for the entire example corpus, using edit distance
with a threshold of 1:

.. image:: _static/neighdendialog.png
   :width: 90%
   :align: center

The corpus with all words’ densities added:

.. image:: _static/neighdencolumn.png
   :width: 90%
   :align: center

An example of calculating all the neighbours for a given word in the
IPHOD corpus, and saving the resulting list of neighbours to an output file:

.. image:: _static/neighdendialogoutput.png
   :width: 90%
   :align: center

The on-screen results table, which can be saved to a file itself:

.. image:: _static/neighdenresults.png
   :width: 90%
   :align: center

And the saved output file listing all 45 of the neighbours of *cat* in the IPHOD corpus:

.. image:: _static/neighdenoutput.png
   :width: 90%
   :align: center

An example .txt file containing one word per line, that can be uploaded
into PCT so that the neighbourhood density of each word is calculated:

.. image:: _static/neighdeninput.png
   :width: 90%
   :align: center

The resulting table of neighbourhood densities for each word on the list
(in the IPHOD corpus, with standard edit distance and a threshold of 1):

.. image:: _static/neighdeninputresults.png
   :width: 90%
   :align: center

To return to the function dialogue box with your most recently used
selections after any results table has been created, click on “Reopen
function dialog.” Otherwise, the results table can be closed and you
will be returned to your corpus view.

.._neighborhood_density_gui:

Implementing the neighbourhood density function on the command line
-------------------------------------------------------------------

In order to perform this analysis on the command line, you must enter a
command in the following format into your Terminal::

   pct_neighdens CORPUSFILE ARG2

...where CORPUSFILE is the name of your *.corpus file and ARG2 is either
the word whose neighborhood density you wish to calculate or the name
of your word list file (if calculating the neighborhood density of each
word). The word list file must contain one word (specified using either
spelling or transcription) on each line. You may also use command line
options to change various parameters of your neighborhood density
calculations. Descriptions of these arguments can be viewed by running
``pct_neighdens –h`` or ``pct_neighdens –help``. The help text from this
command is copied below, augmented with specifications of default values:

Positional arguments:


.. cmdoption:: corpus_file_name

   Name of corpus file

.. cmdoption:: query

   Name of word to query, or name of file including a list of words

Optional arguments:

.. cmdoption:: -h
               --help

   Show this help message and exit

.. cmdoption:: -a ALGORITHM
               --algorithm ALGORITHM

   The algorithm used to determine distance

.. cmdoption:: -d MAX_DISTANCE
               --max_distance MAX_DISTANCE

   Maximum edit distance from the queried word to consider a word a neighbor.

.. cmdoption:: -s SEQUENCE_TYPE
               --sequence_type SEQUENCE_TYPE

   The name of the tier on which to calculate distance

.. cmdoption:: -w COUNT_WHAT
               --count_what COUNT_WHAT

   If 'type', count neighbors in terms of their type frequency. If
   'token', count neighbors in terms of their token frequency.

.. cmdoption:: -m
               --find_mutation_minpairs

   This flag causes the script not to calculate neighborhood density,
   but rather to find minimal pairs--see documentation.

.. cmdoption:: -o OUTFILE
               --outfile OUTFILE

   Name of output file.


EXAMPLE 1: If your corpus file is example.corpus and you want to
calculate the neighborhood density of the word 'nata' using defaults
for all optional arguments, you would run the following command in your
terminal window::

   pct_neighdens example.corpus nata

EXAMPLE 2: Suppose you want to calculate the neighborhood distance of a
list of words located in the file mywords.txt . Your corpus file is again
example.corpus. You want to use the phonological edit distance metric,
and you wish to count as a neighbor any word with a distance less than
0.75 from the query word. In addition, you want the script to produce an
output file called output.txt .  You would need to run the following command::

   pct_neighdens example.corpus mywords.txt -a phonological_edit_distance -d 0.75 -o output.txt

EXAMPLE 3: You wish to find a list of the minimal pairs of the word 'nata'.
You would need to run the following command::

   pct_neighdens example.corpus nata -m

.. _frequency_alternation:

Frequency of alternation[#]_
============================

.. _about_frequency_alternation:

About the function
------------------

The occurrence of alternations can be used in assessing whether two
phonemes in a language are contrastive or allophonic, with alternations
promoting the analysis of allophony (e.g., [Silverman2006]_, [Johnson2010]_,
[Lu2012]_), though it’s clear that not all alternating sounds are
allophonic (e.g., the [k]~[s] alternation in electric~electricity).

In general, two phonemes are considered to alternate if they occur in
corresponding positions in two related words. For example, [s]/[ʃ]
would be considered an alternation in the words [dəpɹɛs] and [dəpɹɛʃən]
as they occur in corresponding positions and the words are morphologically
related. [Johnson2010]_ make the point that alternations may be
more or less frequent in a language, and imply that this frequency may
affect the influence of the alternations on phonological relations. As far
as we know, however, there is no literature that directly tests this claim
or establishes how frequency of alternation could actually be quantified
(though see discussion in [Hall2014b]_).

.. _method_frequency_alternation:

Method of calculation
---------------------

In PCT, frequency of alternation is the ratio of the number of words
that have an alternation of two phonemes to the total number of words
that contain either phoneme, as in:

:math:`Frequency\ of\ alternation = \frac{Words\ with\ an\ alternation\ of\ s_1\ and\ s_2}
{Words\ with\ s_1\ +\ words\ with\ s_2}`

To determine whether two words have an alternation of the targeted phonemes,
one word must contain phoneme 1, the other must contain phoneme 2, and some
threshold of “relatedness” must be met. In an ideal world, this would be
determined by a combination of orthographic, phonological, and semantic
similarity; see discussion in Hall et al. (in submission). Within PCT,
however, a much more basic relatedness criterion is used: string similarity.
This is indeed what [Khorsi2012]_ proposes as a measure of morphological
relatedness, and though we caution that this is not in particularly close
alignment with the standard linguistic interpretation of morphological
relatedness, it is a useful stand-in for establishing an objective
criterion. If both conditions are met, the two words are considered to
have an alternation and are added to the pool of “*words with an
alternation of s1 and s2*.”

It is also possible to require a third condition, namely, that the
location of phoneme 1 and phoneme 2 be roughly phonologically aligned
across the two words (e.g., preceded by the same material). Requiring
phonological alignment will make PCT more conservative in terms of what
it considers to “count” as alternations. However, the phonological
alignment algorithm is based on [Allen2014]_ and currently
only works with English-type morphology, i.e., a heavy reliance on
prefixes and suffixes rather than any other kinds of morphological
alternations. Thus, it should not be used with non-affixing languages.

Again, we emphasize that we do *not* believe this to currently be a
particularly accurate reflection of morphological relatedness, so the
resulting calculation of frequency of alternation should be treated with
**extreme** caution. We include it primarily because it is a straightforward
function of string similarity that has been claimed to be relevant, not
because the current instantiation is thought to be particularly valid.

.. _frequency_of_alternation_gui:

Implementing the frequency of alternation function in the GUI
-------------------------------------------------------------

To start the analysis, click on “Analysis” / “Calculate frequency of
alternation...” in the main menu, and then follow these steps:

1. **Segments**: The first step is to choose which two sounds you wish to
   check alternations for. Click on “Add pair of sounds”; PCT will
   automatically populate a menu of all sounds in the corpus, so all
   that needs to be done is the selection of the targeted two sounds.
   Multiple pairs of sounds can be added by selecting “Add and create
   another” instead “Add” in the selection window.
2. **String similarity algorithm**: Next, choose which distance / similarity
   metric to use. For more information on the similarity metrics, please
   refer to the string similarity section of the manual, as each
   algorithm (Khorsi, edit distance, and phonological edit distance)
   is explained in detail therein.
3. **Tier**: The tier from which string similarity is to be calculated can
   be selected. Generally, one is likely to care most about full
   transcriptions, but other tiers (e.g., a vowel tier) can also be
   selected; in this case, all information removed from the tier is
   ignored.
4. **Frequency Type**: Next, select which frequency type to use for your
   similarity metric, either type or token frequency. This parameter is
   only available if using the Khorsi similarity metric, which relies on
   counting the frequency of occurrence of the sounds in the currently
   selected corpus; neither edit distance metric involves frequency.
5. **Minimal pairs**: Then, select whether you wish to include alternations
   that occur in minimal pairs. If, for example, the goal is to populate
   a list containing all instances where two segments potentially
   alternate, select “include minimal pairs.” Alternatively, if one
   wishes to discard known alternations that are contrastive, select
   “ignore minimal pairs.” (E.g., “bat” and “pat” look like a potential
   “alternation” of [b] and [p] to PCT, because they are extremely similar
   except for the sounds in question, which are also phonologically aligned.)
6. **Threshold values**: If the Khorsi algorithm is selected, enter the minimum
   similarity value required for two words to count as being related.
   Currently the default is -15; this is an arbitrary (and relatively
   low / non-conservative) value. We recommend reading [Khorsi2012]_ and
   examining the range of values obtained using the string similarity
   algorithm before selecting an actual value here. Alternatively, if
   one of the edit distance algorithms is selected, you should instead
   enter a maximum distance value that is allowed for two words to count
   as being related. Again, there is a default (6) that is relatively
   high and non-conservative; an understanding of edit distances is crucial
   for applying this threshold in a meaningful way.
7. **Phonological alignment**: Choose whether you want to require the phones
   to be phonologically aligned or not, as per the above explanation.
8. **Corpus size**: Calculating the full set of possible alternations for a
   pair of sounds may be extremely time-consuming, as all words in the
   corpus must be compared pairwise. To avoid this problem, a subset of
   the corpus can be selected (in which case, we recommend running the
   calculation several times so as to achieve different random subsets
   for comparison). To do so, enter either (1) the number of words you’d
   like PCT to extract from the corpus as a subset (e.g., 5000) or (2) a
   decimal, which will result in that percentage of the corpus being used
   as a subset (e.g., 0.05 for 5% of the corpus).
9. **Output alternations**: You can choose whether you want PCT to output a
   list of all the words it considers to be “alternations.” This is useful
   for determining how accurate the calculation is. If you do want the
   list to be created, enter a file path or select it using the system
   dialogue box that opens when you click on “Select file location.” If
   you do not want such a list, leave this option blank.

An example of selecting the parameters for frequency of alternation,
using the sample corpus:

.. image:: _static/freqaltdialog.png
   :width: 90%
   :align: center

10. **Results**: Once all options have been selected, click “Calculate
    frequency of alternation.” If this is not the first calculation,
    and you want to add the results to a pre-existing results table,
    select the choice that says “add to current results table.” Otherwise,
    select “start new results table.” A dialogue box will open, showing
    a table of the results, including sound 1, sound 2, the total number
    of words with either sound, and total number of words with an
    alternation, the frequency of alternation and information about
    the specified similarity / distance metric and selected threshold
    values. To save these results to a .txt file, click on “Save to file”
    at the bottom of the table.

An example of the results table:

.. image:: _static/freqaltresults.png
   :width: 90%
   :align: center

To return to the function dialogue box with your most recently used
selections, click on “Reopen function dialog.” Otherwise, the results
table can be closed and you will be returned to your corpus view.


Mutual Information[#]_
======================

.. _about_mi:

About the function
------------------

Mutual information is a measure of how much dependency there is between
two random variables, X and Y. That is, there is a certain amount of
information gained by learning that X is present and *also* a certain amount
of information gained by learning that Y is present. But knowing that X
is present might also tell you something about the likelihood of Y being
present, and vice versa. If X and Y always co-occur, then knowing that
one is present already tells you that the other must also be present. On
the other hand, if X and Y are entirely independent, then knowing that
one is present tells you nothing about the likelihood that the other is
present.

In phonology, there are two primary ways in which one could interpret X
and Y as random variables. In one version, X and Y are equivalent random
variables, each varying over “possible speech sounds in some unit” (where
the unit could be any level of representation, e.g. a word or even a
non-meaningful unit such as a bigram). In this case, one is measuring
how much the presence of X anywhere in the defined unit affects the
presence of Y in that same unit, regardless of the order in which X and
Y occur, such that the mutual information of (X; Y) is the same as the
mutual information of (Y; X), and furthermore, the pointwise mutual
information of any individual value of each variable (X = *a*; Y = *b*) is
the same as the pointwise mutual information of (X = *b*; Y = *a*). Although
his is perhaps the most intuitive version of mutual information, given
that it does give a symmetric measure for “how much information does the
presence of a provide about the presence of *b*,” we are not currently
aware of any work that has attempted to use this interpretation of MI
for phonological purposes.

The other interpretation of MI assumes that X and Y are different random
variables, with X being “possible speech sounds occurring as the first
member of a bigram” and Y being “possible speech sounds occurring as the
second member of a bigram.” This gives a directional interpretation to
mutual information, such that, while the mutual information of (X; Y) is
the same as the mutual information of (Y; X), the pointwise mutual
information of (X = *a*; Y = *b*) is NOT the same as the pointwise mutual
information of (X = *b*; Y = *a*), because the possible values for X and Y
are different. (It is still, trivially, the case that the pointwise mutual
information of (X = *a*; Y = *b*) and (Y = *b*; X = *a*) are equal.)

This latter version of mutual information has primarily been used as a
measure of co-occurrence restrictions (harmony, phonotactics, etc.). For
example, [Goldsmith2012]_ use pointwise mutual information as a
way of examining Finnish vowel harmony; see also discussion in
[Goldsmith2002]_. Mutual information has also been used instead of
transitional probability as a way of finding boundaries between words
in running speech, with the idea that bigrams that cross word boundaries
will have, on average, lower values of mutual information than bigrams
that are within words (see [Brent1999]_, [Rytting2004]_). Note, however, that
in order for this latter use of mutual information to be useful, one must
be using a corpus based on running text rather than a corpus that is
simply a list of individual words and their token frequencies.

.. _mi_method:

Method of calculation
---------------------

Both of the interpretations of mutual information described above are
implemented in PCT. We refer to the first one, in which X and Y are
interpreted as equal random variables, varying over “possible speech
sounds in a unit,” as word-internal co-occurrence pointwise mutual
information (pMI), because we specifically use the word as the unit in
which to measure pMI. We refer to the second one, in which X and Y are
different random variables, over either the first or second members of
bigrams, as ordered pair pMI.

The general formula for pointwise mutual information is given below;
it is the binary logarithm of the joint probability of X = *a* and Y = *b*,
divided by the product of the individual probabilities that X = *a* and Y = *b*.

:math:`pMI = log_2 (\frac{p(X=a \& Y = b)}{p(X=a)*p(Y=b)})`

**Word-internal co-occurrence pMI**: In this version, the joint probability
that X = *a* and Y = *b* is equal to the probability that some unit
(here, a word) contains both a and b (in any order). Therefore, the
pointwise mutual information of the sounds *a* and *b* is equal to the binary
logarithm of the probability of some word containing both *a* and *b*, divided
by the product of the individual probabilities of a word containing *a* and
a word containing *b*.

Pointwise mutual information for individual segments:

:math:`pMI_{word-internal} = log_2 (\frac{p(a \in W \& b \in W)}
{p(a \in W)*p(b \in W)})`

Ordered pair pMI: In this version, the joint probability that X = *a* and
Y = *b* is equal to the probability of occurrence of the sequence ab.
Therefore, the pointwise mutual information of a bigram (e.g., *ab*) is
equal to the binary logarithm of the probability of the bigram divided
by the product of the individual segment probabilities, as shown in the
formula below.

Pointwise mutual information for bigrams:

:math:`pMI_{ordered-pair} = log_2 (\frac{p(ab)}
{p(a)*p(b)})`

For example, given the bigram [a, b], its pointwise mutual information
is the binary logarithm of the probability of the sequence [ab] in the
corpus divided by a quantity equal to the probability of [a] times the
probability of [b]. Bigram probabilities are calculated by dividing counts
by the total number of bigrams, and unigram probabilities are calculated
equivalently.

Note that pMI can also be expressed in terms of the information content
of each of the members of the bigram. Information is measured as the
negative log of the probability of a unit :math:`(I(a) = -log_2*p(a))`, so the
pMI of a bigram *ab* is also equal to :math:`I(a) + I(b) – I(ab)`.

Note that in PCT, calculations are not rounded until the final stage,
whereas in [Goldsmith2012]_, rounding was done at some
intermediate stages as well, which may result in slightly different
final pMI values being calculated.

.. _mi_gui:

Implementing the mutual information function in the GUI
-------------------------------------------------------

To start the analysis, click on “Analysis” / “Calculate mutual information...”
in the main menu, and then follow these steps:

1. **Bigram**: Click on the “Add bigram” button in the “Mutual Information”
   dialogue box. A new window will open with a phonetic inventory of all
   the segments that occur in your corpus. Select the bigram by clicking
   on one segment from the “left-hand side” and one segment from the
   “right-hand side.” To add more than one bigram, click “Add and create
   another” to be automatically returned to the selection window. Once
   the last bigram has been selected, simply click “Add” to return to
   the Mutual Information dialogue box. All the selected bigrams will
   appear in a list. To remove one, click on it and select “Remove
   selected bigram.”
2. **Tier**: Mutual information can be calculated on any available tier.
   The default is transcription. If a vowel tier has been created,
   for example, one could calculate the mutual information between
   vowels on that tier, ignoring intervening consonants, to examine
   harmony effects.
3. **Domain**: Choosing “set domain to word” will change the calculation so
   that the calculation is for word-internal co-occurrence pMI. In this
   case, the order and adjacency  of the bigram does not matter; it is
   simply treated as a pair of segments that could occur anywhere in a word.
4. **Word boundary count**: A standard word object in PCT contains word
   boundaries on both sides of it (e.g., [#kæt#] ‘cat’). If words were
   concatenated in real running speech, however, one would expect to see
   only one word boundary between each pair of words (e.g., [#mai#kæt#]
   ‘my cat’ instead of [#mai##kæt#]). To reproduce this effect and assume
   that word boundaries occur only once between words (as is assumed in
   [Goldsmith2012]_, choose “halve word boundary count.” Note that this
   technically divides the number of boundaries in half and then adds one,
   to compensate for the extra “final” boundary at the end of an utterance.
   (It will make a difference only for calculations that include a boundary
   as one member of the pair.)
5. **Results**: Once all options have been selected, click “Calculate mutual
   information.” If this is not the first calculation, and you want to add
   the results to a pre-existing results table, select the choice that
   says “add to current results table.” Otherwise, select “start new
   results table.” A dialogue box will open, showing a table of the
   results, including sound 1, sound 2, the tier used, and the mutual
   information value. To save these results to a .txt file, click on
   “Save to file” at the bottom of the table.

The following image shows the inventory window used for selecting bigrams
in the sample corpus:

.. image:: _static/bigram.png
   :width: 90%
   :align: center

The selected bigrams appear in the list in the “Mutual Information” dialogue box:

.. image:: _static/midialog.png
   :width: 90%
   :align: center

The resulting mutual information results table:

.. image:: _static/miresults.png
   :width: 90%
   :align: center

To return to the function dialogue box with your most recently used selections,
click on “Reopen function dialog.” Otherwise, the results table can be
closed and you will be returned to your corpus view.

.. _mi_cli:

Implementing the mutual information function on the command line
----------------------------------------------------------------

In order to perform this analysis on the command line, you must enter a
command in the following format into your Terminal::

   pct_mutualinfo CORPUSFILE ARG2

...where CORPUSFILE is the name of your \*.corpus file and ARG2 is the
bigram whose mutual information you wish to calculate. The bigram must
be in the format 's1,s2' where s1 and s2 are the first and second
segments in the bigram. You may also use command line options to
change the sequency type to use for your calculations, or to specify
an output file name. Descriptions of these arguments can be viewed by
running ``pct_mutualinfo -h`` or ``pct_mutualinfo --help``. The help text
from this command is copied below, augmented with specifications of
default values:

Positional arguments:

.. cmdoption:: corpus_file_name

   Name of corpus file

.. cmdoption:: query

   Bigram, as str separated by comma

Optional arguments:

.. cmdoption:: -h
               --help

   Show help message and exit

.. cmdoption:: -s SEQUENCE_TYPE
               --sequence_type SEQUENCE_TYPE

   The attribute of Words to calculate FL over. Normally, this will be
   the transcription, but it can also be the spelling or a user-specified tier.

.. cmdoption:: -o OUTFILE
               --outfile OUTFILE

   Name of output file

EXAMPLE 1: If your corpus file is example.corpus and you want to calculate
the mutual information of the bigram 'si' using defaults for all optional
arguments, you would run the following command in your terminal window::

   pct_mutualinfo example.corpus s,i

EXAMPLE 2: Suppose you want to calculate the mutual information of the
bigram 'si' on the spelling tier. In addition, you want the script to
produce an output file called output.txt. You would need to run the
following command::

   pct_mutualinfo example.corpus s,i -s spelling -o output.txt

.. _acoustic_similarity:


Acoustic Similarity
===================

.. _about_acoustic_similarity:

About the function
------------------

Acoustic similarity analyses quantify the degree to which waveforms of
linguistic objects (such as sounds or words) are similar to each other.
The acoustic similarity measures provided here have primarily been used
in the study of phonetic convergence between interacting speakers;
convergence is measured as a function of increasing similarity. These
measures are also commonly used in automatic speech and voice recognition
systems, where incoming speech is compared to stored representations.
Phonologically, acoustic similarity also has a number of applications.
For example, it has been claimed that sounds that are acoustically distant
from each other cannot be allophonically related, even if they are in
complementary distribution (e.g. [Pike1947]_; [Janda1999]_).

Acoustic similarity alogorithms work on an aggregate scale, quantifying,
on average, how similar one group of waveforms is to another.
Representations have traditionally been in terms of mel-frequency cepstrum
coefficents (MFCCs; [Delvaux2007]_; [Mielke2012]_), which is
used widely for automatic speech recognition, but one recent introduction
is multiple band amplitude envelopes [Lewandowski2012]_. Both MFCCs and
amplitude envelopes will be described in more detail in the following
sections, and both are available as part of PCT.

The second dimension to consider is the algorithm used to match
representations. The most common one is dynamic time warping (DTW),
which uses dynamic programming to calculate the optimal path through a
distance matrix [Sakoe1971]_, and gives the best alignment of
two time series. Because one frame in one series can align to multiple
frames in another series without a significant cost, DTW provides a
distance independent of time. The other algorithm that is used is
cross-correlation (see discussion in [Lewandowski2012]_, which aligns
two time series at variable lags. Taking the max value of the alignment
gives a similarity value for the two time series, with higher values
corresponding to higher similarity.

.. _method_acoustic_similarity:

Method of calculation
---------------------

Preprocessing
`````````````

Prior to conversion to MFCCs or amplitude envelopes, the waveform is
pre-emphasized to give a flatter spectrum and correct for the higher
drop off in amplitude of higher frequencies due to distance from the mouth.

MFCCs
`````

The calculation of MFCCs in PCT’s function follows the Rastamat
[Ellis2005]_'s implementation of HTK-style MFCCs [HTK]_ in [Matlab]_.
Generating MFCCs involves windowing the acoustic waveform and transforming
the windowed signal to the linear frequency domain through a Fourier
transform. Following that, a filterbank of triangular filters is
constructed in the mel domain, which gives greater resolution to
lower frequencies than higher frequencies. Once the filterbank is
applied to the spectrum from the Fourier transform, the spectrum is
represented as the log of the power in each of the mel filters. Using
this mel spectrum, the mel frequency cepstrum is computed by performing
a discrete cosine transform. This transform returns orthogonal
coefficients describing the shape of the spectrum, with the first
coefficent as the average value, the second as the slope of the spectrum,
the third as the curvature, and so on, with each coefficient representing
higher order deviations. The first coefficent is discarded, and the next
X coefficents are taken, where X is the number of coefficents specified
when calling the function. The number of coefficents must be one less
than the number of filters, as the number of coefficents returned by the
discrete cosine transform is equal to the number of filters in the mel
filterbank.

Amplitude envelopes
```````````````````

The calculation of amplitude envelopes follows the Matlab implementation
found in [Lewandowski2012]_. First, the signal is filtered into X number
of logarithmically spaced bands, where X is specified in the function call,
using 4th order Butterworth filters. For each band, the amplitude envelope
is calculated by converting the signal to its analytic signal through a
Hilbert transform. Each envelope is downsampled to 120 Hz.

Dynamic time warping (DTW)
``````````````````````````

PCT implements a standard DTW algorithm [SakoeChiba, 1971]_
and gives similar results as the dtw package [Giorgino2009)]_ in [R].
Given two representations, a 2D matrix is constructed where the dimensions
are equal to the number of frames in each representation. The initial
values for each cell of the matrix is the Euclidean distance between the
two feature vectors of those frames. The cells are updated so that they
equal the local distance plus the minimum distance of the possible previous
cells. At the end, the final cell contains the summed distance of the
best path through the matrix, and this is the minimum distance between
two representations.

Cross-correlation
`````````````````

Cross-correlation seeks to align two time series based on corresponding
peaks and valleys. From each representation a time series is extracted
for each frame's feature and this time series is cross-correlated with
the respective time series in the other representation. For instance,
the time series for an amplitude envelope’s representation corresponds
to each frequency band, and each frequency band of the first representation
is cross-correlated with each respective frequency band of the second
representation. The time series are normalized so that they sum to 1,
and so matching signals receive a cross-correlation value of 1 and
completely opposite signals receive a cross-correlation value of 0.
The overall distance between two representations is the inverse of the
average cross-correlation values for each band.

Similarity across directories
`````````````````````````````

The algorithm for assessing the similarity of two directories
(corresponding to segments) averages the similarity of each .wav
file in the first directory to each .wav file in the second directory.

.. _acoustic_similarity_gui:

Implementing the acoustic similarity function in the GUI
--------------------------------------------------------

To start the analysis, click on the “Calculate acoustic similarity...” in
the Analysis menu and provide the following parameters. Note that unlike
the other functions, acoustic similarity is not tied directly to any corpus
that is loaded into PCT; sound files are accessed directly through
directories on your computer.

1. **Comparison type**: There are three kinds of comparisons that can be done
   in PCT: single-directory, two-directory, or pairwise.

   a. **Single directory**: If a single directory is selected (using the
      “Choose directory...” dialogue box), two types of results will be
      returned: (1) each of the pairwise comparisons and (2) an average
      of all these comparisons (i.e., a single value).
   b. **Two directories**: Choose two directories, each corresponding to a
      set of sounds to be compared. For example, if one were interested
      in the similarity of [s] and [ʃ] in Hungarian, one directory would
      contain .wav files of individual [s] tokens, and the other directory
      would contain .wav files of individual [ʃ] tokens. Every sound file
      in the first directory will be compared to every sound file in the
      second directory, and the acoustic similarity measures that are
      returned will again be (1) all the pairwise comparisons and (2)
      an average of all these comparisons (i.e., a single value).
   c. **Pairwise**: One can also use a tab-delimied.txt file that lists all
      of the pairwise comparisons of individual sound files by listing
      their full path names. As with a single directory, each pairwise
      comparison will be returned separately.

2. **Representation**: Select whether the sound files should be represented
   as MFCCs or amplitude envelopes (described in more detail above).
3. **Distance algorithm**: Select whether comparison of sound files should
   be done using dynamic time warping or cross-correlation (described in
   more detail above).
4. **Frequency limits**: Select a minimum frequency and a maximum frequency
   to use when generating representations. The human voice typically
   doesn't go below 80 Hz, so that is the default cut off to avoid
   low-frequency noise. The maximum frequency has a hard bound of the
   Nyquist frequency of the sound files, that is, half their sampling rate.
   The lowest sampling rate that is typically used for speech is 16,000 Hz,
   so a cutoff near the Nyquist (8,000 Hz) is used as the default. The
   range of human hearing is 20 Hz to 20 kHz, but most energy in speech
   tends to fall off after 10 kHz.
5. **Frequency resolution**: Select the number of filters to be used to divide
   up the frequency range specified above. The default for MFCCs is for 26
   filters to be constructed, and for amplitude envelopes, 8 filters.
6. **Number of coefficients (MFCC only)**: Select the number of coefficients
   to be used in MFCC representations. The default is 12 coefficients,
   as that is standard in the field. If the number of coefficients is
   more than the number of filters minus one, the number of coefficients
   will be set to the number of filters minus one.
7. **Output**: Select whether to return results as similarity (inverse
   distance) or to us ethe default, distance (inverse similarity).
   Dynamic time warping natively returns a distance measure which gets
   inverted to similarity and cross-correlation natively returns a
   similarity value which gets inverted to distance.
8. **Multiprocessing**: As the generation and comparison of representations
   can be time-intensive, using multiprocessing on parts that can be
   run in parallel can speed the process up overall. In order to make
   this option available, the python-acoustic-similarity module must be
   installed; multiprocessing itself can be enabled by going to
   “Options” / “Preferences” / “Processing” (see also §3.9.1).

Here’s an example of the parameter-selection box:

.. image:: _static/acousticsimdialog.png
   :width: 90%
   :align: center

9. **Calculating and saving results**: The first time an analysis is run,
   the option to “Calculate acoustic similarity (start new results
   table)” should be selected. This will output the results to a
   pop-up window that lists the directories, the representation choice,
   the matching function, the minimum and maximum frequencies, the
   number of filters, the number of coefficients, the raw result, and
   whether the result is similarity (1) or distance (0). Subsequent
   analyses can either be added to the current table (as long as it
   hasn’t been closed between analyses) or put into a new table. Once
   a table has been created, click on “Save to file” at the bottom of
   the table window in order to open a system dialogue box and choose
   a directory; the table will be saved as a tab-delimited .txt file.

Here’s an example of the results file:

.. image:: _static/asresults.png
   :width: 90%
   :align: center

To return to the function dialogue box with your most recently used
selections, click on “Reopen function dialog.” Otherwise, the results
table can be closed and you will be returned to your corpus view.

.. [#] As emphasized throughout this section, the algorithm implemented
   in PCT is an extremely inaccurate way of calculating frequency of
   alternation, and should be used only with a full understanding of
   its severe limitations.
.. [#] The algorithm in PCT calculates what is sometimes referred to
   as the “pointwise” mutual information of a pair of units X and Y,
   in contrast to “mutual information,” which would be the expected
   average value of the pointwise mutual information of all possible
   values of X and Y. We simplify to use “mutual information” throughout.
