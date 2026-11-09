#ifndef KV_RULE_6_8_1_BEFORE_OK_HPP
#define KV_RULE_6_8_1_BEFORE_OK_HPP

// Compliant: the object is created and initialised before it is read.
#include <cstdint>

namespace kv::rule_6_8_1_before::ok {

inline std::int32_t in_order() {
  std::int32_t value = 3;
  std::int32_t const* const p = &value;
  return *p;
}

}  // namespace kv::rule_6_8_1_before::ok

#endif  // KV_RULE_6_8_1_BEFORE_OK_HPP
