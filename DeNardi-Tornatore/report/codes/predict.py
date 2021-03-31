path_model = "model.tflite"

def myconverter(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, datetime.datetime):
        return obj.__str__()

def predict_model(images, frames):
    data_json = []

    # Load the TFLite model and allocate tensors.
    interpreter = tf.lite.Interpreter(model_path=path_model)
    interpreter.allocate_tensors()

    # Get input and output tensors.
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    x = 0
    for i in range(images.shape[0]):
        if(i in frames):
            input_data = images[i].reshape(1, images.shape[1], images.shape[2], images.shape[3])

            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()

            output_data = interpreter.get_tensor(output_details[0]['index'])

            b = np.zeros_like(np.squeeze(output_data))
            b[np.arange(len(np.squeeze(output_data))), np.argmax(np.squeeze(output_data),axis=-1)] = 1

            value = np.argmax(b.astype('uint8'), axis=1)
            data_json.append({'tab_x' : x, 'value' : value})

            x += 1

    return json.dumps(data_json, default=myconverter)