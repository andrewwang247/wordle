"""
Assist user in playing an online game.

Copyright 2026. Andrew Wang.
"""
# pylint: disable=no-value-for-parameter
import logging
from click import command, option
from constants import convert_squares
from cache import load_words, load_patterns, log_initial_assistance
from engine import Engine
from game import Game

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def play_one_round(game: Game, engine: Engine, infolen: int) -> bool:
    """Play a single round. Returns whether player won."""
    try:
        user_guess = input('\nGuess: ')
        user_response = input('Squares: ')
        squares = convert_squares(user_response)

        is_win = game.append(user_guess, squares)
        engine.feedback(user_guess, squares)
        engine.log_assistance(infolen)
        return is_win
    except AssertionError as err:
        # In case the user input is unrecognized
        logger.warning(err)
        return False


@command()
@option('--targeted', '-t', is_flag=True, default=False,
        help='Use known targets sub-list to prime engine.')
@option('--infolen', '-i', type=int, default=10,
        help='Max # of suggestions to log per round.')
def main(targeted: bool, infolen: int):
    """Play Wordle with an unknown solution."""
    words, targets = load_words()
    patterns = load_patterns()
    game = Game(words, patterns)
    engine = Engine(words, patterns, targets if targeted else None)

    if targeted:
        engine.log_assistance(infolen)
    else:
        log_initial_assistance(infolen)
    logger.info('Use "b", "y", "g" to denote squares color')
    while not play_one_round(game, engine, infolen):
        pass

    answer = game.guess_hist[-1]
    engine.simulate(answer, targets if targeted else None)


if __name__ == '__main__':
    main()
