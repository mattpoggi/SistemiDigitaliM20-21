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

    ESC          : quit
"""

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

import time
import datetime
import math
from defaults import Defaults
from utils_frame import FrameBuffer

# ==============================================================================
# -- Global functions ----------------------------------------------------------
# ==============================================================================

def get_actor_display_name(actor, truncate=250):
    name = ' '.join(actor.type_id.replace('_', '.').title().split('.')[1:])
    return (name[:truncate - 1] + u'\u2026') if len(name) > truncate else name

# ==============================================================================
# -- HUD -----------------------------------------------------------------------
# ==============================================================================


class HUD(object):
    def __init__(self, width, height):
        self.dim = (width, height)
        
        font = pygame.font.Font(pygame.font.get_default_font(), 20)
        font_name = 'courier' if os.name == 'nt' else 'mono'
        fonts = [x for x in pygame.font.get_fonts() if font_name in x]
        default_font = 'ubuntumono'
        mono = default_font if default_font in fonts else fonts[0]
        mono = pygame.font.match_font(mono)

        self._font_mono = pygame.font.Font(mono, 12 if os.name == 'nt' else 14)
        self._notifications = FadingText(font, (width, 40), (0, height - 40))
        self.help = HelpText(pygame.font.Font(mono, 16), width, height)
        self.server_fps = 0
        self.frame = 0
        self.simulation_time = 0
        self._show_info = True
        self._info_text = []
        self._server_clock = pygame.time.Clock()

        self.view = 1
        self.pointsDrawner0 = PointsDrawner(self.dim, (0,0), Defaults.circleColor0)
        self.pointsDrawner1 = PointsDrawner(self.dim, (0,0), Defaults.circleColor1)
        self.pointsDrawner2 = PointsDrawner(self.dim, (0,0), Defaults.circleColor2)
        self.lineDrawner = LineDrawner(self.dim, (0,0))
        self.rectDrawner = RectDrawner(self.dim, (0,0))
        self.imageDrawner = ImageDrawner(self.dim, (0,0))
        
    def on_world_tick(self, timestamp):
        self._server_clock.tick()
        self.server_fps = self._server_clock.get_fps()
        self.frame = timestamp.frame
        self.simulation_time = timestamp.elapsed_seconds

    def tick(self, world, clock):
        self._notifications.tick(world, clock)

        #if not self._show_info:
        #    return
            
        t = world.player.get_transform()
        v = world.player.get_velocity()
        c = world.player.get_control()

        if world.useCruiseControl and world.cruiseResult:
            frame, velocitaUscita, accelerazione, parseTime, inferenceTime, calibrationTime = world.cruiseResult

            cruiseFPS = world.cruiseFps

            velocitaCrociera = world.velocitaCrociera * 3.6 if not math.isnan(world.velocitaCrociera) else float('nan')

            scaleFactor = frame[FrameBuffer.SCALE_FACTOR] if FrameBuffer.SCALE_FACTOR in frame else float('nan')
            shiftFactor = frame[FrameBuffer.SHIFT_FACTOR] if FrameBuffer.SHIFT_FACTOR in frame else float('nan')

            gtError = frame[FrameBuffer.CALIBRATED_PREDICTION_ERROR] if FrameBuffer.CALIBRATED_PREDICTION_ERROR in frame else float('nan')
            gtErrorThreshold = frame[FrameBuffer.CALIBRATED_PREDICTION_THRESHOLD_ERROR] if FrameBuffer.CALIBRATED_PREDICTION_THRESHOLD_ERROR in frame else float('nan')
            zError = frame[FrameBuffer.TRIANGULATION_ERROR_Z] if FrameBuffer.TRIANGULATION_ERROR_Z in frame else float('nan')

            num_of_points2d = 0
            num_of_points3d = 0

            if FrameBuffer.POINTS_2D in frame:
                num_of_points2d = len(frame[FrameBuffer.POINTS_2D])
                self.pointsDrawner0.setPoints(frame[FrameBuffer.POINTS_2D])

                if FrameBuffer.POINTS_2D_NEXT_FRAME in frame:
                    self.pointsDrawner1.setPoints(frame[FrameBuffer.POINTS_2D_NEXT_FRAME])
                    self.lineDrawner.setPoints(frame[FrameBuffer.POINTS_2D], frame[FrameBuffer.POINTS_2D_NEXT_FRAME])

            if FrameBuffer.POINTS_3D in frame:
                num_of_points3d = len(frame[FrameBuffer.POINTS_3D])

                if world.camera_manager is not None:
                    projPoints = world.camera_manager.camera.project(frame[FrameBuffer.POINTS_3D]).T
                    projPoints = projPoints[:2].T.tolist()
                    self.pointsDrawner2.setPoints(projPoints)
        
            if FrameBuffer.ROI in frame:
                x0,y0,w,h = frame[FrameBuffer.ROI]
            else:
                x0,y0,w,h = Defaults.roi
                
            self.rectDrawner.setPoints((x0,y0), (x0+w,y0+h))

            self._info_text = [
                'Server:  % 16.0f FPS' % self.server_fps,
                'Client:  % 16.0f FPS' % clock.get_fps(),
                'Cruise:  % 16.0f FPS' % cruiseFPS,
                'Vehicle: % 20s' % get_actor_display_name(world.player, truncate=20),
                'Map:     % 20s' % world.map.name,
                'Simulation time: % 12s' % datetime.timedelta(seconds=int(self.simulation_time)),
                'Speed:   % 14.1f km/h' % (3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2)),
                'Cruise S:% 11.1f km/h' % (velocitaUscita * 3.6),
                'Cruise A:% 10.2f m/s^2' % accelerazione,
                'Location:% 20s' % ('(% 5.1f, % 5.1f)' % (t.location.x, t.location.y)),
                'Rotation:% 20s' % ('(% 5.1f, % 5.1f, % 5.1f)' % (t.rotation.roll, t.rotation.pitch, t.rotation.yaw)),
                'Scale Factor: %2.4f ' % scaleFactor,
                'Shift Factor: %2.4f ' % shiftFactor,
                'GTError (> %2.0f m): %3.00f %%' % (gtErrorThreshold, gtError),
                'Tr.ErrorZ: %2.0f m' % zError,
                'Points: 2D %5d, 3D %5d ' % (num_of_points2d, num_of_points3d),
                'CR Time: (I: %1.3f, C: %1.3f)' % (inferenceTime, calibrationTime)]
        else:
                self._info_text = [
                'Server:  % 16.0f FPS' % self.server_fps,
                'Client:  % 16.0f FPS' % clock.get_fps(),
                'Vehicle: % 20s' % get_actor_display_name(world.player, truncate=20),
                'Map:     % 20s' % world.map.name,
                'Simulation time: % 12s' % datetime.timedelta(seconds=int(self.simulation_time)),
                'Speed:   % 15.0f km/h' % (3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2)),
                'Location:% 20s' % ('(% 5.1f, % 5.1f)' % (t.location.x, t.location.y)),
                'Rotation:% 20s' % ('(% 5.1f, % 5.1f, % 5.1f)' % (t.rotation.roll, t.rotation.pitch, t.rotation.yaw)),
                'Accelero: (%5.1f,%5.1f,%5.1f)' % (world.imu_sensor.accelerometer),
                '']

        if isinstance(c, carla.VehicleControl):
            self._info_text += [
                ('Throttle:', c.throttle, 0.0, 1.0),
                ('Steer:', c.steer, -1.0, 1.0),
                ('Brake:', c.brake, 0.0, 1.0),
                ('Reverse:', c.reverse),
                'Gear:        %s' % {-1: 'R', 0: 'N'}.get(c.gear, c.gear)]

    def toggle_info(self):
        self._show_info = not self._show_info

    def notification(self, text, seconds=2.0):
        self._notifications.set_text(text, seconds=seconds)

    def error(self, text):
        self._notifications.set_text('Error: %s' % text, (255, 0, 0))

    def render(self, display):
        if self.view == 1:
            self.pointsDrawner0.render(display)
            self.pointsDrawner1.render(display)
            self.pointsDrawner2.render(display)
            self.lineDrawner.render(display)
            self.rectDrawner.render(display)
            
        if self._show_info:
            info_surface = pygame.Surface((220, self.dim[1]))
            info_surface.set_alpha(100)
            display.blit(info_surface, (0, 0))

            v_offset = 4
            bar_h_offset = 100
            bar_width = 106

            for item in self._info_text:
                if v_offset + 18 > self.dim[1]:
                    break

                if isinstance(item, list):
                    if len(item) > 1:
                        points = [(x + 8, v_offset + 8 + (1.0 - y) * 30) for x, y in enumerate(item)]
                        pygame.draw.lines(display, (255, 136, 0), False, points, 2)
                    item = None
                    v_offset += 18

                elif isinstance(item, tuple):
                    if isinstance(item[1], bool):
                        rect = pygame.Rect((bar_h_offset, v_offset + 8), (6, 6))
                        pygame.draw.rect(display, (255, 255, 255), rect, 0 if item[1] else 1)
                    else:
                        rect_border = pygame.Rect((bar_h_offset, v_offset + 8), (bar_width, 6))
                        pygame.draw.rect(display, (255, 255, 255), rect_border, 1)
                        f = (item[1] - item[2]) / (item[3] - item[2])
                        if item[2] < 0.0:
                            rect = pygame.Rect((bar_h_offset + f * (bar_width - 6), v_offset + 8), (6, 6))
                        else:
                            rect = pygame.Rect((bar_h_offset, v_offset + 8), (f * bar_width, 6))
                        pygame.draw.rect(display, (255, 255, 255), rect)
                    item = item[0]

                if item:  # At this point has to be a str.
                    surface = self._font_mono.render(item, True, (255, 255, 255))
                    display.blit(surface, (8, v_offset))
                v_offset += 18

        self._notifications.render(display)
        self.help.render(display)

# ==============================================================================
# -- FadingText ----------------------------------------------------------------
# ==============================================================================


class FadingText(object):
    def __init__(self, font, dim, pos):
        self.font = font
        self.dim = dim
        self.pos = pos
        self.seconds_left = 0
        self.surface = pygame.Surface(self.dim)

    def set_text(self, text, color=(255, 255, 255), seconds=2.0):
        text_texture = self.font.render(text, True, color)
        self.surface = pygame.Surface(self.dim)
        self.seconds_left = seconds
        self.surface.fill((0, 0, 0, 0))
        self.surface.blit(text_texture, (10, 11))

    def tick(self, _, clock):
        delta_seconds = 1e-3 * clock.get_time()
        self.seconds_left = max(0.0, self.seconds_left - delta_seconds)
        self.surface.set_alpha(500.0 * self.seconds_left)

    def render(self, display):
        display.blit(self.surface, self.pos)


# ==============================================================================
# -- HelpText ------------------------------------------------------------------
# ==============================================================================


class HelpText(object):
    """Helper class to handle text output using pygame"""
    def __init__(self, font, width, height):
        lines = __doc__.split('\n')
        self.font = font
        self.line_space = 18
        self.dim = (780, len(lines) * self.line_space + 12)
        self.pos = (0.5 * width - 0.5 * self.dim[0], 0.5 * height - 0.5 * self.dim[1])
        self.seconds_left = 0
        self.surface = pygame.Surface(self.dim)
        self.surface.fill((0, 0, 0, 0))
        for n, line in enumerate(lines):
            text_texture = self.font.render(line, True, (255, 255, 255))
            self.surface.blit(text_texture, (22, n * self.line_space))
            self._render = False
        self.surface.set_alpha(220)

    def toggle(self):
        self._render = not self._render

    def render(self, display):
        if self._render:
            display.blit(self.surface, self.pos)


# ==============================================================================
# -- PointsDrawner   -----------------------------------------------------------
# ==============================================================================

class PointsDrawner(object):
    def __init__(self, dim, pos, color = None, radius = None, auto_flush = True, max_value = None):
        self.dim = dim
        self.pos = pos
        self.surface = pygame.Surface(self.dim, pygame.SRCALPHA)

        if color is None:
            color = Defaults.circleColor

        if radius is None:
            radius = Defaults.circleRadius

        if max_value is None:
            max_value = Defaults.maxRenderingValue        

        self.color = color
        self.radius = radius
        self.auto_flush = auto_flush
        self.max_value = max_value

    def setPoints(self, points2d, color = None, radius = None):

        if color is None:
            color = self.color

        if radius is None:
            radius = self.radius

        self.surface = pygame.Surface(self.dim, pygame.SRCALPHA)

        i = 0
        while i < self.max_value and i < len(points2d):
            if len(points2d[i]) >= 2:
                if points2d[i][0] < self.dim[0] and points2d[i][1] < self.dim[1]:
                    if points2d[i][0] >= 0 and points2d[i][1] >= 0:
                        try:
                            pygame.draw.circle(self.surface, color, (int(points2d[i][0]), int(points2d[i][1])), radius)
                        except:
                            print(points2d[i])
            i+=1

    def render(self, display):
        display.blit(self.surface, self.pos)
        
        if self.auto_flush:
            self.surface = pygame.Surface(self.dim, pygame.SRCALPHA)

# ==============================================================================
# -- LineDrawner   -------------------------------------------------------------
# ==============================================================================

class LineDrawner(object):
    def __init__(self, dim, pos, color = None, tickness = None, auto_flush = True, max_value = None):
        self.dim = dim
        self.pos = pos
        self.surface = pygame.Surface(self.dim, pygame.SRCALPHA)
        
        if color is None:
            color = Defaults.lineColor

        if tickness is None:
            tickness = Defaults.lineTickness

        if max_value is None:
            max_value = Defaults.maxRenderingValue

        self.color = color
        self.tickness = tickness
        self.auto_flush = auto_flush
        self.max_value = max_value

    def setPoints(self, points2d_1, points2d_2, color = None, tickness = None):

        if color is None:
            color = self.color

        if tickness is None:
            tickness = self.tickness

        self.surface = pygame.Surface(self.dim, pygame.SRCALPHA)

        i = 0
        while i < self.max_value and i < len(points2d_1) and i < len(points2d_2):
            if points2d_1[i][0] < self.dim[0] and points2d_1[i][1] < self.dim[1] and points2d_2[i][0] < self.dim[0] and points2d_2[i][1] < self.dim[1]:
                if points2d_1[i][0] >=0 and points2d_1[i][1] >=0 and points2d_2[i][0] >=0 and points2d_2[i][1] >=0:
                    pygame.draw.line(self.surface, color, (int(points2d_1[i][0]), int(points2d_1[i][1])), (int(points2d_2[i][0]), int(points2d_2[i][1])), tickness)
            i+=1

    def render(self, display):
        display.blit(self.surface, self.pos)

        if self.auto_flush:
            self.surface = pygame.Surface(self.dim, pygame.SRCALPHA)

# ==============================================================================
# -- RectDrawner   -------------------------------------------------------------
# ==============================================================================

class RectDrawner(object):
    def __init__(self, dim, pos, color = None, tickness = None, auto_flush = True, max_value = None):
        self.dim = dim
        self.pos = pos
        self.surface = pygame.Surface(self.dim, pygame.SRCALPHA)
        
        if color is None:
            color = Defaults.lineColor

        if tickness is None:
            tickness = Defaults.lineTickness

        if max_value is None:
            max_value = Defaults.maxRenderingValue

        self.color = color
        self.tickness = tickness
        self.auto_flush = auto_flush
        self.max_value = max_value

    def setPoints(self, points2d_1, points2d_2, color = None, tickness = None):

        if color is None:
            color = self.color

        if tickness is None:
            tickness = self.tickness

        self.surface = pygame.Surface(self.dim, pygame.SRCALPHA)

        pygame.draw.line(self.surface, color, (int(points2d_1[0]), int(points2d_1[1])), (int(points2d_1[0]), int(points2d_2[1])), tickness)
        pygame.draw.line(self.surface, color, (int(points2d_1[0]), int(points2d_1[1])), (int(points2d_2[0]), int(points2d_1[1])), tickness)
        pygame.draw.line(self.surface, color, (int(points2d_2[0]), int(points2d_1[1])), (int(points2d_2[0]), int(points2d_2[1])), tickness)
        pygame.draw.line(self.surface, color, (int(points2d_1[0]), int(points2d_2[1])), (int(points2d_2[0]), int(points2d_2[1])), tickness)

    def render(self, display):
        display.blit(self.surface, self.pos)

        if self.auto_flush:
            self.surface = pygame.Surface(self.dim, pygame.SRCALPHA)

# ==============================================================================
# -- ImageDrawner   ------------------------------------------------------------
# ==============================================================================

class ImageDrawner(object):
    def __init__(self, dim, pos):
        self.dim = dim
        self.pos = pos
        self.surface = pygame.Surface(self.dim)
        
    def setImage(self, rgbImage):
        self.surface = pygame.surfarray.make_surface(rgbImage.swapaxes(0, 1)) if rgbImage is not None else None

    def render(self, display):
        if self.surface is not None:
            display.blit(self.surface, self.pos)

