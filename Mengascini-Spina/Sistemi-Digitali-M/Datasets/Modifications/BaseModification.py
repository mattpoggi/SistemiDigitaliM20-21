from abc import abstractmethod


class BaseModification:

    def __init__(self):
        pass

    @abstractmethod
    def apply(self, sample):
        """
        Function to apply this modification to an image
        :param sample: sample to which this modification we be applied
        """
        raise NotImplementedError
