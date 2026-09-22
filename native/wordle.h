/*
Wordle comparison.

Copyright 2026. Andrew Wang.
*/
#pragma once
#include <cstddef>
#include <limits>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace wordle {
static constexpr auto NUM_CHARS = std::numeric_limits<unsigned char>::max() + 1;
static constexpr auto BLACK = 'b', GREEN = 'g', YELLOW = 'y';

/**
 * @brief Validate and get the common word length.
 * @param words The list of words to validate.
 * @return The common length of all words.
 * @throws invalid_argument if words are empty or differ in length.
 */
std::size_t uniform_length(std::span<const std::string> words);

/**
 * @brief Read words line by line from a file.
 * @param fname The name of the input file.
 * @return Newline delimited list of words.
 * @throws invalid_argument if any word's length is not len.
 */
std::vector<std::string> read_words(std::string_view fname);

/**
 * @brief Generate the Wordle square pattern for a round.
 * @pre Parameters must both have length of len.
 * @param guess The word that was guessed.
 * @param answer The puzzle solution.
 * @param len The common word length.
 * @return A string of color indicators corresponding to squares.
 */
std::string compare(std::string_view guess, std::string_view answer,
                    std::size_t len) noexcept;
}  // namespace wordle
