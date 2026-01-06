"""
Play offline games in user interactive mode.

Copy right 2026. Andrew Wang.
"""
# pylint: disable=no-value-for-parameter
from sys import stdout
import logging
import numpy as np
from click import command, option
from cache import load_words, load_patterns
from game import Game
from engine import Engine, BEST_FIRST_GUESS

logging.basicConfig(level=logging.INFO, stream=stdout)
logger = logging.getLogger(__name__)


def play_one_round(
        game: Game,
        engine: Engine,
        assist: bool,
        infolen: int) -> bool:
    """Play a single round. Returns whether player won."""
    try:
        user_guess = input('\nGuess: ')
        squares, is_win = game.guess(user_guess)
        if is_win:
            return True
        engine.feedback(user_guess, squares)
        if assist:
            engine.log_assistance(infolen)
        return False
    except AssertionError as err:
        # In case the user input is unrecognized
        logger.warning(err)
        return False


@command()
@option('--assist', '-a', is_flag=True, default=False,
        help='Display frequency and entropy assistance to player.')
@option('--infolen', '-i', type=int, default=6,
        help='If assisting, max # of suggestions to log per turn.')
def main(assist: bool, infolen: int):
    """Play Wordle with a randomly chosen solution."""
    words = load_words()
    patterns = load_patterns()
    game = Game(words, patterns)
    engine = Engine(words, patterns)

    answer = np.random.choice(words, 1)[0]
    game.set_solution(answer)
    if assist:
        logger.info('The optimal starting guess is %s', BEST_FIRST_GUESS)
    while not play_one_round(game, engine, assist, infolen):
        pass

    logger.info('\n\nSimulated engine playthrough')
    engine.reset()
    engine.simulate(answer)


if __name__ == '__main__':
    main()
