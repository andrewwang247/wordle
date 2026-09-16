"""Basic Wordle square enumeration and comparisons.

Copyright 2026. Andrew Wang.
"""

import logging
from enum import Enum
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from tqdm import tqdm

type ByteArr = np.ndarray[tuple[int], np.dtype[np.bytes_]]
type ByteGrid = np.ndarray[tuple[int, int], np.dtype[np.bytes_]]

logger = logging.getLogger(__name__)


class Square(Enum):
    """Define square colors and their unicode representation."""

    BLACK = "\U00002b1b"
    YELLOW = "\U0001f7e8"
    GREEN = "\U0001f7e9"


def convert_squares(squares: bytes) -> str:
    """Convert convenience string of b, y, and g into squares."""
    values = []
    for sq in squares:
        assert sq in {ord("g"), ord("y"), ord("b")}, (
            f"Unrecognized character {sq} in squares"
        )
        if sq == ord("b"):
            values.append(Square.BLACK.value)
        elif sq == ord("y"):
            values.append(Square.YELLOW.value)
        else:
            values.append(Square.GREEN.value)
    return "".join(values)


def wordle_compare(
    guess: bytes,
    answer: bytes,
    pbar: tqdm[Any] | None = None,
) -> bytes:
    """Given a guess and an answer, generate the squares pattern.

    This runs in a very tight vectorized loop during compilation.
    """
    assert len(guess) == len(answer), "Guess and answer must have matching lengths"
    guess_np: ByteArr = np.frombuffer(guess, dtype="S1")
    answer_np: ByteArr = np.frombuffer(answer, dtype="S1")
    squares: ByteArr = np.full_like(guess_np, b"b", dtype="S1")

    # Green is the easiest case to handle by position.
    # not_green is used as a mask in further processing.
    not_green = guess_np != answer_np
    squares[~not_green] = b"g"

    # Count times n a letter in a non-green guess spot occurs in answer.
    # Color the first (up to) n occurrences of the letter yellow in guess.
    for cand in np.unique(guess_np[not_green]):
        # For every distinct character in guess not in a green spot,
        # get the number of times it appears in a non green answer spot.
        cand_count = np.count_nonzero(answer_np[not_green] == cand)
        # Mask for where this character appears in guess.
        matching_spots = guess_np == cand
        # Get indices where both not green and guess matches character.
        possible_idx = np.where(not_green & matching_spots)[0]
        # Make all of those indices up to cand_count yellow.
        squares[possible_idx[:cand_count]] = b"y"

    if pbar:
        pbar.update(1)
    return squares.tobytes()
