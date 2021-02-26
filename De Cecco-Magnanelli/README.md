# NeoMap
NeoMap is a simple Android app to help people prevent skin cancer.
This app allows users to classify some of the most frequent types of skin cancers, and it takes advantage of convolutional neural networks.

## Author

[Jasmin De Cecco](https://github.com/jasmindc), [Lorenzo Magnanelli](https://github.com/rolench)

## Dataset
The dataset used for this project is ["ISIC 2019: Training"](https://challenge.isic-archive.com/data#2019) which classify dermoscopic images among eight different diagnostic categories:
1. Melanoma
2. Melanocytic nevus
3. Basal cell carcinoma
4. Actinic keratosis
5. Benign keratosis
6. Dermatofibroma
7. Vascular lesion
8. Squamous cell carcinoma

It contains 255331 images with different resolutions taken from various devices. Moreover, due to the severe class imbalance of real-world dataset, it has been necessary to make some operations for having uniformity across the images (cropout black areas, [Shades of Gray color constancy algorithm](https://www.kaggle.com/apacheco/shades-of-gray-color-constancy) and final resize) and for reaching the number of 6000 images per category.

In the end, we have split all the images into training set (60%), validation set (20%) and test set (20%). [Here](https://bit.ly/2P8CSm9) you can find the modified dataset.

## Neural Networks
Used tools: 
- Tensorflow 2.x 
-	Keras

Among the trained networks, we have chosen Xception and MobilenetV2, the first is the most accurate with an accuracy of 94.4%, and the other is the lightest (14.4 MB) model beyond being the one optimized for mobiles.
The input shape is 299x299x3 for Xception and 224x224x3 for MobilenetV2.

Finally, these networks have been converted to Tensorflow Lite models using different quantization strategies.

## Performance
We have tested the quantized models on Huawei p20 lite and Samsung Galaxy S10e using not only CPU but also the following delegates:
-	GPU
-	NNAPI
-	[XNNPACK](https://github.com/google/XNNPACK)

CPU and XNNPACK have been tested with 4 threads. 

Here there are the best results measured in milliseconds:

  **GPU Samsung Galaxy S10e**

|   | float32 | float16 | int8
|---|----------|------------|---------
MobileNetV2 | 11.2 | 12.6 | 15.5
Xception | 109.6 | 92 | 233.1

  **XNNPACK Huawei p20 lite**

|   | float32 | float16 | int8
|---|----------|------------|---------
MobileNetV2 | 54.6 | 52.6 | 40.6
Xception | 922.4 | 908.1 | 586.4

Despite the different quantizations, the accuracy of the tflite models has not changed compared to the Tensorflow models in all cases except Xception int8. In fact, in this case, accuracy is 87% instead of 94.4%. 

## Inference
These are the steps followed by the application to do the inference:
1.	load the model with loadMappedFile and labels with loadLabels
2.	create and add the chosen delegate to tfliteOptions object
3.	create a tflite interpreter with the previews options
4.	define input and output tensors
5.	preprocessing input and output related to the quantized strategy
6.	inference and return the map of the labels-probability

## Android application
On the first page of the application, there is a ListView that shows the different skin cancers. The user can click on each field to reach the relative Wikipedia page. On the bottom of this page, there is a button to load an image from the camera or another folder of the phone. The loaded image can also be cropped, rotated, and flipped (the bigger the crop, the better the prediction). Then, the user can go on with the inference where several settings can be configured, in particular: the model, the number of threads, and the delegate.

To properly run the app, you can download the models [here](https://bit.ly/3uxfnmW) and copy them into NeoMap\app\src\main\assets folder.

## Useful links
To load and crop an image: https://github.com/ArthurHub/Android-Image-Cropper

Shades of Gray color constancy C++: https://github.com/pi19404/m19404/tree/master/ColorConstancy
