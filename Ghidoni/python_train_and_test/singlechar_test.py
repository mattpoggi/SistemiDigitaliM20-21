'''
	be sure the python libraries are reachable
'''

	
from qrcodes import  IMAGE_SIZE, make_label_for_position, MAX_SIZE, ALL_CHAR_CLASSES, PairGeneratorChar

import cv2
import numpy as np
from PIL import Image
import tensorflow as tf
import qrcode 

import os

import time



DAMAGES = [0,1,2]
folder = 'test_dataset_25'
SAMPLE_TO_LOAD = 990

from tflite_converter import build_net


times = []
for index in range(MAX_SIZE):
	tf.reset_default_graph()
	CHAR_INDEX = index

	checkpoint_folder = "final/char"+str(CHAR_INDEX)+"/trained_model"


			
	neterr = [0] * 5

	cverr = 0
	pyzerr = 0
	zxing = 0
	ok=[]
	i=0

	print('loading test images...')

	test_sample_generator = PairGeneratorChar(folder,SAMPLE_TO_LOAD,CHAR_INDEX,DAMAGES,0.9)
				

	print('...done')
		

	x_image = tf.placeholder(tf.float32, shape=[ 1,IMAGE_SIZE, IMAGE_SIZE, 1], name="x_image")
	y_ = tf.placeholder(tf.float32, shape=[ 1,len(ALL_CHAR_CLASSES)], name="y_")

	keep_prob = tf.placeholder(tf.float32, name="keep_probability")

	y_readout = build_net(x_image)

	char_output = tf.argmax(y_readout,1,name='output')
	prediction = tf.equal(tf.argmax(y_readout, 1), tf.argmax(y_, 1))
	accuracy = tf.reduce_mean(tf.cast(prediction, tf.float32),name='accuracy')


	loader = tf.train.Saver()

	with tf.Session() as sess:
		loader.restore(sess, '{}/model'.format(checkpoint_folder))
		labels = np.ones((1,len(ALL_CHAR_CLASSES)))
		
		for test_step in range(SAMPLE_TO_LOAD):
			
			images, label_list = test_sample_generator.getTestImageLabel()
				
			for qr_damaged_index in range(len(DAMAGES)):
				
				label = label_list[qr_damaged_index]
				#network 
			
				start_time = time.time()
			
				output,acc = sess.run([char_output,accuracy], feed_dict={x_image:[images[qr_damaged_index]],
																		y_:labels,
																		keep_prob: 1.0})
												
				elaps = time.time() - start_time
				times.append(elaps)
				output = np.asarray(output,dtype=np.int32).squeeze()
				if ALL_CHAR_CLASSES[output] !=  label[CHAR_INDEX]:
					neterr[qr_damaged_index] = neterr[qr_damaged_index] + 1
					
			
			i+=1
			
	
	print("Total network errors type 0:", neterr[0], "out of", len(os.listdir(folder)))
	print("Total network errors type 1:", neterr[1], "out of", len(os.listdir(folder)))
	print("Total network errors type 2:", neterr[2], "out of", len(os.listdir(folder)))

avg = np.array(times).mean()
print("avg time: ",avg)
