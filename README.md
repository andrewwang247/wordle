# Wordle

Calculate the entropy of each possible guess and square permutation. This will be stored in an array of shape (`NUM_WORDS` , $3^N$) where $N$ = `WORD_LEN`. We will assume a uniform probability distribution over the possible words. The probability $P(s | w)$ of getting square pattern $s$ after guessing word $w \in W$ is simply the proportion of words $c$ in the corpus such that `is_match(w, c, s)`. We define the information gained by this guess (measured in bits) as:

```math
I(w, s) = - \log_2 P(s | w) = - \log_2 \left( \frac{\text{matches}(w, s)}{|W|} \right)
```

We want to choose the word that maximizes the expected information gain. That is, the entropy $H$ given by the following sum over all square patterns:

```math
H(w) = - \sum_s P(s | w) \cdot \log_2 P(s | w)
```
