"""
Wordle game engine that plays optimally.

Copyright 2026. Andrew Wang.
"""
import logging
from typing import cast, List, Optional
from functools import partial
import numpy as np
import numpy.typing as npt
import pandas as pd
from wordfreq import zipf_frequency
from .constants import BEST_OPENER, BEST_TARGETED_OPENER
from .game import Game
from .ranking import Ranker

logger = logging.getLogger(__name__)

_STRATEGY_PHASE_SWITCH = 2


class Engine:
    """Wordle playing engine."""

    def __init__(self, words: npt.NDArray[np.str_],
                 patterns: npt.NDArray[np.str_],
                 targets: Optional[npt.NDArray[np.str_]] = None):
        """Construct with ranker to help decide next guess."""
        self.words = words
        self.targets = targets
        self.ranker = Ranker(words, patterns)

        logger.info('Retrieving Zipf frequency for words')
        freq_vec = np.vectorize(partial(
            zipf_frequency, lang='en'), otypes=[float])
        self.log_freq = pd.DataFrame(
            data=freq_vec(words),
            index=words,
            columns=['log_freq'])
        if targets is not None:
            self.ranker.manual_prune(targets)
            self.cached_opener = BEST_TARGETED_OPENER
        else:
            self.cached_opener = BEST_OPENER

        # Track the history of reachable counts and entropies
        reachable, uncertainty = self.ranker.remaining_state()
        self.reachable_hist: List[int] = [reachable]
        self.uncertainty_hist: List[float] = [uncertainty]

    def feedback(self, guess: str, squares: str) -> None:
        """Update internal state with guess and squares result."""
        assert len(guess) == len(squares), \
            f'Mismatched lengths: guess {len(guess)} and square {len(squares)}'
        self.ranker.update(guess, squares)
        reachable, uncertainty = self.ranker.remaining_state()
        possibilities_reduction = self.reachable_hist[-1] - reachable
        print(f'Reduced possibilities by {possibilities_reduction} words')
        uncertainty_reduction = self.uncertainty_hist[-1] - uncertainty
        print(f'Reduced uncertainty by {uncertainty_reduction:.2f} bits')
        self.reachable_hist.append(reachable)
        self.uncertainty_hist.append(uncertainty)

    def likely_solutions(self) -> pd.DataFrame:
        """Rank the most likely solutions based on word frequency."""
        possible = self.words[self.ranker.reachable]
        subset: pd.DataFrame = self.log_freq.loc[possible]  # type: ignore
        return subset.sort_values(by='log_freq', ascending=False)

    def log_assistance(self, infolen: int) -> None:
        """Log ranked guesses and solutions to assist player."""
        if infolen <= 0:
            logger.info('Infolen %d <= 0. Skip logging assistance.', infolen)
            return
        pos_df = self.likely_solutions()
        print('Likely solutions')
        print(pos_df[:infolen])
        guesses, entrops = self.ranker.informative_guesses()
        gs_df = pd.DataFrame(data=np.round(entrops, 3),
                             index=guesses, columns=['entropy'])
        print('Informative guesses')
        print(gs_df[:infolen])

    def simulate(self, solution: str) -> Game:
        """Simulate playing with defined solution. Return constructed game."""
        self.reset()
        announcement = 'Simulating engine game with solution'
        print('=' * (len(announcement) + 1 + len(solution)))
        print(f'{announcement} {solution}')
        game = Game(self.words, self.ranker.patterns)
        game.set_solution(solution)
        if self.targets is not None:
            assert solution in self.targets, \
                f'{solution} is not in provided targets sub-list'
            self.ranker.manual_prune(self.targets)
        while True:
            guess = self._make_guess(game.current_round())
            squares, is_win = game.guess_is_win(guess)
            if is_win:
                break
            self.feedback(guess, squares)
        return game

    def reset(self) -> None:
        """Reset the internal state for a new game."""
        logger.info('Resetting engine state')
        self.ranker.reset()
        # Initial item in reachable and uncertainty history remains constant
        self.reachable_hist = self.reachable_hist[:1]
        self.uncertainty_hist = self.uncertainty_hist[:1]

    def _make_guess(self, round_num: int) -> str:
        """Decide on the optimal next guess."""
        if round_num == 0:
            logger.info('Using cached opener to speed things up.')
            return self.cached_opener
        remaining = np.sum(self.ranker.reachable)
        if remaining <= _STRATEGY_PHASE_SWITCH:
            logger.info('Reached endgame. Choosing likely solution to win.')
            solutions = self.likely_solutions()
            assert solutions.size > 0, 'Could not find likely solutions.'
            return cast(str, solutions.index[0])
        logger.info('Choosing highest entropy guess to prune state space.')
        guesses = self.ranker.informative_guesses()[0]
        assert guesses.size > 0, 'Could not find informative guesses.'
        return cast(str, guesses[0])
