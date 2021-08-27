import random
from pathlib import Path
import numpy as np
from PIL import Image
import tensorflow_datasets as tfds
import tensorflow as tf

from Datasets.Modifications.BlurModification import BlurModification
from Datasets.Modifications.CompressionModification import CompressionModification
from Datasets.Modifications.ExposureModification import ExposureModification
from Datasets.Modifications.SaltAndPepperModification import SaltAndPepperModification
from Datasets.Utilities.Maps.Noiseprint.NoiseprintExtractor import NoiseprintExtractor
from Datasets.Utilities.Maps.Noiseprint.noiseprint import normalize_noiseprint
from Datasets.Utilities.Maps.SRM.SRMExtractor import SRMExtractor
from Datasets.Utilities.utilityFunctions import get_files_with_type

"Class to download the CASIA2 dataset"


class CASIA2(tfds.core.GeneratorBasedBuilder):
    VERSION = tfds.core.Version('1.0.0')
    RELEASE_NOTES = {
        '1.0.0': 'Initial release.',
    }

    IMAGE_TYPES = ('*.jpg', '*.tif')
    MASK_TYPES = ('*.png')
    PATH_SHEET_NAME_FIXES = Path(__file__).absolute().parent / "Utilities" / "CASIA2_fileNamesCorrection.xlsx"

    test_proportion = 0.1

    def __init__(self, **kwargs):
        """
        :param test_proportion: percentage of data allocated for testing
        """

        # call the parent's __init__
        super(CASIA2, self).__init__()

        # check if the test_proportion parameter is in a valid range
        test_proportion = kwargs.get("test_proportion", 0.1)
        assert (test_proportion < 1 and test_proportion >= 0)

        # check if the validation_proportion parameter is in a valid range
        validation_proportion = kwargs.get("validation_proportion", 0.1)
        assert (validation_proportion < 1 and validation_proportion >= 0)

        # check if testporportion and validation proportion together are still in a valid range
        assert (validation_proportion + test_proportion < 1)

        self.test_proportion = test_proportion
        self.validation_proportion = validation_proportion

        # if true prints logs while building the dataset
        self.verbose = kwargs.get("verbose", True)

        # the shape of the images accepted by the model
        self.supported_shape = (256, 384, 3)

        # setup data generators
        self.SRMGenerator = SRMExtractor()
        self.NoiseprintGenerator = NoiseprintExtractor()

    def features(self):
        """
        This function return a dictionary holding the type and shape of the data this builder object
        generates foreach sample
        :return:
        """

        desired_shape_3 = (256, 384, 3)
        desired_shape_1 = (256, 384, 1)

        return {
            'image': tfds.features.Image(shape=desired_shape_3),
            'noiseprint': tfds.features.Tensor(shape=desired_shape_1, dtype=tf.float32),
            'SRM': tfds.features.Image(shape=desired_shape_3),
            'flipped': tfds.features.ClassLabel(num_classes=2),
            'tampered': tfds.features.ClassLabel(num_classes=2)
        }

    def _info(self) -> tfds.core.DatasetInfo:
        """Returns the dataset metadata describint the dataset"""

        return tfds.core.DatasetInfo(
            builder=self,
            description="_DESCRIPTION",
            features=tfds.features.FeaturesDict(self.features()),
            # If there's a common (input, target) tuple from the
            # features, specify them here. They'll be used if
            # `as_supervised=True` in `builder.as_dataset`.
            homepage='https://dataset-homepage/',
            citation="_CITATION",
        )

    def _split_generators(self, dl_manager: tfds.download.DownloadManager):
        """Download the data and define splits."""

        # list of the Datasets to download, one contains the training samples, the other contains the ground truths
        datasets_to_download = {
            'samples': 'https://drive.google.com/u/0/uc?id=1IDUgcoUeonBxx2rASX-_QwV9fhbtqdY8&export=download'
        }

        # download and extract the Datasets
        extracted_ds_paths = dl_manager.download_and_extract(datasets_to_download)

        # get paths of the extracted archives
        self.extracted_path_data_au = Path(extracted_ds_paths['samples']) / "CASIA2.0_revised" / "Au"
        self.extracted_path_data_tp = Path(extracted_ds_paths['samples']) / "CASIA2.0_revised" / "Tp"


        # get list of authentic and tapered images
        authentic_files = get_files_with_type(self.extracted_path_data_au, self.IMAGE_TYPES)
        tampered_files = get_files_with_type(self.extracted_path_data_tp, self.IMAGE_TYPES)


        # discard invalid files
        authentic_files = self._keep_valid(authentic_files)
        tampered_files = self._keep_valid(tampered_files)

        print("Found {} pristine and {} tampered images".format(len(authentic_files), len(tampered_files)))

        # shuffle the elements in the 2 lists
        random.shuffle(authentic_files)
        random.shuffle(tampered_files)

        # balance the classes by shortening the authentic and tampered sets to the length of the smallest
        min_len = int(min(len(authentic_files), len(tampered_files)))
        authentic_files = authentic_files[:min_len]
        tampered_files = tampered_files[:min_len]
        print("MIN_LEN: ", min_len)

        # select elements belonging to the train partition
        split_index = int(min_len * (1 - self.test_proportion - self.validation_proportion))
        train_authentic = authentic_files[:split_index]
        train_tampered = tampered_files[:split_index]

        # select elements belonging to the validation partition
        split_index_val = int(min_len * (1 - self.test_proportion))
        val_authentic = authentic_files[split_index:split_index_val]
        val_tampered = tampered_files[split_index:split_index_val]

        # select elements belonging to the test partition
        test_authentic = authentic_files[split_index_val:]
        test_tampered = tampered_files[split_index_val:]

        # create Modification classes

        # Blurred images
        blur_2 = BlurModification(2)
        blur_5 = BlurModification(5)
        blur_7 = BlurModification(7)

        # Salt and pepper
        salt_4 = SaltAndPepperModification(0.4, 0.001)
        salt_5 = SaltAndPepperModification(0.5, 0.008)
        salt_6 = SaltAndPepperModification(0.6, 0.016)

        # Change exposure 1-100
        exposed_20 = ExposureModification(20)
        exposed_50 = ExposureModification(50)
        exposed_70 = ExposureModification(70)

        # JPEG Compression 1-100
        compressed_20 = CompressionModification(20)
        compressed_50 = CompressionModification(50)
        compressed_75 = CompressionModification(75)

        return {"train": self._generate_examples("train", train_authentic, train_tampered, []),
                "validation": self._generate_examples("validation", val_authentic, val_tampered, []),
                "test": self._generate_examples("test", test_authentic, test_tampered, []),
                "test_blur_2": self._generate_examples("test", test_authentic, test_tampered, [blur_2]),
                "test_blur_5": self._generate_examples("test", test_authentic, test_tampered, [blur_5]),
                "test_blur_7": self._generate_examples("test", test_authentic, test_tampered, [blur_7]),
                "test_salt_4": self._generate_examples("test", test_authentic, test_tampered, [salt_4]),
                "test_salt_5": self._generate_examples("test", test_authentic, test_tampered, [salt_5]),
                "test_salt_6": self._generate_examples("test", test_authentic, test_tampered, [salt_6]),
                "test_exposed_20": self._generate_examples("test", test_authentic, test_tampered, [exposed_20]),
                "test_exposed_50": self._generate_examples("test", test_authentic, test_tampered, [exposed_50]),
                "test_exposed_70": self._generate_examples("test", test_authentic, test_tampered, [exposed_70]),
                "test_compressed_20": self._generate_examples("test", test_authentic, test_tampered, [compressed_20]),
                "test_compressed_50": self._generate_examples("test", test_authentic, test_tampered, [compressed_50]),
                "test_compressed_75": self._generate_examples("test", test_authentic, test_tampered, [compressed_75]),
                }

    def _generate_examples(self, name: str, authentic_files: list, tampered_files: list, modifications: list):

        # let's make sure the set is balance
        assert (len(authentic_files) == len(tampered_files))

        # import authentic images
        counter_authentic = 0
        for authentic_img in authentic_files:
            # generate the data of the sample
            sample = self._process_image(authentic_img, False, modifications)

            counter_authentic += 1
            yield str(authentic_img), sample

        # import tampered images
        counter_tampered = 0
        for tampered_img in tampered_files:
            # generate the data of the sample
            sample = self._process_image(tampered_img, True, modifications)

            counter_tampered += 1
            yield str(tampered_img), sample

        print(
            "Dataset: {} contains {} pristine and {} tampered images".format(name, counter_authentic, counter_tampered))

    def _keep_valid(self, files_paths: list):
        """
        Given a list of files return a list only of those that are valid
        :param files_paths:
        :return:
        """
        list = []

        set_of_shapes = {}

        for file_path in files_paths:

            image = Image.open(file_path).convert('RGB')
            image = np.asarray(image)

            if str(image.shape) not in set_of_shapes:
                set_of_shapes[str(image.shape)] = 0

            set_of_shapes[str(image.shape)] += 1

            # check that the image is of the right dimension (or directly transformable to)
            if image.shape[0] not in self.supported_shape or image.shape[1] not in self.supported_shape:
                continue

            list.append(file_path)

        # print data about the dataset
        if self.verbose:
            print("Valid images:{}".format(len(list)))

        return list

    def _process_image(self, path, is_tampered, modifications=[]):

        target_shape = (256, 384)

        image = Image.open(path).convert('RGB')
        image = np.asarray(image)

        # apply modifications to the image
        for modification in modifications:
            image = modification.apply(image)

        # if the image is flipped rotate it and all its noise maps
        flipped = False
        if image.shape[0] == target_shape[1]:
            image = np.rot90(image, 3)
            flipped = True

        # extract noiseprint map
        noiseprint = normalize_noiseprint(self.NoiseprintGenerator.extract(image))

        # extract SRM map
        srm = self.SRMGenerator.extract(image)

        assert (image.shape[0] == self.supported_shape[0])
        assert (image.shape[1] == self.supported_shape[1])
        assert (image.shape[2] == 3)

        assert (image.shape == srm.shape)
        assert (image.shape[0] == noiseprint.shape[0])
        assert (image.shape[1] == noiseprint.shape[1])

        return {"image": image, "noiseprint": noiseprint, "SRM": srm, "flipped": flipped, "tampered": is_tampered}