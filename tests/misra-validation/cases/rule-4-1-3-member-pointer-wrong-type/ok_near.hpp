// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_1_3_MEMBER_POINTER_WRONG_TYPE_OK_NEAR_HPP
#define KV_RULE_4_1_3_MEMBER_POINTER_WRONG_TYPE_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_4_1_3_member_pointer_wrong_type::near {

// A derived member converted to a base member pointer, applied to an object that really is the derived type.
struct Base {
  std::uint32_t tag{0U};
};
struct Derived : Base {
  std::uint32_t extra{7U};
};
inline std::uint32_t peek(const Derived& d) {
  const std::uint32_t Base::*pm = static_cast<std::uint32_t Base::*>(&Derived::extra);
  const Base& b = d;
  return (b.*pm) ^ b.tag;
}

}  // namespace kv::rule_4_1_3_member_pointer_wrong_type::near

#endif  // KV_RULE_4_1_3_MEMBER_POINTER_WRONG_TYPE_OK_NEAR_HPP
