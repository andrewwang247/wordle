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

using std::array;
using std::bit_cast;
using std::byteswap;
using std::endian;
using std::format;
using std::ofstream;
using std::size_t;
using std::uint16_t;

void numpy::write_header(ofstream& fout, size_t nbytes, size_t dim) {
  // Header dictionary data.
  const auto header_data = format(HEADER_TEMPLATE, nbytes, dim, dim);
  const auto data_len = header_data.size();

  uint16_t specifier{};
  // magic + version + len specifier + dictionary
  const auto current_bytes =
      MAGIC_VERSION.size() + sizeof(specifier) + data_len;
  // Get padding needed to reach next multiple of PAD_ALIGN.
  const auto padding = PAD_ALIGN - (current_bytes % PAD_ALIGN);

  specifier = static_cast<uint16_t>(data_len + padding);
  if constexpr (endian::native == endian::big) {
    specifier = byteswap(specifier);
  }
  const auto spec_bytes = bit_cast<array<char, sizeof(specifier)>>(specifier);

  fout.write(MAGIC_VERSION.data(), MAGIC_VERSION.size());
  fout.write(spec_bytes.data(), sizeof(specifier));
  fout.write(header_data.data(), static_cast<int>(data_len));
  // By construction, padding > 0
  for (auto i = 0U; i != padding - 1; ++i) fout.put('\x20');
  fout.put('\n');
}
