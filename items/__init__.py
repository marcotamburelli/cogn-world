import math
from typing import Callable, Dict, List, Tuple, TypedDict

import pygame as pg
from pygame import Rect, Surface

from util import Grid, Item, ItemStatus, ItemType

from .actions import Action, ActionParams, ActionType, Orientation


class Frames(TypedDict):
    standing_images: List[Surface]
    moving_images: List[List[Surface]]


def extract_frames(file: str, frame_size: Tuple[int, int]) -> Frames:
    # Load image containing frames
    sprite_sheet = pg.image.load(file).convert_alpha()

    # Define the dimension of each frame
    frame_width = frame_size[0]
    frame_height = frame_size[1]

    def get_surface(x, y):
        frame_rect = Rect(x, y, frame_width, frame_height)
        return sprite_sheet.subsurface(frame_rect)

    orientation_no = len(Orientation)

    standing_images = [
        get_surface(0, y * frame_height) for y in range(0, orientation_no)
    ]

    frame_no = int(sprite_sheet.get_rect().width / frame_width)

    moving_images = [
        [
            get_surface(x * frame_width, (orientation_no + d.value) * frame_height) for x in range(frame_no)
        ] for d in Orientation
    ]

    return Frames(standing_images=standing_images, moving_images=moving_images)


class Dynamic(Item):
    def __init__(
        self,
        id: str,
        item_type: ItemType,
        x: int,
        y: int,
        frames: Frames
    ):
        super().__init__()

        self.__id = id
        self.__item_type = item_type
        self.images: List[List[Surface]] = []

        self.__frames = frames
        self.__orientation = Orientation.down
        self.__alpha = self.__orientation.radiants()
        self.__current_action = Action(
            action_type=ActionType.stand,
            params=ActionParams(rotation=self.__alpha)
        )

        self.__image_idx = 0
        self.__rect = self.image.get_rect()
        self.__rect.x = x - self.__rect.width / 2
        self.__rect.y = y - self.__rect.height / 2

        self.__item_status: ItemStatus = {'score': 0, 'removed': False}
        self.collision_rules: Dict[
            ItemType, Callable[[Item, Item, int], bool]
        ] = {}

    def __stand(self):
        self.__image_idx = 0

    def __orient(self, alpha: float):
        self.__alpha += alpha

        while self.__alpha < 0:
            self.__alpha = 2 * math.pi + self.__alpha

        while self.__alpha > 2 * math.pi:
            self.__alpha = self.__alpha - 2 * math.pi

        self.__orientation = Orientation.get_orientation(self.__alpha)

    def __move(self, dx: float, dy: float, frame_step: int):
        # It's assumed that the frame number is the same for each orientation
        frames_number = len(self.__frames['moving_images'][0])
        self.__image_idx = (self.__image_idx + frame_step) % frames_number

        self.__rect = self.__rect.move(dx, dy)

    def __can_move(
            self,
            dx: float,
            dy: float,
            area: Rect,
            grid: Grid
    ) -> bool:
        try_rect = self.__rect.move(dx, dy)

        if not area.contains(try_rect):
            return False

        for item in grid.items_in_area(try_rect):
            if item.id == self.__id or item.item_type is not ItemType.wall:
                continue

            if try_rect.colliderect(item.rect):
                return False

        return True

    def act(self, dt: float, area: Rect, grid: Grid):
        if self.__current_action is None:
            return

        action_type = self.__current_action['action_type']
        action_params = self.__current_action['params']

        if action_type is ActionType.stand:
            self.__stand()

        elif action_type is ActionType.rotate:
            a_speed = action_params['angular_speed']
            alpha = dt * a_speed
            self.__orient(alpha)

        elif action_type is ActionType.move or action_type is ActionType.hunt:
            l_speed = action_params['linear_speed']
            ds = dt * l_speed
            dx = ds * math.cos(self.__alpha)
            dy = - ds * math.sin(self.__alpha)

            if self.__can_move(dx, dy, area, grid):
                grid.remove_item(self)
                self.__move(dx=dx, dy=dy, frame_step=1 if l_speed > 0 else -1)
                grid.insert_item(self)

            else:
                self.__current_action = Action(
                    action_type=ActionType.stand,
                    params={}
                )

    def __match_rule(self, item: Item, current_timestamp: int) -> bool:
        if self.id == item.id or not self.__rect.colliderect(item.rect):
            return False

        if item.item_type in self.collision_rules:
            return self.collision_rules[item.item_type](self, item, current_timestamp)

        return False

    def act_collisions(self, grid: Grid, current_timestamp: int) -> List[Item]:
        items = grid.items_in_area(self.__rect)

        return [item for item in items if self.__match_rule(item, current_timestamp)]

    @property
    def action(self) -> Action:
        return self.__current_action

    def start_action(self, a: Action, current_timestamp: int, force: bool = False) -> bool:
        if 'start_timestamp' in self.__current_action \
                and 'start_timestamp' in self.__current_action:
            current_a_start = self.__current_action['start_timestamp']
            current_a_duration = self.__current_action['duration_millis'] or 0

            can_replace = current_timestamp - current_a_start >= current_a_duration or force
        else:
            can_replace = True

        if can_replace:
            self.__current_action = a.copy()

    @property
    def rect(self) -> Rect:
        return Rect(
            self.__rect.left,
            self.__rect.top,
            self.__rect.width,
            self.__rect.height
        )

    @property
    def orientation_rad(self) -> float:
        return self.__alpha

    @property
    def image(self) -> Surface:
        if self.__current_action['action_type'] is ActionType.move \
                or self.__current_action['action_type'] is ActionType.hunt:
            return self.__frames['moving_images'][self.__orientation.value][self.__image_idx]
        else:
            return self.__frames['standing_images'][self.__orientation.value]

    @property
    def id(self) -> str:
        return self.__id

    @property
    def item_type(self) -> ItemType:
        return self.__item_type

    @property
    def item_status(self) -> ItemStatus:
        return self.__item_status

    @item_status.setter
    def item_status(self, s: ItemStatus):
        self.__item_status = s


class Static(Item):
    def __init__(
        self,
        id: str,
        item_type: ItemType,
        x: int,
        y: int,
        image: Surface,
        value: int = 10
    ):
        super().__init__()

        self.__id = id
        self.__item_type = item_type
        self.images: List[List[Surface]] = []

        self.__image = image
        self.__rect = self.image.get_rect()
        self.__rect.x = x - self.__rect.width / 2
        self.__rect.y = y - self.__rect.height / 2

        self.__item_status: ItemStatus = {'value': value, 'removed': False}

    @property
    def rect(self) -> Rect:
        return Rect(
            self.__rect.left,
            self.__rect.top,
            self.__rect.width,
            self.__rect.height
        )

    @property
    def image(self) -> Surface:
        return self.__image

    @property
    def id(self) -> str:
        return self.__id

    @property
    def item_type(self) -> ItemType:
        return self.__item_type

    @property
    def item_status(self) -> ItemStatus:
        return self.__item_status

    @item_status.setter
    def item_status(self, s: ItemStatus):
        self.__item_status = s
