#!/usr/bin/env python

"""Tests for `damitalia` package."""

import pytest
from damitalia import damitalia, params

@pytest.fixture
def extremity_id():
    extremity = int(params.BOARD_BREADTH * (params.BOARD_BREADTH / 2) - 1)
    return extremity

@pytest.fixture
def first_row1_id():
    first_row1 = int(params.BOARD_BREADTH / 2)
    return first_row1

@pytest.fixture
def extremity_couple():
    extremity = [params.BOARD_BREADTH - 1, params.BOARD_BREADTH - 1]
    return extremity

@pytest.fixture
def v_board_setting():
    board_setting = {i: None for i \
            in range(damitalia.get_max_square_index() + 1)}
    board_setting[1] = damitalia.Stone(0, 'pawn', 'white')
    board_setting[4] = damitalia.Stone(1, 'pawn', 'black')
    board_setting[5] = damitalia.Stone(2, 'pawn', 'black')
    board_setting[12] = damitalia.Stone(2, 'pawn', 'white')
    board_setting[16] = damitalia.Stone(1, 'pawn', 'black')
    board_setting[17] = damitalia.Stone(2, 'queen', 'black')
    return board_setting

@pytest.fixture
def dual_board_setting():
    board_setting = {i: None for i \
            in range(damitalia.get_max_square_index() + 1)}
    board_setting[5] = damitalia.Stone(1, 'pawn', 'white')
    board_setting[10] = damitalia.Stone(0, 'pawn', 'black')
    return board_setting


@pytest.fixture
def forelast_board_setting():
    board_setting = {i: None for i in range(damitalia.get_max_square_index() + 1)}
    ind = damitalia.coord_couple2int([params.BOARD_BREADTH - 2, params.BOARD_BREADTH
            -2])
    board_setting[ind] = damitalia.Stone(0, 'pawn', 'white')
    ind = damitalia.coord_couple2int([0, params.BOARD_BREADTH - 2])
    board_setting[ind] = damitalia.Stone(1, 'pawn', 'white')
    ind = damitalia.coord_couple2int([1, params.BOARD_BREADTH - 1])
    board_setting[ind] = damitalia.Stone(3, 'pawn', 'black')
    ind = damitalia.coord_couple2int([1, 1])
    board_setting[ind] = damitalia.Stone(4, 'pawn', 'white')
    ind = damitalia.coord_couple2int([2, 2])
    board_setting[ind] = damitalia.Stone(5, 'pawn', 'black')
    return board_setting


@pytest.fixture
def capture_board_setting():
    board_setting = {i: None for i in range(damitalia.get_max_square_index() + 1)}
    board_setting[1] = damitalia.Stone(0, 'pawn', 'white')
    board_setting[4] = damitalia.Stone(1, 'pawn', 'black')
    board_setting[5] = damitalia.Stone(2, 'pawn', 'black')
    board_setting[13] = damitalia.Stone(3, 'pawn', 'black')
    board_setting[14] = damitalia.Stone(4, 'pawn', 'black')
    board_setting[20] = damitalia.Stone(5, 'pawn', 'black')
    board_setting[21] = damitalia.Stone(6, 'pawn', 'black')
    return board_setting


def test_coord_int2couple(extremity_id, first_row1_id, extremity_couple):
    """ Test transformation from square id to couple coordinates """
    assert damitalia.coord_int2couple(0) == [0, 0]
    assert damitalia.coord_int2couple(1) == [2, 0]
    assert damitalia.coord_int2couple(first_row1_id) == [1, 1]
    assert damitalia.coord_int2couple(extremity_id) == extremity_couple


def test_coord_couple2int(extremity_id, first_row1_id, extremity_couple):
    """ Test transformation from square couple coordinates to id """
    assert damitalia.coord_couple2int([0, 0]) == 0
    assert damitalia.coord_couple2int([2, 0]) == 1
    assert damitalia.coord_couple2int([1, 1]) == first_row1_id
    assert damitalia.coord_couple2int([2, 1]) == 5
    assert damitalia.coord_couple2int(extremity_couple) == extremity_id


def test_move_class(extremity_couple):
    move = damitalia.Move(0, [-1, -1])
    assert move.is_valid() is False
    move = damitalia.Move(extremity_couple, [-1, 1])
    assert move.is_valid() is False
    move = damitalia.Move(extremity_couple, [-1, -1])
    assert move.is_valid()
    assert (move.get_landing_square_index() ==
        damitalia.coord_couple2int([params.BOARD_BREADTH - 2, 
            params.BOARD_BREADTH - 2]))

def test_get_action_space():
    action_space = damitalia.get_action_space()
    if params.BOARD_BREADTH == 8:
        assert len(action_space) == 98


def test_get_move_directions():
    stone = damitalia.Stone(0, 'pawn', 'black')
    captures = damitalia.get_move_directions(stone)
    captures = [tuple(capture.tolist()) for capture in captures]
    assert set(captures) == set([(-1, -1), (1, -1)])

    stone = damitalia.Stone(0, 'pawn', 'white')
    captures = damitalia.get_move_directions(stone)
    captures = [tuple(capture.tolist()) for capture in captures]
    assert set(captures) == set([(-1, 1), (1, 1)])

    stone = damitalia.Stone(0, 'queen', 'black')
    captures = damitalia.get_move_directions(stone)
    captures = [tuple(capture.tolist()) for capture in captures]
    assert set(captures) == set([(-1, -1), (1, -1), (1, 1), (-1, 1)])


def test_board_captures_moves(v_board_setting, dual_board_setting):
    captures, moves = damitalia.board_captures_moves(v_board_setting, 'white')
    assert len(moves) == 0
    captures = [(capture.get_start_square_index(),
        capture.get_landing_square_index()) for capture in captures]
    assert set(captures) == set([(1, 4), (1, 5)])
    captures, moves = damitalia.board_captures_moves(dual_board_setting, 'white')
    captures = [(capture.get_start_square_index(), 
        capture.get_landing_square_index()) for capture in captures]
    assert set(captures) == set([(5, 10)])
    captures, moves = damitalia.board_captures_moves(dual_board_setting, 'black')
    captures = [(capture.get_start_square_index(), 
        capture.get_landing_square_index()) for capture in captures]
    assert set(captures) == set([(10, 5)])


def test_get_board_setting_after(forelast_board_setting):
    is_capture = False
    ind_before = damitalia.coord_couple2int([params.BOARD_BREADTH - 2, 
        params.BOARD_BREADTH - 2])
    move = damitalia.Move(ind_before, [1, 1])
    board_setting = damitalia.get_board_setting_after(board_setting=forelast_board_setting,
            move=move, is_capture=is_capture)
    ind_after = damitalia.coord_couple2int([params.BOARD_BREADTH - 1,
        params.BOARD_BREADTH - 1])
    assert board_setting.get(ind_before) is None
    assert board_setting.get(ind_after).get_value() == 'queen'


def test_ll_combine():
    l1 = [['a', 'b'], ['c', 'd', 'e']]
    l2 = [[1], [2, 3], [1, 4]]
    res = damitalia.ll_combine(l1, l2)
    tuple_res = set([tuple(e) for e in res])
    should_res = set([('a', 'b', 1), ('a', 'b', 2, 3), ('a', 'b', 1, 4), ('c',
        'd', 'e', 1), ('c', 'd', 'e', 2, 3), ('c', 'd', 'e', 1, 4)])
    assert tuple_res == should_res

def test_get_capture_sequence(capture_board_setting):
    move = damitalia.Move(1, [1, 1]) 
    next_board_setting = damitalia.get_board_setting_after(board_setting=capture_board_setting,
            move=move, is_capture=True)
    print(f'In test_get_capture_sequence():\
            next_board_setting:\n{next_board_setting}')
    capture_sequence = damitalia.get_capture_sequence(board_setting=next_board_setting, \
            capture_sequence=[[move]], square_index=move.get_double_landing(), 
            color='white', stone_value='pawn', call_depth=0)
    capture_sequence = [tuple([(move.get_start_square_index(),
        move.get_landing_square_index()) for move in seq]) for seq in capture_sequence]
    print(f'In test_get_capture_sequence():\
            capture_sequence:\n{capture_sequence}')
    assert set(capture_sequence) == set([((1, 5), (10, 14)), ((1, 5), (10, 13),
        (17, 20)), ((1, 5), (10, 13), (17, 21))])
