"""Test Game framework.

Copyright 2026. Andrew Wang.
"""

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from src import Game


def test_invalid(game: Game) -> None:
    """Test game given invalid inputs."""
    with pytest.raises(AssertionError):
        game.set_solution(b"abcde")
    game.set_solution(b"butte")
    with pytest.raises(AssertionError):
        game.append_is_win(b"abc", b"def")
    with pytest.raises(AssertionError):
        game.guess_is_win(b"ghi")


def test_online(game: Game) -> None:
    """Test online game with provided squares."""
    guesses = [b"reefs", b"crest", b"beach", b"coast"]
    squares = [b"bbgbb", b"ybgbb", b"byyyb", b"yyybb"]
    for rnd, (gs, sq) in enumerate(zip(guesses, squares, strict=True), start=1):
        is_win = game.append_is_win(gs, sq)
        assert not is_win
        assert game.current_round() == rnd
    assert game.append_is_win(b"ocean", b"ggggg")
    assert game.current_round() == len(guesses) + 1


def test_offline(game: Game) -> None:
    """Test offline game with generated squares."""
    game.set_solution(b"fungi")
    guesses = [b"fauna", b"ferns", b"pines", b"woods"]
    squares = [b"gbyyb", b"gbbyb", b"bygbb", b"bbbbb"]
    for rnd, (gs, sq) in enumerate(zip(guesses, squares, strict=True), start=1):
        actual, is_win = game.guess_is_win(gs)
        assert not is_win
        assert actual == sq
        assert game.current_round() == rnd
    win_sq, won = game.guess_is_win(b"fungi")
    assert won
    assert win_sq == b"ggggg"
    assert game.current_round() == len(guesses) + 1
