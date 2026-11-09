// Compliant: the else-if chain ends with an else (here stating that the default stands).
#ifndef KV_RULE_9_4_1_OK_HPP
#define KV_RULE_9_4_1_OK_HPP

#include <cstdint>

namespace kv::rule_9_4_1::ok {

inline std::int32_t classify(std::int32_t v) {
  std::int32_t c = 0;
  if (v < 0) {
    c = -1;
  } else if (v > 0) {
    c = 1;
  } else {
    // zero: c keeps its initial value
  }
  return c;
}

}  // namespace kv::rule_9_4_1::ok

#endif  // KV_RULE_9_4_1_OK_HPP
