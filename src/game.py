"""
Base Wordle game framework.

Copyright 2026. Andrew Wang.
"""
import logging
from typing import List, Optional, Tuple
import numpy as np
import numpy.typing as npt
import pandas as pd
from .constants import Square, SQUARE_VALUES

logger = logging.getLogger(__name__)


class Game:
    """Basic framework for playing Wordle."""

    def __init__(self, words: npt.NDArray[np.str_],
                 patterns: npt.NDArray[np.str_]):
        """Initialize game with references to immutable data and a solution."""
        # Fast way to index given a word.
        self.index = pd.Index(words)  # (n,)
        self.patterns = patterns

        # Null initialize parameters after we have a solution set
        self.solution: Optional[str] = None
        self.sol_idx = 0
        self.guess_hist: List[str] = []
        self.square_hist: List[str] = []

    def set_solution(self, solution: Optional[str] = None):
        """Initialize game with a given (or random) solution."""
        if solution is None:
            self.solution = np.random.choice(self.index)
        else:
            assert solution in self.index, \
                f'{solution} is not in dictionary.'
            self.solution = solution

        self.guess_hist = []
        solution_index = self.index.get_loc(self.solution)
        assert isinstance(solution_index, int), \
            f'Unexpected type {type(solution_index)} from pandas index'
        self.sol_idx = solution_index
        logger.debug('Initialized game with solution %s', self.solution)

    def current_round(self) -> int:
        """Return the current round number."""
        return len(self.guess_hist)

    def append(self, word: str, squares: str) -> bool:
        """Process a guess and response. Return if this is a win."""
        assert word in self.index, f'{word} is not in dictionary.'
        assert all(sq in SQUARE_VALUES for sq in squares), \
            f'{squares} is an invalid square string'
        self.guess_hist.append(word)
        self.square_hist.append(squares)
        logger.info(
            'Round %d: %s %s',
            self.current_round(),
            word,
            squares)
        return all(sq == Square.GREEN.value for sq in squares)

    def guess(self, word: str) -> Tuple[str, bool]:
        """Process a guess and return the square combo + win state."""
        assert self.solution is not None, 'Solution was not set.'
        assert word in self.index, f'{word} is not in dictionary.'
        gs_idx = self.index.get_loc(word)
        result = str(self.patterns[gs_idx, self.sol_idx])
        self.append(word, result)
        is_win = word == self.solution
        if is_win:
            logger.info('Completed game in %d rounds', self.current_round())
        return result, is_win
