import pygame as pg

from util import Item, ItemType

from . import Dynamic
from .actions import ActionType


def __consume_bonus_item(self: Dynamic, item: Item, _: int) -> bool:
    if self.action['action_type'] is not ActionType.pick:
        return False

    current_score = self.item_status['score']
    current_score += item.item_status['value']

    self.item_status['score'] = current_score

    item.item_status['removed'] = True

    return True


def __consume_malus_item(self: Dynamic, item: Item, _: int) -> bool:
    if self.action['action_type'] is not ActionType.pick:
        return False

    current_score = self.item_status['score']
    current_score -= item.item_status['value']

    self.item_status['score'] = current_score

    item.item_status['removed'] = True

    return True


def __get_bite(self: Dynamic, item: Dynamic, _: int):
    a = item.action
    at = a['action_type']

    if at is ActionType.hunt:
        current_score = self.item_status['score']
        current_score -= item.item_status['value']

        self.item_status['score'] = current_score


MAIN_CHAR_COLLISION = {
    ItemType.bonus: __consume_bonus_item,
    ItemType.malus: __consume_malus_item,
    ItemType.monster: __get_bite
}


def __eat_item(self: Dynamic, item: Item, _: int) -> bool:
    item.item_status['removed'] = True

    return True


def __bite(self: Dynamic, _: Dynamic, current_timestamp: int):
    a = self.action
    at = a['action_type']

    if at is ActionType.hunt:
        self.start_action(
            a={
                **a,
                'action_type': ActionType.move,
                'start_timestamp': current_timestamp,
                'duration_millis': 1000
            },
            current_timestamp=current_timestamp,
            force=True
        )


MONSTER_COLLISION = {
    ItemType.bonus: __eat_item,
    ItemType.malus: __eat_item,
    ItemType.character: __bite
}
