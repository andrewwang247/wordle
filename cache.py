"""
Loading and caching data for words and patterns.

Precompute square responses for all pairings.

Copyright 2026. Andrew Wang.
"""
import logging
from os import listdir, path
from shutil import copyfileobj
import numpy as np
from tqdm import tqdm
from constants import wordle_compare

logger = logging.getLogger(__name__)

_CHUNK_DIR = 'bin/'
_DICTIONARY_FILE = 'resources/words.txt'
_PATTERN_ARCHIVE_FILE = 'resources/patterns.npz'
_PATTERN_CACHE_FILE = 'resources/patterns.npy'


def load_words() -> np.ndarray:
    """Load the dictionary array (n,) from words list."""
    words = np.loadtxt(_DICTIONARY_FILE, dtype=str)
    logger.info('Loaded %d words from %s', len(words), _DICTIONARY_FILE)
    len_vec = np.vectorize(len, otypes=[int])
    unique_lens = np.unique(len_vec(words))
    assert unique_lens.shape == (1,), \
        'Words in dictionary must have uniform length'
    logger.info('Validated all words have length %d', unique_lens[0])
    return words


def compile_patterns():
    """
    Compile and cache pattern combinations for every pairing.

    Save the output patterns to a compressed numpy archive.
    """
    words = load_words()
    num_words = len(words)
    logger.info('Cross compiling %d patterns for %d words',
                num_words**2, num_words)
    cmp_pat = np.vectorize(wordle_compare, otypes=[str])
    with tqdm(total=num_words**2) as pbar:
        # Matrix multiply vectorization magic.
        patterns: np.ndarray = cmp_pat(words[:, np.newaxis], words, pbar)
    logger.info('Writing patterns to cache %s', _PATTERN_CACHE_FILE)
    np.save(_PATTERN_CACHE_FILE, patterns)
    logger.info('Writing patterns to archive %s', _PATTERN_ARCHIVE_FILE)
    np.savez_compressed(_PATTERN_ARCHIVE_FILE, patterns)


def load_patterns() -> np.ndarray:
    """Load already compiled patterns (n, n) from archive."""
    if path.exists(_PATTERN_CACHE_FILE):
        logger.info('Loading pre-compiled cache %s', _PATTERN_CACHE_FILE)
        return np.load(_PATTERN_CACHE_FILE)
    logger.info('No pattern cache %s found', _PATTERN_CACHE_FILE)

    if not path.exists(_PATTERN_ARCHIVE_FILE):
        logger.info('No pattern archive %s found', _PATTERN_ARCHIVE_FILE)
        chunk_files = listdir(_CHUNK_DIR)
        assert chunk_files, \
            'Missing saved archive partitions. Run compile_patterns.'
        chunk_files.sort()

        logger.info('Joining %d binary chunks from %s',
                    len(chunk_files), _CHUNK_DIR)
        with open(_PATTERN_ARCHIVE_FILE, 'wb') as fdst:
            for chunk in chunk_files:
                chunk_path = path.join(_CHUNK_DIR, chunk)
                with open(chunk_path, 'rb') as fsrc:
                    copyfileobj(fsrc, fdst)

    logger.info('Loading pre-compiled archive %s', _PATTERN_ARCHIVE_FILE)
    patterns = np.load(_PATTERN_ARCHIVE_FILE)['arr_0']
    logger.info('Writing patterns to cache %s', _PATTERN_CACHE_FILE)
    np.save(_PATTERN_CACHE_FILE, patterns)
    return patterns
