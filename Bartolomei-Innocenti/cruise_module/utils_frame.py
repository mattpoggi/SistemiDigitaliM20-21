import numpy as np
import logging

class FrameBuffer:
    RGB_IMAGE = "rgbImage"
    BGR_IMAGE = "bgrImage"
    GRAY_IMAGE = "grayImage"
    PREDICTION = "prediction"
    GROUND_TRUTH = "gt"
    RT_MATRIX = "RtMtx"
    RT_MATRIX_INVERSE = "RtMtxInverse"
    POINTS_2D = "points2d"
    POINTS_2D_NEXT_FRAME = "points2dNextFrame"
    POINTS_3D = "points3d"
    TRIANGULATION_ERROR_XY = "trErrorXY"
    TRIANGULATION_ERROR_Z = "trErrorZ"
    CALIBRATED_PREDICTION = "calibratedPrediction"
    CALIBRATED_PREDICTION_ERROR = "depthError"
    CALIBRATED_PREDICTION_THRESHOLD_ERROR = "depthErrorThreshold"
    KEYPOINTS = "kp"
    DESCRIPTORS = "des"
    SCALE_FACTOR = "scaleFactor"
    SHIFT_FACTOR = "shiftFactor"
    TIMESTAMP = "timestamp"
    ROI = "roi"
    LOCATION = "location"
    ROTATION = "rotation"

    def __init__(self, initialState = None, size = 2):
        self.loggingName = "FrameBuffer"

        if isinstance(initialState, list):
            self._shiftArray = initialState
            self._size = max(len(initialState), size)
        else:
            self._shiftArray = []
            self._size = size
    
    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        if value <= 1:
            raise RuntimeError("{0} size non valida".format(self.loggingName))

        self._size = value

    @property
    def __getitem__(self, key):
        return self._shiftArray[key]

    @property
    def frame0(self):
        if len(self._shiftArray) > 0:
            return self._shiftArray[0]
        else:
            return {}

    @property
    def frame1(self):
        if len(self._shiftArray) > 1:
            return self._shiftArray[1]
        else:
            return {}

    @property
    def enoughFrames(self):
        return len(self._shiftArray) >= self.size
    
    def shiftFrame(self, frame):
        self._shiftArray.append(frame)
        if len(self._shiftArray) > self.size:
            return self._shiftArray.pop(0)
        return None

    def clearBuffer(self):
        self._shiftArray = []

    def frameBufferFiltered(self, filter):
        self._shiftArray = filter(self._shiftArray)
    
    def frameBufferFilteredCopy(self, filter):
        return FrameBuffer(filter(self._shiftArray))

class NPSlidingWindow:
    def __init__(self, size, rows):
        self.loggingName = "Sliding Window"

        if size <= 1:
            raise RuntimeError("{0} size non valida".format(self.loggingName))

        if rows <= 0:
            raise RuntimeError("{0} rows non valida".format(self.loggingName))

        self._size = size
        self._rows = rows
        self.clear()

    def __getitem__(self, key):
        return self._buffer[key]

    @property
    def size(self):
        return self._size

    @property
    def rows(self):
        return self._rows
    
    @property
    def currentSize(self):
        return self._currentSize

    def _invalidate(self):
        self._invalidateAverage = True

    def slide(self, frame):
        frame = np.array(frame)

        #logging.debug("{0} frame shape: {1}, buffer shape: {2}".format(self.loggingName, frame.shape, self._buffer.shape))

        if frame.shape == self._buffer.shape[1:] or frame.shape == (self._buffer.shape[1], 1):
            frame = np.reshape(frame, self._buffer.shape[1:])
            self._buffer[self._index] = frame
            self._index = (self._index+1) % self._size
            self._invalidate()
        
            if self._currentSize < self._size:
                self._currentSize += 1

    @property
    def average(self):
        if self._invalidateAverage or self._average is None:
            self._average = np.average(self._buffer[:self._currentSize].T, axis=1)
            self._invalidateAverage = False
        return self._average
    
    def clear(self):
        self._buffer = np.zeros((self._size, self._rows))
        self._index = 0
        self._currentSize = 0
        self._invalidateAverage = True
        self._average = None