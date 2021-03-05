import pandas as pd
import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras.layers import Dense
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ModelCheckpoint
import math
import time
import cv2
import itertools
import os
import shutil
import random
from tensorflow.keras import backend as K

def coeff_determination(y_true, y_pred):
    from keras import backend as K
    SS_res =  K.sum(K.square( y_true-y_pred ))
    SS_tot = K.sum(K.square( y_true - K.mean(y_true) ) )
    return ( 1 - SS_res/(SS_tot + K.epsilon()) )





#CaricoCSV
training_csv = pd.read_csv('Manually_CSV/new_training.csv')
validation_csv = pd.read_csv('Manually_CSV/new_validation.csv')
print("PREDATAGEN")
train_datagen = ImageDataGenerator(rescale=1./255)
test_datagen = ImageDataGenerator(rescale=1./255)

print("PRETRAIN")
train_generator= train_datagen.flow_from_dataframe(
    dataframe=training_csv,
    directory="Manually_Annotated_Images//",
    x_col="subDirectory_filePath",
    y_col="valence",
    weight_col=None,
    target_size=(123, 123),
    color_mode="rgb",
    class_mode="raw",
    batch_size=128,
    subset=None,
    interpolation="nearest",
    validate_filenames=True,
)

validation_generator = test_datagen.flow_from_dataframe(
    dataframe=validation_csv,
    directory="Manually_Annotated_Images//",
    x_col="subDirectory_filePath",
    y_col="valence",
    weight_col=None,
    target_size=(123, 123),
    color_mode="rgb",
    class_mode="raw",
    batch_size=128,
    subset=None,
    interpolation="nearest",
    validate_filenames=True,
)

mobile = tf.keras.applications.MobileNetV2(
	input_shape=(123,123,3),
	alpha=1.0,
	include_top=False,
	weights="imagenet",
	input_tensor=None,
	pooling='avg'
)

x=keras.layers.Dense(1,activation='linear',use_bias='True',name='Logits')(mobile.output)
model=Model(inputs=mobile.inputs, outputs=x)

opt= keras.optimizers.SGD(learning_rate=0.001)

model.compile(
        loss=tf.keras.losses.MeanSquaredError(),
        optimizer=opt,
        metrics=[coeff_determination]
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
                    )