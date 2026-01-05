"""
Basic Wordle square enumeration.

Copyright 2026. Andrew Wang.
"""
from enum import Enum
import numpy as np


class Square(Enum):
    """Define square colors and their index representation."""

    BLACK = 0
    YELLOW = 1
    GREEN = 2


# Unicode encoding of each square
SQUARE_ENCODING = np.array(['\U00002B1B', '\U0001F7E8', '\U0001F7E9'])

WORD_LEN = 5
