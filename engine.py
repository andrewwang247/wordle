"""
Wordle game operations engine.

Copyright 2026. Andrew Wang.
"""
import logging
import re
from os import cpu_count
from collections import Counter
from enum import Enum
from itertools import product
import numpy as np
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class Square(Enum):
    """Define square colors and their unicode representations."""

    BLACK = ord('\U00002B1B')
    YELLOW = ord('\U0001F7E8')
    GREEN = ord('\U0001F7E9')


class WordleEngine:
    """Wordle game operations engine."""

    def __init__(self, fname: str, word_len: int):
        """Import and validate words from file."""
        assert word_len > 0, 'Expected word length must be positive.'
        line_pattern = re.compile(rf'\S{{{word_len}}}')
        re_vec = np.vectorize(line_pattern.fullmatch)
        words = np.loadtxt(fname, dtype=str)
        assert np.all(re_vec(words)), \
            f'All words must be {word_len} non whitespace characters'
        assert words.dtype == f'<U{word_len}'

        chars = np.empty((words.shape[0], word_len), dtype=int)
        for idx, word in enumerate(words):
            chars[idx, :] = list(map(ord, word))

        self._word_len = word_len
        self._num_words = words.shape[0]
        self._words = words
        self._chars = chars
        self._df = pd.DataFrame(data=chars, index=words)
        logger.info(
            'Initialized engine with %d words of length %d',
            words.shape[0],
            word_len)
        
    def _compute_pattern(self, tup):
        """Closure to send to multiprocessign pool."""
        (idl, lhs), (idr, rhs) = tup
        self._patterns[idl, idr, :] = self.wordle_compare(lhs, rhs)

    def compile_patterns(self):
        """Compile and cache pattern combinations for every pairing."""
        self._patterns = np.empty(
            (self._num_words,
             self._num_words,
             self._word_len),
            dtype=int)

        
        nested_for = product(enumerate(self._chars), repeat=2)
        for (idl, lhs), (idr, rhs) in nested_for:
            squares = self.wordle_compare(lhs, rhs)
            self._patterns[idl, idr, :] = squares

        np.save('patterns.npy', self._patterns)

    def wordle_compare(
            self,
            guess: np.ndarray,
            answer: np.ndarray) -> np.ndarray:
        """Given a guess and an answer, generate the squares."""
        assert guess.ndim == answer.ndim == 1
        assert guess.shape == answer.shape
        squares = np.full_like(guess, Square.BLACK.value)

        # Green is the easiest case to handle by position.
        # The mask gm is used to remove them in further processing.
        not_green = guess != answer
        squares[~not_green] = Square.GREEN.value

        # We need to get the number (n) of times a guess letter in
        # a non-green spot occurs in expected. From there, we color
        # the first (up to) n occurences of the letter yellow in guess.
        for cand in np.unique(guess[not_green]):
            cand_count = np.count_nonzero(answer[not_green] == cand)
            for i in range(guess.shape[0]):
                if cand_count == 0:
                    break
                if squares[i] == Square.GREEN.value or guess[i] != cand:
                    continue
                squares[i] = Square.YELLOW.value
                cand_count -= 1
        return squares

    def is_match(
            self,
            guess: np.ndarray,
            candidate: np.ndarray,
            squares: np.ndarray):
        """Given a guess and response squares, decide if candidate matches."""
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
