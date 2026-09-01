"""Assist user in playing an online game.

Copyright 2026. Andrew Wang.
"""

# pylint: disable=no-value-for-parameter,duplicate-code
import logging

from click import IntRange, command, option

from src import Engine, Game, cache, convert_squares

logger = logging.getLogger(__name__)


def play_one_round(game: Game, engine: Engine, infolen: int) -> bool:
    """Play a single round. Returns whether player won."""
    try:
        user_guess = input("\nGuess: ")
        user_response = input("Squares: ")
        squares = convert_squares(user_response)
        if game.append_is_win(user_guess, squares):
            return True
        engine.feedback(user_guess, squares)
        engine.log_assistance(infolen)
    except AssertionError as err:
        logger.warning(err)
    return False


@command()
@option(
    "--infolen",
    "-l",
    type=IntRange(0, 10),
    default=5,
    help="Max # of suggestions to log per round. 0 is no assistance.",
)
@option(
    "--targeted",
    "-t",
    is_flag=True,
    default=False,
    help="Use known targets sub-list to prime engine.",
)
@option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Displays application logs if set.",
)
def main(infolen: int, *, targeted: bool, verbose: bool) -> None:
    """Play Wordle with an unknown solution."""
    logging.basicConfig(level=logging.INFO if verbose else logging.WARNING)
    words, targets = cache.load_words()
    patterns = cache.load_patterns()
    game = Game(words, patterns)
    engine = Engine(words, patterns, targets if targeted else None)

    if infolen > 0:
        cache.log_initial_assistance(infolen, targeted=targeted)
    print('Use "b", "y", "g" to denote squares color')
    while not play_one_round(game, engine, infolen):
        pass

    answer = game.guess_hist[-1]
    assert answer is not None, "Game solution should not be None"
    engine.simulate(answer)


if __name__ == "__main__":
    main()
