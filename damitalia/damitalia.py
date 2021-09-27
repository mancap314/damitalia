"""Main module."""
import numpy as np
from typing import Dict, List, Tuple, Union
from .params import BOARD_BREADTH
import itertools
import logging
import logging.config
from copy import deepcopy
from itertools import product

# create logger
from os import path
log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logging.conf')
logging.config.fileConfig(log_file_path)
logger = logging.getLogger('damitalia')


class Stone:
    def __init__(self, stone_id: int, value: str, color: str):
        if value not in ['pawn', 'queen']:
            logger.error("value for a stone must be 'pawn' or 'queen'. Stone\
                    creation cancelled.")
            return
        if color not in ['white', 'black']:
            logger.error("color for a stone must be 'white' or 'black'. Stone\
                    creation cancelled.")
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
            logger.error("value for a stone must be 'pawn' or 'queen'. Stone\
                    creation cancelled.")
            return
        if value == 'pawn' and self.value == 'queen':
            logger.error("Stone %i: Impossible to change value from 'queen' to\
                    'stone'", self.stone_id)
            return
        self.value = value

    def __str__(self):
        return f'<Stone {self.stone_id}: {self.color} {self.value}>'

    def __repr__(self):
        return self.__str__()


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
            logger.error('%i is an invalid square', start_square)
            self.isvalid = False
        else:
            self.start_square = start_square
        if (direction.shape[0] != 2 or np.abs(direction).min() != 1 or
                np.abs(direction).max() != 1):
            logger.error('%s is not a correct direction', str(direction))
            self.isvalid = False
        else:
            self.direction = direction
        self.landing_square = self.start_square + self.direction
        if (self.landing_square.max() >= BOARD_BREADTH or
                self.landing_square.min() < 0):
            logger.warning('move landing out of board')
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

    def __str__(self):
        return f'<Move ({self.get_start_square_index()}, {self.get_landing_square_index()})>'

    def __repr__(self):
        return self.__str__()


class Game:
    def __init__(self, initial_setting: Union[Dict[int, Union[Stone, None]], None] = None):
        if isinstance(initial_setting, dict):
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
        logger.error("""keys for this dict don't fit index range given
                by BOARD_RANGE defined in params.py""")
        is_valid = False
    for v in setting.values():
        if v is not None or not isinstance(v, Stone):
            logger.error('initial_setting must contain only None or Stone')
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
        logger.warning('coordinates %s correspond to a white square.\
                Return index of the previous black square', str(coord))
    index = int((BOARD_BREADTH / 2) * coord[1] + int(coord[0] / 2))
    return index


def get_action_space() -> List[Move]:
    action_space = []
    possible_moves = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
    for index, direction in itertools.product(range(get_max_square_index() + 1),
            possible_moves):
        move = Move(index, direction)
        if move.is_valid():
            action_space.append(move)
    logger.info('%i moves in action_space', len(action_space))
    return action_space


def get_move_directions(stone: Stone) -> List[np.array]:
    basic_directions = [np.array([-1, 1], dtype=np.int8), np.array([1, 1],
        dtype=np.int8)]
    if stone.get_value() == 'pawn':
        capture_directions = basic_directions if stone.get_color() == 'white' else [-m
                for m in basic_directions]
        return capture_directions
    return basic_directions + [-m for m in basic_directions]


def preliminary_check(color: str, board_setting: Dict[int, Stone], square_index: int, 
        move_direction: np.array) -> Tuple[bool, Union[None, Move], Union[None, Stone]]:
    stone = board_setting.get(square_index)
    if stone is None or stone.get_color() != color:
        return False, None, None, None
    move = Move(square_index, move_direction)
    if not move.is_valid():
        return False, None, None, None
    next_square_id = move.get_landing_square_index()
    if next_square_id not in board_setting:
        logger.error('no indice %i in board_setting', next_square_id)
        return False, None, None, None
    next_square_stone = board_setting.get(next_square_id)
    return True, move, stone, next_square_stone


def can_eat(color: str, board_setting: Dict[int, Stone], move: Move, stone: Stone,
        next_square_stone: Stone) -> bool:
    opposite_color = 'black' if color == 'white' else 'white'
    if (next_square_stone is None or next_square_stone.get_color() !=
        opposite_color):
        return False
    if (stone.get_value() == 'pawn' and next_square_stone.get_value() ==
        'queen'):
        return False
    overnext_square_id = move.get_double_landing()
    if overnext_square_id == -1:
        return False
    if overnext_square_id not in board_setting:
        logger.error('no indice %i in board_setting', overnext_square_id)
        return False
    overnext_square_stone = board_setting.get(overnext_square_id)
    if overnext_square_stone is not None:
        return False
    return True


def can_move(next_square_stone: Stone) -> bool:
    return next_square_stone is None


def stone_captures_moves(board_setting: Dict[int, Union[None, Stone]],
        square_index: int, color: str, check_moves: bool):
    captures, moves = [], []
    stone = board_setting.get(square_index)
    logger.debug(f'square_index: {square_index}, color: {color}')
    if stone is None or stone.get_color() != color:
        logger.debug(f'stone empty or stone of wrong color at square_index\
                {square_index} for color {color}. Board\
                setting:\n{board_setting}')
        return [], []
    for move_direction in get_move_directions(stone):
        preliminary_ok, move, stone, next_square_stone =\
            preliminary_check(color=color, board_setting=board_setting,
                square_index=square_index,
                move_direction=move_direction)
        if not preliminary_ok:
            continue
        if can_eat(color=color, board_setting=board_setting, move=move,
                stone=stone, next_square_stone=next_square_stone):
            captures.append(move)
        if check_moves and len(captures) == 0 and can_move(next_square_stone):
            moves.append(move)
    return captures, moves


def board_captures_moves(board_setting: Dict[int, Union[None, Stone]], color: str) -> Tuple[List[Move], List[Move]]:
    if color not in ['black', 'white']:
        logger.error("""color must be 'black' or 'white'""")
    captures, moves = [], []
    for square_index in board_setting.keys():
        check_moves = (len(captures) == 0)
        stone_captures, stone_moves =\
            stone_captures_moves(board_setting=board_setting,
                    square_index=square_index, color=color, check_moves=check_moves)
        captures += stone_captures
        moves += stone_moves
    moves = moves if len(captures) == 0 else []
    return captures, moves


def get_board_setting_after(board_setting: Dict[int, Union[None, Stone]], move:
        Move, is_capture: bool = False):
    stone = board_setting.get(move.get_start_square_index())
    board_setting_after = deepcopy(board_setting)
    board_setting_after[move.get_start_square_index()] = None
    final_square = move.get_double_landing() if is_capture \
            else move.get_landing_square_index()
    if is_capture:
        board_setting_after[move.get_landing_square_index()] = None
    board_setting_after[final_square] = stone
    final_row = 0 if stone.get_color() == 'black' else BOARD_BREADTH - 1
    if coord_int2couple(final_square)[1] == final_row:
        stone.set_value('queen')
    return board_setting_after


def ll_combine(l1: List[List], l2: List[List]) -> List[List]:
    return [e1 + e2 for e1, e2 in product(l1, l2)]


def get_capture_sequence(board_setting: Dict[int, Union[None, Stone]],
        capture_sequence: List[List[Move]], square_index: int, color: str,
        stone_value: str, call_depth: int = 0) -> List[List[Move]]:
    captures, _ = stone_captures_moves(board_setting=board_setting,
            square_index=square_index, color=color, check_moves=False)
    logger.debug(f'captures: {captures}')
    if len(captures) == 0 or (stone_value == 'pawn' and call_depth == 2):
        return ll_combine(capture_sequence, [captures])
    next_captures = []
    for capture in captures:
        next_board_setting = get_board_setting_after(board_setting=board_setting, 
                move=capture, is_capture=True)
        next_capture_sequence = ll_combine(capture_sequence, [[capture]])
        next_square_index = capture.get_double_landing()
        next_capture = get_capture_sequence(board_setting=next_board_setting,
            capture_sequence=next_capture_sequence,
            square_index=next_square_index, color=color, 
            stone_value=stone_value, call_depth=call_depth+1) 
        next_captures += next_capture
    logger.debug(f'next_captures: {next_captures}')
    return next_captures
