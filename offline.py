"""
Play offline games in user interactive mode.

Copy right 2026. Andrew Wang.
"""
# pylint: disable=no-value-for-parameter
import logging
from click import command, option
from cache import load_words, load_patterns, log_initial_assistance
from game import Game
from engine import Engine

logging.basicConfig(level=logging.INFO)
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
@option('--solution', '-s', type=str, default=None,
        help='Provide a solution for the game. Random if not set.')
@option('--infolen', '-l', type=int, default=10,
        help='If assisting, max # of suggestions to log per round.')
def main(assist: bool, solution: str, infolen: int):
    """Play Wordle with a provided or random solution."""
    words = load_words()[0]
    patterns = load_patterns()
    game = Game(words, patterns)
    engine = Engine(words, patterns)
    game.set_solution(solution)

    if assist:
        log_initial_assistance(infolen, False)
    while not play_one_round(game, engine, assist, infolen):
        pass

    logger.info('\n\nSimulated engine playthrough')
    answer = game.solution
    assert answer is not None, 'Game solution should not be None'
    engine.simulate(answer)


if __name__ == '__main__':
    main()
