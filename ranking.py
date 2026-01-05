"""
Rank solutions with log frequency and guesses with entropy.

Copyright 2026. Andrew Wang.
"""
from typing import Tuple
from functools import partial
import numpy as np
import pandas as pd
from wordfreq import zipf_frequency


class Ranking:
    """Stateful ranking that iteratively updates on new data."""

    def __init__(self, words: np.ndarray, patterns: np.ndarray):
        """Constructor with references to immutable data."""
        self.words = words # (n,)
        # Fast way to index given a word.
        self.index = pd.Index(words)
        self.patterns = patterns # (n, n)
        # Use masking to keep track of viable solutions
        self.reachable = np.ones_like(words, dtype=bool)
        self.log_freq = np.vectorize(partial(
            zipf_frequency, lang='en'), otypes=[float])

    def update(self, guess: str, squares: str):
        """Update internal state with guess and resultant squares."""
        idx = self.index.get_loc(guess)
        squares_non_match = self.patterns[idx, :] != squares
        self.reachable[squares_non_match] = False

    def solutions(self) -> Tuple[np.ndarray, np.ndarray]:
        """Rank the most likely solutions based on word frequency."""
        possible = self.words[self.reachable]
        frequencies = self.log_freq(possible)
        sorted_idx = np.argsort(frequencies)[::-1]
        return possible[sorted_idx], frequencies[sorted_idx]

    def guesses(self) -> np.ndarray:
        """Rank the probabilistic quality of guesses by entropy."""
        return np.array([])
