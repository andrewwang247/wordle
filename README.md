# Wordle

Play [Wordle](https://en.wikipedia.org/wiki/Wordle) with an engine that combines information theory and word frequency data to make optimal guesses and assist the user in solving puzzles. There are 3 primary modes of interaction for users:

1. A self-contained "offline" mode with a provided or random solution. The user is prompted for guesses and is shown the resulting square pattern. Optional engine assistance is available.
2. An assistant "online" mode that helps the user solve an external puzzle with an unknown solution. The user is promped for both guesses and the square pattern returned by the puzzle.
3. An exploratory simulations mode where the user can play around with the engine solving simulated puzzles in a Jupyter notebook.

## Usage

```text
Usage: offline.py [OPTIONS]

  Play Wordle with a provided or random solution.

Options:
  -a, --assist           Display frequency and entropy assistance to player.
  -s, --solution TEXT    Provide a solution for the game. Random if not set.
  -i, --infolen INTEGER  If assisting, max # of suggestions to log per turn.
  --help                 Show this message and exit.
```

```text
Usage: online.py [OPTIONS]

  Play Wordle with an unknown solution.

Options:
  -i, --infolen INTEGER  Max # of suggestions to log per turn.
  --help                 Show this message and exit.
```

## Engine Assistance

The engine helps the user by providing 2 sorted tables at each round.

1. Viable solutions in this round, sorted by their [Zipf frequency](https://en.wikipedia.org/wiki/Zipf%27s_law), a human-friendly logarithmic scale that measures a word's frequency in natural language as the $\log_{10}$ of its occurence per billion words. When you're ready to take a stab at the solution, consult this table.
2. Guesses that are most likely to yield the most information in the next round, sorted by their [Shannon entropy](https://en.wikipedia.org/wiki/Entropy_(information_theory)) in bits. Intuitively, these guesses are expected to cut down the remaining possibilities by the largest amount. Note that an informative guess is not necessarily (and often isn't) one that matches the existing square patterns.

As an example, consider the first round of a game where you open with `hello` and the solution is `world`. You can expect to see:

```text
INFO:ranking:Remaining possiblities: 14855 words
INFO:ranking:Remaining entropy: 13.86 bits
INFO:__main__:The optimal starting guess is tares

Guess: hello
INFO:game:Turn 1: hello ⬛⬛⬛🟩🟨
INFO:ranking:Remaining possiblities: 121 words
INFO:ranking:Remaining entropy: 6.92 bits
INFO:engine:Reduced possibilities by 14734 words
INFO:engine:Reduced entropy by 6.94 bits
INFO:engine:
           log_freq
solutions          
would          6.27
could          6.06
world          5.89
goals          4.95
tools          4.59
souls          4.21
fools          3.88
pools          3.87
bowls          3.75
soils          3.57
INFO:engine:
          entropy
guesses          
sayid    4.401152
amids    4.356567
diyas    4.349188
maids    4.310339
staid    4.286204
stoai    4.266305
dooms    4.265757
wadis    4.249081
daisy    4.240403
miyas    4.226080
```

The logs tell you that after guessing `hello` and seeing `⬛⬛⬛🟩🟨`:

- You've reduced the number of possible solutions from 14855 to 121. This round contained 6.94 bits of information, reducing the entropy from 13.86 bits to 6.92 bits.
- If you're feeling lucky, you can see among the viable solutions, `would` is the one that occurs most frequently in natural language and would be a suitable pick.
- If 121 possibilities is still too uncertain for you, then `sayid` is expected to be the most informative guess. It's expected to reduce the entropy of the space by 4.4 bits.

You are not obligated to pick according to the engine. The tables will update according to whatever word you pick and its corresponding square pattern. You can even turn off suggestions if you're looking to play puzzles as a challenge. Do what makes your heart happy!

## Algorithm

Calculate the entropy of each possible guess and square permutation. This will be stored in an array of shape (`NUM_WORDS` , $3^N$) where $N$ = `WORD_LEN`. We will assume a uniform probability distribution over the possible words. The probability $P(s | w)$ of getting square pattern $s$ after guessing word $w \in W$ is simply the proportion of words $c$ in the corpus such that `is_match(w, c, s)`. We define the information gained by this guess (measured in bits) as:

```math
I(w, s) = - \log_2 P(s | w) = - \log_2 \left( \frac{\text{matches}(w, s)}{|W|} \right)
```

We want to choose the word that maximizes the expected information gain. That is, the entropy $H$ given by the following sum over all square patterns:

```math
H(w) = - \sum_s P(s | w) \cdot \log_2 P(s | w)
```

## Acknowledgements

This project was inspired by Grant Sanderson of [3Blue1Brown](https://www.3blue1brown.com/). Check out his videos on Wordle:

1. [Solving Wordle using information theory](https://www.youtube.com/watch?v=v68zYyaEmEA)
2. [Oh, wait, actually the best Wordle opener is not "crane"…](https://www.youtube.com/watch?v=fRed0Xmc2Wg)
