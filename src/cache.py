"""Loading and caching data for words and patterns.

Precompute square responses for all pairings.

Copyright 2026. Andrew Wang.
"""

import logging
from pathlib import Path
from shutil import copyfileobj
from typing import cast

import numpy as np
import pandas as pd
from tqdm import tqdm

from .constants import StrArr, StrGrid, wordle_compare

logger = logging.getLogger(__name__)

_CHUNK_DIR = Path("bin/")
_RESOURCE_DIR = Path("resources/")
_DICTIONARY_FILE = _RESOURCE_DIR / "words.txt"
_INITIAL_DATA_FILE = _RESOURCE_DIR / "initial_data.csv"
_PATTERN_ARCHIVE_FILE = _RESOURCE_DIR / "patterns.npz"
_PATTERN_CACHE_FILE = _RESOURCE_DIR / "patterns.npy"
_TARGETS_FILE = _RESOURCE_DIR / "targets.txt"


def _load_txt(fpath: Path) -> StrArr:
    """Load words from a text file and validate properties."""
    words = np.loadtxt(fpath, dtype=str)
    len_vec = np.vectorize(len, otypes=[int])
    unique_lens = np.unique(len_vec(words))
    assert unique_lens.size == 1, f"Words in {fpath} must have uniform length"
    assert np.unique(words).size == words.size, f"Words in {fpath} must be unique"
    logger.info(
        "Loaded %d words of length %d from %s",
        words.size,
        unique_lens[0],
        fpath,
    )
    return words


def load_words() -> tuple[StrArr, StrArr]:
    """Load the dictionary array (n,) and targets from words list."""
    words = _load_txt(_DICTIONARY_FILE)
    targets = _load_txt(_TARGETS_FILE)
    assert np.all(np.isin(targets, words)), "Targets must be subset of words"
    return words, targets


def compile_patterns() -> None:
    """Compile and cache pattern combinations for every pairing.

    Save the output patterns to a compressed numpy archive.
    """
    words = load_words()[0]
    logger.info("Cross compiling %d patterns for %d words", words.size**2, words.size)
    cmp_pat = np.vectorize(wordle_compare, otypes=[str])
    with tqdm(total=words.size**2) as pbar:
        # Matrix multiply vectorization magic.
        patterns: StrGrid = cmp_pat(words[:, np.newaxis], words, pbar)
    logger.info("Writing patterns to cache %s", _PATTERN_CACHE_FILE)
    np.save(_PATTERN_CACHE_FILE, patterns)
    logger.info("Writing patterns to archive %s", _PATTERN_ARCHIVE_FILE)
    np.savez_compressed(_PATTERN_ARCHIVE_FILE, patterns)


def load_patterns() -> StrGrid:
    """Load already compiled patterns (n, n) from archive."""
    if _PATTERN_CACHE_FILE.exists():
        logger.info("Loading pre-compiled cache %s", _PATTERN_CACHE_FILE)
        return cast("StrGrid", np.load(_PATTERN_CACHE_FILE))
    logger.info("No pattern cache %s found", _PATTERN_CACHE_FILE)

    if not _PATTERN_ARCHIVE_FILE.exists():
        logger.info("No pattern archive %s found", _PATTERN_ARCHIVE_FILE)
        chunk_files = list(_CHUNK_DIR.iterdir())
        assert chunk_files, "Missing saved archive partitions. Run compile_patterns."
        chunk_files.sort()

        logger.info(
            "Joining %d binary partitions from %s",
            len(chunk_files),
            _CHUNK_DIR,
        )
        with _PATTERN_ARCHIVE_FILE.open("wb") as fdst:
            for chunk in chunk_files:
                with chunk.open("rb") as fsrc:
                    copyfileobj(fsrc, fdst)

    logger.info("Loading pre-compiled archive %s", _PATTERN_ARCHIVE_FILE)
    patterns = cast("StrGrid", np.load(_PATTERN_ARCHIVE_FILE)["arr_0"])
    logger.info("Writing patterns to cache %s", _PATTERN_CACHE_FILE)
    np.save(_PATTERN_CACHE_FILE, patterns)
    return patterns


def log_initial_assistance(infolen: int, *, targeted: bool) -> None:
    """Log cached opening guess assistance for player."""
    # Only runs once per session. Ok not to store.
    df = pd.read_csv(_INITIAL_DATA_FILE, index_col="word")

    # Attempt to match format of engine assistance.
    df.index = df.index.set_names(None)

    pos_df = df.sort_values(by="log_freq", ascending=False)
    if targeted:
        pos_df = pos_df.dropna()
    print("Likely solutions")
    print(pd.DataFrame(pos_df.log_freq)[:infolen])

    key = "entropy_targeted" if targeted else "entropy"
    gs_df = df.sort_values(by=key, ascending=False)
    print("Informative guesses")
    print(pd.DataFrame(np.round(gs_df[key], 3))[:infolen])
