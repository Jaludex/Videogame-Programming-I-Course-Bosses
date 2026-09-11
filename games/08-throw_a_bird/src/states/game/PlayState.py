"""
ISPPV1 2023
Study Case: Throw a Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState, ported from main.script: the
whole per-frame update/input loop -- aiming, panning, flinging the bird,
camera follow-and-zoom, and idle-detection to reset the bird back to the
slingshot once a shot has settled.

Deviation from the Lua source: main.script disables the parrot's
collisionobject at rest and re-enables it only once flung, so gravity
and everything else leaves it alone until it is thrown.
gale.physics.Body has no enable/disable toggle for an existing fixture,
so instead the bird is held in place by brute force every frame it is
neither being aimed nor already in flight (_hold_bird_at_rest): its
position/velocity are pinned back to the slingshot each update(), which
cancels out whatever one frame of gravity would have done. The bird
remains a normal dynamic body throughout (nothing in the level ever
reaches the slingshot's position anyway), it is just re-pinned faster
than it can visibly fall.
"""

import math

import pygame

from gale.camera import Camera
from gale.input_handler import InputData
from gale.physics.world import World
from gale.state import BaseState
from gale.text import render_text

import settings
from src.entity.Bird import Bird
from src.world.Level import Level

# How close (world pixels) a press has to land to the bird to start
# aiming instead of panning the camera.
AIM_GRAB_RADIUS = 50

# The pull-back vector is clamped to this length (world pixels) both
# while aiming (how far the bird can be dragged back) and when computing
# the launch impulse on release.
MAX_PULL_DISTANCE = 150

# Scales the (clamped) pull-back vector into a launch impulse. Not a
# port of the original's `950` (a force applied for a single Defold
# physics step, at Defold's own physics.scale) -- chosen instead, by
# testing actual throws, so a full pull-back (MAX_PULL_DISTANCE) launches
# the bird fast enough to comfortably clear the gap and reach the tower
# under gale's default gravity, factoring in the energy the bird's own
# high friction/low restitution shed on its first bounce.
#
# This is the only tuning number that matters here, regardless of the
# bird's mass: gale.physics.Body.apply_impulse(ix, iy) divides by
# pixels_per_meter before hand it to Box2D, and Box2D's resulting
# delta-v is impulse / mass -- so passing an impulse of
# `pull * FLING_IMPULSE_SCALE * mass` (mirroring the Lua source's own
# `direction * 950 * parrot_mass`, force proportional to mass) makes
# mass cancel out of the result: launch speed is just
# `pull * FLING_IMPULSE_SCALE`.
#
# 10.5 (barely cleared the gap) was bumped to 16.0 (comfortably punched
# into the tower) per feedback that throws felt too weak -- then walked
# back to the average of the two, 13.25, per feedback that 16.0 then felt
# too strong.
FLING_IMPULSE_SCALE = 13.25

# A shot is considered "settled" once the bird's linear/angular velocity
# has been below these thresholds for IDLE_FRAMES_LIMIT consecutive
# frames (~1.6s at 60fps) -- ported from main.script, retuned for gale's
# pixel/physics scale (angular velocity here is radians/second, not
# Defold's units).
IDLE_LINEAR_SPEED_THRESHOLD = 30
IDLE_ANGULAR_SPEED_THRESHOLD = 0.3
IDLE_FRAMES_LIMIT = 100

CAMERA_FOLLOW_RATE = 6.0
CAMERA_ZOOM_LERP_RATE = 3.0
CAMERA_ZOOM_MIN = 1.0
CAMERA_ZOOM_MAX = 1.5
CAMERA_PAN_MARGIN = 300

HUD_TEXT = "Drag the bird to aim and release to fling. Drag elsewhere to pan."


class PlayState(BaseState):
    def enter(self) -> None:
        self.world = World(gravity=settings.GRAVITY)

        self.level = Level(self.world)
        self.bird = Bird(self.world, self.level.bird_start.x, self.level.bird_start.y)

        self.camera = Camera(settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
        self.camera.x, self.camera.y = self.bird.position
        self.camera_target = pygame.Vector2(self.camera.x, self.camera.y)
        self.camera.follow(self.camera_target, rate=CAMERA_FOLLOW_RATE)
        # Mirrors main.script's self.camera_zoom (ranges 1..1.5, bigger
        # means "farther away"); gale's own Camera.zoom is the inverse
        # (bigger means "closer"), so it is always set to 1/this ratio.
        self.camera_zoom_ratio = 1.0
        self.camera.zoom = 1.0

        self.aiming = False
        self.panning = False
        self.flinging = False
        self.idle_frames = 0

        self.pressed_position = pygame.Vector2()
        self.pressed_camera_target = pygame.Vector2()
        self.aim_offset = pygame.Vector2()

    def fixed_update(self) -> None:
        # Driven by gale.game.Game's own accumulator (added in gale
        # 1.10.0) instead of calling self.world.update(dt) here, which
        # would otherwise run a second, redundant accumulator on top of
        # World's own.
        self.world.fixed_update()
        self.level.fixed_update()

    def update(self, dt: float) -> None:
        self.level.update(dt)

        if self.level.all_enemies_defeated:
            self.state_machine.change("victory")
            return

        if self.flinging:
            self.camera_target.update(self.bird.position)
            self._update_idle()
        elif self.aiming:
            self._hold_bird_while_aiming()
        else:
            self._hold_bird_at_rest()

        self._update_zoom(dt)
        self.camera.update(dt)

    def _hold_bird_at_rest(self) -> None:
        self.bird.reset()

    def _hold_bird_while_aiming(self) -> None:
        # world.update(dt) above still steps gravity on the bird every
        # frame regardless of aiming state (gale.physics.Body has no
        # enable/disable toggle -- see the module docstring), and
        # _on_touch_motion only fires on mouse-motion *events*, not every
        # frame. Without re-pinning here too, any frame with no fresh
        # motion event lets gravity accumulate velocity that then snaps
        # the bird around erratically the moment position gets set again.
        # Re-applying the held offset and zeroing velocity every frame
        # keeps the bird glued to the mouse the whole time it is aiming.
        self.bird.body.position = self.bird.initial_position - self.aim_offset
        self.bird.body.velocity = (0, 0)
        self.bird.body.angular_velocity = 0.0

    def _update_idle(self) -> None:
        linear_speed = self.bird.body.velocity.length()
        angular_speed = abs(self.bird.body.angular_velocity)

        if (
            linear_speed < IDLE_LINEAR_SPEED_THRESHOLD
            and angular_speed < IDLE_ANGULAR_SPEED_THRESHOLD
        ):
            self.idle_frames += 1

            if self.idle_frames > IDLE_FRAMES_LIMIT:
                self.flinging = False
                self.idle_frames = 0
                self.bird.reset()
                self.camera_target.update(self.bird.position)
        else:
            self.idle_frames = 0

    def _update_zoom(self, dt: float) -> None:
        distance = abs(self.bird.position.x - self.bird.initial_position.x)
        reach = max(1.0, self.bird.initial_position.x)
        target_ratio = max(
            CAMERA_ZOOM_MIN, min(CAMERA_ZOOM_MAX, math.sqrt(distance / reach))
        )
        factor = 1.0 - math.exp(-CAMERA_ZOOM_LERP_RATE * dt)
        self.camera_zoom_ratio += (target_ratio - self.camera_zoom_ratio) * factor
        self.camera.zoom = 1.0 / self.camera_zoom_ratio

    def render(self, surface: pygame.Surface) -> None:
        surface.fill(settings.BG_COLOR)
        self.level.render(surface, self.camera)
        self.bird.render(surface, self.camera)

        if self.aiming:
            self._render_pull_line(surface)

        render_text(surface, HUD_TEXT, settings.FONTS["small"], 10, 10, (70, 55, 40))

    def _render_pull_line(self, surface: pygame.Surface) -> None:
        start = self.camera.world_to_screen(self.bird.initial_position)
        end = self.camera.world_to_screen(self.bird.position)
        pygame.draw.line(surface, (110, 75, 40), start, end, 3)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "touch":
            self._on_touch(input_data)
        elif input_id == "touch_motion":
            self._on_touch_motion(input_data)

    def _mouse_to_virtual(self, position) -> pygame.Vector2:
        scale_x = settings.VIRTUAL_WIDTH / settings.WINDOW_WIDTH
        scale_y = settings.VIRTUAL_HEIGHT / settings.WINDOW_HEIGHT
        return pygame.Vector2(position[0] * scale_x, position[1] * scale_y)

    def _on_touch(self, input_data: InputData) -> None:
        position = self._mouse_to_virtual(input_data.position)

        if input_data.pressed:
            self.pressed_position = position
            world_position = pygame.Vector2(self.camera.screen_to_world(position))

            if (
                not self.flinging
                and (world_position - self.bird.position).length() < AIM_GRAB_RADIUS
            ):
                self.aiming = True
                self.aim_offset = pygame.Vector2()
            else:
                self.panning = True
                self.pressed_camera_target = pygame.Vector2(self.camera_target)
        elif input_data.released:
            if self.aiming:
                self._fling()

            self.aiming = False
            self.panning = False

    def _fling(self) -> None:
        pull = self.bird.initial_position - self.bird.position
        if pull.length() < 5:
            self.bird.reset()
            return
        # Scaled by the bird's own mass so it cancels out of the
        # resulting delta-v -- see the FLING_IMPULSE_SCALE docstring.
        scale = FLING_IMPULSE_SCALE * self.bird.mass
        self.bird.body.apply_impulse(pull.x * scale, pull.y * scale)
        self.flinging = True
        self.idle_frames = 0

    def _on_touch_motion(self, input_data: InputData) -> None:
        if not (self.aiming or self.panning):
            return

        position = self._mouse_to_virtual(input_data.position)
        # Screen-space delta since the press, converted to world units by
        # dividing out the camera's current zoom.
        screen_delta = self.pressed_position - position
        world_delta = screen_delta / self.camera.zoom

        if self.aiming:
            if world_delta.length() > MAX_PULL_DISTANCE:
                world_delta.scale_to_length(MAX_PULL_DISTANCE)

            # Just remember the offset; update()'s _hold_bird_while_aiming
            # re-applies it (and zeroes velocity) every frame, not only on
            # the frames a motion event happens to arrive.
            self.aim_offset = world_delta
        elif self.panning:
            target = self.pressed_camera_target + world_delta
            left, right = self.level.ground_x_range
            target.x = max(
                left - CAMERA_PAN_MARGIN, min(right + CAMERA_PAN_MARGIN, target.x)
            )
            self.camera_target.update(target)
