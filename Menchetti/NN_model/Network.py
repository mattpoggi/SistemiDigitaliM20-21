import tensorflow as tf

# Network
class DBR_Network(object):
    def __init__(self, x, labels=None, is_training=True):
        self.is_training = is_training
        self.input = x
        self.labels = labels
        self.loss = None
        self.output = None
        self.output_percentage = None

        self._build_network()

        if not self.is_training:
            return

        self._build_loss()


    def _build_network(self):
        ''' Build the network '''
        with tf.variable_scope('build_network'):
            #input shape: (128,128,128,3)
            batch = self.input.get_shape().as_list()[0]
            l1 = self.conv2d(self.input, kernel_shape=[3,3,3,3], bias_shape=[3], name='L1')
            print('L1 shape: ', l1.get_shape()) #L1 shape: (128,128,128,3)
            l2 = tf.nn.max_pool(l1, ksize=[1,2,2,1], strides=[1,2,2,1], padding='SAME', name='L2')
            print('L2 shape: ', l2.get_shape()) #L2 shape: (128,64,64,3)
            l2 = tf.nn.tanh(l2)

            l3 = self.conv2d(l2, kernel_shape=[3,3,3,3], bias_shape=[3], name='L3')
            print('L3 shape: ', l3.get_shape()) #L3 shape: (128,64,64,3)
            l4 = tf.nn.max_pool(l3, ksize=[1,2,2,1], strides=[1,2,2,1], padding='SAME', name='L4')
            print('L4 shape: ', l4.get_shape()) #L4 shape: (128,32,32,3)
            l4 = tf.nn.tanh(l4)

            l5 = self.conv2d(l4, kernel_shape=[3,3,3,3], bias_shape=[3], name='L5')
            print('L5 shape: ', l5.get_shape()) #L5 shape: (128,32,32,3)
            l6 = tf.nn.max_pool(l5, ksize=[1,2,2,1], strides=[1,2,2,1], padding='SAME', name='L6')
            print('L6 shape: ', l6.get_shape()) #L6 shape: (128,16,16,3)
            l6 = tf.nn.tanh(l6)


            l6 = tf.reshape(l6,[batch, -1]) #Reshape shape: (128,768)
            print('## Reshape shape: ', l6.get_shape())

            l7 = tf.contrib.layers.fully_connected(l6, num_outputs=360, activation_fn=tf.nn.tanh)
            print('L7 shape: ', l7.get_shape()) #L7 shape: (128,360)

            l7bis = tf.contrib.layers.fully_connected(l7, num_outputs=120, activation_fn=tf.nn.tanh)
            print('L7bis shape: ', l7bis.get_shape()) #L7bis shape: (128,120)

            self.output = tf.contrib.layers.fully_connected(l7bis, num_outputs=10, activation_fn=None)
            print('output shape: ', self.output.get_shape()) #output shape: (128,10)
            self.output_percentage = tf.squeeze(tf.nn.softmax(self.output))
            print('output_percentage shape: ', self.output_percentage.get_shape()) #output_percentage shape: (128,10)
            self.prediction = tf.squeeze(tf.argmax(self.output, axis=-1))

    def _build_loss(self):
        ''' Get the loss value '''
        with tf.variable_scope('build_loss'):
            cross_entropy_loss = tf.nn.softmax_cross_entropy_with_logits(logits=self.output, labels=self.labels)
            self.loss = tf.reduce_mean(cross_entropy_loss)

    def conv2d(self, x, kernel_shape, bias_shape, strides=1, padding='SAME', name='conv2D'):
        ''' Block for 2D Convolution '''
        with tf.variable_scope(name):
            weights = tf.get_variable("weights", kernel_shape, initializer=tf.contrib.layers.xavier_initializer(), dtype=tf.float32)
            biases = tf.get_variable("biases", bias_shape, initializer=tf.truncated_normal_initializer(), dtype=tf.float32)
            output = tf.nn.conv2d(x, weights, strides=[1, strides, strides, 1], padding=padding)
            output = tf.nn.bias_add(output, biases)
            return output
