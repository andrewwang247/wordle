"""
Rank solutions with log frequency and guesses with entropy.

Copyright 2026. Andrew Wang.
"""
import logging
from math import log2
from typing import Tuple
from collections import Counter
import numpy as np
import numpy.typing as npt
import pandas as pd
from scipy.stats import entropy

logger = logging.getLogger(__name__)


def _unroll_counts(row: npt.NDArray[np.str_]):
    """Convert a row into unique counts with zero padding."""
    unique_counts = np.array(list(Counter(row).values()), dtype=int)
    # Pad all to same length so we can apply along axis.
    amount_short = row.size - unique_counts.size
    padding = np.zeros(amount_short, dtype=int)
    return np.concatenate([unique_counts, padding])


class Ranker:
    """Stateful ranking that iteratively updates on new data."""

    def __init__(self, words: npt.NDArray[np.str_],
                 patterns: npt.NDArray[np.str_]):
        """Construct with references to immutable data."""
        self.words = words  # (n,)
        # Fast way to index given a word.
        self.index = pd.Index(words)
        self.patterns = patterns  # (n, n)
        # Use masking to keep track of viable solutions
        self.reachable: npt.NDArray[np.bool_] = np.ones_like(words, dtype=bool)

    def remaining_state(self) -> Tuple[int, float]:
        """Compute stats for the remaining reachable space."""
        total_reachable: int = np.sum(self.reachable)  # type: ignore
        logger.info('Remaining possiblities: %d words', total_reachable)
        uncertainty = 0. if total_reachable == 0 else log2(total_reachable)
        logger.info('Remaining uncertainty: %.2f bits', uncertainty)
        return total_reachable, uncertainty

    def update(self, guess: str, squares: str):
        """Update internal state with guess and squares result."""
        assert guess in self.index, f'{guess} is not in dictionary.'
        logger.debug('Updating internal state with new information')
        idx = self.index.get_loc(guess)
        squares_non_match = self.patterns[idx, :] != squares
        self.reachable[squares_non_match] = False

    def informative_guesses(self) -> \
            Tuple[npt.NDArray[np.str_], npt.NDArray[np.float64]]:
        """Rank the probabilistic quality of guesses by entropy (in bits)."""
        # All guesses (axis 0) are included. Exclude unreachable candidates.
        logger.debug('Sorting informative guesses by entropy')
        working_set = self.patterns[:, self.reachable]
        counts = np.apply_along_axis(_unroll_counts, 1, working_set)
        entropies: npt.NDArray[np.float64] \
            = entropy(counts, axis=1, base=2)  # type: ignore
        sorted_idx = np.argsort(entropies)[::-1]
        return self.words[sorted_idx], entropies[sorted_idx]

    def manual_prune(self, targets: npt.NDArray[np.str_]):
        """Mark all targets as not reachable."""
        logger.debug('Marking all target as unreachable')
        mask = np.isin(self.words, targets)
        self.reachable[~mask] = False

    def reset(self):
        """Reset the internal state to a clean slate."""
        logger.debug('Resetting ranker state')
        self.reachable = np.ones_like(self.words, dtype=bool)
