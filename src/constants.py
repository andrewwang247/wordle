"""Basic Wordle square enumeration and comparisons.

Copyright 2026. Andrew Wang.
"""

import logging
from collections import Counter
from enum import StrEnum
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from tqdm import tqdm

type ByteArr = np.ndarray[tuple[int], np.dtype[np.bytes_]]
type ByteGrid = np.ndarray[tuple[int, int], np.dtype[np.bytes_]]

logger = logging.getLogger(__name__)


class Square(StrEnum):
    """Define square colors and their unicode representation."""

    BLACK = "\U00002b1b"
    YELLOW = "\U0001f7e8"
    GREEN = "\U0001f7e9"


_SQUARE_MAP = {ord("b"): Square.BLACK, ord("y"): Square.YELLOW, ord("g"): Square.GREEN}


def convert_squares(squares: bytes) -> str:
    """Convert convenience string of b, y, and g into squares."""
    return "".join(_SQUARE_MAP[sq] for sq in squares)


def wordle_compare(guess: bytes, answer: bytes, pbar: tqdm[Any] | None = None) -> bytes:
    """Given a guess and an answer, generate the squares pattern.

    This runs in a very tight loop during cache generation.
    """
    squares = bytearray(b"b" * len(guess))
    yellow_counts: Counter[int] = Counter()

    # Mark green squares by position matching.
    # Also validates len(guess) == len(answer).
    # Count frequency of non-green characters in answer.
    for i, (guess_letter, ans_letter) in enumerate(zip(guess, answer, strict=True)):
        if guess_letter == ans_letter:
            squares[i] = ord(b"g")
        else:
            yellow_counts[ans_letter] += 1

    # Iterate over non-green letters in guess.
    # Mark up to yellow_counts guess positions yellow.
    for i, letter in enumerate(guess):
        if squares[i] == ord(b"g"):
            continue
        if yellow_counts[letter] > 0:
            squares[i] = ord(b"y")
            yellow_counts[letter] -= 1

    if pbar:
        pbar.update(1)
    return bytes(squares)
