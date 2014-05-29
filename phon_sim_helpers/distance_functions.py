import operator
from numpy import (zeros, floor, sqrt, sum, correlate, argmax, abs)

from scipy.spatial.distance import euclidean

def xcorr_distance(rep_one,rep_two):
    """Computes the cross-correlation distance between two representations
    with the same number of filters.
    
    Parameters
    ----------
    rep_one : 2D array
        First representation to compare. First dimension is time in frames
        or samples and second dimension is the features.
    rep_two : 2D array
        Second representation to compare. First dimension is time in frames
        or samples and second dimension is the features.
    
    Returns
    -------
    float
        Inverse similarity (distance).  Similarity is the maximum cross-
        correlation value (normalized to be between 0 and 1) averaged 
        across all features of the two representations.
    
    """
    assert(rep_one.shape[1] == rep_two.shape[1])
    length_diff = rep_one.shape[0] - rep_two.shape[0]
    if length_diff > 0:
        longer_rep = rep_one
        shorterEnv = rep_two
    else:
        longer_rep = rep_two
        shorter_rep = rep_one
    num_features = longer_rep.shape[1]
    matchSum = correlate(longer_rep[:,0]/sqrt(sum(longer_rep[:,0]**2)),shorter_rep[:,0]/sqrt(sum(shorter_rep[:,0]**2)),mode='valid')
    for i in range(1,num_features):
        longer_feat = longer_rep[:,i]
        denom = sqrt(sum(longer_feat**2))
        longer_feat = longer_feat/denom
        shorter_feat = shorter_rep[:,i]
        denom = sqrt(sum(shorter_feat**2))
        shorter_feat = shorter_feat/denom
        temp = correlate(longer_feat,shorter_feat,mode='valid')
        matchSum += temp
    maxInd = argmax(matchSum)
    matchVal = abs(matchSum[maxInd]/num_features)
    return 1/matchVal

def dtw_distance(rep_one, rep_two):
    """Computes the distance between two representations with the same 
    number of filters using Dynamic Time Warping.
    
    Parameters
    ----------
    rep_one : 2D array
        First representation to compare. First dimension is time in frames
        or samples and second dimension is the features.
    rep_two : 2D array
        Second representation to compare. First dimension is time in frames
        or samples and second dimension is the features.
    
    Returns
    -------
    float
        Distance of dynamically time warping `rep_one` to `rep_two`.
    
    """
    
    assert(rep_one.shape[1] == rep_two.shape[1])
    distMat = generate_distance_matrix(rep_one,rep_two)
    return regularDTW(distMat)
    
def generate_distance_matrix(source,target):
    """Generates a local distance matrix for use in dynamic time warping.
    
    Parameters
    ----------
    source : 2D array
        Source matrix with features in the second dimension.
    target : 2D array
        Target matrix with features in the second dimension.
    
    Returns
    -------
    2D array
        Local distance matrix.
    
    """
    
    sLen = source.shape[0]
    tLen = target.shape[0]
    distMat = zeros((sLen,tLen))
    for i in range(sLen):
        for j in range(tLen):
            distMat[i,j] = euclidean(source[i,:],target[j,:])
    return distMat

def regularDTW(distMat):
    """Use a local distance matrix to perform dynamic time warping.
    
    Parameters
    ----------
    distMat : 2D array
        Local distance matrix.
    
    Returns
    -------
    float
        Total unweighted distance of the optimal path through the
        local distance matrix.
    
    """
    sLen,tLen = distMat.shape
    totalDistance = zeros((sLen+1,tLen+1))
    totalDistance[0,:] = inf
    totalDistance[:,0] = inf
    totalDistance[0,0] = 0
    totalDistance[1:sLen+1,1:tLen+1] = distMat
    
    minDirection = zeros((sLen+1,tLen+1))
    
    for i in range(sLen):
        for j in range(tLen):
            direction,minPrevDistance = min(enumerate([totalDistance[i,j],totalDistance[i,j+1],totalDistance[i+1,j]]), key=operator.itemgetter(1))
            totalDistance[i+1,j+1] = totalDistance[i+1,j+1] + minPrevDistance
            minDirection[i,j] = direction
    
    return totalDistance[sLen,tLen]
    
