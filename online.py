"""
Assist user in playing an online game.

Copyright 2026. Andrew Wang.
"""
# pylint: disable=no-value-for-parameter
from sys import stdout
import logging
from click import command, option
from constants import convert_squares, BEST_FIRST_GUESS
from cache import initialize_resources
from engine import Engine
from game import Game

logging.basicConfig(level=logging.INFO, stream=stdout)
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
@option('--infolen', '-i', type=int, default=10,
        help='Max # of suggestions to log per round.')
def main(infolen: int):
    """Play Wordle with an unknown solution."""
    game, engine = initialize_resources()
    logger.info('Use "b", "y", "g" to denote squares color')
    logger.info('The optimal starting guess is %s', BEST_FIRST_GUESS)

    while not play_one_round(game, engine, infolen):
        pass

    answer = game.guess_hist[-1]
    engine.simulate(answer)


if __name__ == '__main__':
    main()
