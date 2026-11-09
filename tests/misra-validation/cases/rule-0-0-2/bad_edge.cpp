// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_0_0_2::bad_edge {

bool never(std::uint32_t v) {
  bool out = false;
  if (v < 0U) {  // always false for an unsigned value
    out = true;
  }
  return out;
}

std::uint32_t count_bits(std::uint8_t b) {
  std::uint32_t n = 0U;
  if (b <= 255U) {  // always true for an 8-bit value
    n = 1U;
  }
  return n;
}

}  // namespace kv::rule_0_0_2::bad_edge
