"""
Play offline games in user interactive mode.

Copy right 2026. Andrew Wang.
"""
# pylint: disable=no-value-for-parameter,duplicate-code
import logging
from click import command, IntRange, option
from src import Game, Engine, cache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def play_one_round(
        game: Game,
        engine: Engine,
        infolen: int) -> bool:
    """Play a single round. Returns whether player won."""
    try:
        user_guess = input('\nGuess: ')
        squares, is_win = game.guess_is_win(user_guess)
        if is_win:
            return True
        engine.feedback(user_guess, squares)
        engine.log_assistance(infolen)
    except AssertionError as err:
        logger.warning(err)
    return False


@command()
@option('--solution', '-s', type=str, default=None,
        help='Provide a solution for the game. Random if not set.')
@option('--infolen', '-l', type=IntRange(0, 10), default=5,
        help='Max # of suggestions to log per round. 0 is no assistance.')
def main(solution: str, infolen: int):
    """Play Wordle with a provided or random solution."""
    words = cache.load_words()[0]
    patterns = cache.load_patterns()
    game = Game(words, patterns)
    engine = Engine(words, patterns)
    game.set_solution(solution)

    if infolen > 0:
        cache.log_initial_assistance(infolen, False)
    while not play_one_round(game, engine, infolen):
        pass

    answer = game.solution
    assert answer is not None, 'Game solution should not be None'
    engine.simulate(answer)


if __name__ == '__main__':
    main()
