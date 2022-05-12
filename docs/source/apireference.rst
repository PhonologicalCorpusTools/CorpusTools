.. _api_reference:

=============
API Reference
=============

.. _lexicon_classes_api:

Lexicon classes
---------------
.. currentmodule:: corpustools.corpus.classes

.. autosummary::
   :toctree: generate/
   :template: class.rst

   lexicon.Attribute
   lexicon.Corpus
   lexicon.Inventory
   lexicon.FeatureMatrix
   lexicon.Segment
   lexicon.Transcription
   lexicon.Word
   lexicon.EnvironmentFilter
   lexicon.Environment

.. _speech_classes_ref:

Speech corpus classes
---------------------
.. currentmodule:: corpustools.corpus.classes

.. autosummary::
   :toctree: generate/
   :template: class.rst

   spontaneous.Discourse
   spontaneous.Speaker
   spontaneous.SpontaneousSpeechCorpus
   spontaneous.WordToken

.. _corpus_context_api:

Corpus context managers
=======================
.. currentmodule:: corpustools

.. autosummary::
   :toctree: generate/
   :template: class.rst

   contextmanagers.BaseCorpusContext
   contextmanagers.CanonicalVariantContext
   contextmanagers.MostFrequentVariantContext
   contextmanagers.SeparatedTokensVariantContext
   contextmanagers.WeightedVariantContext


.. _corpus_io_api:

Corpus IO functions
===================

Corpus binaries
---------------

.. currentmodule:: corpustools.corpus.io

.. autosummary::
   :toctree: generate/
   :template: function.rst

   binary.download_binary
   binary.load_binary
   binary.save_binary


Loading from CSV
----------------

.. currentmodule:: corpustools.corpus.io

.. autosummary::
   :toctree: generate/
   :template: function.rst

   csv.load_corpus_csv
   csv.load_feature_matrix_csv

Export to CSV
-------------

.. currentmodule:: corpustools.corpus.io

.. autosummary::
   :toctree: generate/
   :template: function.rst

   csv.export_corpus_csv
   csv.export_feature_matrix_csv

TextGrids
---------

.. currentmodule:: corpustools.corpus.io

.. autosummary::
   :toctree: generate/
   :template: function.rst

   pct_textgrid.inspect_discourse_textgrid
   pct_textgrid.load_discourse_textgrid
   pct_textgrid.load_directory_textgrid

Running text
------------

.. currentmodule:: corpustools.corpus.io

.. autosummary::
   :toctree: generate/
   :template: function.rst

   text_spelling.inspect_discourse_spelling
   text_spelling.load_discourse_spelling
   text_spelling.load_directory_spelling
   text_spelling.export_discourse_spelling
   text_transcription.inspect_discourse_transcription
   text_transcription.load_discourse_transcription
   text_transcription.load_directory_transcription
   text_transcription.export_discourse_transcription

Interlinear gloss text
----------------------

.. currentmodule:: corpustools.corpus.io

.. autosummary::
   :toctree: generate/
   :template: function.rst

   text_ilg.inspect_discourse_ilg
   text_ilg.load_discourse_ilg
   text_ilg.load_directory_ilg
   text_ilg.export_discourse_ilg

Other standards
---------------

.. currentmodule:: corpustools.corpus.io

.. autosummary::
   :toctree: generate/
   :template: function.rst

   multiple_files.inspect_discourse_multiple_files
   multiple_files.load_discourse_multiple_files
   multiple_files.load_directory_multiple_files

Analysis functions
==================


.. _freq_alt_api:

Frequency of alternation
------------------------
**Frequency of alternation is currently not supported in PCT.**

.. currentmodule:: corpustools.freqalt

.. autosummary::
   :toctree: generate/
   :template: function.rst

   freq_of_alt.calc_freq_of_alt

.. _func_load_api:

Functional load
---------------

.. currentmodule:: corpustools.funcload

.. autosummary::
   :toctree: generate/
   :template: function.rst

   functional_load.minpair_fl
   functional_load.deltah_fl
   functional_load.relative_minpair_fl
   functional_load.relative_deltah_fl
   functional_load.entropy

.. _kl_api:

Kullback-Leibler divergence
---------------------------

.. currentmodule:: corpustools.kl

.. autosummary::
   :toctree: generate/
   :template: function.rst

   kl.KullbackLeibler


.. _mutual_info_api:

Mutual information
------------------

.. currentmodule:: corpustools.mutualinfo

.. autosummary::
   :toctree: generate/
   :template: function.rst

   mutual_information.pointwise_mi

.. _trans_prob_api:

Transitional probability
------------------------

.. currentmodule:: corpustools.transprob

.. _neigh_den_api:

Neighborhood density
--------------------

.. currentmodule:: corpustools.neighdens

.. autosummary::
   :toctree: generate/
   :template: function.rst

   neighborhood_density.neighborhood_density
   neighborhood_density.find_mutation_minpairs

.. _phono_prob_api:

Phonotactic probability
-----------------------

.. currentmodule:: corpustools.phonoprob

.. autosummary::
   :toctree: generate/
   :template: function.rst

   phonotactic_probability.phonotactic_probability_vitevitch

.. _prod_api:

Predictability of distribution
------------------------------

.. currentmodule:: corpustools.prod

.. autosummary::
   :toctree: generate/
   :template: function.rst

   pred_of_dist.calc_prod_all_envs
   pred_of_dist.calc_prod

.. _symbol_sim_api:

Symbol similarity
-----------------

.. currentmodule:: corpustools.symbolsim

.. autosummary::
   :toctree: generate/
   :template: function.rst

   string_similarity.string_similarity

.. currentmodule:: corpustools.symbolsim

.. autosummary::
   :toctree: generate/
   :template: function.rst

   edit_distance.edit_distance

.. currentmodule:: corpustools.symbolsim

.. autosummary::
   :toctree: generate/
   :template: function.rst

   khorsi.khorsi

.. currentmodule:: corpustools.symbolsim

.. autosummary::
   :toctree: generate/
   :template: function.rst

   phono_edit_distance.phono_edit_distance
