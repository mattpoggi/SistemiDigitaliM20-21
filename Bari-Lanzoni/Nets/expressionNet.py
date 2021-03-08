import numpy as np
import pandas as pd
import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.metrics import categorical_crossentropy
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint
from sklearn.utils import class_weight
import math
import time
import cv2
import itertools
import os
import shutil
import random
from tensorflow.keras import backend as K







#CaricoCSV
training_csv = pd.read_csv('Manually_CSV/training.csv',dtype=str)
validation_csv = pd.read_csv('Manually_CSV/validation.csv',dtype=str)
print("PREDATAGEN")
train_datagen = ImageDataGenerator(rescale=1./255, horizontal_flip=True, rotation_range=30,brightness_range=[0.6,1.4], featurewise_center=True )
test_datagen = ImageDataGenerator(rescale=1./255, featurewise_center=True)

train_datagen.mean = np.array([0.53990436 , 0.4405486  , 0.39328504], dtype=np.float32).reshape((1,1,3))
test_datagen.mean = np.array([0.53990436 , 0.4405486  , 0.39328504], dtype=np.float32).reshape((1,1,3))


print("PRETRAIN")
train_generator= train_datagen.flow_from_dataframe(
    dataframe=training_csv,
    directory="Manually_Annotated_Images//",
    x_col="subDirectory_filePath",
    y_col="expression",
    weight_col=None,
    target_size=(123, 123),
    color_mode="rgb",
    class_mode="categorical",
    batch_size=64,
    subset=None,
    interpolation="nearest",
    validate_filenames=True,
    classes=["0","1","2","3","4","5","6","7","8","9","10"]
    )
    
validation_generator = test_datagen.flow_from_dataframe(
    dataframe=validation_csv,
    directory="Manually_Annotated_Images//",
    x_col="subDirectory_filePath",
    y_col="expression",
    weight_col=None,
    target_size=(123, 123),
    color_mode="rgb",
    class_mode="categorical",
    batch_size=64,
    subset=None,
    interpolation="nearest",
    validate_filenames=True,
    classes=["0","1","2","3","4","5","6","7","8","9","10"]
)

class_weights = class_weight.compute_class_weight('balanced',np.unique(train_generator.classes),train_generator.classes)
print(class_weights)

weight = {i: class_weights[i] for i in range(11)}


model = tf.keras.applications.MobileNetV2(
	input_shape=(123,123,3),
	include_top=True,
	weights=None,
	input_tensor=None,
	pooling='max',
    classes=11,
    classifier_activation="softmax",
)


opt= keras.optimizers.Adam(learning_rate=0.001)

model.compile(
        loss='categorical_crossentropy',
        optimizer=opt,
        metrics=['accuracy']
        )

model.summary()

checkpoint = ModelCheckpoint('model.h5', save_best_only=True)

STEP_SIZE_TRAIN=train_generator.n//train_generator.batch_size
STEP_SIZE_VALID=validation_generator.n//validation_generator.batch_size

history= model.fit(train_generator,
                    epochs=100,
                    verbose=1,
                    callbacks=[checkpoint],
                    validation_data=validation_generator,
                    shuffle=True,
                    steps_per_epoch=STEP_SIZE_TRAIN,                    
                    validation_steps=STEP_SIZE_VALID,
                    class_weight=weight
                  )