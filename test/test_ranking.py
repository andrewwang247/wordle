"""Test ranking calculation.

Copyright 2026. Andrew Wang.
"""

from math import log2
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from src import Ranker


def _get_rankings() -> list[
    tuple[list[bytes], list[bytes], list[int], list[bytes | None]]
]:
    """Get guesses, squares, remainders, and suggestions.

    None is a stand-in for no valid suggestion.
    """
    return [
        (
            [b"gleam", b"comet", b"space", b"blaze"],
            [b"bgyyb", b"bbbyb", b"bbgbg", b"ggggg"],
            [51, 21, 7, 1],
            [b"stane", b"skarn", b"frond", None],
        ),
        (
            [b"coral", b"amber", b"black", b"olive"],
            [b"bybby", b"bbbyb", b"bgbbb", b"ggggg"],
            [215, 54, 23, 1],
            [b"peons", b"sloot", b"stipe", None],
        ),
    ]


def test_invalid(ranker: Ranker) -> None:
    """Test rankings with invalid inputs."""
    with pytest.raises(AssertionError):
        ranker.update(b"abcde", b"bgygb")


@pytest.mark.parametrize(
    ("guesses", "squares", "remainder", "informative"), _get_rankings()
)
def test_game(
    ranker: Ranker,
    guesses: list[bytes],
    squares: list[bytes],
    remainder: list[int],
    informative: list[bytes | None],
) -> None:
    """Test rankings with series of rounds."""
    for gs, sq, remain, suggested in zip(
        guesses, squares, remainder, informative, strict=True
    ):
        ranker.update(gs, sq)
        actual_reachable, uncertainty = ranker.remaining_state()
        assert actual_reachable == remain
        assert uncertainty == log2(remain)
        if suggested:
            actual_guesses, _ = ranker.informative_guesses()
            assert actual_guesses[0] == suggested
