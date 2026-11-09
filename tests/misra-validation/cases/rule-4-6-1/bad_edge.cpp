// Edge cases: an index read unsequenced with an increment, and arguments indeterminately sequenced.
#include <array>
#include <cstdint>

namespace kv::rule_4_6_1::bad_edge {

std::uint32_t load(const std::array<std::uint32_t, 4>& a, std::uint32_t i) {
  return a[i] + i++;  // seeded
}
std::uint32_t pair(std::uint32_t x, std::uint32_t y) { return x ^ y; }
std::uint32_t args(std::uint32_t i) { return pair(i, ++i); }  // seeded

}  // namespace kv::rule_4_6_1::bad_edge
