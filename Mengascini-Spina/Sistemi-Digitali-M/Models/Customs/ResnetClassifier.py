from pathlib import Path
from tensorflow.python.keras.applications.resnet import ResNet50
from tensorflow.python.keras.layers import Flatten, Dense
from tensorflow.python.keras.models import Model
from Models.BaseModels.CNNModel import CNNModel
from Models.BaseModels.DenseModel import DenseModel


class ResnetClassifier(DenseModel, CNNModel):

    def __init__(self, input_shape, n_classes, model_name: str, log_dir: Path, batchnormalization=True, dropout=0.4,
                 verbose: bool = True):
        super(ResnetClassifier, self).__init__(model_name, log_dir, verbose)
        self.input_structure = input_shape
        self.n_classes = n_classes
        self.batchnormalization = batchnormalization
        self.dropout = dropout

    @property
    def output_shape(self) -> tuple:
        """
        Return the input shape the model will have to support
        """
        return self.n_classes

    @property
    def input_shape(self) -> tuple:
        """
        For a resnet the outpus shape is simple the number of classes the network has to recognize
        """
        return self.input_structure

    def build_model(self, input_shape, n_classes) -> Model:
        """
        Function in charge of defining the model structure
        :param input_shape: tuple containing the shape of the data this model will recive as input
        :param n_classes: tuple containing the shape of the output produced by this model
        :return: Keras Sequential Model
        """

        resnet = ResNet50(include_top=False, input_shape=input_shape, weights=None)

        model = Flatten()(resnet.output)
        model = Dense(128, activation='relu', kernel_initializer='he_uniform')(model)
        model = Dense(64, activation='relu', kernel_initializer='he_uniform')(model)
        model = Dense(1, activation='sigmoid')(model)

        return Model(inputs=resnet.inputs, outputs=model)
