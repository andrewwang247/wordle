"""Loading and caching data for words and patterns.

Precompute square responses for all pairings.

Copyright 2026. Andrew Wang.
"""

import logging
import subprocess
from pathlib import Path
from shutil import copyfileobj, which
from typing import cast

import numpy as np
import pandas as pd
from tqdm import tqdm

from .constants import ByteArr, ByteGrid, wordle_compare

logger = logging.getLogger(__name__)

_CHUNK_DIR = Path("archive")
_RESOURCE_DIR = Path("resources")
_PATTERN_ARCHIVE_FILE = _RESOURCE_DIR / "patterns.npz"
_PATTERN_CACHE_FILE = _RESOURCE_DIR / "patterns.npy"
_NATIVE_BINARY = Path("build/patterns")


def _load_txt(fpath: Path) -> ByteArr:
    """Load words from a text file and validate properties."""
    words = np.loadtxt(fpath, dtype=np.bytes_)
    len_vec = np.vectorize(len, otypes=[np.int_])
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


def load_words() -> ByteArr:
    """Load the dictionary array (n,) and targets from words list."""
    return _load_txt(_RESOURCE_DIR / "words.txt")


def load_targets() -> ByteArr:
    """Load the targets subset (n,) from targets list."""
    return _load_txt(_RESOURCE_DIR / "targets.txt")


def load_patterns() -> ByteGrid:
    """Load already compiled patterns (n, n) from archive."""
    if _PATTERN_CACHE_FILE.exists():
        logger.info("Loading pre-compiled cache %s", _PATTERN_CACHE_FILE)
        return cast("ByteGrid", np.load(_PATTERN_CACHE_FILE))
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
    patterns = cast("ByteGrid", np.load(_PATTERN_ARCHIVE_FILE)["arr_0"])
    logger.info("Writing patterns to cache %s", _PATTERN_CACHE_FILE)
    np.save(_PATTERN_CACHE_FILE, patterns)
    return patterns


def log_initial_assistance(infolen: int, *, targeted: bool) -> None:
    """Log cached opening guess assistance for player."""
    # Only runs once per session. Ok not to store.
    df = pd.read_csv(_RESOURCE_DIR / "initial_data.csv", index_col="word")

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


def build_patterns_py(words: ByteArr, *, archive: bool = False) -> None:
    """Build and cache pattern combinations for every pairing - Python version.

    Save patterns to numpy cache and optional compressed archive.
    """
    logger.info("Cross compiling %d patterns for %d words", words.size**2, words.size)
    cmp_pat = np.vectorize(wordle_compare, otypes=[np.bytes_])
    with tqdm(total=words.size**2) as pbar:
        # Matrix multiply vectorization magic.
        patterns: ByteGrid = cmp_pat(words[:, np.newaxis], words, pbar)
    logger.info("Writing patterns to cache %s", _PATTERN_CACHE_FILE)
    np.save(_PATTERN_CACHE_FILE, patterns)
    if archive:
        logger.info("Writing patterns to archive %s", _PATTERN_ARCHIVE_FILE)
        np.savez_compressed(_PATTERN_ARCHIVE_FILE, patterns)


def build_patterns_native(word_file: Path, *, archive: bool = False) -> None:
    """Build and cache pattern combinations for every pairing - Native version.

    Save patterns to numpy cache and optional compressed archive.
    """
    if not _NATIVE_BINARY.exists():
        logger.info("Binary %s not found. Building with Makefile.", _NATIVE_BINARY)
        make_release = which("make")
        assert make_release, "Make is not installed on system."
        subprocess.run([make_release], check=True)
    assert _NATIVE_BINARY.exists()
    logger.info("Cross compiling patterns for dictionary %s", word_file)
    subprocess.run([_NATIVE_BINARY, word_file, _PATTERN_CACHE_FILE], check=True)
    logger.info("Finished writing patterns to cache %s", _PATTERN_CACHE_FILE)
    if archive:
        patterns: ByteGrid = np.load(_PATTERN_CACHE_FILE)
        logger.info("Writing patterns to archive %s", _PATTERN_ARCHIVE_FILE)
        np.savez_compressed(_PATTERN_ARCHIVE_FILE, patterns)
