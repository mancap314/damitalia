"""Main module."""
import numpy as np
from typing import Dict, List, Union
from .params import BOARD_BREADTH
import itertools


class Stone:
    def __init__(self, stone_id: int, value: str, color: str):
        """
        stone_id [int]: id of the stone
        value [str]: 'pawn' or 'queen'
        color [str]: 'black' or 'white'
        """
        if value not in ['pawn', 'queen']:
            print("""ERROR: value for a stone must be 'pawn' or 'queen'.
                    Stone creation cancelled.""")
            return
        if color not in ['white', 'black']:
            print("""ERROR: color for a stone must be 'white' or 'black'.
                    Stone creation cancelled.""")
            return
        self.stone_id = stone_id
        self.value = value
        self.color = color

    def get_color(self) -> str:
        return self.color

    def get_value(self) -> str:
        return self.value

    def set_value(self, value) -> None:
        if value not in ['pawn', 'queen']:
            print("""ERROR: value for a stone must be 'pawn' or 'queen'.
                    Stone creation cancelled.""")
            return
        if value == 'pawn' and self.value == 'queen':
            print(f"""ERROR: Stone {self.stone_id}: Impossible to change value
                    from 'queen' to 'stone'""")
            return
        self.value = value


class Move:
    def __init__(self, start_square: Union[int, list, np.array],
            direction=Union[list, np.array]):
        self.isvalid = True
        self.start_square = np.array([-1, -1], dtype=np.int8)
        self.direction = np.array([0, 0], dtype=np.int8)
        if isinstance(start_square, int):
            start_square = np.array(coord_int2couple(start_square),
                    dtype=np.int8)
        if isinstance(start_square, list):
            start_square = np.array(start_square, dtype=np.int8)
        if isinstance(direction, list) or isinstance(direction, tuple):
            direction = np.array(direction)
        start_square = start_square.reshape((-1,))
        direction = direction.reshape((-1,))
        if (start_square.shape[0] != 2 or start_square.min() < 0 or
                start_square.max() >= BOARD_BREADTH):
            print(f"""Error: {start_square} is an invalid square""")
            self.isvalid = False
        else:
            self.start_square = start_square
        if (direction.shape[0] != 2 or np.abs(direction).min() != 1 or
                np.abs(direction).max() != 1):
            print(f"""ERROR: {direction} is not a correct direction""")
            self.isvalid = False
        else:
            self.direction = direction
        self.landing_square = self.start_square + self.direction
        if (self.landing_square.max() >= BOARD_BREADTH or
                self.landing_square.min() < 0):
            print(f"""WARNING: move landing out of board""")
            self.isvalid = False

    def is_valid(self) -> bool:
        return self.isvalid

    def get_start_square_index(self) -> int:
        return coord_couple2int(self.start_square.tolist())

    def get_landing_square_index(self) -> int:
        if not self.isvalid:
            return -1
        return coord_couple2int(self.landing_square.tolist())

    def get_double_landing(self) -> int:
        double_landing = self.start_square + 2 * self.direction
        if double_landing.min() < 0 or double_landing.max() >= BOARD_BREADTH:
            return -1
        return coord_couple2int(double_landing.tolist())


class Board:
    def __init__(self, initial_setting: Union[Dict[int, Union[Stone, None]], None] = None):
        if isinstance(initial_setting, Dict):
            if not check_setting(initial_setting):
                return
            self.setting = initial_setting
        else:
            stone_id = 0
            self.setting = {}
            for i in range(get_max_square_index()):
                couple = coord_int2couple(i)
                if 0 <= couple[1] < 3:
                    stone = Stone(stone_id, 'white', 'pawn')
                    self.setting[i] = stone
                    stone_id += 1
                elif BOARD_BREADTH - 3 <= couple[1] < BOARD_BREADTH:
                    stone = Stone(stone_id, 'black', 'pawn')
                    self.setting[i] = stone
                    stone_id += 1
                else:
                    self.setting[i] = None

        def get_setting(self):
            return self.setting

        def set_setting(self, setting: Dict[int, Union[Stone, None]], check:
                bool = False) -> None:
            if check and not check_setting(setting):
                return
            self.setting = setting


def check_setting(setting: Dict[int, Union[Stone, None]]):
    is_valid = True
    if (sorted(list(setting.keys())) !=
            list(range(get_max_square_index()))):
        print("""ERROR: keys for this dict don't fit index range given
                by BOARD_RANGE defined in params.py""")
        is_valid = False
    for v in setting.values():
        if v is not None or not isinstance(v, Stone):
            print("""ERROR: initial_setting must contain only None on
            Stone""")
            is_valid = False
            break
    return is_valid


def get_max_square_index() -> int:
    """ Get the max index of a square given `BOARD_BREADTH` (defined in
            params.py) """
    max_square_index = (BOARD_BREADTH / 2) * BOARD_BREADTH - 1
    return int(max_square_index)


def coord_int2couple(coord: int) -> List[int]:
    """ Convert a coordinate given by its index to its couple coordinates """
    y_coord = int(coord // (BOARD_BREADTH / 2))
    x_coord = int(2 * (coord % (BOARD_BREADTH / 2)) + (y_coord % 2))
    return [int(x_coord), int(y_coord)]


def coord_couple2int(coord: list) -> int:
    """ Convert a coordinate given by couple coordinates to its index
    coordinate """
    if isinstance(coord, tuple):
        coord = list(coord)
    if (coord[0] + coord[1] % 2) % 2 == 1:
        print(f"""WARNING: coordinates {coord} correspond to a white square.
                Return index of the previous black square""")
    index = int((BOARD_BREADTH / 2) * coord[1] + int(coord[0] / 2))
    return index


def get_action_space():
    action_space = []
    possible_moves = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
    for index, direction in itertools.product(range(get_max_square_index() + 1),
            possible_moves):
        move = Move(index, direction)
        if move.is_valid():
            action_space.append(move)
    print(f"""INFO: {len(action_space)} moves in action_space""")
    return action_space 

