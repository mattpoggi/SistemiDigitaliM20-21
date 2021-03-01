"""
Funzioni utilizzate OPENCV: Ho bisogno dei parametri intrinseci ed estrinseci della camera.
- Shi-Tomasi: per trovare le features
- Lucas-Kanade: per fare il match delle features
- undistortPoints(): per eliminare i difetti della lente
- triangulatePoints(): per triangolare i punti in 3D rispetto ad un'origine comune.
"""

import logging
import numpy as np
import math
import random
import time
import os
import ctypes

from defaults import Defaults
from utils_frame import FrameBuffer
from utils_frame import NPSlidingWindow
from monocularWrapper import MonocularWrapper
from feature_tracker import FeatureTracker
from camera import PinholeCamera
import utils_geom as gutils
import utils_view as vutils

class Cal_t(ctypes.Structure):
    _fields_ = [('scaleFactor', ctypes.c_float), ('shiftFactor', ctypes.c_float), ('valid', ctypes.c_int)]


class Calibrator:

    OriginRtMtx = np.array([[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]])
    LeftToRightMtx = np.array([[0,1,0,0], [0,0,-1,0], [1,0,0,0], [0,0,0,1]])

    METHOD_RANSAC = 0
    METHOD_LSM = 1
    METHOD_LSM_GT = 2

    CONFIG_KEYS = []
    CONFIG_OPTIONAL_KEYS = ['percentualeIncremento', 'windowSize', 'cutHalf', 'method', 'nIterations', 'normalizedThreshold', 'depthErrorThreshold', 'viewCalibrationImg']
    CONFIG_FINAL_KEYS = ['windowSize']
    CONFIG_SUBTYPES_KEYS = []

    @classmethod
    def loadLibrary(cls):
        #Compilazione e caricamento della libreria C
        if os.path.isfile("calibration.c"):
            os.system("gcc -fPIC -shared -O3 -o calibration.so calibration.c")
            cls.calibration = ctypes.cdll.LoadLibrary("./calibration.so")
            cls.calibration.initSeed()

    @classmethod
    def fromConfig(cls, camera, monocular, config):
        for key in cls.CONFIG_KEYS:
            if key not in config:
                return None

        percentualeIncremento = config['percentualeIncremento'] if 'percentualeIncremento' in config else None
        windowSize = config['windowSize'] if 'windowSize' in config else None
        cutHalf = config['cutHalf'] if 'cutHalf' in config else None
        method = config['method'] if 'method' in config else None
        nIterations = config['nIterations'] if 'nIterations' in config else None
        normalizedThreshold = config['normalizedThreshold'] if 'normalizedThreshold' in config else None
        viewCalibrationImg = config['viewCalibrationImg'] if 'viewCalibrationImg' in config else None

        return cls(camera, monocular, percentualeIncremento, windowSize, cutHalf, method, nIterations, normalizedThreshold, viewCalibrationImg)

    def __init__(self, camera, monocular, percentualeIncremento = None, windowSize = None,
     cutHalf = None, method = None, nIterations = None, normalizedThreshold = None, depthErrorThreshold = None,
     viewCalibrationImg = None):
        self.loggingName = "Calibrator"

        if not isinstance(camera, PinholeCamera):
            raise RuntimeError("{0} camera non è PinholeCamera".format(self.loggingName))
    
        if not isinstance(monocular, MonocularWrapper):
            raise RuntimeError("{0} monocular non è MonocularWrapper".format(self.loggingName))

        if percentualeIncremento is None:
            percentualeIncremento = Defaults.percentualeIncremento

        if windowSize is None:
            windowSize = Defaults.scaleFactorWindowSize

        if cutHalf is None:
            cutHalf = Defaults.cutHalf

        if method is None:
            method = self.METHOD_RANSAC
        
        if nIterations is None:
            nIterations = Defaults.scaleNIterations

        if normalizedThreshold is None:
            normalizedThreshold = Defaults.scaleNormalizedThreshold

        if depthErrorThreshold is None:
            depthErrorThreshold = Defaults.depthErrorThreshold
        
        if viewCalibrationImg is None:
            viewCalibrationImg = Defaults.viewCalibrationImg

        self.camera = camera
        self.monocular = monocular
        self.featureTracker = FeatureTracker()

        self.depthErrorCalculationTime = float('nan')
        self.calibrationTime = float('nan')
        self.algorithmTime = float('nan')

        self.skip = False

        self.config = {'percentualeIncremento': percentualeIncremento, 'windowSize': windowSize,
         'cutHalf': cutHalf, 'method': method, 'nIterations': nIterations, 'normalizedThreshold': normalizedThreshold,
         'depthErrorThreshold':depthErrorThreshold, 'viewCalibrationImg': viewCalibrationImg}

        self.slidingWindow = NPSlidingWindow(windowSize, 2)

        self.calculateScaleRange()
    
    def config(self, config):
        for key in config:
            if key in self.CONFIG_FINAL_KEYS:
                continue

            if key in self.CONFIG_KEYS:
                self.config[key] = config[key]

            if key in self.CONFIG_OPTIONAL_KEYS:
                self.config[key] = config[key]

    @property
    def percentualeIncremento(self):
        return self.config['percentualeIncremento'] if 'percentualeIncremento' in self.config else None

    @property
    def windowSize(self):
        return self.config['windowSize'] if 'windowSize' in self.config else None

    @property
    def cutHalf(self):
        return self.config['cutHalf'] if 'cutHalf' in self.config else None

    @property
    def method(self):
        return self.config['method'] if 'method' in self.config else None

    @property
    def nIterations(self):
        return self.config['nIterations'] if 'nIterations' in self.config else None

    @property
    def normalizedThreshold(self):
        return self.config['normalizedThreshold'] if 'normalizedThreshold' in self.config else None

    @property
    def depthErrorThreshold(self):
        return self.config['depthErrorThreshold'] if 'depthErrorThreshold' in self.config else None

    @property
    def viewCalibrationImg(self):
        return self.config['viewCalibrationImg'] if 'viewCalibrationImg' in self.config else None

    @property
    def scaleFactor(self):
        if self.slidingWindow.currentSize > 0:
            return self.slidingWindow.average[0]
        return Defaults.scaleFactor

    @property
    def shiftFactor(self):
        if self.slidingWindow.currentSize > 0:
            return self.slidingWindow.average[1]
        return Defaults.shiftFactor

    def updateFactors(self, scaleFactor, shiftFactor):
        self.slidingWindow.slide([scaleFactor, shiftFactor])
    
    @property
    def status(self):
        return {**self.config, 'depthErrorCalculationTime': self.depthErrorCalculationTime, 'calibrationTime': self.calibrationTime, 'scaleFactor': self.scaleFactor, 'shiftFactor': self.shiftFactor}

    def calculateScaleRange(self):
        if self.monocular.isDisparityOutput:
            myMin = 1/self.monocular.depthCap
            myMax = 1/self.monocular.depthMin
        else:
            myMin = self.monocular.depthMin
            myMax = self.monocular.depthCap
        
        self.minScaleFactor = 0.0
        self.maxScaleFactor = (100/Defaults.percentualeIncremento) * (myMax-myMin) / (self.monocular.maxOutputValue - self.monocular.minOutputValue)
        self.minShiftFactor = myMin - (self.monocular.minOutputValue * self.maxScaleFactor)
        self.maxShiftFactor = myMax

        if Calibrator.calibration is not None:
            percentualeIncremento_p = ctypes.c_float(Defaults.percentualeIncremento)
            minScaleFactor_p = ctypes.c_float(self.minScaleFactor)
            maxScaleFactor_p = ctypes.c_float(self.maxScaleFactor)
            minShiftFactor_p = ctypes.c_float(self.minShiftFactor)
            maxShiftFactor_p = ctypes.c_float(self.maxShiftFactor)
            Calibrator.calibration.calculateScaleRange(percentualeIncremento_p, minScaleFactor_p, maxScaleFactor_p, minShiftFactor_p, maxShiftFactor_p)

    def scaleFactorInRange(self, scaleFactor):
        return self.minScaleFactor <= scaleFactor and scaleFactor <= self.maxScaleFactor

    def shiftFactorInRange(self, shiftFactor):
        return self.minShiftFactor <= shiftFactor and shiftFactor <= self.maxShiftFactor
        #return True

    def calculateZTriangulationError(self, points3d, gt):
        height, width = gt.shape[:2]

        projPoints = self.camera.project(points3d)#Nx3
        
        mask = np.where((projPoints[:, 0] > 0.0) & (projPoints[:, 0] < width) &
                         (projPoints[:, 1] > 0.0) & (projPoints[:, 1] < height)
                         & (projPoints[:, 2] >= self.monocular.depthMin) & (projPoints[:, 2] <= self.monocular.depthCap))
        
        projPoints = projPoints[mask].T

        pts = np.zeros(gt.shape[:2])
        pts[projPoints[1].astype(np.int), projPoints[0].astype(np.int)] = projPoints[2]
        pts = np.reshape(pts, gt.shape)

        depth_mask = np.where(pts == 0.0, 0, 1)

        mse = np.sum(depth_mask * ((gt - pts) ** 2))
        n = np.sum(depth_mask)

        if n > 0:
            return  math.sqrt(mse / n)
        
    def calculateDepthError(self, calibratedPrediction, gt, threshold = None):
        if threshold is None:
            threshold = self.depthErrorThreshold

        start = time.time()

        good_mask = np.where((gt >= self.monocular.depthMin) & (gt <= self.monocular.depthCap))

        diffImage = np.abs(calibratedPrediction[good_mask] - gt[good_mask])

        outliers = np.where(diffImage > threshold, 1, 0)
        outliers = np.sum(outliers)

        totalPixels = good_mask[0].shape[0]

        end = time.time()
        self.depthErrorCalculationTime = end-start
        
        return (outliers / totalPixels) * 100

    def leastSquareMethod(self, prediction, points3d):
        scaleFactor = 0.0
        shiftFactor = 0.0
        valid = False

        height, width = prediction.shape[:2]
       
        projPoints = self.camera.project(points3d)#Nx3
        
        mask = np.where((projPoints[:, 0] > 0.0) & (projPoints[:, 0] < width) &
                         (projPoints[:, 1] > 0.0) & (projPoints[:, 1] < height)
                         & (projPoints[:, 2] >= self.monocular.depthMin) & (projPoints[:, 2] <= self.monocular.depthCap))
        
        projPoints = projPoints[mask]

        if self.monocular.isDisparityOutput:
            projPoints[:, 2] = 1.0 / projPoints[:, 2]

        projPoints = projPoints.T

        pts = np.zeros(prediction.shape[:2])
        pts[projPoints[1].astype(np.int), projPoints[0].astype(np.int)] = projPoints[2]
        pts = np.reshape(pts, prediction.shape)

        depth_mask = np.where(pts == 0.0, 0, 1)

        a00 = np.sum(depth_mask*prediction*prediction)
        a01 = np.sum(depth_mask*prediction)
        a11 = np.sum(depth_mask)
        
        b0 = np.sum(prediction * pts)
        b1 = np.sum(pts)

        detA = a00 * a11 - a01 * a01

        logging.debug("{0} (a00, a01, a11): {1}, (b0, b1): {2}".format(self.loggingName, (a00, a01, a11), (b0, b1)))

        valid = detA > 0.0

        if valid:
            scaleFactor = (a11*b0 - a01*b1) / detA
            shiftFactor = (-a01*b0 + a00*b1) / detA
            #Ulteriore check intrinseco: lo scale factor deve rimanere in un certo range
            valid = self.scaleFactorInRange(scaleFactor) and self.shiftFactorInRange(shiftFactor)

            if self.viewCalibrationImg:
                mask = np.where(pts != 0.0)
                zP = prediction[mask]
                zGt = pts[mask]
                xy = np.vstack((zP, zGt)).T.tolist()

                vutils.show_calibration(xy, self.monocular.minOutputValue, self.monocular.maxOutputValue, scaleFactor, shiftFactor)

        return valid, scaleFactor, shiftFactor

    def leastSquareMethodGT(self, prediction, gt):
        scaleFactor = 0.0
        shiftFactor = 0.0
        valid = False

        depth_mask = np.where((gt >= self.monocular.depthMin) & (gt <= self.monocular.depthCap), 1, 0)
        mask = np.where((gt >= self.monocular.depthMin) & (gt <= self.monocular.depthCap))

        if self.monocular.isDisparityOutput:
            gt = 1.0 / gt

        a00 = np.sum(depth_mask*prediction*prediction)
        a01 = np.sum(depth_mask*prediction)
        a11 = np.sum(depth_mask)
        
        b0 = np.sum(depth_mask * prediction * gt)
        b1 = np.sum(depth_mask * gt)

        detA = a00 * a11 - a01 * a01

        valid = detA > 0

        if valid:
            scaleFactor = (a11*b0 - a01*b1) / detA
            shiftFactor = (-a01*b0 + a00*b1) / detA

            if self.viewCalibrationImg:
                points = np.random.randint(gt[mask].shape[0], size=30)

                zP = prediction[mask][points]
                zGt = gt[mask][points]
                xy = np.vstack((zP, zGt)).T.tolist()

                vutils.show_calibration(xy, self.monocular.minOutputValue, self.monocular.maxOutputValue, scaleFactor, shiftFactor)

        return valid, scaleFactor, shiftFactor

    def ransacMethod(self, prediction, points3d, nIterations = None, normalizedThreshold = None):
        if nIterations == None:
            nIterations = self.nIterations
        
        if normalizedThreshold == None:
            normalizedThreshold = self.normalizedThreshold

        scaleFactor = 0.0
        shiftFactor = 0.0
        valid = False

        height, width = prediction.shape[:2]
       
        projPoints = self.camera.project(points3d)#Nx3
        
        mask = np.where((projPoints[:, 0] > 0.0) & (projPoints[:, 0] < width) &
                         (projPoints[:, 1] > 0.0) & (projPoints[:, 1] < height)
                         & (projPoints[:, 2] >= self.monocular.depthMin) & (projPoints[:, 2] <= self.monocular.depthCap))
        projPoints = projPoints[mask]

        if projPoints.shape[0] < 2:
            return valid, scaleFactor, shiftFactor

        if self.monocular.isDisparityOutput:
            projPoints[:, 2] = 1.0 / projPoints[:, 2]

        migliorScaleFactor = float('nan')
        migliorShiftFactor = float('nan')
        migliorConsensusSet = []

        i = 0
        while i < nIterations:
            possibileScaleFactor = 0.0
            possibileShiftFactor = 0.0
            possibileValid = False

            #Controllo intrinseco: Ho dei range in cui lo scale factor e lo shift factor si devono collocare
            #Esco comunque dopo un periodo
            k = 0
            while not possibileValid and k < nIterations:
                #Punti scelti a caso dal dataset: effettuo il sort per velocizzare la ricerca del minmax e calcolo errore
                possibiliInliner = random.sample(range(projPoints.shape[0]), 2)

                zGt0 = projPoints[possibiliInliner[0]][2]
                z0 = prediction[int(projPoints[possibiliInliner[0]][1]), int(projPoints[possibiliInliner[0]][0])]

                zGt1 = projPoints[possibiliInliner[1]][2]
                z1 = prediction[int(projPoints[possibiliInliner[1]][1]), int(projPoints[possibiliInliner[1]][0])]

                if abs(z0 - z1) > (self.percentualeIncremento / 100):
                    #Sono dei candidati a diventare migliori. Devo verificare rispetto al migliore attuale
                    possibileScaleFactor = (zGt0 - zGt1) / (z0 - z1)
                    possibileShiftFactor = zGt0 - (z0 * possibileScaleFactor)
                    possibileValid = self.scaleFactorInRange(possibileScaleFactor) and self.shiftFactorInRange(possibileShiftFactor)
                k+=1

            #Controllo il check intrinseco: se non ho trovato uno scale factor nel range esco
            if not possibileValid:
                logging.debug("{0} NOT VALID PSC: {1}, PSH: {2}".format(self.loggingName, possibileScaleFactor, possibileShiftFactor))
                return valid, scaleFactor, shiftFactor

            logging.debug("{0} VALID PSC: {1}, PSH: {2}".format(self.loggingName, possibileScaleFactor, possibileShiftFactor))

            #Candidato a diventare miglior consensus set
            consensusSet = []

            #Calcolo il range dell'errore, per normalizzare
            minError = float('inf')
            maxError = -float('inf')

            for k in range(projPoints.shape[0]):
                zGtP = projPoints[k][2]
                zP = prediction[int(projPoints[k][1]), int(projPoints[k][0])]

                thisError = ((zP * possibileScaleFactor + possibileShiftFactor) - zGtP) ** 2
                minError = thisError if thisError < minError else minError
                maxError = thisError if thisError > maxError else maxError

            for k in range(projPoints.shape[0]):
                zGtP = projPoints[k][2]
                zP = prediction[int(projPoints[k][1]), int(projPoints[k][0])]
                
                thisError = ((zP * possibileScaleFactor + possibileShiftFactor) - zGtP) ** 2
                normalizedError = (thisError - minError) / (maxError - minError)

                if normalizedError < normalizedThreshold:
                    consensusSet.append(k)                    

            if len(consensusSet) > len(migliorConsensusSet):
                migliorScaleFactor = possibileScaleFactor
                migliorShiftFactor = possibileShiftFactor
                migliorConsensusSet = consensusSet

            i +=1

        if not math.isnan(migliorScaleFactor) and not math.isnan(migliorShiftFactor):
            valid = True
            scaleFactor = migliorScaleFactor
            shiftFactor = migliorShiftFactor

            if self.viewCalibrationImg:
                xy = []
                
                for k in range(projPoints.shape[0]):
                    zGtP = projPoints[k][2]
                    zP = prediction[int(projPoints[k][1]), int(projPoints[k][0])]
                    xy.append((zP, zGtP))
                
                vutils.show_calibration(xy, self.monocular.minOutputValue, self.monocular.maxOutputValue, scaleFactor, shiftFactor)
        
        return valid, scaleFactor, shiftFactor

    def ransacMethodC(self, prediction, points3d, nIterations = None, normalizedThreshold = None):
        if nIterations == None:
            nIterations = self.nIterations
        
        if normalizedThreshold == None:
            normalizedThreshold = self.normalizedThreshold

        scaleFactor = 0.0
        shiftFactor = 0.0
        valid = False

        if Calibrator.calibration is None:
            logging.debug("{0} libreria C non caricata correttamente".format(self.loggingName))
            return valid, scaleFactor, shiftFactor

        calibration = Calibrator.calibration

        height, width = prediction.shape[:2]
       
        projPoints = self.camera.project(points3d)#Nx3
        
        mask = np.where((projPoints[:, 0] > 0.0) & (projPoints[:, 0] < width) &
                         (projPoints[:, 1] > 0.0) & (projPoints[:, 1] < height)
                         & (projPoints[:, 2] >= self.monocular.depthMin) & (projPoints[:, 2] <= self.monocular.depthCap))
        projPoints = projPoints[mask]

        if projPoints.shape[0] < 2:
            return valid, scaleFactor, shiftFactor

        if self.monocular.isDisparityOutput:
            projPoints[:, 2] = 1.0 / projPoints[:, 2]

        result = Cal_t()
        
        prediction_p = ctypes.c_void_p(prediction.ctypes.data)
        projPoints_p = ctypes.c_void_p(projPoints.ctypes.data)
        h_p = ctypes.c_int(height)
        w_p = ctypes.c_int(width)
        N_p = ctypes.c_int(projPoints.shape[0])
        nIterations_p = ctypes.c_int(nIterations)
        normalizedThreshold_p = ctypes.c_float(normalizedThreshold)
        result_p = ctypes.pointer(result)

        #logging.debug("Python TEST: pred[0]:{0}, projPoint[0]: {1}".format(prediction[0,0], projPoints[0]))

        calibration.ransacMethod(prediction_p, projPoints_p, h_p, w_p, N_p, nIterations_p, normalizedThreshold_p, result_p)

        if result.valid == 1:
            scaleFactor = result.scaleFactor
            shiftFactor = result.shiftFactor
            valid = True

            logging.debug("{0} C RANSAC riuscito: {1}".format(self.loggingName, (result.scaleFactor, result.shiftFactor, result.valid)))

            if self.viewCalibrationImg:
                xy = []
                
                for k in range(projPoints.shape[0]):
                    zGtP = projPoints[k][2]
                    zP = prediction[int(projPoints[k][1]), int(projPoints[k][0])]
                    xy.append((zP, zGtP))
                
                vutils.show_calibration(xy, self.monocular.minOutputValue, self.monocular.maxOutputValue, scaleFactor, shiftFactor) 
        else:
            logging.debug("{0} C RANSAC non riuscito: {1}".format(self.loggingName, (result.scaleFactor, result.shiftFactor, result.valid)))

        return valid, scaleFactor, shiftFactor

    @staticmethod
    def _frameFilterPrediction(frameBuffer):
        filteredFrameBuffer = []
        i = 0
        while i < len(frameBuffer):
            if FrameBuffer.PREDICTION in frameBuffer[i] and FrameBuffer.CALIBRATED_PREDICTION not in frameBuffer[i]:
                filteredFrameBuffer.append(frameBuffer[i-1])
                filteredFrameBuffer.append(frameBuffer[i])
                break
            i +=1
        return filteredFrameBuffer

    def calibrate(self, frameBuffer):
        """
        Restituisce un immagine di depth a partire dallo stato dell'oggetto.
        Prima necessitiamo di caricare almeno due immagini assieme alle informazioni della posa.
        Calibrazione mediante algoritmo deciso nei parametri
        """
        start = time.time()

        #Ricavo i punti tridimensionali per la calibrazione

        #frameBuffer = frameBuffer.frameBufferFilteredCopy(Calibrator._frameFilterPrediction)
        frame0 = frameBuffer.frame0
        frame1 = frameBuffer.frame1

        imgCamera0 = frame0[FrameBuffer.GRAY_IMAGE]
        imgCamera1 = frame1[FrameBuffer.GRAY_IMAGE]
        gtDepthImage = frame1[FrameBuffer.GROUND_TRUTH]
        prediction1 = frame1[FrameBuffer.PREDICTION]

        valid = False

        if self.skip:
            #Pulisco lo sliding window si riparte da zero.
            self.slidingWindow.clear()
        else:
            #Se calibro con la GT non devo trovare dei punti.
            if self.method == self.METHOD_LSM_GT:
                start_algo = time.time()
                valid, scaleFactor, shiftFactor = self.leastSquareMethodGT(prediction1, gtDepthImage)
                end_algo = time.time()
                self.algorithmTime = end_algo - start_algo

                if valid:
                    self.updateFactors(scaleFactor, shiftFactor)
            else:
                RtMtx0 = frame0[FrameBuffer.RT_MATRIX] @ frame1[FrameBuffer.RT_MATRIX_INVERSE] 
                RtMtx1 = self.OriginRtMtx
                                
                projMtx0 = self.camera.getProjMtx(RtMtx0)
                projMtx1 = self.camera.getProjMtx(RtMtx1)

                #Voglio solo la metà inferiore dei punti
                if self.cutHalf:
                    roi = (0, int((imgCamera0.shape[0] / 1.9)), imgCamera0.shape[1], 100)
                else:
                    roi = None

                #Ricerca delle features
                if FrameBuffer.KEYPOINTS not in frame0:
                    kp0, des0 = self.featureTracker.detectShiTomasi(imgCamera0, roi)
                    frame0[FrameBuffer.KEYPOINTS] = kp0
                    frame0[FrameBuffer.DESCRIPTORS] = des0
                else:
                    kp0 = frame0[FrameBuffer.KEYPOINTS]
                    des0 = frame0[FrameBuffer.DESCRIPTORS]

                if FrameBuffer.KEYPOINTS not in frame1:
                    kp1, des1 = self.featureTracker.detectShiTomasi(imgCamera1, roi)
                    frame1[FrameBuffer.KEYPOINTS] = kp0
                    frame1[FrameBuffer.DESCRIPTORS] = des0
                else:
                    kp1 = frame1[FrameBuffer.KEYPOINTS]
                    des1 = frame1[FrameBuffer.DESCRIPTORS]

                #Match delle features nel frame successivo
                points2d0, points2d1 = self.featureTracker.computeFlow(imgCamera0, imgCamera1, kp0, roi)
                #points2d0, points2d1 = self.featureTracker.match(kp0, kp1, des0, des1)

                #Test
                _, points2d0, points2d1 = self.featureTracker.correctMatches(points2d0, points2d1)
                points3d = np.array([])

                frame0[FrameBuffer.POINTS_2D] = points2d0
                frame0[FrameBuffer.POINTS_2D_NEXT_FRAME] = points2d1
                frame1[FrameBuffer.POINTS_2D] = points2d1
                    
                #Se trovo punti:
                if points2d0.shape[0] > 0 and points2d1.shape[0] > 0:
                    points3d = self.featureTracker.triangulatePoints(points2d0, points2d1, projMtx0, projMtx1)    #Nx4
                    #Devo avere almeno tre punti per la ricerca del piano.
                    if points3d.shape[0] >= 3:
                        #Filtro i punti con ransac
                        #_, points3d,_ = self.featureTracker.ransacPlane(points3d)#Nx3
                        points3d = points3d[:, :3] #Nx3
                        #Devo avere almeno due punti per i metodi.
                        if points3d.shape[0] >= 2:
                            frame1[FrameBuffer.POINTS_3D] = points3d

                if FrameBuffer.POINTS_3D in frame1:  
                    points3d = frame1[FrameBuffer.POINTS_3D]
                    start_algo = time.time()
                    if self.method == self.METHOD_RANSAC:
                        #if Calibrator.calibration is not None:
                        #    valid, scaleFactor, shiftFactor = self.ransacMethodC(prediction1, points3d)
                        #else:
                        valid, scaleFactor, shiftFactor = self.ransacMethod(prediction1, points3d)
                    elif self.method == self.METHOD_LSM:
                        valid, scaleFactor, shiftFactor = self.leastSquareMethod(prediction1, points3d)

                    end_algo = time.time()
                    self.algorithmTime = end_algo - start_algo

                    if valid:
                        self.updateFactors(scaleFactor, shiftFactor)

        #Applico la calibrazione all'immagine
        #TODO: Scale factor applicato solo al ROI
        prediction1 = prediction1 * self.scaleFactor + self.shiftFactor

        prediction1 = np.clip(prediction1, 1/self.monocular.depthCap, None)

        if self.monocular.isDisparityOutput:
            prediction1 = 1.0 / prediction1

        frame1[FrameBuffer.CALIBRATED_PREDICTION] = prediction1
        frame1[FrameBuffer.SCALE_FACTOR] = self.scaleFactor
        frame1[FrameBuffer.SHIFT_FACTOR] = self.shiftFactor

        end = time.time()
        self.calibrationTime = end-start

        k = len(frame1[FrameBuffer.POINTS_2D]) if FrameBuffer.POINTS_2D in frame1 else float('nan')

        logging.debug("{0} Calibration Time ({1} pts): Tot {2} = Detect: {3} + Compute/Flow: {4}/{5} + Triangulate: {6} + RANSAC/CorrectMatches: {7}/{8} + Calibration: {9}".format(
         self.loggingName, k,
         self.calibrationTime, self.featureTracker.detectTime, self.featureTracker.computeTime,
         self.featureTracker.flowTime, self.featureTracker.triangulateTime, self.featureTracker.ransacTime,
         self.featureTracker.correctMatchesTime, self.algorithmTime))

        return valid

#Init libreria C
Calibrator.loadLibrary()