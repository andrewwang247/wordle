"""
Measure the performance of the bot.

Copyright 2026. Andrew Wang.
"""
from multiprocessing import Pool
from cache import load_words, load_patterns
from engine import Engine
from tqdm import tqdm

words = load_words()
patterns = load_patterns()

def parallel_sim(word: str) -> int:
    """Parallel game processing"""
    engine = Engine(words, patterns)
    game = engine.simulate(word)
    return game.current_round()

def main():
    """Benchmark engine strategy against all words."""
    futures = []
    results = []
    with Pool(5) as pool:
        for word in words[:100]:
            future = pool.apply_async(parallel_sim, args=(word,))
            futures.append(future)
        for fut in tqdm(futures):
            results.append(fut.get())


if __name__ == '__main__':
    main()