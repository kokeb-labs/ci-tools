// Edge cases: more forms of the violation.
#include <array>
#include <cstdint>

namespace kv::rule_4_6_1::bad_edge {

void store(std::array<std::uint32_t, 4>& a, std::uint32_t i) {
  a[i] = i++;  // the index read is unsequenced with the increment
}
std::uint32_t pair(std::uint32_t x, std::uint32_t y) { return x ^ y; }
std::uint32_t args(std::uint32_t i) { return pair(i, ++i); }

}  // namespace kv::rule_4_6_1::bad_edge
