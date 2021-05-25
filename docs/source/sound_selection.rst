.. _sound_selection:

***************
Sound Selection
***************

There are many instances in PCT where you are given the opportunity to
select sounds that will be used in an analysis or a :ref:`phonological_search`. This section
describes the general interface used in all such instances, including
using featural descriptions to select sounds. See also :ref:`feature_selection`
for information about how to seelct features on which to do analyses.

When selecting a sound or a pair of sounds, you will be presented with a
dialogue box that contains all of the unique segments that occur in the corpus.
If there is no feature system associated with the corpus, then these will
be arranged in alphabetical order as a solid block. If there is an
associated feature system, then the segments will be arranged in an
IPA-style format. Note that there will be separate tabbed windows for consonants, vowels, and uncategorized segments. You can customize the layout of this display; for
details on how to do so, see :ref:`inventory_categories`. If there are
associated features, there will also be an option at the top of the
"select segment" box to "select by feature."

To select sounds, there are two options:

First, you can simply click on individual segments in the list or chart
of segments. Multiple segments can be selected at once; just click on each box in turn (no additional keys need to be pressed to ensure multiple selection). If you are selecting
sounds for an analysis that involves a single segment, then each selected
segment will undergo the same analysis. (E.g., in a :ref:`phonological_search`,
if you select A, B, C, and D as the target sounds, then each of those sounds
will be searched for in the same environment.) If you are selecting sounds
for an analysis that involves a pair of sounds, then all the pairwise
combinations of the selected sounds will be created. (E.g., if you select
A, B, C, and D as sounds in a pairwise selection, then all of the pairs,
i.e., AB, AC, AD, BC, BD, and CD, will be selected. In many analyses the
order of the sounds in the pair doesn't matter, but PCT also will allow
you to switch the order after the pairs have been created.)

Second, if there is an associated feature file, you can select sounds
using featural descriptions. To do so, simply start typing a feature
value into the "Select by feature" box at the top of the sound selection
box. As soon as any value or characters are typed, a dropdown box will
appear that lists all of the available features that match the current typing.
For example, just typing a "+" sign will reveal + values of all features that
have a + specification in the feature chart (e.g., +anterior, +coronal, +long,
+nasal, + sonorant, +vocalic, etc.). Typing a letter, such as "c" will show
all features that start with that letter (e.g., -consonantal, -constricted
glottis, -consonantal, -coronal, +consonantal, +constricted glottis,
+consonantal, +coronal, etc.). You can continue typing out the feature
or select one from the list by either clicking on it or hitting "return"
when it is the one highlighted. Once a feature is entered, all segments
that have that feature specification will be highlighted on the
chart. This does not in fact "select" them yet -- it just indicates which
segments match the currently listed specifications. Note that segments may be highlighted in multiple tabs -- e.g., selecting the feature [+high] might highlight [k] and [ɡ] in the consonant tab, and [i] and [u] in the vowel tab.  Once segments are
highlighted, you may continue entering features to winnow down the
selection, or revert to clicking on individual segments (e.g., from among
the highlighted ones). As more features are typed in and selected, the
highlighting in the chart will update to match the current feature
specification. (Features in the list can be separated by commas or spaces.)
To actually SELECT all the highlighted segments, you can simply hit "enter"
again after the names of the features are completely entered, and the
highlighting will change to selection. Alternatively, you can click on
the "Select highlighted" button. Once segments are selected, the entire list of selected segments is visible at the bottom of the window. E.g., if all [+high] segments were selected, all of [k, ɡ, i, u] would be listed; this makes it easy to check that the correct set of segments has been selected across all tabs.




