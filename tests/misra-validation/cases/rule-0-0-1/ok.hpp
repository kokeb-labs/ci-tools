// Compliant: every statement can run.
#ifndef KV_RULE_0_0_1_OK_HPP
#define KV_RULE_0_0_1_OK_HPP

#include <cstdint>

namespace kv::rule_0_0_1::ok {

inline std::int32_t clamp(std::int32_t v) {
  std::int32_t out = v;
  if (v < 0) {
    out = 0;
  }
  return out;
}

}  // namespace kv::rule_0_0_1::ok

#endif  // KV_RULE_0_0_1_OK_HPP
