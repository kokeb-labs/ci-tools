// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_6_0_1_OK_NEAR_HPP
#define KV_RULE_6_0_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_6_0_1::near {

struct Counter {
  std::int32_t start{0};
};
inline std::int32_t helper(std::int32_t v) { return v; }
// Brace and copy initialisation create objects; a call statement is not a declaration.
inline bool make() {
  const Counter a{};
  const Counter b = Counter();
  return helper(a.start) == b.start;
}

}  // namespace kv::rule_6_0_1::near

#endif  // KV_RULE_6_0_1_OK_NEAR_HPP
