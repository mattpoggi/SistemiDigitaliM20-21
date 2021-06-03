def rms_energy(path):
    data, sr = librosa.load(path, sr = sr_downs, mono = True, dtype='float64')

    S = librosa.magphase(librosa.stft(data, window=np.ones, center=False))[0]
    rms = librosa.feature.rms(S=S)

    peaks, _ = find_peaks(rms[0], width=5)

    f = peaks.tolist()
    for i in range(len(f)):
        f[i] += 3

    return f