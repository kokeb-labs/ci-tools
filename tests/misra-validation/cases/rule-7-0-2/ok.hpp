#ifndef KV_RULE_7_0_2_OK_HPP
#define KV_RULE_7_0_2_OK_HPP

// Compliant: each condition is a comparison that yields bool.
#include <cstdint>

namespace kv::rule_7_0_2::ok {

inline std::int32_t pick(std::int32_t flags, std::int32_t const* p) {
  if (flags != 0) {
    return 1;
  }
  if (p != nullptr) {
    return *p;
  }
  return 0;
}

}  // namespace kv::rule_7_0_2::ok

#endif  // KV_RULE_7_0_2_OK_HPP
