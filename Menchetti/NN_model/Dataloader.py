import tensorflow as tf
import os
import pandas as pd

# Dataloader
class Dataloader(object):
    def __init__(self, data_path, csv_output_values, img_size, mode='training', batch_size=1):
        self.data_path = data_path
        self.output_values = pd.read_csv(csv_output_values)['UNIQUE_BREED']
        self.mode = mode
        self.img_size = img_size
        self.batch_size = batch_size
        self.dataset = self.prepare_dataset()
        if self.mode == 'training':
            self.iterator =self.dataset.make_initializable_iterator()
        else:
            self.iterator = self.dataset.make_one_shot_iterator()

    def prepare_dataset(self):
        with tf.variable_scope('prepare_dataset'):
            dataset = tf.data.TextLineDataset(os.path.join(self.data_path, 'train_labels.txt'))
            if self.mode == 'training':
                dataset = dataset.shuffle(buffer_size=60000)
                dataset = dataset.map(self.prepare_batch, num_parallel_calls=8)
                dataset = dataset.repeat()
                dataset = dataset.prefetch(30)
            else:
                dataset = dataset.map(self.prepare_batch)
            dataset = dataset.batch(self.batch_size, drop_remainder=True)
            return dataset

    def prepare_batch(self, line):
        with tf.variable_scope("Dataloader"):
            split_line = tf.string_split([line]).values
            img   = tf.strings.join([self.data_path, 'images/', split_line[0]])
            #ONE HOT ENCODE for Strings
            matches = tf.stack([tf.equal(split_line[1], s) for s in self.output_values], axis=-1)
            label = tf.cast(matches, tf.float32)
            img   = self.read_jpg_image(img)
        return [img, label]

    def read_jpg_image(self, path):
        with tf.variable_scope("read_jpg_image"):
            image  = tf.image.decode_jpeg(tf.io.read_file(path))
            image  = tf.image.convert_image_dtype(image,  tf.float32)
            image.set_shape(list(self.img_size))
            return image

    def get_next_batch(self):
        ''' Return the next batch. Override to show portion of the full batch '''
        with tf.variable_scope('get_next_batch'):
            return self.iterator.get_next()

    def initialize(self, session):
        with tf.variable_scope('initialize'):
            session.run(self.iterator.initializer)
