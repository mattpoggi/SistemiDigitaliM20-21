
# Copyright (c) 2019 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

# Allows controlling a vehicle with a keyboard. For a simpler and more
# documented example, please take a look at tutorial.py.


"""
Welcome to CARLA manual control.
Modificato per gestire il cruise control.

Use ARROWS or WASD keys for control.

    W            : throttle
    S            : brake
    A/D          : steer left/right
    Q            : toggle reverse

    L            : toggle next light type
    I            : toggle high beam

    K            : toggle cruise control

    [1-9]        : change to sensor [1-9]

    F1           : toggle HUD

    ESC          : quit
"""

from __future__ import print_function


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

try:
    import pygame
except ImportError:
    raise RuntimeError('cannot import pygame, make sure pygame package is installed')


import numpy as np
import cv2 as cv
import argparse
import logging
import random
import weakref
import time
import math
from hud import HUD
from carla_control import PIDController
from controller import KeyboardControl
from sensors import CameraManager
from sensors import GnssSensor
from sensors import IMUSensor
from client import CruiseClient
from defaults import Defaults

# ==============================================================================
# -- Global functions ----------------------------------------------------------
# ==============================================================================

def get_actor_display_name(actor, truncate=250):
    name = ' '.join(actor.type_id.replace('_', '.').title().split('.')[1:])
    return (name[:truncate - 1] + u'\u2026') if len(name) > truncate else name

# ==============================================================================
# -- World ---------------------------------------------------------------------
# ==============================================================================


class World(object):
    def __init__(self, cruise, carla_world, hud, args):
        self.loggingName = "World"

        self.world = carla_world
        self.actor_role_name = "MonocularCruiseControl"
        try:
            self.map = self.world.get_map()
        except RuntimeError as error:
            print('RuntimeError: {}'.format(error))
            print('  The server could not send the OpenDRIVE (.xodr) file:')
            print('  Make sure it exists, has the same name of your town, and is correct.')
            sys.exit(1)

        self.cruise = cruise
        self.useCruiseControl = False
        self.plotPointCloud = False
        self.cruiseResult = None
        self.cruiseFps = float('nan')
        self.velocitaCrociera = float('nan')
        self.cruiseRequestFrame = True

        self.pidController = PIDController()

        self.hud = hud
        self.player = None

        self.gnss_sensor = None
        self.imu_sensor = None
        self.camera_manager = None

        self._actor_filter = args.filter
        self._gamma = args.gamma

        self.restart()
        self.world.on_tick(hud.on_world_tick)

    def restart(self):
        self.player_max_speed = 1.589
        self.player_max_speed_fast = 3.713

        # Get a random blueprint.
        blueprint = random.choice(self.world.get_blueprint_library().filter(self._actor_filter))
        blueprint.set_attribute('role_name', self.actor_role_name)

        if blueprint.has_attribute('color'):
            color = random.choice(blueprint.get_attribute('color').recommended_values)
            blueprint.set_attribute('color', color)
        if blueprint.has_attribute('driver_id'):
            driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
            blueprint.set_attribute('driver_id', driver_id)
        if blueprint.has_attribute('is_invincible'):
            blueprint.set_attribute('is_invincible', 'true')

        # set the max speed
        if blueprint.has_attribute('speed'):
            self.player_max_speed = float(blueprint.get_attribute('speed').recommended_values[1])
            self.player_max_speed_fast = float(blueprint.get_attribute('speed').recommended_values[2])
        else:
            logging.debug("{0} No recommended values for 'speed' attribute".format(self.loggingName))

        # Spawn the player.
        if self.player is not None:
            spawn_point = self.player.get_transform()
            spawn_point.location.z += 2.0
            spawn_point.rotation.roll = 0.0
            spawn_point.rotation.pitch = 0.0
            self.destroy()
            self.player = self.world.try_spawn_actor(blueprint, spawn_point)
            self.modify_vehicle_physics(self.player)
            

        while self.player is None:
            if not self.map.get_spawn_points():
                print('There are no spawn points available in your map/town.')
                print('Please add some Vehicle Spawn Point to your UE4 scene.')
                sys.exit(1)
            spawn_points = self.map.get_spawn_points()
            spawn_point = random.choice(spawn_points) if spawn_points else carla.Transform()
            self.player = self.world.try_spawn_actor(blueprint, spawn_point)
            self.modify_vehicle_physics(self.player)

        # Set up the sensors.
        self.gnss_sensor = GnssSensor(self.player)
        self.imu_sensor = IMUSensor(self.player)

        self.camera_manager = CameraManager(self.player, self.hud.dim[0], self.hud.dim[1], self._gamma)
        self.camera_manager.init_sensors()

        actor_type = get_actor_display_name(self.player)
        self.hud.notification(actor_type) 

    @staticmethod
    def activateCruiseCallback(weak_self, result):
        self = weak_self()
        if not self:
            return

        self.pidController.destroy()
        self.pidController = PIDController()

        logging.info("{0} stato cruise: {1}".format(self.loggingName, result))
        self.useCruiseControl = result

    def toggleCruise(self):
        if self.useCruiseControl:
            self.useCruiseControl = False
            return

        v = self.player.get_velocity()
        w, h, fx, fy, cx, cy, D = self.camera_manager.cameraConfig

        roi = Defaults.roi

        self.velocitaCrociera = math.sqrt(v.x**2 + v.y**2 + v.z**2)
        self.pidController.set_target_speed(self.velocitaCrociera)

        distanzaMinima = Defaults.distanzaMinima
        distanzaMassima = Defaults.distanzaMassima

        weak_self = weakref.ref(self)
        callback = lambda result: World.activateCruiseCallback(weak_self, result)

        self.cruise.cmdInit(callback, w, h, fx, fy, cx, cy, D, roi, self.velocitaCrociera, distanzaMinima, distanzaMassima)

    @staticmethod
    def runCruiseCallback(weak_self, frame, velocitaUscita, accelerazione, parseTime, inferenceTime, calibrationTime):
        self = weak_self()
        if not self:
            return

        self.cruiseRequestFrame = True

        if frame is None:
            return
        
        self.cruiseFps = 1/(time.time() - self.sendFrameTime)
        self.cruiseResult = (frame, velocitaUscita, accelerazione, parseTime, inferenceTime, calibrationTime)
        
        self.pidController.set_target_speed(velocitaUscita)
        self.pidController.set_target_accel(accelerazione)

        logging.debug("{0} velocitaUscita: {1} m/s, accelerazione: {2} m/s^2".format(self.loggingName, velocitaUscita, accelerazione))

    def runCruise(self):
        if not self.useCruiseControl or not self.cruiseRequestFrame:
            return

        data = self.camera_manager.popQueues()

        if data is not None:
            cameraData, depthData = data

            imageBGR = cameraData['imageBGR']
            imageGT = depthData['image']
            transform = cameraData['transform']

            dictTransform = {'location': {'x': transform.location.x, 'y': transform.location.y, 'z': transform.location.z}, 'rotation':{'roll': transform.rotation.roll, 'pitch': transform.rotation.pitch, 'yaw': transform.rotation.yaw}}

            weak_self = weakref.ref(self)
            callback = lambda frame, velocitaUscita, accelerazione, parseTime, inferenceTime, calibrationTime: World.runCruiseCallback(weak_self, frame, velocitaUscita, accelerazione, parseTime, inferenceTime, calibrationTime)

            self.sendFrameTime = time.time()

            self.cruise.cmdFrameCarlaRt(callback, dictTransform, imageBGR, imageGT)
            self.cruiseRequestFrame = False

    def modify_vehicle_physics(self, vehicle):
        physics_control = vehicle.get_physics_control()
        physics_control.use_sweep_wheel_collision = True
        self.pidController.vehicle_info_updated(physics_control.mass)
        logging.debug("{0} mass: {1}".format(self.loggingName, physics_control.mass))
        vehicle.apply_physics_control(physics_control)
        
    def pidControllerTick(self):
        t = self.player.get_transform()
        v = self.player.get_velocity()
        velocity = math.sqrt(v.x**2 + v.y**2 + v.z**2)
        pitch = t.rotation.pitch

        #f = open("speed_pid", 'r')
        #lines = f.readlines()
        #sKp, sKi, sKd = float(lines[0]), float(lines[1]), float(lines[2])
        #f.close()
        #f = open("accel_pid", 'r')
        #lines = f.readlines()
        #aKp, aKi, aKd = float(lines[0]), float(lines[1]), float(lines[2])
        #f.close()
        #logging.debug("{0} - {1}".format(self.loggingName, (sKp, sKi, sKd, aKp, aKi, aKd)))
        #self.pidController.updatePIDParameters(sKp, sKi, sKd, aKp, aKi, aKd)

        self.pidController.vehicle_status_updated(velocity, pitch)
        self.pidController.run()

    def tick(self, clock):
        self.pidControllerTick()
        self.hud.tick(self, clock)

    def render(self, display):
        self.camera_manager.render(display)
        self.hud.render(display)

    def destroy_sensors(self):
        self.camera_manager.sensor.destroy()
        self.camera_manager.sensor = None
        self.camera_manager.index = None

    def destroy(self):

        sensors = [
            self.camera_manager.rgbaSensor,
            self.camera_manager.depthSensor,
            self.gnss_sensor.sensor,
            self.imu_sensor.sensor]

        for sensor in sensors:
            if sensor is not None:
                sensor.stop()
                sensor.destroy()

        if self.player is not None:
            self.player.destroy()

# ==============================================================================
# -- game_loop() ---------------------------------------------------------------
# ==============================================================================


def game_loop(args):
    pygame.init()
    pygame.font.init()
    world = None

    try:
        cruiseClient = CruiseClient(args.hostCruise, args.portCruiseTcp, args.portCruiseUdp, args.timeout)
        cruiseClient.connect()

        client = carla.Client(args.hostCarla, args.portCarla)
        client.set_timeout(5.0)

        carla_world = client.get_world()
        #settings = carla_world.get_settings()

        # We set CARLA syncronous mode
        #settings.fixed_delta_seconds = 0.1
        #settings.synchronous_mode = True
        #carla_world.apply_settings(settings)

        display = pygame.display.set_mode(
            (args.width, args.height),
            pygame.HWSURFACE | pygame.DOUBLEBUF)

        display.fill((0,0,0))
        
        pygame.display.flip()

        width = args.width
        height = args.height
        
        hud = HUD(width, height)
        world = World(cruiseClient, carla_world, hud, args)
        controller = KeyboardControl(world)

        clock = pygame.time.Clock()
        while True:
            clock.tick_busy_loop(60)
            if controller.parse_events(client, world, clock):
                return

            world.runCruise()
            world.tick(clock)            
            world.render(display)
            pygame.display.flip()
    finally:
        if world is not None:
            world.destroy()

        pygame.quit()


def main():
    argparser = argparse.ArgumentParser(
        description='CARLA Cruise Control Client')
    argparser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='debug',
        help='print debug information')
    argparser.add_argument(
        '--hostCarla',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '--portCarla',
        metavar='PCr',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '--hostCruise',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '--portCruiseTcp',
        metavar='PCT',
        default=5050,
        type=int,
        help='TCP port to listen to (default: 5050)')
    argparser.add_argument(
        '--portCruiseUdp',
        metavar='PCU',
        default=5051,
        type=int,
        help='UDP port to listen to (default: 5051)')
    argparser.add_argument(
        '-t', '--timeout',
        metavar='T',
        default=Defaults.timeout,
        type=int,
        help='Timeout (default: {0})'.format(Defaults.timeout))
    argparser.add_argument(
        '--res',
        metavar='WIDTHxHEIGHT',
        default='640x384',
        help='window resolution (default: 640x384)')
    argparser.add_argument(
        '--filter',
        metavar='PATTERN',
        default='vehicle.tesla.model3',
        help='actor filter (default: "vehicle.tesla.model3")')
    argparser.add_argument(
        '--gamma',
        default=2.2,
        type=float,
        help='Gamma correction of the camera (default: 2.2)')
    args = argparser.parse_args()

    args.width, args.height = [int(x) for x in args.res.split('x')]

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)
    logging.info('listening to server CARLA %s:%s', args.hostCarla, args.portCarla)
    logging.info('listening to server CRUISE TCP %s:%s, UDP %s:%s', args.hostCruise, args.portCruiseTcp, args.hostCruise, args.portCruiseUdp)

    print(__doc__)

    try:
        game_loop(args)
    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')

if __name__ == '__main__':
    main()
