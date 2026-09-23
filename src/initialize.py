"""Configure both online and offline games.

Copyright 2026. Andrew Wang.
"""

from .cache import load_patterns, load_targets, load_words
from .engine import Engine
from .game import Game
from .ranking import Ranker


def setup_environment(*, targeted: bool) -> tuple[Game, Engine]:
    """Setup game environment and engine."""
    words = load_words()
    patterns = load_patterns()
    targets = load_targets() if targeted else None
    game = Game(words, patterns, targets)
    ranker = Ranker(words, patterns)
    engine = Engine(words, ranker, targets)
    return game, engine
