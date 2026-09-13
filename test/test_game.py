"""Test Game framework.

Copyright 2026. Andrew Wang.
"""

import pytest

from src import Game, convert_squares


def test_invalid(game: Game) -> None:
    """Test game given invalid inputs."""
    with pytest.raises(AssertionError):
        game.set_solution("abcde")
    game.set_solution("butte")
    with pytest.raises(AssertionError):
        game.append_is_win("abc", "def")
    with pytest.raises(AssertionError):
        game.guess_is_win("ghi")


def test_online(game: Game) -> None:
    """Test online game with provided squares."""
    guesses = ["reefs", "crest", "beach", "coast"]
    squares = ["bbgbb", "ybgbb", "byyyb", "yyybb"]
    for rnd, (gs, sq) in enumerate(zip(guesses, squares, strict=True), start=1):
        is_win = game.append_is_win(gs, convert_squares(sq))
        assert not is_win
        assert game.current_round() == rnd
    assert game.append_is_win("ocean", convert_squares("ggggg"))
    assert game.current_round() == len(guesses) + 1


def test_offline(game: Game) -> None:
    """Test offline game with generated squares."""
    game.set_solution("fungi")
    guesses = ["fauna", "ferns", "pines", "woods"]
    squares = ["gbyyb", "gbbyb", "bygbb", "bbbbb"]
    for rnd, (gs, sq) in enumerate(zip(guesses, squares, strict=True), start=1):
        actual, is_win = game.guess_is_win(gs)
        assert not is_win
        assert actual == convert_squares(sq)
        assert game.current_round() == rnd
    win_sq, won = game.guess_is_win("fungi")
    assert won
    assert win_sq == convert_squares("ggggg")
    assert game.current_round() == len(guesses) + 1
