// Seeded violation: untyped byte copies and comparisons.
#include <array>
#include <cstdint>
#include <cstring>

namespace kv::rule_24_5_2::bad {

void copy_frame(std::array<std::uint8_t, 4U>& dest, const std::array<std::uint8_t, 4U>& source) {
  static_cast<void>(std::memcpy(dest.data(), source.data(), dest.size()));
}

bool same_frame(const std::array<std::uint8_t, 4U>& a, const std::array<std::uint8_t, 4U>& b) {
  return std::memcmp(a.data(), b.data(), a.size()) == 0;
}

}  // namespace kv::rule_24_5_2::bad
