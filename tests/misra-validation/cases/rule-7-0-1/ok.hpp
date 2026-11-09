#ifndef KV_RULE_7_0_1_OK_HPP
#define KV_RULE_7_0_1_OK_HPP

// Compliant: the truth value selects a number explicitly.
#include <cstdint>

namespace kv::rule_7_0_1::ok {

inline std::int32_t count(bool a, bool b) {
  std::int32_t const first = a ? 1 : 0;
  std::int32_t const second = b ? 1 : 0;
  return first + second;
}

}  // namespace kv::rule_7_0_1::ok

#endif  // KV_RULE_7_0_1_OK_HPP
