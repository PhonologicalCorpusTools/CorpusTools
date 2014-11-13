import os
from numpy import zeros

from functools import partial

from corpustools.acousticsim.representations import to_envelopes, to_mfcc
from corpustools.acousticsim.distance_functions import dtw_distance, xcorr_distance


def _build_to_rep(**kwargs):
    rep = kwargs.get('rep', 'mfcc')


    num_filters = kwargs.get('num_filters',None)
    num_coeffs = kwargs.get('num_coeffs', 20)

    freq_lims = kwargs.get('freq_lims', (80, 7800))

    win_len = kwargs.get('win_len', 0.025)
    time_step = kwargs.get('time_step', 0.01)

    use_power = kwargs.get('use_power', True)

    if num_filters is None:
        if rep == 'envelopes':
            num_filters = 8
        else:
            num_filters = 26


    if rep == 'envelopes':
        to_rep = partial(to_envelopes,
                                num_bands=num_filters,
                                freq_lims=freq_lims)
    elif rep == 'mfcc':
        to_rep = partial(to_mfcc,freq_lims=freq_lims,
                                    num_coeffs=num_coeffs,
                                    num_filters = num_filters,
                                    win_len=win_len,
                                    time_step=time_step,
                                    use_power = use_power)
    else:
        return None
    return to_rep

def acoustic_similarity_mapping(path_mapping,**kwargs):
    """Takes in an explicit mapping of full paths to .wav files to have
    acoustic similarity computed.

    Parameters
    ----------
    path_mapping : iterable of iterables
        Explicit mapping of full paths of .wav files, in the form of a
        list of tuples to be compared.
    rep : {'envelopes','mfcc'}, optional
        The type of representation to convert the wav files into before
        comparing for similarity.  Amplitude envelopes will be computed
        when 'envelopes' is specified, and MFCCs will be computed when
        'mfcc' is specified.
    match_function : {'dtw', 'xcorr'}, optional
        How similarity/distance will be calculated.  Defaults to 'dtw' to
        use Dynamic Time Warping (can be slower) to compute distance.
        Cross-correlation can be specified with 'xcorr', which computes
        distance as the inverse of a maximum cross-correlation value
        between 0 and 1.
    num_filters : int, optional
        The number of frequency filters to use when computing representations.
        Defaults to 8 for amplitude envelopes and 26 for MFCCs.
    num_coeffs : int, optional
        The number of coefficients to use for MFCCs (not used for
        amplitude envelopes).  Default is 20, which captures speaker-
        specific information, whereas 12 would be more speaker-independent.
    freq_lims : tuple, optional
        A tuple of the minimum frequency and maximum frequency in Hertz to use
        for computing representations.  Defaults to (80, 7800) following
        Lewandowski's dissertation (2012).
    output_sim : bool, optional
        If true (default), the function will return similarities (inverse distance).
        If false, distance measures will be returned instead.
    verbose : bool, optional
        If true, command line progress will be displayed after every 50
        mappings have been processed.  Defaults to false.

    Returns
    -------
    list of tuples
        Returns a list of tuples corresponding to the `path_mapping` input,
        with a new final element in the tuple being the similarity/distance
        score for that mapping.

    """

    stop_check = kwargs.get('stop_check',None)
    call_back = kwargs.get('call_back',None)
    to_rep = _build_to_rep(**kwargs)

    num_cores = kwargs.get('num_cores', 1)
    output_sim = kwargs.get('output_sim',False)

    match_function = kwargs.get('match_function', 'dtw')
    cache = kwargs.get('cache',None)
    if match_function == 'xcorr':
        dist_func = xcorr_distance
    elif match_function == 'dct':
        dist_func = dct_distance
    else:
        dist_func = dtw_distance
    cache = dict()
    output_values = list()
    if call_back is not None:
        call_back('Calculating acoustic similarity...')
        call_back(0,len(path_mapping))
        cur = 0
    for i,pm in enumerate(path_mapping):
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 100 == 0:
                call_back(cur)
        for filepath in pm:
            if filepath not in cache:
                cache[filepath] = to_rep(filepath)
        dist_val = dist_func(cache[pm[0]],cache[pm[1]])
        if output_sim:
            dist_val = 1/dist_val
        output_values.append([pm[0],pm[1],dist_val])

    return output_values

def acoustic_similarity_directories(directory_one,directory_two,**kwargs):
    """Computes acoustic similarity across two directories of .wav files.

    Parameters
    ----------
    directory_one : str
        Full path of the first directory to be compared.
    directory_two : str
        Full path of the second directory to be compared.
    all_to_all : bool, optional
        If true (default), do all possible comparisons between the two
        directories.  If false, try to do pairwise comparisons between
        files.
    rep : {'envelopes','mfcc'}, optional
        The type of representation to convert the wav files into before
        comparing for similarity.  Amplitude envelopes will be computed
        when 'envelopes' is specified, and MFCCs will be computed when
        'mfcc' is specified.
    match_function : {'dtw', 'xcorr'}, optional
        How similarity/distance will be calculated.  Defaults to 'dtw' to
        use Dynamic Time Warping (can be slower) to compute distance.
        Cross-correlation can be specified with 'xcorr', which computes
        distance as the inverse of a maximum cross-correlation value
        between 0 and 1.
    num_filters : int, optional
        The number of frequency filters to use when computing representations.
        Defaults to 8 for amplitude envelopes and 26 for MFCCs.
    num_coeffs : int, optional
        The number of coefficients to use for MFCCs (not used for
        amplitude envelopes).  Default is 20, which captures speaker-
        specific information, whereas 12 would be more speaker-independent.
    freq_lims : tuple, optional
        A tuple of the minimum frequency and maximum frequency in Hertz to use
        for computing representations.  Defaults to (80, 7800) following
        Lewandowski's dissertation (2012).
    output_sim : bool, optional
        If true (default), the function will return similarities (inverse distance).
        If false, distance measures will be returned instead.
    verbose : bool, optional
        If true, command line progress will be displayed after every 50
        mappings have been processed.  Defaults to false.

    Returns
    -------
    float
        Average distance/similarity of all the comparisons that were done
        between the two directories.

    """

    stop_check = kwargs.get('stop_check',None)
    call_back = kwargs.get('call_back',None)

    files_one = [x for x in os.listdir(directory_one) if x.lower().endswith('.wav')]
    files_two = [x for x in os.listdir(directory_two) if x.lower().endswith('.wav')]
    if call_back is not None:
        call_back('Mapping directories...')
        call_back(0,len(files_one)*len(files_two))
        cur = 0
    path_mapping = list()
    for x in files_one:
        for y in files_two:
            if stop_check is not None and stop_check():
                return
            if call_back is not None:
                cur += 1
                if cur % 100 == 0:
                    call_back(cur)
            path_mapping.append((os.path.join(directory_one,x),
                        os.path.join(directory_two,y)))

    output = acoustic_similarity_mapping(path_mapping, **kwargs)
    if stop_check is not None and stop_check():
        return
    output_val = sum([x[-1] for x in output]) / len(output)

    threaded_q = kwargs.get('threaded_q', None)
    if kwargs.get('return_all', False):
        output_val = output,output_val
    if not threaded_q:
        return output_val
    else:
        threaded_q.put(output_val)
        return None



