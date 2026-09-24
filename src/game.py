"""Base Wordle game framework.

Copyright 2026. Andrew Wang.
"""

import logging
from typing import cast

import numpy as np
import pandas as pd

from .constants import ByteArr, ByteGrid, convert_squares

logger = logging.getLogger(__name__)

_RNG = np.random.default_rng()


class Game:
    """Basic framework for playing Wordle."""

    def __init__(
        self, words: ByteArr, patterns: ByteGrid, targets: ByteArr | None = None
    ) -> None:
        """Initialize game with references to immutable data and a solution."""
        # Fast way to index given a word.
        self.index = pd.Index(words)  # (n,)
        self.patterns = patterns
        self.targets = targets

        # Null initialize parameters after we have a solution set
        self.solution: bytes | None = None
        self.sol_idx = 0
        self.guess_hist: list[bytes] = []
        self.square_hist: list[bytes] = []

    def set_solution(self, solution: bytes | None = None) -> None:
        """Initialize game with a given (or random) solution."""
        container = self.index if self.targets is None else self.targets
        cname = "dictionary" if self.targets is None else "targets"
        if solution:
            assert solution in container, f"{solution.decode()} is not in {cname}."
            self.solution = solution
        else:
            self.solution = _RNG.choice(container)

        solution_index = self.index.get_loc(self.solution)
        assert isinstance(solution_index, int), (
            f"Unexpected type {type(solution_index)} from pandas index"
        )
        self.sol_idx = solution_index
        logger.info("Initialized game with solution %s", self.solution)

    def current_round(self) -> int:
        """Return the current round number."""
        return len(self.guess_hist)

    def reset(self) -> None:
        """Reset game history. Retain solution if set."""
        self.guess_hist.clear()
        self.square_hist.clear()

    def append_is_win(self, word: bytes, squares: bytes) -> bool:
        """Process a guess and response. Return if this is a win."""
        assert word in self.index, f"{word.decode()} is not in dictionary."
        assert len(word) == len(squares), (
            f"Mismatched lengths: guess {len(word)} and square {len(squares)}"
        )
        assert all(sq in {ord("g"), ord("y"), ord("b")} for sq in squares), (
            f"{squares.decode()} is an invalid pattern"
        )
        self.guess_hist.append(word)
        self.square_hist.append(squares)
        round_number = self.current_round()
        print(f"Round {round_number}: {word.decode()} {convert_squares(squares)}")
        if is_win := all(sq == ord("g") for sq in squares):
            if sol := self.solution:
                assert word == sol, f"{word.decode()} does not match {sol.decode()}."
            else:
                self.set_solution(word)
            print(f"Completed game in {round_number} rounds")
        return is_win

    def guess_is_win(self, word: bytes) -> tuple[bytes, bool]:
        """Process a guess and return the square combo + win state."""
        assert self.solution, "Solution was not defined."
        assert word in self.index, f"{word.decode()} is not in dictionary."
        gs_idx = self.index.get_loc(word)
        result = cast("bytes", self.patterns[gs_idx, self.sol_idx])
        return result, self.append_is_win(word, result)
