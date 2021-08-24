from pathlib import Path
import os
from PIL import Image
from tensorflow.python.keras.layers import Conv2D, BatchNormalization, Activation

import logging
logging.getLogger("tensorflow").setLevel(logging.ERROR)
import tensorflow as tf
tf.get_logger().setLevel('ERROR')
import numpy as np
from tensorflow.python.keras.models import Model

from Datasets.Utilities.Maps.Noiseprint.utility import jpeg_qtableinv


class BiasLayer(tf.keras.layers.Layer):

    def build(self, input_shape):
        self.bias = self.add_weight('bias', shape=input_shape[-1], initializer="zeros")

    @tf.function
    def call(self, inputs, training=None):
        return inputs + self.bias


def _FullConvNetV2(num_levels=17, padding='SAME'):
    """FullConvNet model."""
    activation_fun = [tf.nn.relu, ] * (num_levels - 1) + [tf.identity, ]
    filters_num = [64, ] * (num_levels - 1) + [1, ]
    batch_norm = [False, ] + [True, ] * (num_levels - 2) + [False, ]

    inp = tf.keras.layers.Input([None, None, 1])
    model = inp

    for i in range(num_levels):
        model = Conv2D(filters_num[i], 3, padding=padding, use_bias=False)(model)
        if batch_norm[i]:
            model = BatchNormalization(epsilon=1e-5)(model)
        model = BiasLayer()(model)
        model = Activation(activation_fun[i])(model)

    return Model(inp, model)


class NoiseprintEngineV2:
    save_path = os.path.join(os.path.dirname(__file__), 'noiseprint_V2/net_jpg%d/')
    slide = 1024  # 3072
    largeLimit = 1050000  # 9437184
    overlap = 34

    def __init__(self, quality=None):
        self.model = _FullConvNetV2()
        configSess = tf.compat.v1.ConfigProto()
        configSess.gpu_options.allow_growth = True
        self.quality = quality
        self.loaded_quality = None
        if quality is not None:
            self.load_session(quality)

    def load_session(self, quality):
        # log("Setting quality to %d " % quality)
        quality = min(max(quality, 51), 101)
        if quality == self.loaded_quality:
            return
        checkpoint = self.save_path % quality
        self.model.load_weights(checkpoint)
        self.loaded_quality = quality

    @tf.function(experimental_relax_shapes=True,
                 input_signature=[tf.TensorSpec(shape=(1, None, None, 1), dtype=tf.float32)])
    def _predict_small(self, img):
        return self.model(img)

    def _predict_large(self, img):
        res = np.zeros((img.shape[0], img.shape[1]), np.float32)
        for index0 in range(0, img.shape[0], self.slide):
            index0start = index0 - self.overlap
            index0end = index0 + self.slide + self.overlap

            for index1 in range(0, img.shape[1], self.slide):
                index1start = index1 - self.overlap
                index1end = index1 + self.slide + self.overlap
                clip = img[max(index0start, 0): min(index0end, img.shape[0]),
                       max(index1start, 0): min(index1end, img.shape[1])]
                res_chunk = self._predict_small(clip[np.newaxis, :, :, np.newaxis])
                res_chunk = np.squeeze(res_chunk)

                if index0 > 0:
                    res_chunk = res_chunk[self.overlap:, :]
                if index1 > 0:
                    res_chunk = res_chunk[:, self.overlap:]
                res_chunk = res_chunk[:min(self.slide, res_chunk.shape[0]), :min(self.slide, res_chunk.shape[1])]

                res[index0: min(index0 + self.slide, res.shape[0]),
                index1: min(index1 + self.slide, res.shape[1])] = res_chunk
        return res

    def predict(self, img):
        if img.shape[0] * img.shape[1] > self.largeLimit:
            return self._predict_large(img)
        else:
            return tf.squeeze(self._predict_small(tf.convert_to_tensor(img[np.newaxis, :, :, np.newaxis]))).numpy()

def normalize_noiseprint(noiseprint, margin=34):
    v_min = np.min(noiseprint[margin:-margin, margin:-margin])
    v_max = np.max(noiseprint[margin:-margin, margin:-margin])
    return ((noiseprint - v_min) / (v_max - v_min)).clip(0, 1)
