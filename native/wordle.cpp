/*
Wordle comparison.

Copyright 2026. Andrew Wang.
*/
#include "wordle.h"

#include <algorithm>
#include <bitset>
#include <cstddef>
#include <fstream>
#include <ranges>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

using std::bitset;
using std::get;
using std::ifstream;
using std::invalid_argument;
using std::size_t;
using std::span;
using std::string;
using std::string_view;
using std::vector;

namespace ranges = std::ranges;
namespace views = std::views;

size_t wordle::uniform_length(span<const string> words) {
  if (words.empty()) throw invalid_argument("Word list is empty");

  const auto first_len = words.front().length();
  const auto match_first = [first_len](auto word_len) {
    return word_len == first_len;
  };

  if (!ranges::all_of(words, match_first, &string::length)) {
    throw invalid_argument("Words have mismatched lengths");
  }
  return first_len;
}

vector<string> wordle::read_words(string_view fname) {
  ifstream fin{fname.data()};
  vector<string> words;
  for (string word; fin >> word;) {
    words.emplace_back(word);
  }
  return words;
}

string wordle::compare(string_view guess, string_view answer,
                       size_t len) noexcept {
  string squares(len, BLACK);
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
