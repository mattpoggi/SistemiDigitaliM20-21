"""
Richiedo in ingresso le matrici della camera, i frame della camera.
Restituisco in uscita una serie di punti tridimensionali relativi ai frame.

Funzioni utilizzate OPENCV: Ho bisogno dei parametri intrinseci ed estrinseci della camera.
- Shi-Tomasi: per trovare le features
- Lucas-Kanade: per fare il match delle features
- triangulatePoints(): per triangolare i punti in 3D rispetto ad un'origine comune.
"""

from defaults import Defaults
import logging
import numpy as np
import cv2 as cv
import utils_geom as gutils
from ssc import ssc
import time
import random
import math

#PYNQ Imports
from pynq import Overlay
from pynq import Xlnk

class FeatureTracker:

    overlayInputShape = (480 * 640, )
    overlayOutputShape = (8192, 10)

    @classmethod
    def loadOverlay(cls):
        cls.xlnk = Xlnk()
        cls.overlay = Overlay('/usr/local/lib/python3.6/dist-packages/ORB_FPGA/overlays/ORB_FPGA.bit')
        
        cls.dma_FAST = cls.overlay.axi_dma_FAST
        cls.dma_Gaus = cls.overlay.axi_dma_Gaus
        cls.dma_des = cls.overlay.axi_dma_des_2Mem

        cls.dma_des.recvchannel.start()
        cls.dma_FAST.sendchannel.start()
        cls.dma_Gaus.sendchannel.start()

        cls.src_buf = cls.xlnk.cma_array(shape=cls.overlayInputShape, dtype=np.uint8)
        cls.src_buf_np = np.frombuffer(cls.src_buf, dtype = np.uint8, count = -1)
        cls.des_buf = cls.xlnk.cma_array(shape=cls.overlayOutputShape, dtype=np.int32)

    @classmethod
    def processOverlay(cls, img):
        img = img.ravel()

        if img.shape == cls.overlayInputShape:
            np.copyto(cls.src_buf_np, img, casting='same_kind')
            cls.src_buf.invalidate()
            cls.dma_des.recvchannel.transfer(cls.des_buf)
            cls.dma_FAST.sendchannel.transfer(cls.src_buf)
            cls.dma_Gaus.sendchannel.transfer(cls.src_buf)
            cls.dma_Gaus.sendchannel.wait()
            cls.dma_FAST.sendchannel.wait()
            cls.dma_des.recvchannel.wait()
            cls.des_buf.flush()

            bytes_read=cls.dma_des.mmio.read(0x58)
            featurePointsNum = int(bytes_read/40) - 1
            points = cls.des_buf[0:(featurePointsNum-1)].copy()
            cls.des_buf.invalidate()

            return points

        return None

    @classmethod
    def stopOverlay(cls):
        cls.src_buf.freebuffer()
        cls.des_buf.freebuffer()
        cls.dma_des.recvchannel.stop()
        cls.dma_FAST.sendchannel.stop()
        cls.dma_Gaus.sendchannel.stop()

    def __init__(self):
        self.loggingName = "FeatureTracker"

        # params for ShiTomasi corner detection
        self.feature_params_shitomasi = dict( maxCorners = 200,
                            qualityLevel = 0.001,
                            minDistance = 4,
                            blockSize = 5 )

        # Parameters for lucas kanade optical flow
        self.lk_params = dict(winSize  = (21, 21), 
                              maxLevel = 5,
                              criteria = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 20, 0.03)) 

        FLANN_INDEX_KDTREE = 0
        FLANN_INDEX_LSH = 6  # Multi-Probe LSH: Efficient Indexing for High-Dimensional Similarity Search

        self.orb = cv.ORB_create(nfeatures=2000)
        #self.fast = cv.FastFeatureDetector_create()
        #self.fast.setNonmaxSuppression(0)
        
        self.index_params= dict(algorithm = FLANN_INDEX_LSH,  
                                table_number = 6,      # 12
                                key_size = 12,         # 20
                                multi_probe_level = 1) # 2
                
        self.search_params = dict(checks=50)   # or pass empty dictionary 

        self.flann = cv.FlannBasedMatcher(self.index_params, self.search_params)

        self.lowe_threshold = Defaults.lowe_threshold
        self.distance_threshold = Defaults.distance_threshold
        self.norm_threshold = Defaults.norm_threshold

        self.nIterations = Defaults.planeNIterations
        self.threshold = Defaults.planeThreshold

        self.detectTime = float('nan')
        self.computeTime = float('nan')
        self.flowTime = float('nan')
        self.triangulateTime = float('nan')
        self.ransacTime = float('nan')
        self.correctMatchesTime = float('nan')

    def detectAndCompute(self, img, roi = None):
        start = time.time()

        if roi is None:
            roi = (0,0,img.shape[1], img.shape[0])

        x,y,w,h = roi
        croppedImg = img[y:y+h, x:x+w]

        # find the keypoints with ORB
        kp = self.orb.detect(croppedImg, None)

        # find the keypoints with FAST
        #kp = self.fast.detect(croppedImg, None)

        logging.debug("{0} numero keypoints: {1}".format(self.loggingName, len(kp)))

        #Filtro i keypoints con SSC
        # keypoints should be sorted by strength in descending order before feeding to SSC to work correctly
        
        #def kpSortFunc(kpt):
        #    return kpt.response

        #kp.sort(reverse=True, key=kpSortFunc)
        #kp = ssc(kp, num_ret_points=1000, tolerance=0.5, cols=w, rows=h)

        startCompute = time.time()

        # compute the descriptors with ORB
        kp, des = self.orb.compute(img, kp)

        endCompute = time.time()
        self.computeTime = endCompute-startCompute
                
        #Ripristino a dimensione originale i keypoints
        kps = np.zeros((len(kp), 2), dtype=np.float32)#Nx2
        for i,p in enumerate(kp):
            kps[i] = np.array((p.pt[0] + x, p.pt[1] + y), dtype=np.float32)
        
        end = time.time()
        self.detectTime = (end - start) - self.computeTime

        return kps, des

    def detectShiTomasi(self, img, roi = None):
        start = time.time()

        if roi is None:
            roi = (0,0,img.shape[1], img.shape[0])

        x0,y0,w,h = roi
        croppedImg = img[y0:y0+h, x0:x0+w]

        #ShiTomasi corner detection
        kps = cv.goodFeaturesToTrack(croppedImg, mask = None, **self.feature_params_shitomasi)#Nx1x2
        
        #kps = cv.goodFeaturesToTrack(croppedImg, maxCorners=self.feature_params_shitomasi['maxCorners'],
        #            qualityLevel=self.feature_params_shitomasi['qualityLevel'],
        #            minDistance=self.feature_params_shitomasi['minDistance'],
        #            blockSize=self.feature_params_shitomasi['blockSize'], mask = None)#Nx1x2

        #Filtro i punti con SSC
        #kps = np.array(ssc(kps, num_ret_points=100, tolerance=0.1, cols=w, rows=h))

        #Ripristino a dimensione originale i keypoints
        for i,p in enumerate(kps):
            x,y = p.ravel()
            kps[i, 0] = np.array([x0 + x, y0 + y])

        kps = np.squeeze(kps)#Nx2

        end = time.time()
        self.detectTime = end - start

        return kps, None

    def computeFlow(self, img0, img1, p0, roi = None):
        """
        img0: immagine a bianco e nero: HxWx1
        img1: immagine a bianco e nero: HxWx1
        p0: features trovate in img0: Nx2 o Nx1x2
        restituisce p0: Kx2, p1: Kx2
        """

        if roi is None:
            roi = (0,0,img0.shape[1], img0.shape[0])

        start = time.time()

        p0 = np.reshape(p0, (-1, 1, 2))
        
        x0,y0,w,h = roi
        croppedImg0 = img0[y0:y0+h, x0:x0+w]
        croppedImg1 = img1[y0:y0+h, x0:x0+w]

        p0[:, 0, 0] = p0[:, 0, 0] - x0
        p0[:, 0, 1] = p0[:, 0, 1] - y0

        # calculate optical flow Lucas Kanade

        p1, st, err = cv.calcOpticalFlowPyrLK(croppedImg0, croppedImg1, p0, None, **self.lk_params)

        #logging.debug("{0} LK Err: {1}".format(self.loggingName, err))

        # calculate optical flow RLOF
        #img0 = cv.cvtColor(img0, cv.COLOR_GRAY2BGR)
        #img1 = cv.cvtColor(img1, cv.COLOR_GRAY2BGR)
        #p1, st, err = cv.optflow.calcOpticalFlowSparseRLOF(img0, img1, p0, None)
        #p1, st, err = cv.optflow.calcOpticalFlowSparseRLOF(img0, img1, p0, None)

        # Select good points
        good_new = p1[(st==1) & (err < 4.0)]#Nx2
        good_old = p0[(st==1) & (err < 4.0)]#Nx2

        p0[:, 0, 0] = p0[:, 0, 0] + x0
        p0[:, 0, 1] = p0[:, 0, 1] + y0

        good_new[:, 0] = good_new[:, 0] + x0
        good_new[:, 1] = good_new[:, 1] + y0

        good_old[:, 0] = good_old[:, 0] + x0
        good_old[:, 1] = good_old[:, 1] + y0

        end = time.time()
        self.flowTime = end - start

        return good_old, good_new

    def match(self, kp1, kp2, des1, des2):
    
        start = time.time()

        matches = self.flann.knnMatch(des1,des2,k=2)

        # Need to draw only good matches, so create a mask
        goodMatches = []

        # ratio test as per Lowe's paper
        for pair in matches:
            try:
                m, n = pair
                if m.distance < self.lowe_threshold*n.distance:
                    goodMatches.append(m)

            except ValueError:
                #logging.warn("{0} match ratio non riuscito non è una coppia: {1}".format(self.loggingName, pair))
                pass

        #Filtro distanza > threshold
        reallyGoodMatches = []

        for match in goodMatches:
            if match.distance > self.distance_threshold:
                reallyGoodMatches.append(match)

        #logging.info("{0} trovati {1} good matches".format(self.loggingName, len(reallyGoodMatches)))           

        end = time.time()
        self.matchTime = end - start

        return self.extractMatches(kp1, kp2, reallyGoodMatches)

    def extractMatches(self, kp1, kp2, matches):
        points2d1 = []
        points2d2 = []

        for match in matches:
            point2d1 = kp1[match.queryIdx]
            point2d2 = kp2[match.trainIdx]

            points2d1.append(point2d1)
            points2d2.append(point2d2)

        points2d1 = np.array(points2d1)
        points2d2 = np.array(points2d2)

        return points2d1, points2d2

    def triangulatePoints(self, points1, points2, P1, P2):
        """
        points1: Nx2
        points2: Nx2
        P1: 3x4
        P2: 3x4
        Return points3d (Nx4)
        """

        start = time.time()

        #Triangolazione dei punti:
        #Mi servono le matrici di proiezione dei frame e i punti trovati.

        #Triangolazione OpenCV
        p = cv.triangulatePoints(P1, P2, points1.T, points2.T) # 4xN

        #Triangolazione PYSLAM
        #p = gutils.triangulate_points(P1, P2, points1, points2) #Nx4
        #p = p.T

        #Trasformazione delle coordinate omogenee in coordinate cartesiane. Restituisco un Nx4
        p[:3] = p[:3] / p[3]
        p = p.T
        
        #logging.debug("Crash {0}: points2d: {1}, points3d: {2}".format(self.loggingName, (points1, points2), p))

        #Maschera dei punti non a infinito
        good_mask = np.where(p[:, 3] != 0.0)

        #logging.info("{0} trovati {1} 3d points".format(self.loggingName, good_mask.shape[0]))   

        end = time.time()
        self.triangulateTime = end - start

        return p[good_mask]

    def correctMatches(self, p1, p2):
        if p1.shape[0] >= 8 and p1.shape[0] == p2.shape[0]:
            start = time.time()
            F, mask = cv.findFundamentalMat(p1, p2, method=cv.RANSAC, ransacReprojThreshold=0.05, confidence=0.95)
            
            if F is not None:
                #logging.debug("{0} correctMatches: {1}".format(self.loggingName, (F, mask)))
                mask = mask.ravel()
                p1 = np.expand_dims(p1[mask==1], axis=0)
                p2 = np.expand_dims(p2[mask==1], axis=0)
                p1_n, p2_n = cv.correctMatches(F, p1, p2)
                end = time.time()
                self.correctMatchesTime = end-start

                return F, np.reshape(p1_n, (-1,2)), np.reshape(p2_n, (-1,2))
        return None, p1, p2

    def ransacPlane(self, points, nIterations = None, threshold = None):
        #https://github.com/atharva333/ransac-surface-detection/blob/master/ransac.py
        #Modificato per distanza normalizzata
        """ RANSAC function takes points and uses them for planar fitting
            Returns equation of plane and points that are on plane for visualisation """

        if nIterations == None:
            nIterations = self.nIterations
        
        if threshold == None:
            threshold = self.threshold

        start = time.time()

        trials = nIterations # number of ransac trials
        maxMatches = 0 # intialise max matches to 0
        pointsOnPlane = []
        bestIndices = [] # initialise best indices list
        PP1, PP2, PP3 = 0 ,0, 0 # PP are plane points i.e the points we want
        points = np.array(points) # convert points to numpy array for easier slicing
        points = points[:,:3]
        coef = float('nan')

        # Run for number of trials
        for i in range(trials):
            # Checking for co linearity and the same point

            cross_product_check = np.array([0,0,0])
            while cross_product_check[0] == 0 and cross_product_check[1] == 0 and cross_product_check[2] == 0:
                # Creates list of 3 random integers in the given range
                randomList = random.sample(range(len(points)), 3)
                P1 = points[randomList[0]][:3]
                P2 = points[randomList[1]][:3]
                P3 = points[randomList[2]][:3]
                # make sure they are non-colinear
                cross_product_check = np.cross([i - j for i, j in zip(P1, P2)], [i - j for i, j in zip(P2, P3)])

            # how to - calculate plane coefficients from these points
            coefficients_abc = np.dot(np.linalg.inv(np.array([P1,P2,P3])), np.ones([3,1]))
            coefficient_d = math.sqrt(coefficients_abc[0]*coefficients_abc[0]+coefficients_abc[1]*coefficients_abc[1]+coefficients_abc[2]*coefficients_abc[2])

            # how to - measure distance of all points from plane given the plane coefficients calculated
            if ((abs(coefficients_abc[1]) > 4*abs(coefficients_abc[0])) and (abs(coefficients_abc[1]) > 2*abs(coefficients_abc[2]))):

                dist = abs((np.dot(points, coefficients_abc) - 1)/coefficient_d)

                # Calculate number of points that are under a certain threshold distance away from the plane
                # Later we'll calculate how many points match for each random plane formed

                # Condition produces array where distance is less than given threshold
                indices = (dist < threshold)
                
                if (indices.sum() > maxMatches):
                    coef = coefficients_abc / coefficient_d
                    bestIndices = indices
                    maxMatches = indices.sum()
                    PP1, PP2, PP3 = P1, P2, P3

        for idx, boolean in enumerate(bestIndices):
            if boolean == True:
                #print(points[idx])
                pointsOnPlane.append(points[idx])

        end = time.time()
        self.ransacTime = end-start

        return [PP1, PP2, PP3], np.array(pointsOnPlane), coef