"""
Wordle game engine that plays optimally.

Copyright 2026. Andrew Wang.
"""
import logging
from typing import List
from functools import partial
import numpy as np
import numpy.typing as npt
import pandas as pd
from wordfreq import zipf_frequency
from constants import BEST_FIRST_GUESS, DEFAULT_LANGUAGE
from game import Game
from ranking import Ranker

logger = logging.getLogger(__name__)

_STRATEGY_PHASE_SWITCH = 2


class Engine:
    """Wordle playing engine."""

    def __init__(self, words: npt.NDArray[np.str_],
                 patterns: npt.NDArray[np.str_],
                 cache_first_guess: bool = True):
        """Construct with ranker to help decide next guess."""
        self.words = words
        self.ranker = Ranker(words, patterns)
        self.cache_first_guess = cache_first_guess
        logger.debug('Retrieving Zipf frequency for words')
        freq_vec = np.vectorize(partial(
            zipf_frequency, lang=DEFAULT_LANGUAGE), otypes=[float])
        self.log_freq = pd.DataFrame(
            data=freq_vec(words),
            index=words,
            columns=['log_freq'])

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
            solutions = self.likely_solutions()
            assert solutions.size > 0, 'Could not find likely solutions.'
            return solutions.index[0]
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

    def likely_solutions(self) -> pd.DataFrame:
        """Rank the most likely solutions based on word frequency."""
        possible = self.ranker.still_reachable()
        subset: pd.DataFrame = self.log_freq.loc[possible]  # type: ignore
        return subset.sort_values(by='log_freq', ascending=False)

    def log_assistance(self, infolen: int):
        """Log ranked guesses and solutions to assist player."""
        pos_df = self.likely_solutions()
        logger.info('Likely solutions\n%s', pos_df[:infolen])

        guesses, entrops = self.ranker.informative_guesses()
        gs_df = pd.DataFrame(data=np.round(entrops, 3),
                             index=guesses, columns=['entropy'])
        logger.info('Informative guesses\n%s', gs_df[:infolen])

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
