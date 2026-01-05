"""
Wordle game operations engine.

Copyright 2026. Andrew Wang.
"""
from os import path
import logging
import re
import numpy as np
import pandas as pd
from constants import SQUARE_ENCODING

logger = logging.getLogger(__name__)


_PATTERNS_NPZ = 'patterns.npz'


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
        # self._words = words
        self._chars = chars
        self._df = pd.DataFrame(data=chars, index=words)
        if path.exists(_PATTERNS_NPZ):
            logger.info('Loading pre-compiled patterns from %s', _PATTERNS_NPZ)
            self._patterns = SQUARE_ENCODING[np.load(_PATTERNS_NPZ)['arr_0']]
        else:
            logger.warning(
                'Did not find pre-compiled patterns - required for entropy features')
            logger.info(
                'Run "cat resources/* > patterns.npz" to make patterns available')
            self._patterns = None
        logger.info(
            'Initialized engine with %d words of length %d',
            words.shape[0],
            word_len)

    def lookup_pattern(self, guess: str, expected: str) -> np.ndarray:
        """Render squares as a colored series of blocks."""
        assert self._patterns is not None, \
            'Precompiled patterns are required for pattern lookup.'
        gs_idx = self._df.index.get_loc(guess)
        exp_idx = self._df.index.get_loc(expected)
        return self._patterns[gs_idx, exp_idx, :]
