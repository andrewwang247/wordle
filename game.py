"""
Base Wordle game framework.

Copyright 2026. Andrew Wang.
"""
import logging
from typing import Tuple
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class Wordle:
    """Basic framework for playing a game."""

    def __init__(self, words: np.ndarray, patterns: np.ndarray, solution: str):
        """Initialize game with references to immutable data and a solution."""
        # Fast way to index given a word.
        self.index = pd.Index(words)  # (n,)
        assert solution in self.index, \
            f'Solution {solution} is not in dictionary.'
        self.solution = solution

        idx = self.index.get_loc(solution)
        self.squares = patterns[:, idx]  # (n,)
        logger.info('Initialized Wordle game with solution %s', solution)

    def guess(self, word: str) -> Tuple[str, bool]:
        """Process a guess and return the square combo and if win."""
        assert word in self.index, f'Guess {word} is not in dictionary.'
        idx = self.index.get_loc(word)
        result = str(self.squares[idx])
        logger.info('Guessed %s with result %s', word, result)
        return result, word == self.solution
