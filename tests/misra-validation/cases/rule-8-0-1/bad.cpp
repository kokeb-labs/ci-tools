// Seeded violations: a shift mixed with an addition without parentheses, and sizeof without them.
#include <cstdint>
#include <cstddef>

namespace kv::rule_8_0_1::bad {

std::uint32_t pack(std::uint32_t high, std::uint32_t low) {
  return high << 8U + low;  // seeded
}

std::size_t width(std::uint32_t value) {
  return sizeof value;  // seeded
}

}  // namespace kv::rule_8_0_1::bad
