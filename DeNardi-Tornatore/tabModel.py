import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "0" # 0:All, 1:!Info, 2:!Info,!Warning, 3:!Info,!Warning,!Error
import pickle
import numpy as np
import matplotlib.pyplot as plt
import datetime
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten, Reshape, Activation
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Conv1D, Lambda
from tensorflow.keras.optimizers import Adadelta
from tensorflow.keras.callbacks import History
from tensorflow.keras import backend as K
from tensorflow.keras.utils import normalize

class tabModel:

	def __init__(self, batch_size=128, epochs=500, con_win_size = 9, save_path="saved/"):
		self.batch_size = batch_size
		self.epochs = epochs
		self.con_win_size = con_win_size
		self.save_path = save_path
		self.input_shape = (192, self.con_win_size, 1)
		self.num_classes = 21
		self.num_strings = 6
		self.feature_sets_file = "all_targets_sets.npz"
		self.model_filename = "model.h5"
		self.X_val = []
		self.X_train = []
		self.y_val = []
		self.y_train = []


	def log(self, text):
		text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " | " + text + "\n"
		with open("log/data.log", "a") as myfile:
			if "stampamodello" in text:
				self.model.summary(print_fn=lambda x: myfile.write(x + '\n'))
			else:
				myfile.write(text)
				print(text)
		with open("log/tabModel.log", "a") as myfile2:
			if "stampamodello" in text:
				self.model.summary(print_fn=lambda x: myfile2.write(x + '\n'))
			else:
				myfile2.write(text)

	def load_data(self):
		# Load features sets
		features_sets = np.load(os.path.join("data/", self.feature_sets_file))

		# Assign feature sets
		X_train = features_sets['X_train']
		X_val = features_sets['X_val']

		self.y_train = features_sets['y_train']
		self.y_val = features_sets['y_val']

		# CNN for TF expects (batch, height, width, channels)
		# So we reshape the input tensors with a "color" channel of 1
		self.X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], X_train.shape[2], 1)
		self.X_val = X_val.reshape(X_val.shape[0], X_val.shape[1], X_val.shape[2], 1)

		self.log("X Train set size: " + str(self.X_train.shape))
		self.log("X Validation set size: " + str(self.X_val.shape))
		self.log("y Train set size: " + str(self.y_train.shape))
		self.log("y Validation set size: " + str(self.y_val.shape))

	def softmax_by_string(self, t):
		sh = K.shape(t)
		string_sm = []
		for i in range(self.num_strings):
			string_sm.append(K.expand_dims(K.softmax(t[:,i,:]), axis=1))
		return K.concatenate(string_sm, axis=1)

	def catcross_by_string(self, target, output):
		loss = 0
		for i in range(self.num_strings):
			loss += K.categorical_crossentropy(target[:,i,:], output[:,i,:])
		return loss

	def avg_acc(self, y_true, y_pred):
		return K.mean(K.equal(K.argmax(y_true, axis=-1), K.argmax(y_pred, axis=-1)))

	def build_model(self):
		model = Sequential()
		model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=self.input_shape))
		model.add(Conv2D(64, (3, 3), activation='relu'))
		model.add(Conv2D(64, (3, 3), activation='relu'))
		model.add(MaxPooling2D(pool_size=(2, 2)))
		model.add(Dropout(0.25))   
		model.add(Flatten())
		model.add(Dense(128, activation='relu'))
		model.add(Dropout(0.5))
		model.add(Dense(self.num_classes * self.num_strings)) # no activation
		model.add(Reshape((self.num_strings, self.num_classes)))
		model.add(Activation(self.softmax_by_string))

		model.compile(loss=self.catcross_by_string, optimizer=Adadelta(), metrics=[self.avg_acc])

		self.model = model

	def train(self):
		self.hist = History()
		self.model.fit(self.X_train, self.y_train, batch_size=self.batch_size, epochs=self.epochs, verbose=1, validation_data=(self.X_val, self.y_val), callbacks=[self.hist])

	def plot(self):
		acc = self.hist.history['avg_acc']
		val_acc = self.hist.history['val_avg_acc']
		loss = self.hist.history['loss']
		val_loss = self.hist.history['val_loss']

		epochs_range = range(1, len(acc) + 1)

		plt.figure(figsize=(20, 20))

		plt.subplot(2, 2, 1)
		plt.plot(epochs_range, acc, label='Training Accuracy')
		plt.plot(epochs_range, val_acc, label='Validation Accuracy')
		plt.legend(loc='lower right')
		plt.title('Training and Validation Accuracy')
		plt.ylabel('Accuracy')
		plt.xlabel('Epoch')

		plt.subplot(2, 2, 2)
		plt.plot(epochs_range, loss, label='Training Loss')
		plt.plot(epochs_range, val_loss, label='Validation Loss')
		plt.legend(loc='upper right')
		plt.title('Training and Validation Loss')
		plt.ylabel('Accuracy')
		plt.xlabel('Epoch')

		plt.savefig(self.save_path + "plot.png")

	def save_model(self):
		self.model.save(self.save_path + self.model_filename)


def main():
	tabmodel = tabModel()
	tabmodel.log("Start tabModel")

	tabmodel.log("load data...")
	tabmodel.load_data()

	tabmodel.log("building model...")
	tabmodel.build_model()
	tabmodel.log("stampamodello")
	
	tabmodel.log("training...")
	tabmodel.train()

	tabmodel.log("plot...")
	tabmodel.plot()

	tabmodel.log("save model...")
	tabmodel.save_model()

	tabmodel.log("End tabModel")

if __name__ ==  '__main__':
	main()
