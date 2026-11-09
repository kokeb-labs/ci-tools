// Compliant: the same task without the undefined behaviour.
#ifndef KV_RULE_4_1_3_MEMBER_POINTER_WRONG_TYPE_OK_HPP
#define KV_RULE_4_1_3_MEMBER_POINTER_WRONG_TYPE_OK_HPP

#include <cstdint>

namespace kv::rule_4_1_3_member_pointer_wrong_type::ok {

struct Point {
  std::uint32_t x{0U};
  std::uint32_t y{0U};
};

inline std::uint32_t pick(const Point& p, bool want_x) {
  std::uint32_t Point::*pm = &Point::y;
  if (want_x) {
    pm = &Point::x;
  }
  return p.*pm;
}

}  // namespace kv::rule_4_1_3_member_pointer_wrong_type::ok

#endif  // KV_RULE_4_1_3_MEMBER_POINTER_WRONG_TYPE_OK_HPP
