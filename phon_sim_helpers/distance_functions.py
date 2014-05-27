import operator
from numpy import (zeros, floor, sqrt, sum, correlate, argmax, abs)

from scipy.spatial.distance import euclidean

def xcorr_distance(e1,e2):
    length_diff = e1.shape[0] - e2.shape[0]
    if length_diff > 0:
        longerEnv = e1
        shorterEnv = e2
    else:
        longerEnv = e2
        shorterEnv = e1
    num_bands = longerEnv.shape[1]
    matchSum = correlate(longerEnv[:,0]/sqrt(sum(longerEnv[:,0]**2)),shorterEnv[:,0]/sqrt(sum(shorterEnv[:,0]**2)),mode='valid')
    for i in range(1,num_bands):
        longerBand = longerEnv[:,i]
        denom = sqrt(sum(longerBand**2))
        longerBand = longerBand/denom
        shorterBand = shorterEnv[:,i]
        denom = sqrt(sum(shorterBand**2))
        shorterBand = shorterBand/denom
        temp = correlate(longerBand,shorterBand,mode='valid')
        matchSum += temp
    maxInd = argmax(matchSum)
    matchVal = abs(matchSum[maxInd]/num_bands)
    return -1*log(matchVal)

def dtw_distance(source,target):
    distMat = generate_distance_matrix(source,target)
    return regularDTW(distMat)
    
def generate_distance_matrix(source,target):
    assert(source.shape[1] == target.shape[1])
    sLen = source.shape[0]
    tLen = target.shape[0]
    distMat = zeros((sLen,tLen))
    for i in range(sLen):
        for j in range(tLen):
            distMat[i,j] = euclidean(source[i,:],target[j,:])
    return distMat

def regularDTW(distMat):
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
    
