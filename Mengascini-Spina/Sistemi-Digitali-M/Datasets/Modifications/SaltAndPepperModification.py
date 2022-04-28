from abc import abstractmethod
import numpy as np


class SaltAndPepperModification:

    def __init__(self, s_vs_p, amount):
        self.s_vs_p = s_vs_p
        self.amount = amount

    @abstractmethod
    def apply(self, sample):
        """
        Function to apply this modification to an image
        :param sample as numpy array: sample to which this modification we be applied
        """

        row, col, ch = sample.shape
        #s_vs_p = 0.5
        #amount = 0.004
        out = np.copy(sample)
        # Salt mode
        num_salt = np.ceil(self.amount * sample.size * self.s_vs_p)
        coords = [np.random.randint(0, i - 1, int(num_salt))
                  for i in sample.shape]
        out[coords] = 1

        # Pepper mode
        num_pepper = np.ceil(self.amount * sample.size * (1. - self.s_vs_p))
        coords = [np.random.randint(0, i - 1, int(num_pepper))
                  for i in sample.shape]
        out[coords] = 0
        return out
