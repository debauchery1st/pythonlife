from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.graphics.vertex_instructions import Ellipse
from kivy.graphics.context_instructions import Color
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window

from lifegrid import twenty_three, blank_grid

import os
import pickle

# import random


BOARDS = {"TWENTY_THREE": twenty_three, "BLANK": blank_grid()}


LIFE, DEATH = 1, 0


class Cell(object):
    surroundings = None
    moment = None
    state = None
    cell_x, cell_y = None, None

    def __init__(self, surroundings=None, pos=None, rules=None):
        self.surroundings = surroundings
        if not pos:
            # find the center of the board
            self.cell_x, self.cell_y = x, y = int(len(surroundings[0])/2), int(len(surroundings)/2)
        else:
            try:
                x, y = pos
                self.cell_x, self.cell_y = int(x), int(y)
            except Exception as e:
                raise e
        try:
            self.birth, self.survival = [int(x) for x in str(rules[0])], [int(x) for x in str(rules[1])]
        except IndexError as e:
            self.birth = [3,]
            self.survival = [2,3,]
        self.limit = len(self.surroundings[0]), len(self.surroundings)
        self.population, self.neighborhood = self.hood()
        self.moment = [[c for c in range(self.limit[1])] for r in range(self.limit[0])]

    def rules(self):
        # update the neighborhood statistics
        self.population, self.neighborhood = self.hood()
        if self.population in self.birth:
            return "BORN", LIFE
        if self.population in self.survival:
            return "CONTINUE", self.state
        return ("DIED", DEATH)

    def generate(self):
        msg, self.state = self.rules()
        return self.state

    def generation(self):
        y_range = range(len(self.surroundings))
        x_range = range(len(self.surroundings[0]))
        self.moment = [[0 for c in range(self.limit[1])] for r in range(self.limit[0])]
        for y in y_range:
            for x in x_range:
                self.cell_x = x
                self.cell_y = y
                self.moment[y][x] = self.generate()
        self.surroundings = self.moment

    def hood(self):
        hood_map = self.locate('ALL')
        neighbors = [hood_map[key] for key in ["NE", "N", "NW", "W", "SW", "S", "SE", "E"]]
        population = sum(list(map(lambda xy: self.surroundings[xy[1]][xy[0]], neighbors)))
        return population, hood_map

    def locate(self, target=None):
        compass = {
            "NE": (self.add_y(), self.add_x()),
            "N": (self.cell_x, self.add_y()),
            "NW": (self.add_y(), self.sub_x()),
            "W": (self.sub_x(), self.cell_y),
            "SW": (self.sub_y(), self.sub_x()),
            "S": (self.cell_x, self.sub_y()),
            "SE": (self.sub_y(), self.add_x()),
            "E": (self.add_x(), self.cell_y)
        }
        if target.upper() == "ALL":
            return compass
        if target not in compass.keys():
            raise KeyError("TARGET NOT FOUND")
        return compass[target]

    def add_y(self):
        y = self.cell_y
        return (y+1) if (y+1) < (self.limit[1]-1) else 0

    def sub_y(self):
        y = self.cell_y
        return (y - 1) if (y - 1) > 0 else (self.limit[1]-1)

    def add_x(self):
        x = self.cell_x
        return (x+1) if (x+1) < (self.limit[0]-1) else 0

    def sub_x(self):
        x = self.cell_x
        return (x-1) if (x-1) > 0 else (self.limit[0]-1)

    def __str__(self):
        x, y = self.cell_x, self.cell_y
        return "%s" % self.surroundings[y][x]

    def __int__(self):
        x, y = self.cell_x, self.cell_y
        return self.surroundings[y][x]

    def __add__(self, other):
        return self.__int__() + other

    def __sub__(self, other):
        return self.__int__() - other

    def __mul__(self, other):
        return self.__int__() * other

    def __divmod__(self, other):
        return self.__int__() / other


class golBoxLayout(BoxLayout):
    text_colour = ObjectProperty([1, 0, 0, 1])
    death_box = False
    generation = 0

    def __init__(self, **kwargs):
        b = kwargs.get('gol_board')
        u = int(kwargs.get('gol_unit'))
        s = float(kwargs.get('gol_speed'))
        rules = kwargs.get('gol_rules')
        self.gol_board = kwargs.get('last_board')
        self.generation = kwargs.get('last_gen')
        del kwargs['gol_board']
        del kwargs['gol_unit']
        del kwargs['gol_speed']
        del kwargs['gol_rules']
        del kwargs['last_board']
        del kwargs['last_gen']
        super(golBoxLayout, self).__init__(**kwargs)
        self.board_name = b
        if self.gol_board is None:
            self.gol_board = BOARDS[b]
        self.unit = u
        self.board_width = len(self.gol_board)
        self._scope = Cell(surroundings=self.gol_board, rules=rules)
        self.refresh_layout(None, generate=False)
        # Clock.schedule_interval(self.refresh_layout, s)
        self.generating = False
        self.speed = s

    def play(self):
        if self.generating is False:
            # update speed from settings
            per_second = int(App.get_running_app().config.get('gol', 'speed'))
            self.speed = float(1/per_second)
            self.generating = True
            Clock.schedule_interval(self.refresh_layout, self.speed)
        elif self.generating is True:
            Clock.unschedule(self.refresh_layout)
            self.generating = False

    def menu(self):
        pass

    def on_touch_down(self, touch):
        # touch = pos
        f_y, f_x = touch.pos
        # print(f_x, f_y)
        f_x /= self.unit
        f_y /= self.unit
        x, y = int(f_x), int(f_y)
        try:
            state = self.gol_board[y][x]
            self.gol_board[y][x] = LIFE if state is DEATH else DEATH
            super(golBoxLayout, self).on_touch_down(touch)
            self.refresh_layout(0, generate=False)
        except IndexError as e:
            # off board.
            pass

    def refresh_layout(self, dt, generate=True):
        if self.death_box:
            return
        u = self.unit
        if generate is True:
            # update the board (DEFAULT)
            if self.generation is None:
                self.generation = 0
            self.generation += 1
            App.get_running_app().gen_lbl.text = str(self.generation)
            self._scope.generation()
        self.gol_board = self._scope.surroundings
        # update the display
        with self.canvas:
            self.canvas.clear()
            # Rotate(axis=(0,0,1), angle=135, origin=self.center)
            life_signs = 0
            w = self.board_width
            for y in range(w):
                for x in range(w):
                    state = self.gol_board[y][x]
                    life_signs += state
                    if state == LIFE:
                        # Color(R, G, B, opacity)
                        Color(0, 1, 0, .9)  # green
                        # Color(random.random(), random.random(), random.random(), .9)
                        Ellipse(pos=(y*u, x*u), size=(u, u))
                    else:
                        Color(0, 0, 1, .9)  # blue
                        #Color(0, 0, 0, .9)
                        Ellipse(pos=(y*u, x*u), size=(u, u))
        if life_signs == 0:
            Clock.unschedule(self.refresh_layout)


class PlayButton(Button):
    def on_press(self):
        app = App.get_running_app()
        gb = app.game_board
        gb.play()
        self.text = "Pause" if gb.generating else "Play"


class MenuButton(Button):
    def on_press(self):
        app = App.get_running_app()
        App.open_settings(app)


class GameOfLife(App):

    def build_config(self, config):
        config.setdefaults('gol',
                           {
                               'board': 'TWENTY_THREE',
                               'unit': 25,
                               'speed': 1,
                               'birth': 23,
                               'survival': 23,
                               'world_size': 23
                           })

    def build_settings(self, settings):
        """
        Add our custom section to the default configuration object.
        """
        # We use the string defined above for our JSON, but it could also be
        # loaded from a file as follows:
        #
        settings.add_json_panel('gol', self.config, 'settings.json')

    def build(self):
        if os.path.isfile(os.path.join(os.getcwd(), 'saved.gol')):
            f = open(os.path.join(os.getcwd(), 'saved.gol'), 'rb')
            last_game = pickle.load(f)
            f.close()
            last_gen = last_game['GEN'] if last_game['GEN'] is not None else 0
            last_board = last_game['BOARD']
            b = last_game['SETTINGS']['board']
            u = float(last_game['SETTINGS']['unit'])
            s = float(last_game['SETTINGS']['speed'])
            birth = int(last_game['SETTINGS']['birth'])
            survival = int(last_game['SETTINGS']['survival'])
            w = int(last_game['SETTINGS']['world_size'])
        else:
            last_board = None
            last_gen = None
            try:
                b = self.config.get('gol', 'board')
                u = float(self.config.get('gol', 'unit'))
                s = self.config.get('gol', 'speed')
                birth = self.config.get('gol', 'birth')
                survival = self.config.get('gol', 'survival')
                w = int(self.config.get('gol', 'world_size'))
                if b == 'BLANK':
                    last_board = blank_grid(w)
            except Exception as e:
                last_gen = 0
                u, s = 23, 1
                birth, survival = 23, 23
                w = 23
                b = "TWENTY_THREE"
                self.config.set('gol', 'board', b)
                self.config.set('gol', 'unit', u)
                self.config.set('gol', 'speed', s)
                self.config.set('gol', 'world_size', w)
                #
                self.config.write()
        Window.size = (u * w, (u * w) + w + 5)
        self.root_layout = BoxLayout(orientation="vertical")
        self.control_box = BoxLayout(orientation="horizontal", size_hint_y=.05)
        play_btn = PlayButton(text="Play", height="50")
        # pause_btn = PauseButton(text="Pause", height="50")
        rules_btn = MenuButton(text="Menu", height="50")
        self.control_box.add_widget(play_btn)
        self.gen_lbl = Label(text="generation {}".format(last_gen))
        self.control_box.add_widget(self.gen_lbl)
        # self.control_box.add_widget(pause_btn)
        self.control_box.add_widget(rules_btn)
        self.game_board = golBoxLayout(gol_board=b, gol_unit=u, gol_speed=s, gol_rules=[birth, survival],
                                       last_board=last_board, last_gen=last_gen)
        self.root_layout.add_widget(self.control_box)
        self.root_layout.add_widget(self.game_board)
        return self.root_layout

    def on_stop(self):
        # freeze game
        last_board = self.game_board.gol_board
        last_gen = self.game_board.generation
        settings_board = self.config.get('gol', 'board')
        settings_birth = self.config.get('gol', 'birth')
        settings_unit = self.config.get('gol', 'unit')
        settings_speed = self.config.get('gol', 'speed')
        settings_survival = self.config.get('gol', 'survival')
        settings_world_size = self.config.get('gol', 'world_size')
        with open('saved.gol', 'wb') as f:
            data = {'GEN': last_gen,
                    'BOARD': last_board,
                    'SETTINGS': {
                        'board': settings_board,
                        'speed': settings_speed,
                        'birth': settings_birth,
                        'unit': settings_unit,
                        'survival': settings_survival,
                        'world_size': settings_world_size
                    }}
            output = pickle.dumps(data)
            f.write(output)
        f.close()


if __name__ == "__main__":
    GameOfLife().run()
