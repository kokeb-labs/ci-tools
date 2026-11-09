// Compliant: a widening of a class member access of the same signedness (Rule 7.0.6, item 2).
#ifndef KV_RULE_7_0_6_MEMBER_ACCESS_OK_HPP
#define KV_RULE_7_0_6_MEMBER_ACCESS_OK_HPP

#include <cstdint>

namespace kv::rule_7_0_6_member_access::ok {

struct Gpio {
  std::uint8_t output_mask;
};

inline std::uint32_t outputs(const Gpio& g) {
  const std::uint32_t m = g.output_mask;
  return m;
}

}  // namespace kv::rule_7_0_6_member_access::ok

#endif  // KV_RULE_7_0_6_MEMBER_ACCESS_OK_HPP
