"""
Wordle engine that plays optimally.

Copyright 2026. Andrew Wang.
"""
import logging
import numpy as np
from ranking import Ranking

_BEST_FIRST_GUESS = 'tares'

logger = logging.getLogger(__name__)


class Engine:
    """Wordle playing engine."""

    def __init__(self, words: np.ndarray, patterns: np.ndarray,
                 cache_first_guess: bool = True):
        """Construct with references to immutable data."""
        self.words = words  # (n,)
        self.patterns = patterns  # (n, n)

        self.cache_first_guess = cache_first_guess
        self.ranker = Ranking(words, patterns)

    def make_guess(self, turn: int) -> str:
        """Return the optimal next guess."""
        if self.cache_first_guess and turn == 0:
            logger.info('Using cached first guess %s', _BEST_FIRST_GUESS)
            return _BEST_FIRST_GUESS
        reachable, _ = self.ranker.remaining_state()
        if reachable <= 3:
            logger.info('Reached endgame. Choosing likely solution to win.')
            solutions, _ = self.ranker.likely_solutions()
            assert solutions.size > 0, 'Could not find likely solutions.'
            return solutions[0]
        logger.info('Choosing highest entropy guess to prune state space.')
        guesses, _ = self.ranker.informative_guesses()
        assert guesses.size > 0, 'Could not find informative guesses.'
        return guesses[0]

    def feedback(self, guess: str, squares: str):
        """Update internal state with guess and squares result."""
        self.ranker.update(guess, squares)
