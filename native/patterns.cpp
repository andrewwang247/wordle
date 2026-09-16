/*
Compile Wordle patterns.

Copyright 2026. Andrew Wang
*/
#include <fstream>
#include <string_view>

#include "numpy.h"
#include "wordle.h"

using std::ofstream;
using std::string_view;

static constexpr auto INPUT_FILE = "./resources/words.txt";
static constexpr auto OUTPUT_FILE = "./resources/patterns.npy";

int main() {
  const auto words = wordle::read_words(INPUT_FILE);
  ofstream fout{OUTPUT_FILE};
  numpy::write_header(fout);
  for (const string_view guess : words) {
    for (const string_view answer : words) {
      const auto squares = wordle::compare(guess, answer);
      fout.write(squares.data(), wordle::WORD_LEN);
    }
  }
}
