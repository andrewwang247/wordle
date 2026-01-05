"""
Loading and caching data for words and patterns.
Precompute square responses for all pairings.

Copyright 2026. Andrew Wang.
"""
import logging
import numpy as np
from tqdm import tqdm
from constants import Square

logger = logging.getLogger(__name__)

_DICTIONARY_FILE = 'words.txt'
_PATTERN_CACHE_FILE = 'patterns.npz'


def load_words() -> np.ndarray:
    """Load the dictionary array (n,) from words list."""
    words = np.loadtxt(_DICTIONARY_FILE, dtype=str)
    logger.info('Loaded %d words from %s', len(words), _DICTIONARY_FILE)
    return words


@np.vectorize
def _wordle_compare(guess: str, answer: str, pbar: tqdm) -> str:
    """
    Given a guess and an answer, generate the squares pattern.

    This runs in a very tight vectorized loop during compilation.
    """
    guess_np = np.array(list(guess))
    answer_np = np.array(list(answer))
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

    pbar.update(1)
    return ''.join(squares)


def compile_patterns():
    """
    Compile and cache pattern combinations for every pairing.

    Save the output patterns to a compressed numpy archive.
    """
    words = load_words()
    num_words = len(words)
    logger.info('Cross compiling %d patterns for %d words',
                num_words**2, num_words)
    with tqdm(total=num_words**2) as pbar:
        # Matrix multiply vectorization magic.
        patterns: np.ndarray = _wordle_compare(
            words[:, np.newaxis], words, pbar)
    logger.info('Writing patterns to %s', _PATTERN_CACHE_FILE)
    np.savez_compressed(_PATTERN_CACHE_FILE, patterns)


def load_patterns() -> np.ndarray:
    """Load already compiled patterns (n, n) from archive."""
    logger.info('Loading pre-compiled patterns from %s', _PATTERN_CACHE_FILE)
    return np.load(_PATTERN_CACHE_FILE)['arr_0']
