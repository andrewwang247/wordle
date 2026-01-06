# Wordle

Play [Wordle](https://en.wikipedia.org/wiki/Wordle) with an engine that combines information theory and word frequency data to make optimal guesses and assist the user in solving puzzles. There are 3 primary modes of interaction for users:

1. A self-contained "offline" mode with a provided or random solution. The user is prompted for guesses and is shown the resulting square pattern. Optional engine assistance is available.
2. An assistant "online" mode that helps the user solve an external puzzle with an unknown solution. The user is promped for both guesses and the square pattern returned by the puzzle.
3. An exploratory simulations mode where the user can play around with the engine solving simulated puzzles in a Jupyter notebook as well as examine the data more closely.

## Usage

### Offline

```text
Usage: offline.py [OPTIONS]

  Play Wordle with a provided or random solution.

Options:
  -a, --assist           Display frequency and entropy assistance to player.
  -s, --solution TEXT    Provide a solution for the game. Random if not set.
  -i, --infolen INTEGER  If assisting, max # of suggestions to log per round.
  --help                 Show this message and exit.
```

### Online

```text
Usage: online.py [OPTIONS]

  Play Wordle with an unknown solution.

Options:
  -i, --infolen INTEGER  Max # of suggestions to log per round.
  --help                 Show this message and exit.
```

## Engine Assistance

The engine helps the user by providing 2 sorted tables at each round.

1. Possible solutions in this round, sorted by their [Zipf frequency](https://en.wikipedia.org/wiki/Zipf%27s_law), a human-friendly logarithmic scale that measures a word's frequency in natural language as the $\log_{10}$ of its occurence per billion words. When you're ready to take a stab at the solution, consult this table.
2. Guesses that are most likely to yield the most information in the next round, sorted by their [Shannon entropy](https://en.wikipedia.org/wiki/Entropy_(information_theory)) in bits. Intuitively, these guesses are expected to cut down the remaining possibilities by the largest amount. Note that an informative guess is not necessarily (and often isn't) one that matches the existing square patterns.

### Example

As an example, consider the first round of a game where you open with `hello` and the solution is `world`. You can expect to see:

```text
INFO:ranking:Remaining possiblities: 14855 words
INFO:ranking:Remaining entropy: 13.86 bits
INFO:__main__:The optimal starting guess is tares

Guess: hello
INFO:game:Round 1: hello ⬛⬛⬛🟩🟨
INFO:ranking:Remaining possiblities: 121 words
INFO:ranking:Remaining entropy: 6.92 bits
INFO:engine:Reduced possibilities by 14734 words
INFO:engine:Reduced entropy by 6.94 bits
INFO:engine:
          log_freq
possible          
would         6.27
could         6.06
world         5.89
goals         4.95
tools         4.59
souls         4.21
fools         3.88
pools         3.87
bowls         3.75
soils         3.57
INFO:engine:
         entropy
guesses         
sayid      4.401
amids      4.357
diyas      4.349
maids      4.310
staid      4.286
stoai      4.266
dooms      4.266
wadis      4.249
daisy      4.240
miyas      4.226
```

The logs tell you that after guessing `hello` and seeing ⬛⬛⬛🟩🟨:

- You've reduced the number of possiblities from 14855 to 121. This round contained 6.94 bits of information, reducing the entropy from 13.86 bits to 6.92 bits.
- If you're feeling lucky, you can see among the viable solutions, `would` is the one that occurs most frequently in natural language and would be a suitable pick.
- If 121 possibilities is still too uncertain for you, then `sayid` is expected to be the most informative guess. It's expected to reduce the entropy of the space by 4.4 bits.

You are not obligated to pick according to the engine. The tables will update according to whatever word you pick and its corresponding square pattern. You can even turn off suggestions if you're looking to play puzzles as a challenge. Do what makes your heart happy!

## Simulation

The Jupyter notebook `simulation.ipynb` provides an interactive environment for running puzzle simulations by using the engine as a bot. Essentially, it's the computer playing against itself. We graph the entropy after each round to visualize how the bot iteratively prunes the possibilities space.

![Entropy graph for simulated Wordle games](resources/simulation_graph.png)

### Strategy

The bot follows a simple strategy in an attempt to solve the puzzle in as few rounds as possible.

1. While there are more than $k$ possibilities -- equivalently, while the entropy is greater than $\log_2(k)$, choose the guess that is expected to provide the most information (highest entropy).
2. When there are at most $k$ possibilities -- equivalently, when the entropy is no more than $\log_2(k)$, choose the possibility that most frequently occurs in natural language until the correct answer is reached.

The hyperparameter $k$ represents how lucky we're feeling. A low value for $k$ means that we attempt to reduce the possibilities space as much as possible before shooting for a solution. Conversely, a high value for $k$ means that we start guessing solutions with less information. The bot uses a conservative value of $k = 2$ and only goes for solutions when it's a binary choice.

## Algorithm

Let $W$ be the set of words in our dictionary, $m$ be the length of words ($m = 5$ for Wordle), and $S$ be the set of $3^m$ possible square results we'd see after guessing. A round consists of both a guess word $w \in W$ from the dictionary and the square pattern $s \in S$ that tells us if each character is correct, misplaced, or nonexistant, e.g. $w = \text{fjord}$ and $s = \text{🟩⬛🟩⬛🟨}$.

### Information

Informally, the information $I(w, s)$ of a round measures the extent to which it reduces the possibilities space. Let $p(w, s)$ be the probability of encountering the round $(w, s)$ at this stage. The information is defined as

```math
I(w, s) = \log_2 \left( \frac{1}{p(w, s)} \right) = - \log_2 p(w, s)
```

This number quantifies the number of times we cut the probability space in half, with units of bits. Assume that the probability distribution is uniform, i.e. every word in the dictionary is equally likely to be the solution. Continuing with our example, the probability that we'd see `fjord` and 🟩⬛🟩⬛🟨 is

```math
p(\text{fjord, 🟩⬛🟩⬛🟨}) = \frac{\text{\# of possibilities matching fjord and 🟩⬛🟩⬛🟨}}{\text{total \# of possibilities}}
```

Using our current dictionary and assuming we guess `fjord` and see 🟩⬛🟩⬛🟨 on the first round, we have reduced our space from 14855 possibilities to only 3. Those being `foods`, `foody`, and `feods` - an archaic term for "an estate granted to a vassal by a feudal lord in exchange for service". It follows that

```math
I(\text{fjord, 🟩⬛🟩⬛🟨}) = -\log_2 \left( \frac{3}{14855} \right) \approx 12.27
```

which shows that we've chopped our possibilities space in half more than 12 times. A very informative round!

### Entropy

The entropy of a random variable quantifies its average uncertainty. It tells us the expected information we would gain by "resolving" the variable's value. At any given round and for each word $w \in W$, we can define a random variable $X_w$ over $S$ based on the probability that we would see each of the square patterns. That is, $X_w(s) = p(w, s)$. The entropy $H$ of $X_w$ is the expected value of its information:

```math
H(X_w) = E[ I(X_w) ] = \sum_{s \in S} p(w, s) \cdot I(w, s) = - \sum_{s \in S} p(w, s) \cdot \log_2 p(w, s)
```

By convention, set $I(w, s) = 0$ whenever $p(w, s) = 0$ in this expression to avoid taking logarithms of 0. This means that if $s$ is impossible after guessing $w$ this round, exclude it from the summation. Using our example word `fjord`, compute square probabilities and sort descending. Plotting this series against information, we can visualize the correlation.

![Probability and information plot for fjord](resources/information_graph.png)

Taking the "inner product" of these 2 series yields the entropy when $w = \text{fjord}$, which is $H(X_w) \approx 3.64$ bits. You can further explore entropy in round 1 in the later cells of `simulation.ipynb`. The pre-computed initial round entropy with frequency data is stored in the resource file `resources/initial_data.csv`.

## Acknowledgements

This project was inspired by Grant Sanderson of [3Blue1Brown](https://www.3blue1brown.com/). Check out his videos on Wordle:

1. [Solving Wordle using information theory](https://www.youtube.com/watch?v=v68zYyaEmEA)
2. [Oh, wait, actually the best Wordle opener is not "crane"…](https://www.youtube.com/watch?v=fRed0Xmc2Wg)
