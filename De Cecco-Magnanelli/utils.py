import csv
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Activation, Dense, Flatten, BatchNormalization, Conv2D, MaxPool2D, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.metrics import categorical_crossentropy
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import confusion_matrix
import itertools
import os
import cv2
import random
import shutil
import random
import glob
import matplotlib.pyplot as plt
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

shape_dict = {
    "XCEPTION": (299, 299),
    "VGG16": (224, 224),
    "ALEXNET": (224, 224),
    "RESNET50V2": (224, 224),
    "INCEPTIONV3": (299, 299),
    "MOBILENETV2":  (224, 224),
    "DENSENET169": (224, 224),
    "NASNETMOBILE": (224, 224),
    "NASNETLARGE": (331, 331),
    "EFFICIENTNETB0": (224, 224),
    "EFFICIENTNETB1": (240, 240),
    "EFFICIENTNETB2": (260, 260),
    "EFFICIENTNETB3": (300, 300),
    "EFFICIENTNETB4": (380, 380),
    "EFFICIENTNETB5": (456, 456),
    "EFFICIENTNETB6": (528, 528),
    "EFFICIENTNETB7": (600, 600)
}

# **Utility function**


def create_dir(path):
    """
    create dir if not exists
    """
    if not os.path.exists(path):
        os.makedirs(path)


def count_params(model):
    """
    counts trainable and non trainable params
    """
    non_trainable_params = np.sum(np.prod(v.get_shape().as_list())
                                  for v in model.non_trainable_weights)
    trainable_params = np.sum(np.prod(v.get_shape().as_list())
                              for v in model.trainable_weights)
    return {'non_trainable_params': non_trainable_params, 'trainable_params': trainable_params}


def plotImages(images_arr):
    fig, axes = plt.subplots(1, 10, figsize=(20, 20))
    axes = axes.flatten()
    for img, ax in zip(images_arr, axes):
        ax.imshow(img)
        ax.axis('off')
    plt.tight_layout()
    plt.show()


def random_contrast(img):
    """
    applies random contrast to img
    """
    alpha = random.uniform(0.8, 1.2)
    # alpha modify contrast, beta modify brightness
    img = cv2.convertScaleAbs(img, alpha=alpha, beta=0)
    return np.multiply(img, 1/255.)

# convertScaleAbs:
# for y in range(image.shape[0]):
#     for x in range(image.shape[1]):
#         for c in range(image.shape[2]):
#             new_image[y,x,c] = np.clip(alpha*image[y,x,c] + beta, 0, 255)


# save info each epoch: num epoch, loss, accuracy
class LogsCallback(keras.callbacks.Callback):
    def __init__(self, info_file, weights_dir, freq=10):
        super(LogsCallback, self).__init__()
        self.freq = freq
        self.info_file = info_file
        self.weights_dir = weights_dir

    def on_epoch_end(self, epoch, logs=None):
        info = []
        epoch += 1
        if not os.path.exists(self.info_file):
            columns = ['epoch']
            columns += list(logs.keys())
            columns.append('val_' + columns[1])
            columns.append('val_' + columns[2])
            with open(self.info_file, 'w') as f:
                wr = csv.writer(f, delimiter=",")
                wr.writerow(columns)

        info.append(epoch)
        info += list(logs.values())[:2]

        if epoch % self.freq == 0:
            info += list(logs.values())[-2:]

        with open(self.info_file, 'a') as f:
            wr = csv.writer(f, delimiter=",")
            wr.writerow(info)


def set_callbacks(checkpoint_file, tensorboard_file, log_file, dir_weights_file, freq=10):
    res = []
    # save model each epoch
    checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
        # overwrite everytime
        filepath=checkpoint_file,
        # full model is saved, so we can continue to train from that
        save_weights_only=False,
        monitor='val_categorical_accuracy',
        mode='max',
        save_best_only=False,
        verbose=1)
    res.append(checkpoint_callback)

    # tensorboard
    tb_callback = tf.keras.callbacks.TensorBoard(
        tensorboard_file,
        update_freq='epoch')
    res.append(tb_callback)

    log_callback = LogsCallback(log_file, dir_weights_file, freq)
    res.append(log_callback)
    return res


def calc_init_epoch(logfile, freq=10):
    log = pd.read_csv(logfile)
    columns = list(log.columns)
    init_epoch = log[columns[0]].last_valid_index() + 1
    print('initial epoch {}'.format(init_epoch))

    return init_epoch


def plot_confusion_matrix(cm, classes,
                          filename,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots and saves the confusion matrix.
    Normalization can be applied by setting 'normalize=True'
    """

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print("Confusion matrix, without normalization")

    print(cm)

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

        plt.tight_layout()
        plt.ylabel('True label')
        plt.xlabel('Predicted label')
        plt.savefig(filename)


# create and save loss and accuracy graphs
def save_graphs(input, out_dir, freq=10):
    create_dir(out_dir)

    log = pd.read_csv(input)
    columns = list(log.columns)

    epochs = list(log[columns[0]])
    loss = list(log[columns[1]])
    acc = list(log[columns[2]])
    val_loss = list(log[columns[3]].dropna())
    val_acc = list(log[columns[4]].dropna())

    x = epochs
    x_val = np.arange(freq, len(epochs) + freq, freq)

    y_acc = acc
    y_val_acc = val_acc

    fig, ax1 = plt.subplots()
    ax1.plot(x, y_acc, color='orange', label='accuracy')
    plt.xticks(np.arange(0, len(x) + freq, freq))
    ax1.plot(x_val, y_val_acc, color='blue', label='val_accuracy')
    legend = ax1.legend()
    plt.xlabel('epochs')
    plt.ylabel('accuracy')
    plt.title('Epoch - Accuracy Graph')
    plt.grid()
    plt.savefig(os.path.join(out_dir, 'accuracy_graph'))

    y_loss = loss
    y_val_loss = val_loss

    fig, ax2 = plt.subplots()
    ax2.plot(x, y_loss, color='orange', label='loss')
    plt.xticks(np.arange(0, len(x) + freq, freq))
    ax2.plot(x_val, y_val_loss, color='blue', label='val_loss')
    legend = ax2.legend()
    plt.xlabel('epochs')
    plt.ylabel('loss')
    plt.title('Epoch - Loss Graph')
    plt.grid()
    plt.savefig(os.path.join(out_dir, 'loss_graph'))


def visualize_results(history):
    # Plot the accuracy and loss curves
    acc = history.history['acc']
    val_acc = history.history['val_acc']
    loss = history.history['loss']
    val_loss = history.history['val_loss']

    epochs = range(len(acc))

    plt.plot(epochs, acc, 'b', label='Training acc')
    plt.plot(epochs, val_acc, 'r', label='Validation acc')
    plt.title('Training and validation accuracy')
    plt.legend()

    plt.figure()

    plt.plot(epochs, loss, 'b', label='Training loss')
    plt.plot(epochs, val_loss, 'r', label='Validation loss')
    plt.title('Training and validation loss')
    plt.legend()

    plt.show()


def test_final_model(path_to_final_model, test_batches, res_file, debug, img_dir):
    if os.path.exists(path_to_final_model):
        final_model = keras.models.load_model(path_to_final_model)

        test_labels = test_batches.classes
        print("Evaluate on test data")
        results = final_model.evaluate(test_batches)
        print("test loss, test acc:", results)

        with open(res_file, 'w') as f:
            f.write("test loss, test acc: " + str(results))
        print("Predictions on test data")
        predictions = final_model.predict(x=test_batches, verbose=1)
        # plot and save confusion matrix
        cm = confusion_matrix(y_true=test_labels,
                              y_pred=predictions.argmax(axis=1))

        print('classi: {}\n'.format(test_batches.class_indices))

        filename = os.path.join(img_dir, 'conf_mat')
        cm_plot_labels = test_batches.class_indices.keys()
        plot_confusion_matrix(cm=cm, classes=cm_plot_labels,
                              filename=filename, title='Confusion Matrix')

        # plot and save accuray and loss graphs
        save_graphs(debug, img_dir)

    else:
        print('{} not exists'.format(path_to_final_model))
