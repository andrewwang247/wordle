/*
Wordle comparison.

Copyright 2026. Andrew Wang.
*/
#include "wordle.h"

#include <algorithm>
#include <bitset>
#include <fstream>
#include <ranges>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

using std::bitset;
using std::get;
using std::ifstream;
using std::invalid_argument;
using std::string;
using std::string_view;
using std::vector;

namespace ranges = std::ranges;
namespace views = std::views;

vector<string> wordle::read_words(string_view fname) {
  ifstream fin{fname.data()};
  vector<string> words;
  words.reserve(NUM_WORDS);
  for (string word; fin >> word;) {
    if (word.length() != WORD_LEN) {
      throw invalid_argument("All words must have the same fixed length.");
    }
    words.emplace_back(word);
  }
  return words;
}

string wordle::compare(string_view guess, string_view answer) noexcept {
  string squares(WORD_LEN, BLACK);
  // Mark green squares by position matching.
  for (auto&& [gs, as, sq] : views::zip(guess, answer, squares)) {
    if (gs == as) sq = GREEN;
  }

  // View of where squares aren't green, i.e. mismatch.
  const auto where_mismatch = [&squares](string_view word) {
    return views::zip(word, squares) |
           views::filter([](auto&& tuple) { return get<1>(tuple) != GREEN; });
  };

  auto where_guess_mismatch = where_mismatch(guess) | views::elements<0>;
  auto where_answer_mismatch = where_mismatch(answer) | views::elements<0>;

  bitset<NUM_CHARS> seen;
  for (const auto letter : where_guess_mismatch) {
    // Skip if letter has already been processed.
    const auto idx = static_cast<unsigned char>(letter);
    if (seen[idx]) continue;
    seen[idx] = true;

    // Count non-green appearances of letter in answer.
    const auto max_yellow = ranges::count(where_answer_mismatch, letter);

    // Color up to max_yellow squares where guess matches letter.
    auto yellows = where_mismatch(guess) |
                   views::filter([letter](auto&& tuple) {
                     return get<0>(tuple) == letter;
                   }) |
                   views::elements<1>;
    ranges::fill(yellows | views::take(max_yellow), YELLOW);
  }

  return squares;
}
