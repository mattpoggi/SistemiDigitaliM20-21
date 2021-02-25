import numpy as np
import tensorflow as tf
import os
import string
IMAGE_SIZE = 25

GPU = False
NUM_FULLY_CONNECTED_1 = 128

LETTERS = string.ascii_lowercase + '.'+'/'+':'
EOI = '#' # end of input
MAX_SIZE = 25 # max input/output size
MIN_SIZE = 1
ALL_CHAR_CLASSES = LETTERS + EOI # all available classes

# Helper functions
def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1,  name="weights")
    return tf.Variable(initial,validate_shape=False)


def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape,  name="bias")
    return tf.Variable(initial,validate_shape=False)

def dense(out_prec,num_out_prec,num_out_new,name):
	with tf.name_scope(name):
		if GPU:
			with tf.device('/device:GPU:0'):
				W_fc = weight_variable([num_out_prec, num_out_new])
				b_fc = bias_variable([num_out_new])
			
				
				h_fc = tf.nn.relu(tf.matmul(out_prec, W_fc) + b_fc)

				
		else:
			W_fc = weight_variable([num_out_prec, num_out_new])
			b_fc = bias_variable([num_out_new])
				
			h_fc = tf.nn.relu(tf.matmul(out_prec, W_fc) + b_fc)

		
			
		return h_fc
		
def conv2d( x, kernel_shape, bias_shape, strideh=1, stridew = 1, padding='VALID', name='conv2D'):
	''' Block for 2D Convolution '''
	with tf.variable_scope(name):
		if GPU:
			with tf.device('/device:GPU:0'):
				weights = tf.get_variable("weights", kernel_shape, initializer=tf.contrib.layers.xavier_initializer(), dtype=tf.float32)
				biases = tf.get_variable("biases", bias_shape, initializer=tf.truncated_normal_initializer(), dtype=tf.float32)
				output = tf.nn.conv2d(x, weights, strides=[1, strideh, stridew, 1], padding=padding)
				output = tf.nn.bias_add(output, biases)
		else:
			weights = tf.get_variable("weights", kernel_shape, initializer=tf.contrib.layers.xavier_initializer(), dtype=tf.float32)
			biases = tf.get_variable("biases", bias_shape, initializer=tf.truncated_normal_initializer(), dtype=tf.float32)
			output = tf.nn.conv2d(x, weights, strides=[1, strideh, stridew, 1], padding=padding)
			output = tf.nn.bias_add(output, biases)
	return output

def build_net(x_image):

		
	image_flat = tf.reshape(x_image, [-1, IMAGE_SIZE * IMAGE_SIZE], name='reshaping_input')

	layer = dense(image_flat, IMAGE_SIZE * IMAGE_SIZE, NUM_FULLY_CONNECTED_1,name="fc_1")
	
	
	with tf.name_scope("output"):	
		W_fcR = weight_variable([NUM_FULLY_CONNECTED_1, len(ALL_CHAR_CLASSES)])
		b_fcR = bias_variable([len(ALL_CHAR_CLASSES)])
		y_readout = tf.add(tf.matmul(layer, W_fcR),b_fcR, name="output_vector")
		
	
	return y_readout

def main():
	for i in range(15):
		checkpoint_folder = 'char'+str(i)+'/trained_model'
		tflite_folder = 'tflite_quant8'
		path_freeze_script = 'path to freeze graph script'
		path_graph_to_freeze = checkpoint_folder + "/graph_to_freeze.pb"
		path_ch = checkpoint_folder + '/model'
		path_froze = checkpoint_folder + '/output.frozen'
		out_node_names_freezepy = 'char_output/output,char_output/Softmax'
		out_node_names_conv = ['char_output/output','char_output/Softmax']
		tflite_file = tflite_folder + '/tflite_'+str(i)+'_quant8.tflite'


		with tf.name_scope('input'):
			x_image = tf.placeholder(tf.float32, shape=[ 1,IMAGE_SIZE, IMAGE_SIZE, 1], name="x_image")

		y_readout = build_net(x_image)


		with tf.name_scope('char_output'):
			char_output = tf.argmax(y_readout,1,name='output')
			out = tf.nn.softmax(y_readout)
			print(out)
			print(out.shape)


		with tf.Session() as sess:
			g = sess.graph
			gdef = g.as_graph_def()
			tf.train.write_graph(gdef,checkpoint_folder,"graph_to_freeze.pb",False)



		os.system('python '+path_freeze_script+
					'  --input_graph '+ path_graph_to_freeze+
					'  --input_binary True'+
					'  --input_checkpoint ' + path_ch+
					'  --output_graph '+ path_froze+
					'  --output_node_names '+out_node_names_freezepy)


		converter = tf.compat.v1.lite.TFLiteConverter.from_frozen_graph(
			path_froze,
			['input/x_image'],
			out_node_names_conv,
			input_shapes={"input/x_image" : [1, IMAGE_SIZE,IMAGE_SIZE,1]})
			
		#converter.optimizations = [tf.lite.Optimize.DEFAULT]
		#converter.target_spec.supported_types = [tf.lite.constants.FLOAT16]
		converter.optimizations = [tf.lite.Optimize.OPTIMIZE_FOR_SIZE]
		tflite_model = converter.convert()
		open(tflite_file,'wb').write(tflite_model)
		tf.reset_default_graph()
		
if __name__ == "__main__":
	main()