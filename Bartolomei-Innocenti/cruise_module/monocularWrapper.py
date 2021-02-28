from defaults import Defaults

import logging
import json
import tensorflow as tf
import tflite_runtime.interpreter as tflite
import numpy as np
import time
import matplotlib.cm

from tensorflow.python.platform import gfile

import cv2 as cv

class MonocularWrapper:
    """
    Si occupa di effettuare l'inferenza della depth data un'immagine e un sensore monoculare
    """

    CONFIG_KEYS = []
    CONFIG_FINAL_KEYS = []
    CONFIG_OPTIONAL_KEYS = ['modelIndex']
    CONFIG_SUBTYPES_KEYS = []

    @classmethod
    def loadModels(cls, modelsDefPath = None):
        if modelsDefPath is None:
            modelsDefPath = Defaults.modelsDefPath

        f = open(modelsDefPath, "r")
        modelsDef = f.read()
        cls.models = json.loads(modelsDef)

    def __init__(self, index = 0):    
        self.config = {'modelIndex': index}
        self.inferenceTime = float('nan')
        self.model = self.models[index]
        self.modelLoading()

    @property
    def isDisparityOutput(self):
        return self.model["disparityOutput"]
    
    @property
    def minOutputValue(self):
        return self.model["outputMin"]

    @property
    def maxOutputValue(self):
        return self.model["outputMax"]
    
    @property
    def depthCap(self):
        return self.model["depthCap"]

    @property
    def depthMin(self):
        return self.model["depthMin"]

    @property
    def loggingName(self):
        return "Monocular Wrapper ({0}) ".format(self.model["fileName"])

    @property
    def modelType(self):
        return self.model['modelType']

    @property
    def input_tensor_name(self):
        return self.model["inputNodes"][self.model["defaultInputNode"]]

    @property
    def output_tensor_name(self):
        return self.model["outputNodes"][self.model["defaultOutputNode"]]

    @property
    def resolution(self):
        return (self.model["resolution"][0], self.model["resolution"][1])

    @property
    def modelIndex(self):
        return self.config['modelIndex']
    
    @property
    def modelInputShape(self):
        return tuple(self.model["inputShape"])

    @property
    def modelOutputShape(self):
        return tuple(self.model["outputShape"])

    @property
    def status(self):
        return {**self.config, 'models': self.models}

    def config(self, config):
        if 'modelIndex' in config:
            modelIndex = config['modelIndex']
            self.selectModel(modelIndex)

    def selectModel(self, index = 0):
        if index >= 0 and index < len(self.models): 
            if self.modelType == "tf":
                self.tfUnloading()
            
            self.model = self.models[index]
            self.modelLoading()

    def modelLoading(self):
        if self.modelType == "tf":
            self.tfLoading()
        elif self.modelType == "tflite":
            self.tfliteLoading()
        self.testInference()

    def testInference(self):
        img = np.random.random_sample(self.modelInputShape[1:])
        if self.model["inputNormalizationType"] == "div255":
            img = img * 255.0
        return self.inference(img)

    def inference(self, img):
        if self.modelType == "tf":
            return self.tfInference(img)
        elif self.modelType == "tflite":
            return self.tfliteInference(img)

    def tfLoading(self):
        session = tf.compat.v1.Session()
        
        f = tf.io.gfile.GFile(self.model["fileName"],'rb')
        graph_def = tf.compat.v1.GraphDef()
        graph_def.ParseFromString(f.read())
        f.close()

        session.graph.as_default()
        g_in = tf.import_graph_def(graph_def, name="")

        self.session = session

        self.input_tensor = session.graph.get_tensor_by_name(self.input_tensor_name)
        self.input_tensor.set_shape(self.model["inputShape"])
        
        self.output_tensor = session.graph.get_tensor_by_name(self.output_tensor_name)
        self.output_tensor.set_shape(self.model["outputShape"])

    def tfInference(self, img):
        tmpShape = img.shape[:2]

        start = time.time()

        img = self.preElaboration(img)
        prediction = self.session.run(self.output_tensor, feed_dict={self.input_tensor_name:img})
        #prediction = np.zeros(self.modelOutputShape)
        prediction = np.clip(prediction, self.minOutputValue, self.maxOutputValue)
        prediction = self.postElaboration(prediction, tmpShape)
        
        end = time.time()
        self.inferenceTime = end - start        

        logging.debug("{0} prediction min: {1}, max: {2}".format(self.loggingName, np.min(prediction), np.max(prediction)))

        return prediction

    def tfUnloading(self):
        self.session.close()

    def tfliteLoading(self):
        self.interpreter = tflite.Interpreter(model_path=self.model["fileName"], num_threads=4)
        self.interpreter.allocate_tensors()

        # Get input and output tensors.
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def tfliteInference(self, img):
        tmpShape = img.shape[:2]

        start = time.time()

        img = self.preElaboration(img)
        
        self.interpreter.set_tensor(self.input_details[0]['index'], img)
        self.interpreter.invoke()
        prediction = self.interpreter.get_tensor(self.output_details[0]['index'])
        prediction = np.clip(prediction, self.minOutputValue, self.maxOutputValue)
        prediction = self.postElaboration(prediction, tmpShape)
        
        end = time.time()
        self.inferenceTime = end - start        

        logging.debug("{0} prediction min: {1}, max: {2}".format(self.loggingName, np.min(prediction), np.max(prediction)))

        return prediction

    def preElaboration(self, img):
        height, width = self.resolution

        #Scalo l'immagine in modo che rispetti l'input shape
        if self.resolution != img.shape:
            img = cv.resize(img, (width, height))
        
        if self.model["inputNormalizationType"] == "div255":
            img = img / 255.0

        if self.model["inputType"] == "float32":
            img = img.astype(np.float32)
        elif self.model["inputType"] == "uint8":
            img = img.astype(np.uint8)

        #img = np.expand_dims(img, axis=0)
        img = np.reshape(img, tuple(self.model["inputShape"]))

        return img

    def postElaboration(self, prediction, originalShape):
        height, width = originalShape
        prediction = cv.resize(prediction[0][:,:,0], (width, height))# rimuovo il primo asse e resize a dimensione originale (H, W)
        return np.expand_dims(prediction, axis=-1) #(H, W, 1)

    def colorize(self, prediction, mask=None, vmin=None, vmax=None, cmap="viridis"):
        # normalize
        vmin = np.min(prediction) if vmin is None else vmin
        vmax = np.max(prediction) if vmax is None else vmax

        prediction = (prediction - vmin) / (vmax - vmin)  # vmin..vmax
        prediction *= 255
        prediction = np.reshape(prediction, prediction.shape[:2])
        prediction = np.uint8(prediction)
        
        return cv.applyColorMap(prediction, cv.COLORMAP_JET)

#Init
MonocularWrapper.loadModels()