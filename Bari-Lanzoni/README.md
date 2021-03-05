# EmotionHub

This is an Android app which recognises emotions from facial images in two different ways:
- the main emotion according to Ekman's emotion model

![Main Emotions](/Bari-Lanzoni/Images/Emotions7.jpg)

- valence and arousal values from Russel's dimensional model
![Emotion Wheel](/Bari-Lanzoni/Images/The-2-D-Emotion-Wheel.png)

## Authors

### [Nicolò Bari](https://github.com/nicobari30)

### [Davide Lanzoni](https://github.com/Lanzo98)

## Models

We used MobileNetV2 (123x123 rgb) both for dimensional model (one for valence and another for arousal) and categorical model (main emotions).

About the net: [MobileNetV2](https://arxiv.org/abs/1801.04381)


## Dataset

[AffectNet: A Database for Facial Expression, Valence, and Arousal Computing in the Wild](http://mohammadmahoor.com/affectnet/)

## Working app snapshot

![Main Screen](/Bari-Lanzoni/Images/MainScreen.png)
![Detection 1](/Bari-Lanzoni/Images/Detection1.png)
![Detection 2](/Bari-Lanzoni/Images/Detection2.png)
