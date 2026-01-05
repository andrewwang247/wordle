"""
Basic Wordle square enumeration.

Copyright 2026. Andrew Wang.
"""
from enum import Enum


class Square(Enum):
    """Define square colors and their unicode representation."""

    BLACK = '\U00002B1B'
    YELLOW = '\U0001F7E8'
    GREEN = '\U0001F7E9'
