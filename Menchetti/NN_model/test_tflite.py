import numpy as np
import tensorflow as tf
import cv2



tflite_path = './_tflite/DBR1.9.8-8000.tflite'
image_test  = '../../_single_test/leonberg.jpg'


def resize_square_image_keep_ratio_border(img, desired_size):
    """
    img: img object cv2
    desired_size: intero
    """
    old_size = img.shape[:2] # old_size is in (height, width) format
    ratio = float(desired_size)/max(old_size)
    new_size = tuple([int(x*ratio) for x in old_size])

    # new_size should be in (width, height) format

    img = cv2.resize(img, (new_size[1], new_size[0]))

    delta_w = desired_size - new_size[1]
    delta_h = desired_size - new_size[0]
    top, bottom = delta_h//2, delta_h-(delta_h//2)
    left, right = delta_w//2, delta_w-(delta_w//2)

    color = [0, 0, 0]
    new_img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT,value=color)

    return new_img

def get_test_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #RESIZE IMAGE FOR PREDICT
    image = resize_square_image_keep_ratio_border(image, 128)
    image = image / 255.
    return np.expand_dims(image,0)


# Load TFLite model and allocate tensors.
interpreter = tf.lite.Interpreter(model_path=tflite_path)
interpreter.allocate_tensors()

# Get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Test model on random input data.
input_shape = input_details[0]['shape']
input_data = np.array(np.random.random_sample(input_shape), dtype=np.float32)
interpreter.set_tensor(input_details[0]['index'], input_data)

img = get_test_image(image_test)
new_img = img.astype('float32')
interpreter.set_tensor(input_details[0]['index'], new_img)

interpreter.invoke()

# The function `get_tensor()` returns a copy of the tensor data.
# Use `tensor()` in order to get a pointer to the tensor.
output_data = interpreter.get_tensor(output_details[0]['index'])

print('\n ## OUTPUT DATA:')
print(output_data)
