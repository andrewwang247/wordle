"""
Base Wordle game framework.

Copyright 2026. Andrew Wang.
"""
import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class Wordle:
    """Basic framework for playing a game."""

    def __init__(self, words: np.ndarray, patterns: np.ndarray, solution: str):
        """Initialize game with a fixed solution."""
        # Fast way to index given a word.
        self.index = pd.Index(words)  # (n,)
        assert solution in self.index, \
            f'Solution {solution} is not in dictionary.'
        self.solution = solution

        idx = self.index.get_loc(solution)
        self.squares = patterns[:, idx]  # (n,)
        logger.info('Initialized Wordle game with solution %s', solution)

    def guess(self, word: str) -> str:
        """Process a guess and return the square combo."""
        assert word in self.index, f'Guess {word} is not in dictionary.'
        idx = self.index.get_loc(word)
        result = str(self.squares[idx])
        logger.info('Guessed %s with result %s', word, result)
        return result
