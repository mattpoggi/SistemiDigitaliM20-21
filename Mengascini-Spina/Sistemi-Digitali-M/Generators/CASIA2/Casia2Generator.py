from abc import ABC
from tensorflow.python.data import Dataset

from Generators.DataGenerator import DataGenerator


class Casia2Generator(DataGenerator, ABC):
    """
    Class that given a dataset, prepares and splits the data to serve to the model
    """

    def __init__(self, dataset: Dataset, x_data, batch_size, shuffle=True):
        super().__init__(dataset,batch_size,False,shuffle)
        self.x_samples = x_data
        self.indexes = []
        self.on_epoch_end()

    def _generate_x(self, samples):
        """
        Given a sample id, read the sample input from the
        :param sample_id: id of the sample we have to generte
        :return: input of the sample
        """

        # read the sample from the dataset

        inputs = samples[self.x_samples]

        if self.x_samples  == "image":
            inputs = inputs / 255
        elif self.x_samples  == "noiseprint":
            inputs = inputs
        elif self.x_samples  == "SRM":
            inputs = inputs / 255
        else:
            raise Exception("Requested invalid data key")
        return inputs

    def _generate_y(self, sample):
        """
        Given a sample id, read the sample input from the
        :param sample_id: id of the sample we have to generte
        :return: input of the sample
        """

        # read the sample from the dataset
        Y = sample["tampered"]

        return Y


