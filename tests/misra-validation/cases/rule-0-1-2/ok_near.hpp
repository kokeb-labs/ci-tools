// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_0_1_2_OK_NEAR_HPP
#define KV_RULE_0_1_2_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_0_1_2::near {

inline void reset(std::uint32_t& r) { r = 0U; }
inline std::uint32_t flip(std::uint32_t v) { return v ^ 1U; }

// A void call has no result to use; the non-void call's result is used in the condition.
inline std::uint32_t step(std::uint32_t v) {
  std::uint32_t r = v;
  reset(r);
  if (flip(v) != 0U) {
    r = 1U;
  }
  return r;
}

}  // namespace kv::rule_0_1_2::near

#endif  // KV_RULE_0_1_2_OK_NEAR_HPP
