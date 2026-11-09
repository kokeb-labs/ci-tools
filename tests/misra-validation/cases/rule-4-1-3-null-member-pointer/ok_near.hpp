// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_1_3_NULL_MEMBER_POINTER_OK_NEAR_HPP
#define KV_RULE_4_1_3_NULL_MEMBER_POINTER_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_4_1_3_null_member_pointer::near {

struct Point {
  std::uint32_t x{0U};
};
// A member pointer that may be null, tested before use.
inline std::uint32_t read_or_zero(const Point& p, std::uint32_t Point::*pm) {
  std::uint32_t out = 0U;
  if (pm != nullptr) {
    out = p.*pm;
  }
  return out;
}
inline std::uint32_t x_of(const Point& p) { return read_or_zero(p, &Point::x); }

}  // namespace kv::rule_4_1_3_null_member_pointer::near

#endif  // KV_RULE_4_1_3_NULL_MEMBER_POINTER_OK_NEAR_HPP
