"""Test engine simulation.

Copyright 2026. Andrew Wang.
"""

import pytest

from src import BEST_OPENER, BEST_TARGETED_OPENER, Engine


def _get_histories() -> list[list[bytes | None]]:
    """Retrieve list of game histories. None is a stand-in for any guess."""
    return [
        [BEST_OPENER, b"bound", None, b"fjord"],
        [BEST_OPENER, b"mincy", b"cabin"],
        [BEST_OPENER, b"spite", b"oleum", None, b"stone"],
        [BEST_OPENER, b"spout", None, b"frost"],
        [BEST_OPENER, b"neeld", b"almah", None, b"bleak"],
    ]


def _get_targeted_histories() -> list[list[bytes | None]]:
    """Retrieve list of targeted game histories. None is a stand-in for any guess."""
    return [
        [BEST_TARGETED_OPENER, b"coign", b"flood", b"fjord"],
        [BEST_TARGETED_OPENER, b"mincy", b"cabin"],
        [BEST_TARGETED_OPENER, b"lokum", b"stone"],
        [BEST_TARGETED_OPENER, None, b"frost"],
        [BEST_TARGETED_OPENER, b"medal", None, b"bleak"],
    ]


@pytest.mark.parametrize(
    ("engine_fixture", "history"),
    [
        *[("engine", h) for h in _get_histories()],
        *[("targeted_engine", h) for h in _get_targeted_histories()],
    ],
)
def test_simulate(
    request: pytest.FixtureRequest, engine_fixture: str, history: list[bytes | None]
) -> None:
    """Simulate engine games and validate history."""
    engine = request.getfixturevalue(engine_fixture)
    assert isinstance(engine, Engine)
    solution = history[-1]
    assert solution, "Final word cannot be None."
    game = engine.simulate(solution)
    for guessed, expected in zip(game.guess_hist, history, strict=True):
        if not expected:
            continue
        assert guessed == expected
