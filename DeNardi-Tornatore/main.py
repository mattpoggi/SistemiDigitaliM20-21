import tensorflow as tf
import datetime
import os
from multiprocessing import Pool
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import Session
from datasetGen import main as m1
from dataGenerator import main as m2
from tabModel import main as m3
from tfLiteConverter import main as m4
from modelEvaluate import main as m5


# define path data folder and n file
path = "D:/Projects/GitHub-Projects/tab-writer/data/"
n_file = 360

path_arr = [path] * 360
lists = list(range(0, n_file))


def log(text):
	text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " | " + text + "\n"
	with open("log/data.log", "a") as myfile:
		myfile.write(text)
		print(text)

def gpu(check):
	if check:
		config = ConfigProto()
		config.gpu_options.allow_growth = True
#			config.gpu_options.per_process_gpu_memory_fraction = 0.6  # 0.6 sometimes works better for folks
		sess = Session(config=config)
#			tf.debugging.set_log_device_placement(True)
	else:
		os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

	if tf.test.gpu_device_name():
		log("GPU found")
	else:
		log("No GPU found")

def menu():
	checkgpu = input("Vuoi utilizzare la GPU? (y/n) ")
	log("Vuoi utilizzare la GPU? (y/n) " + checkgpu)

	if (checkgpu == "y"):
		gpu(True)
	else:
		gpu(False)

	datasetgen = input("Vuoi generare il dataset? (y/n) ")
	log("Vuoi generare il dataset? (y/n) " + datasetgen)

	if (datasetgen == "y"):
		log("###############################")
		log("###### INIT NEW DATA GEN ######")
		log("###############################")
		p = Pool(5)
		p.map(m1, zip(path_arr, lists))

	datagenerator = input("Vuoi preparare il dataset? (y/n) ")
	log("Vuoi preparare il dataset? (y/n) " + datagenerator)

	if (datagenerator == "y"):
		log("###############################")
		log("###### INIT PREPARE DATA ######")
		log("###############################")
		m2()

	tabmodel = input("Vuoi generare il modello? (y/n) ")
	log("Vuoi generare il modello? (y/n) " + tabmodel)

	if (tabmodel == "y"):
		log("###############################")
		log("####### INIT MODEL GEN ########")
		log("###############################")
		m3()

	tfliteconverter = input("Vuoi convertire il modello in tflite? (y/n) ")
	log("Vuoi convertire il modello in tflite? (y/n) " + tfliteconverter)

	if (tfliteconverter == "y"):
		log("###############################")
		log("##### INIT MODEL CONVERT ######")
		log("###############################")
		m4()

	modelevaluate = input("Vuoi testare il modello? (y/n) ")
	log("Vuoi testare il modello? (y/n) " + modelevaluate)

	if (modelevaluate == "y"):
		log("###############################")
		log("##### INIT MODEL EVALUATE #####")
		log("###############################")
		m5()


if __name__ == "__main__":
	log("###############################")
	log("########## INIT MAIN ##########")
	log("###############################")
	menu()