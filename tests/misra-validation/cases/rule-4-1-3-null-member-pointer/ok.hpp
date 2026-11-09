// Compliant: the same task without the undefined behaviour.
#ifndef KV_RULE_4_1_3_NULL_MEMBER_POINTER_OK_HPP
#define KV_RULE_4_1_3_NULL_MEMBER_POINTER_OK_HPP

#include <cstdint>

namespace kv::rule_4_1_3_null_member_pointer::ok {

struct Point {
  std::uint32_t x{0U};
};

inline std::uint32_t read(const Point& p) {
  std::uint32_t Point::*pm = &Point::x;
  return p.*pm;
}

}  // namespace kv::rule_4_1_3_null_member_pointer::ok

#endif  // KV_RULE_4_1_3_NULL_MEMBER_POINTER_OK_HPP
