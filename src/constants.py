"""Basic Wordle square enumeration and comparisons.

Copyright 2026. Andrew Wang.
"""

import logging
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
from tqdm import tqdm

type StrArr = np.ndarray[tuple[int], np.dtype[np.str_]]
type StrGrid = np.ndarray[tuple[int, int], np.dtype[np.str_]]

logger = logging.getLogger(__name__)

_RESOURCE_DIR = Path("resources/")
_PATTERN_ARCHIVE_FILE = _RESOURCE_DIR / "patterns.npz"
_PATTERN_CACHE_FILE = _RESOURCE_DIR / "patterns.npy"


class Square(Enum):
    """Define square colors and their unicode representation."""

    BLACK = "\U00002b1b"
    YELLOW = "\U0001f7e8"
    GREEN = "\U0001f7e9"


SQUARE_VALUES = {item.value for item in Square}

BEST_OPENER = "tares"
BEST_TARGETED_OPENER = "tarse"


def convert_squares(user_str: str) -> str:
    """Convert convenience string of b, y, and g into squares."""
    values = []
    for letter in user_str:
        assert letter in ("b", "y", "g"), (
            f"Unrecognized character {letter} in squares string"
        )
        if letter == "b":
            values.append(Square.BLACK.value)
        elif letter == "y":
            values.append(Square.YELLOW.value)
        else:
            values.append(Square.GREEN.value)
    return "".join(values)


def wordle_compare(
    guess: str,
    answer: str,
    pbar: tqdm[Any] | None = None,
) -> str:
    """Given a guess and an answer, generate the squares pattern.

    This runs in a very tight vectorized loop during compilation.
    """
    assert len(guess) == len(answer), "Guess and answer must have matching lengths"
    guess_np = np.array(list(guess), dtype="<1U")
    answer_np = np.array(list(answer), dtype="<1U")
    squares = np.full_like(guess_np, Square.BLACK.value, dtype="<1U")

    # Green is the easiest case to handle by position.
    # The mask gm is used to remove them in further processing.
    not_green = guess_np != answer_np
    squares[~not_green] = Square.GREEN.value

    # We need to get the number (n) of times a guess letter in
    # a non-green spot occurs in expected. From there, we color
    # the first (up to) n occurrences of the letter yellow in guess.
    for cand in np.unique(guess_np[not_green]):
        # For every distinct character in guess not in a green spot,
        # get the number of times it appears in a non green answer spot.
        cand_count = np.count_nonzero(answer_np[not_green] == cand)
        # Mask for where this character appears in guess.
        matching_spots = guess_np == cand
        # Get indices where both not green and guess matches character.
        possible_idx = np.where(not_green & matching_spots)[0]
        # Make all of those indices up to cand_count yellow.
        squares[possible_idx[:cand_count]] = Square.YELLOW.value

    if pbar:
        pbar.update(1)
    return "".join(squares)


def compile_patterns(words: StrArr) -> None:
    """Compile and cache pattern combinations for every pairing.

    Save the output patterns to a compressed numpy archive.
    """
    logger.info("Cross compiling %d patterns for %d words", words.size**2, words.size)
    cmp_pat = np.vectorize(wordle_compare, otypes=[str])
    with tqdm(total=words.size**2) as pbar:
        # Matrix multiply vectorization magic.
        patterns: StrGrid = cmp_pat(words[:, np.newaxis], words, pbar)
    logger.info("Writing patterns to cache %s", _PATTERN_CACHE_FILE)
    np.save(_PATTERN_CACHE_FILE, patterns)
    logger.info("Writing patterns to archive %s", _PATTERN_ARCHIVE_FILE)
    np.savez_compressed(_PATTERN_ARCHIVE_FILE, patterns)
