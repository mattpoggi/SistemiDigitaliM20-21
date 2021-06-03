from tflite_runtime.interpreter import Interpreter
import numpy as np
import time
import argparse
import cv2


# Variabili globali
model_path = "DBR/DBR1.9.8-8000.tflite"
label_path = "DBR/IT_breeds.txt"




class Cane:
    def __init__(self, tipo, filename, razza1, percent1, razza2, percent2):
        self.tipo = tipo         #tipo = { 'invalido', 'puro', 'misto' }
        self.filename = filename
        self.razza1 = razza1
        self.percent1 = percent1
        self.razza2 = razza2
        self.percent2 = percent2

def get_dog_from_predictions_edited(array_predizioni, output_values, filename):
    massimo1 = np.max(array_predizioni)
    indice_massimo1 = np.where(array_predizioni == massimo1)[0][0]
    razza1 = output_values[indice_massimo1]

    array_predizioni = np.delete(array_predizioni, indice_massimo1)
    output_values = np.delete(output_values, indice_massimo1)

    massimo2 = np.max(array_predizioni)
    indice_massimo2 = np.where(array_predizioni == massimo2)[0][0]
    razza2 = output_values[indice_massimo2]

    dog = Cane('invalido', filename, razza1, massimo1, razza2, massimo2)

    limit = 1
    if (dog.percent1 < 0.7):
        dog.tipo = 'invalido'
    else:
        if (dog.percent1 >= 0.7 and dog.percent1 < 0.8):
            limit = 0.15 #15 %
        else:
          if (dog.percent1 >= 0.8 and dog.percent1 < 0.85):
              limit = 0.1 # 10 %
          else:
              if (dog.percent1 >= 0.85 and dog.percent1 < 0.9):
                  limit = 0.07 # 7 %
              else:
                  if (dog.percent1 >= 0.9 and dog.percent1 < 0.95):
                      limit = 0.04 # 4 %

        if (dog.percent2 >= limit):
            dog.tipo = 'misto'
        else:
            dog.tipo = 'puro'

    return dog


def print_human_readable_dog_deploy_edited(dog):
    if (dog.tipo == 'invalido'):
      return ('Non è stato riconosciuto un cane oppure<br />non è stata riconosciuta una razza di cane nota.')
    elif (dog.tipo == 'puro'):
      return ('Trovato un cane di razza pura.<br />Razza: ' + dog.razza1 + '<br />Precisione: %.1f'%(dog.percent1*100))
    elif (dog.tipo == 'misto'):
      return ('Trovato un cane di razza mista.<br />Razza1: ' + dog.razza1 +'<br />Precisione: %.1f'%(dog.percent1*100)
      + '<br /><br />Razza2: ' + dog.razza2 + '<br />Precisione: %.1f'%(dog.percent2*100))

def print_human_readable_dog_deploy_edited_2(dog):
    if (dog.tipo == 'invalido'):
      return ('Non è stato riconosciuto un cane oppure<br />non è stata riconosciuta una razza di cane nota.')
    elif (dog.tipo == 'puro'):
      return ('Trovato un cane di razza pura.<br />Razza: ' + dog.razza1)
    elif (dog.tipo == 'misto'):
      return ('Trovato un cane di razza mista.<br />Razza1: ' + dog.razza1 + '<br />Razza2: ' + dog.razza2)


def set_input_tensor(interpreter, image):
  tensor_index = interpreter.get_input_details()[0]['index']
  input_tensor = interpreter.tensor(tensor_index)()[0]
  input_tensor[:, :] = image

def classify_image(interpreter, image, top_k=1):
  set_input_tensor(interpreter, image)

  interpreter.invoke()
  output_details = interpreter.get_output_details()[0]
  output = interpreter.get_tensor(output_details['index'])
  return output

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

# -- Parser --
parser = argparse.ArgumentParser(description='DBR')
parser.add_argument('--fn', type=str, required=True, help='filename')
args = parser.parse_args()


interpreter = Interpreter(model_path)
#print("Model Loaded Successfully.")

interpreter.allocate_tensors()
_, height, width, _ = interpreter.get_input_details()[0]['shape']
#print("Image Shape (", width, ",", height, ")")

# Load an image to be classified.
image = get_test_image(args.fn)


# Classify the image.
time1 = time.time_ns()
output = classify_image(interpreter, image)
time2 = time.time_ns()
classification_time = time2-time1
#print("Time: " + str(classification_time))



labels = []
with open(label_path, 'r') as f:
    tmp = f.readlines()
    for l in tmp:
        labels.append(l.rstrip())


dog = get_dog_from_predictions_edited(np.squeeze(output), labels, args.fn)
res = print_human_readable_dog_deploy_edited(dog)
print(res)
