"""Test engine simulation.

Copyright 2026. Andrew Wang.
"""

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from src import Engine


def _get_histories() -> list[list[str | None]]:
    """Retrieve list of game histories. None is a stand-in for any guess."""
    return [
        ["tares", "bound", None, "fjord"],
        ["tares", "mincy", "cabin"],
        ["tares", "spite", "oleum", None, "stone"],
        ["tares", "spout", None, "frost"],
        ["tares", "neeld", "almah", None, "bleak"],
    ]


@pytest.mark.parametrize("history", _get_histories())
def test_simulate(engine: Engine, history: list[str | None]) -> None:
    """Simulate engine games and validate history."""
    solution = history[-1]
    assert solution, "Final word cannot be any."
    game = engine.simulate(solution)
    for guessed, expected in zip(game.guess_hist, history, strict=True):
        if not expected:
            continue
        assert guessed == expected
