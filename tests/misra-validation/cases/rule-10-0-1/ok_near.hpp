// Near misses (near): single declarators where lists would be possible; parameter lists.
#ifndef KV_RULE_10_0_1_OK_NEAR_HPP
#define KV_RULE_10_0_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_10_0_1::ok_near {

struct Span {
  std::uint32_t lo = 0U;
  std::uint32_t hi = 0U;
};

inline std::uint32_t width(const Span& s, std::uint32_t step, std::uint32_t limit) {
  std::uint32_t w = 0U;
  for (std::uint32_t i = s.lo; i < s.hi; i += step) {
    w = w + 1U;
  }
  return (w < limit) ? w : limit;
}

}  // namespace kv::rule_10_0_1::ok_near

#endif  // KV_RULE_10_0_1_OK_NEAR_HPP
