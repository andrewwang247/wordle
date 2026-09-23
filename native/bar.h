/*
Simple progress bar.

Copyright 2026. Andrew Wang.
*/
#pragma once
#include <cstddef>

/**
 * @brief Fixed width ASCII progress bar.
 */
class progress_bar {
 private:
  // BAR_WIDTH of TICK rendered in TEMPLATE will take up WIDTH.

  static constexpr auto WIDTH = 80U;
  static constexpr auto TICK = '*';

  static constexpr auto TEMPLATE = "\r[{:<{}}] {:3}%";
  static constexpr auto BAR_WIDTH = WIDTH - 7U;

  /**
   * @brief Progress over entire processing range.
   */
  std::size_t m_outer_total{}, m_outer_counter{};
  /**
   * @brief Progress over subrange for the next tick.
   */
  std::size_t m_inner_total{}, m_inner_counter{};

 public:
  /**
   * @brief Construct progress bar for range of known size.
   * @pre total must be at least BAR_WIDTH.
   * @param total The number of elements to process.
   */
  explicit progress_bar(std::size_t total) noexcept;

  /**
   * @brief Update status with completion of 1 element.
   * @warning Do not increment more than total times.
   */
  void increment();

 private:
  /**
   * @brief Print current bar to stdout.
   * @param new_ln Whether to add a new line.
   */
  void display(bool new_ln) const;
};
