"""Basic Wordle square enumeration and comparisons.

Copyright 2026. Andrew Wang.
"""

import logging
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

    # Mark green squares by position matching.
    # Also validates len(guess) == len(answer)
    for i, (g, a) in enumerate(zip(guess, answer, strict=True)):
        if g == a:
            squares[i] = ord(b"g")

    # Iterate over non-green letters in guess.
    for i, letter in enumerate(guess):
        if squares[i] == ord(b"g"):
            continue
        # Count non-green appearances of letter in answer.
        max_yellow = sum(
            1
            for an, sq in zip(answer, squares, strict=True)
            if sq != ord(b"g") and an == letter
        )
        # Color up to max_yellow squares where guess matches letter.
        num_yellow = 0
        for j, gs in enumerate(guess):
            if num_yellow == max_yellow:
                break
            if gs == letter and squares[j] != ord(b"g"):
                squares[j] = ord(b"y")
                num_yellow += 1

    if pbar:
        pbar.update(1)
    return bytes(squares)
