"""Test engine simulation.

Copyright 2026. Andrew Wang.
"""

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from src import Engine


def _get_histories() -> list[list[bytes | None]]:
    """Retrieve list of game histories. None is a stand-in for any guess."""
    return [
        [b"tares", b"bound", None, b"fjord"],
        [b"tares", b"mincy", b"cabin"],
        [b"tares", b"spite", b"oleum", None, b"stone"],
        [b"tares", b"spout", None, b"frost"],
        [b"tares", b"neeld", b"almah", None, b"bleak"],
    ]


@pytest.mark.parametrize("history", _get_histories())
def test_simulate(engine: Engine, history: list[bytes | None]) -> None:
    """Simulate engine games and validate history."""
    solution = history[-1]
    assert solution, "Final word cannot be None."
    game = engine.simulate(solution)
    for guessed, expected in zip(game.guess_hist, history, strict=True):
        if not expected:
            continue
        assert guessed == expected
