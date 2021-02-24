'''
be sure the python libraries are reachable

generated 9894 out of 9894 images
elapsed time:  7m:43s dll

generated 990 out of 989 images
elapsed time:  0m:50s dll

'''

folder = 'test_dataset_25'

import numpy as np
import cv2
import qrcode
import math
import time
import random
import string
import argparse
import os
from qrcodes import MIN_SIZE, MAX_SIZE,  IMAGE_SIZE_DATASET, VERSION,LEVEL
from dataset_generator import generate_version_err_lev_qr, createDamageMask, applyDamageMaskDll

level_l = qrcode.constants.ERROR_CORRECT_L
level_m = qrcode.constants.ERROR_CORRECT_M
level_q = qrcode.constants.ERROR_CORRECT_Q
level_h = qrcode.constants.ERROR_CORRECT_H
	
qr_levels = [level_l,level_m,level_q, level_h]
	
if __name__ == '__main__':
	GOOGLE_10000_WORDS = 'google-10000-english-no-swears.txt' # update path to the file
	
	
	with open(GOOGLE_10000_WORDS, 'r') as f:
		words10000 = f.readlines()
	
	masks = createDamageMask()
	
	start = time.time()
	i=0
	while (i*10) < len(words10000):
		w = words10000[i*10]
		#trim spaces e prendi i primi 11 char
		label = w.strip()[:MAX_SIZE]
		if len(label) == 0:
			continue
			
		
		i = i + 1
		id_dir = os.path.join(folder,label)
	
		try:
			os.mkdir(id_dir)
		except:
			print('word -- {} -- already generated. Skipping'.format(label))
			continue
		
		#generate_version_err_lev_qr chiede version da 1 in poi
		try:
			qr = generate_version_err_lev_qr(label,level=LEVEL,version=VERSION)	
		except:
			#la stringa non ci sta con questa versione e err-level.
			print("exception")
			sys.exit()
		
	
		qr_damaged_list = applyDamageMaskDll(qr, masks)
	
		for qr_d in range(4):
			img_filename = os.path.join(id_dir, '{}.jpg'.format(qr_d))
			image = np.asarray(qr_damaged_list[qr_d],np.float32)
			image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			cv2.imwrite(img_filename,image)
		qr_filename = os.path.join(id_dir, 'original.jpg')
		image = np.asarray(qr,np.float32)
		cv2.imwrite(qr_filename,image)
		
		label_filename = os.path.join(id_dir,'label.txt')
		file = open(label_filename,'w')
		file.write(label)
		file.close()
		print('generated {} out of {} images'.format(i,len(words10000)//10))
	elapsed_time = time.time() - start
	print('elapsed time: {:2.0f}m:{:2.0f}s'.format(elapsed_time // (60),int(elapsed_time)%60))
		
	