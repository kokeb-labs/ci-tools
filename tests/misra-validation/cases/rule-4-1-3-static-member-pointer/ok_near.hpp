// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_1_3_STATIC_MEMBER_POINTER_OK_NEAR_HPP
#define KV_RULE_4_1_3_STATIC_MEMBER_POINTER_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_4_1_3_static_member_pointer::near {

struct Point {
  std::uint32_t x{0U};
  std::uint32_t y{0U};
};
// A static-duration member pointer that is explicitly initialised to a member.
struct Axis {
  static constexpr std::uint32_t Point::*kMember = &Point::y;
};
inline std::uint32_t read(const Point& p) { return p.*Axis::kMember; }
inline std::uint32_t mix(const Point& p) { return p.x ^ read(p); }

}  // namespace kv::rule_4_1_3_static_member_pointer::near

#endif  // KV_RULE_4_1_3_STATIC_MEMBER_POINTER_OK_NEAR_HPP
