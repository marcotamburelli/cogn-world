import math
import random
from enum import Enum
from typing import Optional, TypedDict

import pygame as pg


class Orientation(Enum):
    up = 0
    up_right = 1
    right = 2
    right_down = 3
    down = 4
    down_left = 5
    left = 6
    left_up = 7

    def radiants(self) -> float:
        alpha = math.pi * (2 - self.value) / 4

        if alpha < 0:
            return 2 * math.pi + alpha
        else:
            return alpha

    @classmethod
    def get_orientation(cls, alpha: float):
        val = round(2 - 4 * alpha / math.pi) % 8

        for member in cls:
            if member.value == val:
                return member

        raise ValueError(f"{val} is not a valid value for {cls.__name__}")


class ActionType(Enum):
    stand = 0
    rotate = 1
    move = 2
    pick = 3
    attack = 4
    hunt = 5


class ActionParams(TypedDict, total=False):
    angular_speed: float
    linear_speed: float


class Action(TypedDict, total=False):
    action_type: ActionType
    start_timestamp: int
    duration_millis: int
    params: ActionParams


def get_keyboard_action(linear_speed: float = 20, angular_speed: float = math.pi) -> Action:
    keys = pg.key.get_pressed()
    current_timestamp = pg.time.get_ticks()

    def get_rotation_action() -> Optional[Action]:
        if keys[pg.K_LEFT]:
            return Action(
                start_timestamp=current_timestamp,
                duration_millis=None,
                action_type=ActionType.rotate,
                params=ActionParams(angular_speed=angular_speed)
            )
        elif keys[pg.K_RIGHT]:
            return Action(
                start_timestamp=current_timestamp,
                duration_millis=None,
                action_type=ActionType.rotate,
                params=ActionParams(angular_speed=-angular_speed)
            )
        else:
            return None

    def get_motion_action() -> Optional[Action]:
        if keys[pg.K_UP]:
            return Action(
                start_timestamp=current_timestamp,
                duration_millis=None,
                action_type=ActionType.move,
                params=ActionParams(linear_speed=linear_speed)
            )
        elif keys[pg.K_DOWN]:
            return Action(
                start_timestamp=current_timestamp,
                duration_millis=None,
                action_type=ActionType.move,
                params=ActionParams(linear_speed=-linear_speed)
            )
        else:
            return None

    def get_static_action() -> Optional[Action]:
        if keys[pg.K_p]:
            return Action(
                start_timestamp=current_timestamp,
                duration_millis=None,
                action_type=ActionType.pick, params={}
            )
        else:
            return Action(
                start_timestamp=current_timestamp,
                duration_millis=None,
                action_type=ActionType.stand,
                params={}
            )

    return get_rotation_action() \
        or get_motion_action() \
        or get_static_action()


def get_random_action(linear_speed: float = 20, angular_speed: float = math.pi) -> Action:
    current_timestamp = pg.time.get_ticks()

    catalog = {
        1: Action(
            start_timestamp=current_timestamp,
            duration_millis=250,
            action_type=ActionType.rotate,
            params=ActionParams(angular_speed=angular_speed)
        ),
        2: Action(
            start_timestamp=current_timestamp,
            duration_millis=250,
            action_type=ActionType.rotate,
            params=ActionParams(angular_speed=-angular_speed)
        ),
        3:  Action(
            start_timestamp=current_timestamp,
            duration_millis=1000,
            action_type=ActionType.hunt,
            params=ActionParams(linear_speed=linear_speed)
        ),
        4:  Action(
            start_timestamp=current_timestamp,
            duration_millis=1000,
            action_type=ActionType.hunt,
            params=ActionParams(linear_speed=linear_speed)
        ),
        5: Action(
            start_timestamp=current_timestamp,
            duration_millis=1000,
            action_type=ActionType.move,
            params=ActionParams(linear_speed=-linear_speed)
        ),
        6: Action(
            start_timestamp=current_timestamp,
            duration_millis=1000,
            action_type=ActionType.move,
            params=ActionParams(linear_speed=-linear_speed)
        ),
        7: Action(
            start_timestamp=current_timestamp,
            duration_millis=500,
            action_type=ActionType.stand,
            params={}
        )
    }

    return catalog[random.randint(1, 7)]
