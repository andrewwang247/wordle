"""Test word comparison and square generation.

Copyright 2026. Andrew Wang.
"""

import pytest

from src import wordle_compare


def _get_comparisons() -> list[tuple[str, str, str]]:
    """Get guesses, solutions, and square combos to test."""
    return [
        ("flaws", "fangs", "gbybg"),
        ("glass", "honey", "bbbbb"),
        ("agave", "javas", "ybyyb"),
        ("tinge", "tinge", "ggggg"),
        ("paris", "sepia", "yybgy"),
        ("chase", "aches", "yyyyy"),
        ("bayes", "saber", "ygbgy"),
    ]


@pytest.mark.parametrize(("guess", "solution", "squares"), _get_comparisons())
def test_compare(guess: str, solution: str, squares: str) -> None:
    """Test square generation from word pairs."""
    actual = wordle_compare(guess, solution)
    assert actual == squares
