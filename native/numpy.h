/*
Numpy file construction.

Copyright 2026. Andrew Wang.
*/
#pragma once
#include <fstream>

namespace numpy {
static constexpr auto MAGIC_VERSION_BYTES = 8, PAD_ALIGN = 64;
// NOLINTBEGIN(whitespace/indent_namespace)
static constexpr auto HEADER_TEMPLATE =
    "{{'descr': '|S{}', 'fortran_order': False, 'shape': ({}, {}), }}";
// NOLINTEND

/**
 * @brief Write pattern header to V1 npy.
 * @param fout The output file stream.
 */
void write_header(std::ofstream& fout);

}  // namespace numpy
