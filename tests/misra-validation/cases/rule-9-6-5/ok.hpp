// Compliant: every path returns a value.
#ifndef KV_RULE_9_6_5_OK_HPP
#define KV_RULE_9_6_5_OK_HPP

#include <cstdint>

namespace kv::rule_9_6_5::ok {

inline std::int32_t sign(std::int32_t v) {
  std::int32_t s = 0;
  if (v > 0) {
    s = 1;
  } else if (v < 0) {
    s = -1;
  } else {
    // zero: s keeps its initial value
  }
  return s;
}

}  // namespace kv::rule_9_6_5::ok

#endif  // KV_RULE_9_6_5_OK_HPP
