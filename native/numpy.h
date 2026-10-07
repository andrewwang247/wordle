/*
Numpy file construction.

Copyright 2026. Andrew Wang.
*/
#pragma once
#include <cstddef>
#include <fstream>

/**
 * @brief Interface with Numpy binary format.
 */
namespace wd::numpy {

/**
 * @brief Write V1 numpy header with dtype bytes and shape (dim, dim).
 * @param fout The output file stream.
 * @param nbytes Number of bytes per item in array.
 * @param dim The size of 1 dimension of the square grid shape.
 */
void write_header(std::ofstream& fout, std::size_t nbytes, std::size_t dim);

}  // namespace wd::numpy
