from abc import ABC, abstractmethod


class MapExtractor(ABC):

    def __init__(self):
        """
        Precompute here all the data the extractor need to work properly
        """
        pass

    @abstractmethod
    def extract(self, base):
        """
        Given an input object this method produce the output map

         :base : base data to produce the output map
        """
        raise NotImplementedError
