// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_5_13_4::bad_edge {

std::uint32_t all_ones() { return 0xFFFF'FFFF; }  // unsigned int, no U, with digit separators  // seeded
template <std::uint32_t V>
struct Mask {
  static constexpr std::uint32_t value = V;
};
std::uint32_t mask() { return Mask<0x8000'0001>::value; }  // seeded

}  // namespace kv::rule_5_13_4::bad_edge
