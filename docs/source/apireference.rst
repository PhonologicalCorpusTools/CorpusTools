=============
API Reference
=============

.. _lexicon_classes_ref:

Lexicon classes
---------------
.. currentmodule:: corpustools.corpus.classes

.. autosummary::
   :toctree: generated/
   :template: class.rst

   lexicon.Attribute
   lexicon.Corpus
   lexicon.FeatureMatrix
   lexicon.Segment
   lexicon.Transcription
   lexicon.Word

.. _speech_classes_ref:

Speech corpus classes
---------------------
.. currentmodule:: corpustools.corpus.classes

.. autosummary::
   :toctree: generated/
   :template: class.rst

   spontaneous.Discourse
   spontaneous.Speaker
   spontaneous.SpontaneousSpeechCorpus
   spontaneous.WordToken


.. _corpus_io_ref:

Corpus IO functions
===================

Corpus binaries
---------------

.. currentmodule:: corpustools.corpus.io

.. autosummary::
   :toctree: generated/
   :template: function.rst

   binary.download_binary
   binary.load_binary
   binary.save_binary


Loading from CSV
----------------

.. currentmodule:: corpustools.corpus.io

.. autosummary::
   :toctree: generated/
   :template: function.rst

   csv.load_corpus_csv
   csv.load_feature_matrix_csv

Export to CSV
-------------

.. currentmodule:: corpustools.corpus.io

.. autosummary::
   :toctree: generated/
   :template: function.rst

   csv.export_corpus_csv
   csv.export_feature_matrix_csv

Loading speech corpora
----------------------

.. currentmodule:: corpustools.corpus.io

.. autosummary::
   :toctree: generated/
   :template: function.rst

   spontaneous.import_spontaneous_speech_corpus

Running text
------------

.. currentmodule:: corpustools.corpus.io

.. autosummary::
   :toctree: generated/
   :template: function.rst

   text_spelling.load_spelling_corpus
   text_transcription.load_transcription_corpus

Analysis functions
==================

Frequency of alternation
------------------------

.. currentmodule:: corpustools.freqalt

.. autosummary::
   :toctree: generated/
   :template: function.rst

   freq_of_alt.calc_freq_of_alt

Functional load
---------------

.. currentmodule:: corpustools.funcload

.. autosummary::
   :toctree: generated/
   :template: function.rst

   functional_load.minpair_fl
   functional_load.deltah_fl
   functional_load.relative_minpair_fl
   functional_load.relative_deltah_fl

Kullback-Leibler divergence
---------------------------

.. currentmodule:: corpustools.kl

.. autosummary::
   :toctree: generated/
   :template: function.rst

   kl.KullbackLeibler

Mutual information
------------------

.. currentmodule:: corpustools.mutualinfo

.. autosummary::
   :toctree: generated/
   :template: function.rst

   mutual_information.pointwise_mi

Neighborhood density
--------------------

.. currentmodule:: corpustools.neighdens

.. autosummary::
   :toctree: generated/
   :template: function.rst

   neighborhood_density.neighborhood_density
   neighborhood_density.find_mutation_minpairs

Phonotactic probability
-----------------------

.. currentmodule:: corpustools.phonoprob

.. autosummary::
   :toctree: generated/
   :template: function.rst

   phonotactic_probability.phonotactic_probability_vitevitch

Predictability of distribution
------------------------------

.. currentmodule:: corpustools.prod

.. autosummary::
   :toctree: generated/
   :template: function.rst

   pred_of_dist.calc_prod_all_envs
   pred_of_dist.calc_prod

Symbol similarity
-----------------

.. currentmodule:: corpustools.symbolsim

.. autosummary::
   :toctree: generated/
   :template: function.rst

   string_similarity.string_similarity

.. currentmodule:: corpustools.symbolsim

.. autosummary::
   :toctree: generated/
   :template: function.rst

   edit_distance.edit_distance

.. currentmodule:: corpustools.symbolsim

.. autosummary::
   :toctree: generated/
   :template: function.rst

   khorsi.khorsi

.. currentmodule:: corpustools.symbolsim

.. autosummary::
   :toctree: generated/
   :template: function.rst

   phono_edit_distance.phono_edit_distance








