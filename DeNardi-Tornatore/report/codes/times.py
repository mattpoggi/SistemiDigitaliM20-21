# parameters
self.sr_downs = 22050
self.hop_length = 512
self.n_bins = 192
self.bins_per_octave = 24

self.frameDuration = self.hop_length / self.sr_downs

def get_times(self, n):
    file_audio = os.path.join(self.path_audio, os.listdir(self.path_audio)[n])
    (source_rate, source_sig) = wavfile.read(file_audio)
    duration_seconds = len(source_sig) / float(source_rate)
    totalFrame = math.ceil(duration_seconds / self.frameDuration)
    self.frame_indices = list(range(totalFrame))
    times = librosa.frames_to_time(self.frame_indices, sr = self.sr_downs, hop_length = self.hop_length)
    return times