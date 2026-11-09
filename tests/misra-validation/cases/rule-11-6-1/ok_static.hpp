// Near miss: a variable with static storage duration is zero-initialised without an initializer.
#ifndef KV_RULE_11_6_1_OK_STATIC_HPP
#define KV_RULE_11_6_1_OK_STATIC_HPP

#include <cstdint>

namespace kv::rule_11_6_1::ok_static {

inline std::uint32_t count_calls() {
  static std::uint32_t calls;
  calls = calls + 1U;
  return calls;
}

}  // namespace kv::rule_11_6_1::ok_static

#endif  // KV_RULE_11_6_1_OK_STATIC_HPP
