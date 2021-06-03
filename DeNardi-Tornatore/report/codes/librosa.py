# parameters
self.sr_downs = 22050
self.hop_length = 512
self.n_bins = 192
self.bins_per_octave = 24

def audio_CQT(self, file_num):
    path = os.path.join(self.path_audio, os.listdir(self.path_audio)[file_num])
    
    # Perform the Constant-Q Transform
    data, sr = librosa.load(path, sr = self.sr_downs, mono = True, dtype='float64')
    data = librosa.util.normalize(data)
    data = librosa.cqt(data, 
                       sr = self.sr_downs, 
                       hop_length = self.hop_length, 
                       fmin = None, 
                       n_bins = self.n_bins, 
                       bins_per_octave = self.bins_per_octave)
    CQT = np.abs(data)
    return CQT