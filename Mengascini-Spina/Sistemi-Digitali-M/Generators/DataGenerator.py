import math
from abc import ABC, abstractmethod
import tensorflow as tf


class DataGenerator(ABC, tf.compat.v2.keras.utils.Sequence):
    """
    Class that given a dataset, prepares and splits the data to serve to the model
    """

    def __init__(self,dataset, batch_size, augment_data: bool = True, shuffle: bool = True):
        """
        :param batch_size: how many elements will every batch contain?
        :param augment_data: Should we use some data augmentation technique
            (if defined) to perturb the data differently at each epoch?
        :param shuffle: should the elements be shuffled at each epoch?
        """
        self.dataset = dataset
        self.batch_size = batch_size

        self.batches = self.dataset.batch(self.batch_size).as_numpy_iterator()

        self.augment_data = augment_data
        self.shuffle = shuffle
        self.batch_index = 0
        self.indexes = []
        self.on_epoch_end()


    def __next__(self):
        """
            Used to iterate over the batches until the end of the epoch
        :return: batch of seld.batch_size samples
        """

        # Get one batch of data
        data = self.__getitem__(self.batch_index)
        # Batch index
        self.batch_index += 1

        # If we have processed the entire dataset then
        if self.batch_index >= self.__len__():
            self.on_epoch_end()
            self.batch_index = 0

        return data

    def __getitem__(self, index):
        """
        Given a batch index, returns the set of elements inthat batch
        :param index:
        :return:
        """
        # Find list of IDs
        batch = next(self.batches)

        X, Y = self._generate_batch(batch)

        self.batch_index += 1

        if self.batch_index >= self.__len__()-2:
            self.on_epoch_end()

        return X.astype('float32'), Y.astype('float32')

    def _generate_batch(self, samples):
        """
        Given a list of samples ids, create a batch with those samples
        :param sample_ids: ids of the samples that have to be included in the batch
        :return:
        """
        # read the samples
        x = self._generate_x(samples)
        y = self._generate_y(samples)

        return x, y

    def __len__(self):
        """
        Compute the length of the set using the elements in the given dataset divided by the number of elements
        in ach batch
        :return: integer
        """

        return math.floor(len(self.dataset)/ self.batch_size)

    def on_epoch_end(self):
        """
        After the execution of an epoch, set up the generator to execute another one.
        :return: None
        """
        self.batch_index = 0
        #self.dataset = self.dataset.shuffle(len(self.dataset))
        self.batches = self.dataset.batch(self.batch_size).as_numpy_iterator()

    def _generate_indexes(self, batch_id):
        """
        Given the id of a batch, generate a list of samples indexes to use in that batch
        :param batch_id:
        :return:
        """
        return self.indexes[batch_id * self.batch_size:(batch_id + 1) * self.batch_size]

    @abstractmethod
    def _generate_x(self, sample_id):
        """
        Given a sample id, read the sample input from the
        :param sample_id: id of the sample we have to generte
        :return: input of the sample
        """
        raise NotImplementedError

    @abstractmethod
    def _generate_y(self, sample_id):
        """
        Given a sample id, read the sample input from the
        :param sample_id: id of the sample we have to generte
        :return: input of the sample
        """
        raise NotImplementedError
