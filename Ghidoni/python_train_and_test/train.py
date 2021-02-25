
'''
be sure the python libraries are reachable

Total network errors type 0: 482 out of 9893
Total network errors type 1: 471 out of 9893
Total network errors type 2: 487 out of 9893

'''
BATCH_SIZE = 1200
MAX_STEPS = 5000
DAMAGES = [0,1,2] 
LR = 5e-4

NUM_FULLY_CONNECTED_1 = 128
	
import argparse
import os
import numpy as np
import signal
import sys


validation_folder = "val_dataset_25"
training_folder = "tr_dataset_25"
SAMPLE_TO_LOAD_TR = 20000
SAMPLE_TO_LOAD_VAL = 1500
MEM_TH_TR = 0.7
MEM_TH_VAL = 0.2

INIT = True


import tensorflow as tf

import cv2
import time


num_val_sample=None
tr_sample_generator = None 
val_sample_generator = None
train_writer = None
test_writer = None

def load_dataset(CHAR_INDEX):
	global tr_sample_generator
	global val_sample_generator
	global num_val_sample
	
	init_tr_dataset = time.time()
	print("loading train dataset....")
	tr_sample_generator = PairGeneratorChar(training_folder,SAMPLE_TO_LOAD_TR,CHAR_INDEX,DAMAGES,mem_th=MEM_TH_TR)
	print("loading train dataset.... done")
	init_tr_elaps = time.time() - init_tr_dataset
	print("init train dataset time:  {:2.0f}m:{:2.0f}s".format(init_tr_elaps // (60),int(init_tr_elaps)%60))

	init_val_dataset = time.time()
	print("loading val dataset....")
	val_sample_generator = PairGeneratorChar(validation_folder,SAMPLE_TO_LOAD_VAL,CHAR_INDEX,DAMAGES,mem_th=MEM_TH_VAL)
	print("loading val dataset.... done")
	init_val_elaps = time.time() - init_val_dataset
	print("init validation dataset time:  {:2.0f}m:{:2.0f}s".format(init_val_elaps // (60),int(init_val_elaps)%60))

	num_val_sample = len(	val_sample_generator.val_indici	)





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

def train(tensorboard_folder,checkpoint_folder ):
	global train_writer 
	global test_writer 
	
	def sigint_handler(signal, frame):
		print('saving all...')
		
		train_writer.close()
		test_writer.close()
		with open('{}/init_index.txt'.format(checkpoint_folder),'w') as f:
			f.write(str(i))
		print('saving complete')
		elaps = time.time() - start_time
		print('elapsed: {:2.0f}m:{:2.0f}s'.format(elaps // (60),int(elaps)%60))
		with open('{}/timing.txt'.format(checkpoint_folder),'w') as f:
			f.write(str(elaps))
		sys.exit(0)
		
	signal.signal(signal.SIGINT, sigint_handler)
	# Inputs
	with tf.name_scope("input"):
		x_image = tf.placeholder(tf.float32, shape=[BATCH_SIZE, IMAGE_SIZE, IMAGE_SIZE, 1], name="x_image")
		y_ = tf.placeholder(tf.float32, shape=[ BATCH_SIZE, len(ALL_CHAR_CLASSES)], name="y_")
		tf.summary.image('x_image', x_image, max_outputs=3)

	with tf.name_scope("dropout_input"):
		keep_prob = tf.placeholder(tf.float32, name="keep_probability")



	y_readout = build_net(x_image)
	char_output = tf.argmax(y_readout,1,name='output')

	# Loss function
	with tf.name_scope("cross_entropy"):
		cross_entropy =	tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(logits=y_readout, labels=y_))
		tf.summary.scalar("cross entropy", cross_entropy)

	# Training
	with tf.name_scope("train_step"):
		train_step = tf.train.AdamOptimizer(learning_rate=LR,name='optimizer').minimize(cross_entropy)

	# Evaluation
	with tf.name_scope("correct_prediction"):
		prediction = tf.equal(tf.argmax(y_readout, 1), tf.argmax(y_, 1))
	with tf.name_scope("accuracy"):
		accuracy = tf.reduce_mean(tf.cast(prediction, tf.float32),name='accuracy')
		tf.summary.scalar("accuracy", accuracy)

	
	saver = tf.train.Saver()
	loader = tf.train.Saver()
	config = tf.ConfigProto(allow_soft_placement=True)

	with tf.Session(config=config) as sess:
		
		# Summaries
		merged = tf.summary.merge_all()

		train_writer = tf.summary.FileWriter("{}/train".format(tensorboard_folder), sess.graph, flush_secs=5)
		test_writer = tf.summary.FileWriter("{}/test".format(tensorboard_folder), flush_secs=5)
		
		if INIT:
			print("init net")
			sess.run(tf.global_variables_initializer())
			sess.run(tf.local_variables_initializer())
			if os.path.exists('{}/init_index.txt'.format(checkpoint_folder)):
				os.remove('{}/init_index.txt'.format(checkpoint_folder))
			init_index=0
		else:
			print("restoring net")
			loader.restore(sess, '{}/model'.format(checkpoint_folder))
			with open('{}/init_index.txt'.format(checkpoint_folder),'r') as f:
				
				init_index = int(f.readline()) + 1

		g = sess.graph
		
		gdef = g.as_graph_def()
		
		tf.train.write_graph(gdef,checkpoint_folder,"graph.pb",False)

		KEEP_PROBABILITY = 1.0
		

		best_accuracy = 0
		start_time = time.time()
		for i in range(init_index,init_index+MAX_STEPS):
			print('iter {} su {}'.format(i,init_index+MAX_STEPS))
			
			#tr_batch_start = time.time()
			batch_images, batch_labels = tr_sample_generator.getTrainBatch(size=BATCH_SIZE)
			#tr_batch_elaps = time.time() - tr_batch_start
			#print("load train batch time:  {:2.0f}m:{:2.0f}s".format(tr_batch_elaps // (60),int(tr_batch_elaps)%60))
			
			
			if len(batch_images) != BATCH_SIZE: 
				tr_sample_generator.reset()
				tr_sample_generator.shuffle()
				batch_images, batch_labels = tr_sample_generator.getTrainBatch(size=BATCH_SIZE)	
			
			if i % 100 == 0:
				accuracy_array = []
				loss_array = []
				for validation_step in range(0,num_val_sample , BATCH_SIZE):
					test_images, test_labels = val_sample_generator.getValidationBatch(size=BATCH_SIZE)
					
					if len(test_images) != BATCH_SIZE:
						break
						
					# Record test set accuracy
					summary, loss, acc = sess.run([merged, cross_entropy, accuracy], feed_dict={
						x_image: test_images,
						y_: test_labels,
						keep_prob: 1.0})
			
					accuracy_array.append(acc)
					loss_array.append(loss)
					
					test_writer.add_summary(summary, i)
					print('validation in progress... {}%'.format(validation_step/num_val_sample*100))
					
				print("Test set accuracy at step {:06}: {:.05}".format(i, np.asarray(accuracy_array).mean()), flush=True)
				tot_accuracy =  np.asarray(accuracy_array).mean()
				tot_loss = np.asarray(loss_array).mean()
				print('validation in progress... 100%')
				print("Test set accuracy at step {:06}: {:.05}".format(i,tot_accuracy), flush=True)
				print("Test set loss at step {:06}: {:.05}".format(i,tot_loss), flush=True)
				
				acc_file = open(os.path.join(tensorboard_folder,"accuracy_loss.txt"),"a")
				acc_file.write("iter {:06} accuracy {:.05} loss {:.05}\n".format(i,tot_accuracy,tot_loss))
				acc_file.close()
				
				val_sample_generator.reset()
				
				
				if tot_accuracy >= best_accuracy:
					print("prev accuracy:",best_accuracy,"best accuracy",tot_accuracy,"saving model")
					best_accuracy = tot_accuracy
					saver.save(sess, '{}/model'.format(checkpoint_folder))
			else:
				if i % 100 == 99:
					# Record execution stats
					run_options = tf.RunOptions(trace_level=tf.RunOptions.FULL_TRACE)
					run_metadata = tf.RunMetadata()
					summary, _ = sess.run([merged, train_step], feed_dict={
										  x_image: batch_images,
										  y_: batch_labels,
										  keep_prob: KEEP_PROBABILITY},
										  options=run_options,
										  run_metadata=run_metadata
										  )
					train_writer.add_run_metadata(run_metadata, "step_{:06}".format(i))
					train_writer.add_summary(summary, i)
				else:
					# Training
					summary, _ = sess.run([merged, train_step], feed_dict={
										  x_image: batch_images,
										  y_: batch_labels,
										  keep_prob: KEEP_PROBABILITY})
					if i % 10 == 0:
						train_writer.add_summary(summary, i)
			

		elaps = time.time() - start_time
		print('elapsed: {:2.0f}m:{:2.0f}s'.format(elaps // (60),int(elaps)%60))
		train_writer.close()
		test_writer.close()
		print('saving index...')
		with open('{}/init_index.txt'.format(checkpoint_folder),'w') as f:
			f.write(str(i))
		with open('{}/timing.txt'.format(checkpoint_folder),'w') as f:
			f.write(str(elaps))
		print('saving index complete')

if __name__ == "__main__":
	for my_index in [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]:
		CHAR_INDEX = my_index
		RUN = 'char' + str(CHAR_INDEX)

		tensorboard_folder = RUN + '/tensorboard'
		checkpoint_folder = RUN +'/trained_model'
		if (os.path.exists(tensorboard_folder) or os.path.exists(checkpoint_folder)) and INIT:
			print("tensorboard or chkp dir already exist")
			sys.exit()
		load_dataset(CHAR_INDEX)	
		train(tensorboard_folder,checkpoint_folder)
		tf.reset_default_graph()
