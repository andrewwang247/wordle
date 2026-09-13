"""Test ranking calculation.

Copyright 2026. Andrew Wang.
"""

from math import log2

import pytest

from src import Ranker, convert_squares, load_patterns, load_words

WORDS, _ = load_words()
PATTERNS = load_patterns()


@pytest.fixture(scope="module")
def ranker() -> Ranker:
    """Create new ranker for all test."""
    ranker = Ranker(WORDS, PATTERNS)
    reachable, uncertainty = ranker.remaining_state()
    assert reachable == len(WORDS)
    assert uncertainty == log2(len(WORDS))
    return ranker


def test_invalid(ranker: Ranker) -> None:
    """Test rankings with invalid inputs."""
    with pytest.raises(AssertionError):
        ranker.update("abcde", convert_squares("bgygb"))


def test_game(ranker: Ranker) -> None:
    """Test rankings over a game with solution blaze."""
    guesses = ["gleam", "comet", "space"]
    squares = ["bgyyb", "bbbyb", "bbgbg"]
    remainder = [51, 21, 7]
    informative = ["stane", "skarn", "frond"]

    for gs, sq, remain, next_gs in zip(
        guesses, squares, remainder, informative, strict=True
    ):
        ranker.update(gs, convert_squares(sq))
        actual_reachable, uncertainty = ranker.remaining_state()
        assert actual_reachable == remain
        assert uncertainty == log2(remain)
        actual_guesses, _ = ranker.informative_guesses()
        assert actual_guesses[0] == next_gs

    ranker.update("blaze", convert_squares("ggggg"))
    reachable, uncertainty = ranker.remaining_state()
    assert reachable == 1
    assert uncertainty == log2(reachable)
