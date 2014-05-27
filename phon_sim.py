from numpy import zeros

from functools import partial

try:
    from phon_sim_helpers.representations import to_envelopes, to_mfcc
    from phon_sim_helpers.distance_functions import dtw_distance, xcorr_distance
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from phon_sim_helpers.representations import to_envelopes, to_mfcc
    from phon_sim_helpers.distance_functions import dtw_distance, xcorr_distance

def phonetic_similarity(path_mapping,
                            num_bands = 8,
                            num_coeffs = 20,
                            freq_lims = (80,7800),
                            rep = 'envelopes',
                            match_function = 'dtw',
                            output_sim = True,
                            verbose=False):
    output_values = []
    total_mappings = len(path_mapping)
    cache = {}
    if match_function == 'dtw':
        dist_func = dtw_distance
    else:
        dist_func = xcorr_distance
    if rep == 'envelopes':
        to_rep = partial(to_envelopes,num_bands=num_bands,freq_lims=freq_lims)
    else:
        to_rep = partial(to_mfcc,freq_lims=freq_lims,
                             num_coeffs=num_coeffs,
                             num_filters = 26, 
                             win_len=0.025,
                             time_step=0.01,
                             use_power = False)
          
    for i,pm in enumerate(path_mapping):
        if verbose and i % 50 == 0:
            print('Mapping %d of %d processed' % (i,total_mappings))
        for filepath in pm:
                if filepath not in cache:
                    cache[filepath] = to_rep(filepath,num_bands,freq_lims)
        dist_val = dist_func(cache[pm[0]],cache[pm[1]])
        if output_sim:
            dist_val = 1/dist_val
        output_values.append([pm[0],pm[1],dist_val])
      
    return output_values
    
def phonetic_similarity(directory_one,directory_two,
                            all_to_all = True,
                            num_bands = 8,
                            num_coeffs = 20,
                            freq_lims = (80,7800),
                            rep = 'envelopes',
                            match_function = 'dtw',
                            output_sim = True,
                            verbose=False):
    if match_function == 'dtw':
        dist_func = dtw_distance
    else:
        dist_func = xcorr_distance
    if rep == 'envelopes':
        to_rep = partial(to_envelopes,num_bands=num_bands,freq_lims=freq_lims)
    else:
        to_rep = partial(to_mfcc,freq_lims=freq_lims,
                             num_coeffs=num_coeffs,
                             num_filters = 26, 
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
    return output_val
    

