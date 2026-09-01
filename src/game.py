"""Base Wordle game framework.

Copyright 2026. Andrew Wang.
"""

import logging

import numpy as np
import numpy.typing as npt
import pandas as pd

from .constants import SQUARE_VALUES, Square

logger = logging.getLogger(__name__)


class Game:
    """Basic framework for playing Wordle."""

    def __init__(
        self,
        words: npt.NDArray[np.str_],
        patterns: npt.NDArray[np.str_],
    ) -> None:
        """Initialize game with references to immutable data and a solution."""
        # Fast way to index given a word.
        self.index = pd.Index(words)  # (n,)
        self.patterns = patterns

        # Null initialize parameters after we have a solution set
        self.solution: str | None = None
        self.sol_idx = 0
        self.guess_hist: list[str] = []
        self.square_hist: list[str] = []

    def set_solution(self, solution: str | None = None) -> None:
        """Initialize game with a given (or random) solution."""
        if solution is None:
            rng = np.random.default_rng()
            self.solution = rng.choice(self.index)
        else:
            assert solution in self.index, f"{solution} is not in dictionary."
            self.solution = solution

        self.guess_hist = []
        solution_index = self.index.get_loc(self.solution)
        assert isinstance(solution_index, int), (
            f"Unexpected type {type(solution_index)} from pandas index"
        )
        self.sol_idx = solution_index
        logger.info("Initialized game with solution %s", self.solution)

    def current_round(self) -> int:
        """Return the current round number."""
        return len(self.guess_hist)

    def append_is_win(self, word: str, squares: str) -> bool:
        """Process a guess and response. Return if this is a win."""
        assert word in self.index, f"{word} is not in dictionary."
        assert len(word) == len(squares), (
            f"Mismatched lengths: guess {len(word)} and square {len(squares)}"
        )
        assert all(sq in SQUARE_VALUES for sq in squares), (
            f"{squares} is an invalid square string"
        )
        self.guess_hist.append(word)
        self.square_hist.append(squares)
        round_number = self.current_round()
        print(f"Round {round_number}: {word} {squares}")
        is_win = all(sq == Square.GREEN.value for sq in squares)
        if not is_win:
            return False
        if self.solution is not None:
            assert word == self.solution, (
                f"Word {word} does not match solution {self.solution}."
            )
        print(f"Completed game in {round_number} rounds")
        return True

    def guess_is_win(self, word: str) -> tuple[str, bool]:
        """Process a guess and return the square combo + win state."""
        assert self.solution is not None, "Solution was not set."
        assert word in self.index, f"{word} is not in dictionary."
        gs_idx = self.index.get_loc(word)
        result = str(self.patterns[gs_idx, self.sol_idx])
        is_win = self.append_is_win(word, result)
        return result, is_win
