.. _phonological_search:

*******************
Phonological search
*******************

PCT allows you to do searches for various strings or syllables. They can be defined by segments or features.
The search returns two types of information: the first is called “summary results,” where a general count
of the number of entries that fit the search is described, and the other is “individual results,” where
a list of all the words in the corpus that contain the specified string is presented. There are two modes
in which this “phonological search” can be conducted: “:ref:`segment_mode`” and “:ref:`syllable_mode`.”
“Segment mode” treats words in the corpus as a linear sequence of segments, so it is useful for
searching for a target in a linear context. This is the only search type that was available
in early versions of PCT. “Syllable mode,” on the other hand, allows you to construct syllables for your search,
such that you can search for both syllable components like “onset” and “coda” and also
for characteristics of words that are defined at the syllabic level, such as tone or stress.
Syllable mode requires your corpus to have syllable delimiters. Finally, you can save a search for later use.

To conduct a search, first choose “Corpus” / “Phonological search...”
and do the following:

.. _segment_mode:

Segment mode
============

Segment mode lets you search a target in linear environments.

1. **Search mode**: Select “Segments.”

2. **Result type**: Select either positive or negative. A positive search returns entries
   that satisfy the environment you choose in the environment selection; while negative search
   returns the strings that do *not* fall under the environment that you specify, i.e., the complement
   of your search.

3. **Tier**: Select the tier on which phonological search should be performed.
   The default would be the transcription tier, so that phonological
   environments are defined locally. But, for example, if a vowel tier
   is selected, then one could search for the occurrence of, e.g., [i]
   before mid vowels on that tier (hence ignoring intervening consonants). (Note that it is not currently possible to do a phonological search within :ref:`pronunciation_variants`; the search will look only at the canonical forms or whatever forms are listed in the specified tier.)

4. **Environments**: Select the strings you want to search for. See :ref:`environment_selection` and :ref:`sound_selection` for details.

   An example of adding environments for a positive search (in this case, the environment “word-initial,
   before a vowel”):

   .. image:: static/phonosearchenvironment.png
      :width: 100%
      :align: center

   An example of the phonological search window, set up to search for voiceless stops word-initially before vowels
   and between [ɑ] vowels, on the transcription tier (positive search):

   .. image:: static/phonosearchenvironment2.png
      :width: 100%
      :align: center

   An example of the phonological search window, set up to search for voiceless stops word-initially before vowels and
   between [ɑ] vowels, on the transcription tier (negative search):

   .. image:: static/phonosearchenvironment3.png
      :width: 100%
      :align: center

5. **Saving Searches**: It is possible to save particular searches and then re-load them for later use (within the same
   corpus, or in a different one). PCT will automatically save the five most recent searches for you, but you can also
   specify that any particular search should be saved for the long term.

   To save a search, click on “Save current search” in the “Phonological Search” dialogue box (see above pictures).
   To modify it or to use a saved search, click on “Load recent search.” See :ref:`saving_phono_search` for details.

6. **Additional filters**: It is possible to filter out tokens by word, phoneme, or syllable frequencies.
   To do this, enter numbers in the relevant slots located under the “Additional filters” group. Note that those
   minimum and maximum frequency filters apply after the search is done, i.e., by removing unwanted search tokens on
   search results. Also note that the syllable number filters are not applicable to a corpus without syllables.
   See :ref:`column-delimited` for how to create a corpus with a syllable delimiter.

7. **Results**: Once all selections have been made, click on “Calculate
   phonological search.” If there is not already an existing results table,
   or you want to start a new one, choose the “Start new results table”
   option. If you want to add the results to a pre-existing table, choose
   the “Add to current results table” option. The results appear in a new
   dialogue box that first shows the summary results, i.e., a list that
   contains the segment that was searched for, each environment that was
   searched for, the total count of words that contain that segment in that
   environment, and the total token frequency for those words (note that
   these are the frequencies of the WORDS containing the specified environments,
   so if for example, a particular word contains multiple instances of the same
   environment, this is NOT reflected in the counts). The individual words in
   the corpus that match the search criteria can be shown by clicking on “Show
   individual results” at the bottom of the screen; this opens a new dialogue
   box in which each word in the corpus that matches the search criteria is
   listed, including the transcription of the word, the segment that was found
   that matches the search criteria, and which environment that segment
   occurred in in that word. Note that the results can be sorted by any of
   the columns by clicking on that column’s name (e.g., to get all the words
   that contained the [a_a] environment together, simply click on the “Environment”
   label at the top of that column). To return to the summary results, click on
   “Show summary results.” Each set of results can be saved to a .txt file by
   clicking “Save to file” at the bottom of the relevant results window. To
   return to the search selection dialogue box, click on “Reopen function dialogue.”
   Otherwise, when finished, click on “Close window” to return to the corpus.

   An example of the summary results window for the above positive phonological search:

   .. image:: static/phonosearchsummary.png
      :width: 90%
      :align: center

   And the individual results from the same search, sorted by environment:

   .. image:: static/phonosearchindividual.png
      :width: 90%
      :align: center

   Finally, the same environment but negative search option returns the following individual results:

   .. image:: static/phonosearchindividualnegative.png
      :width: 90%
      :align: center


.. _syllable_mode:

Syllable mode
=============

Syllable mode enables you to incorporate the notion of the syllable in your phonological searches. The basic
operation is the same as segments mode, except the environment selection. Syllables mode comes in handy
when, for example, you want to limit your search to the second syllable of a word, or to the onset of a syllable.
If you were to do it in segments mode, you would need to construct by hand all the different types of possible syllables before
the target, because the segments mode is blind to the notion of the syllable. Syllables mode also allows you to search
for characteristics that are specified at the syllabic level, such as stress or tone. In order to use syllables mode, though,
your corpus must be delimited for syllables; see :ref:`parsing_parameters`.


1. **Search mode**: Select “Syllables.”

2. **Result type**: Select either positive or negative. A positive search returns entries that satisfy
   the environment you choose in the environment selection; while negative search returns the strings
   that do NOT fall under the environment that you specify.

3. **Tier**: Select the tier on which phonological search should be performed.
   The default would be the transcription tier, so that phonological
   environments are defined locally. But, for example, if a vowel tier
   is selected, then one could search for the occurrence of, e.g., [i]
   before mid vowels on that tier (hence ignoring intervening consonants).
   Note that it is not currently possible to do a syllable search within other tiers than 'Transcription.'
   Also, phonological search within :ref:`pronunciation_variants` is not available. The search will look
   only at the canonical forms or whatever forms are listed in the specified tier.)

4. **Environments**: Construct a syllable by selecting 'Construct the syllable,' or add a non-segment symbol (for non-targets). Constructing a syllable means
   specifying the environment for each syllable component. See examples below for the syllable construction. Also, see :ref:`environment_selection` and :ref:`sound_selection` for environment selection.

   To construct a syllable, first you will need to add a new environment by clicking the “New environment” button.
   And then, you can construct a target syllable by selecting "Construct the syllable" from the dropdown menu
   of Edit. The Construct syllables window will pop up. Now you can specify Onset and Nucleus just as you
   would do in :ref:`environment_selection`. And you can also specify Stress and Tone for the target syllable
   on the right-hand side.

   For each syllable component, you can select environment and specify a search type among "Exactly matches", "Minimally contains", "Starts with", and "Ends with."
   Please note that using "Exactly matches" while not specifying an onset/coda slot means "no onset/coda", while using "Minimally contains" without specifying an
   onset or coda means that the onset or coda may either be empty or filled. Using a single wildcard for onset/coda slot does mean that a segment must fill the slot.

   Additionally, you can exclude specific segments at a syllable component by selecting "Set negative" from the dropdown menu. For example,
   if you want to search for a syllable that has any phoneme except +labial at the onset position and [ɑ] as the nucleus, you can do so in
   the "Construct syllables" window by specifying "Nucleus" as [ɑ] and setting "Onset" as +labial with "Set negative" option checked from
   the dropdown menu. This will search for [sɑ], [rɑ], etc. but exclude [mɑ] or [pɑ].

   Now, let's assume you search for the cases where the second syllables are either /tɑ/ or /sɑ/ (Alveolar-stop or alveolar-fricative onset and low-back vowel nucleus). You may want to select syllable environment as the below screenshot shows. To implement a second syllable position, the target syllable is preceded by a # and an unspecified syllable (select 'Add an unspecified syllable' from dropdown menu)

   An example of constructing a target syllable at the second syllable position (in this case, a syllable constructed so as to have the onset consist of either an alveolar stop or fricative, and the nucleus of a low-back vowel):

   .. image:: static/phonosearchenvironmentsyllable.png
      :width: 100%
      :align: center

   Another example of constructing the syllable (unlike above, only closed syllables are counted):

   .. image:: static/phonosearchenvironmentsyllable2.png
      :width: 100%
      :align: center


5. **Saving Searches**: It is possible to save particular searches, as in the Segments mode. To save a search,
   click on "Save current search" in the "Phonological Search" dialogue box. See :ref:`saving_phono_search` for more
   information.

6. **Additional filters**: It is possible to filter out tokens by word, phoneme, or syllable frequencies.
   To do this, enter numbers in the relevant slots located under the “Additional filters” group. Note that those
   minimum and maximum frequency filters apply after the search is done, i.e., by removing unwanted search tokens on
   search results.

7. **Results**: Once all selections have been made, click on “Calculate
   phonological search.” If there is not already an existing results table,
   or you want to start a new one, choose the “Start new results table”
   option. If you want to add the results to a pre-existing table, choose
   the “Add to current results table” option. The results appear in a new
   dialogue box that first shows the summary results, i.e., a list that
   contains the segment that was searched for, each environment that was
   searched for, the total count of words that contain that segment in that
   environment, and the total token frequency for those words (note that
   these are the frequencies of the WORDS containing the specified environments,
   so if for example, a particular word contains multiple instances of the same
   environment, this is NOT reflected in the counts). The individual words in
   the corpus that match the search criteria can be shown by clicking on “Show
   individual results” at the bottom of the screen; this opens a new dialogue
   box in which each word in the corpus that matches the search criteria is
   listed, including the transcription of the word, the segment that was found
   that matches the search criteria, and which environment that segment
   occurred in in that word. Note that the results can be sorted by any of
   the columns by clicking on that column’s name. To return to the summary results, click on
   “Show summary results.” Each set of results can be saved to a .txt file by
   clicking “Save to file” at the bottom of the relevant results window. To
   return to the search selection dialogue box, click on “Reopen function dialogue.”
   Otherwise, when finished, click on “Close window” to return to the corpus.

   An example of the summary results window for the above syllable mode search:

   .. image:: static/phonosearchsummarysyllable.png
      :width: 70%
      :align: center

   And the individual results from the same syllable mode search, sorted by environment:

   .. image:: static/phonosearchindividualsyllable.png
      :width: 70%
      :align: center


.. _saving_phono_search:

Saving searches
===============

The phonological searches you perform can be saved and used later, including in a different corpus.
You also have the option to name the phonological search that you save. For this, use the two buttons
under the “Searches” group in the “Phonological Search” dialogue. To save all current searches directly,
click “Save current search.” To choose which one to save, or load from previously saved searches,
click “Load recent search.”

* **Save current search**: If you click “Save current search,” a dialogue box with the information of a search will
  appear as shown below. In this example, we have already created a search for word-initial /t/ that comes before a vowel.
  Since we are saving this search, the target is specified as {t}, and environment as {#}_{ɑ,o,e,i,u}.
  If you confirm that this is the search you want to save, you can select “Save” to save it.
  Before clicking “Save,” you can give it a name using the textbox. Here, we name this search ‘word initial t.’
  If you don’t want to save the search, you can click the “cancel” button.

  .. image:: static/savingphonosearch1.png
     :width: 90%
     :align: center

  If the search is successfully saved, a message box will appear as below. Now ‘word initial t’
  can be found in the “Searches” dialogue, which is described next.

  .. image:: static/savingphonosearch2.png
     :width: 30%
     :align: center

* **Load recent search**: Clicking on “Load recent search” in the “Phonological Search” dialogue prompts a dialogue box titled
  “Searches” as shown below. This is the place where you can interact with recent, saved, or current searches:

  .. image:: static/phonosearchsaved.png
     :width: 90%
     :align: center


  On the left are listed the five most recent searches, showing the target and environment for each search.
  In the center are the “Saved searches.” On the right is the list of currently loaded searches. The list consists
  of searches that you created in the “Phonological Search” dialogue. It should be empty if you did not
  enter any search before coming into the “Searches” dialogue.

  You can right-click on one of these panels to bring up further options. For example, right-clicking on a
  recent search allows you to transfer it to the “Saved searches,” to delete it entirely, or to add it to the
  current search. Similarly, right-clicking on a saved search allows you to delete it entirely, to change its name,
  or to add it to the current search. Finally, you can save or delete a current search here too, by right-clicking
  on a recent search.

  .. image:: static/phonosearchsaved2.png
     :width: 90%
     :align: center

  You can give it a name when you save a current or recent search. If you want to change the name of an existing
  search, right-click on a saved search and select “Change name” as shown above. In these cases, the same
  “Name this search” dialogue will appear to let you (re)name the search.

  When you are done with saving searches, building a list of current searches, or other stuff in the “Searches”
  dialogue, click on the “Update environment” button to apply the change and go back to “Phonological Search.”

.. note:: Your “saved searches” are locally stored in the SEARCH folder within the working directory that contains
   the PCT software. See :ref:`local_storage` for details. If you want to conduct the same searches on a different machine,
   simply copy “saved.searches” to another computer.