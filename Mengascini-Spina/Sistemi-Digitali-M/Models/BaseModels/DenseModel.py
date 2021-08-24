from abc import ABC
from pathlib import Path
from tensorflow.python.keras.models import Sequential
from Models.BaseModel import BaseModel
import tensorflow as tf

class DenseModel(BaseModel, ABC):

    def __init__(self, model_name: str, log_dir: Path, verbose: bool = True):
        super(DenseModel, self).__init__(model_name,log_dir,verbose)
    
    @staticmethod
    def dense_block(model:Sequential, units, dropout_rate=0.4, activation="relu") -> Sequential:
        """
        This function defines the standard block of a BaseModels conposed by:
            - Dense layer
            - Dropout
            - BatchNormalization
            - Activation function
        We can use it as a building block to build larger networks in an organized manner

        :param model: the model to which we should append the block
        :param units: the number of units of the dense layer
        :param dropout_rate: probability of a neuron to be switched off
        :param activation: the type of activation function to use (eg: Relu)
        :return: the initial sequential model with the block appended
        """

        model = tf.keras.layers.Dense(units=units)(model)
        model = tf.keras.layers.Dropout(dropout_rate)(model)
        model = tf.keras.layers.BatchNormalization()(model)
        model = tf.keras.layers.Activation(activation)(model)
        return model


