"""
Loading and caching data for words and patterns.

Precompute square responses for all pairings.

Copyright 2026. Andrew Wang.
"""
import logging
from typing import Tuple
from os import listdir, path
from shutil import copyfileobj
import numpy as np
import numpy.typing as npt
import pandas as pd
from tqdm import tqdm
from .constants import wordle_compare

logger = logging.getLogger(__name__)

_CHUNK_DIR = 'bin/'
_DICTIONARY_FILE = 'resources/words.txt'
_INITIAL_DATA_FILE = 'resources/initial_data.csv'
_PATTERN_ARCHIVE_FILE = 'resources/patterns.npz'
_PATTERN_CACHE_FILE = 'resources/patterns.npy'
_TARGETS_FILE = 'resources/targets.txt'


def _load_txt(fname: str) -> npt.NDArray[np.str_]:
    """Load words from a text file and validate properties."""
    words = np.loadtxt(fname, dtype=str)
    len_vec = np.vectorize(len, otypes=[int])
    unique_lens = np.unique(len_vec(words))
    assert unique_lens.size == 1, \
        f'Words in {fname} must have uniform length'
    assert np.unique(
        words).size == words.size, f'Words in {fname} must be unique'
    logger.debug('Loaded %d words of length %d from %s',
                 words.size, unique_lens[0], fname)
    return words


def load_words() -> Tuple[npt.NDArray[np.str_], npt.NDArray[np.str_]]:
    """Load the dictionary array (n,) and targets from words list."""
    words = _load_txt(_DICTIONARY_FILE)
    targets = _load_txt(_TARGETS_FILE)
    assert np.all(np.isin(targets, words)), 'Targets must be subset of words'
    return words, targets


def compile_patterns():
    """
    Compile and cache pattern combinations for every pairing.

    Save the output patterns to a compressed numpy archive.
    """
    words = load_words()[0]
    logger.debug('Cross compiling %d patterns for %d words',
                 words.size**2, words.size)
    cmp_pat = np.vectorize(wordle_compare, otypes=[str])
    with tqdm(total=words.size**2) as pbar:
        # Matrix multiply vectorization magic.
        patterns: npt.NDArray[np.str_] = cmp_pat(
            words[:, np.newaxis], words, pbar)
    logger.debug('Writing patterns to cache %s', _PATTERN_CACHE_FILE)
    np.save(_PATTERN_CACHE_FILE, patterns)
    logger.debug('Writing patterns to archive %s', _PATTERN_ARCHIVE_FILE)
    np.savez_compressed(_PATTERN_ARCHIVE_FILE, patterns)


def load_patterns() -> npt.NDArray[np.str_]:
    """Load already compiled patterns (n, n) from archive."""
    if path.exists(_PATTERN_CACHE_FILE):
        logger.debug('Loading pre-compiled cache %s', _PATTERN_CACHE_FILE)
        return np.load(_PATTERN_CACHE_FILE)
    logger.debug('No pattern cache %s found', _PATTERN_CACHE_FILE)

    if not path.exists(_PATTERN_ARCHIVE_FILE):
        logger.debug('No pattern archive %s found', _PATTERN_ARCHIVE_FILE)
        chunk_files = listdir(_CHUNK_DIR)
        assert chunk_files, \
            'Missing saved archive partitions. Run compile_patterns.'
        chunk_files.sort()

        logger.debug('Joining %d binary partitions from %s',
                     len(chunk_files), _CHUNK_DIR)
        with open(_PATTERN_ARCHIVE_FILE, 'wb') as fdst:
            for chunk in chunk_files:
                chunk_path = path.join(_CHUNK_DIR, chunk)
                with open(chunk_path, 'rb') as fsrc:
                    copyfileobj(fsrc, fdst)

    logger.debug('Loading pre-compiled archive %s', _PATTERN_ARCHIVE_FILE)
    patterns = np.load(_PATTERN_ARCHIVE_FILE)['arr_0']
    logger.debug('Writing patterns to cache %s', _PATTERN_CACHE_FILE)
    np.save(_PATTERN_CACHE_FILE, patterns)
    return patterns


def log_initial_assistance(infolen: int, targeted: bool):
    """Log cached opening guess assistance for player."""
    # Only runs once per session. Ok not to store.
    df = pd.read_csv(_INITIAL_DATA_FILE, index_col='word')

    # Attempt to match format of engine assistance.
    df.index.set_names(None, inplace=True)

    pos_df = df.sort_values(by='log_freq', ascending=False)
    if targeted:
        pos_df = pos_df.dropna()
    logger.info('Likely solutions\n%s',
                pd.DataFrame(pos_df.log_freq)[:infolen])

    key = 'entropy_targeted' if targeted else 'entropy'
    gs_df = df.sort_values(by=key, ascending=False)
    logger.info('Informative guesses\n%s',
                pd.DataFrame(np.round(gs_df[key], 3))[:infolen])
