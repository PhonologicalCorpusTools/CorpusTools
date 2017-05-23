.. _informativity:

*************
Informativity
*************

.. _about_informativity:

About the function
------------------

Informativity is one of three primary information theoretic measures that has been demonstrated to affect how speech is
realized. Informativity is “the weighted average of the negative log predictability of all the occurrences of a segment”
[CohenPriva2015]_. Informally, it can be thought of as the "usual" (average) amount of information (surprisal) that a particular segment carries within a corpus. In other words, rather than being a measure of how probable a segment is in a particular context, it is a measure of how predictable that segment is when it occurs in any context. Thus, it can be used to explain the fact that some segments may be locally probable in some context, and yet exhibit properties generally expected of unpredictable segments: such segments are those whose general predictability (informativity) is low, even if their local predictability is high ([CohenPriva2015]_: 248).

It is formally defined with the following formula:

:math:`-sum[P(context|segment) * log2P(segment|context)]`

Within this formula, :math:`-log2P(segment|context)` is the negative logged probability of the segment in the given context, i.e., its information content. This transformation from probability to information simply captures the idea that more probable elements contain less information and are less surprising. By multiplying each of these information content values by :math:`P(context|segment)`, i.e., the probability of the context given the segment, we weight the local information content by the frequency of that context; by then summing these products over all possible contexts for a segment, we get the total informativity score for that segment.

While other information theoretic measures such as frequency and predictability can be used to describe a wide variety
of deletion and duration effects, Cohen Priva argues that informativity provides more nuanced and accurate predictions,
and offers empirical evidence from English, as well as other languages [CohenPrivaInPress]_.

One of the primary decisions in calculating informativity, is selecting the type of context to be used.
[CohenPriva2015]_ discusses four options used in the literature - uniphone, biphone, triphone, and all preceding
segments in the word. Within PCT, "all preceding" is currently the only supported option.

Consider a toy example, taken from [CohenPriva2015]_, §2.3, in which the following corpus is assumed
(note that, generally speaking, there is no “type frequency” column
in a PCT corpus, as it is assumed that each row in the corpus represents
1 type; it is included here for clarity):

+---------+----------------+-------+
|  Word   | Trans.  | Type | Token | 
|         |         | Freq.| Freq. | 
+=========+=========+======+=======+
|   talk  |  [tɑk]  |    1 |  200  | 
+---------+---------+------+-------+
|  talks  | [tɑks]  |    1 |  100  |
+---------+---------+------+-------+
| talking | [tɑkɪŋ] |    1 |  100  |
+---------+---------+------+-------+
|   walk  |  [wɑk]  |    1 |  150  | 
+---------+---------+------+-------+
|  walks  | [wɑks]  |    1 |  300  |
+---------+---------+------+-------+
| walking | [wɑkɪŋ] |    1 |  150  |
+---------+---------+------+-------+

In this corpus, the segment [s] appears twice, once in 'talks' and once in 'walks.' To calculate the informativity of [s] in this corpus using "all preceding segments" as the context, we do the following:

1. For each context, calculate :math:`log2P(segment|context)` 

   a. For the context in 'talks,' i.e., [tɑk_], there are three words with this context ('talk,' 'talks,' and 'talking'), and their token frequencies are 200, 100, and 100 (respectively). The probability of [s] in this context is the frequency of 'talks' divided by the total frequency of the context, i.e., 100 / (200 + 100 + 100) = 100 / 400 = 0.25. Then, :math:`log2P(0.25)` gives -2. That is, we have (negative) two bits of information in this context (the negation will be inversed at the end of the calculation). [Note: one could certainly imagine doing this calculation using type frequencies, but Cohen Priva presents only token frequencies; we follow his method here.]
   
   b. For the context in 'walks', we can similarly calculate that the probability of [s] in this context is the frequency of 'walks' divided by the total frequency of the context, i.e., 300 / (150 + 300 + 150) = 300 / 600 = 0.5. Then, :math:`log2P(0.5)` gives -1. In other words, we have (negative) one bit of information in this context. It is less surprising to have an [s] after [wɑk] (only 1 bit of information is gained) than it is to have an [s] after [tɑk] (where 2 bits of information were gained).

2. For each context, calculate :math:`P(context|segment)`.

   a. For the context in 'talks', the probability of having this context given an [s] is found by taking the frequency of 'talks' and dividing by the sum of the contexts with [s], i.e., 100 / (100 + 300) = 100 / 400 = 0.25.
   
   b. For the context in 'walks,' we analogously get 300 / (100 + 300) = 300 / 400 = 0.75.
   
   In other words, 25% of the contexts that contain [s] are the [tɑk] contexts (which are more informative) while 75% are the [wɑk] contexts (which are less informative).
   
3. For each context, multiply :math:`log2P(segment|context)` (the information content in the context) by :math:`P(context|segment)` (the relative frequency of this context).

   a. For the context in 'talks' we multiply -2 by 0.25 and get -0.5.
   
   b. For the context in 'walks' we multiply -1 by 0.75 and get -0.75.
   
   In other words, we are weighting the information content of each context by the frequency of the context.

4. We sum the products for each context. Here, -0.5 + -0.75 = -1.25.

5. For ease of comprehension, we take the inverse of the sign. -(-1.25) = 1.25

Thus, the informativity of [s] in this corpus is 1.25 bits. In some (less frequent) contexts, it has an information content of 2 bits, while in other (more frequent) contexts, it has an information content of 1 bit. On average, then, we end up with an average information content (i.e., an informativity) of 1.25 bits.

.. _method_informativity:

Method of calculation
---------------------

.. _method_context:

Defining context
````````````````
The context for a given segment is currently defined as all of the preceding segments within the same word - the
preferred method in [CohenPriva2015]. The context method includes parameters for the index (integer) of the segment and word in question. Index is used instead of segment, as a word may contain more than one of the same segment, and it is important to consider the context for each occurrence. The function returns a tuple of segments comprising the context. Typical users will not interact with context. Future improvements to the informativity function will allow for customizable context.

Informativity
`````````````
The function to get the informativity of one segment is structured such that it calls on other functions within
:math:`informativity.py` to create three dictionaries containing:

1.  The frequency of a segment occurring given a context, with contexts as the key and captured in the dictionary
:math:`s_frs`
2.  The frequency of those contexts, regardless of the segment that occurs after
3.  The conditional probabilities of a segment occurring in a given context, captured in dictionary :math:`c_prs`.

Given this input, the informativity of a given segment is calculated as follows:

:math:`informativity=round(-(sum([(s_frs[c])*log2(c_prs[c]) for c in c_prs]))/sum([(s_frs[s])for s in s_frs]),rounding)`

The following is an example run of the function for a single segment:

.. image:: informativity1.png
   :width: 90%
   :align: center

In addition to getting the informativity for a single segment, :math:`informativity.py` includes a function to calculate
the informativity of all segments in a corpus. This function gets the list of segments from the corpus’ inventory, and
creates a dictionary with the segments as the key, and the output of the get_informativity function as its value.

The following is an example run for getting the informativities for all segments in the inventory:

.. image:: informativity2.png
   :width: 90%
   :align: center

.. _informativity_corpus_file:

Calculating informativity with a .corpus file
---------------------------------------------

1.  **Locate the corpus**: Verify that the lemurian.corpus file is located in the same directory as informativity.py.

2.  **Run informativity.py**: Open a terminal and navigate to the directory where informativity.py is located. Note that
PCT uses Python 3, and run the following:

    :math:`python informativity.py`

The following is an example run of the current test print statements:

.. image:: informativity_559tests.png
   :width: 90%
   :align: center

3.  **Run additional tests**: At your discretion!


**NOTE**: In the future, this portion of the documentation will be modified for calculating informativity in the GUI and
on the command line, to better conform to and integrate with PCT.

.. _functional_load_gui:

Calculating functional load in the GUI
--------------------------------------
Details will be added here upon full integration with PCT.

.. _functional_load_cli:

Implementing the functional load function on the command line
-------------------------------------------------------------
Details will be added here upon full integration with PCT.

.. _informativity_classes_and_functions:

Additional Information
----------------------
Details will be added here upon full integration with PCT.

**********
References
**********

Note that these references will be migrated to the "references.rst" file when fully integrated.

.. [CohenPriva2015] Cohen Priva, Uriel (2015). Informativity affects consonant duration and deletion rates. Laboratory Phonology, 6(2), 243–278.

.. [CohenPrivaInPress] Cohen Priva, Uriel (in press). Informativity and the actuation of lenition. Language. Retrieved from   https://urielcpublic.s3.amazonaws.com/Informativity-and-the-actuation-of-lenition-accepted.pdf
