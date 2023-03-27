from typing import Dict, List, Tuple

import pygame as pg

from items import Dynamic
from items.actions import get_keyboard_action, get_random_action
from items.factory import Provider
from items.rules import MAIN_CHAR_COLLISION, MONSTER_COLLISION
from util import Item
from view import CharacterView

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class Game:
    def __init__(self, config: str) -> None:
        pg.init()

        self.__provider = Provider('config.yaml')

        self. __screen = self.__provider.screen
        self.__score_font = pg.font.Font(None, 36)

        self.__clock = pg.time.Clock()

        self.__main_char = self.__provider.main_character
        self.__main_char.collision_rules = MAIN_CHAR_COLLISION

        self.__char_view = CharacterView(100, 200)

        for monster in self.__get_monsters():
            monster.collision_rules = MONSTER_COLLISION

        self.__grid = self.__provider.grid

        self.__area = self.__screen.get_rect()

        self.__consumed: Dict[str, Tuple[int, Item]] = {}

    def run(self):
        running = True

        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

            # Calculating the time delta from last tick (in seconds)
            dt = self.__clock.get_time() / 1000.0

            current_timestamp = pg.time.get_ticks()

            self.set_main_char_action(dt, current_timestamp)
            self.__set_monsters_actions(dt, current_timestamp)

            self.__resolve_collisions(current_timestamp)

            self.__regenerate_interactive(current_timestamp, duration=10000)

            self.__update_sprites()

            self.__screen.fill(BLACK)

            self.__draw_score()

            self.__draw_sprites()

            view = self.__char_view.get_view(
                target_surface=self.__screen,
                character=self.__main_char
            )
            view.set_alpha(150)
            self.__screen.blit(view, (self.__area.width - 100, 0))

            pg.display.flip()

            # Limit the frame rate to 60 FPS
            self.__clock.tick(25)

        pg.quit()

    def __draw_sprites(self):
        self.__provider.interactive_sprites.draw(self.__screen)
        self.__provider.main_sprites.draw(self.__screen)
        self.__provider.dynamic_sprites.draw(self.__screen)
        self.__provider.static_sprites.draw(self.__screen)

    def __draw_score(self):
        score_text = f"Score: {self.__main_char.item_status['score']}"
        text_surface = self.__score_font.render(score_text, True, WHITE)
        text_surface.set_alpha(100)
        self.__screen.blit(text_surface, (3, 3))

    def __update_sprites(self):
        self.__provider.interactive_sprites.update()
        self.__provider.main_sprites.update()
        self.__provider.dynamic_sprites.update()
        self.__provider.static_sprites.update()

    def __resolve_collisions(self, current_timestamp: int):
        def resolve_collision(d: Dynamic):
            for i in d.act_collisions(self.__grid, current_timestamp):
                if i.item_status['removed']:
                    self.__grid.remove_item(i)
                    i.kill()
                    self.__consumed[i.id] = (current_timestamp, i)

        from itertools import chain

        for d in chain(self.__provider.main_sprites, self.__provider.dynamic_sprites):
            resolve_collision(d)

    def __regenerate_interactive(self, current_timestamp: int, duration: int):
        for (id, (t, i)) in list(self.__consumed.items()):
            if current_timestamp - t > duration:
                del self.__consumed[id]
                i.item_status['removed'] = False

                self.__provider.interactive_sprites.add(i)
                self.__grid.insert_item(i)

    def __set_monsters_actions(self, dt, current_timestamp: int):
        for monster in self.__get_monsters():
            a = get_random_action(linear_speed=75)

            monster.start_action(a, current_timestamp=current_timestamp)
            monster.act(dt=dt, area=self.__area, grid=self.__grid)

    def __get_monsters(self):
        dynamic_sprites: List[Dynamic] = self.__provider \
            .dynamic_sprites \
            .sprites()

        return dynamic_sprites

    def set_main_char_action(self, dt, current_timestamp: int):
        a = get_keyboard_action(linear_speed=100)

        self.__main_char.start_action(
            a,
            current_timestamp=current_timestamp
        )
        self.__main_char.act(dt=dt, area=self.__area, grid=self.__grid)


Game('config.yaml').run()
