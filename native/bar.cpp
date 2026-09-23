/*
Simple progress bar.

Copyright 2026. Andrew Wang.
*/
#include "bar.h"

#include <cstddef>
#include <cstdio>
#include <print>
#include <string>

using std::fflush;
using std::print;
using std::println;
using std::size_t;
using std::string;

progress_bar::progress_bar(size_t total) noexcept
    : m_outer_total(total), m_inner_total(total / BAR_WIDTH) {}

void progress_bar::increment() {
  ++m_inner_counter;
  ++m_outer_counter;
  if (m_inner_counter == m_inner_total) {
    display(false);
    m_inner_counter = 0;
  } else if (m_outer_counter == m_outer_total) {
    display(true);
  }
}

void progress_bar::display(bool new_ln) const {
  const auto num_ticks = BAR_WIDTH * m_outer_counter / m_outer_total;
  const auto percent = 100U * m_outer_counter / m_outer_total;
  const string completed(num_ticks, TICK);
  if (new_ln) {
    println(TEMPLATE, completed, BAR_WIDTH, percent);
  } else {
    print(TEMPLATE, completed, BAR_WIDTH, percent);
  }
  fflush(stdout);
}
