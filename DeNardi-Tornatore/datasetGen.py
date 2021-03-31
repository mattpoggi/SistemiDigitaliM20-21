import os
import jams
import numpy as np
import librosa
import math
import datetime
from tensorflow.keras.utils import to_categorical
from scipy.io import wavfile

class datasetGen:

    def __init__(self, path):
        # file path to the GuitarSet dataset
        self.path_data = path
        self.path_audio = self.path_data + "GuitarSet/audio_mono-mic/"
        self.path_anno = self.path_data + "GuitarSet/annotation/"

        # labeling parameters
        self.string_midi_pitches = [40,45,50,55,59,64]
        self.highest_fret = 19
        self.num_classes = self.highest_fret + 2
        
        # array and dict
        self.frame_indices = []
        self.times = []
        self.labels = []
        self.imgs = []
        self.output = {}
        
        # parameters
        self.sr_downs = 22050
        self.hop_length = 512
        self.n_bins = 192
        self.bins_per_octave = 24
        
        self.frameDuration = self.hop_length / self.sr_downs
        
        # save file path
        self.save_path = self.path_data + "dataset/"


    def log(self, text):
        text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " | " + text + "\n"
        with open("log/data.log", "a") as myfile:
            myfile.write(text)
            print(text)
        with open("log/datasetGen.log", "a") as myfile2:
            myfile2.write(text)

    def audio_CQT(self, file_num):
        path = os.path.join(self.path_audio, os.listdir(self.path_audio)[file_num])
        
        # Perform the Constant-Q Transform
        data, sr = librosa.load(path, sr = self.sr_downs, mono = True, dtype='float64')
        data = librosa.util.normalize(data)
        data = librosa.cqt(data, sr = self.sr_downs, hop_length = self.hop_length, fmin = None, n_bins = self.n_bins, bins_per_octave = self.bins_per_octave)
        CQT = np.abs(data)
        return CQT
        
    def correct_numbering(self, n):
        n += 1
        if n < 0 or n > self.highest_fret:
            n = 0
        return n
    
    def categorical(self, label):
        return to_categorical(label, self.num_classes)
    
    def clean_label(self, label):
        label = [self.correct_numbering(n) for n in label]
        return self.categorical(label)
    
    def clean_labels(self, labs):
        return np.array([self.clean_label(label) for label in labs])

    def spacejam(self, file_num):
        path = os.path.join(self.path_anno, os.listdir(self.path_anno)[file_num])
        jam = jams.load(path)
        
        labs = []
        for string_num in range(6):
            anno = jam.annotations["note_midi"][string_num]
            string_label_samples = anno.to_samples(self.times)
            
            # replace midi pitch values with fret numbers
            for i in self.frame_indices:
                if string_label_samples[i] == []:
                    string_label_samples[i] = -1
                else:
                    string_label_samples[i] = int(round(string_label_samples[i][0]) - self.string_midi_pitches[string_num])
            labs.append([string_label_samples])
        
        labs = np.array(labs)
        
        # remove the extra dimension 
        labs = np.squeeze(labs)
        labs = np.swapaxes(labs, 0, 1)
        
        # clean labels
        labs = self.clean_labels(labs)
        return labs

    def get_times(self, n):
        file_audio = os.path.join(self.path_audio, os.listdir(self.path_audio)[n])
        (source_rate, source_sig) = wavfile.read(file_audio)
        duration_seconds = len(source_sig) / float(source_rate)
        totalFrame = math.ceil(duration_seconds / self.frameDuration)
        self.frame_indices = list(range(totalFrame))
        times = librosa.frames_to_time(self.frame_indices, sr = self.sr_downs, hop_length = self.hop_length)
        return times

    def save_data(self, filename):
        np.savez(filename, **self.output)
               
    def get_filename(self, n):
        filename = os.path.basename(os.path.join(self.path_anno, os.listdir(self.path_anno)[n]))
        return filename[:-5]

    def store(self, n, num_frames):
        save_path = self.save_path
        filename = self.get_filename(n)
               
        self.output["imgs"] = self.imgs
        self.output["labels"] = self.labels
        
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        self.save_data(save_path + filename + ".npz")
        self.log("done file n. " + str(n+1) + ": " + filename + ", " + str(num_frames) + " frames")

    def load(self, n):
        self.times = self.get_times(n)

        self.imgs = np.swapaxes(self.audio_CQT(n), 0, 1)
        self.labels = self.spacejam(n)
            
        self.store(n, len(self.times))
        
        self.output = {}
        self.imgs = []
        self.labels = []


def main(args):
    path = args[0]
    n = args[1]
    gen = datasetGen(path)
    gen.log("start file n. " + str(n+1))
    gen.load(n)

if __name__ == "__main__":
    main(args)