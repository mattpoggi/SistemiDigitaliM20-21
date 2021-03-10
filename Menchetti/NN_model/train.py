import tensorflow as tf
import numpy as np
import pandas as pd
import time

from Dataloader import Dataloader
from Network import DBR_Network


# -- Variabili globali --
# Paths
modelName = 'DBR1.9.8'
trained_model_path = './trainedModel/'
csv_output_values = '../../_DBR_dataset_128px_v4/_breeds/unique_breed_translation.csv'
train_path = '../../_DBR_dataset_128px_v4/train/'
log_path = './logs/'

# Variabili
img_size = (128, 128, 3)      #dimensione immagini dataset

learning_rate = 1e-3
training_steps = 8000
batch_size = 128

output_values = pd.read_csv(csv_output_values)['UNIQUE_BREED']    #quali valori in uscita


# Training
if __name__ == '__main__':
    trainedModel = trained_model_path + modelName
    file_log = log_path + modelName + '-' + str(training_steps) + '_train_log.txt'

    with open(file_log, 'w') as f:
      global_step = tf.Variable(0, trainable=False)
      dataloader = Dataloader(data_path=train_path, csv_output_values=csv_output_values, img_size=img_size, batch_size=batch_size)
      imgs, labels = dataloader.get_next_batch()
      network = DBR_Network(x=imgs, labels=labels)
      optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
      loss = network.loss
      optimization_op = optimizer.minimize(loss)
      saver = tf.train.Saver()

      number_of_params = 0
      for variable in tf.trainable_variables():
          number_of_params += np.array(variable.get_shape().as_list()).prod()

      print("number of trainable parameters: {}".format(number_of_params))
      print("number of trainable parameters: {}".format(number_of_params), file=f)


      config = tf.ConfigProto(allow_soft_placement=True)
      start = time.time()
      best_accuracy = 0

      with tf.Session(config=config) as session:
          session.run(tf.global_variables_initializer())
          session.run(tf.local_variables_initializer())
          dataloader.initialize(session)
          #PROVA
          #labels_value = session.run([labels])
          #print('DANIELEEEE: ', labels_value)
          for step in range(training_steps):
              loss_value, _ = session.run([loss, optimization_op])
              elapsed_time = time.time() - start
              if step and step % 1000 == 0:
                  print('step:{}/{} | loss:{:7.6f} | elapsed time: {:2.0f}m:{:2.0f}s'.format(step, training_steps, loss_value, elapsed_time // (60), int(elapsed_time)%60))
                  print('step:{}/{} | loss:{:7.6f} | elapsed time: {:2.0f}m:{:2.0f}s'.format(step, training_steps, loss_value, elapsed_time // (60), int(elapsed_time)%60), file=f)
          saver.save(session, trainedModel, global_step=training_steps)

      print('Training ended!')
      print('Training ended!', file=f)

      print("\n## Log di training in: "+ file_log)
