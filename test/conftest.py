"""Configure pytest fixtures.

Copyright 2026. Andrew Wang.
"""

from math import log2

import pytest

from src import Engine, Game, Ranker, StrArr, StrGrid, load_patterns, load_words


@pytest.fixture(scope="session")
def words() -> StrArr:
    """Provide singleton word list."""
    words, _ = load_words()
    return words


@pytest.fixture(scope="session")
def patterns() -> StrGrid:
    """Provide singleton precomputed patterns."""
    return load_patterns()


@pytest.fixture
def game(words: StrArr, patterns: StrGrid) -> Game:
    """Create starting game for all tests."""
    game = Game(words, patterns)
    assert game.current_round() == 0
    return game


@pytest.fixture
def ranker(words: StrArr, patterns: StrGrid) -> Ranker:
    """Create new ranker for all test."""
    ranker = Ranker(words, patterns)
    reachable, uncertainty = ranker.remaining_state()
    num_words = len(words)
    assert reachable == num_words
    assert uncertainty == log2(num_words)
    return ranker


@pytest.fixture
def engine(words: StrArr, ranker: Ranker) -> Engine:
    """Create new engine for each test."""
    return Engine(words, ranker)
