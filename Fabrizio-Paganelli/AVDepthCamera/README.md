# AVDepthCamera

This is an iOS app merging two features:
 - a colour camera that uses a Core ML model for predicting number gestures (0 to 5);
 - a grayscale camera with a Core ML Model for predicting three hand gestures: *fist, palm, ok.*

## Models

We used MobileNetV2 (224x224 rgb) for both of the two versions. It's been retrained on each of the two datasets to recognise the appropriate label classes.

About the net: [MobileNetV2](https://arxiv.org/abs/1801.04381)

## Datasets

 Grayscale: [Multi-Modal Dataset for Hand Gesture Recognition](https://www.kaggle.com/adeshdalvi41/hand-signs)
  
 Colours: [Hand Gestures Dataset](https://www.kaggle.com/gti-upm/multimodhandgestrec)

