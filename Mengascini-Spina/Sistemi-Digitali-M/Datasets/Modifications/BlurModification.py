from abc import abstractmethod
from scipy import ndimage


class BlurModification:

    def __init__(self, sigma):
        self.sigma = sigma

    @abstractmethod
    def apply(self, sample):
        """
        Function to apply this modification to an image
        :param sample as numpy array: sample to which this modification we be applied
        """

        return ndimage.uniform_filter(sample, size=(self.sigma, self.sigma, 1))
