# ==============================================================================
# -- find carla module ---------------------------------------------------------
# ==============================================================================
import glob
import os
import sys

try:
    sys.path.append(glob.glob('carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

# ==============================================================================
# -- imports -------------------------------------------------------------------
# ==============================================================================
import carla
from carla import ColorConverter as cc

try:
    import pygame
except ImportError:
    raise RuntimeError('cannot import pygame, make sure pygame package is installed')

import weakref
import math
import numpy as np
from defaults import Defaults
from camera import PinholeCamera

# ==============================================================================
# -- CameraManager -------------------------------------------------------------
# ==============================================================================


class CameraManager(object):
    def __init__(self, parent_actor, width, height, gamma_correction, queueLength = None, fov = None):
        
        if queueLength == None:
            queueLength = Defaults.queueLength

        if fov == None:
            fov = Defaults.fov

        self.width = width
        self.height = height
        self.fov = fov

        self.focal = self.width / (2.0 * np.tan(self.fov * np.pi / 360.0))
        self.distCoeff = [0.0, 0.0, 0.0, 0.0, 0.0]
        
        self.sensor = None
        self.surface = None

        self._parent = parent_actor
        
        self.queueLength = queueLength

        self.cameraQueue = []
        self.depthQueue = []

        self.camera = PinholeCamera(width, height, self.focal, self.focal, width / 2.0, height / 2.0, self.distCoeff)

        self.camera_transform = (carla.Transform(carla.Location(x=2.5, z=1.2)), carla.AttachmentType.Rigid)
        
        """ ['sensor.camera.rgb', cc.Raw, 'Camera RGB Distorted',
                {'lens_circle_multiplier': '3.0',
                'lens_circle_falloff': '3.0',
                'chromatic_aberration_intensity': '0.5',
                'chromatic_aberration_offset': '0'}] """

        self.sensors = [
            ['sensor.camera.rgb', cc.Raw, 'Camera RGB', {'bloom_intensity': '0.0', 'lens_flare_intensity': '0.0', 'motion_blur_intensity': '0.0'}],
            ['sensor.camera.depth', cc.Raw, 'Camera Depth', {}],]

        self.rgbaSensor = None
        self.depthSensor = None

        world = self._parent.get_world()
        bp_library = world.get_blueprint_library()

        for item in self.sensors:
            bp = bp_library.find(item[0])
            if item[0].startswith('sensor.camera'):
                bp.set_attribute('image_size_x', str(self.width))
                bp.set_attribute('image_size_y', str(self.height))
                bp.set_attribute('fov', str(self.fov))

                if bp.has_attribute('gamma'):
                    bp.set_attribute('gamma', str(gamma_correction))

                for attr_name, attr_value in item[3].items():
                    bp.set_attribute(attr_name, attr_value)

            item.append(bp)

        self.init_sensors()

    @property
    def cameraConfig(self):
        return self.camera.cameraConfig

    def init_sensors(self):
        if self.rgbaSensor is not None:
            self.rgbaSensor.destroy()
            self.surface = None

        if self.depthSensor is not None:
            self.depthSensor.destroy()
            self.surface = None
        
        self.rgbaSensor = self._parent.get_world().spawn_actor(
            self.sensors[0][-1],
            self.camera_transform[0],
            attach_to=self._parent,
            attachment_type=self.camera_transform[1])

        self.depthSensor = self._parent.get_world().spawn_actor(
            self.sensors[1][-1],
            self.camera_transform[0],
            attach_to=self._parent,
            attachment_type=self.camera_transform[1])
        
        # We need to pass the lambda a weak reference to self to avoid
        # circular reference.
        weak_self = weakref.ref(self)

        self.rgbaSensor.listen(lambda image: CameraManager._parse_rgba_image(weak_self, image))
        self.depthSensor.listen(lambda image: CameraManager._parse_depth_image(weak_self, image))

    def render(self, display):
        if self.surface is not None:
            display.blit(self.surface, (0, 0))

    def popQueues(self):
        if len(self.cameraQueue) > 1 and len(self.depthQueue) > 1:
            cameraData = self.cameraQueue.pop(0)
            depthData = self.depthQueue.pop(0)

            #sync dei frame
            if cameraData["frame"] > depthData["frame"]:
                if len(self.depthQueue) > 1:
                    depthData = self.depthQueue.pop(0)

            elif cameraData["frame"] < depthData["frame"]:
                if len(self.cameraQueue) > 1:
                    cameraData = self.cameraQueue.pop(0)
            
            return cameraData, depthData
        
        return None

    @staticmethod
    def _parse_rgba_image(weak_self, image):
        self = weak_self()
        if not self:
            return
        
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))   #BGRA

        bgrImage = array[:, :, :3] #BGR
        rgbImage = bgrImage[:, :, ::-1] #RGB

        #rgbImage = cv.cvtColor(bgrImage, cv.COLOR_BGR2RGB)
        self.surface = pygame.surfarray.make_surface(rgbImage.swapaxes(0, 1))

        myDict = {"imageRGB": rgbImage, "imageBGR": bgrImage, "frame": image.frame, "timestamp":image.timestamp, "transform": image.transform}

        if len(self.cameraQueue) >= self.queueLength:
            toDiscart = len(self.cameraQueue) - self.queueLength + 1
            self.cameraQueue = self.cameraQueue[toDiscart:]

        self.cameraQueue.append(myDict)

        
    @staticmethod
    def _parse_depth_image(weak_self, image):
        self = weak_self()
        if not self:
            return
        
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))   #BGRA
        array = array[:, :, :3] #BGR

        depthArray = (array[:,:,2] + array[:,:,1] * 256 + array[:,:,0] * 65536) / 16777215.0 # BGR -> normalized
        depthArray = depthArray * 1000 # normalized -> meters
        depthArray = np.reshape(depthArray, (array.shape[0], array.shape[1], 1)) # (H, W, 1)

        myDict = {"image": depthArray, "frame": image.frame, "timestamp":image.timestamp, "transform": image.transform}

        if len(self.depthQueue) >= self.queueLength:
            toDiscart = len(self.depthQueue) - self.queueLength + 1
            self.depthQueue = self.depthQueue[toDiscart:]

        self.depthQueue.append(myDict)

        
# ==============================================================================
# -- GnssSensor ----------------------------------------------------------------
# ==============================================================================


class GnssSensor(object):
    def __init__(self, parent_actor, transform = None, queueLength = None):
        
        if transform == None:
            transform = carla.Transform()
        
        if queueLength == None:
            queueLength = Defaults.queueLength
        
        self.sensor = None
        self._parent = parent_actor
        self.lat = 0.0
        self.lon = 0.0
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.gnss')

        self.queueLength = queueLength

        self.gnssQueue = []

        self.sensor = world.spawn_actor(bp, transform, attach_to=self._parent)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda data: GnssSensor._on_gnss_event(weak_self, data))

    @staticmethod
    def _on_gnss_event(weak_self, data):
        self = weak_self()
        if not self:
            return
        self.lat = data.latitude
        self.lon = data.longitude

        myDict = {"data": data, "frame": data.frame, "timestamp": data.timestamp, "transform": data.transform}

        if len(self.gnssQueue) >= self.queueLength:
            toDiscart = len(self.gnssQueue) - self.queueLength + 1
            self.gnssQueue = self.gnssQueue[toDiscart:]        

        self.gnssQueue.append(myDict)


# ==============================================================================
# -- IMUSensor -----------------------------------------------------------------
# ==============================================================================


class IMUSensor(object):
    def __init__(self, parent_actor, transform = None, queueLength = None):
        
        if transform == None:
            transform = carla.Transform()
        
        if queueLength == None:
            queueLength = Defaults.queueLength
        
        self.sensor = None
        self._parent = parent_actor
        self.accelerometer = (0.0, 0.0, 0.0)
        self.gyroscope = (0.0, 0.0, 0.0)
        self.compass = 0.0
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.imu')

        self.queueLength = queueLength

        self.imuQueue = []

        self.sensor = world.spawn_actor(
            bp, transform, attach_to=self._parent)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(
            lambda data: IMUSensor._IMU_callback(weak_self, data))

    @staticmethod
    def _IMU_callback(weak_self, data):
        self = weak_self()
        if not self:
            return
        limits = (-99.9, 99.9)
        self.accelerometer = (
            max(limits[0], min(limits[1], data.accelerometer.x)),
            max(limits[0], min(limits[1], data.accelerometer.y)),
            max(limits[0], min(limits[1], data.accelerometer.z)))
        self.gyroscope = (
            max(limits[0], min(limits[1], math.degrees(data.gyroscope.x))),
            max(limits[0], min(limits[1], math.degrees(data.gyroscope.y))),
            max(limits[0], min(limits[1], math.degrees(data.gyroscope.z))))
        self.compass = math.degrees(data.compass)

        myDict = {"data": data, "frame": data.frame, "timestamp": data.timestamp, "transform": data.transform}

        if len(self.imuQueue) >= self.queueLength:
            toDiscart = len(self.imuQueue) - self.queueLength + 1
            self.imuQueue = self.imuQueue[toDiscart:]

        self.imuQueue.append(myDict)
