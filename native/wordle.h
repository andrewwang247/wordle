/*
Wordle comparison.

Copyright 2026. Andrew Wang.
*/
#pragma once
#include <string>
#include <string_view>
#include <vector>

namespace wordle {
static constexpr auto WORD_LEN = 5UZ, NUM_WORDS = 14'855UZ;
static constexpr auto NUM_CHARS = 1 << 8;
static constexpr auto BLACK = 'b', GREEN = 'g', YELLOW = 'y';

/**
 * @brief Read words line by line from a file.
 * @param fname The name of the input file.
 * @return Newline delimited list of words.
 * @throws invalid_argument if any word's length is not WORD_LEN.
 */
std::vector<std::string> read_words(std::string_view fname);

/**
 * @brief Generate the Wordle square pattern for a round.
 * @pre Parameters must both have length of WORD_LEN.
 * @param guess The word that was guessed.
 * @param answer The puzzle solution.
 * @return A string of color indicators corresponding to squares.
 */
std::string compare(std::string_view guess, std::string_view answer) noexcept;
}  // namespace wordle
