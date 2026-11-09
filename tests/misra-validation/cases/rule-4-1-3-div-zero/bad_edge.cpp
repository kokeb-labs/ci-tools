// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_4_1_3_div_zero::bad_edge {

std::uint32_t wrap(std::uint32_t v) {
  const std::uint32_t modulus = 0U;
  return v % modulus;  // remainder by zero
}
std::int32_t signed_share(std::int32_t v) {
  constexpr std::int32_t kParts = 0;
  return v / kParts;
}

}  // namespace kv::rule_4_1_3_div_zero::bad_edge
