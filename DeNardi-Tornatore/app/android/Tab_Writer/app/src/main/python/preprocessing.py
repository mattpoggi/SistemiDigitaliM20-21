import numpy as np
import librosa
from scipy.signal import find_peaks


# parameters
sr_downs = 22050
hop_length = 512
n_bins = 192
bins_per_octave = 24

def rms_energy(path):
    data, sr = librosa.load(path, sr = sr_downs, mono = True, dtype='float64')
    
    S = librosa.magphase(librosa.stft(data, window=np.ones, center=False))[0]
    rms = librosa.feature.rms(S=S)

    peaks, _ = find_peaks(rms[0], width=5)

    f = peaks.tolist()
    for i in range(len(f)):
        f[i] += 3

    return f

def audio_CQT(path):
    # Perform the Constant-Q Transform
    data, sr = librosa.load(path, sr = sr_downs, mono = True, dtype='float64')
    data = librosa.util.normalize(data)
    data = librosa.cqt(data, sr = sr_downs, hop_length = hop_length, fmin = None, n_bins = n_bins, bins_per_octave = bins_per_octave)
    CQT = np.abs(data)
    return CQT

def preprocessing_file(path):
    images = []

    cqt = np.swapaxes(audio_CQT(path), 0, 1)
    full_x = np.pad(cqt, [(4,4), (0,0)], mode='constant')

    for n in range(len(cqt)):
        sample_x = np.swapaxes(full_x[n : n + 9], 0, 1)
        images.append(sample_x.astype('float32'))

    images = np.expand_dims(np.array(images), axis=-1)
    
    frames = rms_energy(path)
    return images, frames