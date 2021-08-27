from pathlib import Path
import os
from PIL import Image
from tensorflow.python.keras.layers import Conv2D, BatchNormalization, Activation
import logging
logging.getLogger("tensorflow").setLevel(logging.ERROR)
import tensorflow as tf
tf.get_logger().setLevel('ERROR')
import numpy as np
import java
from tensorflow.python.keras.models import Model
import imageio
import base64
from utility import jpeg_qtableinv
import io
import cv2

slide = 1024
largeLimit = 1050000
overlap = 34

def noiseprint_calc():

    #Load the image file
    path = os.path.join(os.environ['HOME'], 'src.png')
    src = Image.open(path).convert("RGB")
    src = np.asarray(src)

    #Load the model based on the quality of the image
    quality = 200
    try:
        quality = jpeg_qtableinv(src)
    except:
        quality = 200

    quality = min(max(quality, 51), 101)
    file_name = 'net_jpg' + str(quality) + '.tflite'
    model_path = os.path.join(os.path.dirname(__file__), file_name)

    #Setup the interpreter
    global interpreter
    interpreter = tf.lite.Interpreter(model_path=str(model_path))
    interpreter.allocate_tensors()
    global input_details
    input_details = interpreter.get_input_details()
    global output_details
    output_details = interpreter.get_output_details()

    #Extract the noiseprint
    src = np.asarray(Image.fromarray(src).convert("YCbCr"))[..., 0].astype(np.float32) / 256.0
    noiseprint = predict(src)[..., np.newaxis]

    #Normalization
    margin = 34
    v_min = np.min(noiseprint[margin:-margin, margin:-margin])
    v_max = np.max(noiseprint[margin:-margin, margin:-margin])
    norm_noiseprint = ((noiseprint - v_min) / (v_max - v_min)).clip(0, 1)

    return java.jfloat(get_result(norm_noiseprint))


def predict_small(img):
    global interpreter
    global input_details
    global output_details
    interpreter.set_tensor(input_details[0]["index"], img)
    interpreter.invoke()
    return interpreter.get_tensor(output_details[0]['index'])

def predict_large(img):
    res = np.zeros((img.shape[0], img.shape[1]), np.float32)
    for index0 in range(0, img.shape[0], slide):
        index0start = index0 - overlap
        index0end = index0 + slide + overlap

        for index1 in range(0, img.shape[1], slide):
            index1start = index1 - overlap
            index1end = index1 + slide + overlap
            clip = img[max(index0start, 0): min(index0end, img.shape[0]),
                   max(index1start, 0): min(index1end, img.shape[1])]
            res_chunk = predict_small(clip[np.newaxis, :, :, np.newaxis])
            res_chunk = np.squeeze(res_chunk)

            if index0 > 0:
                res_chunk = res_chunk[overlap:, :]
            if index1 > 0:
                res_chunk = res_chunk[:, overlap:]
            res_chunk = res_chunk[:min(slide, res_chunk.shape[0]), :min(slide, res_chunk.shape[1])]

            res[index0: min(index0 + slide, res.shape[0]),
            index1: min(index1 + slide, res.shape[1])] = res_chunk
    return res


def predict(img):
    if img.shape[0] * img.shape[1] > largeLimit:
        return predict_large(img)
    else:
        return tf.squeeze(predict_small(img[np.newaxis, :, :, np.newaxis])).numpy()


def get_result(norm_noiseprint):

    noiseprint = np.expand_dims(norm_noiseprint, axis=0)

    model_path = os.path.join(os.path.dirname(__file__), 'noiseprint.tflite')
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    interpreter.set_tensor(input_details[0]['index'], noiseprint)
    interpreter.invoke()
    return interpreter.get_tensor(output_details[0]['index'])[0][0].item()