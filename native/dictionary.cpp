/*
Read from and validate dictionaries.

Copyright 2026. Andrew Wang.
*/
#include "dictionary.h"

#include <algorithm>
#include <cstddef>
#include <fstream>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

using std::ifstream;
using std::invalid_argument;
using std::size_t;
using std::span;
using std::string;
using std::string_view;
using std::vector;

namespace ranges = std::ranges;

vector<string> dictionary::load(string_view fname) {
  ifstream fin{fname.data()};
  vector<string> words;
  for (string word; fin >> word;) {
    words.emplace_back(word);
  }
  return words;
}

size_t dictionary::uniform_length(span<const string> words) {
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
