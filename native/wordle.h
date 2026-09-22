/*
Wordle comparison.

Copyright 2026. Andrew Wang.
*/
#pragma once
#include <cstddef>
#include <limits>
#include <string>
#include <string_view>

/**
 * @brief Compute square patterns given guess and answer.
 */
class wordle {
 private:
  static constexpr auto NUM_CHARS =
      std::numeric_limits<unsigned char>::max() + 1;
  static constexpr auto BLACK = 'b', GREEN = 'g', YELLOW = 'y';

  std::size_t m_word_len{};

 public:
  /**
   * @brief Initialize with common word length.
   * @param len The length of every input word.
   */
  explicit wordle(std::size_t len) noexcept;

  /**
   * @brief Generate the Wordle square pattern for a round.
   * @pre Parameters must both have same length.
   * @param guess The word that was guessed.
   * @param answer The puzzle solution.
   * @return A string of color indicators corresponding to squares.
   */
  std::string compare(std::string_view guess,
                      std::string_view answer) const noexcept;
};
