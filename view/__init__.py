import math

import pygame as pg
from pygame import Rect, Surface

from items import Dynamic


class CharacterView:
    def __init__(self, window_width: int, window_height: int) -> None:
        self.__window_width = window_width
        self.__window_height = window_height
        # self.__screen = Surface((window_width, window_height))

    def get_view(self, target_surface: Surface, character: Dynamic) -> Surface:
        s = max(self.__window_width, self.__window_height)
        r = s / math.cos(math.pi / 4)
        ch_rect = character.rect
        x = ch_rect.x + ch_rect.width / 2
        y = ch_rect.y + ch_rect.height / 2

        R1 = Rect(
            x - r,
            y - r,
            2 * r,
            2 * r
        )

        alpha = math.degrees(character.orientation_rad)

        target_rect = target_surface.get_rect()

        crop = target_surface.subsurface(R1.clip(target_rect)).copy()
        # crop.set_alpha(100)

        view = Surface((R1.width, R1.height))
        img_x = 0 if R1.left > 0 else -R1.left
        img_y = 0 if R1.top > 0 else -R1.top

        view.blit(crop, (img_x, img_y))

        view = pg.transform.rotate(view, 90 - alpha)

        R1 = view.get_rect()

        R2 = Rect(
            (R1.width - self.__window_width) / 2,
            R1.height / 2 - self.__window_height + ch_rect.height,
            self.__window_width,
            self.__window_height
        )

        return view.subsurface(R2).copy()

    @property
    def screen(self) -> Surface:
        return self.__screen
