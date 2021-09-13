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

