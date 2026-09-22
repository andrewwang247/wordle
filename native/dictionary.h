/*
Read from and validate dictionaries.

Copyright 2026. Andrew Wang.
*/
#pragma once
#include <cstddef>
#include <span>
#include <string>
#include <string_view>
#include <vector>

/**
 * @brief Read and validate dictionary words.
 */
namespace dictionary {

/**
 * @brief Read words line by line from a file.
 * @param fname The name of the input file.
 * @return Newline delimited list of words.
 */
std::vector<std::string> load(std::string_view fname);

/**
 * @brief Validate and get the common word length.
 * @param words The list of words to validate.
 * @return The common length of all words.
 * @throws invalid_argument if words are empty or differ in length.
 */
std::size_t uniform_length(std::span<const std::string> words);

}  // namespace dictionary
