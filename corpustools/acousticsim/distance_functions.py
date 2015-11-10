import operator
from numpy import (zeros, floor, sqrt, sum, correlate, argmax, abs,inf)

from scipy.spatial.distance import euclidean

def xcorr_distance(rep_one,rep_two):
    """Computes the cross-correlation distance between two representations
    with the same number of filters.

    Parameters
    ----------
    rep_one : 2D array
        First representation to compare. First dimension is time in frames
        or samples and second dimension is the _features.
    rep_two : 2D array
        Second representation to compare. First dimension is time in frames
        or samples and second dimension is the _features.

    Returns
    -------
    float
        Inverse similarity (distance).  Similarity is the maximum cross-
        correlation value (normalized to be between 0 and 1) averaged
        across all _features of the two representations.

    """
    assert(rep_one.shape[1] == rep_two.shape[1])
    length_diff = rep_one.shape[0] - rep_two.shape[0]
    if length_diff > 0:
        longer_rep = rep_one
        shorter_rep = rep_two
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

def dtw_distance(rep_one, rep_two,norm=True):
    """Computes the distance between two representations with the same
    number of filters using Dynamic Time Warping.

    Parameters
    ----------
    rep_one : 2D array
        First representation to compare. First dimension is time in frames
        or samples and second dimension is the _features.
    rep_two : 2D array
        Second representation to compare. First dimension is time in frames
        or samples and second dimension is the _features.

    Returns
    -------
    float
        Distance of dynamically time warping `rep_one` to `rep_two`.

    """

    assert(rep_one.shape[1] == rep_two.shape[1])
    distMat = generate_distance_matrix(rep_one,rep_two)
    return regularDTW(distMat,norm=norm)

def generate_distance_matrix(source,target):
    """Generates a local distance matrix for use in dynamic time warping.

    Parameters
    ----------
    source : 2D array
        Source matrix with _features in the second dimension.
    target : 2D array
        Target matrix with _features in the second dimension.

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

def regularDTW(distMat,norm=True):
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
    totalDistance = zeros((sLen,tLen))
    totalDistance[0:sLen,0:tLen] = distMat

    minDirection = zeros((sLen,tLen))

    for i in range(1,sLen):
        totalDistance[i,0] = totalDistance[i,0] + totalDistance[i-1,0]

    for j in range(1,tLen):
        totalDistance[0,j] = totalDistance[0,j] + totalDistance[0,j-1]



    for i in range(1,sLen):
        for j in range(1,tLen):
            #direction,minPrevDistance = min(enumerate([totalDistance[i,j],totalDistance[i,j+1],totalDistance[i+1,j]]), key=operator.itemgetter(1))
            #totalDistance[i+1,j+1] = totalDistance[i+1,j+1] + minPrevDistance
            #minDirection[i,j] = direction
            minDirection[i,j],totalDistance[i,j] = min(enumerate([totalDistance[i-1,j-1] + 2*totalDistance[i,j],
                                                            totalDistance[i-1,j] + totalDistance[i,j],
                                                            totalDistance[i,j-1] + totalDistance[i,j]]), key=operator.itemgetter(1))
    if norm:
        return totalDistance[sLen-1,tLen-1] / (sLen+tLen)
    return totalDistance[sLen-1,tLen-1]

