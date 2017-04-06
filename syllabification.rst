.. _syllable_segmentation:

*************
Syllable Segmentation
*************

.. _about_Syllable Segmentation:

About the function
------------------

The syllable segmentation functions act as a work flow for the analysis of syllable structure. While it will provide information about any language type, it is specifically designed with onset maximization and coda maximization in mind. Onset Maximization was first described by [Selkirk1982]_: when syllabifying, any consonants should be allotted to the beginning of a syllable, so long as the language allows a consonant cluster phonotactically. However, following Selkirk, Coda maximization was also suggested [Wells1990]_. Generally, all known languages allow onsets although some languages do not permit codas. The typological literature suggests that there are languages that require onsets and languages where they are optional, but there are no languages where onsets are banned [Zec2007]_. In contrast, no language requires codas, and some do not allow them at all. Nevertheless, languages such as English and Finnish have been argued to feature coda maximization (in combination with other factors). Indeed while languages such as Finnish allow both onsets and codas, they allow coda clusters but do not allow onset clusters. In the future, both onset maximization code and coda maximization code will work together.

The intended work flow for these functions is as follows: 
1. Create a list of all word-initial syllable onsets and all word-final codas (if any). 
2. Segment the corpus either with the onsets or codas first. (Usually onsets the first time) 
3. Examine the resulting segmentation. There will likely be word-medial syllable clusters left over that have not been segmented.
(3a.) Modify the csv list of possible onset clusters or coda clusters.
(3b) Segment the corpus by onsets or codas. 



.. _word_onset:

Word Onset Finder
---------------------


Calculating informativity with a .corpus file
---------------------------------------------
    
1.  **Run word_onset_finder.py**: Open a terminal and navigate to the directory where informativity.py is located. Note that PCT uses Python 3, and run the following:

2. This will output a file "onsets.csv"

3.  **Run word_onset_segmenter.py**: this will output a file "segmented_by_codas.py"

4. Modify the file "onsets.csv" in order to try different segmentation schemas, although it is important to ensure that if new segment is added it is necessary to put '.' in the second column.


**NOTE**: In the future, this portion of the documentation will be modified for syllabifying in the GUI and on the command line, to better conform to and integrate with PCT.

.. _functional_load_gui:

Syllabifying in the GUI
--------------------------------------
Details will be added here upon full integration with PCT.

.. _functional_load_cli:

Implementing the syllabifying functions on the command line
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

.. [Selkirk1982] Selkirk, Elisabeth (1982). Syllables. The structure of phonological representations, 2, 337-383.

.. [Wells1990] Wells, John. C. (1990). Syllabification and allopho-ny. Studies in the pronunciation of English: A commemorative volume in honour of AC Gimson, 76-86.

.. [Zec2007] Zec, D. (2007). The syllable. The Cambridge handbook of phonology, 161-194.

