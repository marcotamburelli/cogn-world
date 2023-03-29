from typing import Tuple

import pygame as pg
from pygame import Rect, Surface

from items import Dynamic, Static, extract_frames
from util import Grid, ItemType


def build_main_character(
        id: str,
        x: int,
        y: int,
        frame_size: Tuple[int, int],
        frame_img_path: str
) -> Dynamic:
    return Dynamic(
        id=id,
        item_type=ItemType.character,
        x=x,
        y=y,
        frames=extract_frames(frame_img_path, frame_size=frame_size)
    )


def build_monster(
        id: str,
        x: int,
        y: int,
        frame_size: Tuple[int, int],
        frame_img_path: str
) -> Dynamic:
    return Dynamic(
        id=id,
        item_type=ItemType.monster,
        x=x,
        y=y,
        frames=extract_frames(frame_img_path, frame_size=frame_size)
    )


def build_wall(
        id: str,
        x: int,
        y: int,
        frame_img_path: str
) -> Static:
    return Static(
        id=id,
        item_type=ItemType.wall,
        x=x,
        y=y,
        image=pg.image.load(frame_img_path).convert_alpha()
    )


def build_consumable(
        id: str,
        x: int,
        y: int,
        value: int,
        frame_img_path: str
) -> Static:
    return Static(
        id=id,
        item_type=ItemType.bonus if value > 0 else ItemType.malus,
        x=x,
        y=y,
        image=pg.image.load(frame_img_path).convert_alpha(),
        value=value * (1 if value > 0 else -1)
    )


class Provider:
    def __init__(self, def_file: str) -> None:
        import yaml

        with open(def_file, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        self.__cell_width: int = data['cell_width']
        self.__cell_height: int = data['cell_height']

        map_str: str = data['map']

        rows = map_str.splitlines()

        self.__grid_width = max([len(row) for row in rows])
        self.__grid_height = len(rows)

        self.__grid = Grid(
            cell_size=(self.__cell_width, self.__cell_height),
            grid_size=(self.__grid_width, self.__grid_height)
        )
        window_width = self.__cell_width * self.__grid_width
        window_height = self.__cell_height * self.__grid_height

        self.__game_area = Surface((window_width, window_height))

        self.__static_sprites = pg.sprite.Group()
        self.__interactive_sprites = pg.sprite.Group()
        self.__dynamic_sprites = pg.sprite.Group()
        self.__main_sprites = pg.sprite.Group()

        for j in range(len(rows)):
            row = rows[j]
            for i in range(len(row)):
                if row[i] == 'W':
                    wall = build_wall(
                        id=f'wall-{i}-{j}',
                        x=(i + .5) * self.__cell_width,
                        y=(j + .5) * self.__cell_height,
                        frame_img_path='images/wall.png'
                    )

                    self.__grid.insert_item(wall)
                    self.__static_sprites.add(wall)

                if row[i] == 'S':
                    stone = build_wall(
                        id=f'stone-{i}-{j}',
                        x=(i + .5) * self.__cell_width,
                        y=(j + .5) * self.__cell_height,
                        frame_img_path='images/medium_stone.png'
                    )

                    self.__grid.insert_item(stone)
                    self.__static_sprites.add(stone)

                if row[i] == 'a':
                    self.insert_apple(i, j)

                if row[i] == 'b':
                    self.insert_bad_apple(i, j)

                if row[i] == 'c':
                    self.__main_character = build_main_character(
                        id=f'main_character-{i}-{j}',
                        x=(i + .5) * self.__cell_width,
                        y=(j + .5) * self.__cell_height,
                        frame_size=(32, 32),
                        frame_img_path='images/man.png'
                    )

                    self.__grid.insert_item(self.__main_character)
                    self.__main_sprites.add(self.__main_character)

                if row[i] == 'm':
                    monster = build_monster(
                        id=f'monster-{i}-{j}',
                        x=(i + .5) * self.__cell_width,
                        y=(j + .5) * self.__cell_height,
                        frame_size=(56, 56),
                        frame_img_path='images/monster.png'
                    )
                    monster.item_status['value'] = 7

                    self.__grid.insert_item(monster)
                    self.__dynamic_sprites.add(monster)

    def insert_bad_apple(self, i: int, j: int):
        apple = build_consumable(
            id=f'bad-apple-{i}-{j}',
            x=(i + .5) * self.__cell_width,
            y=(j + .5) * self.__cell_height,
            frame_img_path='images/bad_apple.png',
            value=-5
        )

        self.__grid.insert_item(apple)
        self.__interactive_sprites.add(apple)

    def insert_apple(self,  i: int, j: int):
        apple = build_consumable(
            id=f'apple-{i}-{j}',
            x=(i + .5) * self.__cell_width,
            y=(j + .5) * self.__cell_height,
            frame_img_path='images/apple.png',
            value=10
        )

        self.__grid.insert_item(apple)
        self.__interactive_sprites.add(apple)

    @property
    def grid_width(self):
        return self.__grid_width

    @property
    def grid_height(self):
        return self.__grid_height

    @property
    def game_area(self) -> pg.Surface:
        return self.__game_area

    @property
    def grid(self) -> Grid:
        return self.__grid

    @property
    def main_character(self) -> Dynamic:
        return self.__main_character

    @property
    def static_sprites(self) -> pg.sprite.Group:
        return self.__static_sprites

    @property
    def interactive_sprites(self) -> pg.sprite.Group:
        return self.__interactive_sprites

    @property
    def dynamic_sprites(self) -> pg.sprite.Group:
        return self.__dynamic_sprites

    @property
    def main_sprites(self) -> pg.sprite.Group:
        return self.__main_sprites
