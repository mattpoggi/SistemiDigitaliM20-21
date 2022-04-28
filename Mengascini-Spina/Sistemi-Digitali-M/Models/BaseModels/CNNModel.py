from abc import ABC

from tensorflow.python.keras.layers import MaxPooling2D, UpSampling2D
from tensorflow.python.keras.models import Sequential

from Models.BaseModel import BaseModel
import tensorflow as tf

class CNNModel(BaseModel, ABC):

    @staticmethod
    def convolutional_block(model:Sequential, filters, kernel_size, strides, padding="same", dropout_rate=0.4, activation="relu") -> Sequential:
        """
        This function defines the standard block of a BaseModels conposed by:
            - Convolution
            - Dropout
            - BatchNormalization
            - Activation fadd unction
        We can use it as a building block to build larger networks in an organized manner

        :param model: the model to which we should append the block
        :param filters: the number of filters the BaseModels should output
        :param kernel_size: the kernel size of the BaseModels
        :param strides: the strides parameter of the BaseModels
        :param padding: the padding parameter to pass to the BaseModels layer (default: same)
        :param dropout_rate: probability of a neuron to be switched off
        :param activation: the type of activation function to use (eg: Relu)
        :return: the initial sequential model with the block appended
        """

        model = tf.keras.layers.Conv2D(filters=filters, kernel_size=kernel_size, strides=strides,padding=padding,
                                       activation=activation,kernel_initializer='he_uniform')(model)
        model = tf.keras.layers.BatchNormalization()(model)
        model = tf.keras.layers.Dropout(dropout_rate)(model)
        return model

    @staticmethod
    def downsampling_block(model:Sequential,downsampling_factor,padding="same"):
        """
            This block can be used to downsample daa of a 2D convolution
        :param model: the model to which we should append the block
        :param downsampling_factor: the factor by which we want to downsample
        :param padding: the type of padding to apply
        :return: the initial sequential model with the block appended
        """
        return MaxPooling2D(downsampling_factor, padding=padding)(model)

    @staticmethod
    def upsampling_block(model:Sequential, upsampling_factor, interpolation="nearest"):
        """
            This block can be used to upsample data of a 2D convolution
        :param model: the model to which we should append the block
        :param upsampling_factor: the factor by which we want to downsample
        :param padding: the type of padding to apply
        :return: the initial sequential model with the block appended
        """
        return UpSampling2D(upsampling_factor, interpolation=interpolation)(model)


