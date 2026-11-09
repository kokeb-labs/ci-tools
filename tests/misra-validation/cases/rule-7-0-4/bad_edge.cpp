// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_7_0_4::bad_edge {

std::int32_t merge(std::int32_t a, std::int32_t b) { return (a | b) ^ 0x10; }

std::int32_t invert(std::int32_t v) { return ~v; }

std::int32_t grow(std::int32_t v) {
  v <<= 1;
  return v;
}

std::uint32_t too_far(std::uint32_t v) { return v << 32U; }

}  // namespace kv::rule_7_0_4::bad_edge
