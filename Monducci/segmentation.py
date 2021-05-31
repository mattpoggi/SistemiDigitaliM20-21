import cv2
import numpy as np
import math
from tensorflow.keras.models import load_model
import tensorflow as tf

def make_square(im):
    x, y, c = im.shape
    if x<y:
        dif = y-x
        new_im = cv2.copyMakeBorder( im, math.ceil(dif/2.0), math.floor(dif/2.0), 0, 0, cv2.BORDER_REPLICATE, value=(255,255,255)) 
        return new_im
    elif x>y:
        dif = x-y
        new_im = cv2.copyMakeBorder( im, 0,0, math.ceil(dif/2.0), math.floor(dif/2.0), cv2.BORDER_REPLICATE, value=(255,255,255))
        return new_im
    else:
        return im

model = load_model("MODEL/PATH")
dic = ['!', '(', ')', '+', ',', '-', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '=', '[', ']', 'a', 'alpha', 'ascii_124', 'b', 'beta', 'c', 'cos', 'd', 'delta', 'div', 'e', 'exists', 'f', 'forall', 'forward_slash', 'g', 'gamma', 'geq', 'gt', 'h', 'i', 'in', 'infty', 'int', 'j', 'k', 'l', 'lambda', 'leq', 'lim', 'log', 'lt', 'm', 'mu', 'n', 'neq', 'o', 'p', 'phi', 'pi', 'pm', 'prime', 'q', 'r', 'rightarrow', 's', 'sigma', 'sin', 'sqrt', 'sum', 't', 'tan', 'theta', 'u', 'v', 'w', 'x', 'y', 'z', '{', '}']


img = cv2.imread("IMAGE/PATH/TEST")

#grayscale
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
cv2.waitKey(0)

#binarize 
ret,thresh = cv2.threshold(gray,127,255,cv2.THRESH_BINARY_INV)
cv2.waitKey(0)

#find contours
ctrs, hier = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

#sort contours
sorted_ctrs = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])

images = []

for i, ctr in enumerate(sorted_ctrs):
    # Get bounding box
    x, y, w, h = cv2.boundingRect(ctr)

    # Getting ROI
    roi = img[y:y+h, x:x+w]
    image = make_square(roi)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.resize(image, (45,45), interpolation = cv2.INTER_AREA)
    image = tf.expand_dims(image, 0)
    images.append(image)


preds = []

for image in images:
    pred = model.predict(image)
    preds.append(pred)

    
ris = ''    
for pred in preds:
    ris+=dic[np.argmax(pred)]

ris = ris.replace('--', "=")
print(ris)
