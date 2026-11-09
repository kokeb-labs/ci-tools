// Near misses: compliant code close to a violation.
#ifndef KV_RULE_7_0_3_OK_NEAR_HPP
#define KV_RULE_7_0_3_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_7_0_3::ok_near {

inline char copy(char c) {
  char const d = c;
  return d;
}


inline bool is_end(char c) { return c == '\0'; }

}  // namespace kv::rule_7_0_3::ok_near

#endif  // KV_RULE_7_0_3_OK_NEAR_HPP
