
# Tampery App
Tampery is a software used to recognize tampered images. We use three different techniques to extract features from images to classify them as pristine or tampered.
We also deployed this software as an android application. 
 ## Authors
[Antonio Spina](https://github.com/antonio-sp) [Andrea Mengascini](https://github.com/andrea-mengascini) 
## Citations
Dataset: [Casia Dataset](https://res.mdpi.com/symmetry/symmetry-11-00083/article_deploy/symmetry-11-00083.pdf)

NoisePrint: [Noiseprint Model](https://grip-unina.github.io/noiseprint/)

SRM: [SRM Filter Kernel](https://openaccess.thecvf.com/content_cvpr_2018/papers/Zhou_Learning_Rich_Features_CVPR_2018_paper.pdf)

## Instructions
- Run the notebook "SD.ipynb" in "Sistemi-Digitali-M" in order to train the network.

## Example Images
 <figure>
  <img src="img/4_img.png" alt="drawing" width="200"/>
  <figcaption>RGB Image</figcaption>
</figure>
 <figure>
  <img src="img/4_noiseprint.png" alt="drawing" width="200"/>
  <figcaption>Noiseprint Map</figcaption>
</figure>
 <figure>
  <img src="img/4_srm.png" alt="drawing" width="200"/>
  <figcaption>SRM Map</figcaption>
</figure>

## Android Application

### Screenshot
<p align="center">
 <img src="img/1.jpg" alt="drawing" width="200"/>
 <img src="img/2.jpg" alt="drawing" width="200"/>
 <img src="img/3.jpg" alt="drawing" width="200"/>
</p>

### Chaquopy
In order to extract the noiseprint map on Android we used the Chaquopy plugin to execute python code in Android.

Python libraries used in chaquopy: 
- Pillow
- numpy
- tensorflow
- imageio
- scipy
- opencv-python
