/*
Numpy file construction.

Copyright 2026. Andrew Wang.
*/
#include "numpy.h"

#include <array>
#include <bit>
#include <cstddef>
#include <cstdint>
#include <format>
#include <fstream>
#include <string_view>

using std::array;
using std::bit_cast;
using std::byteswap;
using std::endian;
using std::format;
using std::ofstream;
using std::size_t;
using std::uint16_t;

using std::string_view_literals::operator""sv;

namespace wd {

void numpy::write_header(ofstream& fout, size_t nbytes, size_t dim) {
  static constexpr auto HEADER_TEMPLATE =
      "{{'descr': '|S{}', 'fortran_order': False, 'shape': ({}, {}), }}";

  // Header dictionary data.
  const auto header_data = format(HEADER_TEMPLATE, nbytes, dim, dim);
  const auto data_len = header_data.size();

  static constexpr auto PAD_ALIGN = 64;
  array<char, PAD_ALIGN> pad_buffer{};
  pad_buffer.fill('\x20');

  static constexpr auto MAGIC_VERSION = "\x93NUMPY\x01\x00"sv;
  uint16_t specifier{};

  // magic + version + len specifier + dictionary
  const auto current_bytes =
      MAGIC_VERSION.size() + sizeof(specifier) + data_len;
  // Get padding needed to reach next multiple of PAD_ALIGN.
  const auto padding = PAD_ALIGN - (current_bytes % PAD_ALIGN);
  // By construction, padding > 0
  pad_buffer[padding - 1] = '\n';

  specifier = static_cast<uint16_t>(data_len + padding);
  if constexpr (endian::native == endian::big) {
    specifier = byteswap(specifier);
  }
  const auto spec_bytes = bit_cast<array<char, sizeof(specifier)>>(specifier);

  fout.write(MAGIC_VERSION.data(), MAGIC_VERSION.size());
  fout.write(spec_bytes.data(), sizeof(specifier));
  fout.write(header_data.data(), static_cast<int>(data_len));
  fout.write(pad_buffer.data(), static_cast<int>(padding));
}

}  // namespace wd
