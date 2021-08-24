from Datasets.Utilities.Maps.MapExtractor import MapExtractor
from Datasets.Utilities.Maps.Noiseprint.noiseprint import NoiseprintEngineV2
import numpy as np
from PIL import Image
from Datasets.Utilities.Maps.Noiseprint.utility import jpeg_qtableinv


class NoiseprintExtractor(MapExtractor):


    def extract(self, image):
        """
        Extract the noiseprint from the given image

        :param image: the image as a numpy array
        """

        quality = 200
        try:
            quality = jpeg_qtableinv(image)
        except:
            quality = 200
        image = np.asarray(Image.fromarray(image).convert("YCbCr"))[..., 0].astype(np.float32) / 256.0

        return NoiseprintEngineV2(quality).predict(image)[..., np.newaxis]