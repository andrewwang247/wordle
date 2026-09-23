/*
Wordle comparison.

Copyright 2026. Andrew Wang.
*/
#include "wordle.h"

#include <array>
#include <cstddef>
#include <string>
#include <string_view>

using std::array;
using std::size_t;
using std::string;
using std::string_view;

wordle::wordle(size_t len) noexcept : m_word_len(len) {}

string wordle::compare(string_view guess, string_view answer) const noexcept {
  string squares(m_word_len, BLACK);
  array<int, NUM_CHARS> yellow_counts{};

  // Mark green squares by position matching.
  // Count frequency of non-green characters in answer.
  for (auto i = 0U; i != m_word_len; ++i) {
    if (guess[i] == answer[i]) {
      squares[i] = GREEN;
    } else {
      const auto ans_idx = static_cast<unsigned char>(answer[i]);
      ++yellow_counts[ans_idx];
    }
  }

  // Iterate over non-green letters in guess.
  // Mark up to yellow_counts guess positions yellow.
  for (auto i = 0U; i != m_word_len; ++i) {
    if (squares[i] == GREEN) continue;

    const auto gs_idx = static_cast<unsigned char>(guess[i]);
    if (yellow_counts[gs_idx] > 0) {
      squares[i] = YELLOW;
      --yellow_counts[gs_idx];
    }
  }

  return squares;
}
