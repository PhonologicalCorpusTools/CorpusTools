from numpy import (array, zeros, floor, sqrt, dot, arange, hanning,
                    sin, pi, linspace, log10, round, maximum, minimum,
                    sum, cos, spacing, diag, correlate, argmax)
from numpy.fft import fft

from scipy.signal import filtfilt, butter, hilbert, resample, lfilter
from scipy.io import wavfile

    
def preproc(path,sr=None,alpha=0.97):
    oldsr,sig = wavfile.read(path)
    
    if sr is not None and sr != oldsr:
        t = len(sig)/oldsr
        numsamp = t * sr
        proc = resample(sig,numsamp)
    else:
        proc = sig
    proc = lfilter([1., -alpha],1,proc)
    return sr,proc

def filter_bank(nfft,nfilt,minFreq,maxFreq,sr):

    minMel = freqToMel(minFreq)
    maxMel = freqToMel(maxFreq)
    melPoints = linspace(minMel,maxMel,nfilt+2)
    binfreqs = melToFreq(melPoints)
    bins = round((nfft-1)*binfreqs/sr)

    fftfreqs = arange(int(nfft/2))/nfft * sr

    fbank = zeros([nfilt,int(nfft/2)])
    for i in range(nfilt):
        fs = binfreqs[i+arange(3)]
        fs = fs[1] + (fs - fs[1])
        loslope = (fftfreqs - fs[0])/(fs[1] - fs[0])
        highslope = (fs[2] - fftfreqs)/(fs[2] - fs[1])
        fbank[i,:] = maximum(zeros(loslope.shape),minimum(loslope,highslope))
    fbank = fbank / max(sum(fbank,axis=1))
    return fbank.transpose()

def freqToMel(freq):
    return 2595 * log10(1+freq/700.0)

def melToFreq(mel):
    return 700*(10**(mel/2595.0)-1)


def dct_spectrum(spec):
    ncep=spec.shape[0]
    dctm = zeros((ncep,ncep))
    for i in range(ncep):
        dctm[i,:] = cos(i * arange(1,2*ncep,2)/(2*ncep) * pi) * sqrt(2/ncep)
    dctm = dctm * 0.230258509299405
    cep =  dot(dctm , (10*log10(spec + spacing(1))))
    return cep

def to_mfcc(filename, freq_lims,num_coeffs,win_len,time_step,num_filters = 26, use_power = False):
    #HTK style, interpreted from RastaMat
    sr, proc = preproc(filename,alpha=0.97)
    
    minHz = freq_lims[0]
    maxHz = freq_lims[1]
    
    L = 22
    n = arange(num_filters)
    lift = 1+ (L/2)*sin(pi*n/L)
    lift = diag(lift)
    
    nperseg = int(win_len*sr)
    noverlap = int(time_step*sr)
    window = hanning(nperseg+2)[1:nperseg+1]
    
    filterbank = filter_bank(nperseg,num_filters,minHz,maxHz,sr)
    step = nperseg - noverlap
    indices = arange(0, proc.shape[-1]-nperseg+1, step)
    num_frames = len(indices)
    
    mfccs = zeros((num_frames,num_coeffs))
    for k,ind in enumerate(indices):
        seg = proc[ind:ind+nperseg] * window
        complexSpectrum = fft(seg)
        powerishSpectrum = abs(complexSpectrum[:int(nperseg/2)])
        filteredSpectrum = dot(powerishSpectrum, filterbank)**2
        dctSpectrum = dct_spectrum(filteredSpectrum)
        dctSpectrum = dot(dctSpectrum , lift)
        if not use_power:
            dctSpectrum = dctSpectrum[1:]
        mfccs[k,:] = dctSpectrum[:num_coeffs]
    return mfccs
    

def to_envelopes(path,num_bands,freq_lims,window_length=None,time_step=None):
    sr, proc = preproc(path,alpha=0.97)
    proc = proc/sqrt(mean(proc**2))*0.03;
    bandLo = [ freq_lims[0]*exp(log(freq_lims[1]/freq_lims[0])/num_bands)**x for x in range(num_bands)]
    bandHi = [ freq_lims[0]*exp(log(freq_lims[1]/freq_lims[0])/num_bands)**(x+1) for x in range(num_bands)]
    if window_length is not None and time_step is not None:
        use_windows = True
        nperseg = int(window_length*sr)
        noverlap = int(time_step*sr)
        window = hanning(nperseg+2)[1:nperseg+1]
        step = nperseg - noverlap
        indices = arange(0, proc.shape[-1]-nperseg+1, step)
        num_frames = len(indices)
        envelopes = zeros((num_bands,num_frames))
    else:
        use_windows=False
        sr_env = 120
        t = len(proc)/sr
        numsamp = ceil(t * sr_env)
        envelopes = []
    for i in range(num_bands):
        b, a = butter(2,(bandLo[i]/(sr/2),bandHi[i]/(sr/2)), btype = 'bandpass')
        env = filtfilt(b,a,proc)
        env = abs(hilbert(env))
        if use_windows:
            window_sums = []
            for k,ind in enumerate(indices):
                seg = env[ind:ind+nperseg] * window
                window_sums.append(sum(seg))
            envelopes[i,:] = window_sums
        else:
            env = resample(env,numsamp)
            envelopes.append(env)
    return array(envelopes).T

