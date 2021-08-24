"""
The SRM is a filter described by this paper:
https://openaccess.thecvf.com/content_cvpr_2018/papers/Zhou_Learning_Rich_Features_CVPR_2018_paper.pdf
usefull to extract noise levels from an image
"""
import cv2
import numpy as np

from Datasets.Utilities.Maps.MapExtractor import MapExtractor


class SRMExtractor(MapExtractor):

    def __init__(self):
        """
        Compute the SRM filter to apply to the image to extract noise levels
        The SRM filter is composed by 3 sub kernels as described in this paper:
        https://openaccess.thecvf.com/content_cvpr_2018/papers/Zhou_Learning_Rich_Features_CVPR_2018_paper.pdf
        """

        filter1 = [[0, 0, 0, 0, 0],
                   [0, -1, 2, -1, 0],
                   [0, 2, -4, 2, 0],
                   [0, -1, 2, -1, 0],
                   [0, 0, 0, 0, 0]]
        filter2 = [[-1, 2, -2, 2, -1],
                   [2, -6, 8, -6, 2],
                   [-2, 8, -12, 8, -2],
                   [2, -6, 8, -6, 2],
                   [-1, 2, -2, 2, -1]]
        filter3 = [[0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0],
                   [0, 1, -2, 1, 0],
                   [0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0]]

        filter1 = np.asarray(filter1, dtype=float) / 4
        filter2 = np.asarray(filter2, dtype=float) / 12
        filter3 = np.asarray(filter3, dtype=float) / 2

        self.filter = filter1 + filter2 + filter3


    def extract(self, base):
        """
        Given an input image, apply the SRM filter and return the result

        :param base: input image as numpy array
        """
        return cv2.filter2D(base, -1, self.filter)