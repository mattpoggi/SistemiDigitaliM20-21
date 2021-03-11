#DA FAREEEEE
import tensorflow as tf
import numpy as np
import pandas as pd
import cv2

import sys
sys.path.append('../../')
from utils.DBR_utils import get_dog_from_predictions, resize_square_image_keep_ratio_border, print_human_readable_dog_cli

from Network import DBR_Network


# -- Variabili globali --
# Paths
modelName = 'DBR1.9.8-8000'
trained_model_path = './trainedModel/'
csv_output_values = '../../_DBR_dataset_128px_v4/_breeds/unique_breed_translation.csv'
test_image_path   = '../../_single_test/leonberg.jpg'

# Variabili
img_size = (128, 128, 3)  #dimensione immagini dataset
output_values_it = pd.read_csv(csv_output_values)['IT']


def get_test_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #RESIZE IMAGE FOR PREDICT
    image = resize_square_image_keep_ratio_border(image, img_size[0])
    image = image / 255.
    return np.expand_dims(image,0)

# Predict one
if __name__ == '__main__':
    trainedModel = trained_model_path + modelName

    x = tf.placeholder(tf.float32,shape=[1,img_size[0],img_size[1],img_size[2]], name='input')
    network = DBR_Network(x=x, is_training=False)

    loader = tf.train.Saver()

    config = tf.ConfigProto(allow_soft_placement=True)
    with tf.Session(config=config) as session:
        loader.restore(session, trainedModel)

        image = get_test_image(test_image_path)
        predicted_value, output_percentage = session.run([network.prediction, network.output_percentage], feed_dict={x:image})
        dog = get_dog_from_predictions(output_percentage, output_values_it, test_image_path)
        print('\n- Risultato -')
        res = print_human_readable_dog_cli(dog)
        print(res)
