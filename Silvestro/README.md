# HeartBest
Android heart rate monitor.

This application uses [OpenCV](https://opencv.org/releases/) to find the location of the user's face and isolate the forehead region.

Data is collected from this location over time to estimate the user's heart rate.

This is done by measuring average optical intensity in the forehead location, in the subimage's green channel alone.

Physiological data can be estimated this way thanks to the optical absorption characteristics of oxyhaemoglobin.

### Repository [here](https://github.com/0ry0n/HeartBest)

### Author [Giuseppe Silvestro](https://github.com/0ry0n)

### Example
![](https://github.com/0ry0n/HeartBest/blob/main/screenshots/Face.jpg)

**Video demonstration [here](https://github.com/0ry0n/HeartBest/blob/main/screenshots)**
