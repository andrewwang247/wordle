"""Test ranking calculation.

Copyright 2026. Andrew Wang.
"""

from math import log2

import pytest

from src import Ranker, convert_squares


def _get_rankings() -> list[tuple[list[str], list[str], list[int], list[str | None]]]:
    """Get guesses, squares, remainders, and suggestions.

    None is a stand-in for no valid suggestion.
    """
    return [
        (
            ["gleam", "comet", "space", "blaze"],
            ["bgyyb", "bbbyb", "bbgbg", "ggggg"],
            [51, 21, 7, 1],
            ["stane", "skarn", "frond", None],
        ),
        (
            ["coral", "amber", "black", "olive"],
            ["bybby", "bbbyb", "bgbbb", "ggggg"],
            [215, 54, 23, 1],
            ["peons", "sloot", "stipe", None],
        ),
    ]


def test_invalid(ranker: Ranker) -> None:
    """Test rankings with invalid inputs."""
    with pytest.raises(AssertionError):
        ranker.update("abcde", convert_squares("bgygb"))


@pytest.mark.parametrize(
    ("guesses", "squares", "remainder", "informative"), _get_rankings()
)
def test_game(
    ranker: Ranker,
    guesses: list[str],
    squares: list[str],
    remainder: list[int],
    informative: list[str | None],
) -> None:
    """Test rankings with series of rounds."""
    for gs, sq, remain, suggested in zip(
        guesses, squares, remainder, informative, strict=True
    ):
        ranker.update(gs, convert_squares(sq))
        actual_reachable, uncertainty = ranker.remaining_state()
        assert actual_reachable == remain
        assert uncertainty == log2(remain)
        if suggested:
            actual_guesses, _ = ranker.informative_guesses()
            assert actual_guesses[0] == suggested
