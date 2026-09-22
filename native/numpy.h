/*
Numpy file construction.

Copyright 2026. Andrew Wang.
*/
#pragma once
#include <cstddef>
#include <fstream>
#include <string_view>

/**
 * @brief Interface with Numpy binary format.
 */
namespace numpy {
using std::string_view_literals::operator""sv;

static constexpr auto PAD_ALIGN = 64;
static constexpr auto MAGIC_VERSION = "\x93NUMPY\x01\x00"sv;
// NOLINTBEGIN(whitespace/indent_namespace)
static constexpr auto HEADER_TEMPLATE =
    "{{'descr': '|S{}', 'fortran_order': False, 'shape': ({}, {}), }}";
// NOLINTEND

/**
 * @brief Write V1 numpy header with dtype bytes and shape (dim, dim).
 * @param fout The output file stream.
 * @param nbytes Number of bytes per item in array.
 * @param dim The size of 1 dimension of the square grid shape.
 */
void write_header(std::ofstream& fout, std::size_t nbytes, std::size_t dim);

}  // namespace numpy
