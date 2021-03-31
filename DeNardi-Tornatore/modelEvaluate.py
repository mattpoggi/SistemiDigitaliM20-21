import os
import numpy as np
import datetime
import random
from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K


class modelEvaluate:

	def __init__(self, save_path="saved/"):
		self.save_path = save_path
		self.num_strings = 6
		self.feature_sets_file = "all_targets_sets.npz"
		self.model_filename = "model.h5"
		self.X_test = []
		self.y_test = []


	def log(self, text):
		text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " | " + text + "\n"
		with open("log/data.log", "a") as myfile:
			myfile.write(text)
			print(text)
		with open("log/modelEvaluate.log", "a") as myfile2:
			myfile2.write(text)

	def load_data(self):
		# Load features sets
		features_sets = np.load(os.path.join("data/", self.feature_sets_file))

		# Assign feature sets
		X_test = features_sets['X_test']

		self.y_test = features_sets['y_test']

		# CNN for TF expects (batch, height, width, channels)
		# So we reshape the input tensors with a "color" channel of 1
		self.X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], X_test.shape[2], 1)

		self.log("X Test set size: " + str(self.X_test.shape))
		self.log("y Test set size: " + str(self.y_test.shape))

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

	def load_model(self):
		self.model = load_model(self.save_path + self.model_filename, custom_objects={'softmax_by_string': self.softmax_by_string, 'avg_acc': self.avg_acc, 'catcross_by_string': self.catcross_by_string})

	def test(self):
		# TEST: Load model and run it against test set
		r = random.randint(0, len(self.X_test))
		for i in range (r, r + 10):
			print("Answer:", self.y_test[i], "Prediction:", self.model.predict(np.expand_dims(self.X_test[i], 0)))

		self.y_pred = self.model.predict(self.X_test)

	def evaluate(self):
		# Evaluate model with test set
		results = self.model.evaluate(x=self.X_test, y=self.y_test)
		self.log("Test loss, Test acc: " + str(results))

	def save_predictions(self):
		np.savez(self.save_path + "predictions.npz", y_pred=self.y_pred, y_test=self.y_test)

def main():
	modelevaluate = modelEvaluate()
	modelevaluate.log("Start modelEvaluate")

	modelevaluate.load_data()
	modelevaluate.load_model()

	modelevaluate.log("test model...")
	modelevaluate.test()

	modelevaluate.log("evaluate model...")
	modelevaluate.evaluate()

	modelevaluate.log("save predictions...")
	modelevaluate.save_predictions()

	modelevaluate.log("End modelEvaluate")

if __name__ ==  '__main__':
	main()