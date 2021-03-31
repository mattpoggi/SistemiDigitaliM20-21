outpututput_directory_path = './output'

# the model_dir states where the graph and checkpoint files
# will be saved to
estimator_model = tf.keras.estimator.model_to_estimator(keras_model = model, model_dir = output_directory_path)

def input_function(features,labels=None,shuffle=False):
    input_fn = tf.estimator.inputs.numpy_input_fn(
        x={"conv2d_1_input": features},
        y=labels,
        shuffle=shuffle,
        batch_size = 128,
        num_epochs = 30
    )
    return input_fn
  
estimator_model.train(input_fn = input_function(X_train,y_train,True))
