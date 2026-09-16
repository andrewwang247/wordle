"""Configure pytest fixtures.

Copyright 2026. Andrew Wang.
"""

from math import log2

import pytest

from src import ByteArr, ByteGrid, Engine, Game, Ranker, load_patterns, load_words


@pytest.fixture(scope="session")
def words() -> ByteArr:
    """Provide singleton word list."""
    return load_words()


@pytest.fixture(scope="session")
def patterns() -> ByteGrid:
    """Provide singleton precomputed patterns."""
    return load_patterns()


@pytest.fixture
def game(words: ByteArr, patterns: ByteGrid) -> Game:
    """Create starting game for all tests."""
    game = Game(words, patterns)
    assert game.current_round() == 0
    return game


@pytest.fixture
def ranker(words: ByteArr, patterns: ByteGrid) -> Ranker:
    """Create new ranker for all test."""
    ranker = Ranker(words, patterns)
    reachable, uncertainty = ranker.remaining_state()
    num_words = len(words)
    assert reachable == num_words
    assert uncertainty == log2(num_words)
    return ranker


@pytest.fixture
def engine(words: ByteArr, ranker: Ranker) -> Engine:
    """Create new engine for each test."""
    return Engine(words, ranker)
