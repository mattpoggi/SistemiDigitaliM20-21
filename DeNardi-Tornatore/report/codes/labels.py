# labeling parameters
self.string_midi_pitches = [40,45,50,55,59,64]
self.highest_fret = 19
self.num_classes = self.highest_fret + 2

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