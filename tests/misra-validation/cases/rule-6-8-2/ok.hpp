#ifndef KV_RULE_6_8_2_OK_HPP
#define KV_RULE_6_8_2_OK_HPP

// Compliant: the value is returned by copy.
#include <cstdint>

namespace kv::rule_6_8_2::ok {

inline std::int32_t by_value() {
  std::int32_t const local = 1;
  return local;
}

}  // namespace kv::rule_6_8_2::ok

#endif  // KV_RULE_6_8_2_OK_HPP
