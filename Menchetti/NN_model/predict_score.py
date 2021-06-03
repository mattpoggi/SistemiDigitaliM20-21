#DA FAREEEEE
import tensorflow as tf
import numpy as np
import pandas as pd
import cv2

import sys
sys.path.append('../../')
from utils.DBR_utils import resize_square_image_keep_ratio_border, calc_score_top1, calc_score_top5, read_test_labels

from Network import DBR_Network



# -- Variabili globali --
# Paths
modelName = 'DBR1.9.8-8000'
trained_model_path = './trainedModel/'
csv_output_values = '../../_DBR_dataset_128px_v4/_breeds/unique_breed_translation.csv'
testing_folder = '../../_DBR_dataset_128px_v4/test/'
log_path = './logs/'

# Variabili
img_size = (128, 128, 3)  #dimensione immagini dataset
output_values = pd.read_csv(csv_output_values)['UNIQUE_BREED']


def get_test_batch(dataset, index):
    ''' Load next training batch '''
    batch = {
        'images' : None,
    }
    image_path = dataset + str(index).zfill(5)+'.jpg'
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #RESIZE IMAGE FOR PREDICT
    image = resize_square_image_keep_ratio_border(image, img_size[0])
    #image = np.pad(image, ((2,2),(2,2)),'constant')
    image = image / 255.
    #image = np.expand_dims(image, axis=-1)
    batch['images'] = np.expand_dims(image,0)
    return batch

# Predict score
if __name__ == '__main__':
    trainedModel = trained_model_path + modelName
    file_log = log_path + modelName + '_predict_score_log.txt'

    with open(file_log, 'w') as f:
        x = tf.placeholder(tf.float32,shape=[1,img_size[0],img_size[1],img_size[2]], name='input')
        network = DBR_Network(x=x, is_training=False)

        testing_images = testing_folder + 'images/'
        testing_labels = read_test_labels(testing_folder + 'test_labels.txt')

        loader = tf.train.Saver()

        config = tf.ConfigProto(allow_soft_placement=True)
        results = []
        total_number = len(testing_labels)
        with tf.Session(config=config) as session:
            loader.restore(session, trainedModel)

            for step in range(total_number):
                next_batch = get_test_batch(testing_images, step)
                predicted_value, output_percentage = session.run([network.prediction, network.output_percentage], feed_dict={x:next_batch['images']})
                results.append([testing_labels[step],output_percentage])

            score_top1 = calc_score_top1(results, output_values)
            score_top5 = calc_score_top5(results, output_values)
            print('\n- Risultati -\n')
            print('- Risultati -\n', file=f)
            print('# TOP 1 #')
            print('# TOP 1 #', file=f)
            print('Corrette:\t' + str(score_top1))
            print('Corrette:\t' + str(score_top1), file=f)
            print('Totali:\t' + str(total_number))
            print('Totali:\t' + str(total_number), file=f)
            print('\nPrecisione: ' + str(score_top1/(total_number)))
            print('\nPrecisione: ' + str(score_top1/(total_number)), file=f)
            print('\n\n\n# TOP 5 #')
            print('\n\n\n# TOP 5 #', file=f)
            print('Corrette:\t' + str(score_top5))
            print('Corrette:\t' + str(score_top5), file=f)
            print('Totali:\t' + str(total_number))
            print('Totali:\t' + str(total_number), file=f)
            print('\nPrecisione: ' + str(score_top5/(total_number)))
            print('\nPrecisione: ' + str(score_top5/(total_number)), file=f)


            print("\n## Log di predict score in: "+ file_log)
