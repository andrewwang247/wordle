"""
Rank solutions with log frequency and guesses with entropy.

Copyright 2026. Andrew Wang.
"""
import logging
from math import log2
from typing import Tuple
from functools import partial
from collections import Counter
import numpy as np
import pandas as pd
from scipy.stats import entropy
from wordfreq import zipf_frequency

logger = logging.getLogger(__name__)


def _unroll_counts(row: np.ndarray):
    """Convert a row into unique counts with zero padding."""
    unique_counts = np.array(list(Counter(row).values()), dtype=int)
    # Pad all to same length so we can apply along axis.
    amount_short = len(row) - len(unique_counts)
    padding = np.zeros(amount_short, dtype=int)
    return np.concatenate([unique_counts, padding])


class Ranking:
    """Stateful ranking that iteratively updates on new data."""

    def __init__(self, words: np.ndarray, patterns: np.ndarray):
        """Constructor with references to immutable data."""
        self.words = words  # (n,)
        # Fast way to index given a word.
        self.index = pd.Index(words)
        self.patterns = patterns  # (n, n)
        # Use masking to keep track of viable solutions
        self.reachable = np.ones_like(words, dtype=bool)
        self.log_freq = np.vectorize(partial(
            zipf_frequency, lang='en'), otypes=[float])
        self._log_state()

    def _log_state(self):
        """Compute the internal entropy of the reachable space."""
        total_reachable = np.sum(self.reachable)
        logger.info('Possibilities: %d', total_reachable)
        space_bits = 0 if total_reachable == 0 else log2(total_reachable)
        logger.info('Entropy: %.2f', space_bits)

    def update(self, guess: str, squares: str):
        """Update internal state with guess and squares result."""
        logger.info('Guessed %s with result %s', guess, squares)
        idx = self.index.get_loc(guess)
        squares_non_match = self.patterns[idx, :] != squares
        self.reachable[squares_non_match] = False
        self._log_state()

    def likely_solutions(self) -> Tuple[np.ndarray, np.ndarray]:
        """Rank the most likely solutions based on word frequency."""
        possible = self.words[self.reachable]
        frequencies = self.log_freq(possible)
        sorted_idx = np.argsort(frequencies)[::-1]
        return possible[sorted_idx], frequencies[sorted_idx]

    def informative_guesses(self) -> Tuple[np.ndarray, np.ndarray]:
        """Rank the probabilistic quality of guesses by entropy (in bits)."""
        # All guesses (axis 0) are included. Exclude unreachable candidates.
        working_set = self.patterns[:, self.reachable]
        counts = np.apply_along_axis(_unroll_counts, 1, working_set)
        entropies: np.ndarray = entropy(counts, axis=1, base=2)  # type: ignore
        sorted_idx = np.argsort(entropies)[::-1]
        return self.words[sorted_idx], entropies[sorted_idx]
