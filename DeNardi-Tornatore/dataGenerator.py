import os
import numpy as np
import matplotlib.pyplot as plt
import random
import pickle
import datetime
from tensorflow.keras.utils import  normalize

class dataGenerator():

    def __init__(self, data_path="data/dataset/", n_file=360, con_win_size=9):
        self.data_path = data_path
        self.n_file = n_file
        self.con_win_size = con_win_size
        self.halfwin = con_win_size // 2
        self.feature_sets_file = "data/all_targets_sets.npz"
        self.training_data = []
        self.X_val = []
        self.X_test = []
        self.X_train = []
        self.y_val = []
        self.y_test = []
        self.y_train = []

 
    def log(self, text):
        text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " | " + text + "\n"
        with open("log/data.log", "a") as myfile:
            myfile.write(text)
            print(text)
        with open("log/dataGenerator.log", "a") as myfile2:
            myfile2.write(text)

    def load_data(self):
        for i in range(self.n_file):
            self.log("n." + str(i+1))
            inp = np.load(os.path.join(self.data_path, os.listdir(self.data_path)[i]))

            full_x = np.pad(inp["imgs"], [(self.halfwin,self.halfwin), (0,0)], mode='constant')

            for frame_idx in range(len(inp['imgs'])):
                # load a context window centered around the frame index
                sample_x = np.swapaxes(full_x[frame_idx : frame_idx + self.con_win_size], 0, 1)
                self.training_data.append((sample_x.astype('float64'), inp['labels'][frame_idx][::-1].astype('float64')))

    def prepare_data(self, data):
        inp = []
        out = []

        for imgs, labels in data:
            inp.append(imgs)
            out.append(labels)
        return inp, out

    def partition_data(self):
        # Randomize training set
        random.shuffle(self.training_data)

        X_train, y_train = self.prepare_data(self.training_data)

        # Calculate validation and test set sizes
        val_set_size = int(len(self.training_data) * 0.1)
        test_set_size = int(len(self.training_data) * 0.1)

        # Break x apart into train, validation, and test sets
        self.X_val = X_train[:val_set_size]
        self.X_test = X_train[val_set_size:(val_set_size + test_set_size)]
        self.X_train = X_train[(val_set_size + test_set_size):]

        # Break y apart into train, validation, and test sets
        self.y_val = y_train[:val_set_size]
        self.y_test = y_train[val_set_size:(val_set_size + test_set_size)]
        self.y_train = y_train[(val_set_size + test_set_size):]

        self.log("Train set size: " + str(len(self.X_train)))
        self.log("Validation set size: " + str(len(self.X_val)))
        self.log("Test set size: " + str(len(self.X_test)))

    def save_data(self):
        # Save features and truth vector (y) sets to disk
        np.savez(self.feature_sets_file, X_train=self.X_train, y_train=self.y_train, X_val=self.X_val, y_val=self.y_val, X_test=self.X_test, y_test=self.y_test)


def main():
    datagenerator = dataGenerator()
    datagenerator.log("Start dataGenerator")

    datagenerator.log("load data...")
    datagenerator.load_data()

    datagenerator.log("partition data...")
    datagenerator.partition_data()

    datagenerator.log("save data...")
    datagenerator.save_data()

    datagenerator.log("End dataGenerator")

if __name__ ==  '__main__':
    main()

    
    