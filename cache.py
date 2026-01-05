"""
Pre-compile and cache wordle comparisons, forming a pattern grid.

Copyright 2026. Andrew Wang.
"""
from itertools import product
from collections import Counter
import numpy as np
from tqdm import tqdm
from constants import Square


def _wordle_compare(
        guess: np.ndarray,
        answer: np.ndarray) -> np.ndarray:
    """
    Given a guess and an answer, generate the squares pattern.

    This function runs in a very tight loop during compilation.
    """
    assert guess.ndim == answer.ndim == 1
    assert guess.shape == answer.shape
    squares = np.full_like(guess, Square.BLACK.value, dtype=np.uint8)

    # Green is the easiest case to handle by position.
    # The mask gm is used to remove them in further processing.
    not_green = guess != answer
    squares[~not_green] = Square.GREEN.value

    # We need to get the number (n) of times a guess letter in
    # a non-green spot occurs in expected. From there, we color
    # the first (up to) n occurences of the letter yellow in guess.
    for cand in np.unique(guess[not_green]):
        # For every distinct character in guess not in a green spot,
        # get the number of times it appears in a non green answer spot.
        cand_count = np.count_nonzero(answer[not_green] == cand)
        # Mask for where this character appears in guess.
        matching_spots = guess == cand
        # Get indicies where both not green and guess matches character.
        possible_idx = np.where(not_green & matching_spots)[0]
        # Make all of those indices up to cand_count yellow.
        squares[possible_idx[:cand_count]] = Square.YELLOW.value
    return squares


def is_match(guess: np.ndarray, candidate: np.ndarray, squares: np.ndarray):
    """
    Given a guess and response squares, decide if candidate matches.

    This function serves as validation for the pattern grid.
    """
    assert guess.ndim == candidate.ndim == squares.ndim == 1
    assert guess.shape == candidate.shape == squares.shape

    # Validate that all green square positions match.
    gm = squares == Square.GREEN.value
    if np.any(guess[gm] != candidate[gm]):
        return False

    # 1. The yellow masking must not create matches positionally.
    # 2. Assuming (1) is checked, the yellow guess letters are a
    # multi-subset of the non-green candidate letters.
    ym = squares == Square.YELLOW.value
    if np.any(guess[ym] == candidate[ym]):
        return False
    # pylint: disable-next=unnecessary-negation
    if not Counter(guess[ym]) <= Counter(candidate[~gm]):
        return False

    # 1. The black masking must not create matches positionally.
    # 2. The black guess letters that do not appear in yellow positions
    # must not be contained in the non-green candidate letters.
    bm = squares == Square.BLACK.value
    if np.any(guess[bm] == candidate[bm]):
        return False
    non_yellow_blacks = set(guess[bm]) - set(guess[ym])
    candidate_non_greens = set(candidate[~gm])
    return not non_yellow_blacks.intersection(candidate_non_greens)


def compile_patterns(chars: np.ndarray):
    """Compile and cache pattern combinations for every pairing."""
    assert chars.ndim == 2
    num_words, word_len = chars.shape[0]
    patterns = np.empty((num_words, num_words, word_len), dtype=np.uint8)
    nested_for = product(enumerate(chars), repeat=2)
    for (idl, lhs), (idr, rhs) in tqdm(nested_for, total=num_words**2):
        squares = _wordle_compare(lhs, rhs)
        patterns[idl, idr, :] = squares
    np.save('patterns.npy', patterns)
