"""
PIPELINE:

Ricavo due frame successivi dalla camera RGB di CARLA.
Rimuovo le distorsioni all'immagine.
Ricavo la [R | t] dai sensori di CARLA.
Calcolo le features nei frame e faccio un match
Uso la funzione triangulatePoints() per ricavare i punti nelle coordinate spaziali, con riferimento al primo frame.
Uso l'algoritmo di calibrazione per mettere in scala PyDNet, usato anche in ARPydnet.
Uso le informazioni di profondità per il controllore del cruise-control e aggiorno il simulatore di conseguenza. (In CruiseControl)
Effettuo uno shift dei frame e ripeto dal primo punto.
"""
"""
Calibratore per ricavare la distanza: tempo impiegato per il calcolo.
Controllo sul veicolo.
Funzione che dice la velocità di uscita

coefficiente di attrito supponiamo fisso
Decellerazione della frenatura [0, max]
limite del sensore monoculare (20m)
velocità attuale.
"""

import logging
import numpy as np
import cv2 as cv
import tensorflow as tf
import math
import time
import threading

from defaults import Defaults
from utils_frame import FrameBuffer, NPSlidingWindow
from calibrator import Calibrator
from monocularWrapper import MonocularWrapper
from camera import PinholeCamera
import utils_geom as gutils

class CruiseControl:
    """
    Classe che si occupa della gestione del CruiseControl.
    """

    """
    -roi: (x0 > 0, y0 > 0, w > 0, h > 0) 
    -velocitaAttuale: [0, inf[
    -velocitaCrociera: ]0, inf[
    -distanzaMinima: ]depthMin, distanzaLimite[
    -distanzaLimite: ]distanzaMinima, depthCap-depthMin[
    """

    CONFIG_KEYS = ['roi', 'velocitaCrociera']
    CONFIG_FINAL_KEYS = ['windowSize']
    CONFIG_OPTIONAL_KEYS = ['distanzaMinima', 'distanzaLimite', 'windowSize', 'skipThreshold']
    CONFIG_SUBTYPES_KEYS = ['monocular', 'calibrator', 'camera']

    SHIFT_KEY = 'shift'
    SHIFT_TYPES = ['carlaRt', 'gnssIMUEncoder']
    FRAME_KEYS = ['imageBGR', 'imageGT', 'transform', 'gnss', 'imu', 'encoder']

    ORIGIN_POINT = np.array([0.0, 0.0, 0.0, 1.0])
    X_VECTOR = np.array([1.0, 0.0, 0.0, 1.0])
    Y_VECTOR = np.array([0.0, 1.0, 0.0, 1.0])
    Z_VECTOR = np.array([0.0, 0.0, 1.0, 1.0])

    @classmethod
    def fromConfig(cls, config):
        if 'camera' not in config:
            return None
        
        camera = PinholeCamera.fromConfig(config['camera'])

        if camera:
            monocular = MonocularWrapper()

            if 'calibrator' in config:
                calibrator = Calibrator.fromConfig(camera, monocular, config['calibrator'])
            else:
                calibrator = Calibrator(camera, monocular)

            if calibrator:
                for key in cls.CONFIG_KEYS:
                    if key not in config:
                        return None

                roi = config['roi']
                velocitaCrociera = config['velocitaCrociera']
                #Parametri opzionali
                distanzaMinima = config['distanzaMinima'] if 'distanzaMinima' in config else None
                distanzaLimite = config['distanzaLimite'] if 'distanzaLimite' in config else None
                windowSize = config['windowSize'] if 'windowSize' in config else None
                skipThreshold = config['skipThreshold'] if 'skipThreshold' in config else None

                return cls(camera, monocular, calibrator, roi, velocitaCrociera, distanzaMinima, distanzaLimite, windowSize, skipThreshold)
                
    def __init__(self, camera, monocular, calibrator, roi, velocitaCrociera, distanzaMinima = None, distanzaLimite = None, windowSize = None, skipThreshold = None):
        self.loggingName = "Cruise Control"

        self.camera = camera
        self.monocular = monocular
        self.calibrator = calibrator
        self.frameBuffer = FrameBuffer(initialState=None, size=500)

        if not isinstance(camera, PinholeCamera):
            raise RuntimeError("{0} camera non è PinholeCamera".format(self.loggingName))
        
        if roi is None:
            raise RuntimeError("{0} roi assente".format(self.loggingName))
        
        if velocitaCrociera is None:
            raise RuntimeError("{0} velocitaCrociera assente".format(self.loggingName))

        if distanzaMinima is None:
            distanzaMinima = self.monocular.depthMin
        
        if distanzaLimite is None:
            distanzaLimite = self.monocular.depthCap-self.monocular.depthMin

        if windowSize is None:
            windowSize = Defaults.cruiseWindowSize
        
        if skipThreshold is None:
            skipThreshold = Defaults.skipThreshold

        self.config = {'roi': roi, 'velocitaCrociera': velocitaCrociera,
         'distanzaMinima': distanzaMinima, 'distanzaLimite': distanzaLimite,
          'windowSize': windowSize, 'skipThreshold': skipThreshold}

        self.parseTime = float('nan')

        self.slidingWindow = NPSlidingWindow(windowSize, 2)

        self.lastCalibration = None
        self.inferenceRunning = False

    @property
    def velocitaUscita(self):
        if self.slidingWindow.currentSize > 0:
            return self.slidingWindow.average[0]
        return self.velocitaCrociera
    
    @property
    def accelerazione(self):
        if self.slidingWindow.currentSize > 0:
            return self.slidingWindow.average[1]
        return 0.0

    def config(self, config):
        for key in config:
            if key in self.CONFIG_FINAL_KEYS:
                continue

            if key in self.CONFIG_KEYS:
                self.config[key] = config[key]

            if key in self.CONFIG_OPTIONAL_KEYS:
                self.config[key] = config[key]

        configSubObjs(config)

    def configSubObjs(self, myDict):
        if 'monocular' in myDict:
            monocularConfig = dict['monocular']
            self.monocular.config(monocularConfig) 
        
        if 'camera' in myDict:
            cameraConfig = myDict['camera']
            self.camera.config(cameraConfig)

        if 'calibrator' in myDict:
            calibratorConfig = myDict['calibrator']
            self.calibrator.config(calibratorConfig)

    @property
    def status(self):
        return {**self.config, 'parseTime': self.parseTime, 'monocular': self.monocular.status, 'camera': self.camera.status, 'calibrator': self.calibrator.status}

    @property
    def roi(self):
        return self.config['roi'] if 'roi' in self.config else None

    @property
    def velocitaCrociera(self):
        return self.config['velocitaCrociera'] if 'velocitaCrociera' in self.config else None

    @property
    def distanzaMinima(self):
        return self.config['distanzaMinima'] if 'distanzaMinima' in self.config else None

    @property
    def distanzaLimite(self):
        return self.config['distanzaLimite'] if 'distanzaLimite' in self.config else None

    @property
    def windowSize(self):
        return self.config['windowSize'] if 'windowSize' in self.config else None

    @property
    def skipThreshold(self):
        return self.config['skipThreshold'] if 'skipThreshold' in self.config else None

    @property
    def timing(self):
        return self.parseTime, self.monocular.inferenceTime, self.calibrator.calibrationTime

    @staticmethod
    def _frameFilterCalibratedPrediction(frameBuffer):
        filteredFrameBuffer = []
        for frame in frameBuffer:
            if FrameBuffer.CALIBRATED_PREDICTION in frame:
                filteredFrameBuffer.append(frame)
        return filteredFrameBuffer

    @staticmethod
    def _shiftUntilNextCalibratedPrediciton(frameBuffer):
        counter = 0
        i = len(frameBuffer)-1
        while i >= 0:
            if FrameBuffer.CALIBRATED_PREDICTION in frameBuffer[i]:
                break
            counter +=1
            i-=1

        return frameBuffer[len(frameBuffer)-counter:]

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

    def calibrate(self):
        frameBuffer = self.frameBuffer.frameBufferFilteredCopy(self._frameFilterPrediction)
        frameBuffer.size = 2

        if frameBuffer.enoughFrames:
            self.calibrator.skip = self.velocitaUscita < self.skipThreshold
            self.calibrator.calibrate(frameBuffer)
            frame = frameBuffer.frame1

            if FrameBuffer.GROUND_TRUTH in frame and FrameBuffer.CALIBRATED_PREDICTION in frame:
                depthError = self.calibrator.calculateDepthError(frame[FrameBuffer.CALIBRATED_PREDICTION], frame[FrameBuffer.GROUND_TRUTH])
                if depthError:
                    frame[FrameBuffer.CALIBRATED_PREDICTION_ERROR] = depthError
                    frame[FrameBuffer.CALIBRATED_PREDICTION_THRESHOLD_ERROR] = self.calibrator.depthErrorThreshold

            if FrameBuffer.GROUND_TRUTH in frame and FrameBuffer.POINTS_3D in frame:
                zError = self.calibrator.calculateZTriangulationError(frame[FrameBuffer.POINTS_3D], frame[FrameBuffer.GROUND_TRUTH])
                if zError:
                    frame[FrameBuffer.TRIANGULATION_ERROR_Z] = zError
            
            self.lastCalibration = frame.copy()
            
    def shiftFrom(self, data, timestamp):
        if self.SHIFT_KEY in data:
            shiftType = data[self.SHIFT_KEY]
            if shiftType in self.SHIFT_TYPES:
                if shiftType == 'carlaRt':
                    self.shiftFromCarlaUseTransform(data, timestamp)

                time.sleep(0.05)
                
                return self.lastCalibration

    def shiftFromCarlaUseTransform(self, data, timestamp):
        """
        Ricava le informazioni per la calibrazione dai sensori carla.
        Non utilizza i sensori IMU e GNSS per la stima della posa, ma utilizza direttamente le Transform di Carla.
        Non è necessario sincronizzare i timestamp dei vari sensori.
        """
        
        bgrImage = data["imageBGR"]
        gtImage = data["imageGT"] if 'imageGT' in data else None
        transform = data["transform"]
        location = transform['location']
        rotation = transform['rotation']

        #Trasformazione della matrice con un sistema di coordinate congruo a OpenCV.
        # (x, y ,z) -> (x, -y, z)
        
        location['y'] = -location['y']
        rotation['pitch'] = -rotation['pitch']

        #Genero la matrice Rt
        t = np.array([location['x'], location['y'], location['z']]) 
        t = np.expand_dims(t, axis=1) #(3,1)
        R = (gutils.yaw_matrix(math.radians(rotation['yaw'])) @ gutils.pitch_matrix(math.radians(rotation['pitch'])) @ gutils.roll_matrix(math.radians(rotation['roll'])))
        RtMtx = np.hstack((R,t))
        RtMtx = np.vstack((RtMtx, np.array([0,0,0,1])))
        RtMtxInverse = np.linalg.inv(RtMtx)
        RtMtx, RtMtxInverse = RtMtxInverse, RtMtx

        return self.shift(bgrImage, gtImage, location, rotation, RtMtx, RtMtxInverse, timestamp)

    def shift(self, bgrImage, gtImage, location, rotation, RtMtx, RtMtxInverse, timestamp):
        """
        Esegue uno shift a sinistra delle informazioni per la calibrazione, aggiungendone nuove (FIFO).
        """
        
        rgbImage, bgrImage, grayImage = self.parseCameraImage(bgrImage)

        frame = {FrameBuffer.RGB_IMAGE: rgbImage, FrameBuffer.BGR_IMAGE: bgrImage, FrameBuffer.GRAY_IMAGE: grayImage,
         FrameBuffer.GROUND_TRUTH: gtImage, FrameBuffer.RT_MATRIX: RtMtx,
         FrameBuffer.RT_MATRIX_INVERSE: RtMtxInverse, FrameBuffer.TIMESTAMP: timestamp,
         FrameBuffer.LOCATION: location, FrameBuffer.ROTATION: rotation}

        self._asyncInference(frame)
        
        return self.frameBuffer.shiftFrame(frame)

    def _asyncInference(self, frame):
        if not self.inferenceRunning:
            x = threading.Thread(target=self._inferenceRun, args=(frame, ), daemon=False)
            x.start()
            self.inferenceRunning = True
    
    def _inferenceRun(self, frame):
        predictionImage = self.monocular.inference(frame[FrameBuffer.RGB_IMAGE])
        frame[FrameBuffer.PREDICTION] = predictionImage

        try:
            self.calibrate()
        finally:
            self.inferenceRunning = False

    def parseCameraImage(self, bgrImage):
        """
        Esegue una rimozione della distorsione.
        Esegue una trasformazione in GRAY
        Esegue una trasformazione in Disparity
        """

        start = time.time()

        bgrImage = self.camera.undistortImage(bgrImage)
        rgbImage = cv.cvtColor(bgrImage, cv.COLOR_BGR2RGB)
        grayImage = cv.cvtColor(bgrImage, cv.COLOR_BGR2GRAY)

        end = time.time()
        self.parseTime = end-start

        return rgbImage, bgrImage, grayImage

    def previsioneCruise(self):
        """
        Velocità attuale
        Frame Buffer pieno
        Distanza minima
        Distanza limite
        Restituisce accelerazione

        Funzionamento:
        - Calcolo deltaT: Differenza di tempo tra i due frame
        - Effettuo il ROI e Average delle depth: trovo due scalari depth0 e depth1
        - Calcolo deltaS: depth1 - depth0, si tratta della differenza tra le distanze auto ostacolo nei due frame
        - Check distanzaLimite: se deltaS è in un certo range (filtro rumore) e l'ultima distanza (depth1) è maggiore della distanzaLimite
           allora posso aumentare la velocita gradualmente usando deltaS = depth1 - distanzaLimite
        - Calcolo la velocitaDifferenza: deltaS / deltaT e la sommo alla velocità attuale per trovare la velocitaUscita
        - VelocitaUscita [0, velocitaCrociera]
        - Calcolo deltaV: velocitaUscita - velocitaAttuale, se positiva devo accelerare
        - Se deltaV < 0 allora addolcisco la frenata calcolando il massimo spazio di frenata
        - Restituisco l'accelerazione: deltaV / deltaT e la velocitaUscita
        """
        
        frameBuffer = self.frameBuffer.frameBufferFilteredCopy(CruiseControl._frameFilterCalibratedPrediction)
        frameBuffer.size = 2

        if frameBuffer.enoughFrames:
            frame0 = frameBuffer.frame0
            frame1 = frameBuffer.frame1

            RtMtx = frame1[FrameBuffer.RT_MATRIX] @ frame0[FrameBuffer.RT_MATRIX_INVERSE] 
            spaceVector = RtMtx @ self.ORIGIN_POINT

            distanzaPercorsa = math.sqrt(spaceVector[0] ** 2 + spaceVector[1] ** 2 + spaceVector[2] ** 2)

            #Delta di tempo dato dai due frame
            deltaT = frame1[FrameBuffer.TIMESTAMP] - frame0[FrameBuffer.TIMESTAMP] 

            if deltaT == 0.0:
                return self.velocitaUscita, self.accelerazione

            velocitaAttuale = distanzaPercorsa / deltaT

            logging.debug("{0} distanzaPercorsa: {1}, deltaT: {2}, velocità attuale: {3}".format(self.loggingName, distanzaPercorsa, deltaT, velocitaAttuale))

            #Effettuo il ROI (Region Of Interest) dei frame
            x0,y0,w,h = self.roi

            #Applico la pendenza
            y0 = int(y0 + 20 * math.sin(math.radians(frame1[FrameBuffer.ROTATION]['pitch'])))

            frame1[FrameBuffer.ROI] = (x0, y0, w, h)

            #logging.debug("{0} ROI: {1}".format(self.loggingName, self.roi))

            depth0 = frame0[FrameBuffer.CALIBRATED_PREDICTION]
            depth0 = depth0[y0:y0+h, x0:x0+w]
            depth1 = frame1[FrameBuffer.CALIBRATED_PREDICTION]
            depth1 = depth1[y0:y0+h, x0:x0+w]

            #logging.debug("{0} depth0: Min: {1}, Avg: {2}, Max: {3}".format(self.loggingName, np.min(depth0), np.average(depth0), np.max(depth0)))
            #logging.debug("{0} depth1: Min: {1}, Avg: {2}, Max: {3}".format(self.loggingName, np.min(depth1), np.average(depth1), np.max(depth1)))

            depth0 = np.min(depth0)
            depth1 = np.min(depth1)

            #Filtro il rumore
            depth0 = min(max(depth0, self.monocular.depthMin), self.monocular.depthCap)
            depth1 = min(max(depth1, self.monocular.depthMin), self.monocular.depthCap)

            #Delta spostamento dato dalla differenza della media delle depth
            deltaS = depth1 - depth0

            #Se dopo il limite allora posso aumentare la velocità
            if depth1 > self.distanzaLimite and depth0 > self.distanzaLimite:
                deltaS = depth1-self.distanzaLimite

            #Se entro il minimo allora devo frenare assolutamente
            if depth1 < self.distanzaMinima:
                deltaS = -depth1
        
            velocitaDifferenza = deltaS / deltaT

            #Calcolo la velocita di uscita: [0, velocitaCrociera]
            velocitaUscita = velocitaAttuale
            velocitaUscita += velocitaDifferenza
            velocitaUscita = min(velocitaUscita, self.velocitaCrociera)
            velocitaUscita = max(0, velocitaUscita)

            #Delta della velocità in caso di velocità uscita maggiore attuale allora positiva
            deltaV = velocitaDifferenza

            #Addolcimento frenatura: solo se ho abbastanza spazio
            if deltaV < 0:
                #Calcolo lo spazio massimo di frenata: solo se lo spazio è maggiore della distanza minima
                maxSpazioFrenata = depth1 - self.distanzaMinima if depth1 > self.distanzaMinima else depth1
                #Calcolo il tempo necessario per raggiungere il deltaV nello spazio di frenatura
                deltaT = maxSpazioFrenata / -deltaV

            logging.debug("{0} deltaV: {1}, deltaT: {2}, deltaS: {3}, depth: {4}".format(self.loggingName, deltaV, deltaT, deltaS, depth1))

            accelerazione = deltaV / deltaT
            accelerazione = min(accelerazione, 0)

            self.slidingWindow.slide([velocitaUscita, accelerazione])
            self.frameBuffer.frameBufferFiltered(CruiseControl._shiftUntilNextCalibratedPrediciton)            

        return self.velocitaUscita, self.accelerazione