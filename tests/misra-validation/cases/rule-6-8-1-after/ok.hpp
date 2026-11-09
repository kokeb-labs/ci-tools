#ifndef KV_RULE_6_8_1_AFTER_OK_HPP
#define KV_RULE_6_8_1_AFTER_OK_HPP

// Compliant: the pointer is only read while the object it points to is alive.
#include <cstdint>

namespace kv::rule_6_8_1_after::ok {

inline std::int32_t fresh() {
  std::int32_t local = 7;
  std::int32_t const* const p = &local;
  return *p;
}

}  // namespace kv::rule_6_8_1_after::ok

#endif  // KV_RULE_6_8_1_AFTER_OK_HPP
