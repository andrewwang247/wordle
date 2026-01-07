"""
Wordle game engine that plays optimally.

Copyright 2026. Andrew Wang.
"""
import logging
from typing import List
import numpy as np
import pandas as pd
from constants import BEST_FIRST_GUESS
from game import Game
from ranking import Ranker

logger = logging.getLogger(__name__)

_STRATEGY_PHASE_SWITCH = 2


class Engine:
    """Wordle playing engine."""

    def __init__(self, words: np.ndarray, patterns: np.ndarray,
                 cache_first_guess: bool = True):
        """Construct with ranker to help decide next guess."""
        self.ranker = Ranker(words, patterns)
        self.cache_first_guess = cache_first_guess

        # Track the history of reachable counts and entropies
        reachable, uncertainty = self.ranker.remaining_state()
        self.reachable_hist: List[int] = [reachable]
        self.uncertainty_hist: List[float] = [uncertainty]

    def make_guess(self, round_num: int) -> str:
        """Decide on the optimal next guess."""
        if self.cache_first_guess and round_num == 0:
            logger.debug('Using cached first guess %s', BEST_FIRST_GUESS)
            return BEST_FIRST_GUESS
        remaining = np.sum(self.ranker.reachable)
        if remaining <= _STRATEGY_PHASE_SWITCH:
            logger.debug('Reached endgame. Choosing likely solution to win.')
            solutions, _ = self.ranker.likely_solutions()
            assert solutions.size > 0, 'Could not find likely solutions.'
            return solutions[0]
        logger.debug('Choosing highest entropy guess to prune state space.')
        guesses, _ = self.ranker.informative_guesses()
        assert guesses.size > 0, 'Could not find informative guesses.'
        return guesses[0]

    def feedback(self, guess: str, squares: str):
        """Update internal state with guess and squares result."""
        assert len(guess) == len(squares), \
            f'Mismatch in guess {len(guess)} and square {len(squares)} lengths'
        self.ranker.update(guess, squares)
        reachable, uncertainty = self.ranker.remaining_state()
        logger.info('Reduced possibilities by %d words',
                    self.reachable_hist[-1] - reachable)
        logger.info('Reduced uncertainty by %.2f bits',
                    self.uncertainty_hist[-1] - uncertainty)
        self.reachable_hist.append(reachable)
        self.uncertainty_hist.append(uncertainty)

    def log_assistance(self, infolen: int):
        """Log ranked guesses and solutions to assist player."""
        possible, freqs = self.ranker.likely_solutions()
        pos_df = pd.DataFrame(index=pd.Index(possible, name='possible'),
                              data=freqs, columns=['log_freq'])
        logger.info('\n%s', pos_df[:infolen])

        guesses, entrops = self.ranker.informative_guesses()
        gs_df = pd.DataFrame(index=pd.Index(guesses, name='guesses'),
                             data=np.round(entrops, 3), columns=['entropy'])
        logger.info('\n%s', gs_df[:infolen])

    def simulate(self, solution: str) -> Game:
        """Simulate playing with defined solution. Return constructed game."""
        self.reset()
        logger.info('Simulating engine game with solution %s', solution)
        game = Game(self.ranker.words, self.ranker.patterns)
        game.set_solution(solution)
        while True:
            guess = self.make_guess(game.current_round())
            squares, is_win = game.guess(guess)
            if is_win:
                break
            self.feedback(guess, squares)
        return game

    def reset(self):
        """Reset the internal state for a new game."""
        logger.debug('Resetting engine state')
        self.ranker.reset()
        # Initial item in reachable and uncertainty history remains constant
        self.reachable_hist = self.reachable_hist[:1]
        self.uncertainty_hist = self.uncertainty_hist[:1]
