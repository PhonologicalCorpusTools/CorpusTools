from numpy import (array, zeros, floor, sqrt, dot, arange, hanning,
                    sin, pi, linspace, log10, round, maximum, minimum,
                    sum, cos, spacing, diag, correlate, argmax, mean, exp,
                    log, ceil)
from numpy.fft import fft

from scipy.signal import filtfilt, butter, hilbert, resample, lfilter
from scipy.io import wavfile


def preproc(path,sr=None,alpha=0.97):
    """Preprocess a .wav file for later processing.

    Parameters
    ----------
    path : str
        Full path to .wav file to load.
    sr : int, optional
        Sampling rate to resample at, if specified.
    alpha : float, optional
        Alpha for preemphasis, defaults to 0.97.

    Returns
    -------
    int
        Sampling rate.
    array
        Processed PCM.

    """
    oldsr,sig = wavfile.read(path)

    try:
        sig = sig[:,0]
    except IndexError:
        pass

    if sr is not None and sr != oldsr:
        t = len(sig)/oldsr
        numsamp = t * sr
        proc = resample(sig,numsamp)
    else:
        sr = oldsr
        proc = sig
    if alpha != 0:
        proc = lfilter([1., -alpha],1,proc)
    return sr,proc

def to_powerspec(x, sr, win_len, time_step):
    nperseg = int(win_len*sr)
    nperstep = int(time_step*sr)
    nfft = int(2**(ceil(log(nperseg)/log(2))))
    window = hanning(nperseg+2)[1:nperseg+1]

    indices = arange(int(nperseg/2), x.shape[0] - int(nperseg/2) + 1, nperstep)
    num_frames = len(indices)

    pspec = zeros((num_frames,int(nfft/2)+1))
    for i in range(num_frames):
        X = x[indices[i]-int(nperseg/2):indices[i]+int(nperseg/2)]
        X = X * window
        fx = fft(X, n = nfft)
        power = abs(fx[:int(nfft/2)+1])**2
        pspec[i,:] = power
    return pspec

def filter_bank(nfft,nfilt,minFreq,maxFreq,sr):
    """Construct a mel-frequency filter bank.

    Parameters
    ----------
    nfft : int
        Number of points in the FFT.
    nfilt : int
        Number of mel filters.
    minFreq : int
        Minimum frequency in Hertz.
    maxFreq : int
        Maximum frequency in Hertz.
    sr : int
        Sampling rate of the sampled waveform.

    Returns
    -------
    array
        Filter bank to multiply an FFT spectrum to create a mel-frequency
        spectrum.

    """

    minMel = freqToMel(minFreq)
    maxMel = freqToMel(maxFreq)
    melPoints = linspace(minMel,maxMel,nfilt+2)
    binfreqs = melToFreq(melPoints)
    bins = round((nfft-1)*binfreqs/sr)

    fftfreqs = arange(int(nfft/2+1))/nfft * sr

    fbank = zeros((nfilt,int(nfft/2 +1)))
    for i in range(nfilt):
        fs = binfreqs[i+arange(3)]
        fs = fs[1] + (fs - fs[1])
        loslope = (fftfreqs - fs[0])/(fs[1] - fs[0])
        highslope = (fs[2] - fftfreqs)/(fs[2] - fs[1])
        fbank[i,:] = maximum(zeros(loslope.shape),minimum(loslope,highslope))
    #fbank = fbank / max(sum(fbank,axis=1))
    return fbank.transpose()

def freqToMel(freq):
    """Convert a value in Hertz to a value in mel.

    Parameters
    ----------
    freq : numeric
        Frequency value in Hertz to convert.

    Returns
    -------
    float
        Frequency value in mel.

    """

    return 2595 * log10(1+freq/700.0)

def melToFreq(mel):
    """Convert a value in mel to a value in Hertz.

    Parameters
    ----------
    mel : numeric
        Frequency value in mel to convert.

    Returns
    -------
    float
        Frequency value in Hertz.

    """
    return 700*(10**(mel/2595.0)-1)


def dct_spectrum(spec):
    """Convert a spectrum into a cepstrum via type-III DCT (following HTK).

    Parameters
    ----------
    spec : array
        Spectrum to perform a DCT on.

    Returns
    -------
    array
        Cepstrum of the input spectrum.

    """
    ncep=spec.shape[0]
    dctm = zeros((ncep,ncep))
    for i in range(ncep):
        dctm[i,:] = cos(i * arange(1,2*ncep,2)/(2*ncep) * pi) * sqrt(2/ncep)
    dctm = dctm * 0.230258509299405
    cep =  dot(dctm , (10*log10(spec + spacing(1))))
    return cep

def to_mfcc(filename, freq_lims,num_coeffs,win_len,time_step,num_filters = 26, use_power = False,debug=False):
    """Generate MFCCs in the style of HTK from a full path to a .wav file.

    Parameters
    ----------
    filename : str
        Full path to .wav file to process.
    freq_lims : tuple
        Minimum and maximum frequencies in Hertz to use.
    num_coeffs : int
        Number of coefficients of the cepstrum to return.
    win_len : float
        Window length in seconds to use for FFT.
    time_step : float
        Time step in seconds for windowing.
    num_filters : int
        Number of mel filters to use in the filter bank, defaults to 26.
    use_power : bool
        If true, use the first coefficient of the cepstrum, which is power
        based.  Defaults to false.

    Returns
    -------
    2D array
        MFCCs for each frame.  The first dimension is the time in frames,
        the second dimension is the MFCC values.

    """
    sr, proc = preproc(filename,alpha=0.97)

    minHz = freq_lims[0]
    maxHz = freq_lims[1]

    L = 22
    n = arange(num_filters)
    lift = 1+ (L/2)*sin(pi*n/L)
    lift = diag(lift)

    pspec = to_powerspec(proc,sr,win_len,time_step)

    filterbank = filter_bank((pspec.shape[1]-1) * 2,num_filters,minHz,maxHz,sr)


    num_frames = pspec.shape[0]

    mfccs = zeros((num_frames,num_coeffs))
    aspec =zeros((num_frames,num_filters))
    for k in range(num_frames):
        filteredSpectrum = dot(sqrt(pspec[k,:]), filterbank)**2
        aspec[k,:] = filteredSpectrum
        dctSpectrum = dct_spectrum(filteredSpectrum)
        dctSpectrum = dot(dctSpectrum , lift)
        if not use_power:
            dctSpectrum = dctSpectrum[1:]
        mfccs[k,:] = dctSpectrum[:num_coeffs]
    if debug:
        return mfccs,pspec,aspec
    return mfccs


def to_envelopes(path,num_bands,freq_lims,downsample=True):
    """Generate amplitude envelopes from a full path to a .wav, following
    Lewandowski (2012).

    Parameters
    ----------
    filename : str
        Full path to .wav file to process.
    num_bands : int
        Number of frequency bands to use.
    freq_lims : tuple
        Minimum and maximum frequencies in Hertz to use.
    downsample : bool
        If true, envelopes will be downsampled to 120 Hz

    Returns
    -------
    2D array
        Amplitude envelopes over time
    """
    sr, proc = preproc(path,alpha=0.97)

    #proc = proc / 32768 #hack!! for 16-bit pcm
    proc = proc/sqrt(mean(proc**2))*0.03;
    bandLo = [ freq_lims[0]*exp(log(freq_lims[1]/freq_lims[0])/num_bands)**x for x in range(num_bands)]
    bandHi = [ freq_lims[0]*exp(log(freq_lims[1]/freq_lims[0])/num_bands)**(x+1) for x in range(num_bands)]

    envelopes = []
    for i in range(num_bands):
        b, a = butter(2,(bandLo[i]/(sr/2),bandHi[i]/(sr/2)), btype = 'bandpass')
        env = filtfilt(b,a,proc)
        env = abs(hilbert(env))
        if downsample:
            env = resample(env,int(ceil(len(env)/int(ceil(sr/120)))))
            #env = decimate(env,int(ceil(sr/120)))
        envelopes.append(env)
    return array(envelopes).T

