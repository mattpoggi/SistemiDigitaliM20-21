import multiprocessing
import qrcode
import random
import string
import numpy as np
import os
import cv2
import psutil

IMAGE_SIZE = 25 #net input resolution
LETTERS = string.ascii_lowercase + '.'+'/'+':'
EOI = '#' # end of input
MAX_SIZE = 15 # max input/output size
MIN_SIZE = 1
ALL_CHAR_CLASSES = LETTERS + EOI # all available classes
VERSION = 2
LEVEL = qrcode.constants.ERROR_CORRECT_M
PADDING_SIZE = 0#qr padding
IMAGE_SIZE_DATASET = 25
CORNER_SIZE = IMAGE_SIZE_DATASET//4+IMAGE_SIZE_DATASET//8 
MARGIN = 20 
NUM_MASKS_PER_CORNER = 10

level_l = qrcode.constants.ERROR_CORRECT_L
level_m = qrcode.constants.ERROR_CORRECT_M
level_q = qrcode.constants.ERROR_CORRECT_Q
level_h = qrcode.constants.ERROR_CORRECT_H

qr_levels = [level_l, level_m,level_q, level_h]
qr_levels_dict = {level_l:'level_l', level_m:'level_m',level_q:'level_q', level_h:'level_h'}

# create training label for existing text and required position
def make_label_for_position(label, pos):
    char = label[pos] if pos < len(label) else EOI # either a letter or EOI
    return np.asarray(list( map(lambda l: l == char, ALL_CHAR_CLASSES)),dtype=np.float)

	
class PairGeneratorChar(object):
	def __init__(self,folder,sample_to_load,char_index,damages,mem_th,dynamic_load = False):
		self.folder = folder
		self.mem_th = mem_th
		self.char_index = char_index
		self.current=0
		self.current_internal = 0
		i=0
		self.damages = damages
		self.sample_to_load = sample_to_load
		#if the dataset is too large to fit in mem. in one go, sets dynamic_load to true to load part of the dataset so that
		# occupy mem_th percentage of  currently free mem. Eye, the dynamic_load option set to true reload portions of the dataset each time the previous one is exhausted
		#If False make sure sample to load and mem_th are calibrated to fit everything in memory.
		self.dynamic_load = dynamic_load 
		self.files = []
		for file in os.listdir(folder):
			self.files.append(file)
    
		self.loadDataset(sample_to_load,damages)
		
	
	def reset(self):
		self.current = 0
			
	
	def shuffle(self):
		random.shuffle(self.train_indici)

	def next_dataset_part(self):
		if self.current_part == self.final_part:
			self.current_part = 0
		else:
			self.current_part += 1
		self.loadDataset(self.sample_to_load,self.damages)
    
	def conditions_stop_loading(self):
		if self.sample_to_load == self.load_stop: 
				self.shuffle()
				return False
		if self.current_internal >= len(self.files):
				self.current_internal = 0
				return True
		
		if psutil.virtual_memory().percent >= (self.start_occupied + self.perc_to_occupy):
				return False

		return True
	
	def loadDataset(self,sample_to_load=None,damages=None):
		if sample_to_load is None:
			sample_to_load = self.sample_to_load
		if damages is None:
			damages = self.damages

		self.images_and_label = []
		self.train_indici = [] #to shuffle
		self.val_indici = [] #not to shuffle

		self.start_occupied = psutil.virtual_memory().percent
		self.start_free = 100.0 - self.start_occupied
		self.perc_to_occupy = self.mem_th * self.start_free

	
		
		print("Loading dataset...")
		index = 0
		self.load_stop=0
		while self.conditions_stop_loading():
			
			id = self.files[self.current_internal]
			
			images=[]
			for damage in damages:
				#image
				sample_filename = os.path.join(self.folder,id,	'{}.jpg'.format(damage))
				#print("loaded ",sample_filename)
				image = cv2.imread(sample_filename)
				image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
				image = image / 255.
				image = np.expand_dims(image, axis=-1)
				images.append(image)
			
				#print("sample_filename:",sample_filename,"label:",label,"labelonehot:",chars_labels[CHAR_INDEX])
			
			#assert len(images) == 2
			self.train_indici.append(index)
			self.val_indici.append(index)
			index = index + 1
			#label
			label_filename = os.path.join(self.folder,id,'label.txt')
			file = open(label_filename,'r')
			label_string = file.readline()
			file.close()
			#label one hot
			label = make_label_for_position(label_string,self.char_index)
			
			label_string = label_string + EOI*(MAX_SIZE-len(label_string))
			self.images_and_label.append({'image':images,'label':label,'label_str':label_string})
			self.load_stop+=1	
			self.current_internal += 1
		print("loaded {} images".format(index*len(damages)))
	
	def getTrainBatch(self,size):
		images = []
		labels = []
		size= size//len(self.damages) 
		
		
		#print("size",size)
		#print("self.current",self.current)
		i=0
		for index in range(self.current,self.current+size):
			if index >= (len(self.train_indici)):
				self.current = 0
				
				if self.dynamic_load:
					self.loadDataset()
				self.shuffle()
				return self.getTrainBatch(size)
			
			id = self.train_indici[index]
			
			pair = self.images_and_label[id]
			for inloop in range(len(self.damages)):
				
				images.append(pair['image'][inloop])
				
				labels.append(pair['label'] )
				i+=1
		#print("eseguito tr batch",i)
		self.current += size
		return images, labels
		
	def getTestImageLabel(self):
		images = []
		labels = []
		
		#print("size",size)
		#print("self.current",self.current)
		i=0
		index = self.current
		if index >= (len(self.val_indici)):
			self.current = 0
		
			if self.dynamic_load:
				self.loadDataset()
		
			return self.getTestImageLabel()
			
		id = self.val_indici[index]
		#print("index",index)
		#print("scelto id",id)
		pair = self.images_and_label[id]
		for inloop in range(len(self.damages)):
		
			images.append(pair['image'][inloop])
			
			labels.append(pair['label_str'] )
			i+=1
		
		self.current += 1
		return images, labels
		
	def getValidationBatch(self,size):
		images = []
		labels = []
		size= size//len(self.damages)
		
		#print("size",size)
		#print("self.current",self.current)
		i=0
		for index in range(self.current,self.current+size):
			if index >= (len(self.val_indici)):
				self.current = 0
		
				if self.dynamic_load:
					self.loadDataset()
				
				return images, labels
			
			id = self.val_indici[index]
		
			pair = self.images_and_label[id]
			for inloop in range(len(self.damages)):
			
				images.append(pair['image'][inloop])
			
				labels.append(pair['label'] )
				i+=1
		
		self.current += size
		return images, labels
	
	
