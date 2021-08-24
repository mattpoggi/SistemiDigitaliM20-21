from abc import abstractmethod
import cv2


class ExposureModification:

    def __init__(self, value):
        self.value = value

    @abstractmethod
    def apply(self, sample):
        """
        Function to apply this modification to an image
        :param sample as numpy array: sample to which this modification we be applied
        """

        hsv = cv2.cvtColor(sample, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        lim = 255 - self.value
        v[v > lim] = 255
        v[v <= lim] += self.value

        final_hsv = cv2.merge((h, s, v))
        img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        return img
