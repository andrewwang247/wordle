"""
Base Wordle game framework.

Copyright 2026. Andrew Wang.
"""
import logging
from typing import List, Optional, Tuple
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class Game:
    """Basic framework for playing Wordle."""

    def __init__(self, words: np.ndarray, patterns: np.ndarray):
        """Initialize game with references to immutable data and a solution."""
        # Fast way to index given a word.
        self.index = pd.Index(words)  # (n,)
        self.patterns = patterns

        # Null initialize parameters after we have a solution set
        self.solution: Optional[str] = None
        self.sol_idx = 0
        self.guess_hist: List[str] = []

    def set_solution(self, solution: str):
        """Initialize game with a given solution."""
        assert solution in self.index, \
            f'{solution} is not in dictionary.'
        self.solution = solution
        self.guess_hist = []
        solution_index = self.index.get_loc(solution)
        assert isinstance(solution_index, int)
        self.sol_idx = solution_index
        logger.debug('Initialized game with solution %s', solution)

    def current_turn(self) -> int:
        """Return the current turn number."""
        return len(self.guess_hist)

    def guess(self, word: str) -> Tuple[str, bool]:
        """Process a guess and return the square combo + win state."""
        assert self.solution is not None, 'Solution was not set.'
        assert word in self.index, f'{word} is not in dictionary.'
        self.guess_hist.append(word)
        gs_idx = self.index.get_loc(word)
        result = str(self.patterns[gs_idx, self.sol_idx])
        logger.info(
            'Turn %d: %s %s',
            self.current_turn(),
            word,
            result)
        is_win = word == self.solution
        if is_win:
            logger.info('Completed game in %d turns', self.current_turn())
        return result, is_win
