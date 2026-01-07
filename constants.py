"""
Basic Wordle square enumeration and comparisons.

Copyright 2026. Andrew Wang.
"""
from typing import Optional
from enum import Enum
import numpy as np
from tqdm import tqdm


class Square(Enum):
    """Define square colors and their unicode representation."""

    BLACK = '\U00002B1B'
    YELLOW = '\U0001F7E8'
    GREEN = '\U0001F7E9'


SQUARE_VALUES = {item.value for item in Square}

BEST_FIRST_GUESS = 'tares'
DEFAULT_LANGUAGE = 'en'


def convert_squares(user_str: str) -> str:
    """Convert convenience string of b, y, and g into squares."""
    values = []
    for letter in user_str:
        assert letter in ('b', 'y', 'g'), \
            f'Unrecognized character {letter} in squares string'
        if letter == 'b':
            values.append(Square.BLACK.value)
        elif letter == 'y':
            values.append(Square.YELLOW.value)
        else:
            values.append(Square.GREEN.value)
    return ''.join(values)


def wordle_compare(guess: str, answer: str,
                   pbar: Optional[tqdm] = None) -> str:
    """
    Given a guess and an answer, generate the squares pattern.

    This runs in a very tight vectorized loop during compilation.
    """
    assert len(guess) == len(answer), \
        'Guess and answer must have matching lengths'
    guess_np = np.array(list(guess), dtype='<1U')
    answer_np = np.array(list(answer), dtype='<1U')
    squares = np.full_like(guess_np, Square.BLACK.value, dtype='<1U')

    # Green is the easiest case to handle by position.
    # The mask gm is used to remove them in further processing.
    not_green = guess_np != answer_np
    squares[~not_green] = Square.GREEN.value

    # We need to get the number (n) of times a guess letter in
    # a non-green spot occurs in expected. From there, we color
    # the first (up to) n occurences of the letter yellow in guess.
    for cand in np.unique(guess_np[not_green]):
        # For every distinct character in guess not in a green spot,
        # get the number of times it appears in a non green answer spot.
        cand_count = np.count_nonzero(answer_np[not_green] == cand)
        # Mask for where this character appears in guess.
        matching_spots = guess_np == cand
        # Get indicies where both not green and guess matches character.
        possible_idx = np.where(not_green & matching_spots)[0]
        # Make all of those indices up to cand_count yellow.
        squares[possible_idx[:cand_count]] = Square.YELLOW.value

    if pbar:
        pbar.update(1)
    return ''.join(squares)
