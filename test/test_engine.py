"""Test engine simulation.

Copyright 2026. Andrew Wang.
"""

import pytest

from src import Engine, Ranker, load_patterns, load_words

WORDS, _ = load_words()
PATTERNS = load_patterns()


def _get_histories() -> list[list[str]]:
    """Retrieve list of game histories."""
    return [["tares", "bound", "cirri", "fjord"]]


@pytest.fixture
def engine() -> Engine:
    """Create new engine for each test."""
    ranker = Ranker(WORDS, PATTERNS)
    return Engine(WORDS, ranker)


@pytest.mark.parametrize("history", _get_histories())
def test_simulate(engine: Engine, history: list[str]) -> None:
    """Simulate engine games and validate history."""
    solution = history[-1]
    game = engine.simulate(solution)
    assert game.guess_hist == history
