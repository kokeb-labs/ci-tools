// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_8_3_1::bad_edge {

std::uint32_t all_ones() { return -1U; }  // seeded

std::uint64_t negate_wide(std::uint64_t v) { return -v; }  // seeded

template <typename T>
T flip(T v) {
  return -v;  // seeded
}

std::uint32_t use(std::uint32_t v) { return flip(v); }

}  // namespace kv::rule_8_3_1::bad_edge
