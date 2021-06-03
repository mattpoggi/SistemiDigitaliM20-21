# Object Detection Training on Custom Dataset of a neural network (ssd_mobilenet_v1) and obtaining TFLite model.
### Repository: <a href="https://github.com/P-damicis/object_detection_ssd.git">P-damicis/object_detection_ssd</a>
### Author: <a href="https://github.com/P-damicis">Pier Domenico d'Amicis</a>
<br>
In this repository there are some files needed to train a neural network for object detection that exploits the Tensorflow API.
<ol>
  <li>get your custom dataset
  <li>upload it to <i><a href="roboflow.com">roboflow.com</a></i>
  <li>open COLAB notebook <b>MobileNet_ssd_Object_Detection.ipynb</b>
  <li>follow the instructions
  <li>enjoy
</ol>

At the end of the execution you will have obtained a TFLite model to use in your mobile application.
<ul>
  <li>Upload TFLite model on your Android Studio project, as below<br> 
    <img src="https://github.com/P-damicis/object_detection_ssd/blob/master/imgs/load%20tflite.PNG" height="350px" widht="300px" ><br><br>
 
  <li>Get the automatically generated code to perform the inference<br>
    <img src="https://github.com/P-damicis/object_detection_ssd/blob/master/imgs/mobilenet.PNG" height="300px" widht="350px"> <br><br>
</ul>


### Example of application:
<br>
<table style="margin-left: auto; margin-right: auto;">
  <tr>
    <td>
      <img src="https://github.com/P-damicis/object_detection_ssd/blob/master/imgs/oki2.jpg" width="60%" height="60%" >
    </td>
    <td>
      <img src="https://github.com/P-damicis/object_detection_ssd/blob/master/imgs/takenNoquant.jpg" width="60%" height="60%" >
    </td>
  </tr>
</table>

<b><a href="https://liveunibo-my.sharepoint.com/personal/pierdomenico_damicis_studio_unibo_it/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fpierdomenico%5Fdamicis%5Fstudio%5Funibo%5Fit%2FDocuments%2FSistemi%20Digitali%2Fsample%5Ffinal%2Emp4&parent=%2Fpersonal%2Fpierdomenico%5Fdamicis%5Fstudio%5Funibo%5Fit%2FDocuments%2FSistemi%20Digitali&originalPath=aHR0cHM6Ly9saXZldW5pYm8tbXkuc2hhcmVwb2ludC5jb20vOnY6L2cvcGVyc29uYWwvcGllcmRvbWVuaWNvX2RhbWljaXNfc3R1ZGlvX3VuaWJvX2l0L0VVRWZxbzhtcWxWSWdpWFNlb3ItQ3B3QlM3cV9nUDhLSDFKNF9jNUNibkJ0MlE%5FcnRpbWU9dXJBWkFPUUUyVWc">Video of usage</a></b>
