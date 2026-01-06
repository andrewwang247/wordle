"""
Wordle game engine that plays optimally.

Copyright 2026. Andrew Wang.
"""
import logging
from typing import List
from game import Game
from ranking import Ranker

_BEST_FIRST_GUESS = 'tares'

logger = logging.getLogger(__name__)


class Engine:
    """Wordle playing engine."""

    def __init__(self, ranker: Ranker,
                 cache_first_guess: bool = True):
        """Construct with ranker to help decide next guess."""
        self.ranker = ranker
        self.cache_first_guess = cache_first_guess

        # Track the history of reachable counts and entropies
        reachable, entropy = self.ranker.remaining_state()
        self.reachable_hist: List[int] = [reachable]
        self.entropy_hist: List[float] = [entropy]

    def make_guess(self, turn: int) -> str:
        """Return the optimal next guess."""
        if self.cache_first_guess and turn == 0:
            logger.info('Using cached first guess %s', _BEST_FIRST_GUESS)
            return _BEST_FIRST_GUESS
        reachable = self.ranker.still_reachable()
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
        reachable, entropy = self.ranker.remaining_state()
        logger.info('Reduced reachable words by %d',
                    self.reachable_hist[-1] - reachable)
        logger.info('Reduced entropy by %.2f', self.entropy_hist[-1] - entropy)
        self.reachable_hist.append(reachable)
        self.entropy_hist.append(entropy)

    def reset(self):
        """Reset the internal state for a new game."""
        self.ranker.reset()
        # Initial item in reachable and entropy history remains constant
        self.reachable_hist = self.reachable_hist[:1]
        self.entropy_hist = self.entropy_hist[:1]

    def simulate(self, solution: str) -> List[str]:
        """Simulate a game with a given solution. Return guess history."""
        game = Game(self.ranker.words, self.ranker.patterns)
        game.set_solution(solution)
        while True:
            guess = self.make_guess(game.current_turn())
            squares, is_win = game.guess(guess)
            if is_win:
                break
            self.feedback(guess, squares)
        return game.guess_hist
