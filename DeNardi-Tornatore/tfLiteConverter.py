from tensorflow import lite
from tensorflow.keras import backend as K
from tensorflow.keras.models import load_model
import datetime

class tfLiteConverter:

	def __init__(self, save_path="saved/"):
		self.save_path = save_path
		self.num_strings = 6
		self.model_filename = "model.h5"
		self.tflite_filename = "model.tflite"


	def log(self, text):
		text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " | " + text + "\n"
		with open("log/data.log", "a") as myfile:
			myfile.write(text)
			print(text)
		with open("log/tfLiteConverter.log", "a") as myfile2:
			myfile2.write(text)

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

	def convert_tflite(self):
		model = load_model(self.save_path + self.model_filename, custom_objects={'softmax_by_string': self.softmax_by_string, 'avg_acc': self.avg_acc, 'catcross_by_string': self.catcross_by_string})
		converter = lite.TFLiteConverter.from_keras_model(model)
		tflite_model = converter.convert()
		open(self.save_path + self.tflite_filename, "wb").write(tflite_model)


def main():
	tfliteconverter = tfLiteConverter()
	tfliteconverter.log("Start tfLiteConverter")

	tfliteconverter.log("convert tflite...")
	tfliteconverter.convert_tflite()

	tfliteconverter.log("End tfLiteConverter")

if __name__ ==  '__main__':
	main()