#!/usr/bin/env python

#
# Copyright (c) 2019 Intel Corporation
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.
#
"""
Control Carla vehicle
"""
import sys
import datetime
import numpy
import time

from simple_pid import PID
import carla_control_physics as phys  # pylint: disable=relative-import


class PIDController(object):

    """
    Convert ackermann_drive messages to carla VehicleCommand with a PID controller
    """

    def __init__(self):
        """
        Constructor

        """

        self.frequency = 1000.0 #Hz

        self.info = {}

        # target values
        self.info['target'] = {}
        self.info['target']['speed'] = 0.
        self.info['target']['accel'] = 0.

        # current values
        self.info['current'] = {}
        self.info['current']['time_sec'] = time.time()
        self.info['current']['speed'] = 0.
        self.info['current']['accel'] = 0.

        # control values
        self.info['status'] = {}
        self.info['status']['status'] = 'n/a'

        self.info['status']['speed_control_activation_count'] = 0
        self.info['status']['speed_control_accel_delta'] = 0.
        self.info['status']['speed_control_accel_target'] = 0.

        self.info['status']['accel_control_pedal_delta'] = 0.
        self.info['status']['accel_control_pedal_target'] = 0.

        self.info['status']['brake_upper_border'] = 0.
        self.info['status']['throttle_lower_border'] = 0.

        # restriction values
        self.info['restrictions'] = {}

        # control output
        self.info['output'] = {}
        self.info['output']['throttle'] = 0.
        self.info['output']['brake'] = 1.0

        # set initial maximum values
        self.vehicle_info_updated()

        # PID controller
        # the controller has to run with the simulation time, not with real-time

        # we might want to use a PID controller to reach the final target speed
        self.speed_controller = PID(Kp=1.5,
                                    Ki=0.0,
                                    Kd=0.5,
                                    sample_time=0.001,
                                    output_limits=(0.0, self.info['restrictions']['max_speed']))

        self.accel_controller = PID(Kp=1.1,
                                    Ki=0.0,
                                    Kd=0.1,
                                    sample_time=0.001,
                                    output_limits=(-self.info['restrictions']['max_decel'], self.info['restrictions']['max_accel']))

    @property
    def throttle(self):
        return self.info['output']['throttle']
    
    @property
    def brake(self):
        return self.info['output']['brake']

    def destroy(self):
        """
        Function (override) to destroy this object.

        Finish the PID controllers.
        :return:
        """
        self.speed_controller = None
        self.accel_controller = None

    def updatePIDParameters(self, sKp, sKi, sKd, aKp, aKi, aKd):
        if (self.speed_controller.Kp, self.speed_controller.Ki, self.speed_controller.Kd) != (sKp, sKi, sKd):
            self.speed_controller.tunings = (sKp, sKi, sKd)
        if (self.accel_controller.Kp, self.accel_controller.Ki, self.accel_controller.Kd) != (aKp, aKi, aKd):
            self.accel_controller.tunings = (aKp, aKi, aKd)

    def vehicle_status_updated(self, velocity, pitch):
        """
        Stores the car status for the next controller calculation
        :return:
        """
        # set target values
        self.vehicle_status = {'velocity': velocity, 'orientation': {'pitch': pitch}}

    def vehicle_info_updated(self, carMass = None):
        """
        Stores the car info for the next controller calculation
        :return:
        """
        # set target values
        self.vehicle_info = {}

        if carMass is not None:
            self.vehicle_info['mass'] = carMass

        # calculate restrictions
        self.info['restrictions']['max_speed'] = phys.get_vehicle_max_speed(self.vehicle_info)
        self.info['restrictions']['max_accel'] = phys.get_vehicle_max_acceleration(self.vehicle_info)
        self.info['restrictions']['max_decel'] = phys.get_vehicle_max_deceleration(self.vehicle_info)
        self.info['restrictions']['min_accel'] = 1.0

        # clipping the pedal in both directions to the same range using the usual lower
        # border: the max_accel to ensure the the pedal target is in symmetry to zero

        self.info['restrictions']['max_pedal'] = min(
            self.info['restrictions']['max_accel'], self.info['restrictions']['max_decel'])

    def set_target_speed(self, target_speed):
        """
        set target speed
        """
        if abs(target_speed) > self.info['restrictions']['max_speed']:
            
            self.info['target']['speed'] = numpy.clip(
                target_speed, -self.info['restrictions']['max_speed'], self.info['restrictions']['max_speed'])
        else:
            self.info['target']['speed'] = target_speed

    def set_target_accel(self, target_accel):
        """
        set target accel
        """
        epsilon = 0.1
        # if speed is set to zero, then use max decel value
        if self.info['target']['speed'] < epsilon:
            self.info['target']['accel'] = -self.info['restrictions']['max_decel']
        else:
            self.info['target']['accel'] = numpy.clip(
                target_accel, -self.info['restrictions']['max_decel'], self.info['restrictions']['max_accel'])

    def vehicle_control_cycle(self):
        """
        Perform a vehicle control cycle and sends out CarlaEgoVehicleControl message
        """
        # perform actual control
        self.run_speed_control_loop()
        self.run_accel_control_loop()
        self.update_drive_vehicle_control_command()            

    def run_speed_control_loop(self):
        """
        Run the PID control loop for the speed

        The speed control is only activated if desired acceleration is moderate
        otherwhise we try to follow the desired acceleration values

        Reasoning behind:

        An autonomous vehicle calculates a trajectory including position and velocities.
        The ackermann drive is derived directly from that trajectory.
        The acceleration and jerk values provided by the ackermann drive command
        reflect already the speed profile of the trajectory.
        It makes no sense to try to mimick this a-priori knowledge by the speed PID
        controller.
        =>
        The speed controller is mainly responsible to keep the speed.
        On expected speed changes, the speed control loop is disabled
        """
        epsilon = 0.00001
        target_accel_abs = abs(self.info['target']['accel'])

        if target_accel_abs < self.info['restrictions']['min_accel']:
            if self.info['status']['speed_control_activation_count'] < 2:
                self.info['status']['speed_control_activation_count'] += 1
        else:
            if self.info['status']['speed_control_activation_count'] > 0:
                self.info['status']['speed_control_activation_count'] -= 1

        # set the auto_mode of the controller accordingly
        self.speed_controller.set_auto_mode(self.info['status']['speed_control_activation_count'] >= 2)

        if self.speed_controller.auto_mode:
            self.speed_controller.setpoint = self.info['target']['speed']
            self.info['status']['speed_control_accel_target'] = self.speed_controller(self.info['current']['speed'])

            # clipping borders
            clipping_lower_border = -target_accel_abs
            clipping_upper_border = target_accel_abs

            # per definition of ackermann drive: if zero, then use max value
            if target_accel_abs < epsilon:
                clipping_lower_border = -self.info['restrictions']['max_decel']
                clipping_upper_border = self.info['restrictions']['max_accel']

            self.info['status']['speed_control_accel_target'] = numpy.clip(
                self.info['status']['speed_control_accel_target'],
                clipping_lower_border, clipping_upper_border)
        else:
            self.info['status']['speed_control_accel_delta'] = 0.
            self.info['status']['speed_control_accel_target'] = self.info['target']['accel']

    def run_accel_control_loop(self):
        """
        Run the PID control loop for the acceleration
        """
        # setpoint of the acceleration controller is the output of the speed controller
        self.accel_controller.setpoint = self.info['status']['speed_control_accel_target']
        self.info['status']['accel_control_pedal_target'] = self.accel_controller(self.info['current']['accel'])

        # @todo: we might want to scale by making use of the the abs-jerk value
        # If the jerk input is big, then the trajectory input expects already quick changes
        # in the acceleration; to respect this we put an additional proportional factor on top
        self.info['status']['accel_control_pedal_target'] = numpy.clip(
            self.info['status']['accel_control_pedal_target'],
            -self.info['restrictions']['max_pedal'], self.info['restrictions']['max_pedal'])

    def update_drive_vehicle_control_command(self):
        """
        Apply the current speed_control_target value to throttle/brake commands
        """

        # the driving impedance moves the 'zero' acceleration border
        # Interpretation: To reach a zero acceleration the throttle has to pushed
        # down for a certain amount
        self.info['status']['throttle_lower_border'] = phys.get_vehicle_driving_impedance_acceleration(
            self.vehicle_info, self.vehicle_status, False)

        # the engine lay off acceleration defines the size of the coasting area
        # Interpretation: The engine already prforms braking on its own;
        #  therefore pushing the brake is not required for small decelerations
        self.info['status']['brake_upper_border'] = self.info['status']['throttle_lower_border'] + \
            phys.get_vehicle_lay_off_engine_acceleration(self.vehicle_info)

        if self.info['status']['accel_control_pedal_target'] > self.info['status']['throttle_lower_border']:
            self.info['status']['status'] = "accelerating"
            self.info['output']['brake'] = 0.0
            # the value has to be normed to max_pedal
            # be aware: is not required to take throttle_lower_border into the scaling factor,
            # because that border is in reality a shift of the coordinate system
            # the global maximum acceleration can practically not be reached anymore because of
            # driving impedance
            self.info['output']['throttle'] = (
                (self.info['status']['accel_control_pedal_target'] -
                 self.info['status']['throttle_lower_border']) /
                abs(self.info['restrictions']['max_pedal']))
        elif self.info['status']['accel_control_pedal_target'] > self.info['status']['brake_upper_border']:
            self.info['status']['status'] = "coasting"
            # no control required
            self.info['output']['brake'] = 0.0
            self.info['output']['throttle'] = 0.0
        else:
            self.info['status']['status'] = "braking"
            # braking required
            self.info['output']['brake'] = (
                (self.info['status']['brake_upper_border'] -
                 self.info['status']['accel_control_pedal_target']) /
                abs(self.info['restrictions']['max_pedal']))
            self.info['output']['throttle'] = 0.0

        # finally clip the final control output (should actually never happen)
        self.info['output']['brake'] = numpy.clip(
            self.info['output']['brake'], 0., 1.)
        self.info['output']['throttle'] = numpy.clip(
            self.info['output']['throttle'], 0., 1.)

    def update_current_values(self):
        """
        Function to update vehicle control current values.

        we calculate the acceleration on ourselves, because we are interested only in
        the acceleration in respect to the driving direction
        In addition a small average filter is applied

        :return:
        """
        current_time_sec = time.time()
        delta_time = current_time_sec - self.info['current']['time_sec']
        current_speed = self.vehicle_status['velocity']

        if delta_time > (1/self.frequency):
            delta_speed = current_speed - self.info['current']['speed']
            current_accel = delta_speed / delta_time
            # average filter
            self.info['current']['accel'] = (self.info['current']['accel'] * 4 + current_accel) / 5

        self.info['current']['time_sec'] = current_time_sec
        self.info['current']['speed'] = current_speed

    def run(self):
        self.update_current_values()
        self.vehicle_control_cycle()

        