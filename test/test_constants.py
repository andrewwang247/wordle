"""Test word comparison and square generation.

Copyright 2026. Andrew Wang.
"""

import pytest

from src import wordle_compare


def _get_comparisons() -> list[tuple[bytes, bytes, bytes]]:
    """Get guesses, solutions, and square combos to test."""
    return [
        (b"flaws", b"fangs", b"gbybg"),
        (b"glass", b"honey", b"bbbbb"),
        (b"agave", b"javas", b"ybyyb"),
        (b"tinge", b"tinge", b"ggggg"),
        (b"paris", b"sepia", b"yybgy"),
        (b"chase", b"aches", b"yyyyy"),
        (b"bayes", b"saber", b"ygbgy"),
    ]


@pytest.mark.parametrize(("guess", "solution", "squares"), _get_comparisons())
def test_compare(guess: bytes, solution: bytes, squares: bytes) -> None:
    """Test square generation from word pairs."""
    actual = wordle_compare(guess, solution)
    assert actual == squares
