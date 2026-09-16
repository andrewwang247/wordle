/*
Compile Wordle patterns.

Copyright 2026. Andrew Wang
*/
#include <fstream>
#include <stdexcept>
#include <string_view>

#include "numpy.h"
#include "wordle.h"

using std::invalid_argument;
using std::ofstream;
using std::string_view;

int main(int argc, char* argv[]) {
  if (argc != 3) {
    throw invalid_argument("Args: input_path.txt output_path.npy");
  }

  const auto words = wordle::read_words(argv[1]);
  const auto len = wordle::uniform_length(words);

  ofstream fout{argv[2]};
  numpy::write_header(fout, len, words.size());

  for (const string_view guess : words) {
    for (const string_view answer : words) {
      const auto squares = wordle::compare(guess, answer, len);
      fout.write(squares.data(), static_cast<int>(len));
    }
  }
}
