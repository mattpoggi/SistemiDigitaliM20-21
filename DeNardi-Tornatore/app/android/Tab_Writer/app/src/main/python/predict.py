import numpy as np
import tensorflow as tf
import json

path_model = "/data/user/0/com.unibo.tab_writer/files/chaquopy/AssetFinder/app/model.tflite"

def myconverter(obj):
	if isinstance(obj, np.integer):
		return int(obj)
	elif isinstance(obj, np.floating):
		return float(obj)
	elif isinstance(obj, np.ndarray):
		return obj.tolist()
	elif isinstance(obj, datetime.datetime):
		return obj.__str__()

def predict_model(images, frames):
	data_json = []

	# Load the TFLite model and allocate tensors.
	interpreter = tf.lite.Interpreter(model_path=path_model)
	interpreter.allocate_tensors()

	# Get input and output tensors.
	input_details = interpreter.get_input_details()			# [{'name': 'conv2d_1_input', 'index': 46, 'shape': array([  1, 192,   9,   1]), 'dtype': <class 'numpy.float32'>, 'quantization': (0.0, 0)}]
	output_details = interpreter.get_output_details()		# [{'name': 'activation_1/concat', 'index': 18, 'shape': array([ 1,  6, 19]), 'dtype': <class 'numpy.float32'>, 'quantization': (0.0, 0)}]

#	input_shape = input_details[0]['shape']
#	print(input_shape) 										# [  1 192   9   1]
#	print(images[0].shape) 									# (192, 9, 1)
#	print(images.shape)										# (15, 192, 9, 1)
	
#	input_data = np.array(images[0], dtype=np.float32)

	x = 0
	for i in range(images.shape[0]):
		if(i in frames):
			input_data = images[i].reshape(1, images.shape[1], images.shape[2], images.shape[3])

			interpreter.set_tensor(input_details[0]['index'], input_data)
			interpreter.invoke()

			output_data = interpreter.get_tensor(output_details[0]['index'])

			b = np.zeros_like(np.squeeze(output_data))
			b[np.arange(len(np.squeeze(output_data))), np.argmax(np.squeeze(output_data),axis=-1)] = 1

			value = np.argmax(b.astype('uint8'), axis=1)
			data_json.append({'tab_x' : x, 'value' : value})
            # [{"tab_x": 0, "value": [4, 0, 0, 0, 0, 0]}, {"tab_x": 1, "value": [6, 0, 0, 0, 0, 0]}, {"tab_x": 2, "value": [7, 0, 0, 0, 0, 0]}]

			x += 1

	return json.dumps(data_json, default=myconverter)