import os
from numpy import zeros

from functools import partial

from corpustools.acousticsim.representations import to_envelopes, to_mfcc
from corpustools.acousticsim.distance_functions import dtw_distance, xcorr_distance

def acoustic_similarity_mapping(path_mapping,
                            rep = 'envelopes',
                            match_function = 'dtw',
                            num_filters = None,
                            num_coeffs = 20,
                            freq_lims = (80,7800),
                            output_sim = True,
                            verbose=False):
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
    if num_filters is None:
        if rep == 'envelopes':
            num_filters = 8
        else:
            num_filters = 26
    output_values = []
    total_mappings = len(path_mapping)
    cache = {}
    if match_function == 'dtw':
        dist_func = dtw_distance
    else:
        dist_func = xcorr_distance
    if rep == 'envelopes':
        to_rep = partial(to_envelopes,num_bands=num_filters,freq_lims=freq_lims)
    else:
        to_rep = partial(to_mfcc,freq_lims=freq_lims,
                             num_coeffs=num_coeffs,
                             num_filters = num_filters, 
                             win_len=0.025,
                             time_step=0.01,
                             use_power = False)
          
    for i,pm in enumerate(path_mapping):
        if verbose and i % 50 == 0:
            print('Mapping %d of %d processed' % (i,total_mappings))
        for filepath in pm:
                if filepath not in cache:
                    cache[filepath] = to_rep(filepath)
        dist_val = dist_func(cache[pm[0]],cache[pm[1]])
        if output_sim:
            dist_val = 1/dist_val
        output_values.append([pm[0],pm[1],dist_val])
      
    return output_values
    
def acoustic_similarity_directories(directory_one,directory_two,
                            all_to_all = True,
                            rep = 'envelopes',
                            match_function = 'dtw',
                            num_filters = None,
                            num_coeffs = 20,
                            freq_lims = (80,7800),
                            output_sim = True,
                            verbose=False,
                            use_multi=False,
                            threaded_q=None):
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
    if num_filters is None:
        if rep == 'envelopes':
            num_filters = 8
        else:
            num_filters = 26
    if match_function == 'dtw':
        dist_func = dtw_distance
    else:
        dist_func = xcorr_distance
    if rep == 'envelopes':
        to_rep = partial(to_envelopes,num_bands=num_filters,freq_lims=freq_lims)
    else:
        to_rep = partial(to_mfcc,freq_lims=freq_lims,
                             num_coeffs=num_coeffs,
                             num_filters = num_filters, 
                             win_len=0.025,
                             time_step=0.01,
                             use_power = False)
                             
    files_one = os.listdir(directory_one)
    len_one = len(files_one)
    files_two = os.listdir(directory_two)
    len_two = len(files_two)
    if not all_to_all and len_one == len_two:
        output = zeros((len_one,))
        for i in range(len_one):
            if verbose and i % 50 == 0:
                print('Mapping %d of %d processed' % (i,len_one))
            rep_one = to_rep(os.path.join(directory_one,files_one[i]))
            rep_two = to_rep(os.path.join(directory_two,files_two[i]))
            dist_val = dist_func(rep_one,rep_two)
            if output_sim:
                dist_val = 1 / dist_val
            output[i] = dist_val
        output_val = output.mean()
    else:
        output = zeros((len_one,len_two))
        for i in range(len_one):
            rep_one = to_rep(os.path.join(directory_one,files_one[i]))
            for j in range(len_two):
                rep_two = to_rep(os.path.join(directory_two,files_two[j]))
                dist_val = dist_func(rep_one,rep_two)
                if output_sim:
                    dist_val = 1 / dist_val
                output[i,j] = dist_val
        output_val = output[output > 0].mean()
    if not threaded_q:
        return output_val
    else:
        threaded_q.put(output_val)
        return None
    
    

