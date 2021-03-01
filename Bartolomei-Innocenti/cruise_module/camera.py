import numpy as np
import cv2 as cv
import utils_geom as gutils

class PinholeCamera:
    CONFIG_KEYS = ['width', 'height', 'fx', 'fy', 'cx', 'cy', 'D']

    @classmethod
    def fromConfig(cls, config):
        for key in cls.CONFIG_KEYS:
            if key not in config:
                return None

        width = config['width']
        height = config['height']
        fx = config['fx']
        fy = config['fy']
        cx = config['cx']
        cy = config['cy']
        D = config['D']
        return cls(width, height, fx, fy, cx, cy, D)

    def __init__(self, width, height, fx, fy, cx, cy, D): # D = [k1, k2, p1, p2, k3]    
        
        #TODO: check dei parametri

        D = np.array(D, dtype=np.float32) # np.array([k1, k2, p1, p2, k3])  distortion coefficients 
        
        self.config = {'width': width, 'height': height,
         'fx': fx, 'fy': fy,
          'cx': cx, 'cy': cy, 'D': D}
            
        self.distorted = np.linalg.norm(D) > 1e-10
        self.initialized = False  

        self.K = np.array([[fx, 0,cx],
                           [ 0,fy,cy],
                           [ 0, 0, 1]])

        self.Kinv = np.array([[1/fx,    0,-cx/fx],
                              [   0, 1/fy,-cy/fy],
                              [   0,    0,    1]])             
            
        self.init()    
        
    def init(self):
        if not self.initialized:
            self.initialized = True 

            if self.distorted:
                alpha = 1 # 1 -> Inserisce dei pixel neri per bilanciare la distorsione
                self.newK, self.roi = cv.getOptimalNewCameraMatrix(self.K, self.D, (self.width, self.height), alpha, (self.width, self.height)) 
                self.newKinv = np.linalg.inv(self.newK)

    @property
    def width(self):
        return self.config['width'] if 'width' in self.config else None
        
    @property
    def height(self):
        return self.config['height'] if 'height' in self.config else None

    @property
    def fx(self):
        return self.config['fx'] if 'fx' in self.config else None

    @property
    def fy(self):
        return self.config['fy'] if 'fy' in self.config else None

    @property
    def cx(self):
        return self.config['cx'] if 'cx' in self.config else None

    @property
    def cy(self):
        return self.config['cy'] if 'cy' in self.config else None

    @property
    def D(self):
        return self.config['D'] if 'D' in self.config else None

    def config(self, config):
        for key in config:
            if key in self.CONFIG_KEYS:
                self.config[key] = config[key]

    @property
    def status(self):
        return {**self.config, 'distorted': self.distorted, 'initialized': self.initialized}

    # project a 3D point or an array of 3D points (w.r.t. camera frame), of shape [Nx3]
    # out: Nx3 image points  (u, v, Z)  
    def project(self, xcs):
        if not isinstance(xcs, np.ndarray):
            return None
                   
        if self.distorted:
            projs = self.newK @ xcs.T
        else:
            projs = self.K @ xcs.T
        
        #Trasformazione delle coordinate omogenee in coordinate cartesiane.
        #Round delle coordinate XY
        projs[:2] = projs[:2] / projs[2]  
        projs[:2] = np.rint(projs[:2])
        projs = projs.astype(np.float32)
        projs = projs.T # Nx3
        
        #Maschera dei punti a infinito
        good_mask = np.where(projs[:, 2] != 0.0)

        return projs[good_mask]

    # unproject a 2D point or an array of 2D points  (w.r.t. camera frame), of shape [Nx2] + Depth of shape [Nx1]
    # out: Nx3 3D points
    def unproject(self, uvs, depth):

        uvs = gutils.add_ones(uvs)

        if self.distorted:
            unprojs = self.newKinv @ uvs.T
        else:
            unprojs = self.Kinv @ uvs.T

        unprojs = unprojs.T * depth

        return unprojs

    def getProjMtx(self, RtMtx):
        RtMtx = RtMtx[:3]

        if self.distorted:
            projMtx = self.newK @ RtMtx
        else:
            projMtx = self.K @ RtMtx
            
        return projMtx

    def undistortImage(self, image):
        h,  w = image.shape[:2]

        if self.height != h:
            raise Exception("Height not valid")

        if self.width != w:
            raise Exception("Width not valid")

        dst = image

        if self.distorted:
            #https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html
            # undistort
            dst = cv.undistort(image, self.K, self.D, None, self.newK)

            # crop the image
            x,y,w,h = self.roi
            dst = dst[y:y+h, x:x+w]

        return dst