import tensorflow as tf

model = tf.keras.models.load_model("PATH/HDF5/MODEL")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()
open("converted_model_v12.tflite", "wb").write(tflite_model)