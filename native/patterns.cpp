/*
Compile Wordle patterns.

Copyright 2026. Andrew Wang
*/
#include <fstream>
#include <stdexcept>
#include <string_view>

#include "bar.h"
#include "dictionary.h"
#include "numpy.h"
#include "wordle.h"

using std::invalid_argument;
using std::ofstream;
using std::string_view;

int main(int argc, char* argv[]) {
  if (argc != 3) {
    throw invalid_argument("Args: input_path.txt output_path.npy");
  }

  const auto words = dictionary::load(argv[1]);
  const auto word_len = dictionary::uniform_length(words);
  const auto dictionary_len = words.size();

  ofstream fout{argv[2]};
  numpy::write_header(fout, word_len, dictionary_len);

  const wordle patterns{word_len};
  progress_bar pbar{dictionary_len * dictionary_len};
  for (const string_view guess : words) {
    for (const string_view answer : words) {
      const auto squares = patterns.compare(guess, answer);
      fout.write(squares.data(), static_cast<int>(word_len));
      pbar.increment();
    }
  }
}
