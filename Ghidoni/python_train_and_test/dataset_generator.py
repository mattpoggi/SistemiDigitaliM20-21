'''
be sure the python libraries are reachable

python dataset_generator.py --folder tr_dataset --num_images 100

qr capacity  https://www.qrcode.com/en/about/version.html

qr code:4999 | elapsed time:  4m: 0s dll 25

qr code:19999 | elapsed time: 13m:50s dll 25

qr code:19999 | elapsed time: 14m:25s python 25

qr damaging time:  0m: 0s
qr code:19999 | elapsed time: 65m:44s dll 700

qr damaging time:  0m: 5s
qr code:1757 | elapsed time: 181m:42s python 700

'''
from PIL import Image, ImageDraw
import numpy as np
#from skimage.util import random_noise
import cv2
import qrcode
import math
import time
import random
import string
import argparse
import os
import ctypes
import copy
from ctypes import *
from qrcodes import MIN_SIZE, MAX_SIZE, LETTERS, IMAGE_SIZE_DATASET, VERSION, PADDING_SIZE, LEVEL,NUM_MASKS_PER_CORNER



level_l = qrcode.constants.ERROR_CORRECT_L
level_m = qrcode.constants.ERROR_CORRECT_M
level_q = qrcode.constants.ERROR_CORRECT_Q
level_h = qrcode.constants.ERROR_CORRECT_H

mask_lib = ctypes.WinDLL('absolute path to maskWhite.dll')
mask_fun = mask_lib.applyDamageMask

def createDamageMask():
	masks = [None]*2
	masks[0] = [None] *2
	masks[1] = [None] * 2
	
	quarto = IMAGE_SIZE_DATASET//4
	terzo = IMAGE_SIZE_DATASET//3
	
	print("preloading masks....")
	for x in 0,1:
		for y in 0,1:
			masks[x][y] = []
			centre = [x*(IMAGE_SIZE_DATASET-1),y*(IMAGE_SIZE_DATASET-1)]
			for mask in range(NUM_MASKS_PER_CORNER):

				w,h = np.random.randint(low=quarto, high=terzo+1,size=2, dtype=int)
				im = Image.new('RGB', (IMAGE_SIZE_DATASET, IMAGE_SIZE_DATASET), (255,255, 255))
				square = ImageDraw.Draw(im)

				coorx_sx = centre[0]-w
				coory_sx = centre[1]-h
				coorx_dx = centre[0]+w
				coory_dx = centre[1]+h
				square.rectangle((coorx_sx,coory_sx ,coorx_dx,coory_dx), fill=(0, 0, 0) )

				width, height, channels = im.size[1], im.size[0], 3
				masks[x][y].append(np.asarray(im.getdata(),dtype=np.int32).reshape((width, height, channels)))
	print("mask loaded")		
	return masks

def applyDamageMaskPython(qr, masks):
	qr_damaged_list = []
	for qr_d in range(4):
		qr_damaged_list.append(np.zeros((IMAGE_SIZE_DATASET,IMAGE_SIZE_DATASET,3),dtype=np.uint32))

	height, width = np.shape(qr)
	for mask_x in 0,1:
		for mask_y in 0,1:
			mask = random.choice(masks[mask_x][mask_y])
			for i in range(height):
				for j in range(width):
					if mask[i][j][0] == 0 and mask[i][j][1]==0 and mask[i][j][2]==0:
						qr_damaged_list[mask_x*2+mask_y][i][j] = 255
					else: 
						qr_damaged_list[mask_x*2+mask_y][i,j,0] = qr[i,j]
						qr_damaged_list[mask_x*2+mask_y][i,j,1] = qr[i,j]
						qr_damaged_list[mask_x*2+mask_y][i,j,2] = qr[i,j]

	
	return qr_damaged_list

def applyDamageMaskDll(qr, masks):
	qr_damaged_list = []
	for qr_d in range(4):
		qr_damaged_list.append(np.zeros((IMAGE_SIZE_DATASET,IMAGE_SIZE_DATASET,3),dtype=np.int32))
	
	height, width = np.shape(qr)
	for mask_x in 0,1:
		for mask_y in 0,1:
			mask = random.choice(masks[mask_x][mask_y])
			qr_damaged = np.zeros((height,width,3),dtype=np.int32)
			qr_p = c_void_p(qr.ctypes.data)
			mask_p = c_void_p(mask.ctypes.data)
			res_p = c_void_p(qr_damaged.ctypes.data)
			h_p = c_int(height)
			w_p = c_int(width)
		
			mask_fun(qr_p, mask_p, res_p, h_p, w_p)
			qr_damaged_list[mask_x*2+mask_y] =  qr_damaged
	
		
	return qr_damaged_list

def generate_version_err_lev_qr(rand_string,level,version):
	
	module_per_side = 21+4*(version-1)+PADDING_SIZE*2
	box_size = IMAGE_SIZE_DATASET // module_per_side
	
	qr = qrcode.QRCode(
			version=version,  
			error_correction=level,  
			box_size=box_size,  
			border=PADDING_SIZE,  
		)
	
	qr.add_data(rand_string)

	# fit=False throw exception if the string cannot fit into qr
	qr.make(fit=False) 
		
	
	qr = qr.make_image(fill_color="black", back_color="white").getdata()
	qr = np.reshape(qr,(module_per_side*box_size,module_per_side*box_size))
	
	
	qr = np.asarray(qr,dtype=np.int32)
	
	return qr
	

def generateQRDamaged():

	qr_levels = {'level_l':level_l, 'level_m':level_m,'level_q':level_q, 'level_h':level_h}
	
	i=0
	for f in os.listdir(args.folder):
		i = i + 1
	
	masks = createDamageMask()
	start = time.time()
	for iter in range(i,i+args.num_images):	
		size = random.randint(MIN_SIZE, MAX_SIZE)
		rand_string = "".join(random.choice(LETTERS) for _ in range(size))
		
		main_dirname = os.path.join(args.folder,'{}'.format(iter))
		os.mkdir(main_dirname)
		label_filename = os.path.join(main_dirname,'label.txt')
		f=open(label_filename,'w')
		f.write(rand_string)
		f.close()
		
		
		try:
			
			#start_qr_time = time.time()
			qr = generate_version_err_lev_qr(rand_string,level=LEVEL,version=VERSION)
			#qr_time = time.time() - start_qr_time
			#print('qr creation time: {:2.0f}m:{:2.0f}s'.format(qr_time // (60),int(qr_time)%60))
		except Exception as e:
			print(e)
			exit()
				
		start_damaging_time = time.time()
		qr_damaged_list = applyDamageMaskDll(qr, masks)
		damaging_time = time.time() - start_damaging_time
		print('qr damaging time: {:2.0f}m:{:2.0f}s'.format(damaging_time // (60),int(damaging_time)%60))
		
		#start_saving_time = time.time()
		for qr_d in range(4):
			img_filename = os.path.join(main_dirname, '{}.jpg'.format(qr_d))
			image = np.asarray(qr_damaged_list[qr_d],np.float32)
			image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			cv2.imwrite(img_filename,image)
		qr_filename = os.path.join(main_dirname, 'original.jpg')
		image = np.asarray(qr,np.float32)
		cv2.imwrite(qr_filename,image)
		#saving_time = time.time() - start_saving_time
		#print('saving  time: {:2.0f}m:{:2.0f}s'.format(saving_time // (60),int(saving_time)%60))
		elapsed_time = time.time() - start
		print('qr code:{} | elapsed time: {:2.0f}m:{:2.0f}s'.format(iter-i,elapsed_time // (60),int(elapsed_time)%60))
		
	
	
	print('done')

	
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Create damaged qr codes')
	parser.add_argument('--folder', type=str, required=True, help='folder to put into qr codes')
	parser.add_argument('--num_images', type=int,required=True, help='number of string. qr codes will be version*4*4')

	args = parser.parse_args()
	try:
		generateQRDamaged()
	except Exception as e:
		print(e)
