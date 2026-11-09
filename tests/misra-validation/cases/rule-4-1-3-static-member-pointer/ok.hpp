// Compliant: the same task without the undefined behaviour.
#ifndef KV_RULE_4_1_3_STATIC_MEMBER_POINTER_OK_HPP
#define KV_RULE_4_1_3_STATIC_MEMBER_POINTER_OK_HPP

#include <cstdint>

namespace kv::rule_4_1_3_static_member_pointer::ok {

struct Point {
  std::uint32_t x{0U};
};

inline std::uint32_t read(const Point& p) {
  constexpr std::uint32_t Point::*member = &Point::x;
  return p.*member;
}

}  // namespace kv::rule_4_1_3_static_member_pointer::ok

#endif  // KV_RULE_4_1_3_STATIC_MEMBER_POINTER_OK_HPP
