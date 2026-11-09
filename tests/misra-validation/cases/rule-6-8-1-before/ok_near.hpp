// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_6_8_1_BEFORE_OK_NEAR_HPP
#define KV_RULE_6_8_1_BEFORE_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_6_8_1_before::near {

// The pointer is initialised on both paths of a conditional before it is dereferenced.
inline std::int32_t choose(bool first) {
  const std::int32_t a = 1;
  const std::int32_t b = 2;
  const std::int32_t* const p = first ? &a : &b;
  return *p;
}

}  // namespace kv::rule_6_8_1_before::near

#endif  // KV_RULE_6_8_1_BEFORE_OK_NEAR_HPP
