from enum import Enum
from typing import Dict, List, TypedDict, Tuple

from pygame import Rect, Surface
from pygame.sprite import Sprite


class ItemType(Enum):
    character = 0
    monster = 1
    wall = 2
    bonus = 3
    malus = 4


class ItemStatus(TypedDict, total=False):
    score: int
    value: int
    removed: bool


class Item(Sprite):
    @property
    def rect(self) -> Rect:
        raise NotImplementedError(
            '"rect" property must be implemented in subclasses')

    @property
    def image(self) -> Surface:
        raise NotImplementedError(
            '"image" property must be implemented in subclasses')

    @property
    def id(self) -> str:
        raise NotImplementedError(
            '"id" property must be implemented in subclasses')

    @property
    def item_type(self) -> ItemType:
        raise NotImplementedError(
            '"item_type" property must be implemented in subclasses')

    @property
    def item_status(self) -> ItemStatus:
        raise NotImplementedError(
            '"item_status" property must be implemented in subclasses')

    @item_status.setter
    def item_status(self, s: ItemStatus):
        raise NotImplementedError(
            '"item_status" property must be implemented in subclasses')


class Grid:
    def __init__(self, cell_size: Tuple[int, int], grid_size: Tuple[int, int]) -> None:
        self.__area = cell_size[0] * grid_size[0],  cell_size[1] * grid_size[1]

        self.__cell_size = cell_size

        # sprites aligned with the border could result in "list index out of range"
        # hence foro safety reason the grid is increased by 1 unit for both x and y.
        x = range(grid_size[0] + 1)
        y = range(grid_size[1] + 1)
        self.__grid: List[List[Dict[str, Item]]] = [[{} for _ in y] for _ in x]

    def __get_grid_rect(self, rect: Rect):
        x0 = rect.x // self.__cell_size[0]
        y0 = rect.y // self.__cell_size[1]
        x1 = (rect.x + rect.width) // self.__cell_size[0]
        y1 = (rect.y + rect.height) // self.__cell_size[1]

        return x0, y0, x1, y1

    @property
    def area(self) -> Tuple[int, int]:
        return self.__area

    def insert_items(self, *args: Item):
        for i in args:
            self.insert_item(i)

    def insert_item(self, item: Item):
        x0, y0, x1, y1 = self.__get_grid_rect(item.rect)

        for i in range(x0, x1+1):
            for j in range(y0, y1 + 1):
                self.__grid[i][j][item.id] = item

    def remove_item(self, item: Item):
        x0, y0, x1, y1 = self.__get_grid_rect(item.rect)
        id = item.id

        for i in range(x0, x1+1):
            for j in range(y0, y1+1):
                cell = self.__grid[i][j]

                if id in cell:
                    del cell[id]

    def items_in_area(self, rect: Rect) -> List[Item]:
        x0, y0, x1, y1 = self.__get_grid_rect(rect)

        area_dict = {
            id: item for i in range(x0, x1 + 1) for j in range(y0, y1 + 1) for id, item in self.__grid[i][j].items()
        }

        return list(area_dict.values())
